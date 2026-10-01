import json
import hashlib
import hmac
import os
import select
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import uuid
from pathlib import Path

from agent_app import LocalAgent
from desktop_worker import _LockedWriter, _NativeOfficialHost, _watch_local_inbox
from muse_goal_store import GoalStore
from muse_goals import validate_plan
from test_muse_goals import spec_for


class _Buffer:
    def __init__(self):
        self._parts = []
        self._lock = threading.Lock()

    def write(self, value):
        with self._lock:
            self._parts.append(value)

    def flush(self):
        return None

    def text(self):
        with self._lock:
            return "".join(self._parts)


def _wait_for_records(buffer, count, timeout=3.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        records = [json.loads(line) for line in buffer.text().splitlines() if line.strip()]
        if len(records) >= count:
            return records
        time.sleep(0.02)
    raise AssertionError(f"timed out waiting for {count} worker records: {buffer.text()!r}")


class DesktopWorkerTests(unittest.TestCase):
    def test_official_native_click_is_bound_to_pending_goal_and_one_use(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            spec = spec_for("官方确认写入")
            spec["goal_id"] = "goal:native-worker-boundary"
            spec["context_refs"] = []
            spec["triggers"] = [{"kind": "interval", "every_seconds": 60}]
            spec["steps"] = [{"id": "save", "capability": "workspace.write_artifact",
                              "args": {"relative_path": "notes/official.txt", "content": "已确认"},
                              "input_refs": []}]
            spec["permissions"]["capabilities"] = ["workspace.write_artifact"]
            spec["permissions"]["resource_refs"] = ["resource:workspace/notes/official.txt"]
            validate_plan(spec)
            store = GoalStore(workspace)
            store.save_draft(spec, "request:native-worker", {})
            goal = store.get(spec["goal_id"])
            agent = LocalAgent(workspace)
            secret = "native-test-secret-" + "a" * 64
            host = _NativeOfficialHost(agent, secret)
            prepared = host.bridge.prepare({"name": "muse_goal_step", "arguments": {
                "goal_id": goal["goal_id"], "revision": goal["revision"],
                "plan_digest": goal["digest"], "step_id": "save"}, "_meta": {
                "muse_host_session_id": "main:api:native-test",
                "muse_host_turn_id": str(uuid.uuid4()),
                "muse_host_tool_call_id": "call-native-test",
                "muse_host_call_nonce": str(uuid.uuid4())}})
            self.assertTrue(prepared["ok"], prepared)
            pending = host.handle({"type": "official_pending_list"})["pending"][0]
            self.assertEqual(pending["plan_digest"], goal["digest"])
            event = {"type": "official_native_decide", "pending_id": prepared["pending_id"],
                     "decision": "approve", "reviewed_digest": goal["digest"]}
            self.assertEqual(host.handle({**event, "native_witness": {}})["error"],
                             "native_click_not_verified")
            self.assertFalse((workspace / "notes/official.txt").exists())
            nonce = str(uuid.uuid4())
            mac = hmac.new(secret.encode(), host._signed_message(pending, "approve", nonce),
                           hashlib.sha256).hexdigest()
            witness = {"nonce": nonce, "decision": "approve", "mac": mac}
            result = host.handle({**event, "native_witness": witness})
            self.assertTrue(result["ok"], result)
            self.assertEqual((workspace / "notes/official.txt").read_text(), "已确认")
            self.assertEqual(result["receipt"]["sha256"], result["readback_sha256"])
            self.assertEqual(host.handle({**event, "native_witness": witness})["error"],
                             "pending_not_waiting")

    def test_only_one_resident_worker_owns_a_workspace(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            worker = Path(__file__).with_name("desktop_worker.py")
            command = [sys.executable, "-B", str(worker), str(workspace)]
            env = dict(os.environ, GOSIM_LOCAL_INBOX="0", PYTHONDONTWRITEBYTECODE="1",
                       LOCAL_MODEL_URL="http://127.0.0.1:9/v1/chat/completions")
            first = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, env=env)
            try:
                first.stdin.write('{"type":"health"}\n')
                first.stdin.flush()
                ready, _, _ = select.select([first.stdout], [], [], 5)
                self.assertTrue(ready, "first worker did not answer health")
                self.assertTrue(json.loads(first.stdout.readline())["ok"])

                second = subprocess.run(command, input='{"type":"health"}\n',
                                        capture_output=True, text=True, timeout=5, env=env)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(json.loads(second.stdout)["status"], "WORKSPACE_IN_USE")

                first.stdin.close()
                first.wait(timeout=5)
                restarted = subprocess.run(command, input='{"type":"health"}\n',
                                           capture_output=True, text=True, timeout=5, env=env)
                self.assertEqual(restarted.returncode, 0, restarted.stderr)
                self.assertTrue(json.loads(restarted.stdout)["ok"])
            finally:
                if first.poll() is None:
                    first.kill()
                    first.wait(timeout=5)
                first.stdout.close()
                first.stderr.close()
                if not first.stdin.closed:
                    first.stdin.close()

    def test_replayed_mail_still_reaches_goal_after_message_was_claimed(self):
        class InterruptedAgent:
            def __init__(self):
                self.goal_events = []

            def handle(self, event):
                if event["type"] == "message_event":
                    return {"ok": True, "status": "DUPLICATE_IGNORED"}
                if event["type"] == "goal_event":
                    self.goal_events.append(event["event"])
                    return {"ok": True, "status": "READY", "results": []}
                raise AssertionError(event)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "inbox" / "events.jsonl"
            agent = InterruptedAgent()
            stop = threading.Event()
            watcher = threading.Thread(target=_watch_local_inbox,
                                       args=(path, agent, _LockedWriter(_Buffer()), stop), daemon=True)
            watcher.start()
            try:
                deadline = time.monotonic() + 2.0
                while not path.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                with path.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps({"type": "message_event", "source": "qqmail",
                                             "message_id": "replay-1", "text": "合成邮件",
                                             "metadata": {"transport": "imap.qq.com:993/tls"}},
                                            ensure_ascii=False) + "\n")
                    stream.flush()
                deadline = time.monotonic() + 2.0
                while not agent.goal_events and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertEqual(len(agent.goal_events), 1)
                self.assertEqual(agent.goal_events[0]["topic"], "mail.received")
            finally:
                stop.set()
                watcher.join(timeout=2)

    def test_resident_inbox_processes_audits_and_dedupes_after_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            inbox = workspace / "inbox" / "events.jsonl"
            event = {
                "type": "message_event",
                "source": "synthetic",
                "message_id": "resident-worker-001",
                "conversation_id": "local-contract",
                "direction": "incoming",
                "text": "请把值班说明列入待办",
            }
            buffer = _Buffer()
            sink = _LockedWriter(buffer)
            stop = threading.Event()
            watcher = threading.Thread(
                target=_watch_local_inbox,
                args=(inbox, LocalAgent(workspace), sink, stop),
                daemon=True,
            )
            watcher.start()
            deadline = time.monotonic() + 2.0
            while not inbox.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            self.assertTrue(inbox.exists())

            with inbox.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, ensure_ascii=False) + "\n")
                stream.flush()
            first = _wait_for_records(buffer, 1)[0]
            self.assertEqual(first["status"], "PROCESSED")
            self.assertEqual(first["analysis"]["category"], "task")
            self.assertEqual(first["audit"]["source_scope"], "synthetic")
            self.assertFalse(first["privacy"]["stored_full_text"])

            with inbox.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(event, ensure_ascii=False) + "\n")
                stream.flush()
            second = _wait_for_records(buffer, 2)[1]
            self.assertEqual(second["status"], "DUPLICATE_IGNORED")

            stop.set()
            watcher.join(timeout=2)
            self.assertFalse(watcher.is_alive())

            restarted = LocalAgent(workspace)
            self.assertEqual(
                restarted.handle({"type": "message_status"})["message_queue"]["processed_count"],
                1,
            )
            self.assertEqual(restarted.handle(event)["status"], "DUPLICATE_IGNORED")

    def test_resident_inbox_rejects_unallowlisted_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            inbox = workspace / "inbox" / "events.jsonl"
            buffer = _Buffer()
            sink = _LockedWriter(buffer)
            stop = threading.Event()
            watcher = threading.Thread(
                target=_watch_local_inbox,
                args=(inbox, LocalAgent(workspace), sink, stop),
                daemon=True,
            )
            watcher.start()
            deadline = time.monotonic() + 2.0
            while not inbox.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            with inbox.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"type": "shell_exec", "argv": ["rm", "-rf", "/"]}) + "\n")
                stream.write(json.dumps({"type": "mail_reply_content", "card_id": "test", "body": "test", "confirmed": True}) + "\n")
                stream.write(json.dumps({"type": "chat_message", "text": "查询跨账户记忆",
                                         "memory_scopes": ["qqmail:account-7"]}) + "\n")
                stream.write(json.dumps({"type": "plugin_decide", "plugin_id": "builtin.text_stats",
                                         "decision": "enable", "approved": True}) + "\n")
                stream.flush()
            results = _wait_for_records(buffer, 4)
            stop.set()
            watcher.join(timeout=2)
            self.assertEqual(results, [{"ok": False, "error": "local_inbox_event_rejected"}] * 4)

    def test_resident_inbox_routes_verified_robrix2_envelope(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp) / "workspace"
            inbox = workspace / "inbox" / "events.jsonl"
            buffer = _Buffer()
            sink = _LockedWriter(buffer)
            stop = threading.Event()
            watcher = threading.Thread(
                target=_watch_local_inbox,
                args=(inbox, LocalAgent(workspace), sink, stop),
                daemon=True,
            )
            watcher.start()
            deadline = time.monotonic() + 2.0
            while not inbox.exists() and time.monotonic() < deadline:
                time.sleep(0.02)
            envelope = {
                "type": "robrix2_event",
                "adapter": "robrix2_matrix",
                "verified": True,
                "recipient_consent": True,
                "room_membership": "join",
                "transaction_id": "robrix2-tx-001",
                "room_id": "!room:example.org",
                "sender_id": "@sender:example.org",
                "event_type": "m.room.message",
                "content": {"msgtype": "m.text", "body": "请把宿主事件列入待办"},
            }
            with inbox.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(envelope, ensure_ascii=False) + "\n")
                envelope["verified"] = False
                envelope["transaction_id"] = "robrix2-tx-002"
                stream.write(json.dumps(envelope, ensure_ascii=False) + "\n")
                stream.flush()
            records = _wait_for_records(buffer, 2)
            stop.set()
            watcher.join(timeout=2)
            result = records[0]
            self.assertEqual(result["status"], "PROCESSED")
            self.assertEqual(result["source"], "robrix2")
            self.assertEqual(result["result_card"]["status"], "COMPLETED")
            blocked = records[1]
            self.assertEqual(blocked["status"], "BLOCKED_UNVERIFIED")
            self.assertEqual(blocked["result_card"]["status"], "BLOCKED_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
