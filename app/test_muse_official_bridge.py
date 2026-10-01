"""Security boundary for an official MCP call waiting on a native Goal decision."""

import json
import sqlite3
import tempfile
import threading
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from muse_action_bus import ApprovedActionBus
from muse_capabilities import CapabilityExecutor
from muse_goal_store import GoalStore
from muse_goals import validate_plan
from muse_official_bridge import OfficialGoalBridge, TOOL_NAME
from test_muse_goals import spec_for


class OfficialGoalBridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.store = GoalStore(self.workspace)
        self.spec = spec_for("官方同轮静态写入")
        self.spec["goal_id"] = "goal:official-bridge"
        self.spec["context_refs"] = []
        self.spec["triggers"] = [{"kind": "interval", "every_seconds": 60}]
        self.spec["steps"] = [{"id": "save", "capability": "workspace.write_artifact",
                               "args": {"relative_path": "notes/official.txt",
                                        "content": "提纲\n来自隔离测试的精确内容"},
                               "input_refs": []}]
        self.spec["permissions"]["capabilities"] = ["workspace.write_artifact"]
        self.spec["permissions"]["resource_refs"] = ["resource:workspace/notes/official.txt"]
        validate_plan(self.spec)
        self.store.save_draft(self.spec, "request:official-bridge", {})
        self.goal = self.store.get(self.spec["goal_id"])
        self.witness = object()
        self.bridge = OfficialGoalBridge(
            self.workspace,
            ApprovedActionBus(self.workspace, CapabilityExecutor(self.workspace)),
            native_click_guard=lambda witness, _pending: witness is self.witness)
        self.args = {"goal_id": self.goal["goal_id"], "revision": 1,
                     "plan_digest": self.goal["digest"], "step_id": "save"}
        self.params = {"name": TOOL_NAME, "arguments": dict(self.args), "_meta": {
            "muse_host_session_id": "main:api:official-a", "muse_host_turn_id": str(uuid.uuid4()),
            "muse_host_tool_call_id": "call-official-a",
            "muse_host_call_nonce": str(uuid.uuid4())}}
        self.target = self.workspace / "notes/official.txt"

    def test_exact_native_decision_uses_bus_readback_and_returns_to_same_call(self):
        prepared = self.bridge.prepare(self.params)
        self.assertTrue(prepared["ok"], prepared)
        self.assertFalse(self.target.exists())
        self.assertEqual(len(self.bridge.list_pending_for_ui()), 1)
        self.assertEqual(self.bridge.pending_for_ui(prepared["pending_id"])["plan"], self.spec)
        self.assertEqual(self.bridge.decide_from_native(
            prepared["pending_id"], "approve", self.goal["digest"], object())["error"],
            "native_click_not_verified")
        self.assertFalse(self.target.exists())
        result = []
        waiter = threading.Thread(target=lambda: result.append(
            self.bridge.wait_for_result(prepared["pending_id"])))
        waiter.start()
        decided = self.bridge.decide_from_native(
            prepared["pending_id"], "approve", self.goal["digest"], self.witness)
        waiter.join(timeout=5)
        self.assertFalse(waiter.is_alive())
        self.assertTrue(decided["ok"], decided)
        self.assertEqual(self.target.read_text(), self.spec["steps"][0]["args"]["content"])
        self.assertEqual(decided["receipt"]["sha256"], decided["readback_sha256"])
        self.assertTrue(decided["receipt"]["readback_matches"])
        self.assertEqual(self.store.get(self.goal["goal_id"])["status"], "completed")
        self.assertFalse(result[0]["isError"])
        official_result = json.loads(result[0]["content"][0]["text"])
        self.assertEqual(official_result["official_session_id"],
                         self.params["_meta"]["muse_host_session_id"])
        self.assertEqual(official_result["official_turn_id"],
                         self.params["_meta"]["muse_host_turn_id"])
        self.assertEqual(official_result["receipt"], decided["receipt"])
        self.assertEqual(self.bridge.decide_from_native(
            prepared["pending_id"], "approve", self.goal["digest"], self.witness)["error"],
            "pending_not_waiting")
        self.assertFalse(self.bridge.prepare(self.params)["ok"])

    def test_model_spoof_and_wrong_digest_never_approve(self):
        self.assertEqual(self.bridge.prepare({"name": TOOL_NAME, "arguments": self.args})["error"],
                         "host_context_required")
        forged = dict(self.params, arguments=dict(self.args, _meta=dict(self.params["_meta"])))
        self.assertEqual(self.bridge.prepare(forged)["error"], "model_arguments_invalid")
        prepared = self.bridge.prepare(self.params)
        self.assertEqual(self.bridge.decide_from_native(
            prepared["pending_id"], "approve", "0" * 64, self.witness)["error"],
            "pending_expired_or_digest_changed")
        self.assertEqual(self.store.get(self.goal["goal_id"])["status"], "draft")
        self.assertFalse(self.target.exists())

    def test_second_session_and_replayed_nonce_cannot_take_pending_goal(self):
        first = self.bridge.prepare(self.params)
        self.assertTrue(first["ok"])
        other = {"name": TOOL_NAME, "arguments": dict(self.args), "_meta": {
            **self.params["_meta"], "muse_host_session_id": "main:api:official-b",
            "muse_host_turn_id": str(uuid.uuid4()),
            "muse_host_call_nonce": str(uuid.uuid4())}}
        self.assertEqual(self.bridge.prepare(other)["error"],
                         "official_call_replayed_or_goal_pending")
        self.assertEqual(self.bridge.prepare(self.params)["error"],
                         "official_call_replayed_or_goal_pending")
        self.assertFalse(self.target.exists())

    def test_deny_and_expiry_leave_goal_draft(self):
        prepared = self.bridge.prepare(self.params)
        denied = self.bridge.decide_from_native(prepared["pending_id"], "deny",
                                                self.goal["digest"], self.witness)
        self.assertEqual(denied["status"], "DENIED")
        self.assertTrue(self.bridge.wait_for_result(prepared["pending_id"])["isError"])
        self.assertFalse(self.target.exists())
        self.assertEqual(self.store.get(self.goal["goal_id"])["status"], "draft")
        other = dict(self.params, _meta={**self.params["_meta"],
                                        "muse_host_call_nonce": str(uuid.uuid4()),
                                        "muse_host_tool_call_id": "call-official-b"})
        pending = self.bridge.prepare(other)
        self.assertTrue(pending["ok"])
        with sqlite3.connect(self.store.path) as db:
            db.execute("UPDATE muse_official_pending SET expires_at=? WHERE pending_id=?",
                       ("2000-01-01T00:00:00+00:00", pending["pending_id"]))
        self.assertEqual(self.bridge.decide_from_native(
            pending["pending_id"], "approve", self.goal["digest"], self.witness)["error"],
            "pending_expired_or_digest_changed")
        self.assertTrue(self.bridge.wait_for_result(pending["pending_id"])["isError"])
        self.assertFalse(self.target.exists())

    def test_plan_revision_change_invalidates_pending(self):
        prepared = self.bridge.prepare(self.params)
        changed = dict(self.spec, revision=2,
                       steps=[dict(self.spec["steps"][0], args={
                           "relative_path": "notes/official.txt", "content": "提纲\n另一版内容"})])
        self.store.save_revision(changed, {})
        self.assertEqual(self.bridge.pending_for_ui(prepared["pending_id"])["error"],
                         "goal_revision_or_digest_changed")
        self.assertFalse(self.bridge.decide_from_native(
            prepared["pending_id"], "approve", self.goal["digest"], self.witness)["ok"])
        self.assertFalse(self.target.exists())

    def test_timeout_during_action_reports_in_progress(self):
        prepared = self.bridge.prepare(self.params)
        with sqlite3.connect(self.store.path) as db:
            db.execute("UPDATE muse_official_pending SET status='EXECUTING' WHERE pending_id=?",
                       (prepared["pending_id"],))
        with patch("muse_official_bridge.WAIT_SECONDS", -2):
            result = self.bridge.wait_for_result(prepared["pending_id"])
        self.assertEqual(json.loads(result["content"][0]["text"])["status"], "IN_PROGRESS")
        self.assertTrue(result["isError"])
        self.assertFalse(self.target.exists())


if __name__ == "__main__":
    unittest.main()
