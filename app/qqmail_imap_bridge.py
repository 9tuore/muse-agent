#!/usr/bin/env python3
"""Small, explicit QQ Mail IMAP bridge for the resident local agent.

The bridge only connects to QQ Mail's TLS IMAP endpoint, reads unseen messages
with BODY.PEEK, and writes redacted ``message_event`` envelopes into the local
inbox watched by ``desktop_worker.py``.  It never stores the password or full
message body in its state file.  QQ Mail authorization codes are supplied at
runtime through a private stdin pipe, environment variables, or a local
terminal prompt.
"""

from __future__ import annotations

import argparse
import getpass
import hashlib
import imaplib
import json
import os
import re
import ssl
import smtplib
import sys
import time
from datetime import datetime, timezone
from email import message_from_bytes
from email.header import decode_header, make_header
from email.message import Message
from email.message import EmailMessage
from email.policy import default
from email.utils import parseaddr
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from muse_events import normalize_event


IMAP_HOST = "imap.qq.com"
IMAP_PORT = 993
SMTP_HOST = "smtp.qq.com"
SMTP_PORT = 465
MAX_BODY_CHARS = 4000
MAX_REPLY_CHARS = 4000
MAX_AUTH_CODE_BYTES = 256
CONTACT_REFRESH_SECONDS = 120


def _decode_header(value: Optional[str]) -> str:
    if not value:
        return ""
    try:
        return str(make_header(decode_header(value))).strip()
    except (LookupError, UnicodeError, ValueError):
        return value.strip()


def _text_parts(message: Message) -> Iterable[str]:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() != "text/plain":
                continue
            try:
                value = part.get_content()
            except (LookupError, UnicodeError, AttributeError):
                payload = part.get_payload(decode=True) or b""
                value = payload.decode(part.get_content_charset() or "utf-8", errors="replace")
            if isinstance(value, str) and value.strip():
                yield value.strip()
        return
    if message.get_content_type() == "text/plain":
        try:
            value = message.get_content()
        except (LookupError, UnicodeError, AttributeError):
            payload = message.get_payload(decode=True) or b""
            value = payload.decode(message.get_content_charset() or "utf-8", errors="replace")
        if isinstance(value, str) and value.strip():
            yield value.strip()


def message_text(message: Message) -> str:
    """Return a bounded subject/body summary for local routing."""
    subject = _decode_header(message.get("Subject"))
    body = "\n\n".join(_text_parts(message))
    if not body:
        body = "（邮件没有可读取的纯文本正文）"
    text = "\n".join(part for part in (f"主题：{subject}" if subject else "", body) if part)
    return text[:MAX_BODY_CHARS]


def message_event_from_bytes(
    uid: str,
    raw_message: bytes,
    *,
    allowed_sender: Optional[str] = None,
    account_scope: Optional[str] = None,
) -> Dict[str, Any]:
    """Convert one fetched message into the local agent's message schema."""
    message = message_from_bytes(raw_message, policy=default)
    sender_name, sender_address = parseaddr(_decode_header(message.get("From")))
    sender_address = sender_address.strip().lower()
    trusted = bool(allowed_sender and sender_address == allowed_sender.strip().lower())
    message_id = f"qqmail:{uid}"
    event = {
        "type": "message_event",
        "source": "qqmail",
        "topic": "mail.received",
        "payload_ref": "resource:qqmail-inbox",
        "message_id": message_id,
        "conversation_id": f"qqmail:{sender_address or 'unknown'}",
        "direction": "incoming",
        "sender_id": sender_address or sender_name or "unknown",
        "trusted_sender": trusted,
        "text": message_text(message),
        "metadata": {
            "uid": str(uid),
            "subject": _decode_header(message.get("Subject"))[:240],
            "sender": sender_address[:240],
            "date": _decode_header(message.get("Date"))[:80],
            "message_id_header": _decode_header(message.get("Message-ID"))[:240],
            "transport": "imap.qq.com:993/tls",
            "body_stored": False,
        },
    }
    event.update(normalize_event(
        event, account_scope=account_scope, allowed_resource_refs={"resource:qqmail-inbox"}
    ))
    return event


class QQMailIMAPBridge:
    """Poll unseen QQ Mail messages and append local events."""

    def __init__(
        self,
        workspace: Path,
        address: str,
        auth_code: str,
        *,
        allowed_sender: Optional[str] = None,
        poll_seconds: float = 10.0,
    ):
        self.workspace = workspace.resolve()
        self.address = address.strip()
        self.auth_code = auth_code
        self.allowed_sender = allowed_sender.strip().lower() if allowed_sender else None
        self.poll_seconds = max(3.0, float(poll_seconds))
        self.inbox_path = self.workspace / "inbox" / "events.jsonl"
        self.reply_dir = self.workspace / "outbox" / "qqmail-replies"
        self.state_path = self.workspace / ".qqmail_bridge_state.json"
        self.health_path = self.workspace / ".qqmail_bridge_health.json"
        self.contacts_path = self.workspace / ".qqmail_contacts.json"
        self.last_contacts_refresh = 0.0
        self.seen_uids = self._load_seen_uids()

    def _write_health(self, status: str, *, appended: int = 0, error: str = "") -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        value = {"version": 1, "status": status,
                 "checked_at": datetime.now(timezone.utc).isoformat(),
                 "appended": appended, "error": error}
        temporary = self.health_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        os.replace(temporary, self.health_path)

    def _load_seen_uids(self) -> set[str]:
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
            values = state.get("seen_uids", [])
            if isinstance(values, list):
                return {str(value) for value in values[-2048:]}
        except (OSError, ValueError, TypeError):
            pass
        return set()

    def _persist_seen_uids(self) -> None:
        self.workspace.mkdir(parents=True, exist_ok=True)
        temporary = self.state_path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps({"version": 1, "seen_uids": sorted(self.seen_uids)[-2048:]}, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, self.state_path)

    def _connect(self) -> imaplib.IMAP4_SSL:
        context = ssl.create_default_context()
        client = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, ssl_context=context, timeout=20)
        client.login(self.address, self.auth_code)
        return client

    def _account_scope(self) -> str:
        # Stable local account identity without putting an email address into
        # GoalSpec resource references or normalized event routing fields.
        digest = hashlib.sha256(self.address.strip().lower().encode("utf-8")).hexdigest()[:16]
        return "qqmail:" + digest

    def _refresh_contacts(self, client: imaplib.IMAP4_SSL) -> None:
        """List recent inbox correspondents from headers only, without changing read flags."""
        status, data = client.uid("search", None, "ALL")
        if status != "OK":
            raise RuntimeError("qqmail_contacts_search_failed")
        uids = (data[0].split() if data and data[0] else [])[-60:]
        headers: Dict[bytes, bytes] = {}
        if uids:
            status, fetched = client.uid(
                "fetch", b",".join(uids),
                "(UID BODY.PEEK[HEADER.FIELDS (FROM REPLY-TO SUBJECT MESSAGE-ID DATE)])",
            )
            if status != "OK":
                raise RuntimeError("qqmail_contacts_fetch_failed")
            for item in fetched or []:
                if not isinstance(item, tuple) or not isinstance(item[1], bytes):
                    continue
                match = re.search(rb"\bUID\s+(\d+)\b", item[0] if isinstance(item[0], bytes) else b"")
                if match:
                    headers[match.group(1)] = item[1]
        contacts = []
        seen = set()
        for uid in reversed(uids):
            raw = headers.get(uid)
            if not raw:
                continue
            message = message_from_bytes(raw, policy=default)
            name, from_address = parseaddr(_decode_header(message.get("From")))
            _, reply_address = parseaddr(_decode_header(message.get("Reply-To")))
            address = (reply_address or from_address).strip().lower()
            if (not re.fullmatch(r"[^@\s<>]+@[^@\s<>]+\.[^@\s<>]+", address)
                    or address == self.address.lower() or address in seen):
                continue
            seen.add(address)
            subject = _decode_header(message.get("Subject")).replace("\r", " ").replace("\n", " ")[:240]
            header_id = _decode_header(message.get("Message-ID")).replace("\r", "").replace("\n", "")[:240]
            contacts.append({
                "contact_id": hashlib.sha256((self._account_scope() + ":" + address).encode()).hexdigest()[:24],
                "name": name.replace("\r", " ").replace("\n", " ")[:100],
                "address": address[:320], "subject": subject,
                "message_id_header": header_id, "source_message_id": "qqmail:" + uid.decode("ascii"),
            })
            if len(contacts) == 30:
                break
        value = {"version": 1, "checked_at": datetime.now(timezone.utc).isoformat(),
                 "source": "qqmail_imap_recent_inbox_headers", "contacts": contacts}
        temporary = self.contacts_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        os.replace(temporary, self.contacts_path)

    def poll_once(self) -> int:
        # Reply requests are intentionally handled by this same authenticated
        # bridge process.  The desktop worker never receives or stores the
        # QQ authorization code.
        self._process_reply_outbox()
        client = self._connect()
        appended = 0
        try:
            status, _ = client.select("INBOX", readonly=True)
            if status != "OK":
                raise RuntimeError("qqmail_select_failed")
            status, data = client.uid("search", None, "UNSEEN")
            if status != "OK":
                raise RuntimeError("qqmail_search_failed")
            raw_uids = data[0].split() if data and data[0] else []
            for raw_uid in raw_uids:
                uid = raw_uid.decode("ascii", errors="ignore")
                if not uid or uid in self.seen_uids:
                    continue
                status, fetched = client.uid("fetch", raw_uid, "(BODY.PEEK[])")
                if status != "OK":
                    continue
                raw_message = next(
                    (item[1] for item in fetched if isinstance(item, tuple) and isinstance(item[1], bytes)),
                    None,
                )
                if not raw_message:
                    continue
                event = message_event_from_bytes(
                    uid, raw_message, allowed_sender=self.allowed_sender,
                    account_scope=self._account_scope()
                )
                self._append_event(event)
                self.seen_uids.add(uid)
                appended += 1
            self._persist_seen_uids()
            if time.monotonic() - self.last_contacts_refresh >= CONTACT_REFRESH_SECONDS:
                try:
                    self._refresh_contacts(client)
                except (OSError, imaplib.IMAP4.error, RuntimeError, ValueError) as exc:
                    print(f"qqmail_contacts={type(exc).__name__}", flush=True)
                self.last_contacts_refresh = time.monotonic()
            return appended
        finally:
            try:
                client.logout()
            except (imaplib.IMAP4.error, OSError):
                pass

    def _send_reply(self, request: Dict[str, Any]) -> None:
        recipient = str(request.get("to", "")).strip()
        subject = str(request.get("subject", "")).strip()[:240]
        body = str(request.get("body", "")).strip()
        if "@" not in recipient or len(recipient) > 320:
            raise ValueError("qqmail_reply_recipient_invalid")
        if not body or len(body) > MAX_REPLY_CHARS:
            raise ValueError("qqmail_reply_body_invalid")
        message = EmailMessage()
        message["From"] = self.address
        message["To"] = recipient
        message["Subject"] = subject if subject.lower().startswith("re:") else f"Re: {subject}" if subject else "回复"
        in_reply_to = str(request.get("in_reply_to", "")).strip()
        if in_reply_to:
            message["In-Reply-To"] = in_reply_to[:240]
            message["References"] = in_reply_to[:240]
        message.set_content(body)
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=20) as client:
            client.login(self.address, self.auth_code)
            client.send_message(message)

    def _process_reply_outbox(self) -> int:
        """Send atomically-created reply files and emit a bounded result event."""
        if not self.reply_dir.exists():
            return 0
        processed = 0
        for path in sorted(self.reply_dir.glob("*.json")):
            request: Dict[str, Any] = {}
            try:
                request = json.loads(path.read_text(encoding="utf-8"))
                if not isinstance(request, dict):
                    raise ValueError("qqmail_reply_request_invalid")
                request_id = str(request.get("request_id", "")).strip()[:160]
                if not request_id:
                    raise ValueError("qqmail_reply_request_id_missing")
                self._send_reply(request)
                event = {
                    "type": "qqmail_reply_result",
                    "source": "qqmail",
                    "request_id": request_id,
                    "status": "SENT",
                    "recipient": str(request.get("to", ""))[:240],
                    "subject": str(request.get("subject", ""))[:240],
                    "transport": "smtp.qq.com:465/tls",
                }
            except (OSError, smtplib.SMTPException, ValueError, TypeError, json.JSONDecodeError) as exc:
                event = {
                    "type": "qqmail_reply_result",
                    "source": "qqmail",
                    "request_id": str(request.get("request_id", path.stem))[:160],
                    "status": "FAILED",
                    "error": type(exc).__name__,
                }
            event.update(normalize_event(event, account_scope=self._account_scope()))
            self._append_event(event)
            try:
                path.unlink()
            except OSError:
                pass
            processed += 1
        return processed

    def _append_event(self, event: Dict[str, Any]) -> None:
        inbox = self.inbox_path.parent
        inbox.mkdir(parents=True, exist_ok=True, mode=0o700)
        if inbox.is_symlink() or inbox.resolve() != self.workspace / "inbox":
            raise OSError("qqmail_inbox_symlink_rejected")
        os.chmod(inbox, 0o700)
        fd = os.open(str(self.inbox_path), os.O_WRONLY | os.O_APPEND | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            os.fchmod(fd, 0o600)
            with os.fdopen(fd, "a", encoding="utf-8", closefd=False) as stream:
                stream.write(json.dumps(event, ensure_ascii=False, separators=(",", ":")) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
        finally:
            os.close(fd)

    def run_forever(self) -> None:
        while True:
            try:
                appended = self.poll_once()
                self._write_health("CONNECTED", appended=appended)
            except (OSError, imaplib.IMAP4.error, RuntimeError, ValueError) as exc:
                self._write_health("ERROR", error=type(exc).__name__)
                print(f"qqmail_poll={type(exc).__name__}", flush=True)
            time.sleep(self.poll_seconds)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Poll QQ Mail over TLS IMAP into the local agent inbox")
    parser.add_argument("--workspace", type=Path, default=Path.home() / "Library/Application Support/GOSIM Local Agent/workspace")
    parser.add_argument("--address", default=os.environ.get("QQMAIL_ADDRESS"))
    parser.add_argument("--auth-code", default=os.environ.get("QQMAIL_AUTH_CODE"))
    parser.add_argument("--auth-code-stdin", action="store_true")
    parser.add_argument("--allowed-sender", default=os.environ.get("QQMAIL_ALLOWED_SENDER"))
    parser.add_argument("--poll-seconds", type=float, default=float(os.environ.get("QQMAIL_POLL_SECONDS", "10")))
    parser.add_argument("--once", action="store_true")
    return parser


def _read_auth_code_from_stdin(stream: Any) -> str:
    raw = stream.readline(MAX_AUTH_CODE_BYTES + 2)
    if not raw.endswith(b"\n"):
        raise ValueError("qqmail_auth_code_stdin_line_required")
    value = raw[:-1].removesuffix(b"\r")
    if not value or len(value) > MAX_AUTH_CODE_BYTES:
        raise ValueError("qqmail_auth_code_stdin_invalid")
    try:
        code = value.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("qqmail_auth_code_stdin_invalid") from exc
    if not code.strip() or any(ord(character) < 32 for character in code):
        raise ValueError("qqmail_auth_code_stdin_invalid")
    return code.strip()


def main() -> None:
    args = _parser().parse_args()
    if args.auth_code_stdin:
        if args.auth_code:
            raise SystemExit("--auth-code-stdin 与 --auth-code/QQMAIL_AUTH_CODE 不能并用")
        if not args.address or not args.address.strip():
            raise SystemExit("qqmail_address_required_for_stdin_auth")
        address = args.address.strip()
        try:
            auth_code = _read_auth_code_from_stdin(sys.stdin.buffer)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
    else:
        address = (args.address or input("QQ邮箱地址：")).strip()
        auth_code = args.auth_code or getpass.getpass("QQ邮箱授权码（不会写入仓库）：")
    if not address or not auth_code:
        raise SystemExit("QQ邮箱地址和授权码不能为空")
    bridge = QQMailIMAPBridge(
        args.workspace,
        address,
        auth_code,
        allowed_sender=args.allowed_sender,
        poll_seconds=args.poll_seconds,
    )
    if args.once:
        print(json.dumps({"appended": bridge.poll_once()}, ensure_ascii=False))
    else:
        bridge.run_forever()


if __name__ == "__main__":
    main()
