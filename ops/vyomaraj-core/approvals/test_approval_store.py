"""Offline tests for atomic owner-decision persistence and audit integrity."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import approval_queue as queue
import approval_store as storage


class ApprovalStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / 'approvals.sqlite3'
        self.store = storage.ApprovalStore(self.path)
        self.seed = json.loads(Path(queue.QUEUE_PATH).read_text(encoding='utf-8'))

    def tearDown(self):
        self.temp.cleanup()

    def decision_record(self, item_id, decision='approve', *, voice=None):
        item = self.store.item(item_id)
        return queue.build_decision_record(
            item, decision, voice, decided_by='configured-owner-subject',
            camera=self.seed['camera'], notifications=self.seed['notifications'],
        )

    def persist(self, item_id, *, jti='one-time-jti', decision='approve', target=None):
        record = self.decision_record(item_id, decision)
        return self.store.persist_decision(
            item_id, record, jti=jti, target_sha256=target or ('a' * 64),
        )

    def test_seeded_queue_and_review_use_private_local_database(self):
        view = self.store.queue()
        self.assertEqual(view['counts']['total'], 3)
        self.assertEqual(view['counts']['awaiting_owner'], 3)
        self.assertEqual(view['audit']['event_count'], 0)
        self.assertTrue(view['audit']['integrity_verified'])
        self.assertEqual(self.store.open_review('comics-monsoon-post-issue')['item']['id'],
                         'comics-monsoon-post-issue')
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_decision_commit_updates_queue_consumes_jti_and_appends_audit_atomically(self):
        item_id = 'comics-monsoon-post-issue'
        result = self.persist(item_id, jti='private-jti-1', decision='approve')
        self.assertEqual(result['status'], 'owner_decision_recorded_locally')
        self.assertEqual(result['persistence']['store'], 'private_local_sqlite')
        self.assertFalse(result['persistence']['publication_enabled'])
        self.assertFalse(result['persistence']['notification_sent'])
        self.assertEqual(self.store.item(item_id)['status'],
                         'owner_approved_for_publishing_gate_not_published')
        state = self.store.verify_audit_chain()
        self.assertTrue(state['valid'])
        self.assertEqual(state['event_count'], 1)

        connection = self.store._connect()
        try:
            stored_jti = connection.execute(
                'SELECT jti_sha256 FROM consumed_approvals'
            ).fetchone()['jti_sha256']
            event = connection.execute('SELECT event_json FROM audit_events').fetchone()['event_json']
            saved = connection.execute('SELECT record_json FROM decisions').fetchone()['record_json']
        finally:
            connection.close()
        self.assertEqual(stored_jti, hashlib.sha256(b'private-jti-1').hexdigest())
        self.assertNotIn('private-jti-1', event)
        self.assertNotIn('private-jti-1', saved)
        self.assertNotIn('owner token', saved.lower())
        with self.assertRaises(storage.InvalidApproval):
            self.store.open_review(item_id)

    def test_one_time_jti_replay_is_refused_even_for_a_different_queue_item(self):
        self.persist('comics-monsoon-post-issue', jti='same-jti')
        record = self.decision_record('film-monsoon-outline', 'reject')
        with self.assertRaises(storage.ApprovalReplay):
            self.store.persist_decision(
                'film-monsoon-outline', record, jti='same-jti', target_sha256='b' * 64,
            )
        self.assertEqual(self.store.item('film-monsoon-outline')['status'], 'awaiting_owner')
        self.assertEqual(self.store.verify_audit_chain()['event_count'], 1)

    def test_concurrent_decisions_cannot_both_advance_the_same_item(self):
        import threading
        outcomes = []
        barrier = threading.Barrier(2)

        def decide(jti):
            record = self.decision_record('film-monsoon-outline', 'rework')
            barrier.wait()
            try:
                self.store.persist_decision(
                    'film-monsoon-outline', record, jti=jti, target_sha256='c' * 64,
                )
                outcomes.append('committed')
            except storage.InvalidApproval:
                outcomes.append('already_decided')

        threads = [threading.Thread(target=decide, args=(f'jti-{n}',)) for n in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
        self.assertCountEqual(outcomes, ['committed', 'already_decided'])
        self.assertEqual(self.store.verify_audit_chain()['event_count'], 1)

    def test_tampered_audit_event_is_detected(self):
        self.persist('comics-monsoon-post-issue')
        connection = self.store._connect()
        try:
            connection.execute("UPDATE audit_events SET event_json='{}'")
        finally:
            connection.close()
        self.assertFalse(self.store.verify_audit_chain()['valid'])
        record = self.decision_record('film-monsoon-outline', 'reject')
        with self.assertRaises(storage.ApprovalStoreError):
            self.store.persist_decision(
                'film-monsoon-outline', record, jti='second-jti', target_sha256='d' * 64,
            )
        self.assertEqual(self.store.item('film-monsoon-outline')['status'], 'awaiting_owner')

    def test_invalid_targets_and_decision_records_do_not_mutate_store(self):
        record = self.decision_record('comics-monsoon-post-issue')
        for target in ('short', 'g' * 64):
            with self.subTest(target=target), self.assertRaises(storage.InvalidApproval):
                self.store.persist_decision(
                    'comics-monsoon-post-issue', record, jti='unused-jti', target_sha256=target,
                )
        self.assertEqual(self.store.item('comics-monsoon-post-issue')['status'], 'awaiting_owner')
        self.assertEqual(self.store.verify_audit_chain()['event_count'], 0)


if __name__ == '__main__':
    unittest.main()
