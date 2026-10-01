#!/usr/bin/env python3
"""Small browser UI for the local GOSIM Agent prototype.

It deliberately uses only the Python standard library and exposes the same
LocalAgent confirmation boundary as the JSONL and AppCard adapters.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from agent_app import LocalAgent, LocalModelRouter


HTML = r"""<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GOSIM 本地 Agent · 实测版</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#f4f6f8;color:#17202a;margin:0}
main{max-width:900px;margin:28px auto;padding:0 18px}.card{background:#fff;border-radius:14px;padding:20px;margin:14px 0;box-shadow:0 3px 14px #00000012}
h1{margin:0 0 6px;font-size:25px}.muted{color:#667085;font-size:13px}.row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
input,select,button{font:inherit;border:1px solid #cbd5e1;border-radius:8px;padding:9px 11px}input{flex:1;min-width:220px}button{cursor:pointer;background:#eef2ff}button.primary{background:#2563eb;color:#fff;border-color:#2563eb}button.ok{background:#15803d;color:#fff;border-color:#15803d}button.no{background:#fff1f2;color:#be123c;border-color:#fecdd3}
button:disabled{opacity:.45;cursor:not-allowed}.status{font-size:13px;padding:5px 9px;border-radius:99px;background:#ecfdf3;color:#047857}.status.bad{background:#fff7ed;color:#c2410c}
pre{background:#111827;color:#d1fae5;border-radius:9px;padding:13px;min-height:95px;white-space:pre-wrap;overflow:auto}.hint{font-size:13px;color:#475467}
</style></head><body><main>
<div class="card"><h1>GOSIM 本地 Agent · 实测版</h1>
<div class="muted">浏览器适配器｜本机 Qwen3-0.6B 路由｜文件与终端动作均需确认</div>
<p><span id="health" class="status">正在检查本地模型…</span> <span class="muted">工作区：</span><code id="workspace"></code></p></div>
<div class="card"><h2>1. 发送消息</h2><div class="row"><input id="message" value="请把这条测试记录保存到本地"><button class="primary" onclick="sendMessage()">发送</button></div><p class="hint">包含“保存/写入”的消息会生成待确认的本地文件任务。</p></div>
<div class="card"><h2>2. 请求受限终端动作</h2><div class="row"><select id="command"><option>mkdir</option><option>touch</option></select><input id="arg" value="test-folder"><button onclick="requestTerminal()">生成终端任务</button></div><p class="hint">当前只允许 mkdir / touch，固定在工作区执行，且必须人工确认。</p></div>
<div class="card"><h2>3. 审核与执行</h2><div class="row"><button id="approve" class="ok" disabled onclick="confirmTask(true)">确认执行</button><button id="reject" class="no" disabled onclick="confirmTask(false)">拒绝</button><button onclick="openWorkspace()">打开工作区</button></div></div>
<div class="card"><h2>事件结果</h2><pre id="output">等待输入…</pre></div>
<script>
const $=id=>document.getElementById(id);
function show(v){$('output').textContent=JSON.stringify(v,null,2);let p=v&&v.task_card;let active=!!(p&&p.requires_confirmation&&p.status==='proposed');$('approve').disabled=!active;$('reject').disabled=!active}
async function event(body){try{let r=await fetch('/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});show(await r.json())}catch(e){show({ok:false,error:String(e)})}}
function sendMessage(){event({type:'user_input',text:$('message').value})}
function requestTerminal(){event({type:'terminal_request',argv:[$('command').value,$('arg').value]})}
function confirmTask(approved){event({type:'confirm',approved})}
function openWorkspace(){event({type:'open_workspace'})}
async function health(){try{let v=await (await fetch('/health')).json();$('workspace').textContent=v.workspace;$('health').textContent=v.model?'本地 Qwen 已连接':'本地 Qwen 未连接';if(!v.model)$('health').classList.add('bad')}catch(e){$('health').textContent='服务不可用';$('health').classList.add('bad')}}
health();
</script></main></body></html>"""


class AppState:
    def __init__(self, workspace: Path, model_url: str | None):
        workspace.mkdir(parents=True, exist_ok=True)
        self.workspace = workspace.resolve()
        self.agent = LocalAgent(self.workspace, LocalModelRouter(model_url))
        self.lock = threading.Lock()


def model_alive(url: str | None) -> bool:
    if not url:
        return False
    try:
        import urllib.request

        with urllib.request.urlopen(url.replace("/v1/chat/completions", "/health"), timeout=1.5) as response:
            return response.status == 200
    except (OSError, ValueError):
        return False


class Handler(BaseHTTPRequestHandler):
    state: AppState

    def _send(self, status: int, data: Any, content_type: str = "application/json") -> None:
        raw = data.encode("utf-8") if isinstance(data, str) else json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            return self._send(200, HTML, "text/html")
        if path == "/health":
            return self._send(200, {"ok": True, "model": model_alive(self.state.agent.model_router.url), "workspace": str(self.state.workspace)})
        self._send(404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/event":
            return self._send(404, {"ok": False, "error": "not_found"})
        try:
            length = int(self.headers.get("Content-Length", "0"))
            event = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as exc:
            return self._send(400, {"ok": False, "error": "invalid_json", "detail": str(exc)})
        # This legacy browser prototype has no authentication. Its original
        # small task-card flow remains available, but it cannot approve Muse
        # goals, register watched folders, or change model/memory policy.
        if not isinstance(event, dict) or event.get("type") not in {
            "user_input", "terminal_request", "confirm", "open_workspace"
        }:
            return self._send(403, {"ok": False, "error": "legacy_event_not_allowed"})
        if event.get("type") == "open_workspace":
            if sys.platform != "darwin":
                return self._send(200, {"ok": False, "error": "open_workspace_unsupported", "workspace": str(self.state.workspace)})
            try:
                completed = subprocess.run(
                    ["/usr/bin/open", str(self.state.workspace)],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False,
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                return self._send(200, {"ok": False, "error": "open_workspace_failed", "detail": str(exc)})
            return self._send(200, {
                "ok": completed.returncode == 0,
                "workspace": str(self.state.workspace),
                "opened": completed.returncode == 0,
                "stderr": completed.stderr.strip(),
            })
        with self.state.lock:
            try:
                result = self.state.agent.handle(event)
            except (OSError, ValueError, TypeError) as exc:
                result = {"ok": False, "error": "agent_error", "detail": str(exc)}
        self._send(200, result)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    port = int(os.environ.get("LOCAL_APP_PORT", "8766"))
    workspace = Path(os.environ.get("LOCAL_APP_WORKSPACE", "runtime/user-demo"))
    model_url = os.environ.get("LOCAL_MODEL_URL", "http://127.0.0.1:8080/v1/chat/completions")
    state = AppState(workspace, model_url)
    Handler.state = state
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"GOSIM local app: http://127.0.0.1:{port}", flush=True)
    print(f"workspace: {state.workspace}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
