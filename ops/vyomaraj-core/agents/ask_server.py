#!/usr/bin/env python3
"""Ask-the-catalog HTTP surface: a small read-only server over ask_catalog.Catalog.

Endpoints (all GET, no writes, no external calls):

  /                the search page
  /api/ask?q=...   cited retrieval results (JSON)
  /api/stats       what the catalog contains, counted from the files
  /health          liveness

Retrieval only. No model key is configured and no generated text is ever returned,
so a question the catalog cannot answer comes back as an empty result list.
"""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

from ask_catalog import Catalog, HERE

PAGE = HERE / 'ask.html'
CATALOG = None


def catalog():
    global CATALOG
    if CATALOG is None:
        CATALOG = Catalog()
    return CATALOG


class Handler(BaseHTTPRequestHandler):
    server_version = 'VyomarajAskCatalog/1.0'

    def _send(self, status, body, content_type):
        payload = body if isinstance(body, bytes) else body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(payload)

    def _json(self, status, data):
        self._send(status, json.dumps(data, ensure_ascii=False, indent=2) + '\n', 'application/json; charset=utf-8')

    def do_GET(self):
        parts = urlsplit(self.path)
        path = parts.path.rstrip('/') or '/'
        try:
            if path == '/':
                self._send(200, PAGE.read_bytes(), 'text/html; charset=utf-8')
            elif path == '/health':
                self._json(200, {'status': 'ok', 'service': 'ask-catalog'})
            elif path == '/api/stats':
                self._json(200, catalog().stats())
            elif path == '/api/ask':
                params = parse_qs(parts.query)
                query = (params.get('q') or [''])[0]
                limit = (params.get('limit') or ['10'])[0]
                self._json(200, catalog().ask(query, limit=limit))
            else:
                self._json(404, {'error': 'not found', 'paths': ['/', '/api/ask?q=', '/api/stats', '/health']})
        except ValueError as exc:
            self._json(400, {'error': str(exc)})

    def log_message(self, fmt, *args):
        print('ask-catalog %s - %s' % (self.address_string(), fmt % args), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0', help='bind address (default 0.0.0.0 so a preview can reach it)')
    parser.add_argument('--port', type=int, default=4190)
    args = parser.parse_args()
    stats = catalog().stats()
    print(f"Ask the catalog on http://{args.host}:{args.port} — "
          f"{stats['positions']} positions, {stats['content_references']} content references, "
          f"{stats['categories']} categories. Retrieval only; no model call.", flush=True)
    ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
