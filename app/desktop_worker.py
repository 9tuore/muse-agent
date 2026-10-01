#!/usr/bin/env python3
"""Persistent JSONL worker used by the native AppKit desktop bundle."""
from __future__ import annotations

import os
import json
import fcntl
import hashlib
import hmac
import sys
import threading
import time
import uuid
from pathlib import Path

from agent_app import LocalAgent, LocalModelRouter, run_stream
from muse_events import normalize_event
from official_event_adapter import OfficialEventAdapterError, adapt_official_event, adapter_metadata
from muse_official_bridge import OfficialGoalBridge


class _LockedWriter:
    """Serialize foreground stdin replies and background inbox replies."""

    def __init__(self, stream):
        self.stream = stream
        self.lock = threading.Lock()

    def write(self, value: str) -> None:
        with self.lock:
            self.stream.write(value)

    def flush(self) -> None:
        with self.lock:
            self.stream.flush()


class _NativeOfficialHost:
    """Keep official approval off the inbox and model-facing event routes."""

    def __init__(self, agent: LocalAgent, witness_secret: str):
        self.agent = agent
        self.secret = witness_secret.encode("utf-8") if len(witness_secret) >= 64 else b""
        self.used_nonces: set[str] = set()
        self.bridge = OfficialGoalBridge(
            agent.workspace, agent.muse_capabilities,
            native_click_guard=self._verify_click if self.secret else None,
        )

    @staticmethod
    def _signed_message(pending: dict, decision: str, nonce: str) -> bytes:
        fields = (pending["pending_id"], str(pending["revision"]), pending["plan_digest"],
                  pending["official_session_id"], pending["official_turn_id"],
                  pending["official_tool_call_id"], pending["official_call_nonce"],
                  decision, nonce)
        return b"|".join(str(len(value.encode("utf-8"))).encode("ascii") + b":" +
                         value.encode("utf-8") for value in fields)

    def _verify_click(self, witness: object, pending: dict) -> bool:
        if not self.secret or not isinstance(witness, dict) or set(witness) != {
                "nonce", "decision", "mac"}:
            return False
        nonce, decision, mac = (witness.get(key) for key in ("nonce", "decision", "mac"))
        if not isinstance(nonce, str) or not isinstance(mac, str) or decision not in {
                "approve", "deny"} or nonce in self.used_nonces:
            return False
        try:
            if uuid.UUID(nonce).version != 4:
                return False
            expected = hmac.new(self.secret, self._signed_message(pending, decision, nonce),
                                hashlib.sha256).hexdigest()
        except (ValueError, KeyError, AttributeError):
            return False
        if not hmac.compare_digest(expected, mac):
            return False
        self.used_nonces.add(nonce)
        return True

    def handle(self, event: dict) -> dict:
        event_type = event.get("type") if isinstance(event, dict) else None
        if event_type == "official_pending_list":
            if set(event) != {"type"}:
                return {"ok": False, "operation": event_type, "error": "invalid_request"}
            return {"ok": True, "operation": event_type, "status": "READY",
                    "approval_available": bool(self.secret),
                    "pending": self.bridge.list_pending_for_ui()}
        if event_type == "official_native_decide":
            if set(event) != {"type", "pending_id", "decision", "reviewed_digest",
                              "native_witness"}:
                return {"ok": False, "operation": event_type, "error": "invalid_request"}
            witness = event["native_witness"]
            if (not self.secret or not isinstance(witness, dict) or
                    witness.get("decision") != event["decision"]):
                return {"ok": False, "operation": event_type,
                        "error": "native_click_not_verified"}
            result = self.bridge.decide_from_native(
                event["pending_id"], event["decision"], event["reviewed_digest"], witness)
            return {"operation": event_type, **result}
        return self.agent.handle(event)


def _emit(sink: _LockedWriter, result: dict) -> None:
    sink.write(json.dumps(result, ensure_ascii=False) + "\n")
    sink.flush()


def _watch_goals(agent: LocalAgent, sink: _LockedWriter, stop: threading.Event) -> None:
    """Advance approved, due goals while the native application is resident."""
    reported_watch_errors = {}
    brief_last_emitted = {}
    last_activity_error = None
    while not stop.is_set():
        try:
            for observed in agent.muse_watches.poll():
                response = agent.handle({"type": "goal_event", "event": observed})
                for result in response.get("results", []):
                    _emit(sink, result)
            watch_errors = agent.muse_watches.last_errors
            if watch_errors != reported_watch_errors:
                for resource_ref, reason in watch_errors.items():
                    _emit(sink, {"ok": False, "status": "WATCH_BLOCKED", "resource_ref": resource_ref,
                                 "error": reason})
                reported_watch_errors = watch_errors.copy()
            response = agent.handle({"type": "goal_tick"})
            for result in response.get("results", []):
                _emit(sink, result)
            brief = agent.handle({"type": "brief_tick"})
            if brief.get("status") == "BRIEF_READY":
                brief_id = brief["brief"]["brief_id"]
                if time.monotonic() - brief_last_emitted.get(brief_id, -1e9) >= 60:
                    _emit(sink, brief)
                    brief_last_emitted[brief_id] = time.monotonic()
            elif brief.get("reason") in {"brief_off", "already_delivered"}:
                brief_last_emitted.clear()
            activity = agent.handle({"type": "activity_poll"})
            if activity.get("status") == "EVENT":
                _emit(sink, activity)
                last_activity_error = None
            elif activity.get("status") == "BLOCKED":
                if activity.get("error") != last_activity_error:
                    _emit(sink, activity)
                    last_activity_error = activity.get("error")
            else:
                last_activity_error = None
        except Exception as exc:
            _emit(sink, {"ok": False, "status": "GOAL_TICK_FAILED", "error": str(exc)[:240]})
        stop.wait(2.0)


def _watch_local_inbox(path: Path, agent: LocalAgent, sink: _LockedWriter, stop: threading.Event) -> None:
    """Tail a local JSONL inbox so the resident worker can react without UI input.

    The inbox is intentionally local and allowlisted to message/control/status
    events plus strictly verified Robrix2/OctoSense host envelopes. It is a
    testable stand-in for an approved external connector; it does not read
    WeChat, notifications, databases, or arbitrary files.
    """
    if path.parent.is_symlink() or path.is_symlink():
        raise ValueError("local_inbox_symlink_rejected")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.parent.chmod(0o700)
    path.touch(exist_ok=True)
    path.chmod(0o600)
    with path.open("r", encoding="utf-8") as stream:
        while not stop.is_set():
            line = stream.readline()
            if not line:
                stop.wait(0.25)
                continue
            if not line.strip():
                continue
            event = None
            try:
                event = json.loads(line)
                if (not isinstance(event, dict) or event.get("type") not in {
                    "message_event",
                    "message_control",
                    "message_status",
                    "qqmail_reply_result",
                    "chat_message",
                    "memory_search",
                    "memory_index_folder",
                    "system_status",
                    "health",
                    "robrix2_event",
                    "octosense_appcard_result",
                } or (event.get("type") == "chat_message" and "memory_scopes" in event)):
                    result = {"ok": False, "error": "local_inbox_event_rejected"}
                else:
                    if event.get("type") in {"robrix2_event", "octosense_appcard_result"}:
                        try:
                            event = adapt_official_event(event)
                        except OfficialEventAdapterError as exc:
                            reason = str(exc)
                            result = {
                                "ok": False,
                                "status": "BLOCKED_UNVERIFIED",
                                "error": reason,
                                **adapter_metadata(),
                            }
                            result["result_card"] = agent.blocked_result_card(
                                "robrix2", "BLOCKED_UNVERIFIED", reason
                            )
                        else:
                            result = agent.handle(event)
                    else:
                        result = agent.handle(event)
            except (json.JSONDecodeError, TypeError) as exc:
                result = {"ok": False, "error": "invalid_json", "detail": str(exc)}
            if result.get("status") == "IGNORED":
                continue
            _emit(sink, result)
            # The message queue may have committed just before a process crash.
            # Re-offer its inbox line to GoalStore on restart; GoalStore dedupes
            # the event and rejects observations predating approval.
            if (isinstance(event, dict) and event.get("type") == "message_event"
                    and result.get("status") in {"PROCESSED", "DUPLICATE_IGNORED"}):
                try:
                    mail_bridge = (event.get("source") == "qqmail" and
                                   isinstance(event.get("metadata"), dict) and
                                   event["metadata"].get("transport") == "imap.qq.com:993/tls")
                    observed = dict(event)
                    if mail_bridge:
                        # Existing QQ bridge processes may predate the
                        # normalized topic/ref fields. This local file route is
                        # trusted only as a same-user connector observation.
                        observed.update(topic="mail.received", payload_ref="resource:qqmail-inbox")
                    supplied_scope = observed.get("account_scope")
                    mail_scope = (supplied_scope if isinstance(supplied_scope, str)
                                  and supplied_scope.startswith("qqmail:")
                                  and len(supplied_scope) == len("qqmail:") + 16
                                  and all(character in "0123456789abcdef" for character in supplied_scope[7:])
                                  else "qqmail:legacy-single-account")
                    normalized = normalize_event(
                        observed,
                        account_scope=mail_scope if mail_bridge else "local-inbox",
                        allowed_resource_refs={"resource:qqmail-inbox"} if mail_bridge else set(),
                    )
                    response = agent.handle({"type": "goal_event", "event": normalized})
                    for goal_result in response.get("results", []):
                        _emit(sink, goal_result)
                except (TypeError, ValueError) as exc:
                    _emit(sink, {"ok": False, "status": "GOAL_EVENT_REJECTED", "error": str(exc)[:240]})


def main() -> None:
    workspace = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Library/Application Support/GOSIM Local Agent/workspace"
    workspace.mkdir(parents=True, exist_ok=True)
    # One resident worker owns a workspace, including when two app versions
    # share the same bundle identifier and SQLite database during an upgrade.
    try:
        lock_fd = os.open(str(workspace / ".muse_worker.lock"),
                          os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    except OSError:
        print(json.dumps({"ok": False, "status": "WORKSPACE_LOCK_FAILED"}), flush=True)
        return
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(lock_fd)
        print(json.dumps({"ok": False, "status": "WORKSPACE_IN_USE"}), flush=True)
        return
    except OSError:
        os.close(lock_fd)
        print(json.dumps({"ok": False, "status": "WORKSPACE_LOCK_FAILED"}), flush=True)
        return
    try:
        _run_workspace(workspace)
    finally:
        os.close(lock_fd)


def _run_workspace(workspace: Path) -> None:
    native_witness_secret = os.environ.pop("MUSE_NATIVE_WITNESS_SECRET", "")
    agent = LocalAgent(workspace, LocalModelRouter(os.environ.get("LOCAL_MODEL_URL", "http://127.0.0.1:8080/v1/chat/completions")))
    native_host = _NativeOfficialHost(agent, native_witness_secret)
    sink = _LockedWriter(sys.stdout)
    stop = threading.Event()
    watcher = None
    goal_watcher = threading.Thread(target=_watch_goals, args=(agent, sink, stop), daemon=True)
    goal_watcher.start()
    if os.environ.get("GOSIM_LOCAL_INBOX", "1") != "0":
        inbox = Path(os.environ.get("GOSIM_LOCAL_INBOX_FILE", str(workspace / "inbox" / "events.jsonl")))
        watcher = threading.Thread(target=_watch_local_inbox, args=(inbox, agent, sink, stop), daemon=True)
        watcher.start()
    try:
        run_stream(native_host, sink=sink)
    finally:
        stop.set()
        goal_watcher.join(timeout=2.0)
        if watcher is not None:
            watcher.join(timeout=1.0)
        if agent._muse_activity is not None:
            agent._muse_activity.stop()


if __name__ == "__main__":
    main()
