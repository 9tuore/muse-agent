"""Isolated Edge browser research through Chrome DevTools Protocol.

The session owns only its fresh profile.  Public page text is returned as
untrusted source material, never interpreted as instructions or tool calls.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import plistlib
import shutil
import socket
import struct
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit
from urllib.request import urlopen

from muse_capabilities import _public_address, _public_url


EDGE_BUNDLE_ID = "com.microsoft.edgemac"
MAX_PAGE_TEXT = 12_000
MAX_RESULTS = 10
MAX_FRAME = 1_048_576


class BrowserError(ValueError):
    pass


def discover_edge_binary() -> tuple[Path, str]:
    """Resolve the installed Edge bundle by macOS bundle ID, not project path."""
    script = ('ObjC.import("AppKit"); var u=$.NSWorkspace.sharedWorkspace.'
              'URLForApplicationWithBundleIdentifier("com.microsoft.edgemac"); '
              'u ? ObjC.unwrap(u.path) : ""')
    result = subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", "-e", script],
                            capture_output=True, text=True, timeout=5, check=False)
    bundle = Path(result.stdout.strip()) if result.returncode == 0 and result.stdout.strip() else None
    if bundle is None or bundle.suffix != ".app" or not bundle.is_dir():
        raise BrowserError("BLOCKED_BROWSER_UNAVAILABLE")
    info_path = bundle / "Contents" / "Info.plist"
    try:
        with info_path.open("rb") as stream:
            info = plistlib.load(stream)
        executable = info["CFBundleExecutable"]
        version = info["CFBundleShortVersionString"]
    except (OSError, KeyError, ValueError, TypeError):
        raise BrowserError("BLOCKED_BROWSER_UNAVAILABLE") from None
    if (info.get("CFBundleIdentifier") != EDGE_BUNDLE_ID or not isinstance(executable, str)
            or "/" in executable or not isinstance(version, str) or not version):
        raise BrowserError("BLOCKED_BROWSER_UNAVAILABLE")
    binary = bundle / "Contents" / "MacOS" / executable
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise BrowserError("BLOCKED_BROWSER_UNAVAILABLE")
    return binary, version


class _CDP:
    def __init__(self, ws_url: str, port: int, allowed_domains: list[str] | None = None):
        parsed = urlsplit(ws_url)
        if parsed.scheme != "ws" or parsed.hostname not in {"127.0.0.1", "localhost"} or parsed.port != port:
            raise BrowserError("untrusted_debugger_endpoint")
        self.sock = socket.create_connection(("127.0.0.1", port), timeout=8)
        self.sock.settimeout(1)
        self.next_id = 0
        self.dns_checked: set[str] = set()
        self.allowed_domains = allowed_domains
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (f"GET {parsed.path} HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
                   f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
                   f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
        self.sock.sendall(request.encode("ascii"))
        header = bytearray()
        while b"\r\n\r\n" not in header and len(header) < 8192:
            header.extend(self.sock.recv(1024))
        expected = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode("ascii")).digest())
        if not header.startswith(b"HTTP/1.1 101") or expected not in header:
            status = header.split(b"\r\n", 1)[0].decode("ascii", errors="replace")[:100]
            self.sock.close()
            raise BrowserError("debugger_websocket_rejected:" + status)
        self.pending = bytes(header.split(b"\r\n\r\n", 1)[1])

    def close(self):
        self.sock.close()

    def _recv_exact(self, size: int) -> bytes:
        out = bytearray()
        if self.pending:
            take = self.pending[:size]
            out.extend(take)
            self.pending = self.pending[len(take):]
        while len(out) < size:
            chunk = self.sock.recv(size - len(out))
            if not chunk:
                raise BrowserError("debugger_closed")
            out.extend(chunk)
        return bytes(out)

    def _send(self, payload: dict):
        encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        if len(encoded) > 65_535:
            raise BrowserError("cdp_command_too_large")
        header = bytearray([0x81])
        if len(encoded) < 126:
            header.append(0x80 | len(encoded))
        else:
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", len(encoded)))
        mask = os.urandom(4)
        self.sock.sendall(bytes(header) + mask + bytes(value ^ mask[index % 4]
                                                      for index, value in enumerate(encoded)))

    def _message(self) -> dict:
        while True:
            first, second = self._recv_exact(2)
            opcode = first & 0x0F
            size = second & 0x7F
            if size == 126:
                size = struct.unpack("!H", self._recv_exact(2))[0]
            elif size == 127:
                size = struct.unpack("!Q", self._recv_exact(8))[0]
            if size > MAX_FRAME or second & 0x80:
                raise BrowserError("invalid_cdp_frame")
            data = self._recv_exact(size)
            if opcode == 8:
                raise BrowserError("debugger_closed")
            if opcode == 9:
                self._send_pong(data)
                continue
            if opcode != 1:
                continue
            value = json.loads(data)
            if isinstance(value, dict):
                return value

    def _send_pong(self, data: bytes):
        mask = os.urandom(4)
        self.sock.sendall(bytes([0x8A, 0x80 | len(data)]) + mask +
                          bytes(value ^ mask[index % 4] for index, value in enumerate(data)))

    def _filter_request(self, event: dict):
        params = event.get("params", {})
        request_id = params.get("requestId")
        raw = params.get("request", {}).get("url", "")
        try:
            _, host, _ = _public_url(raw, self.allowed_domains)
            if host not in self.dns_checked:
                _public_address(host)
                self.dns_checked.add(host)
        except (ValueError, OSError, TimeoutError):
            self.next_id += 1
            self._send({"id": self.next_id, "method": "Fetch.failRequest",
                        "params": {"requestId": request_id, "errorReason": "BlockedByClient"}})
        else:
            self.next_id += 1
            self._send({"id": self.next_id, "method": "Fetch.continueRequest",
                        "params": {"requestId": request_id}})

    def call(self, method: str, params: dict | None = None, timeout: float = 20) -> dict:
        self.next_id += 1
        command_id = self.next_id
        self._send({"id": command_id, "method": method, "params": params or {}})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                message = self._message()
            except socket.timeout:
                continue
            if message.get("method") == "Fetch.requestPaused":
                self._filter_request(message)
            elif message.get("id") == command_id:
                if "error" in message:
                    raise BrowserError("cdp_error:" + str(message["error"].get("message", "unknown"))[:160])
                return message.get("result", {})
        raise BrowserError("cdp_timeout:" + method)


class IsolatedEdgeSession:
    """One public-web research tab in a new profile; close owns its process."""

    def __init__(self, workspace: Path, edge_binary: Path | None = None,
                 allowed_domains: list[str] | None = None):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        if edge_binary is None:
            edge_binary, self.browser_version = discover_edge_binary()
        else:
            self.browser_version = "test-injected"
        if not Path(edge_binary).is_file():
            raise BrowserError("BLOCKED_BROWSER_UNAVAILABLE")
        self.profile = Path(tempfile.mkdtemp(prefix="muse-edge-research-", dir=self.workspace))
        self.process: subprocess.Popen | None = None
        self.cdp: _CDP | None = None
        self.port: int | None = None
        self.result_selector: str | None = None
        self.allowed_domains = allowed_domains
        self.edge_binary = Path(edge_binary)

    def start(self):
        if self.process is not None:
            raise BrowserError("session_already_started")
        self.process = subprocess.Popen([
            str(self.edge_binary), f"--user-data-dir={self.profile}", "--remote-debugging-port=0",
            "--no-first-run", "--no-default-browser-check", "--new-window", "about:blank",
        ], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active = self.profile / "DevToolsActivePort"
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                raise BrowserError("isolated_edge_exited")
            if active.is_file() and not active.is_symlink():
                lines = active.read_text(encoding="ascii").splitlines()
                if lines and lines[0].isdigit():
                    self.port = int(lines[0])
                    break
            time.sleep(0.1)
        if self.port is None:
            raise BrowserError("edge_debugger_not_ready")
        with urlopen(f"http://127.0.0.1:{self.port}/json", timeout=5) as response:
            tabs = json.load(response)
        pages = [item for item in tabs if item.get("type") == "page" and item.get("url") == "about:blank"]
        if len(pages) != 1:
            raise BrowserError("isolated_tab_missing_or_ambiguous")
        self.cdp = _CDP(pages[0]["webSocketDebuggerUrl"], self.port, self.allowed_domains)
        self.cdp.call("Page.enable")
        self.cdp.call("Runtime.enable")
        self.cdp.call("Fetch.enable", {"patterns": [{"urlPattern": "*", "requestStage": "Request"}]})
        return {"status": "READY", "browser": "Microsoft Edge", "browser_version": self.browser_version,
                "profile": str(self.profile),
                "pid": self.process.pid}

    def close(self):
        if self.cdp:
            try:
                self.cdp.call("Browser.close", timeout=5)
            except (BrowserError, OSError, socket.timeout):
                pass
            self.cdp.close()
            self.cdp = None
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.process = None
        if self.profile.is_dir() and self.profile.parent == self.workspace:
            shutil.rmtree(self.profile)

    def __enter__(self):
        try:
            self.start()
        except Exception:
            self.close()
            raise
        return self

    def __exit__(self, *_):
        self.close()

    def _evaluate(self, expression: str):
        if not self.cdp:
            raise BrowserError("browser_not_started")
        result = self.cdp.call("Runtime.evaluate", {"expression": expression, "returnByValue": True,
                                                     "awaitPromise": True}, timeout=20)
        if "exceptionDetails" in result:
            raise BrowserError("page_evaluation_failed")
        return result.get("result", {}).get("value")

    def _loaded(self):
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            if self._evaluate("document.readyState") in {"interactive", "complete"} and self._evaluate("!!document.body"):
                return
            time.sleep(0.2)
        raise BrowserError("page_load_timeout")

    def navigate(self, raw_url: str) -> dict:
        if not self.cdp:
            raise BrowserError("browser_not_started")
        url, host, _ = _public_url(raw_url, self.allowed_domains)
        _public_address(host)
        self.cdp.call("Page.navigate", {"url": url})
        self._loaded()
        return self.read_current()

    def read_current(self) -> dict:
        value = self._evaluate("JSON.stringify({url:location.href,title:document.title,"
                               "text:(document.body&&document.body.innerText||'').slice(0,12000)})")
        page = json.loads(value)
        url, _, _ = _public_url(page["url"], self.allowed_domains)
        body = str(page.get("text", ""))[:MAX_PAGE_TEXT]
        when = datetime.now(timezone.utc).isoformat()
        return {"source_url": url, "title": str(page.get("title", ""))[:240], "text": body,
                "retrieved_at": when, "content_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
                "browser": "Microsoft Edge", "untrusted_source": True}

    def _page_targets(self) -> list[dict]:
        if self.port is None:
            raise BrowserError("browser_not_started")
        with urlopen(f"http://127.0.0.1:{self.port}/json", timeout=5) as response:
            return [item for item in json.load(response) if item.get("type") == "page"]

    def search(self, query: str, *, engine: str = "bing") -> dict:
        if not isinstance(query, str) or not 2 <= len(query.strip()) <= 160:
            raise BrowserError("query_invalid")
        sources = {
            "bing": ("https://cn.bing.com/search?q=", "li.b_algo h2 a[href]"),
            "python.org": ("https://www.python.org/search/?q=", "ul.list-recent-events.menu li h3 a[href]"),
            "wikipedia": ("https://en.wikipedia.org/w/index.php?title=Special:Search&search=",
                          "li.mw-search-result .mw-search-result-heading a[href]"),
        }
        if engine not in sources:
            raise BrowserError("search_engine_not_reviewed")
        prefix, self.result_selector = sources[engine]
        page = self.navigate(prefix + quote(query.strip()))
        return self._extract_search_results(query, engine, page)

    def read_search_results(self, query: str, *, engine: str = "python.org") -> dict:
        """Read an already navigated search page, including one reached by a learned form."""
        if engine != "python.org" or not isinstance(query, str) or not 2 <= len(query.strip()) <= 160:
            raise BrowserError("search_engine_not_reviewed")
        self.result_selector = "ul.list-recent-events.menu li h3 a[href]"
        page = self.read_current()
        parsed = urlsplit(page["source_url"])
        from urllib.parse import parse_qs
        if (parsed.hostname != "www.python.org" or parsed.path != "/search/" or
                parse_qs(parsed.query).get("q") != [query]):
            raise BrowserError("search_page_changed")
        return self._extract_search_results(query, engine, page)

    def _extract_search_results(self, query: str, engine: str, page: dict) -> dict:
        selector = json.dumps(self.result_selector)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            visible = self._evaluate("(()=>{let a=document.querySelector(" + selector + ");"
                                     "return !!(a&&a.innerText&&a.getBoundingClientRect().height>0)})()")
            if visible:
                break
            time.sleep(0.25)
        value = self._evaluate("JSON.stringify(Array.from(document.querySelectorAll(" + selector + "))"
                               ".slice(0,10).map(a=>({title:(a.innerText||'').slice(0,240),url:a.href,"
                               "snippet:(a.closest('li')?.innerText||'').slice(0,500)})))")
        candidates = json.loads(value)
        results = []
        for index, item in enumerate(candidates):
            try:
                url, host, _ = _public_url(item.get("url"), self.allowed_domains)
                _public_address(host)
            except (ValueError, OSError, TimeoutError):
                continue
            results.append({"title": str(item.get("title", ""))[:240], "url": url,
                            "snippet": str(item.get("snippet", ""))[:500],
                            "result_index": index})
        return {"query": query, "engine": engine, "search_page": page["source_url"], "retrieved_at": page["retrieved_at"],
                "results": results[:MAX_RESULTS], "browser": "Microsoft Edge"}

    def click_result(self, index: int, expected_url: str) -> dict:
        if not isinstance(index, int) or not 0 <= index < MAX_RESULTS or not self.result_selector:
            raise BrowserError("result_index_invalid")
        expected_url, host, _ = _public_url(expected_url, self.allowed_domains)
        _public_address(host)
        selector = json.dumps(self.result_selector)
        expression = ("(()=>{let a=Array.from(document.querySelectorAll(" + selector + "))["
                      + str(index) + "];if(!a)return null;a.target='_self';a.scrollIntoView();"
                      "let r=a.getBoundingClientRect();return {url:a.href,x:r.x+r.width/2,y:r.y+r.height/2," 
                      "width:r.width,height:r.height};})()")
        target = self._evaluate("JSON.stringify(" + expression + ")")
        rect = json.loads(target) if target else None
        if not rect or _public_url(rect.get("url"), self.allowed_domains)[0] != expected_url or rect["width"] < 1 or rect["height"] < 1:
            raise BrowserError("result_changed_or_not_visible")
        x, y = float(rect["x"]), float(rect["y"])
        if not 0 <= x <= 5000 or not 0 <= y <= 5000:
            raise BrowserError("result_outside_viewport")
        assert self.cdp is not None
        previous = self._evaluate("location.href")
        self.cdp.call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y,
                                                    "button": "left", "clickCount": 1})
        self.cdp.call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y,
                                                    "button": "left", "clickCount": 1})
        deadline = time.monotonic() + 3
        changed = False
        while time.monotonic() < deadline:
            if self._evaluate("location.href") != previous:
                changed = True
                break
            time.sleep(0.2)
        transport = "cdp_mouse"
        if not changed:
            transport = "dom_click_fallback"
            self._evaluate("(()=>{let a=Array.from(document.querySelectorAll(" + selector + "))"
                           ".find(a=>a.href===" + json.dumps(expected_url) + ");"
                           "if(!a)return false;a.target='_self';a.click();return true})()")
            deadline = time.monotonic() + 7
            while time.monotonic() < deadline:
                if self._evaluate("location.href") != previous:
                    changed = True
                    break
                time.sleep(0.2)
        if not changed:
            targets = self._page_targets()
            observed = [str(item.get("url", ""))[:160] for item in targets]
            raise BrowserError("click_did_not_navigate:targets=" + repr(observed))
        self._loaded()
        page = self.read_current()
        if urlsplit(page["source_url"]).hostname != host:
            raise BrowserError("click_landed_on_unexpected_host:" + str(urlsplit(page["source_url"]).hostname))
        page["clicked_result_index"] = index
        page["expected_url"] = expected_url
        page["click_transport"] = transport
        return page
