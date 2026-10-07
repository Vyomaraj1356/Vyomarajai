import json
from pathlib import Path
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from unittest.mock import patch

import studio_server as server


class ResearchHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.old_research_store = server.RESEARCH_STORE
        cls.old_approval_store = server.APPROVAL_STORE
        cls.old_require = server.OWNER_GUARD.require_owner_approval
        cls.old_verify = server.OWNER_GUARD.verify_owner_approval
        server.RESEARCH_STORE = server.discovery.Store(Path(cls.temp.name) / 'research.sqlite3')
        server.APPROVAL_STORE = server.APPROVAL_STORE_MODULE.ApprovalStore(
            Path(cls.temp.name) / 'approvals.sqlite3'
        )

        def mock_verify(token, *, action, target, required_scope):
            try:
                prefix, jti, token_action, token_scope, token_target = token.split('|', 4)
            except (AttributeError, ValueError):
                raise server.OWNER_GUARD.AuthorizationDenied('Mock owner token is malformed.')
            if (prefix != 'mock-owner-token' or token_action != action
                    or token_scope != required_scope or token_target != target):
                raise server.OWNER_GUARD.AuthorizationDenied('Mock owner token target mismatch.')
            return {'sub': 'owner-subject-test', 'jti': jti, 'action': action,
                    'scope': [required_scope], 'target': target, 'authn': 'passkey',
                    'step_up': action == 'approval.decide' or action.startswith('upgrade.')}

        def mock_require(*, action, target, required_scope, token=None):
            return mock_verify(token, action=action, target=target, required_scope=required_scope)

        server.OWNER_GUARD.verify_owner_approval = mock_verify
        server.OWNER_GUARD.require_owner_approval = mock_require
        cls.http = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.http.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:' + str(cls.http.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.http.shutdown()
        cls.http.server_close()
        cls.thread.join()
        server.RESEARCH_STORE = cls.old_research_store
        server.APPROVAL_STORE = cls.old_approval_store
        server.OWNER_GUARD.require_owner_approval = cls.old_require
        server.OWNER_GUARD.verify_owner_approval = cls.old_verify
        cls.temp.cleanup()

    @classmethod
    def auth_headers(cls, action, scope, data, jti):
        target = server.OWNER_GUARD.canonical_action_target(action, data)
        token = '|'.join(('mock-owner-token', jti, action, scope, target))
        return {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + token}

    def request(self, path, data=None, headers=None):
        defaults = {'Content-Type': 'application/json'} if data is not None else {}
        req = urllib.request.Request(
            self.base + path,
            data=json.dumps(data).encode() if data is not None else None,
            headers=headers or defaults,
        )
        try:
            with urllib.request.urlopen(req) as response:
                return response.status, response.read(), response.headers
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read(), exc.headers

    def test_status_and_assets(self):
        for route in ['/research/', '/research/app.js', '/research/styles.css', '/api/research/status']:
            status, body, headers = self.request(route)
            self.assertEqual(status, 200)
            self.assertIn("default-src 'none'", headers['Content-Security-Policy'])
        data = json.loads(self.request('/api/research/status')[1])
        self.assertFalse(data['automatic_publishing'])

    def test_research_writers_fail_closed_without_request_token(self):
        before_jobs = len(server.RESEARCH_STORE.status()['jobs'])
        run_body = {'profile': 'classic-films'}
        status, raw, _ = self.request('/api/research/run', run_body)
        self.assertEqual(status, 401)
        error = json.loads(raw)
        self.assertEqual(error['required']['action'], 'research.run')
        self.assertEqual(error['required']['target'], server.OWNER_GUARD.canonical_action_target(
            'research.run', run_body,
        ))
        self.assertEqual(len(server.RESEARCH_STORE.status()['jobs']), before_jobs)

        review_body = {'record_id': 'missing', 'decision': 'accepted_metadata_only',
                       'acknowledge_metadata_only': True}
        status, raw, _ = self.request('/api/research/review', review_body)
        self.assertEqual(status, 401)
        self.assertEqual(json.loads(raw)['required']['action'], 'research.review')

    def test_enqueue_closed_fields_and_profile(self):
        headers = self.auth_headers('research.run', 'research.run', {'profile': 'hindi-theatre'}, 'run-ok')
        self.assertEqual(self.request('/api/research/run', {'profile': 'hindi-theatre'}, headers)[0], 202)
        for body in [{'profile': 'evil'}, {'profile': 'hindi-theatre', 'url': 'http://localhost/private'},
                     [], {'profile': []}]:
            action_headers = self.auth_headers('research.run', 'research.run', body, 'invalid-' + str(len(json.dumps(body))))
            self.assertEqual(self.request('/api/research/run', body, action_headers)[0], 400)

    def test_cross_origin_refused_before_owner_token(self):
        status = self.request(
            '/api/research/run', {'profile': 'classic-films'},
            {'Content-Type': 'application/json', 'Origin': 'https://evil.example'},
        )[0]
        self.assertEqual(status, 403)

    def test_same_origin_research_enqueue_requires_matching_owner_token(self):
        data = {'profile': 'classic-films'}
        headers = self.auth_headers('research.run', 'research.run', data, 'same-origin-run')
        headers['Origin'] = self.base
        self.assertEqual(self.request('/api/research/run', data, headers)[0], 202)

    def test_review_requires_ack_and_owner_token(self):
        record = server.discovery.candidate(
            'fixture', 'one', 'Fixture', 'https://example.org/source', 'classic-films',
        )
        server.RESEARCH_STORE.save(record)
        body = {'record_id': record['id'], 'decision': 'accepted_metadata_only',
                'acknowledge_metadata_only': False}
        self.assertEqual(self.request('/api/research/review', body)[0], 400)
        body['acknowledge_metadata_only'] = True
        status, _, _ = self.request(
            '/api/research/review', body,
            self.auth_headers('research.review', 'research.review', body, 'review-one'),
        )
        self.assertEqual(status, 200)
        reviewed = next(r for r in server.RESEARCH_STORE.records(limit=5000)
                        if r['id'] == record['id'])
        self.assertEqual(reviewed['review_status'], 'accepted_metadata_only')
        self.assertEqual(reviewed['rights_status'], 'UNKNOWN')
        self.assertIsNone(reviewed['media_url'])

    def test_exports_remain_metadata_only_and_pagination_is_bounded(self):
        self.assertEqual(self.request('/api/research/records?offset=-1')[0], 400)
        self.assertEqual(self.request('/api/research/records?offset=abc')[0], 400)
        self.assertEqual(json.loads(self.request('/api/research/records?offset=5000')[1])['records'], [])
        self.assertEqual(json.loads(self.request('/api/research/export')[1])['scope'],
                         'unverified_metadata_not_media_or_licences')

    def test_approval_endpoint_requires_request_token_and_persists_audited_decision(self):
        item_id = 'comics-monsoon-post-issue'
        body = {'item_id': item_id, 'decision': 'approve'}
        status, raw, _ = self.request('/api/approvals/decide', body)
        self.assertEqual(status, 401)
        challenge = json.loads(raw)['required']
        self.assertEqual(challenge['action'], 'approval.decide')
        self.assertEqual(challenge['target'], server.OWNER_GUARD.canonical_action_target(
            'approval.decide', body,
        ))
        self.assertEqual(server.APPROVAL_STORE.item(item_id)['status'], 'awaiting_owner')

        headers = self.auth_headers('approval.decide', 'approval.decide', body, 'approval-jti-1')
        status, raw, _ = self.request('/api/approvals/decide', body, headers)
        self.assertEqual(status, 200)
        decision = json.loads(raw)
        self.assertEqual(decision['status'], 'owner_decision_recorded_locally')
        self.assertEqual(decision['decided_by'], 'owner-subject-test')
        self.assertFalse(decision['publishing_enabled'])
        self.assertFalse(decision['notifications']['sent'])
        self.assertTrue(server.APPROVAL_STORE.verify_audit_chain()['valid'])
        self.assertEqual(server.APPROVAL_STORE.queue()['counts']['awaiting_owner'], 2)

        status, _, _ = self.request('/api/approvals/decide', body, headers)
        self.assertEqual(status, 409)
        self.assertFalse(server.APPROVAL_STORE.status()['production_deployed'])

    def test_approval_queue_and_review_read_persisted_state(self):
        status, raw, _ = self.request('/api/approvals/queue')
        self.assertEqual(status, 200)
        data = json.loads(raw)
        self.assertEqual(data['counts']['total'], 3)
        review = self.request('/api/approvals/review/film-monsoon-outline')
        self.assertEqual(review[0], 200)
        self.assertEqual(json.loads(review[1])['item']['id'], 'film-monsoon-outline')

    def test_private_state_and_templates_not_served(self):
        for path in ['/research/.state/discovery.sqlite3', '/research/.env',
                     '/research/compose.example.yml', '/research/discovery.py',
                     '/.git/config', '/api/research/settings']:
            self.assertEqual(self.request(path)[0], 404)

    def test_json_required_no_form_posts(self):
        self.assertEqual(self.request(
            '/api/research/run', {'profile': 'classic-films'},
            {'Content-Type': 'text/plain'},
        )[0], 415)


if __name__ == '__main__':
    unittest.main()
