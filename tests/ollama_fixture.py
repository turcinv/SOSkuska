"""Loopback-only Ollama protocol fixture. No real models or cloud requests."""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class FakeOllama:
    def __init__(self):
        self.mode = 'ok'
        self.status = 200
        self.model_names = ['study-model:latest']
        self.models_payload = None
        self.error_detail = 'model unavailable'
        self.requests = []
        self.gate = threading.Event()
        fixture = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_):
                pass

            def do_GET(self):
                fixture.requests.append(('GET', self.path, None))
                if fixture.mode == 'slow_models':
                    fixture.gate.wait(3)
                payload = fixture.models_payload if fixture.models_payload is not None else {'models': [{'name': n} for n in fixture.model_names]}
                self.send_response(fixture.status)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                try:
                    self.wfile.write(json.dumps(payload).encode())
                except OSError:
                    pass

            def do_POST(self):
                payload = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))))
                fixture.requests.append(('POST', self.path, payload))
                self.send_response(fixture.status)
                self.send_header('Content-Type', 'application/x-ndjson')
                self.end_headers()
                try:
                    mode = fixture.mode
                    if fixture.status != 200:
                        self.wfile.write(json.dumps({'error': fixture.error_detail}).encode())
                        return
                    if mode == 'malformed':
                        self.wfile.write(b'not json\n')
                        return
                    if mode == 'surrogate':
                        self.wfile.write((json.dumps({'message': {'content': chr(0xd800)}, 'done': True})+'\n').encode())
                        return
                    if mode == 'error_surrogate':
                        self.wfile.write((json.dumps({'error': chr(0xd800)})+'\n').encode())
                        return
                    if mode == 'error':
                        self.wfile.write(b'{"error":"out of memory"}\n')
                        return
                    if mode == 'oversized':
                        self.wfile.write((json.dumps({'message': {'content': 'x' * 17000}, 'done': True})+'\n').encode())
                        return
                    if mode == 'huge_line':
                        self.wfile.write(b'x' * 262145)
                        return
                    if mode == 'stall':
                        self.wfile.write(b'{"message":')
                        self.wfile.flush()
                        fixture.gate.wait(3)
                        return
                    if mode == 'empty':
                        self.wfile.write(b'{"done":true}\n')
                        return
                    if mode == 'thinking':
                        self.wfile.write(b'{"message":{"thinking":"internal"},"done":false}\n')
                    self.wfile.write((json.dumps({'message': {'content': 'Hello '}, 'done': False})+'\n').encode())
                    self.wfile.flush()
                    if mode == 'slow':
                        fixture.gate.wait(3)
                    if mode == 'eof':
                        return
                    self.wfile.write((json.dumps({'message': {'content': 'svět / мир'}, 'done': True}, ensure_ascii=False)+'\n').encode())
                    self.wfile.flush()
                except (OSError, BrokenPipeError):
                    pass

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={'poll_interval': 0.05}, daemon=True)
        self.url = f'http://127.0.0.1:{self.server.server_port}'
        self.thread.start()

    def close(self):
        self.gate.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)
