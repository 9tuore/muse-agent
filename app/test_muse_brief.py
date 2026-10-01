import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from muse_brief import BriefService
from muse_goals import GoalService
from test_muse_goals import _ResearchExecutor, _ResearchModel


class BriefTests(unittest.TestCase):
    def _goal(self, workspace, *, body="第一版"):
        model, executor = _ResearchModel(), _ResearchExecutor(workspace)
        executor.body = body
        goal = GoalService(workspace, model, executor)
        draft = goal.handle({"type": "goal_propose", "request_id": "brief-test-goal",
                             "text": "持续整理 https://example.test/brief"})
        goal.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                     "revision": 1, "decision": "approve",
                     "plan_digest": draft["plan_digest"]})
        return goal, executor, draft["goal_id"]

    def test_off_by_default_then_verified_run_prepared_replayed_and_acked(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            brief = BriefService(workspace)
            self.assertEqual(brief.tick()["reason"], "brief_off")
            brief.set_settings({"brief_mode": "custom", "brief_local_time": "00:00"},
                               now=datetime.now(timezone.utc) - timedelta(minutes=1))
            goal, _, goal_id = self._goal(workspace)
            self.assertEqual(goal.tick()[0]["status"], "COMPLETED")
            first = brief.tick()
            self.assertEqual(first["status"], "BRIEF_READY")
            self.assertFalse(first["replayed"])
            self.assertEqual(first["brief"]["verified_updates"][0]["goal_id"], goal_id)
            self.assertEqual(first["brief"]["verified_updates"][0]["source_urls"],
                             ["https://example.test/brief"])
            self.assertEqual(first["brief"]["needs_decision"], [])
            replay = BriefService(workspace).tick()
            self.assertEqual(replay["brief"]["brief_id"], first["brief"]["brief_id"])
            self.assertTrue(replay["replayed"])
            self.assertEqual(brief.acknowledge(first["brief"]["brief_id"])["status"], "ACKNOWLEDGED")
            self.assertEqual(BriefService(workspace).tick()["reason"], "already_delivered")

    def test_enabling_after_old_run_does_not_backfill_and_no_change_is_silent(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            goal, executor, _ = self._goal(workspace)
            self.assertEqual(goal.tick()[0]["status"], "COMPLETED")
            brief = BriefService(workspace)
            brief.set_settings({"brief_mode": "custom", "brief_local_time": "00:00"})
            self.assertEqual(brief.tick()["reason"], "no_verified_updates")
            self.assertEqual(goal.tick(datetime.now(timezone.utc) + timedelta(seconds=61))[0]["status"], "NO_CHANGE")
            self.assertEqual(brief.tick()["reason"], "no_verified_updates")
            executor.body = "第二版，有真实重要更新"
            self.assertEqual(goal.tick(datetime.now(timezone.utc) + timedelta(seconds=122))[0]["status"], "COMPLETED")
            self.assertEqual(brief.tick()["status"], "BRIEF_READY")

    def test_quiet_hours_and_invalid_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            brief = BriefService(workspace)
            with self.assertRaisesRegex(ValueError, "quiet_hours_pair_required"):
                brief.set_settings({"brief_mode": "custom", "quiet_start": "22:00"})
            with self.assertRaisesRegex(ValueError, "brief_time_invalid"):
                brief.set_settings({"brief_mode": "custom", "brief_local_time": "25:00"})
            brief.set_settings({"brief_mode": "custom", "brief_local_time": "00:00",
                                "quiet_start": "10:00", "quiet_end": "14:00"})
            midday = datetime.now().astimezone().replace(hour=12, minute=0, second=0, microsecond=0)
            self.assertEqual(brief.tick(midday)["status"], "QUIET_HOURS")

    def test_failed_goal_is_decision_not_verified_update(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            brief = BriefService(workspace)
            brief.set_settings({"brief_mode": "custom", "brief_local_time": "00:00"},
                               now=datetime.now(timezone.utc) - timedelta(minutes=1))
            goal = GoalService(workspace, _ResearchModel(fail_step=True), _ResearchExecutor(workspace))
            draft = goal.handle({"type": "goal_propose", "request_id": "brief-failed",
                                 "text": "持续整理 https://example.test/brief"})
            goal.handle({"type": "goal_decide", "goal_id": draft["goal_id"],
                         "revision": 1, "decision": "approve",
                         "plan_digest": draft["plan_digest"]})
            self.assertEqual(goal.tick()[0]["status"], "WAITING_USER")
            ready = brief.tick()
            self.assertEqual(ready["status"], "BRIEF_READY")
            self.assertEqual(ready["brief"]["verified_updates"], [])
            self.assertEqual(len(ready["brief"]["needs_decision"]), 1)
            self.assertIn("已验证更新 0 项", ready["brief"]["summary"])


if __name__ == "__main__":
    unittest.main()
