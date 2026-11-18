"""Ollama HTTP/stream/cancellation and bounded session conversation regression tests."""
import queue
import socket
import sys
import threading
import time
import unittest
from unittest.mock import Mock, patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'soskuska'))
from ollama_client import ControlledHTTPSConnection, Cancelled, OllamaClient, OllamaError, RequestControl, endpoint_url
from tutor import TutorTask, chat_messages
from ollama_fixture import FakeOllama


class TutorRulesTests(unittest.TestCase):
    def test_endpoint_validation_and_normalization(self):
        self.assertEqual(endpoint_url(' http://LOCALHOST:11434/ '), 'http://localhost:11434')
        self.assertEqual(endpoint_url('http://[::1]:11434'), 'http://[::1]:11434')
        for value in ['file:///tmp/a', 'ftp://host', 'http://user:secret@host', 'http://host/path',
                      'http://host?q=1', 'http://host#x', 'http://host:wrong', 'http://my host', 'http://', 'http://host:0', 'https://host:0']:
            with self.subTest(value=value), self.assertRaises(OllamaError):
                endpoint_url(value)

    def test_prompt_and_language_validation(self):
        for prompt in ['', ' ', 'x'*4001]:
            with self.assertRaises(OllamaError):
                chat_messages([], prompt)
        with self.assertRaises(OllamaError):
            chat_messages([], 'Hello', 'Unsupported')
        self.assertIn('Reply in Russian', chat_messages([], ' Что такое предел? ', 'Russian')[0]['content'])
        self.assertEqual(chat_messages([], ' вопрос ')[-1]['content'], 'вопрос')

    def test_context_uses_only_recent_completed_turns_and_no_private_store(self):
        turns = [{'prompt': str(i), 'answer': 'answer', 'status': 'completed'} for i in range(10)]
        turns.append({'prompt': 'failed secret', 'answer': 'partial', 'status': 'failed'})
        messages = chat_messages(turns, 'next')
        self.assertEqual(len(messages), 14)
        self.assertEqual(messages[1]['content'], '4')
        self.assertNotIn('failed secret', str(messages))
        self.assertEqual(messages[-1], {'role': 'user', 'content': 'next'})

    def test_context_character_budget(self):
        turns = [{'prompt': 'q'*4000, 'answer': 'a'*16000, 'status': 'completed'} for _ in range(6)]
        messages = chat_messages(turns, 'next')
        self.assertEqual(len(messages), 4)
        self.assertLess(sum(len(m['content']) for m in messages), 25000)


class OllamaClientTests(unittest.TestCase):
    def setUp(self):
        self.fixture = FakeOllama()
        self.addCleanup(self.fixture.close)
        self.client = OllamaClient(self.fixture.url, timeout=1, total_timeout=2)

    def test_models_use_tags_and_names_from_server(self):
        self.fixture.model_names = ['z-model', 'a-model']
        self.assertEqual(self.client.models(RequestControl()), ['a-model', 'z-model'])
        self.assertEqual(self.fixture.requests[0][:2], ('GET', '/api/tags'))
        self.fixture.model_names = []
        self.assertEqual(self.client.models(RequestControl()), [])

    def test_invalid_model_response(self):
        self.fixture.models_payload = {'wrong': []}
        with self.assertRaisesRegex(OllamaError, 'invalid'):
            self.client.models(RequestControl())

    def test_stream_utf8_chunks_and_request_context(self):
        output = []
        self.client.chat('study-model:latest', chat_messages([], 'Vysvětli / объясни'), RequestControl(), output.append)
        self.assertEqual(''.join(output), 'Hello svět / мир')
        method, path, payload = self.fixture.requests[0]
        self.assertEqual((method, path), ('POST', '/api/chat'))
        self.assertTrue(payload['stream'])
        self.assertEqual(payload['model'], 'study-model:latest')
        self.assertEqual(payload['messages'][-1]['content'], 'Vysvětli / объясни')

    def test_thinking_is_not_displayed(self):
        self.fixture.mode = 'thinking'
        output = []
        self.client.chat('m', [], RequestControl(), output.append)
        self.assertNotIn('internal', ''.join(output))

    def test_errors_empty_reply_and_truncated_stream_are_not_complete(self):
        for mode, match in [('error', 'out of memory'), ('malformed', 'invalid'), ('empty', 'no answer'),
                            ('eof', 'ended before'), ('oversized', 'limit'), ('huge_line', 'too large')]:
            self.fixture.mode = mode
            with self.subTest(mode=mode), self.assertRaisesRegex(OllamaError, match):
                self.client.chat('m', [], RequestControl(), lambda _: None)

    def test_http_errors_and_no_redirect_follow(self):
        for status in [302, 404, 500]:
            self.fixture.status = status
            with self.subTest(status=status), self.assertRaises(OllamaError):
                self.client.chat('m', [], RequestControl(), lambda _: None)
        self.assertEqual(len(self.fixture.requests), 3)

    def test_cancel_before_request_sends_nothing(self):
        control = RequestControl()
        control.cancel()
        with self.assertRaises(Cancelled):
            self.client.models(control)
        self.assertEqual(self.fixture.requests, [])

    def test_stop_interrupts_read_even_when_server_closes_connection(self):
        self.fixture.mode = 'slow'
        task = TutorTask('chat', self.fixture.url, model='m', messages=[])
        task.start()
        event = task.events.get(timeout=2)
        self.assertEqual(event, ('text', 'Hello '))
        started = time.monotonic()
        task.cancel()
        task.thread.join(2)
        self.assertFalse(task.thread.is_alive())
        self.assertLess(time.monotonic()-started, 2)
        self.assertEqual(task.events.get(timeout=1)[0], 'stopped')

    def test_wall_timeout_interrupts_an_unterminated_chunk(self):
        self.fixture.mode = 'stall'
        client = OllamaClient(self.fixture.url, timeout=2, total_timeout=0.15)
        start = time.monotonic()
        with self.assertRaisesRegex(OllamaError, 'timed out'):
            client.chat('m', [], RequestControl(), lambda _: None)
        self.assertLess(time.monotonic()-start, 1.5)

    def test_worker_reports_done_and_error_on_background_thread(self):
        task = TutorTask('models', self.fixture.url)
        task.start()
        task.thread.join(2)
        self.assertFalse(task.thread.is_alive())
        self.assertEqual(task.events.get(timeout=1), ('done', ['study-model:latest']))
        self.fixture.models_payload = []
        task = TutorTask('models', self.fixture.url)
        task.start()
        task.thread.join(2)
        self.assertEqual(task.events.get(timeout=1)[0], 'error')

    def test_stop_interrupts_stalled_tls_handshake(self):
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        self.addCleanup(listener.close)
        accepted = threading.Event()
        release = threading.Event()
        def stall():
            connection, _ = listener.accept()
            accepted.set()
            release.wait(3)
            connection.close()
        server = threading.Thread(target=stall, daemon=True)
        server.start()
        task = TutorTask('models', f'https://127.0.0.1:{listener.getsockname()[1]}')
        task.start()
        try:
            self.assertTrue(accepted.wait(2))
            # Wait for the client to publish the wrapped socket before cancelling.
            deadline = time.monotonic()+2
            while task.control.transport_socket is None and time.monotonic()<deadline:
                time.sleep(0.01)
            self.assertIsNotNone(task.control.transport_socket)
            task.cancel()
            task.thread.join(1)
            self.assertFalse(task.thread.is_alive())
            self.assertEqual(task.events.get(timeout=1)[0], 'stopped')
        finally:
            release.set()
            server.join(2)

    def test_wall_timeout_interrupts_stalled_tls_handshake(self):
        listener = socket.socket()
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        self.addCleanup(listener.close)
        release = threading.Event()
        def stall():
            connection, _ = listener.accept()
            release.wait(3)
            connection.close()
        server = threading.Thread(target=stall, daemon=True)
        server.start()
        client = OllamaClient(f'https://127.0.0.1:{listener.getsockname()[1]}', timeout=2, total_timeout=0.2)
        try:
            started = time.monotonic()
            with self.assertRaisesRegex(OllamaError, 'timed out'):
                client.models(RequestControl())
            self.assertLess(time.monotonic()-started, 1.5)
        finally:
            release.set()
            server.join(2)

    def test_cancel_during_connect_never_sends_prompt(self):
        control = RequestControl()
        sock = Mock()
        def connected_after_stop(*_args, **_kwargs):
            control.cancel()
            return sock
        with patch('socket.create_connection', side_effect=connected_after_stop):
            with self.assertRaises(Cancelled):
                self.client.chat('m', chat_messages([], 'Do not send this question'), control, lambda _: None)
        sock.sendall.assert_not_called()

    def test_invalid_unicode_model_names_are_rejected_before_display(self):
        self.fixture.model_names = [chr(0xd800)]
        with self.assertRaisesRegex(OllamaError, 'invalid') as error:
            self.client.models(RequestControl())
        str(error.exception).encode('utf-8')

    def test_invalid_unicode_answer_never_reaches_callback(self):
        self.fixture.mode = 'surrogate'
        output = []
        with self.assertRaisesRegex(OllamaError, 'invalid'):
            self.client.chat('m', [], RequestControl(), output.append)
        self.assertEqual(output, [])

    def test_remote_diagnostics_are_safe_unicode(self):
        for mode in ['http', 'error_surrogate']:
            self.fixture.mode = mode
            self.fixture.error_detail = chr(0xd800)
            self.fixture.status = 500 if mode == 'http' else 200
            with self.subTest(mode=mode), self.assertRaises(OllamaError) as error:
                self.client.chat('m', [], RequestControl(), lambda _: None)
            str(error.exception).encode('utf-8')

    def test_https_host_header_preserves_explicit_port(self):
        for port, expected in [(None, b'Host: example.test'), (80, b'Host: example.test:80'), (443, b'Host: example.test')]:
            connection = ControlledHTTPSConnection('example.test', port, RequestControl())
            sock = Mock()
            connection.sock = sock
            connection.request('GET', '/api/tags')
            sent = b''.join(call.args[0] for call in sock.sendall.call_args_list)
            self.assertIn(expected+b'\r\n', sent)
            self.assertEqual(connection.port, 443 if port is None else port)
            connection.close()

    def test_connection_failure_is_actionable_and_does_not_claim_not_installed(self):
        self.fixture.close()
        self.fixture.close = lambda: None
        with self.assertRaisesRegex(OllamaError, 'Check the URL'):
            self.client.models(RequestControl())


if __name__ == '__main__':
    unittest.main()
