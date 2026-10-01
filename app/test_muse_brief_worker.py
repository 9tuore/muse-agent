import json
import sqlite3
import tempfile
import threading
import unittest
from datetime import datetime, timezone
from pathlib import Path

from agent_app import LocalAgent
from desktop_worker import _LockedWriter, _watch_goals
from muse_goal_store import GoalStore


class _StopOnBrief:
    def __init__(self, stop):
        self.stop = stop
        self.lines = []

    def write(self, value):
        self.lines.append(value)
        if '"BRIEF_READY"' in value:
            self.stop.set()

    def flush(self):
        pass


class BriefWorkerTests(unittest.TestCase):
    def test_resident_worker_emits_verified_brief_and_ui_ack_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            GoalStore(workspace)
            agent = LocalAgent(workspace)
            saved = agent.handle({"type": "brief_settings_set", "settings": {
                "brief_mode": "custom", "brief_local_time": "00:00"}})
            self.assertTrue(saved["ok"])
            timestamp = datetime.now(timezone.utc).isoformat()
            result = {"status": "COMPLETED", "verification": "CHECKS_PASSED", "receipts": [{
                "capability": "workspace.write_artifact", "output": {"relative_path": "notes/result.md"}}]}
            with sqlite3.connect(str(workspace / "memory.sqlite3")) as db:
                db.execute("INSERT INTO muse_goal_runs(run_id,goal_id,revision,approval_id,trigger_kind,"
                           "event_id,status,started_at,finished_at,result_json) VALUES (?,?,?,?,?,?,?,?,?,?)",
                           ("run:brief-test", "goal:brief-test", 1, "approval:brief-test", "interval",
                            None, "completed", timestamp, timestamp, json.dumps(result)))
            stop = threading.Event()
            output = _StopOnBrief(stop)
            _watch_goals(agent, _LockedWriter(output), stop)
            frames = [json.loads(line) for line in output.lines]
            briefs = [frame for frame in frames if frame.get("status") == "BRIEF_READY"]
            self.assertEqual(len(briefs), 1)
            self.assertEqual(briefs[0]["brief"]["verified_updates"][0]["run_id"], "run:brief-test")
            self.assertTrue(agent.handle({"type": "brief_ack",
                                          "brief_id": briefs[0]["brief"]["brief_id"]})["ok"])
            self.assertEqual(LocalAgent(workspace).handle({"type": "brief_tick"})["status"], "NO_CHANGE")


if __name__ == "__main__":
    unittest.main()
