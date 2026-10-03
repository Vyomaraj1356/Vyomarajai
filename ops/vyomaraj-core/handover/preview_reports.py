#!/usr/bin/env python3
"""Render only explicitly allowlisted sanitized handover reports; never serve repository paths."""
import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
REPORTS = {
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
}
DOWNLOADS = {'/download/inventory.md': REPORTS['/'],
             '/download/dr-status.md': REPORTS['/dr-status'],
             '/download/handover.txt': REPORTS['/handover']}
STYLE = '''body{margin:0;background:#f3f5f8;color:#152536;font:16px/1.65 system-ui,sans-serif}
main{max-width:1100px;margin:32px auto;padding:32px;background:white;border-radius:16px}
nav{display:flex;gap:20px;flex-wrap:wrap;padding:16px 0;border-bottom:1px solid #ccd5df}
a{color:#1759a7}h1,h2,h3{line-height:1.25;color:#102f52}h2{margin-top:48px;border-top:1px solid #dce3eb;padding-top:24px}
code{font-size:.88em;background:#edf2f7;padding:2px 4px;overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere}
.table{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #dce3eb;padding:10px;text-align:left;vertical-align:top}th{background:#e9eff6}
.notice{background:#fff4d6;padding:14px;border-left:4px solid #c18506}li{margin:5px 0}@media(max-width:700px){main{margin:0;padding:18px;border-radius:0}}'''


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


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlsplit(self.path).path
        filename = REPORTS.get(route) or DOWNLOADS.get(route)
        if filename is None:
            self.send_error(404, 'Only the allowlisted reports are available'); return
        path = HERE / filename
        if not path.is_file():
            self.send_error(404, 'Report not available'); return
        if route in DOWNLOADS:
            content = path.read_bytes()
            kind = 'text/plain; charset=utf-8'
        else:
            text = path.read_text(encoding='utf-8')
            body = markdown(text) if path.suffix == '.md' else '<pre>' + html.escape(text) + '</pre>'
            if route == '/reports/history':
                body = '<p class="notice"><strong>HISTORICAL SNAPSHOT — NOT CURRENT.</strong> Current total: 127 counted slots and six uncounted headings. See the current inventory and agent reconciliation.</p>' + body
            content = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                       '<meta name="viewport" content="width=device-width,initial-scale=1">'
                       '<title>Vyomaraj — verified reports</title><style>' + STYLE + '</style><main>'
                       '<nav><a href="/">Current inventory</a><a href="/reports/agents">Agent reconciliation</a><a href="/reports/history">Historical audit</a><a href="/dr-status">DR resolution</a>'
                       '<a href="/reports/research">Integrated research update</a><a href="/reports/contents">All experience contents</a><a href="/reports/film">Film</a><a href="/reports/music">Music</a><a href="/reports/bhakti">Bhakti</a><a href="/handover">Handover</a><a href="/download/inventory.md">Download inventory</a></nav>'
                       '<p class="notice">Sanitized source inventory. Unknown names and unverified live services '
                       'are not presented as working integrations. DR access is currently blocked.</p>'
                       + body + '</main></html>').encode()
            kind = 'text/html; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'")
        if route in DOWNLOADS:
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
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
