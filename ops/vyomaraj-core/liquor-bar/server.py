#!/usr/bin/env python3
"""Serve only the reviewed Liquor/Bar prototype assets, never the repository root."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
FILES = {'/': ('index.html', 'text/html'), '/index.html': ('index.html', 'text/html'),
         '/app.js': ('app.js', 'application/javascript'), '/styles.css': ('styles.css', 'text/css'),
         '/content.json': ('content.json', 'application/json')}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        item = FILES.get(urlsplit(self.path).path)
        if not item:
            self.send_error(404, 'Not an allowlisted prototype asset'); return
        filename, mime = item
        content = (ROOT / filename).read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Security-Policy', "default-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; form-action 'none'")
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=4175)
    args = parser.parse_args()
    print(f'Roots & Pairings preview on 0.0.0.0:{args.port}', flush=True)
    ThreadingHTTPServer(('0.0.0.0', args.port), Handler).serve_forever()
