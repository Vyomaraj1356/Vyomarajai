#!/usr/bin/env python3
"""Allowlisted integrated preview + bounded deterministic planning API."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
from pathlib import Path
from urllib.parse import urlsplit

from local_planner import build_plan, InvalidPlan

CORE = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('report_renderer', CORE / 'handover/preview_reports.py')
reports = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reports)
ASSETS = {}
for prefix, directory in [('/bhakti/', 'bhakti-experience'), ('/pairings/', 'liquor-bar'), ('/music/', 'music-experience'), ('/film/', 'film-experience')]:
    for name, mime in [('index.html', 'text/html'), ('app.js', 'application/javascript'),
                       ('styles.css', 'text/css'), ('content.json', 'application/json')]:
        ASSETS[prefix + name] = (CORE / directory / name, mime)
    ASSETS[prefix] = ASSETS[prefix + 'index.html']
ASSETS['/assets/pairings.css'] = (CORE / 'liquor-bar/styles.css', 'text/css')
ASSETS['/assets/fonts.css'] = (CORE / 'experience/assets/fonts.css', 'text/css')
ASSETS['/assets/devanagari.woff2'] = (CORE / 'experience/assets/devanagari.woff2', 'font/woff2')
REPORTS = {
    '/reports/': 'FULL_SYSTEM_INVENTORY_2026_10_03.md',
    '/reports/bhakti': 'BHAKTI_FEATURE_UPDATE_2026_10_03.md',
    '/reports/film': 'FILM_THEATRE_ADS_UPDATE_2026_10_03.md',
    '/reports/contents': 'EXPERIENCE_CONTENTS_2026_10_03.md',
    '/reports/music': 'MUSIC_AUDIO_VIDEO_UPDATE_2026_10_03.md',
    '/reports/dr': 'DR_RESOLUTION_2026_10_03.md',
}


class Handler(BaseHTTPRequestHandler):
    home_route = '/bhakti/'

    def send_bytes(self, content, mime, code=200):
        self.send_response(code)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; media-src blob:; font-src 'self'; base-uri 'none'; form-action 'none'")
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
        elif route == '/api/status':
            self.json_response(json.loads((CORE / 'experience/LOCAL_INTEGRATION.json').read_text()))
        elif route == '/reports/download/bhakti.md':
            self.send_bytes((CORE / 'handover/BHAKTI_FEATURE_UPDATE_2026_10_03.md').read_bytes(), 'text/plain')
        elif route in REPORTS:
            path = CORE / 'handover' / REPORTS[route]
            if not path.is_file():
                self.send_error(404); return
            body = reports.markdown(path.read_text())
            page = ('<!doctype html><html lang="en"><meta charset="utf-8">'
                    '<meta name="viewport" content="width=device-width,initial-scale=1">'
                    '<title>Vyomaraj reports</title><style>' + reports.STYLE + '</style><link rel="stylesheet" href="/assets/fonts.css"><main>'
                    '<nav><a href="/film/">Film & stage</a><a href="/reports/film">Film report</a><a href="/reports/contents">All content</a><a href="/music/">Music & media</a><a href="/reports/music">Music report</a><a href="/bhakti/">Bhakti-Shakti</a><a href="/pairings/">Roots & Pairings</a>'
                    '<a href="/reports/">Full inventory</a><a href="/reports/bhakti">Bhakti update</a>'
                    '<a href="/reports/dr">DR status</a></nav>'
                    '<p class="notice">Local preview and planning are implemented. External AI, production deployment '
                    'and DR synchronization are not verified.</p>' + body + '</main></html>')
            self.send_bytes(page.encode(), 'text/html')
        else:
            self.send_error(404, 'Only approved preview assets and reports are served')

    def do_POST(self):
        if urlsplit(self.path).path != '/api/plan':
            self.send_error(404); return
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
            plan = build_plan(data)
        except InvalidPlan as exc:
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
    parser.add_argument('--home', choices=('bhakti', 'music', 'pairings', 'film'), default='bhakti')
    args = parser.parse_args()
    Handler.home_route = '/' + args.home + '/'
    print(f'Vyomaraj Experience Studio on 0.0.0.0:{args.port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', args.port), Handler).serve_forever()
