"""Small direct Ollama HTTP client; no Tk, proxies, redirects or cloud fallback."""
import http.client
import json
import socket
import ssl
import threading
from contextlib import contextmanager
from urllib.parse import urlsplit

MAX_REPLY = 16000
MAX_LINE = 262144


class OllamaError(ValueError):
    pass


class Cancelled(OllamaError):
    pass


class RequestControl:
    def __init__(self):
        self.cancelled = threading.Event()
        self.timed_out = False
        self.lock = threading.Lock()
        self.connection = None
        self.transport_socket = None

    def attach(self, connection):
        with self.lock:
            self.connection = connection
        self.check()

    def check(self):
        if self.cancelled.is_set():
            if self.timed_out:
                raise OllamaError("Ollama request timed out. Please retry or choose a smaller model.")
            raise Cancelled("Stopped.")

    def cancel(self, timeout=False):
        self.timed_out = timeout
        self.cancelled.set()
        with self.lock:
            connection = self.connection
            sock = (connection.sock if connection is not None else None) or self.transport_socket
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass


def endpoint_url(value):
    value = value.strip()
    try:
        value.encode('utf-8')
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        raise OllamaError("Use an HTTP or HTTPS server URL, for example http://127.0.0.1:11434.") from None
    if (port == 0 or parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.path not in ("", "/") or parsed.query or parsed.fragment
            or any(c.isspace() for c in value)):
        raise OllamaError("Use a server URL without credentials, a path, query or fragment.")
    host = f'[{parsed.hostname}]' if ':' in parsed.hostname else parsed.hostname
    return f'{parsed.scheme}://{host}' + (f':{port}' if port is not None else '')


def safe_detail(value):
    # JSON permits escaped lone surrogates; Tcl requires encodable Unicode.
    return str(value).encode('utf-8', errors='replace').decode('utf-8')[:300]


class ControlledHTTPSConnection(http.client.HTTPConnection):
    """Expose the live TLS socket before its cancellable blocking handshake."""
    default_port = 443

    def __init__(self, host, port, control, **kwargs):
        super().__init__(host, port, **kwargs)
        self.control = control

    def connect(self):
        super().connect()
        context = ssl.create_default_context()
        self.control.check()
        self.sock = context.wrap_socket(self.sock, server_hostname=self.host, do_handshake_on_connect=False)
        with self.control.lock:
            self.control.transport_socket = self.sock
        self.control.check()
        self.sock.do_handshake()


class OllamaClient:
    def __init__(self, endpoint, *, timeout=30, total_timeout=180):
        self.endpoint = endpoint_url(endpoint)
        self.timeout = timeout
        self.total_timeout = total_timeout

    @contextmanager
    def _request(self, path, control, payload=None):
        control.check()
        parsed = urlsplit(self.endpoint)
        connection = (ControlledHTTPSConnection(parsed.hostname, parsed.port, control, timeout=self.timeout)
                      if parsed.scheme == 'https' else http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=self.timeout))
        control.attach(connection)
        # A wall-clock bound also stops a server that trickles data forever.
        timer = threading.Timer(self.total_timeout, lambda: control.cancel(timeout=True))
        timer.daemon = True
        timer.start()
        response = None
        try:
            body = json.dumps(payload, ensure_ascii=False).encode('utf-8') if payload is not None else None
            control.check()
            # HTTPConnection.request otherwise connects lazily and can send a
            # cancelled prompt immediately after slow DNS/TCP setup returns.
            connection.connect()
            with control.lock:
                control.transport_socket = connection.sock
            control.check()
            connection.request('POST' if payload is not None else 'GET', path, body=body,
                               headers={'Content-Type': 'application/json', 'Accept': 'application/json'})
            control.check()
            response = connection.getresponse()
            if response.status != 200:
                raw = response.read(4096)
                try:
                    detail = json.loads(raw).get('error', '')
                except (ValueError, AttributeError):
                    detail = ''
                if response.status == 404 and path == '/api/chat':
                    raise OllamaError("Model or chat endpoint not found. Refresh models and check the server URL.")
                raise OllamaError(f'Ollama returned HTTP {response.status}. {safe_detail(detail)}'.strip())
            yield response
        except (OSError, http.client.HTTPException) as exc:
            control.check()
            if isinstance(exc, (TimeoutError, socket.timeout)):
                raise OllamaError("Ollama did not respond in time. Please retry.") from None
            raise OllamaError("Could not connect to or read from the Ollama server. Check the URL and that the service is running.") from None
        finally:
            timer.cancel()
            if response is not None:
                response.close()
            connection.close()
            with control.lock:
                control.connection = None
                control.transport_socket = None

    def models(self, control):
        with self._request('/api/tags', control) as response:
            raw = response.read(1048577)
            control.check()
            if len(raw) > 1048576:
                raise OllamaError('The model list is too large.')
            try:
                data = json.loads(raw)
                models = data['models']
                if not isinstance(models, list):
                    raise ValueError
                names = set()
                for item in models:
                    if not isinstance(item, dict) or not isinstance(item.get('name'), str) or not 0 < len(item['name']) <= 200:
                        raise ValueError
                    item['name'].encode('utf-8')
                    names.add(item['name'])
            except (ValueError, KeyError, TypeError):
                raise OllamaError('The server returned an invalid Ollama model list.') from None
            return sorted(names)[:200]

    def chat(self, model, messages, control, on_text):
        if not isinstance(model, str) or not model.strip() or len(model) > 200:
            raise OllamaError('Choose an available model.')
        payload = {'model': model, 'messages': messages, 'stream': True}
        length = 0
        with self._request('/api/chat', control, payload) as response:
            while True:
                control.check()
                raw = response.readline(MAX_LINE + 1)
                control.check()
                if not raw:
                    raise OllamaError('The response ended before Ollama marked it complete. Partial text is kept.')
                if len(raw) > MAX_LINE:
                    raise OllamaError('An Ollama response chunk was too large. Partial text is kept.')
                if not raw.strip():
                    continue
                try:
                    data = json.loads(raw)
                    if not isinstance(data, dict):
                        raise ValueError
                    if data.get('error'):
                        raise OllamaError(f'Ollama: {safe_detail(data["error"])}')
                    message = data.get('message', {})
                    text = message.get('content', '')
                    if not isinstance(message, dict) or not isinstance(text, str) or type(data.get('done')) is not bool:
                        raise ValueError
                    text.encode('utf-8')
                except (ValueError, AttributeError) as exc:
                    if isinstance(exc, OllamaError):
                        raise
                    raise OllamaError('Ollama returned invalid streamed data. Partial text is kept.') from None
                if length + len(text) > MAX_REPLY:
                    raise OllamaError('Reply reached the 16,000-character limit. Partial text is kept; ask a shorter question.')
                if text:
                    length += len(text)
                    on_text(text)
                if data['done']:
                    if length == 0:
                        raise OllamaError('The model returned no answer text. Try another model or question.')
                    return
