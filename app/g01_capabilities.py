#!/usr/bin/env python3
"""G-01's bounded capability host for local, owned test actions.

This module is intentionally independent from the message and desktop agents.
It exposes a small typed action set and an in-memory capability lease so the
project can exercise the same policy boundary as the official runtime without
pretending that Python is an OctoScript host.

The only process this module may stop is the test worker it started itself. A
worker identity is checked from both a per-run token and the process command
line before a signal is sent.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import secrets
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional


MAX_FILE_BYTES = 64 * 1024
WORKER_POLL_SECONDS = 0.10
WORKER_START_TIMEOUT_SECONDS = 8.0
WORKER_STOP_TIMEOUT_SECONDS = 2.0


class CapabilityError(RuntimeError):
    """A rejected capability request or an observed action failure."""


@dataclass
class CapabilityLease:
    """A host-issued, attenuated lease for this adapter instance.

    This is a local policy object, not the official OctoScript
    ``CapabilityLease`` type. The mapping to the official lease is documented
    in ``docs/official_integration.md``.
    """

    lease_id: str
    allowed_tools: frozenset[str]
    max_calls: Dict[str, int]
    expires_at: float
    calls: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def issue(
        cls,
        tools: Iterable[str],
        *,
        max_calls: Optional[Mapping[str, int]] = None,
        ttl_seconds: float = 60.0,
    ) -> "CapabilityLease":
        allowed = frozenset(tools)
        limits = {tool: int((max_calls or {}).get(tool, 1)) for tool in allowed}
        if not allowed or any(limit <= 0 for limit in limits.values()):
            raise ValueError("a lease needs at least one positive call limit")
        if ttl_seconds <= 0:
            raise ValueError("lease ttl must be positive")
        return cls(
            lease_id=f"g01-lease-{secrets.token_hex(8)}",
            allowed_tools=allowed,
            max_calls=limits,
            expires_at=time.time() + ttl_seconds,
        )

    def charge(self, tool: str) -> None:
        if time.time() >= self.expires_at:
            raise CapabilityError("capability_lease_expired")
        if tool not in self.allowed_tools:
            raise CapabilityError("capability_not_granted")
        used = self.calls.get(tool, 0)
        if used >= self.max_calls[tool]:
            raise CapabilityError("capability_call_limit_exceeded")
        self.calls[tool] = used + 1


def _atomic_json_write(path: Path, value: Mapping[str, Any]) -> None:
    """Write a small state record without exposing a partially-written file."""

    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _read_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CapabilityError(f"worker_record_unreadable:{type(exc).__name__}") from exc
    if not isinstance(value, dict):
        raise CapabilityError("worker_record_invalid")
    return value


def _process_command(pid: int) -> str:
    """Return a process command line using a bounded, local OS query."""

    try:
        completed = subprocess.run(
            ["ps", "-p", str(pid), "-o", "command="],
            check=False,
            capture_output=True,
            text=True,
            timeout=1.0,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return completed.stdout.strip()


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except (OSError, ProcessLookupError):
        return False
    return True


def _worker_loop(record_path: Path, token: str) -> int:
    """Run the intentionally tiny worker used only by G-01 tests."""

    stopping = False

    def request_stop(_signum: int, _frame: Any) -> None:
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    started_at = time.time()
    while not stopping:
        _atomic_json_write(
            record_path,
            {
                "worker": "g01-test-worker",
                "state": "running",
                "pid": os.getpid(),
                "token": token,
                "started_at": started_at,
                "heartbeat_at": time.time(),
            },
        )
        time.sleep(WORKER_POLL_SECONDS)
    _atomic_json_write(
        record_path,
        {
            "worker": "g01-test-worker",
            "state": "stopped",
            "pid": os.getpid(),
            "token": token,
            "started_at": started_at,
            "stopped_at": time.time(),
        },
    )
    return 0


class CapabilityHost:
    """Host-owned, allowlisted actions for the G-01 device workflow."""

    TOOLS = frozenset(
        {
            "system.status",
            "workspace.write_readback",
            "test_worker.start",
            "test_worker.health",
            "test_worker.stop",
        }
    )

    def __init__(self, workspace: Path, *, health_url: Optional[str] = None):
        workspace = Path(workspace)
        workspace.mkdir(parents=True, exist_ok=True)
        self.workspace = workspace.resolve()
        if not self.workspace.is_dir():
            raise CapabilityError("workspace_not_directory")
        self.health_url = health_url
        self.record_path = self.workspace / ".g01-test-worker.json"
        self._worker_process: Optional[subprocess.Popen[Any]] = None
        self.lease = CapabilityLease.issue(
            self.TOOLS,
            max_calls={
                "system.status": 8,
                "workspace.write_readback": 8,
                "test_worker.start": 2,
                "test_worker.health": 16,
                "test_worker.stop": 2,
            },
        )

    def execute(self, tool: str, payload: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        self.lease.charge(tool)
        payload = payload or {}
        if not isinstance(payload, Mapping):
            raise CapabilityError("payload_must_be_object")
        if tool == "system.status":
            return self.system_status()
        if tool == "workspace.write_readback":
            return self.write_readback(payload)
        if tool == "test_worker.start":
            return self.start_worker()
        if tool == "test_worker.health":
            return self.worker_health()
        if tool == "test_worker.stop":
            return self.stop_worker()
        raise CapabilityError("capability_not_granted")

    def system_status(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "ok": True,
            "source": "g01-capability-host",
            "observed_at": time.time(),
            "pid": os.getpid(),
            "platform": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "workspace": str(self.workspace),
            "worker": self.worker_health(),
        }
        if self.health_url:
            result["local_model"] = self._local_health()
        return result

    def _local_health(self) -> Dict[str, Any]:
        parsed = urllib.parse.urlparse(self.health_url or "")
        if (
            parsed.scheme != "http"
            or parsed.hostname not in {"127.0.0.1", "::1", "localhost"}
            or parsed.path != "/health"
            or parsed.query
            or parsed.fragment
        ):
            return {"status": "rejected_url"}
        try:
            with urllib.request.urlopen(self.health_url, timeout=1.0) as response:
                body = json.loads(response.read(16 * 1024).decode("utf-8"))
            return {"status": "healthy", "response": body}
        except (OSError, ValueError, UnicodeError, urllib.error.URLError) as exc:
            return {"status": "unavailable", "error": type(exc).__name__}

    def _safe_target(self, relative_path: Any) -> Path:
        if not isinstance(relative_path, str) or not relative_path:
            raise CapabilityError("path_rejected")
        if relative_path == ".g01-test-worker.json":
            raise CapabilityError("reserved_path")
        if "\x00" in relative_path or "\\" in relative_path:
            raise CapabilityError("path_rejected")
        candidate = Path(relative_path)
        if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
            raise CapabilityError("path_rejected")
        current = self.workspace
        for part in candidate.parts:
            current = current / part
            if current.is_symlink():
                raise CapabilityError("symlink_path_rejected")
        target = (self.workspace / candidate).resolve(strict=False)
        if target != self.workspace and self.workspace not in target.parents:
            raise CapabilityError("path_boundary_violation")
        return target

    def write_readback(self, payload: Mapping[str, Any]) -> Dict[str, Any]:
        relative_path = payload.get("relative_path")
        content = payload.get("content")
        overwrite = payload.get("overwrite", False)
        if not isinstance(content, str) or not isinstance(overwrite, bool):
            raise CapabilityError("file_payload_rejected")
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_FILE_BYTES:
            raise CapabilityError("file_too_large")
        target = self._safe_target(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        # Re-check parents after mkdir: a pre-existing symlink is never followed.
        check = self.workspace
        for part in Path(relative_path).parts[:-1]:
            check = check / part
            if check.is_symlink():
                raise CapabilityError("symlink_path_rejected")
        if target.is_symlink():
            raise CapabilityError("symlink_path_rejected")
        try:
            if overwrite:
                fd, temporary = tempfile.mkstemp(prefix=".g01-write-", dir=str(target.parent))
                try:
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(encoded)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.replace(temporary, target)
                finally:
                    try:
                        os.unlink(temporary)
                    except FileNotFoundError:
                        pass
            else:
                with target.open("xb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
        except FileExistsError as exc:
            raise CapabilityError("overwrite_protection") from exc
        except OSError as exc:
            raise CapabilityError(f"file_write_failed:{type(exc).__name__}") from exc
        try:
            readback = target.read_bytes()
        except OSError as exc:
            raise CapabilityError(f"file_readback_failed:{type(exc).__name__}") from exc
        if readback != encoded:
            raise CapabilityError("file_readback_mismatch")
        return {
            "ok": True,
            "tool": "workspace.write_readback",
            "relative_path": relative_path,
            "bytes": len(encoded),
            "readback": True,
        }

    def _owned_record(self) -> Dict[str, Any]:
        record = _read_json(self.record_path)
        try:
            pid = int(record["pid"])
            token = str(record["token"])
        except (KeyError, TypeError, ValueError) as exc:
            raise CapabilityError("worker_record_invalid") from exc
        if record.get("worker") != "g01-test-worker" or not token or not _pid_alive(pid):
            raise CapabilityError("worker_not_owned")
        command = _process_command(pid)
        if "--worker-loop" not in command or token not in command:
            raise CapabilityError("worker_identity_mismatch")
        return record

    def start_worker(self) -> Dict[str, Any]:
        if self.record_path.exists():
            try:
                existing = self._owned_record()
            except CapabilityError:
                existing = None
            if existing:
                return {"ok": True, "tool": "test_worker.start", "state": "already_running", "pid": existing["pid"]}
        token = secrets.token_hex(16)
        command = [sys.executable, str(Path(__file__).resolve()), "--worker-loop", str(self.record_path), token]
        try:
            self._worker_process = subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
                close_fds=True,
            )
        except OSError as exc:
            raise CapabilityError(f"worker_start_failed:{type(exc).__name__}") from exc
        deadline = time.monotonic() + WORKER_START_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            try:
                record = _read_json(self.record_path)
                if record.get("state") == "running" and record.get("token") == token:
                    return {"ok": True, "tool": "test_worker.start", "state": "running", "pid": record["pid"]}
            except CapabilityError:
                pass
            time.sleep(WORKER_POLL_SECONDS)
        raise CapabilityError("worker_start_timeout")

    def worker_health(self) -> Dict[str, Any]:
        if not self.record_path.exists():
            return {"ok": True, "tool": "test_worker.health", "state": "absent", "pid_alive": False}
        record = _read_json(self.record_path)
        pid = record.get("pid")
        alive = isinstance(pid, int) and _pid_alive(pid)
        identity = False
        if alive and record.get("token"):
            command = _process_command(pid)
            identity = "--worker-loop" in command and str(record["token"]) in command
        heartbeat = record.get("heartbeat_at")
        fresh = isinstance(heartbeat, (int, float)) and time.time() - heartbeat < 2.0
        healthy = record.get("state") == "running" and alive and identity and fresh
        return {
            "ok": True,
            "tool": "test_worker.health",
            "state": "running" if healthy else record.get("state", "unknown"),
            "pid": pid,
            "pid_alive": alive,
            "owned": identity,
            "heartbeat_fresh": fresh,
            "healthy": healthy,
        }

    def stop_worker(self) -> Dict[str, Any]:
        record = self._owned_record()
        pid = int(record["pid"])
        try:
            os.kill(pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        deadline = time.monotonic() + WORKER_STOP_TIMEOUT_SECONDS
        while time.monotonic() < deadline and _pid_alive(pid):
            time.sleep(WORKER_POLL_SECONDS)
        if _pid_alive(pid):
            # Re-check ownership immediately before the stronger signal.
            command = _process_command(pid)
            if command != "<defunct>":
                self._owned_record()
                os.kill(pid, signal.SIGKILL)
        if self._worker_process is not None:
            try:
                self._worker_process.wait(timeout=WORKER_STOP_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                pass
            self._worker_process = None
        deadline = time.monotonic() + WORKER_STOP_TIMEOUT_SECONDS
        while time.monotonic() < deadline and _pid_alive(pid):
            time.sleep(WORKER_POLL_SECONDS)
        health = self.worker_health()
        if health.get("pid_alive"):
            raise CapabilityError("worker_stop_timeout")
        return {"ok": True, "tool": "test_worker.stop", "state": "stopped", "pid": pid, "health": health}


def _run_jsonl(workspace: Path, health_url: Optional[str]) -> int:
    host = CapabilityHost(workspace, health_url=health_url)
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            request = json.loads(line)
            if not isinstance(request, dict) or not isinstance(request.get("tool"), str):
                raise CapabilityError("request_rejected")
            result = host.execute(request["tool"], request.get("payload"))
            output = {"ok": True, "lease_id": host.lease.lease_id, "result": result}
        except (json.JSONDecodeError, CapabilityError, TypeError) as exc:
            output = {"ok": False, "error": str(exc)}
        print(json.dumps(output, ensure_ascii=False, sort_keys=True), flush=True)
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, default=Path.cwd() / "runtime" / "g01")
    parser.add_argument("--health-url", default=None)
    parser.add_argument("--worker-loop", nargs=2, metavar=("RECORD", "TOKEN"))
    args = parser.parse_args(argv)
    if args.worker_loop:
        return _worker_loop(Path(args.worker_loop[0]), args.worker_loop[1])
    return _run_jsonl(args.workspace, args.health_url)


if __name__ == "__main__":
    raise SystemExit(main())
