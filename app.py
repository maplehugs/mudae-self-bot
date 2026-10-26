"""Start the bot and its control panel: `python app.py`, then open http://127.0.0.1:8765"""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

import mudae

PORT = 8765
UI = Path(__file__).with_name('ui.html')
ACTIONS = {
    '/api/start': mudae.start,
    '/api/stop': mudae.stop,
    '/api/roll': mudae.roll,
    '/api/test-alert': lambda: mudae.alert('🔔 Prueba de alerta del bot de Mudae'),
}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def reply(self, body, ctype='application/json', code=200):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def trusted(self):
        # Host check blocks DNS rebinding (other sites reading the token); JSON-only POST blocks CSRF.
        host_ok = self.headers.get('Host') in (f'127.0.0.1:{PORT}', f'localhost:{PORT}')
        return host_ok and (self.command == 'GET' or self.headers.get('Content-Type') == 'application/json')

    def do_GET(self):
        if not self.trusted():
            return self.reply({'error': 'forbidden'}, code=403)
        url = urlparse(self.path)
        query = parse_qs(url.query, keep_blank_values=True)
        if self.path == '/':
            self.reply(UI.read_bytes(), 'text/html; charset=utf-8')
        elif self.path == '/api/state':
            self.reply(mudae.state())
        elif self.path == '/api/config':
            self.reply(mudae.cfg)
        elif self.path == '/api/names':
            self.reply(mudae.names())
        elif url.path in ('/api/guilds', '/api/channels'):
            guild = query.get('guild', [''])[0]
            try:
                if url.path == '/api/guilds':
                    self.reply(mudae.guilds(refresh='refresh' in query))
                elif guild.isdigit():  # goes into a Discord URL
                    self.reply(mudae.channels(guild))
                else:
                    self.reply({'error': 'guild inválido'}, code=400)
            except (ValueError, requests.RequestException) as e:
                self.reply({'error': str(e)}, code=502)
        else:
            self.reply({'error': 'not found'}, code=404)

    def do_POST(self):
        if not self.trusted():
            return self.reply({'error': 'forbidden'}, code=403)
        if self.path == '/api/config':
            try:
                mudae.save_config(json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0)))))
            except ValueError:
                return self.reply({'error': 'bad json'}, code=400)
            return self.reply(mudae.cfg)
        if self.path not in ACTIONS:
            return self.reply({'error': 'not found'}, code=404)
        mudae.run_bg(ACTIONS[self.path])
        self.reply({'ok': True})


if __name__ == '__main__':
    mudae.start_scheduler()
    if mudae.cfg['token']:
        mudae.run_bg(mudae.start)
    print(f'Panel: http://127.0.0.1:{PORT}')
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
