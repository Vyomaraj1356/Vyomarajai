#!/usr/bin/env python3
"""Allowlisted integrated preview + bounded deterministic planning API."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import re
import threading
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from local_planner import build_plan, InvalidPlan

CORE_ROOT = Path(__file__).resolve().parent.parent


def _load_governance_module(name):
    spec = importlib.util.spec_from_file_location(name, CORE_ROOT / name / (name + '_queue.py' if name == 'approvals' else {'finance': 'finance_followup.py', 'upgrades': 'change_manager.py'}[name]))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

CORE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('report_renderer', CORE / 'handover/preview_reports.py')
reports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reports)
research_spec = importlib.util.spec_from_file_location('vyomaraj_discovery', CORE / 'research/discovery.py')
discovery = importlib.util.module_from_spec(research_spec)
research_spec.loader.exec_module(discovery)
GOVERNANCE = {}
for module_name, file_name in (('approvals', 'approval_queue.py'),
                               ('finance', 'finance_followup.py'),
                               ('upgrades', 'change_manager.py')):
    _spec = importlib.util.spec_from_file_location(module_name, CORE / module_name / file_name)
    GOVERNANCE[module_name] = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(GOVERNANCE[module_name])

RESEARCH_STORE = None

def research_store():
    global RESEARCH_STORE
    if RESEARCH_STORE is None:
        RESEARCH_STORE = discovery.Store()
    return RESEARCH_STORE

ASSETS = {'/policy.json': (CORE / 'governance/PUBLIC_POLICY.json', 'application/json')}
for prefix, directory in [('/aghor/', 'aghor-experience'), ('/bhakti/', 'bhakti-experience'), ('/pairings/', 'liquor-bar'), ('/music/', 'music-experience'), ('/film/', 'film-experience'), ('/comics/', 'comics-experience'), ('/approvals/', 'approvals'), ('/finance/', 'finance'), ('/upgrades/', 'upgrades')]:
    for name, mime in [('index.html', 'text/html'), ('app.js', 'application/javascript'),
                       ('styles.css', 'text/css'), ('content.json', 'application/json')]:
        ASSETS[prefix + name] = (CORE / directory / name, mime)
    ASSETS[prefix] = ASSETS[prefix + 'index.html']
for name, mime in [('index.html','text/html'),('app.js','application/javascript'),('styles.css','text/css')]:
    ASSETS['/research/' + name] = (CORE / 'research' / name, mime)
ASSETS['/research/'] = ASSETS['/research/index.html']
ASSETS['/assets/pairings.css'] = (CORE / 'liquor-bar/styles.css', 'text/css')
ASSETS['/assets/fonts.css'] = (CORE / 'experience/assets/fonts.css', 'text/css')
ASSETS['/assets/devanagari.woff2'] = (CORE / 'experience/assets/devanagari.woff2', 'font/woff2')
for name, mime in [('index.html','text/html'),('app.js','application/javascript'),('styles.css','text/css'),('AGENT_REGISTRY_CURRENT.json','application/json'),('CONTENT_INDEX_CURRENT.json','application/json'),('CONTENT_OWNERSHIP_CURRENT.json','application/json')]:
    ASSETS['/agents/' + name] = (CORE / 'agents' / name, mime)
ASSETS['/agents/'] = ASSETS['/agents/index.html']
ASSETS['/education/'] = ASSETS['/agents/index.html']
REPORTS = {
    '/sovereign/': 'SOVEREIGN_POLICY_2026_10_03.md',
    '/contracts/': 'ENTERTAINMENT_CONTRACTS_2026_10_03.md',
    '/reports/policy': 'VIEW_ONLY_UPDATE_2026_10_03.md',
    '/reports/aghor': 'AGHOR_RESEARCH_2026_10_03.md',
    '/reports/resilience': 'DR_AGHOR_INTEGRATION_2026_10_03.md',
    '/reports/agents': 'AGENT_RECONCILIATION_2026_10_03.md',
    '/reports/history': 'HISTORICAL_SYSTEM_INVENTORY_2026_10_03.md',
    '/reports/research': 'RESEARCH_INTEGRATION_2026_10_03.md',
    '/reports/': 'FULL_SYSTEM_INVENTORY_2026_10_03.md',
    '/reports/bhakti': 'BHAKTI_FEATURE_UPDATE_2026_10_03.md',
    '/reports/film': 'FILM_THEATRE_ADS_UPDATE_2026_10_03.md',
    '/reports/contents': 'EXPERIENCE_CONTENTS_2026_10_03.md',
    '/reports/music': 'MUSIC_AUDIO_VIDEO_UPDATE_2026_10_03.md',
    '/reports/dr': 'DR_RESOLUTION_2026_10_03.md',
    '/reports/next-session': reports.HANDOVER_NOTE,
    '/reports/handover-notepad': reports.HANDOVER_NOTE,
    '/reports/recovery': reports.RECOVERY_DOC,
    '/reports/dr-sync': reports.DR_SYNC_REPORT,
    '/reports/post-pr25-handover': reports.POST_PR25_NOTE,
    '/reports/build': 'BUILD_AND_CONFIGURATION_2026_10_04.md',
    '/reports/architecture': 'ARCHITECTURE_V16_8_2026_10_04.md',
    '/reports/test-evidence': 'TEST_EVIDENCE_2026_10_04.json',
    '/reports/auto-align': 'AUTO_ALIGN_NEXT_SESSION_2026_10_04.md',
    '/reports/platform-check': 'PLATFORM_CONFIGURATION_CHECK_2026_10_04.md',
    '/reports/issues': 'ISSUES_AND_PRS_LEDGER_2026_10_04.md',
    '/reports/go-live': 'NAVARATRI_GO_LIVE_PLAN_2026_10_11.md',
    '/reports/stack': 'STACK_AND_PLATFORM_RECORD_2026_10_06.md',
    '/reports/network-diagram': 'ARCHITECTURE_V16_8_2026_10_04.md',
    '/reports/market-readiness': 'MARKET_READINESS_AND_WIRING_2026_10_06.md',
    '/reports/full-handover': 'VYOMARAJ_FULL_HANDOVER_2026_10_06.md',
    '/reports/ai-handoff': 'AI_PLATFORM_HANDOFF_2026_10_06.md',
    '/reports/runbook': 'VYOMARAJ_RUNBOOK_2026_10_06.md',
    '/reports/recovery-index': 'ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md',
    '/reports/go-live-gaps': 'GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md',
    '/reports/next-session-plan': 'NEXT_SESSION_PLAN_2026_10_07.md',
    '/reports/session-update': 'SESSION_UPDATE_2026_10_06.md',
}


def sync_status():
    """Replication facts taken from checked-in evidence.

    There is no live sync process in these servers, and this endpoint does not pretend there is:
    it reports what the repository can prove. The landing page used to poll /api/sync/status every
    four seconds and POST /api/sync/trigger every two minutes against an endpoint that never
    existed, so its status box hung on "Loading sync status..." forever.
    """
    path = CORE / 'handover' / reports.DR_SYNC_REPORT
    text = path.read_text(encoding='utf-8', errors='ignore') if path.is_file() else ''
    date = re.search(r'DR sync results — (\d{4}-\d{2}-\d{2})', text)
    tip = re.search(r'Main tip covered by this record: `([0-9a-f]{7,40})`', text)
    schedule = re.search(r'schedule: `([^`]+)`', text)
    return {
        'schema': 'vyomaraj-sync-status/1',
        'mode': 'repository_evidence_only',
        'isSyncing': False,
        'live_sync_process_running': False,
        'evidence_date': date.group(1) if date else None,
        'main_tip_covered': tip.group(1)[:8] if tip else None,
        'workflow_schedule_utc': schedule.group(1) if schedule else None,
        'detail': ('Replication is a GitHub Actions job on push and schedule, '
                   'not a background process in this page'),
        'source': str(path.relative_to(reports.ROOT)) if path.is_file() else None,
    }


class Handler(BaseHTTPRequestHandler):
    home_route = '/bhakti/'

    def send_bytes(self, content, mime, code=200):
        self.send_response(code)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        # img-src 'self' carries the same-origin capture gallery; no external image host is allowed.
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; media-src blob:; img-src 'self'; font-src 'self'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(content)

    def send_download(self, content, mime, filename):
        self.send_response(200)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(content)

    def json_response(self, data, code=200):
        self.send_bytes(json.dumps(data, ensure_ascii=False).encode(), 'application/json', code)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == '/':
            self.send_response(302)
            self.send_header('Location', self.home_route)
            self.send_header('Content-Length', '0')
            self.end_headers()
        elif route in ASSETS:
            path, mime = ASSETS[route]
            self.send_bytes(path.read_bytes(), mime)
        elif route == '/healthz':
            try:
                registry = json.loads((CORE / 'agents/AGENT_REGISTRY_CURRENT.json').read_text())
                ready = registry['totals']['sub_agents'] == len(registry['agents'])
            except (OSError, ValueError, KeyError):
                ready = False
            self.json_response({'ready': ready, 'scope': 'local_application_metadata_only', 'production_dr_verified': False}, 200 if ready else 503)
        elif route == '/api/realtime':
            self.json_response(reports._realtime().realtime_facts())
        elif route == '/reports/realtime':
            body = (reports.PAGE_NOTES.get(route, '') + reports._realtime().realtime_page()).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif route == '/reports/download/go-live-gaps.md':
            path = CORE / 'handover/GO_LIVE_GAPS_AND_PLATFORM_2026_10_06.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route in ('/reports/download/next-session-plan.md', '/reports/download/next-session-plan.txt'):
            path = CORE / 'handover/NEXT_SESSION_PLAN_2026_10_07.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route in ('/reports/download/session-update.md', '/reports/download/session-update.txt'):
            path = CORE / 'handover/SESSION_UPDATE_2026_10_06.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route == '/reports/download/recovery-index.md':
            path = CORE / 'handover/ARENA_SESSION_RECOVERY_INDEX_2026_10_06.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route == '/reports/download/recovery-manifest.json':
            path = CORE / 'handover/ARENA_SESSION_RECOVERY_MANIFEST_2026_10_06.json'
            self.send_download(path.read_bytes(), 'application/json', path.name)
        elif route == '/reports/download/ai-handoff.md':
            path = CORE / 'handover/AI_PLATFORM_HANDOFF_2026_10_06.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route == '/reports/download/ai-context-pack.json':
            path = CORE / 'handover/AI_CONTEXT_PACK_2026_10_06.json'
            self.send_download(path.read_bytes(), 'application/json', path.name)
        elif route == '/reports/download/runbook.md':
            path = CORE / 'handover/VYOMARAJ_RUNBOOK_2026_10_06.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route == '/reports/download/ai-handoff.zip':
            path = CORE / 'handover/transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip'
            self.send_download(path.read_bytes(), 'application/zip', path.name)
        elif route == '/reports/download/full-handover.md':
            path = CORE / 'handover/VYOMARAJ_FULL_HANDOVER_2026_10_06.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route == '/reports/download/full-handover.zip':
            path = CORE / 'handover/transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip'
            self.send_download(path.read_bytes(), 'application/zip', path.name)
        elif route == '/api/sync/status':
            self.json_response(sync_status())
        elif route == '/api/research/status':
            self.json_response(research_store().status())
        elif route == '/api/research/records':
            try:
                query = parse_qs(urlsplit(self.path).query)
                offset = int(query.get('offset', ['0'])[0])
                if not 0 <= offset <= 5000: raise ValueError()
            except ValueError:
                self.json_response({'error': 'invalid_offset'}, 400); return
            self.json_response({'records': research_store().records(offset)})
        elif route == '/api/research/export':
            self.json_response({'scope': 'unverified_metadata_not_media_or_licences', 'records': research_store().records(limit=5000)})
        elif route == '/api/status':
            self.json_response(json.loads((CORE / 'experience/LOCAL_INTEGRATION.json').read_text()))
        elif route == '/reports/download/bhakti.md':
            self.send_bytes((CORE / 'handover/BHAKTI_FEATURE_UPDATE_2026_10_03.md').read_bytes(), 'text/plain')
        elif route == '/reports/download/next-session.txt':
            self.send_download((CORE / 'handover' / reports.HANDOVER_NOTE).read_bytes(), 'text/plain; charset=utf-8', reports.HANDOVER_NOTE)
        elif route == '/reports/download/handover-notepad.txt':
            self.send_download((CORE / 'handover' / reports.HANDOVER_NOTE).read_bytes(), 'text/plain; charset=utf-8', reports.HANDOVER_NOTE)
        elif route == '/reports/download/transfer-package.zip':
            self.send_download((CORE / 'handover' / reports.TRANSFER_ZIP).read_bytes(), 'application/zip', Path(reports.TRANSFER_ZIP).name)
        elif route == '/reports/download/post-pr25-handover.txt':
            self.send_download((CORE / 'handover' / reports.POST_PR25_NOTE).read_bytes(), 'text/plain; charset=utf-8', reports.POST_PR25_NOTE)
        elif route == '/reports/download/post-pr25-transfer.zip':
            self.send_download((CORE / 'handover' / reports.POST_PR25_ZIP).read_bytes(), 'application/zip', Path(reports.POST_PR25_ZIP).name)
        elif route == '/reports/download/auto-align.json':
            path = CORE / 'handover/AUTO_ALIGN_NEXT_SESSION.json'
            self.send_download(path.read_bytes(), 'application/json', path.name)
        elif route == '/reports/download/platform-check.md':
            path = CORE / 'handover/PLATFORM_CONFIGURATION_CHECK_2026_10_04.md'
            self.send_download(path.read_bytes(), 'text/plain; charset=utf-8', path.name)
        elif route == '/reports/download/issues-ledger.json':
            path = CORE / 'handover/ISSUES_AND_PRS_LEDGER.json'
            self.send_download(path.read_bytes(), 'application/json', path.name)
        elif route.startswith('/reports/screenshot/'):
            name = route.rsplit('/', 1)[-1]
            path = reports.SCREENSHOTS_DIR / name
            if not reports.SCREENSHOT_NAME.fullmatch(name) or not path.is_file():
                self.send_error(404); return
            self.send_download(path.read_bytes(), reports.SCREENSHOT_MIME[path.suffix], name)
        elif route == '/reports/download/network-diagram.png':
            path = CORE / 'handover/ARCHITECTURE_DIAGRAM_2026_10_06.png'
            self.send_download(path.read_bytes(), 'image/png', path.name)
        elif route == '/reports/download/network-diagram.svg':
            path = CORE / 'handover/ARCHITECTURE_DIAGRAM_2026_10_06.svg'
            self.send_download(path.read_bytes(), 'image/svg+xml', path.name)
        elif route in REPORTS or route in reports.REFERENCE_REPORTS:
            path = (reports.REFERENCE_REPORTS[route] if route in reports.REFERENCE_REPORTS
                    else CORE / 'handover' / REPORTS[route])
            if not path.is_file():
                self.send_error(404); return
            body = reports.PAGE_NOTES.get(route, '') + reports.render_document(path)
            if route == '/reports/history':
                body = '<p class="notice"><strong>HISTORICAL SNAPSHOT — NOT THE CURRENT ROSTER.</strong> Current structure: see the current registry and inventory for authoritative counts; Education, Finance and Entertainment are registry-derived. See the current inventory or reconciliation above.</p>' + body
            if route == '/reports/recovery':
                body = reports.RECOVERY_LINKS + body
            page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<meta name="theme-color" content="#0a1628"><title>Vyomaraj reports</title><style>' + reports.STYLE + '</style><link rel="stylesheet" href="/assets/fonts.css"><main>'
                    '<nav aria-label="Viewer sections"><a href="/sovereign/">Sovereign</a><a href="/contracts/">Contracts</a><a href="/reports/policy">Latest policy update</a><a href="/aghor/">Aghor & Aghori</a><a href="/reports/resilience">DR & integration update</a><a href="/agents/">Current agents</a><a href="/education/">Education</a><a href="/reports/agents">Reconciliation</a><a href="/reports/history">Historical audit</a><a href="/research/">Research desk</a><a href="/reports/research">Integration report</a><a href="/film/">Film & stage</a><a href="/reports/film">Film report</a><a href="/comics/">Comics</a><a href="/reports/contents">All content</a><a href="/music/">Music & media</a><a href="/reports/music">Music report</a><a href="/bhakti/">Bhakti-Shakti</a><a href="/pairings/">Roots & Pairings</a>'
                    '<a href="/reports/">Full inventory</a><a href="/reports/bhakti">Bhakti update</a>'
                    '<a href="/reports/dr">DR status</a><a href="/reports/build">Build &amp; configuration</a><a href="/reports/next-session">Next session handover</a><a href="/reports/handover-notepad">Handover notepad</a><a href="/comics/">Comics</a><a href="/approvals/">Owner approvals</a><a href="/finance/">Finance desk</a><a href="/upgrades/">Change desk</a><a href="/reports/dr-sync">DR sync results</a><a href="/reports/recovery">Recovery package</a><a href="/reports/chats">All chats</a><a href="/reports/issue-6">Issue #6 resolution</a><a href="/reports/test-evidence">Test evidence</a><a href="/reports/auto-align">Auto-align plan</a><a href="/reports/platform-check">Platform check</a><a href="/reports/issues">New-session runbook (in order)</a><a href="/reports/next-session-plan">Next session plan</a><a href="/reports/session-update">Session update</a></nav>'
                    '<p class="notice">Entertainment and view-only spiritual content; participation is voluntary. No hazardous rituals or cure claims. Respect for humans, animals, religions, castes and creeds. Earning is not guaranteed. Local preview and creative planning are implemented. Git snapshot match evidence is in the DR report; external AI '
                    'and runtime/site disaster recovery are not verified.</p>' + body + '</main></html>')
            self.send_bytes(page.encode(), 'text/html')
        else:
            self.send_error(404, 'Only approved preview assets and reports are served')

    def do_POST(self):
        route = urlsplit(self.path).path
        if route not in ('/api/plan', '/api/research/run', '/api/research/review',
                         '/api/approvals/decide', '/api/finance/briefing', '/api/upgrades/plan'):
            self.send_error(404); return
        if route.startswith('/api/research/') or route.startswith('/api/approvals/') or route.startswith('/api/finance/') or route.startswith('/api/upgrades/'):
            origin = self.headers.get('Origin')
            if self.headers.get('Sec-Fetch-Site') == 'cross-site' or (origin and (urlsplit(origin).scheme not in ('http', 'https') or urlsplit(origin).netloc != self.headers.get('Host'))):
                self.json_response({'error': 'cross_origin_refused'}, 403); return
        if self.headers.get_content_type() != 'application/json':
            self.json_response({'error': 'Use application/json.'}, 415); return
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            self.json_response({'error': 'Invalid content length.'}, 400); return
        if not 0 < length <= 16384:
            self.json_response({'error': 'Request must be 1–16384 bytes.'}, 413); return
        self.connection.settimeout(10)
        try:
            data = json.loads(self.rfile.read(length))
            if route == '/api/plan':
                plan = build_plan(data)
            elif route == '/api/approvals/decide':
                if (not isinstance(data, dict) or set(data) - {'item_id', 'decision', 'voice_instruction'}
                        or not isinstance(data.get('item_id'), str) or not isinstance(data.get('decision'), str)):
                    raise GOVERNANCE['approvals'].InvalidApproval('item_id and decision are required.')
                plan = GOVERNANCE['approvals'].record_decision(
                    data['item_id'], data['decision'], data.get('voice_instruction'))
            elif route == '/api/finance/briefing':
                if not isinstance(data, dict) or set(data) != {'request'} or data['request'] != 'followup_and_briefing':
                    raise ValueError('request must be followup_and_briefing.')
                plan = {'schema_version': 1, 'status': 'local_followup_and_briefing_drafted',
                        'followup': GOVERNANCE['finance'].build_followup(),
                        'briefing': GOVERNANCE['finance'].build_morning_briefing(),
                        'drafts_only': True, 'notifications_sent': False}
            elif route == '/api/upgrades/plan':
                if isinstance(data, dict) and data.get('record') and data.get('decision'):
                    plan = GOVERNANCE['upgrades'].apply_permission(data['record'], data['decision'])
                elif isinstance(data, dict) and data.get('record') and data.get('failure'):
                    plan = GOVERNANCE['upgrades'].report_failure(data['record'], data['failure'])
                else:
                    plan = GOVERNANCE['upgrades'].plan_change(data)
            elif route == '/api/research/run':
                if not isinstance(data, dict) or set(data) != {'profile'} or not isinstance(data['profile'], str):
                    raise discovery.DiscoveryError('profile_only_request_required')
                self.json_response(research_store().enqueue(data['profile']), 202); return
            else:
                if not isinstance(data, dict) or set(data) != {'record_id', 'decision', 'acknowledge_metadata_only'} or data['acknowledge_metadata_only'] is not True or not isinstance(data['record_id'], str) or not isinstance(data['decision'], str):
                    raise discovery.DiscoveryError('metadata_only_acknowledgement_required')
                plan = research_store().review(data['record_id'], data['decision'])
        except discovery.DiscoveryError as exc:
            self.json_response({'error': str(exc)}, 400); return
        except InvalidPlan as exc:
            self.json_response({'error': str(exc)}, 400); return
        except GOVERNANCE['approvals'].InvalidApproval as exc:
            self.json_response({'error': str(exc)}, 400); return
        except GOVERNANCE['upgrades'].InvalidChange as exc:
            self.json_response({'error': str(exc)}, 400); return
        except (ValueError, UnicodeError, RecursionError):
            self.json_response({'error': 'Invalid JSON.'}, 400); return
        except (TimeoutError, OSError):
            self.json_response({'error': 'Request unavailable or timed out.'}, 408); return
        self.json_response(plan)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=4176)
    parser.add_argument('--home', choices=('bhakti', 'music', 'pairings', 'film', 'comics', 'research', 'agents', 'education', 'aghor', 'reports'), default='bhakti')
    args = parser.parse_args()
    Handler.home_route = '/' + args.home + '/'
    threading.Thread(target=discovery.worker_loop, args=(research_store(), threading.Event()), daemon=True).start()
    print(f'Vyomaraj Experience Studio on 0.0.0.0:{args.port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', args.port), Handler).serve_forever()
