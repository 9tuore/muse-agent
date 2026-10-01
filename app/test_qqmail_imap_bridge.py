import unittest
import json
import io
import os
import sys
import tempfile
import stat
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from email.message import EmailMessage

from qqmail_imap_bridge import message_event_from_bytes, message_text
from qqmail_imap_bridge import QQMailIMAPBridge
from qqmail_imap_bridge import _read_auth_code_from_stdin, main


class QQMailBridgeTests(unittest.TestCase):
    def _raw_message(self, sender="Phone <phone@example.com>"):
        message = EmailMessage()
        message["From"] = sender
        message["To"] = "agent@qq.com"
        message["Subject"] = "手机测试"
        message["Date"] = "Sat, 27 Sep 2026 09:00:00 +0800"
        message.set_content("请把这封邮件列入待办")
        return message.as_bytes()

    def test_health_status_records_connection_without_credentials(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge = QQMailIMAPBridge(Path(tmp), "agent@qq.com", "fixture-secret")
            bridge._write_health("CONNECTED", appended=1)
            path = Path(tmp) / ".qqmail_bridge_health.json"
            data = json.loads(path.read_text())
            self.assertEqual((data["status"], data["appended"]), ("CONNECTED", 1))
            self.assertNotIn("fixture-secret", path.read_text())
            self.assertNotIn("agent@qq.com", path.read_text())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_imap_connection_has_bounded_network_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            bridge = QQMailIMAPBridge(Path(tmp), "agent@qq.com", "fixture-secret")
            with patch("qqmail_imap_bridge.imaplib.IMAP4_SSL") as connect:
                bridge._connect()
            self.assertEqual(connect.call_args.kwargs["timeout"], 20)

    def test_recent_inbox_contacts_use_headers_only_and_reply_to(self):
        class Inbox:
            calls = []

            def uid(self, operation, *args):
                self.calls.append((operation, args))
                if operation == "search":
                    return "OK", [b"11 12 13"]
                assert b"BODY.PEEK[HEADER.FIELDS" in args[1].encode()
                return "OK", [
                    (b"1 (UID 11 BODY[HEADER.FIELDS] {12}",
                     b"From: Alice <alice@example.com>\r\nSubject: Older\r\nMessage-ID: <old@example.com>\r\n\r\n"),
                    (b"2 (UID 12 BODY[HEADER.FIELDS] {12}",
                     b"From: Bob <bob@example.com>\r\nReply-To: assistant@example.net\r\nSubject: Agenda\r\nMessage-ID: <bob@example.com>\r\n\r\n"),
                    (b"3 (UID 13 BODY[HEADER.FIELDS] {12}",
                     b"From: Alice <alice@example.com>\r\nSubject: Newer\r\nMessage-ID: <new@example.com>\r\n\r\n"),
                ]

        with tempfile.TemporaryDirectory() as tmp:
            bridge = QQMailIMAPBridge(Path(tmp), "agent@qq.com", "fixture-secret")
            client = Inbox()
            bridge._refresh_contacts(client)
            path = Path(tmp) / ".qqmail_contacts.json"
            contacts = json.loads(path.read_text())["contacts"]
            self.assertEqual([item["address"] for item in contacts],
                             ["alice@example.com", "assistant@example.net"])
            self.assertEqual(contacts[0]["subject"], "Newer")
            self.assertEqual(contacts[0]["message_id_header"], "<new@example.com>")
            self.assertNotIn("fixture-secret", path.read_text())
            self.assertNotIn("body", path.read_text().lower())
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)

    def test_event_is_bounded_and_untrusted_by_default(self):
        event = message_event_from_bytes("42", self._raw_message())
        self.assertEqual(event["source"], "qqmail")
        self.assertEqual(event["message_id"], "qqmail:42")
        self.assertFalse(event["trusted_sender"])
        self.assertEqual(event["event_id"], "qqmail:42")
        self.assertEqual(event["topic"], "mail.received")
        self.assertEqual(event["payload_ref"], "resource:qqmail-inbox")
        self.assertEqual(event["sensitivity"], "personal")
        self.assertIn("手机测试", event["text"])
        self.assertIn("列入待办", event["text"])
        self.assertFalse(event["metadata"]["body_stored"])

    def test_allowlisted_sender_can_be_trusted_for_local_fixture(self):
        event = message_event_from_bytes(
            "43", self._raw_message(), allowed_sender="phone@example.com"
        )
        self.assertTrue(event["trusted_sender"])

    def test_message_text_does_not_include_attachment_body(self):
        message = EmailMessage()
        message["Subject"] = "附件测试"
        message.set_content("正文")
        message.add_attachment(b"secret", maintype="application", subtype="octet-stream", filename="x.bin")
        self.assertIn("正文", message_text(message_from_bytes_for_test(message.as_bytes())))
        self.assertNotIn("secret", message_text(message_from_bytes_for_test(message.as_bytes())))

    def test_reply_outbox_uses_authenticated_bridge_and_emits_result(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            bridge = QQMailIMAPBridge(workspace, "agent@qq.com", "fixture-code")
            reply_dir = workspace / "outbox" / "qqmail-replies"
            reply_dir.mkdir(parents=True)
            request = {
                "request_id": "reply:fixture-1",
                "to": "friend@example.com",
                "subject": "周末",
                "body": "好的，周六见！",
                "in_reply_to": "<fixture@example.com>",
            }
            (reply_dir / "fixture.json").write_text(json.dumps(request, ensure_ascii=False), encoding="utf-8")
            sent = []
            bridge._send_reply = lambda value: sent.append(value)  # type: ignore[method-assign]
            self.assertEqual(bridge._process_reply_outbox(), 1)
            self.assertEqual(sent[0]["to"], "friend@example.com")
            event = json.loads((workspace / "inbox" / "events.jsonl").read_text(encoding="utf-8").strip())
            self.assertEqual(event["type"], "qqmail_reply_result")
            self.assertEqual(event["status"], "SENT")
            self.assertEqual(event["event_id"], "reply:fixture-1")
            self.assertTrue(event["account_scope"].startswith("qqmail:"))
            self.assertNotIn("@", event["account_scope"])
            self.assertEqual(stat.S_IMODE((workspace / "inbox").stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE((workspace / "inbox" / "events.jsonl").stat().st_mode), 0o600)
            self.assertFalse((reply_dir / "fixture.json").exists())

    def test_private_stdin_auth_code_is_bounded_and_not_printed(self):
        self.assertEqual(_read_auth_code_from_stdin(io.BytesIO(b"fixture-code\n")), "fixture-code")
        for raw in (b"", b"\n", b"missing-newline", b"x" * 257 + b"\n", b"\xff\n"):
            with self.assertRaises(ValueError):
                _read_auth_code_from_stdin(io.BytesIO(raw))

        seen = []
        class FakeBridge:
            def __init__(self, workspace, address, auth_code, **kwargs):
                seen.append((address, auth_code))

            def poll_once(self):
                return 0

        output = io.StringIO()
        argv = ["qqmail_imap_bridge.py", "--workspace", "/tmp/qqmail-stdin-fixture",
                "--address", "agent@qq.com", "--auth-code-stdin", "--once"]
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", argv), \
                patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"fixture-code\n"))), \
                patch("qqmail_imap_bridge.QQMailIMAPBridge", FakeBridge), redirect_stdout(output):
            main()
        self.assertEqual(seen, [("agent@qq.com", "fixture-code")])
        self.assertNotIn("fixture-code", output.getvalue())

        with patch.dict(os.environ, {"QQMAIL_AUTH_CODE": "fixture-env"}, clear=True), \
                patch.object(sys, "argv", argv), patch("qqmail_imap_bridge.QQMailIMAPBridge", FakeBridge):
            with self.assertRaises(SystemExit):
                main()
        self.assertEqual(len(seen), 1)

        missing_address = ["qqmail_imap_bridge.py", "--auth-code-stdin", "--once"]
        with patch.dict(os.environ, {}, clear=True), patch.object(sys, "argv", missing_address), \
                patch("builtins.input", side_effect=AssertionError("stdin_secret_read_as_address")):
            with self.assertRaisesRegex(SystemExit, "qqmail_address_required_for_stdin_auth"):
                main()


def message_from_bytes_for_test(raw):
    from email import message_from_bytes
    from email.policy import default

    return message_from_bytes(raw, policy=default)


if __name__ == "__main__":
    unittest.main()
