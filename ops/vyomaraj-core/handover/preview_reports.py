#!/usr/bin/env python3
"""Render only explicitly allowlisted sanitized handover reports; never serve repository paths."""
import json
import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HANDOVER_NOTE = 'NEXT_SESSION_HANDOVER_2026_10_04.txt'
RECOVERY_DOC = 'RECOVERY_AND_HANDOVER_PACKAGE_2026_10_04.md'
DR_SYNC_REPORT = 'DR_SYNC_RESULTS_2026_10_04.md'
TRANSFER_ZIP = 'transfer/NEXT_SESSION_TRANSFER_2026_10_04.zip'
POST_PR25_NOTE = 'NEXT_SESSION_HANDOVER_POST_PR25_2026_10_04.txt'
POST_PR25_ZIP = 'transfer/NEXT_SESSION_UPDATE_POST_PR25_2026_10_04.zip'
REPORTS = {
    '/sovereign/': 'SOVEREIGN_POLICY_2026_10_03.md',
    '/contracts/': 'ENTERTAINMENT_CONTRACTS_2026_10_03.md',
    '/reports/policy': 'VIEW_ONLY_UPDATE_2026_10_03.md',
    '/reports/aghor': 'AGHOR_RESEARCH_2026_10_03.md',
    '/reports/resilience': 'DR_AGHOR_INTEGRATION_2026_10_03.md',
    '/reports/agents': 'AGENT_RECONCILIATION_2026_10_03.md',
    '/reports/history': 'HISTORICAL_SYSTEM_INVENTORY_2026_10_03.md',
    '/': 'FULL_SYSTEM_INVENTORY_2026_10_03.md',
    '/dr-status': 'DR_RESOLUTION_2026_10_03.md',
    '/reports/research': 'RESEARCH_INTEGRATION_2026_10_03.md',
    '/reports/contents': 'EXPERIENCE_CONTENTS_2026_10_03.md',
    '/reports/film': 'FILM_THEATRE_ADS_UPDATE_2026_10_03.md',
    '/reports/music': 'MUSIC_AUDIO_VIDEO_UPDATE_2026_10_03.md',
    '/reports/bhakti': 'BHAKTI_FEATURE_UPDATE_2026_10_03.md',
    '/handover': 'HANDOVER_ALL_UPDATES_2026_10_03.txt',
    '/reports/next-session': HANDOVER_NOTE,
    '/reports/handover-notepad': HANDOVER_NOTE,
    '/reports/recovery': RECOVERY_DOC,
    '/reports/dr-sync': DR_SYNC_REPORT,
    '/reports/post-pr25-handover': POST_PR25_NOTE,
    '/reports/architecture': 'ARCHITECTURE_V16_8_2026_10_04.md',
    '/reports/build': 'BUILD_AND_CONFIGURATION_2026_10_04.md',
    '/reports/test-evidence': 'TEST_EVIDENCE_2026_10_04.json',
    '/reports/auto-align': 'AUTO_ALIGN_NEXT_SESSION_2026_10_04.md',
    '/reports/platform-check': 'PLATFORM_CONFIGURATION_CHECK_2026_10_04.md',
    '/reports/issues': 'ISSUES_AND_PRS_LEDGER_2026_10_04.md',
    '/reports/go-live': 'NAVARATRI_GO_LIVE_PLAN_2026_10_11.md',
    '/reports/stack': 'STACK_AND_PLATFORM_RECORD_2026_10_06.md',
    '/reports/network-diagram': 'ARCHITECTURE_V16_8_2026_10_04.md',
    '/reports/market-readiness': 'MARKET_READINESS_AND_WIRING_2026_10_06.md',
    '/reports/full-handover': 'VYOMARAJ_FULL_HANDOVER_2026_10_06.md',
    '/reports/realtime': 'REALTIME_STATUS.md',
    '/reports/ai-handoff': 'AI_PLATFORM_HANDOFF_2026_10_06.md',
    '/reports/runbook': 'VYOMARAJ_RUNBOOK_2026_10_06.md',
}
# Canonical documents whose checked-in copy deliberately lives outside this directory. Each entry
# is a literal path fixed in code; no request value is ever joined to the filesystem, so the
# exact-route allowlist stays exact.
SCREENSHOTS_DIR = HERE / 'screenshots'


def screenshot_gallery():
    """Inline every capture that is small enough to send, link the rest. Never invent a caption."""
    if not SCREENSHOTS_DIR.is_dir():
        return '<p class="notice">No captures have been taken. Run capture_screens.mjs.</p>'
    manifest = SCREENSHOTS_DIR / 'SCREENSHOT_CAPTURE_RAW.json'
    meta = {}
    if manifest.is_file():
        import json as _json
        meta = {s['name']: s for s in _json.loads(manifest.read_text()).get('screenshots', [])}
    cards = []
    for png in sorted(list(SCREENSHOTS_DIR.glob('*.jpg')) + list(SCREENSHOTS_DIR.glob('*.png'))):
        size_mb = png.stat().st_size / 1e6
        record = meta.get(png.stem, {})
        caption = f"{record.get('title', png.stem)} — {record.get('url', '')} · {size_mb:.2f} MB"
        blocked = record.get('failed_requests') or []
        warn = (f'<br><strong>blocked sub-request:</strong> <code>{blocked[0]["url"][:90]}</code>'
                if blocked else '')
        if size_mb <= 2.5:
            body = (f'<img src="/reports/screenshot/{png.name}" alt="{png.stem} screenshot" '
                    f'style="max-width:100%;height:auto;border:1px solid #23405f;border-radius:10px">')
        else:
            body = (f'<p><em>{size_mb:.1f} MB — too large to display inline. '
                    f'<a href="/reports/screenshot/{png.name}">Open the full capture</a></em></p>')
        cards.append(f'<figure style="margin:26px 0">{body}<figcaption style="color:#94a3b8;'
                     f'font-size:13px;margin-top:8px">{caption}{warn}</figcaption></figure>')
    return ''.join(cards)


REFERENCE_REPORTS = {
    '/reports/chats': ROOT / 'Vyomaraj-All-Chats-Database-One-Month.md',
    '/reports/issue-6': ROOT / 'ops/dr/ISSUE_6_RESOLUTION_2026_10_04.md',
    '/reports/live-wiring': HERE / 'LIVE_WIRING_STATE_2026_10_06.json',
    '/reports/screenshots': SCREENSHOTS_DIR / 'SCREENSHOT_CAPTURE_RAW.json',
}
# Fixed, code-composed notices. Report text itself is never turned into markup or a hyperlink.
PAGE_NOTES = {
    '/reports/chats': '<p class="notice"><strong>All-chats count notice:</strong> the source heading says '
                      '28 chats while the file contains 34 numbered entries. The file is served unchanged; '
                      'owner confirmation is required before changing either count.</p>',
    '/reports/issue-6': '<p class="notice"><strong>Issue #6 resolution statement</strong> — acceptance '
                        'criteria, the correctly blocked run it followed, and the addenda that cite '
                        'the live DR record.</p>',
    '/reports/test-evidence': '<p class="notice"><strong>Recorded test evidence</strong> — the counts '
                              'are those actually executed at the recorded time, not a standing '
                              'promise about later runs.</p>',
    '/reports/go-live': '<p class="notice"><strong>Navaratri go-live plan</strong> — the four-day '
                        'run-up to Ghatasthapana, Sunday 11 October 2026: day-by-day plan, the '
                        'owner decisions that block it, the gates, and the risks in the order they '
                        'can stop a launch.</p>',
    '/reports/ai-handoff': '<p class="notice"><strong>Handoff for another AI platform</strong> - a '
                           'self-contained brief a different assistant can read to help without being '
                           'misled: the verified state, the agent structure, the platform truth and the '
                           'rules it must respect. Safe to share: owner contact details are redacted and '
                           'no secret is present. '
                           '<a href="/reports/download/ai-handoff.md">Download the brief</a> &middot; '
                           '<a href="/reports/download/ai-context-pack.json">Download the JSON context pack</a> '
                           '&middot; <a href="/reports/download/ai-handoff.zip">Download the whole package</a></p>',
    '/reports/runbook': '<p class="notice"><strong>Runbook</strong> - the procedure: start everything, '
                        'verify, regenerate evidence, configure a new thing, integrate with a platform, '
                        'inherit content, hand over and protect. '
                        '<a href="/reports/download/runbook.md">Download the runbook</a></p>',
    '/reports/realtime': '<p class="notice"><strong>Live status</strong> - measured on this request, never cached. '
                         'JSON at <a href="/api/realtime">/api/realtime</a>.</p>',
    '/reports/screenshots': '<p class="notice"><strong>Real captures of the running pages</strong> - taken with a '
                            'headless Chromium against the live servers, one file per page, hashes recorded in the '
                            'manifest below. Nothing here is a mock-up.</p>' + screenshot_gallery(),
    '/reports/market-readiness': '<p class="notice"><strong>Market readiness and wiring</strong> - what is configured, '
                                 'what is integrated, what was inherited, which parts of the vision are connected, and '
                                 'the exact free wiring needed before real earning. Generated from live checks.</p>',
    '/reports/full-handover': '<p class="notice"><strong>Full handover — all details</strong> - real-time '
                              'state, the chats record, the complete agent tree, the Vyomaraj and Jarvis '
                              'configurations, every AI platform and what is connected, and the issue '
                              'research. <a href="/reports/download/full-handover.md">Download the document</a> '
                              '&middot; <a href="/reports/download/full-handover.zip">Download everything as '
                              'one archive</a></p>',
    '/reports/network-diagram': '<p class="notice"><strong>Network and architecture diagram</strong> - '
                                'generated from the verified stack record, layer by layer: people, live '
                                'delivery, browser runtime, local rehearsal, automation, DR, and what is not '
                                'owned. Red means claimed with nothing running behind it. '
                                '<a href="/reports/download/network-diagram.png">Download the colour PNG</a> &middot; '
                                '<a href="/reports/download/network-diagram.svg">Download the SVG</a></p>',
    '/reports/stack': '<p class="notice"><strong>Stack and platform record</strong> — what the '
                      'product is actually built on, the whole one-month archive with hashes, and '
                      'which claims in the old market-ready README have nothing running behind '
                      'them. Read section 3 before repeating any figure from it.</p>',
    '/reports/live-wiring': '<p class="notice"><strong>Live wiring state</strong> — generated by '
                            'verify_live_wiring.py against the running stack: which routes answer, '
                            'which downloads are byte-identical, how each lane pack binds to the '
                            'current agent registry, and what is explicitly not verified.</p>',
    '/reports/post-pr25-handover': '<p class="notice"><strong>Post-PR25 companion</strong> — created on '
                                   '2026-10-06 after this file was found to be missing from the '
                                   'repository; it records checkpoint #20 and the two windows in which '
                                   'verify-or-sync did not execute. Read its section 0 before quoting '
                                   'any earlier claim about it.</p>',
}
# route -> (file relative to this directory, exact content type)
DOWNLOADS = {'/download/inventory.md': (REPORTS['/'], 'text/plain; charset=utf-8'),
             '/download/dr-status.md': (REPORTS['/dr-status'], 'text/plain; charset=utf-8'),
             '/download/handover.txt': (REPORTS['/handover'], 'text/plain; charset=utf-8'),
             '/reports/download/next-session.txt': (HANDOVER_NOTE, 'text/plain; charset=utf-8'),
             '/reports/download/handover-notepad.txt': (HANDOVER_NOTE, 'text/plain; charset=utf-8'),
             '/reports/download/transfer-package.zip': (TRANSFER_ZIP, 'application/zip'),
             '/reports/download/post-pr25-handover.txt': (POST_PR25_NOTE, 'text/plain; charset=utf-8'),
             '/reports/download/post-pr25-transfer.zip': (POST_PR25_ZIP, 'application/zip'),
             '/reports/download/auto-align.json': ('AUTO_ALIGN_NEXT_SESSION.json', 'application/json'),
             '/reports/download/platform-check.md': ('PLATFORM_CONFIGURATION_CHECK_2026_10_04.md', 'text/plain; charset=utf-8'),
             '/reports/download/issues-ledger.json': ('ISSUES_AND_PRS_LEDGER.json', 'application/json'),
             '/reports/download/network-diagram.png':
                 ('ARCHITECTURE_DIAGRAM_2026_10_06.png', 'image/png'),
             '/reports/download/network-diagram.svg':
                 ('ARCHITECTURE_DIAGRAM_2026_10_06.svg', 'image/svg+xml'),
             '/reports/download/full-handover.zip':
                 ('transfer/VYOMARAJ_FULL_HANDOVER_2026_10_06.zip', 'application/zip'),
             '/reports/download/full-handover.md':
                 ('VYOMARAJ_FULL_HANDOVER_2026_10_06.md', 'text/plain; charset=utf-8'),
             '/reports/download/ai-handoff.md':
                 ('AI_PLATFORM_HANDOFF_2026_10_06.md', 'text/plain; charset=utf-8'),
             '/reports/download/ai-context-pack.json':
                 ('AI_CONTEXT_PACK_2026_10_06.json', 'application/json'),
             '/reports/download/runbook.md':
                 ('VYOMARAJ_RUNBOOK_2026_10_06.md', 'text/plain; charset=utf-8'),
             '/reports/download/ai-handoff.zip':
                 ('transfer/AI_PLATFORM_HANDOFF_2026_10_06.zip', 'application/zip')}
# Literal, code-composed links only: no report text is ever turned into a hyperlink.
RECOVERY_LINKS = ('<div class="notice"><strong>New-session runbook (in order):</strong> '
                  '<a href="/reports/issues">Issues and PRs ledger</a> &middot; '
                  '<a href="/reports/auto-align">Auto-align execution plan</a> &middot; '
                  '<a href="/reports/platform-check">Platform completion paths</a> &middot; '
                  '<a href="/reports/next-session">Next session handover</a> &middot; '
                  '<a href="/reports/download/next-session.txt">Download Notepad .txt</a> &middot; '
                  '<a href="/reports/dr-sync">DR sync results</a> &middot; '
                  '<a href="/reports/download/transfer-package.zip">Download transfer package .zip</a> &middot; '
                  '<a href="/reports/post-pr25-handover">Post-PR25 companion</a> &middot; '
                  '<a href="/reports/download/post-pr25-transfer.zip">Download post-PR25 package .zip</a></div>')
STYLE = '''body{margin:0;background:#0a1628;color:#e9eff7;font:16px/1.65 system-ui,sans-serif}
main{max-width:1100px;margin:32px auto;padding:32px;background:#0e2138;border:1px solid #23405f;border-radius:16px}
nav{display:flex;gap:18px;flex-wrap:wrap;padding:14px 0;border-bottom:1px solid #23405f}
a{color:#f5c96b}a:hover{color:#ffe0a3}h1,h2,h3{line-height:1.25;color:#f59e0b}h2{margin-top:48px;border-top:1px solid #23405f;padding-top:24px}
code{font-size:.88em;background:#132b47;color:#ffe0a3;padding:2px 4px;overflow-wrap:anywhere;border-radius:4px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#081524;border:1px solid #23405f;border-radius:10px;padding:14px}
.table{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #23405f;padding:10px;text-align:left;vertical-align:top}th{background:#16334f;color:#f5c96b}tr:nth-child(even) td{background:#0c1c2f}
.notice{background:#2a2109;padding:14px;border-left:4px solid #f59e0b;border-radius:6px}li{margin:5px 0}@media(max-width:700px){main{margin:0;padding:18px;border-radius:0}}'''
# The palette above is the Vyomaraj product palette (Shani Blue #0a1628, Kuber Gold #f59e0b).
# It is defined once here; every page of both report servers inherits it from this constant.



def inline(text):
    # Escape first; deliberately do not enable raw HTML or arbitrary hyperlinks.
    escaped = html.escape(text)
    escaped = re.sub(r'`([^`]+)`', r'<code>\1</code>', escaped)
    return re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', escaped)


def markdown(text):
    result, table, listing = [], False, False
    for line in text.splitlines():
        is_table = line.startswith('|') and line.endswith('|')
        is_list = line.startswith('- ')
        if table and not is_table:
            result.append('</tbody></table></div>'); table = False
        if listing and not is_list:
            result.append('</ul>'); listing = False
        if is_table:
            cells = re.split(r'(?<!\\)\|', line[1:-1])
            if all(re.fullmatch(r'\s*:?-+:?\s*', x) for x in cells):
                continue
            if not table:
                result.append('<div class="table"><table><tbody>')
                tag = 'th'; table = True
            else:
                tag = 'td'
            result.append('<tr>' + ''.join(f'<{tag}>{inline(x.strip().replace(chr(92)+"|", "|"))}</{tag}>' for x in cells) + '</tr>')
        elif is_list:
            if not listing:
                result.append('<ul>'); listing = True
            result.append('<li>' + inline(line[2:]) + '</li>')
        elif line.startswith('#'):
            match = re.match(r'^(#{1,6}) (.*)$', line)
            if match:
                n = len(match[1]); result.append(f'<h{n}>{inline(match[2])}</h{n}>')
            else:
                result.append('<p>' + inline(line) + '</p>')
        elif line.strip():
            result.append('<p>' + inline(line) + '</p>')
    if table: result.append('</tbody></table></div>')
    if listing: result.append('</ul>')
    return '\n'.join(result)


def render_document(path):
    """Render one allowlisted document to an HTML body. Non-markdown suffixes stay escaped text."""
    text = path.read_text(encoding='utf-8')
    if path.suffix == '.md':
        return markdown(text)
    if path.suffix == '.json':
        return ('<p class="notice">Machine-readable evidence, served exactly as recorded in the '
                'repository.</p><pre>' + html.escape(text) + '</pre>')
    return '<pre>' + html.escape(text) + '</pre>'


SCREENSHOT_NAME = re.compile(r'^[a-z0-9-]+\.(png|jpg)$')


def _realtime():
    import importlib.util as _ilu
    spec = _ilu.spec_from_file_location('realtime_status', HERE / 'realtime_status.py')
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
SCREENSHOT_MIME = {'.png': 'image/png', '.jpg': 'image/jpeg'}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path).path
        if route == '/api/realtime':
            body = json.dumps(_realtime().realtime_facts(), indent=2).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if route.startswith('/reports/screenshot/'):
            name = route.rsplit('/', 1)[-1]
            path = SCREENSHOTS_DIR / name
            if not SCREENSHOT_NAME.fullmatch(name) or not path.is_file():
                self.send_error(404, 'Only captured screenshots are available'); return
            content = path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', SCREENSHOT_MIME[path.suffix])
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(content)
            return
        if route == '/reports/realtime':
            body = (PAGE_NOTES.get(route, '') + _realtime().realtime_page()).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        filename = REPORTS.get(route) or (DOWNLOADS.get(route) or (None,))[0]
        if filename is None and route not in REFERENCE_REPORTS:
            self.send_error(404, 'Only the allowlisted reports are available'); return
        path = REFERENCE_REPORTS[route] if route in REFERENCE_REPORTS else HERE / filename
        if not path.is_file():
            self.send_error(404, 'Report not available'); return
        if route in DOWNLOADS:
            content = path.read_bytes()
            kind = DOWNLOADS[route][1]
        else:
            body = PAGE_NOTES.get(route, '') + render_document(path)
            if route == '/reports/history':
                body = '<p class="notice"><strong>HISTORICAL SNAPSHOT — NOT CURRENT.</strong> Current total: 128 counted slots and six uncounted headings. See the current inventory and agent reconciliation.</p>' + body
            if route == '/reports/recovery':
                body = RECOVERY_LINKS + body
            content = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                       '<meta name="viewport" content="width=device-width,initial-scale=1">'
                       '<meta name="theme-color" content="#0a1628">'
                       '<title>Vyomaraj — verified reports</title><style>' + STYLE + '</style><main>'
                       '<nav aria-label="Viewer sections"><a href="/sovereign/">Sovereign</a><a href="/contracts/">Contracts</a><a href="/reports/policy">Latest policy update</a><a href="/">Current inventory</a><a href="/reports/resilience">Latest DR & integration</a><a href="/reports/aghor">Aghor research</a><a href="/reports/agents">Agent reconciliation</a><a href="/reports/history">Historical audit</a><a href="/dr-status">DR resolution</a>'
                       '<a href="/reports/research">Integrated research update</a><a href="/reports/contents">All experience contents</a><a href="/reports/film">Film</a><a href="/reports/music">Music</a><a href="/reports/bhakti">Bhakti</a><a href="/handover">Handover</a><a href="/comics/">Comics</a><a href="/approvals/">Owner approvals</a><a href="/finance/">Finance desk</a><a href="/upgrades/">Change desk</a><a href="/reports/architecture">Architecture</a><a href="/reports/build">Build &amp; configuration</a><a href="/reports/next-session">Next session handover</a><a href="/reports/handover-notepad">Handover notepad</a><a href="/reports/dr-sync">DR sync results</a><a href="/reports/post-pr25-handover">Post-PR25 companion</a><a href="/reports/recovery">Recovery package</a><a href="/reports/chats">All chats</a><a href="/reports/issue-6">Issue #6 resolution</a><a href="/reports/test-evidence">Test evidence</a><a href="/reports/auto-align">Auto-align plan</a><a href="/reports/platform-check">Platform check</a><a href="/reports/issues">New-session runbook (in order)</a><a href="/reports/network-diagram">Network diagram</a><a href="/reports/screenshots">Real page captures</a><a href="/reports/market-readiness">Market readiness</a><a href="/reports/realtime">Live status</a><a href="/reports/full-handover">Full handover</a><a href="/reports/ai-handoff">AI handoff</a><a href="/reports/runbook">Runbook</a><a href="/download/inventory.md">Download inventory</a></nav>'
                       '<p class="notice">Sanitized source inventory. Unknown names and unverified live services '
                       'are not presented as working integrations. Git snapshot match evidence is in the DR report; runtime/site disaster recovery remains unverified.</p>'
                       + body + '</main></html>').encode()
            kind = 'text/html; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        # 'img-src self' is required for the capture gallery: same-origin images only, still no scripts,
        # no external hosts, no frames. Without it the hardened default-src 'none' blocks every image.
        self.send_header('Content-Security-Policy',
                         "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'; base-uri 'none'")
        if route in DOWNLOADS:
            self.send_header('Content-Disposition', f'attachment; filename="{Path(filename).name}"')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass  # Do not record user URLs, headers or query values.


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=4174)
    args = parser.parse_args()
    print(f'Report viewer listening on 0.0.0.0:{args.port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', args.port), Handler).serve_forever()
