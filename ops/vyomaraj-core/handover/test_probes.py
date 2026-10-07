"""Tests for the one-shot, fixed-loopback local monitor."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import socket
import tempfile
import threading
import unittest
from unittest.mock import patch

import probes


class _ReplyHandler(BaseHTTPRequestHandler):
    status = 200

    def do_GET(self):
        if self.path == '/redirect':
            self.send_response(302)
            self.send_header('Location', 'http://example.com/should-not-be-followed')
            self.end_headers()
            return
        self.send_response(self.status)
        self.end_headers()
        self.wfile.write(b'ok')

    def log_message(self, *args):
        pass


class ProbeTests(unittest.TestCase):
    def setUp(self):
        _ReplyHandler.status = 200
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), _ReplyHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.target = {'id': 'test', 'label': 'Test service',
                       'port': self.server.server_port, 'path': '/health'}

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def test_success_records_listener_http_and_latency(self):
        _ReplyHandler.status = 200
        row = probes.probe_target(self.target, timeout=1)
        self.assertTrue(row['listening'])
        self.assertEqual(row['http_status'], 200)
        self.assertTrue(row['healthy'])
        self.assertGreaterEqual(row['latency_ms'], 0)

    def test_custom_ports_remain_loopback_and_are_range_checked(self):
        targets = probes.targets_with_ports((5174, 5176, 5181, 5182))
        self.assertEqual([row['port'] for row in targets], [5174, 5176, 5181, 5182])
        self.assertTrue(all(probes._target_url(row).startswith('http://127.0.0.1:')
                            for row in targets))
        with self.assertRaises(ValueError):
            probes.targets_with_ports((0, 5176, 5181, 5182))
        with self.assertRaises(ValueError):
            probes.targets_with_ports((5174, 5176, 5181))

    def test_probe_is_loopback_only_and_does_not_follow_redirects(self):
        hostile = dict(self.target, host='example.com', scheme='https', path='/redirect')
        self.assertEqual(probes._target_url(hostile),
                         f'http://127.0.0.1:{self.server.server_port}/redirect')
        row = probes.probe_target(hostile, timeout=1)
        self.assertTrue(row['listening'])
        self.assertEqual(row['http_status'], 302)
        self.assertFalse(row['healthy'])

    def test_http_error_still_records_a_listening_socket(self):
        _ReplyHandler.status = 503
        snapshot = probes.collect_snapshot(
            targets=(self.target,), captured_at_utc='2026-10-07T04:00:00Z', timeout=1)
        row = snapshot['targets'][0]
        self.assertTrue(row['listening'])
        self.assertEqual(row['http_status'], 503)
        self.assertFalse(row['healthy'])
        self.assertEqual(row['consecutive_failures'], 1)

    def test_connection_refusal_is_not_reported_as_a_listener(self):
        probe_socket = socket.socket()
        probe_socket.bind(('127.0.0.1', 0))
        port = probe_socket.getsockname()[1]
        probe_socket.close()
        target = {'id': 'closed', 'label': 'Closed service', 'port': port, 'path': '/'}
        row = probes.probe_target(target, timeout=0.2)
        self.assertFalse(row['listening'])
        self.assertIsNone(row['http_status'])
        self.assertFalse(row['healthy'])

    def test_consecutive_failures_preserve_last_success_time(self):
        previous = {
            'schema': probes.SCHEMA,
            'targets': [{'id': 'test', 'healthy': True, 'consecutive_failures': 0,
                         'last_successful_check_utc': '2026-10-07T03:00:00Z'}],
        }
        failed = {'id': 'test', 'service': 'Test service', 'port': self.target['port'],
                  'path': '/health', 'listening': False, 'http_status': None,
                  'healthy': False, 'latency_ms': 12.5, 'error_kind': 'URLError'}
        with patch.object(probes, 'probe_target', side_effect=lambda *args, **kwargs: dict(failed)):
            first = probes.collect_snapshot((self.target,), previous=previous,
                                            captured_at_utc='2026-10-07T04:00:00Z')
            second = probes.collect_snapshot((self.target,), previous=first,
                                             captured_at_utc='2026-10-07T04:01:00Z')
        self.assertEqual(first['targets'][0]['consecutive_failures'], 1)
        self.assertEqual(second['targets'][0]['consecutive_failures'], 2)
        self.assertEqual(second['targets'][0]['last_successful_check_utc'], '2026-10-07T03:00:00Z')

    def test_recovery_resets_failure_count_and_updates_last_success(self):
        previous = {
            'schema': probes.SCHEMA,
            'targets': [{'id': 'test', 'healthy': False, 'consecutive_failures': 4,
                         'last_successful_check_utc': '2026-10-07T03:00:00Z'}],
        }
        healthy = {'id': 'test', 'service': 'Test service', 'port': self.target['port'],
                   'path': '/health', 'listening': True, 'http_status': 200,
                   'healthy': True, 'latency_ms': 1.0, 'error_kind': None}
        with patch.object(probes, 'probe_target', return_value=healthy):
            snapshot = probes.collect_snapshot((self.target,), previous=previous,
                                               captured_at_utc='2026-10-07T04:00:00Z')
        self.assertEqual(snapshot['targets'][0]['consecutive_failures'], 0)
        self.assertEqual(snapshot['targets'][0]['last_successful_check_utc'], '2026-10-07T04:00:00Z')

    def test_writer_appends_jsonl_and_atomically_updates_latest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            log = root / 'samples.jsonl'
            latest = root / 'latest.json'
            for stamp in ('2026-10-07T04:00:00Z', '2026-10-07T04:01:00Z'):
                probes.write_snapshot({'schema': probes.SCHEMA, 'captured_at_utc': stamp,
                                       'scope': 'test', 'targets': []}, log, latest)
            rows = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            self.assertEqual(probes.load_snapshot(latest)['captured_at_utc'], '2026-10-07T04:01:00Z')
            self.assertEqual(list(root.glob('*.tmp')), [])

    def test_monitor_page_reports_missing_or_invalid_snapshot_without_probing(self):
        with tempfile.TemporaryDirectory() as temp:
            latest = Path(temp) / 'latest.json'
            page = probes.render_monitor_html(latest)
            self.assertIn('Local service monitor', page)
            self.assertIn('No probe has run yet', page)
            self.assertIn('never starts a probe', page)
            latest.write_text('{not json')
            page = probes.render_monitor_html(latest)
            self.assertIn('snapshot is unreadable', page)

    def test_monitor_page_escapes_snapshot_text_and_states_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            latest = Path(temp) / 'latest.json'
            snapshot = {
                'schema': probes.SCHEMA,
                'captured_at_utc': '2026-10-07T04:00:00Z',
                'scope': 'fixed loopback preview only',
                'targets': [{'id': 'x', 'service': '<script>alert(1)</script>', 'port': 4174,
                             'path': '/', 'listening': True, 'http_status': 200, 'healthy': True,
                             'latency_ms': 2.0, 'last_successful_check_utc': '2026-10-07T04:00:00Z',
                             'consecutive_failures': 0}],
            }
            latest.write_text(json.dumps(snapshot))
            page = probes.render_monitor_html(latest)
            self.assertNotIn('<script>', page)
            self.assertIn('&lt;script&gt;', page)
            self.assertIn('independent-site disaster-recovery', page)


if __name__ == '__main__':
    unittest.main()
