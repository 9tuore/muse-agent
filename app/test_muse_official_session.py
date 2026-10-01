import unittest

from muse_official_session import OfficialGoalSession, OfficialSessionError


SESSION = "main:api:g01-test"
TURN = "3d956fe2-51b5-4370-8a15-fef8868364be"
APPROVAL = "d8f00957-69cc-467d-bc79-0503f11773da"


def frame(method, **params):
    return {"jsonrpc": "2.0", "method": method,
            "params": {"session_id": SESSION, "turn_id": TURN, **params}}


class OfficialGoalSessionTests(unittest.TestCase):
    def setUp(self):
        self.link = OfficialGoalSession(goal_id="goal-a", revision=2,
                                        plan_digest="sha256:example", session_id=SESSION)
        self.link.accept_session_open({"result": {"opened": {
            "session_id": SESSION, "active_profile_id": "main"}}})
        self.link.accept_turn_start(TURN, {"result": {"accepted": True}})
        self.assertEqual(self.link.observe(frame("turn/started")), "TURN_STARTED")

    def test_approved_and_completed_stays_evidence_only(self):
        self.assertEqual(self.link.observe(frame("approval/requested", approval_id=APPROVAL,
                                                tool_name="shell")), "APPROVAL_REQUESTED")
        self.assertEqual(self.link.observe(frame("approval/decided", approval_id=APPROVAL,
                                                decision="approve", auto_resolved=False,
                                                decided_by="user")), "APPROVAL_DECIDED")
        self.assertEqual(self.link.observe(frame("turn/completed", session_result={
            "message_id": "final-5", "committed_seq": 5})), "TURN_COMPLETED")
        evidence = self.link.evidence()
        self.assertEqual(evidence["official_session_id"], SESSION)
        self.assertEqual(evidence["official_turn_id"], TURN)
        self.assertEqual(evidence["official_session_result"],
                         {"message_id": "final-5", "committed_seq": 5})
        self.assertTrue(evidence["client_approval_observed"])
        self.assertFalse(evidence["manual_approval_observed"])
        self.assertEqual(evidence["authority"], "NONE")
        self.assertEqual(self.link.observe(frame("approval/requested", approval_id=APPROVAL,
                                                tool_name="shell")), "APPROVAL_REQUESTED")
        self.assertEqual(self.link.observe(frame("approval/decided", approval_id=APPROVAL,
                                                decision="approve", auto_resolved=False,
                                                decided_by="user")), "APPROVAL_DECIDED")
        self.assertEqual(self.link.observe(frame("turn/completed", session_result={
            "message_id": "final-5", "committed_seq": 5})), "TURN_COMPLETED")

    def test_wrong_session_or_turn_cannot_supply_evidence(self):
        other = frame("approval/requested", approval_id=APPROVAL, tool_name="shell")
        other["params"]["session_id"] = "main:api:other"
        self.assertEqual(self.link.observe(other), "OTHER_SESSION")
        other["params"]["session_id"] = SESSION
        other["params"]["turn_id"] = "0f3df39d-87c6-4ca7-a190-564725865204"
        with self.assertRaisesRegex(OfficialSessionError, "turn_mismatch"):
            self.link.observe(other)
        self.assertEqual(self.link.evidence()["official_approvals"], {})

    def test_auto_approval_and_replay_loss_are_not_manual_confirmation(self):
        self.link.observe(frame("approval/requested", approval_id=APPROVAL, tool_name="shell"))
        self.link.observe(frame("approval/decided", approval_id=APPROVAL,
                                decision="approve", auto_resolved=True, decided_by="policy"))
        self.link.observe(frame("protocol/replay_lossy", dropped_count=1))
        self.assertFalse(self.link.evidence()["manual_approval_observed"])
        self.assertFalse(self.link.evidence()["client_approval_observed"])
        self.assertTrue(self.link.evidence()["replay_lossy"])

    def test_replay_loss_invalidates_observed_manual_confirmation(self):
        self.link.observe(frame("approval/requested", approval_id=APPROVAL, tool_name="shell"))
        self.link.observe(frame("approval/decided", approval_id=APPROVAL,
                                decision="approve", auto_resolved=False, decided_by="user"))
        self.assertTrue(self.link.evidence()["client_approval_observed"])
        self.assertFalse(self.link.evidence()["manual_approval_observed"])
        self.link.observe(frame("protocol/replay_lossy", dropped_count=1))
        self.assertFalse(self.link.evidence()["manual_approval_observed"])
        self.assertFalse(self.link.evidence()["client_approval_observed"])

    def test_rpc_decided_by_is_not_proof_of_user_gesture(self):
        self.link.observe(frame("approval/requested", approval_id=APPROVAL, tool_name="shell"))
        self.link.observe(frame("approval/decided", approval_id=APPROVAL,
                                decision="approve", auto_resolved=False, decided_by="main"))
        evidence = self.link.evidence()
        self.assertTrue(evidence["client_approval_observed"])
        self.assertFalse(evidence["manual_approval_observed"])
        self.assertEqual(evidence["authority"], "NONE")

    def test_conflicting_terminal_and_approval_replay_rejected(self):
        self.link.observe(frame("approval/requested", approval_id=APPROVAL, tool_name="shell"))
        decided = frame("approval/decided", approval_id=APPROVAL, decision="approve",
                        auto_resolved=False, decided_by="user")
        self.link.observe(decided)
        self.link.observe(decided)
        changed = frame("approval/decided", approval_id=APPROVAL, decision="deny",
                        auto_resolved=False, decided_by="user")
        with self.assertRaisesRegex(OfficialSessionError, "approval_decision_invalid"):
            self.link.observe(changed)
        self.link.observe(frame("turn/error", code="runtime_error", message="failed"))
        with self.assertRaisesRegex(OfficialSessionError, "conflicting_terminal"):
            self.link.observe(frame("turn/completed", session_result={
                "message_id": "final-5", "committed_seq": 5}))
        with self.assertRaisesRegex(OfficialSessionError, "conflicting_approval_request"):
            self.link.observe(frame("approval/requested", approval_id=APPROVAL,
                                    tool_name="different"))

    def test_open_and_start_require_matching_official_responses(self):
        candidate = OfficialGoalSession(goal_id="goal-a", revision=2,
                                        plan_digest="sha256:example", session_id=SESSION)
        with self.assertRaisesRegex(OfficialSessionError, "session_open_mismatch"):
            candidate.accept_session_open({"result": {"opened": {
                "session_id": "other", "active_profile_id": "main"}}})
        candidate.accept_session_open({"result": {"opened": {
            "session_id": SESSION, "active_profile_id": "main"}}})
        with self.assertRaisesRegex(OfficialSessionError, "turn_not_accepted"):
            candidate.accept_turn_start(TURN, {"result": {"accepted": False}})


if __name__ == "__main__":
    unittest.main()
