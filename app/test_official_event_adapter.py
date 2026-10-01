import tempfile
import unittest
from pathlib import Path

from agent_app import LocalAgent
from official_event_adapter import (
    OfficialEventAdapterError,
    adapt_official_event,
    adapter_metadata,
)


def _matrix_event(**overrides):
    event = {
        "adapter": "robrix2_matrix",
        "verified": True,
        "recipient_consent": True,
        "room_membership": "join",
        "room_id": "!g02:example.test",
        "sender_id": "@tester:example.test",
        "event_type": "m.room.message",
        "msgtype": "m.text",
        "transaction_id": "txn-001",
        "body": "请整理这条已审查消息",
    }
    event.update(overrides)
    return event


class OfficialEventAdapterTests(unittest.TestCase):
    def test_verified_matrix_event_becomes_local_agent_message(self):
        converted = adapt_official_event(_matrix_event())
        self.assertEqual(converted["type"], "message_event")
        self.assertEqual(converted["source"], "robrix2")
        self.assertTrue(converted["adapter_verified"])
        self.assertEqual(converted["message_id"], "txn-001")
        self.assertEqual(converted["text"], "请整理这条已审查消息")
        self.assertEqual(converted["live_status"], "NOT_LIVE")
        self.assertEqual(converted["capability_mode"], "deferred_only")
        with tempfile.TemporaryDirectory() as tmp:
            result = LocalAgent(Path(tmp)).handle(converted)
            self.assertEqual(result["status"], "PROCESSED")
            self.assertEqual(result["source"], "robrix2")
            self.assertEqual(result["official_adapter"]["live_status"], "NOT_LIVE")
            self.assertEqual(result["result_card"]["adapter_kind"], "robrix2_matrix")

    def test_verified_native_article_event_uses_official_msgtype(self):
        converted = adapt_official_event(
            _matrix_event(msgtype="rs.robius.robrix.article_app", body="[Mini app] Article editor")
        )
        self.assertEqual(converted["msgtype"], "rs.robius.robrix.article_app")

    def test_reviewed_appcard_result_uses_same_local_contract(self):
        event = _matrix_event(
            adapter="octosense_appcard",
            msgtype="m.text",
            transaction_id="appcard-001",
            body="AppCard 审查后的消息结果",
            review="approved",
            phase="completed",
            deferred_only=True,
        )
        converted = adapt_official_event(event)
        self.assertEqual(converted["adapter_kind"], "octosense_appcard")
        self.assertEqual(converted["msgtype"], "m.text")
        self.assertEqual(converted["message_id"], "appcard-001")

    def test_missing_verification_consent_membership_msgtype_or_transaction_is_rejected(self):
        cases = (
            ("verified", False, "verified_required"),
            ("recipient_consent", False, "recipient_consent_required"),
            ("room_membership", "invite", "room_membership_join_required"),
            ("msgtype", "m.image", "msgtype_not_allowed"),
            ("transaction_id", "", "transaction_id_required"),
        )
        for key, value, error in cases:
            with self.subTest(key=key):
                with self.assertRaisesRegex(OfficialEventAdapterError, error):
                    adapt_official_event(_matrix_event(**{key: value}))

    def test_appcard_requires_review_completed_phase_and_deferred_mode(self):
        base = _matrix_event(adapter="octosense_appcard", msgtype="m.text")
        for key, value, error in (
            ("review", "pending", "appcard_review_required"),
            ("phase", "proposed", "appcard_completed_result_required"),
            ("deferred_only", False, "appcard_deferred_only_required"),
        ):
            event = dict(base, review="approved", phase="completed", deferred_only=True)
            event[key] = value
            with self.subTest(key=key):
                with self.assertRaisesRegex(OfficialEventAdapterError, error):
                    adapt_official_event(event)

    def test_robrix_approval_wire_events_cannot_become_goal_messages(self):
        # robrix2's agent_chat feature uses a separate server-validated
        # approval protocol. Its request/status/verdict events are not text.
        for namespace in ("com.agentchat", "com.hafleet", "com.hagency"):
            for kind in ("request", "status", "verdict"):
                with self.subTest(namespace=namespace, kind=kind):
                    with self.assertRaisesRegex(OfficialEventAdapterError, "msgtype_not_allowed"):
                        adapt_official_event(_matrix_event(
                            msgtype=f"{namespace}.approval.{kind}.v1"))

    def test_metadata_declares_prototype_and_not_live(self):
        self.assertEqual(
            adapter_metadata(),
            {
                "adapter_status": "prototype",
                "capability_mode": "deferred_only",
                "live_status": "NOT_LIVE",
            },
        )


if __name__ == "__main__":
    unittest.main()
