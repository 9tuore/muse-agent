#!/usr/bin/env python3
"""Exercise a fresh signed package with loopback-only provider fixtures."""

import json
import os
import subprocess
import sys
import tempfile
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock


RUN = Path(sys.argv[1]).resolve()
RESOURCES = RUN / "GOSIM-Local-Agent.app/Contents/Resources"
if not RESOURCES.is_dir():
    raise SystemExit("fresh_package_resources_missing")
sys.path.insert(0, str(RESOURCES))

import muse_models  # noqa: E402
import muse_provider_protocols  # noqa: E402


if Path(muse_models.__file__).resolve().parent != RESOURCES:
    raise SystemExit("model_module_not_loaded_from_package")


class Fixture(BaseHTTPRequestHandler):
    calls = []

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.calls.append({"path": self.path, "auth": self.headers.get("Authorization"),
                           "model": body.get("model"), "protocol_keys": sorted(body)})
        if self.path.startswith("/fail"):
            self.send_response(int(self.path.removeprefix("/fail")))
            self.end_headers()
            return
        if self.path == "/v1/responses":
            response = {"status": "completed", "model": body["model"],
                        "output": [{"type": "message", "content": [{
                            "type": "output_text", "text": "high-only loopback fixture"}]}],
                        "usage": {"input_tokens": 9, "output_tokens": 5}}
        else:
            response = {"model": body["model"], "choices": [{"message": {
                "content": "fixture"}}], "usage": {"prompt_tokens": 9, "completion_tokens": 5}}
        encoded = json.dumps(response).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, *_args):
        pass


def set_high(gateway, endpoint, *, protocol="openai_responses", model="gpt-6-astra",
             key_ref=False, remote_calls=0, daily_tokens=20000):
    settings = gateway.get_settings()
    settings["mode"] = "high"
    settings["profiles"]["local-default"]["endpoint"] = ""
    high = settings["profiles"]["high-default"]
    high.update(endpoint=endpoint, protocol=protocol, model=model,
                keychain_service=("org.gosim.local-agent.model.high-default" if key_ref else ""),
                keychain_account=("high-default" if key_ref else ""))
    settings["cloud_data_allowed"] = True
    settings["allow_unknown_cost"] = True
    settings["daily_remote_call_limit"] = remote_calls
    settings["daily_token_limit"] = daily_tokens
    gateway.update_settings(settings)


def expect_error(gateway, expected):
    outcome = gateway.generate("fixture only", purpose="chat", max_tokens=8)
    if outcome.get("error") != expected or outcome.get("ok") is not False:
        raise AssertionError((expected, outcome))
    return {"status": outcome["status"], "error": outcome["error"]}


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Fixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    endpoint = f"http://127.0.0.1:{server.server_port}/v1/responses"
    workspaces = Path(tempfile.mkdtemp(prefix="probe-workspaces-", dir=RUN))
    report = {"fresh_app": str(RUN / "GOSIM-Local-Agent.app"),
              "resource_python": sys.executable,
              "module_paths": {name: str(Path(module.__file__).resolve()) for name, module in
                               (("muse_models", muse_models),
                                ("muse_provider_protocols", muse_provider_protocols))},
              "cases": {}}
    try:
        # First boot of the bundled worker with no configured local model or key.
        worker_space = workspaces / "high-only-worker"
        gateway = muse_models.ModelGateway(worker_space)
        set_high(gateway, endpoint)
        env = os.environ.copy()
        env.update(HOME=str(RUN / "home"), GOSIM_LOCAL_INBOX="0",
                   LOCAL_MODEL_URL="", PYTHONDONTWRITEBYTECODE="1",
                   PYTHONNOUSERSITE="1", PYTHONPATH=str(RESOURCES))
        (RUN / "home").mkdir(exist_ok=True)
        worker = subprocess.run(
            [sys.executable, "-B", str(RESOURCES / "desktop_worker.py"), str(worker_space)],
            input='{"type":"health"}\n{"type":"chat_message","text":"hello"}\n',
            capture_output=True, text=True, timeout=30, env=env, cwd=RUN)
        frames = [json.loads(line) for line in worker.stdout.splitlines() if line.strip()]
        health = next((frame for frame in frames if frame.get("agent") == "local-agent"), None)
        chat = next((frame for frame in frames if frame.get("status") in
                     {"REPLIED", "MODEL_UNAVAILABLE"}), None)
        if (worker.returncode or health is None or health.get("muse_model_mode") != "high"
                or chat is None or chat.get("status") != "REPLIED"
                or chat.get("model", {}).get("provider") != "high-default"
                or chat.get("model", {}).get("route") != "high"
                or len(Fixture.calls) != 1 or Fixture.calls[0]["auth"] is not None):
            raise AssertionError({"worker_exit": worker.returncode, "frames": frames,
                                  "fixture_calls": Fixture.calls, "stderr": worker.stderr[-500:]})
        report["cases"]["high_only_worker_cold_boot"] = {
            "status": "PASS", "worker_exit": worker.returncode,
            "health_mode": health["muse_model_mode"], "chat_status": chat["status"],
            "chat_reply": chat["chat_reply"],
            "route": chat["model"]["route"], "provider": chat["model"]["provider"],
            "loopback_calls": len(Fixture.calls), "authorization_header": None,
            "local_endpoint": gateway.get_settings()["profiles"]["local-default"]["endpoint"]}

        # A stale remote Keychain binding cannot leak to a loopback endpoint.
        loop = muse_models.ModelGateway(workspaces / "loopback-secret")
        set_high(loop, endpoint, key_ref=True)
        loop.key_bindings_path.write_text('{"high-default":"https://former.invalid:443"}')
        with mock.patch.object(loop, "_keychain_password", side_effect=AssertionError(
                "loopback_must_not_read_keychain")):
            local_result = loop.generate("hello", purpose="chat", max_tokens=8)
        if not local_result.get("ok") or Fixture.calls[-1]["auth"] is not None:
            raise AssertionError(local_result)
        report["cases"]["loopback_secret_guard"] = {
            "status": "PASS", "route": local_result["route"],
            "authorization_header": None, "keychain_lookup": "NOT_CALLED"}

        # Remote endpoints are syntactically valid but never contacted. A
        # sentinel rejects any attempt to open a network connection.
        remote = muse_models.ModelGateway(workspaces / "remote-denials")
        remote_endpoint = "https://provider.invalid/v1/responses"
        set_high(remote, remote_endpoint, key_ref=True, remote_calls=0)
        remote_calls_before = len(Fixture.calls)
        with mock.patch.object(urllib.request, "build_opener", side_effect=AssertionError(
                "remote_network_must_not_open")) as opener:
            report["cases"]["budget_zero"] = expect_error(remote, "remote_call_budget_exhausted")
            set_high(remote, remote_endpoint, key_ref=True, remote_calls=1)
            report["cases"]["unknown_price"] = expect_error(remote, "cost_unknown")
            origin = remote._origin(remote_endpoint)
            remote.configure_pricing(
                profile_id="high-default", model="gpt-6-astra", origin=origin,
                input_cny_per_million="10", output_cny_per_million="20",
                source="synthetic fixture price", confirmed=True)
            remote.key_bindings_path.write_text(
                '{"high-default":"https://different.invalid:443"}')
            report["cases"]["origin_mismatch"] = expect_error(remote, "keychain_origin_mismatch")
            remote.key_bindings_path.write_text(json.dumps({"high-default": origin}))
            with mock.patch.object(remote, "_keychain_password", return_value=None):
                report["cases"]["no_key"] = expect_error(remote, "keychain_secret_unavailable")
            set_high(remote, remote_endpoint, key_ref=True, remote_calls=1, daily_tokens=1)
            with mock.patch.object(remote, "_keychain_password", return_value="synthetic-only"):
                report["cases"]["token_over_limit"] = expect_error(remote, "model_budget_exhausted")
            set_high(remote, remote_endpoint, key_ref=True, remote_calls=1)
            remote.configure_pricing(
                profile_id="high-default", model="gpt-6-astra", origin=origin,
                input_cny_per_million="100000", output_cny_per_million="100000",
                source="synthetic high fixture price", confirmed=True)
            with mock.patch.object(remote, "_keychain_password", return_value="synthetic-only"):
                report["cases"]["money_over_limit"] = expect_error(
                    remote, "model_money_budget_exhausted")
            if opener.call_count or len(Fixture.calls) != remote_calls_before:
                raise AssertionError("remote_guard_contacted_network")
        report["remote_network_opener_calls"] = 0

        errors = muse_models.ModelGateway(workspaces / "provider-errors")
        for code, expected in ((401, "provider_auth_failed"),
                               (429, "provider_rate_limited"),
                               (503, "provider_overloaded")):
            set_high(errors, f"http://127.0.0.1:{server.server_port}/fail{code}")
            report["cases"][f"http_{code}"] = expect_error(errors, expected)
        report["loopback_request_count"] = len(Fixture.calls)
        report["loopback_requests"] = [
            {"path": call["path"], "model": call["model"],
             "authorization_header_present": call["auth"] is not None,
             "protocol_keys": call["protocol_keys"]} for call in Fixture.calls]
        report["status"] = "PASS"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
    output = Path(__file__).resolve().parent.parent / "evidence/muse-g01-candidate16-provider-20260928.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"output": str(output), "status": report["status"],
                      "cases": list(report["cases"]),
                      "loopback_request_count": report["loopback_request_count"]}))


if __name__ == "__main__":
    main()
