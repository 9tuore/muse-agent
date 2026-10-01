#!/usr/bin/env python3
"""Probe official Octos with an owned, larger-context local Qwen server."""

import json
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SHARED_ROOT = Path("/Users/mima0000/Documents/ChatGPT/Agent APP黑客松")
SERVER = SHARED_ROOT / "runtime/llama-b11178/llama-server"
MODEL = SHARED_ROOT / "runtime/models/Qwen3-0.6B-Q8_0.gguf"
EVIDENCE_NAME = "muse-g01-official-isolated-qwen-32768-20260928.json"


def main() -> int:
    if not SERVER.is_file() or not MODEL.is_file():
        print("isolated_qwen_binary_or_model_missing", file=sys.stderr)
        return 2
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    base_url = f"http://127.0.0.1:{port}/v1"
    with tempfile.TemporaryDirectory(prefix="g01-isolated-qwen-", dir="/tmp") as temp:
        log_path = Path(temp) / "server.log"
        command = [str(SERVER), "-m", str(MODEL), "--host", "127.0.0.1",
                   "--port", str(port), "--ctx-size", "32768", "--parallel", "1",
                   "--reasoning", "off", "--alias", "qwen3-0.6b"]
        with log_path.open("w", encoding="utf-8") as log:
            server = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT,
                                      start_new_session=True)
            try:
                deadline = time.monotonic() + 120
                while time.monotonic() < deadline:
                    if server.poll() is not None:
                        raise RuntimeError(f"isolated_qwen_exited:{server.returncode}")
                    try:
                        with urllib.request.urlopen(base_url + "/models", timeout=2) as response:
                            if response.status == 200:
                                break
                    except (OSError, urllib.error.URLError):
                        time.sleep(1)
                else:
                    raise RuntimeError("isolated_qwen_start_timeout")
                environment = dict(os.environ, G01_QWEN_BASE_URL=base_url,
                                   G01_EVIDENCE_NAME=EVIDENCE_NAME)
                result = subprocess.run([sys.executable, str(ROOT / "scripts/probe_g01_octos_main_qwen.py")],
                                        cwd=ROOT, env=environment, timeout=180, check=False)
                evidence_path = ROOT / "evidence" / EVIDENCE_NAME
                if evidence_path.exists():
                    report = json.loads(evidence_path.read_text(encoding="utf-8"))
                    report["isolated_qwen"] = {"context_tokens": 32768, "port": port,
                                                "server_exit_before_cleanup": server.poll(),
                                                "log_tail": log_path.read_text(encoding="utf-8")[-3000:]}
                    evidence_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                                             encoding="utf-8")
                return result.returncode
            except (RuntimeError, subprocess.TimeoutExpired) as exc:
                print(str(exc), file=sys.stderr)
                print(log_path.read_text(encoding="utf-8")[-3000:], file=sys.stderr)
                return 1
            finally:
                os.killpg(server.pid, signal.SIGTERM)
                try:
                    server.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(server.pid, signal.SIGKILL)
                    server.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
