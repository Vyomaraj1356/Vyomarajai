#!/usr/bin/env python3
"""One-shot loopback monitor for the local Vyomaraj preview stack.

This is deliberately not a daemon and has no external targets: each run makes one GET to the four
fixed local preview ports, appends one JSONL record and atomically replaces a local latest snapshot.
The report viewer only reads that snapshot; opening /reports/monitor never runs a probe.

Example:
    python3 ops/vyomaraj-core/handover/probes.py --once --state /tmp/vyomaraj-probes.jsonl
"""
import argparse
from datetime import datetime, timezone
import html
import json
import os
from pathlib import Path
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, ProxyHandler, build_opener

SCHEMA = 'vyomaraj-local-probes/1'
DEFAULT_STATE = Path('/tmp/vyomaraj-probes.jsonl')
DEFAULT_LATEST = Path('/tmp/vyomaraj-probes.latest.json')
TARGETS = (
    {'id': 'viewer', 'label': 'Report viewer', 'port': 4174, 'path': '/'},
    {'id': 'gateway', 'label': 'Availability gateway', 'port': 4176, 'path': '/api/availability'},
    {'id': 'lane_a', 'label': 'Experience lane A', 'port': 4181, 'path': '/healthz'},
    {'id': 'lane_b', 'label': 'Experience lane B', 'port': 4182, 'path': '/healthz'},
)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def _target_url(target):
    """Build a loopback-only URL; target data cannot select a host or scheme."""
    port = int(target['port'])
    path = str(target.get('path', '/'))
    if not 1 <= port <= 65535 or not path.startswith('/') or path.startswith('//'):
        raise ValueError('invalid fixed probe target')
    return f'http://127.0.0.1:{port}{path}'


class _RejectRedirects(HTTPRedirectHandler):
    """Prevent a local probe response from redirecting the client to any non-loopback host."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_LOCAL_OPENER = build_opener(ProxyHandler({}), _RejectRedirects())


def _local_urlopen(url, timeout):
    return _LOCAL_OPENER.open(url, timeout=timeout)


def probe_target(target, timeout=2.0, opener=None):
    """Measure one fixed local endpoint; HTTP errors still prove that a listener answered."""
    opener = opener or _local_urlopen
    started = time.perf_counter()
    listening = False
    status = None
    error_kind = None
    try:
        with opener(_target_url(target), timeout=timeout) as response:
            listening = True
            status = int(response.status)
    except HTTPError as exc:
        listening = True
        status = int(exc.code)
        error_kind = 'http_error'
        exc.close()
    except (URLError, OSError, TimeoutError) as exc:
        # Do not store exception text: it may contain local paths or URLs.
        error_kind = type(exc).__name__
    latency_ms = round((time.perf_counter() - started) * 1000, 3)
    healthy = listening and status == 200
    return {
        'id': str(target['id']),
        'service': str(target['label']),
        'port': int(target['port']),
        'path': str(target.get('path', '/')),
        'listening': listening,
        'http_status': status,
        'healthy': healthy,
        'latency_ms': latency_ms,
        'error_kind': error_kind,
    }


def targets_with_ports(ports):
    """Return the four fixed targets with operator-selected numeric loopback ports."""
    ports = tuple(int(port) for port in ports)
    if len(ports) != len(TARGETS) or any(not 1 <= port <= 65535 for port in ports):
        raise ValueError('exactly four TCP ports in the range 1..65535 are required')
    return tuple({**target, 'port': port} for target, port in zip(TARGETS, ports))


def load_snapshot(path):
    """Read a bounded, schema-checked latest file; missing/invalid data is not a healthy state."""
    path = Path(path)
    try:
        if path.stat().st_size > 1_000_000:
            return None
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError, TypeError):
        return None
    if not isinstance(data, dict) or data.get('schema') != SCHEMA or not isinstance(data.get('targets'), list):
        return None
    return data


def collect_snapshot(targets=TARGETS, previous=None, timeout=2.0, captured_at_utc=None, opener=None):
    """Probe each target once and carry forward each target's last successful time."""
    captured_at_utc = captured_at_utc or utc_now()
    prior_by_id = {}
    if isinstance(previous, dict) and previous.get('schema') == SCHEMA:
        prior_by_id = {str(row.get('id')): row for row in previous.get('targets', [])
                       if isinstance(row, dict) and row.get('id') is not None}
    results = []
    for target in targets:
        row = probe_target(target, timeout=timeout, opener=opener)
        prior = prior_by_id.get(row['id'], {})
        if row['healthy']:
            row['consecutive_failures'] = 0
            row['last_successful_check_utc'] = captured_at_utc
        else:
            try:
                previous_failures = int(prior.get('consecutive_failures') or 0)
            except (TypeError, ValueError):
                previous_failures = 0
            row['consecutive_failures'] = min(1_000_000_000, max(0, previous_failures) + 1)
            row['last_successful_check_utc'] = prior.get('last_successful_check_utc')
        results.append(row)
    return {
        'schema': SCHEMA,
        'captured_at_utc': captured_at_utc,
        'scope': 'manual one-shot loopback preview check; not production monitoring or independent-site DR',
        'targets': results,
    }


def write_snapshot(snapshot, state_path=DEFAULT_STATE, latest_path=DEFAULT_LATEST):
    """Append an immutable sample and atomically publish its latest snapshot to local paths."""
    state_path = Path(state_path)
    latest_path = Path(latest_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(snapshot, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    with state_path.open('a', encoding='utf-8') as stream:
        stream.write(encoded + '\n')
        stream.flush()
        os.fsync(stream.fileno())
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=latest_path.parent,
                                         prefix=latest_path.name + '.', suffix='.tmp', delete=False) as stream:
            temp_name = stream.name
            stream.write(json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + '\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, latest_path)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def configured_latest_path():
    """An operator may set a local file path; no HTTP request can override it."""
    return Path(os.environ.get('VYOMARAJ_PROBE_LATEST', str(DEFAULT_LATEST)))


def render_monitor_html(latest_path=None):
    """Render a read-only HTML fragment. This function never probes or writes."""
    path = Path(latest_path) if latest_path is not None else configured_latest_path()
    snapshot = load_snapshot(path)
    parts = [
        '<h1>Local service monitor</h1>',
        '<p>This page only reads the latest local snapshot. It never starts a probe.</p>',
    ]
    if snapshot is None:
        parts += [
            '<p><strong>No probe has run yet, or the local snapshot is unreadable.</strong></p>',
            '<p>Start the four preview services, then run '
            '<code>python3 ops/vyomaraj-core/handover/probes.py --once '
            '--state /tmp/vyomaraj-probes.jsonl</code>.</p>',
            '<p>Scope: fixed loopback preview endpoints only; no production, alert-delivery, '
            'replication-lag or independent-site DR claim.</p>',
        ]
        return '\n'.join(parts)

    parts.append(f"<p>Captured at <code>{html.escape(str(snapshot.get('captured_at_utc', 'unknown')))}</code>. "
                 f"{html.escape(str(snapshot.get('scope', 'Local preview only.')))}</p>")
    parts += [
        '<div class="table"><table><thead><tr><th>Service</th><th>Port</th><th>Listener</th>'
        '<th>HTTP</th><th>Latency (ms)</th><th>Last successful check (UTC)</th>'
        '<th>Consecutive failures</th></tr></thead><tbody>'
    ]
    for row in snapshot['targets']:
        if not isinstance(row, dict):
            continue
        healthy = row.get('healthy') is True
        status = 'UP' if healthy else 'DOWN / UNKNOWN'
        listener = 'yes' if row.get('listening') is True else 'no'
        http_status = row.get('http_status') if row.get('http_status') is not None else '—'
        latency = row.get('latency_ms') if row.get('latency_ms') is not None else '—'
        last_success = row.get('last_successful_check_utc') or 'never recorded'
        failures = row.get('consecutive_failures', 0)
        values = (row.get('service', row.get('id', 'unknown')), row.get('port', '—'), listener,
                  http_status, latency, last_success, failures)
        parts.append('<tr><td>' + html.escape(status + ' — ' + str(values[0])) + '</td>'
                     + ''.join('<td>' + html.escape(str(value)) + '</td>' for value in values[1:])
                     + '</tr>')
    parts.append('</tbody></table></div>')
    parts.append('<p>One-shot local preview measurements only — not production monitoring, alert delivery, '
                 'replication-lag, backup or independent-site disaster-recovery evidence.</p>')
    return '\n'.join(parts)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--once', action='store_true', required=True,
                        help='run exactly one sample; recurring mode is deliberately not provided')
    parser.add_argument('--state', type=Path, default=DEFAULT_STATE,
                        help='append-only local JSONL log (default: /tmp/vyomaraj-probes.jsonl)')
    parser.add_argument('--latest', type=Path, default=None,
                        help='local latest JSON path (default: /tmp/vyomaraj-probes.latest.json)')
    for option, target in zip(('--viewer-port', '--gateway-port', '--lane-a-port', '--lane-b-port'), TARGETS):
        parser.add_argument(option, type=int, default=target['port'],
                            help=f'loopback TCP port (default: {target["port"]})')
    parser.add_argument('--timeout', type=float, default=2.0,
                        help='per-target timeout in seconds (0 < timeout <= 10)')
    args = parser.parse_args(argv)
    if not 0 < args.timeout <= 10:
        parser.error('--timeout must be greater than 0 and at most 10 seconds')
    try:
        targets = targets_with_ports((args.viewer_port, args.gateway_port,
                                      args.lane_a_port, args.lane_b_port))
    except ValueError as exc:
        parser.error(str(exc))
    latest = args.latest or configured_latest_path()
    previous = load_snapshot(latest)
    snapshot = collect_snapshot(targets=targets, previous=previous, timeout=args.timeout)
    write_snapshot(snapshot, args.state, latest)
    unhealthy = sum(1 for row in snapshot['targets'] if not row['healthy'])
    print(f"recorded {len(snapshot['targets'])} fixed loopback probes at {snapshot['captured_at_utc']}; "
          f"unhealthy={unhealthy}; latest snapshot: {latest}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
