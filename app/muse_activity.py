"""Opt-in, bounded frontmost-app Activity feed from native NSWorkspace events."""

from __future__ import annotations

import json
import os
import re
import select
import subprocess
from collections import deque
from pathlib import Path


_BUNDLE = re.compile(r"[A-Za-z0-9.-]{3,160}\Z")
_EXCLUDED = ("game", "steam", "password", "keychain", "bitwarden", "1password",
             "bank", "wallet", "payment")


class ActivityFeed:
    def __init__(self, helper: Path, *, allowed_bundle_ids: set[str], enabled: bool = False):
        self.helper = Path(helper)
        if not self.helper.is_file():
            raise ValueError("activity_helper_missing")
        self.allowed = set(allowed_bundle_ids)
        if (not 1 <= len(self.allowed) <= 16 or any(
                not isinstance(bundle, str) or not _BUNDLE.fullmatch(bundle) or "." not in bundle or
                any(word in bundle.lower() for word in _EXCLUDED) for bundle in self.allowed)):
            raise ValueError("activity_scope_invalid")
        self.enabled = enabled is True
        self.process: subprocess.Popen | None = None
        self.recent = deque(maxlen=100)
        self._pending_bytes = b""
        self._pending_lines = deque()

    def start(self) -> dict:
        if not self.enabled:
            return {"status": "DISABLED"}
        if self.process is not None:
            return {"status": "ALREADY_RUNNING"}
        try:
            self.process = subprocess.Popen([str(self.helper), json.dumps(sorted(self.allowed))],
                                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                            stderr=subprocess.DEVNULL)
        except OSError:
            return {"status": "BLOCKED", "error": "activity_helper_unavailable"}
        return {"status": "RUNNING", "source": "NSWorkspace",
                "observes": ["frontmost_snapshot", "frontmost_changed"],
                "unsupported": ["global_notifications", "lock_screen", "screen_content", "clipboard"]}

    def poll(self, timeout_seconds: float = 0.1) -> dict:
        if self.process is None or self.process.stdout is None:
            return {"status": "DISABLED" if not self.enabled else "NOT_RUNNING"}
        if not 0 <= timeout_seconds <= 5:
            return {"status": "INVALID_TIMEOUT"}
        if self.process.poll() is not None:
            return {"status": "BLOCKED", "error": "activity_helper_exited"}
        if not self._pending_lines:
            readable, _, _ = select.select([self.process.stdout], [], [], timeout_seconds)
            if not readable:
                return {"status": "NO_EVENT"}
            self._pending_bytes += os.read(self.process.stdout.fileno(), 4096)
            if len(self._pending_bytes) > 8192:
                return {"status": "BLOCKED", "error": "activity_event_too_large"}
            while b"\n" in self._pending_bytes:
                line, self._pending_bytes = self._pending_bytes.split(b"\n", 1)
                self._pending_lines.append(line)
        if not self._pending_lines:
            return {"status": "NO_EVENT"}
        try:
            event = json.loads(self._pending_lines.popleft().decode("utf-8"))
        except (TypeError, ValueError):
            return {"status": "BLOCKED", "error": "activity_event_invalid"}
        if (not isinstance(event, dict) or event.get("status") != "EVENT" or
                event.get("type") not in {"frontmost_snapshot", "frontmost_changed"} or
                event.get("bundle_id") not in self.allowed or event.get("source") != "NSWorkspace" or
                not isinstance(event.get("observed_at"), str)):
            return {"status": "BLOCKED", "error": "activity_event_outside_scope"}
        self.recent.append(event)
        return event

    def stop(self) -> None:
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=2)
            if self.process.stdout is not None:
                self.process.stdout.close()
            self.process = None
        self._pending_bytes = b""
        self._pending_lines.clear()

    def set_enabled(self, enabled: bool) -> dict:
        if enabled is not True:
            self.stop()
            self.enabled = False
            self.recent.clear()
            return {"status": "DISABLED", "recent_count": 0}
        self.enabled = True
        return self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *_):
        self.stop()
