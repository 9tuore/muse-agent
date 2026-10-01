import imaplib
import json
import tempfile
import time
import unittest
from email.message import EmailMessage
from pathlib import Path

from agent_app import LocalAgent
from g01_capabilities import CapabilityError, CapabilityHost
from qqmail_imap_bridge import QQMailIMAPBridge


class _FixtureIMAP:
    def __init__(self, raw_message: bytes):
        self.raw_message = raw_message

    def select(self, mailbox, readonly=True):
        assert mailbox == "INBOX"
        assert readonly is True
        return "OK", [b"1"]

    def uid(self, command, *args):
        if command == "search":
            return "OK", [b"42"]
        if command == "fetch":
            return "OK", [(b"42 (BODY[])", self.raw_message)]
        raise AssertionError(command)

    def logout(self):
        return "BYE", [b"logged out"]


class _DisconnectThenRecoverBridge(QQMailIMAPBridge):
    def __init__(self, workspace: Path, raw_message: bytes):
        super().__init__(workspace, "agent@qq.com", "fixture-code", allowed_sender="phone@example.com")
        self.raw_message = raw_message
        self.connected = False

    def _connect(self):
        if not self.connected:
            raise imaplib.IMAP4.error("fixture_disconnect")
        return _FixtureIMAP(self.raw_message)


class G02MailAndSystemChainTests(unittest.TestCase):
    @staticmethod
    def _mail_bytes():
        message = EmailMessage()
        message["From"] = "Phone <phone@example.com>"
        message["To"] = "agent@qq.com"
        message["Subject"] = "值班任务"
        message.set_content("请写入本地：邮件确认后的值班记录")
        return message.as_bytes()

    def test_mail_chain_has_event_id_approval_dedupe_and_readback(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            bridge = _DisconnectThenRecoverBridge(workspace, self._mail_bytes())
            with self.assertRaisesRegex(imaplib.IMAP4.error, "fixture_disconnect"):
                bridge.poll_once()
            bridge.connected = True
            self.assertEqual(bridge.poll_once(), 1)
            self.assertEqual(bridge.poll_once(), 0)
            event = json.loads((workspace / "inbox" / "events.jsonl").read_text().splitlines()[0])
            self.assertEqual(event["message_id"], "qqmail:42")
            self.assertTrue(event["trusted_sender"])

            agent = LocalAgent(workspace)
            proposed = agent.handle(event)
            self.assertEqual(proposed["event_id"], "qqmail:42")
            self.assertEqual(proposed["action_status"], "REQUIRES_EXPLICIT_CONFIRMATION")
            task_id = proposed["result_card"]["id"]
            self.assertTrue(task_id.startswith("card:"))
            self.assertEqual(proposed["task_card"]["metadata"]["source_message_id"], "qqmail:42")
            self.assertFalse((workspace / "message-note.txt").exists())

            duplicate = agent.handle(event)
            self.assertEqual(duplicate["status"], "DUPLICATE_IGNORED")
            completed = agent.handle({"type": "confirm", "approved": True})
            self.assertEqual(completed["result_card"]["id"], task_id)
            self.assertEqual(completed["verification"], "READBACK_MATCH")
            self.assertEqual(
                (workspace / "message-note.txt").read_text(encoding="utf-8"),
                "邮件确认后的值班记录\n",
            )

    def test_mail_chain_rejects_untrusted_sender_without_pending_action(self):
        with tempfile.TemporaryDirectory() as tmp:
            message = EmailMessage()
            message["From"] = "unknown@example.com"
            message["Subject"] = "值班任务"
            message.set_content("请写入本地：不可信邮件")
            from qqmail_imap_bridge import message_event_from_bytes

            event = message_event_from_bytes("43", message.as_bytes())
            result = LocalAgent(Path(tmp)).handle(event)
            self.assertEqual(result["action_status"], "BLOCKED_UNTRUSTED_MESSAGE")
            self.assertEqual(result["result_card"]["status"], "BLOCKED")
            self.assertFalse((Path(tmp) / "message-note.txt").exists())

    def test_system_chain_has_real_lease_id_expiry_and_recovery(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            host = CapabilityHost(workspace)
            task_id = f"system:{host.lease.lease_id}"
            status = host.execute("system.status")
            self.assertTrue(status["ok"])
            self.assertRegex(task_id, r"^system:g01-lease-[0-9a-f]+$")
            host.lease.expires_at = time.time() - 1
            with self.assertRaisesRegex(CapabilityError, "capability_lease_expired"):
                host.execute("system.status")

            recovered = CapabilityHost(workspace)
            recovered_status = recovered.execute("system.status")
            self.assertTrue(recovered_status["ok"])
            self.assertNotEqual(recovered.lease.lease_id, host.lease.lease_id)


if __name__ == "__main__":
    unittest.main()
