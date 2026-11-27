"""Read-only MCP server; skipped unless the optional `mcp` package is installed."""
import asyncio
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SERVER = ROOT / "soskuska" / "mcp_server.py"
sys.path.insert(0, str(ROOT / "soskuska"))
from database_lock import DatabaseLease
from storage import Store

try:
    from mcp import Client
except ImportError:
    Client = None
else:
    import mcp_server

TOOLS = {"list_subjects", "get_subject", "search_questions", "list_decks", "due_flashcards",
         "study_statistics", "practice_history", "upcoming_exams"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns


@unittest.skipIf(Client is None, "optional 'mcp' package not installed (pip install -r soskuska/requirements-mcp.txt)")
class McpServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "study.sqlite3"
        store = Store(self.path)
        try:
            exam = (date.today() + timedelta(days=3)).isoformat()
            self.sid = store.create_subject("Biology", exam_date=exam)
            topic = store.create_topic(self.sid, "Cells")
            self.qid = store.create_question(self.sid, "What powers the cell?", ["Mitochondria", "Ribosome", "Wall", "Golgi"],
                                             0, "Easy", topic, "Mitochondria make ATP.")
            self.deck = store.create_deck(self.sid, "Bio cards")
            store.create_flashcard(self.deck, "ATP?", "Energy currency")
            store.add_session(300, self.sid)
            attempt = store.start_practice(self.sid, 1)
            store.save_practice_answer(attempt, 0, 0)
            store.complete_practice(attempt)
        finally:
            store.close()

    def run_client(self, body, *, allow_answers=True, mode="auto"):
        async def go():
            async with Client(mcp_server.build_server(self.path, allow_answers=allow_answers), mode=mode) as client:
                return await body(client)
        return asyncio.run(go())

    def call(self, name, arguments=None, **options):
        return self.run_client(lambda client: client.call_tool(name, arguments or {}), **options)

    @staticmethod
    def error_text(result):
        assert result.is_error, result
        return " ".join(block.text for block in result.content)

    def test_tools_are_listed_read_only_in_both_protocol_modes(self):
        for mode in ("auto", "legacy"):
            with self.subTest(mode=mode):
                tools = self.run_client(lambda client: client.list_tools(), mode=mode).tools
                self.assertEqual({tool.name for tool in tools}, TOOLS)
                for tool in tools:
                    hints = tool.annotations
                    self.assertEqual((hints.read_only_hint, hints.destructive_hint, hints.idempotent_hint,
                                      hints.open_world_hint), (True, False, True, False), tool.name)

    def test_every_tool_answers_from_the_database(self):
        calls = {
            "list_subjects": {}, "get_subject": {"subject_id": self.sid},
            "search_questions": {"subject_id": self.sid}, "list_decks": {},
            "due_flashcards": {"deck_id": self.deck}, "study_statistics": {"period": "All time"},
            "practice_history": {}, "upcoming_exams": {},
        }
        before = digest(self.path)

        async def sweep(client):
            results = {name: await client.call_tool(name, args) for name, args in calls.items()}
            resource = await client.read_resource("soskuska://subjects")
            return results, resource
        results, resource = self.run_client(sweep)
        for name, result in results.items():
            self.assertFalse(result.is_error, (name, result.content))
            self.assertIsInstance(result.structured_content, dict, name)
        self.assertEqual(results["list_subjects"].structured_content["items"][0]["name"], "Biology")
        self.assertEqual(results["practice_history"].structured_content["items"][0]["score_percent"], 100.0)
        self.assertEqual(results["upcoming_exams"].structured_content["items"][0]["days_until_exam"], 3)
        self.assertIn("**Biology**", resource.contents[0].text)
        self.assertEqual(digest(self.path), before)
        self.assertFalse(Path(str(self.path) + "-journal").exists())

    def test_answer_keys_and_backs_are_hidden_by_default_and_can_be_forbidden(self):
        hidden = self.call("search_questions", {"subject_id": self.sid})
        text = json.dumps(hidden.structured_content) + " ".join(block.text for block in hidden.content)
        self.assertNotIn("correct_option", text)
        self.assertNotIn("make ATP", text)
        shown = self.call("search_questions", {"subject_id": self.sid, "include_answers": True})
        self.assertEqual(shown.structured_content["items"][0]["correct_option"], "A")
        self.assertNotIn("Energy currency", json.dumps(self.call("due_flashcards", {"deck_id": self.deck}).structured_content))
        for name, args in (("search_questions", {"subject_id": self.sid, "include_answers": True}),
                           ("due_flashcards", {"deck_id": self.deck, "include_backs": True})):
            with self.subTest(name=name):
                self.assertIn("--no-answers", self.error_text(self.call(name, args, allow_answers=False)))
        self.assertFalse(self.call("search_questions", {"subject_id": self.sid}, allow_answers=False).is_error)

    def test_invalid_arguments_become_tool_errors(self):
        cases = [
            ("get_subject", {"subject_id": 999}, "does not exist"),
            ("get_subject", {"subject_id": True}, "valid integer"),
            ("search_questions", {"subject_id": self.sid, "include_answers": "yes"}, "valid boolean"),
            ("search_questions", {"subject_id": self.sid, "topic_id": 1, "without_topic": True}, "either"),
            ("search_questions", {"subject_id": self.sid, "difficulty": "Impossible"}, "Easy"),
            ("study_statistics", {"period": "Forever"}, "Last 7 days"),
            ("due_flashcards", {"deck_id": self.deck, "limit": 0}, "limit"),
        ]
        for name, args, expected in cases:
            with self.subTest(name=name, args=args):
                self.assertIn(expected, self.error_text(self.call(name, args)))

    def test_exact_question_lookup_checks_one_answer(self):
        result = self.call("search_questions", {"subject_id": self.sid, "question_id": self.qid, "include_answers": True})
        self.assertEqual([(i["id"], i["correct_option"]) for i in result.structured_content["items"]], [(self.qid, "A")])
        self.assertIn("valid integer", self.error_text(self.call("search_questions", {"subject_id": self.sid, "question_id": "1"})))

    def test_limits_are_clamped(self):
        store = Store(self.path)
        try:
            for n in range(60):
                store.create_question(self.sid, f"Question {n}?", [f"a{n}", f"b{n}", f"c{n}", f"d{n}"], 1)
        finally:
            store.close()
        result = self.call("search_questions", {"subject_id": self.sid, "limit": 500}).structured_content
        self.assertEqual((result["returned"], result["total"]), (50, 61))

    def test_busy_schema_and_missing_database_errors(self):
        opened = []
        original = mcp_server.Store.open_existing

        def tracking(*args, **kwargs):
            opened.append(original(*args, **kwargs))
            return opened[-1]
        with patch.object(mcp_server.Store, "open_existing", side_effect=tracking):
            self.call("list_subjects")
            self.assertIn("does not exist", self.error_text(self.call("get_subject", {"subject_id": 999})))
        self.assertEqual(len(opened), 2)
        self.assertTrue(all(store.lease.file is None for store in opened), "every call must release its lease")
        with DatabaseLease(self.path, exclusive=True):  # As held by a restore.
            self.assertIn("busy", self.error_text(self.call("list_subjects")))
        self.assertFalse(self.call("list_subjects").is_error, "no lease may outlive a call")
        db = sqlite3.connect(self.path)
        db.execute("PRAGMA user_version=9"); db.commit(); db.close()
        self.assertIn("Open SOSkúška once", self.error_text(self.call("list_subjects")))
        self.path.unlink()
        self.assertIn("no longer exists", self.error_text(self.call("list_subjects")))
        self.assertFalse(self.path.exists(), "the server must never create a database")

    def test_unexpected_errors_hide_their_message(self):
        secret = "Mitochondria make ATP."
        with patch.object(mcp_server.queries, "subjects_overview", side_effect=KeyError(secret)), \
             self.assertLogs("soskuska.mcp", "ERROR") as logs:
            text = self.error_text(self.call("list_subjects"))
        self.assertIn("internal error", text)
        self.assertNotIn(secret, text + " ".join(logs.output))

    def test_prompts_guide_without_revealing_answers(self):
        async def prompts(client):
            names = {prompt.name for prompt in (await client.list_prompts()).prompts}
            quiz = await client.get_prompt("quiz_me", {"subject_id": str(self.sid), "count": "3"})
            return names, quiz.messages[0].content.text
        names, quiz = self.run_client(prompts)
        self.assertEqual(names, {"quiz_me", "weak_topics"})
        self.assertIn("include_answers=false", quiz)
        self.assertIn("one question at a time", quiz)

    def test_server_imports_no_gui_modules(self):
        code = ("import sys; sys.path.insert(0, sys.argv[1]); import mcp_server; "
                "sys.exit(1 if {'tkinter', 'customtkinter', 'app'} & set(sys.modules) else 0)")
        result = subprocess.run([sys.executable, "-c", code, str(SERVER.parent)], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_database_at_start_is_an_error_and_is_not_created(self):
        missing = Path(self.temp.name) / "nothing" / "dashboard.sqlite3"
        result = subprocess.run([sys.executable, str(SERVER), "--data", str(missing)], capture_output=True,
                                text=True, timeout=60, stdin=subprocess.DEVNULL)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.assertIn("no SOSkúška database", result.stderr)
        self.assertFalse(missing.parent.exists())

    def test_stdio_session_writes_only_protocol_messages(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "list_subjects", "arguments": {}}},
        ]
        before = digest(self.path)
        log = open(Path(self.temp.name) / "stderr.txt", "w+", encoding="utf-8")  # File-backed: never an undrained pipe.
        self.addCleanup(log.close)
        process = subprocess.Popen([sys.executable, str(SERVER), "--data", str(self.path), "--no-answers"],
                                   stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log,
                                   text=True, encoding="utf-8")
        watchdog = threading.Timer(60, process.kill)
        watchdog.start()
        try:
            # Keep stdin open until the last reply, as a real host does: on EOF the
            # SDK stops without finishing requests still in flight.
            replies = []
            for message in messages:
                process.stdin.write(json.dumps(message) + "\n")
                process.stdin.flush()
                if "id" in message:
                    line = process.stdout.readline()
                    self.assertTrue(line, "server closed stdout early")
                    replies.append(json.loads(line))  # Any non-protocol stdout line fails here.
            process.stdin.close()
            rest = process.stdout.read()
            self.assertEqual(process.wait(), 0)
        finally:
            watchdog.cancel()
            if process.poll() is None:
                process.kill()
            for stream in (process.stdin, process.stdout):
                if not stream.closed:
                    stream.close()
        self.assertEqual(rest.strip(), "", "unexpected output after the last reply")
        self.assertTrue(all(reply.get("jsonrpc") == "2.0" for reply in replies), replies)
        by_id = {reply.get("id"): reply for reply in replies}
        self.assertEqual(by_id[1]["result"]["serverInfo"]["name"], "SOSkúška")
        self.assertEqual({tool["name"] for tool in by_id[2]["result"]["tools"]}, TOOLS)
        self.assertEqual(by_id[3]["result"]["structuredContent"]["items"][0]["name"], "Biology")
        log.seek(0)
        self.assertNotIn("Biology", log.read())
        self.assertEqual(digest(self.path), before)


if __name__ == "__main__":
    unittest.main()
