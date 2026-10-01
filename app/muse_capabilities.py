"""Bounded, host-approved capabilities for Muse goals.

Model output is only a proposed call. The caller supplies ``approved`` from a
separate host approval record; no field in ``call`` can grant authority.
"""

from __future__ import annotations

import hashlib
import html.parser
import http.client
import ipaddress
import json
import os
import re
import socket
import sqlite3
import ssl
import subprocess
import zlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urlsplit, urlunsplit


MAX_ARTIFACT_BYTES = 64 * 1024
MAX_WEB_BYTES = 128 * 1024
MAX_WEB_READ_BYTES = 512 * 1024
MAX_WEB_DECODED_BYTES = 512 * 1024
MAX_WEB_TEXT = 12 * 1024
BUILTIN_SCOPE = {"project": "gosim-muse", "account": "local", "visibility": "personal"}
BUILTIN_CATALOG = {
    "web.read": ("builtin.web.read.v1", "read", ["network.public_https"], 12),
    "web.search": ("builtin.web.search.v1", "read", ["network.public_https"], 12),
    "browser.research": ("builtin.browser.research.v1", "read", ["browser.isolated_profile", "network.public_https"], 120),
    "workspace.write_artifact": ("builtin.workspace.write_artifact.v1", "local_write", ["workspace.selected_path"], 10),
    "system.frontmost_app": ("builtin.system.frontmost_app.v1", "read", ["app.selected_bundle"], 3),
    "system.app_health": ("builtin.system.app_health.v1", "read", ["app.selected_bundle"], 3),
    "app.recipe": ("builtin.app.recipe.v1", "local_write", ["app.accessibility", "workspace.selected_path"], 30),
}


def builtin_capability_documents(scope: Optional[dict] = None) -> list[dict]:
    """Reviewed host declarations. Staging these is distinct from Goal approval."""
    selected_scope = dict(scope or BUILTIN_SCOPE)
    when = "2026-09-28T00:00:00+00:00"
    return [{
        "schema_version": "muse.dsl/1", "kind": "capability", "id": capability_id,
        "revision": 1, "scope": selected_scope, "created_at": when, "updated_at": when,
        "origin": {"type": "local_runtime", "ref": "muse-reviewed-catalog"},
        "payload": {"capability_id": capability_id, "version": "1.0.0", "input_schema": {"type": "object"},
                    "output_schema": {"type": "object"},
                    "target_app": ("com.microsoft.edgemac" if capability_id == "browser.research" else
                                   "com.apple.TextEdit" if capability_id == "app.recipe" else None),
                    "required_permissions": permissions, "risk": risk,
                    "preconditions": ["host_goal_revision_approved"], "adapter": adapter,
                    "verification": {"kind": "independent_readback" if risk == "local_write" else "source_receipt"},
                    "timeout_seconds": timeout, "idempotent": True,
                    "compensation": None},
    } for capability_id, (adapter, risk, permissions, timeout) in BUILTIN_CATALOG.items()]


def register_builtin_catalog(catalog: Any, scope: Optional[dict] = None) -> list[dict]:
    """Host startup hook for pinned built-ins; it does not approve any Goal."""
    documents = builtin_capability_documents(scope)
    trusted = frozenset(item["payload"]["adapter"] for item in documents)
    registered = []
    for document in documents:
        current = catalog.get(document["id"], document["scope"])
        if current is not None:
            if current["document"] != document:
                catalog.stage(document)
                current = catalog.get(document["id"], document["scope"])
            registered.append(current)
            continue
        entry = catalog.stage(document)
        if not catalog.approve(document["id"], document["revision"], entry["digest"],
                               document["scope"], trusted_adapters=trusted):
            raise ValueError("builtin_catalog_approval_failed")
        registered.append(catalog.get(document["id"], document["scope"]))
    return registered


class _PageText(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts = []  # type: list[str]
        self.title = []  # type: list[str]
        self._skip = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: Any) -> None:
        if tag in {"script", "style", "nav", "footer"}:
            self._skip += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav", "footer"} and self._skip:
            self._skip -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value and not self._skip:
            self.parts.append(value)
            if self._in_title:
                self.title.append(value)


class _PinnedHTTPS(http.client.HTTPSConnection):
    """Connect to a checked public IP while retaining TLS hostname checks."""

    def __init__(self, host: str, address: str) -> None:
        super().__init__(host, port=443, timeout=8, context=ssl.create_default_context())
        self.address = address

    def connect(self) -> None:
        raw = socket.create_connection((self.address, 443), self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except Exception:
            raw.close()
            raise


def _decode_web_body(raw: bytes, content_encoding: str) -> bytes:
    encoding = content_encoding.strip().lower()
    if encoding in {"", "identity"}:
        if raw.startswith(b"\x1f\x8b"):
            raise ValueError("compressed_body_without_content_encoding")
        return raw
    if encoding not in {"gzip", "deflate"}:
        raise ValueError("unsupported_content_encoding")
    formats = (zlib.MAX_WBITS + 16,) if encoding == "gzip" else (zlib.MAX_WBITS, -zlib.MAX_WBITS)
    for index, wbits in enumerate(formats):
        try:
            decoder = zlib.decompressobj(wbits)
            body = decoder.decompress(raw, MAX_WEB_DECODED_BYTES + 1)
            if len(body) > MAX_WEB_DECODED_BYTES or decoder.unconsumed_tail:
                raise ValueError("decoded_page_too_large")
            if not decoder.eof or decoder.unused_data:
                raise ValueError("compressed_page_incomplete_or_trailing_data")
            body += decoder.flush(MAX_WEB_DECODED_BYTES - len(body) + 1)
            if len(body) > MAX_WEB_DECODED_BYTES:
                raise ValueError("decoded_page_too_large")
            return body
        except zlib.error:
            if index == len(formats) - 1:
                raise ValueError("compressed_page_invalid") from None
    raise ValueError("compressed_page_invalid")


def _public_url(raw: Any, allowed_domains: Any = None) -> tuple[str, str, str]:
    if not isinstance(raw, str) or len(raw) > 2048:
        raise ValueError("url_rejected")
    parsed = urlsplit(raw)
    host = (parsed.hostname or "").lower().rstrip(".")
    if (parsed.scheme != "https" or not host or parsed.username or parsed.password
            or parsed.port not in (None, 443) or parsed.fragment):
        raise ValueError("public_https_required")
    if host == "localhost" or host.endswith((".localhost", ".local", ".internal")):
        raise ValueError("private_host_rejected")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("ip_literal_rejected")
    if allowed_domains is not None:
        if not isinstance(allowed_domains, list) or not allowed_domains:
            raise ValueError("allowed_domains_invalid")
        allowed = [str(value).lower().rstrip(".") for value in allowed_domains]
        if any(not re.fullmatch(r"[a-z0-9][a-z0-9.-]{0,252}[a-z0-9]", value) for value in allowed):
            raise ValueError("allowed_domains_invalid")
        if not any(host == domain or host.endswith("." + domain) for domain in allowed):
            raise ValueError("domain_not_approved")
    path = parsed.path or "/"
    return urlunsplit(("https", host, path, parsed.query, "")), host, path + ("?" + parsed.query if parsed.query else "")


def _public_address(host: str) -> str:
    addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
    if not addresses or any(not ipaddress.ip_address(value).is_global for value in addresses):
        raise ValueError("non_public_address_rejected")
    return sorted(addresses)[0]


def _safe_parts(raw: Any) -> list[str]:
    if not isinstance(raw, str) or not raw or len(raw) > 512 or "\\" in raw or "\x00" in raw:
        raise ValueError("path_rejected")
    path = Path(raw)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in raw.split("/")):
        raise ValueError("path_rejected")
    parts = list(path.parts)
    if (parts[0].startswith(".") or parts[0].lower() in
            {"inbox", "outbox", "runtime", "config", "settings", "logs", "dist"}):
        raise ValueError("reserved_path")
    if path.suffix.lower() not in {".md", ".txt", ".csv"}:
        raise ValueError("artifact_type_rejected")
    return parts


class CapabilityExecutor:
    """Execute a small reviewed catalog in the caller's fixed workspace."""

    CAPABILITIES = frozenset(BUILTIN_CATALOG)

    def __init__(self, workspace: Path, *, catalog: Any = None, scope: Optional[dict] = None,
                 browser_recipe_host: Any = None):
        self.workspace = Path(workspace).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        if not self.workspace.is_dir():
            raise ValueError("workspace_not_directory")
        self.ledger = self.workspace / ".muse-capability-actions.sqlite3"
        self.catalog = catalog
        self.scope = dict(scope or BUILTIN_SCOPE)
        self.browser_recipe_host = browser_recipe_host
        fd = os.open(str(self.ledger), os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        try:
            os.fchmod(fd, 0o600)
        finally:
            os.close(fd)

    def execute(self, call: dict, *, approved: bool, context: Optional[dict] = None) -> dict:
        call = call if isinstance(call, dict) else {}
        action_id = call.get("action_id")
        capability = call.get("capability")
        base = {"ok": False, "status": "REJECTED", "action_id": action_id,
                "capability": capability, "output": {}, "verification": {}, "evidence": {}}
        if (not isinstance(action_id, str) or len(action_id) > 160
                or not re.fullmatch(r"[A-Za-z0-9._:-]+", action_id)):
            return dict(base, status="INVALID_CALL", error="action_id_required")
        if not isinstance(call.get("goal_id"), str) or not call["goal_id"]:
            return dict(base, status="INVALID_CALL", error="goal_id_required")
        if type(call.get("revision")) is not int or call["revision"] < 1:
            return dict(base, status="INVALID_CALL", error="revision_required")
        if not isinstance(call.get("args"), dict):
            return dict(base, status="INVALID_CALL", error="args_must_be_object")
        if capability not in self.CAPABILITIES:
            return dict(base, status="BLOCKED", error="unknown_capability")
        if approved is not True:
            return dict(base, status="WAITING_APPROVAL", error="host_approval_required")
        if context is not None and not isinstance(context, dict):
            return dict(base, status="INVALID_CALL", error="context_must_be_object")
        context = context or {}
        if "scope" in context and context["scope"] != self.scope:
            return dict(base, status="BLOCKED", error="capability_scope_mismatch")
        if self.catalog is not None:
            try:
                entry = self.catalog.get(capability, self.scope)
                expected = next(item for item in builtin_capability_documents(self.scope)
                                if item["id"] == capability)
                encoded = json.dumps(entry["document"], ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8") if entry else b""
                if (not entry or not entry["enabled"] or entry["document"] != expected or
                        hashlib.sha256(encoded).hexdigest() != entry["digest"]):
                    return dict(base, status="BLOCKED", error="capability_catalog_not_enabled_or_changed")
            except (ValueError, KeyError, TypeError, StopIteration, sqlite3.Error):
                return dict(base, status="BLOCKED", error="capability_catalog_unavailable")
        permissions = context.get("permissions")
        if permissions is not None:
            allowed_caps = permissions.get("capabilities") if isinstance(permissions, dict) else None
            if not isinstance(allowed_caps, list) or capability not in allowed_caps:
                return dict(base, status="BLOCKED", error="capability_outside_approved_plan")
            if capability == "workspace.write_artifact":
                try:
                    path = "/".join(_safe_parts(call["args"].get("relative_path")))
                except ValueError as exc:
                    return dict(base, status="BLOCKED", error=str(exc))
                refs = permissions.get("resource_refs")
                if not isinstance(refs, list) or "resource:workspace/" + path not in refs:
                    return dict(base, status="BLOCKED", error="resource_outside_approved_plan")
        try:
            if capability == "web.search":
                return self._web_search(call, base, context)
            if capability == "browser.research":
                return self._browser_research(call, base, context)
            if capability == "web.read":
                return self._web_read(call, base, context)
            if capability == "system.frontmost_app":
                return self._frontmost(call, base, context)
            if capability == "system.app_health":
                return self._app_health(call, base, context)
            if capability == "app.recipe":
                return dict(base, status="BLOCKED", error="textedit_recipe_host_required")
            return self._write_artifact(call, base)
        except (OSError, ValueError, UnicodeError, LookupError, TimeoutError, sqlite3.Error,
                http.client.HTTPException, subprocess.TimeoutExpired) as exc:
            return dict(base, status="BLOCKED", error=str(exc)[:160])

    def _web_search(self, call: dict, base: dict, context: dict) -> dict:
        from muse_web_search import search_public

        args = call["args"]
        if set(args) - {"query", "max_results"}:
            raise ValueError("search_args_invalid")
        output = search_public(args.get("query"), max_results=args.get("max_results", 10),
                               allowed_domains=context.get("allowed_domains"))
        return dict(base, ok=True, status="COMPLETED", output=output,
                    verification={"http_status": 200, "candidate_count": output["candidate_count"],
                                  "public_results": len(output["results"])},
                    evidence={"search_page": output["search_page"],
                              "retrieved_at": output["retrieved_at"],
                              "content_sha256": output["content_sha256"]})

    def _browser_research(self, call: dict, base: dict, context: dict) -> dict:
        from muse_browser import IsolatedEdgeSession
        from muse_search_policy import page_relevance, topic_terms

        args = call["args"]
        basic = {"query", "engine", "max_pages"}
        learned = {"recipe_id", "recipe_revision", "recipe_digest",
                   "target_bundle_id", "window_title"}
        recipe_bound = set(args) == basic | learned
        if set(args) not in (basic, basic | learned) or args.get("engine") != "python.org":
            raise ValueError("browser_research_args_invalid")
        query, max_pages = args["query"], args["max_pages"]
        if (not isinstance(query, str) or not 2 <= len(query.strip()) <= 160 or
                type(max_pages) is not int or not 1 <= max_pages <= 3):
            raise ValueError("browser_research_args_invalid")
        permissions = context.get("permissions")
        refs = permissions.get("resource_refs") if isinstance(permissions, dict) else None
        if (not isinstance(refs, list) or any(not isinstance(ref, str) for ref in refs) or
                not {"app:com.microsoft.edgemac", "site:python.org"} <= set(refs)):
            return dict(base, status="BLOCKED", error="browser_scope_not_approved")
        allowed_domains = context.get("allowed_domains")
        if not isinstance(allowed_domains, list) or not allowed_domains:
            return dict(base, status="BLOCKED", error="browser_domains_not_approved")
        _public_url("https://www.python.org/", allowed_domains)
        if context.get("gui_control_granted") is not True:
            return dict(base, status="WAITING_USER", error="gui_control_not_granted")
        if recipe_bound:
            if self.browser_recipe_host is None:
                return dict(base, status="BLOCKED", error="browser_recipe_host_unavailable")
            self.browser_recipe_host.validate_for_run(call, context)
        sources = []
        rejected = []
        with IsolatedEdgeSession(self.workspace / ".muse-browser-sessions",
                                 allowed_domains=allowed_domains) as browser:
            search = (self.browser_recipe_host.search_with_recipe(browser, call, context)
                      if recipe_bound else browser.search(query, engine="python.org"))
            terms = topic_terms(query)
            if not terms:
                raise ValueError("browser_query_has_no_topic")
            for result in search["results"][:10]:
                title = result["title"].lower()
                snippet = result.get("snippet", "").lower()
                path = urlsplit(result["url"]).path.lower()
                if (any(part in path for part in ("/jobs/", "/events/", "/retired/", "/community/sigs/",
                                                  "/download/releases/", "/doc/2.")) or
                        re.search(r"\b(?:jobs?|careers?|hiring|retired|obsolete|deprecated)\b", title) or
                        re.search(r"\bpython\s+[12]\.\d", title) or
                        re.search(r"\bpython\s+3\.\d+\.\d+(?:a\d+|b\d+|rc\d+)\b", title) or
                        not all(term in title or term in snippet for term in terms)):
                    rejected.append({"result_index": result["result_index"], "reason": "candidate_not_current_or_topical"})
                    continue
                if sources or rejected:
                    browser.navigate(search["search_page"])
                page = browser.click_result(result["result_index"], result["url"])
                if not page["title"] or len(page["text"].strip()) < 80:
                    rejected.append({"result_index": result["result_index"], "reason": "page_content_insufficient"})
                    continue
                topical, reason = page_relevance(query, page)
                if not topical:
                    rejected.append({"result_index": result["result_index"], "reason": reason})
                    continue
                sources.append({"rank": result["result_index"] + 1, "title": page["title"],
                                "source_url": page["source_url"], "text": page["text"],
                                "retrieved_at": page["retrieved_at"],
                                "content_sha256": page["content_sha256"],
                                "click_transport": page["click_transport"], "untrusted_source": True})
                if len(sources) == max_pages:
                    break
            version = browser.browser_version
        if len(sources) != max_pages:
            return dict(base, status="BLOCKED", error="browser_sources_insufficient",
                        output={"query": query, "sources": sources, "rejected_candidates": rejected})
        output = {"query": query, "engine": "python.org", "search_page": search["search_page"],
                  "sources": sources, "quality": "UNREVIEWED"}
        if recipe_bound:
            output.update({key: search[key] for key in
                           ("recipe_id", "recipe_revision", "recipe_digest", "recipe_steps")})
        return dict(base, ok=True, status="COMPLETED", output=output,
                    verification={"clicked_pages": len(sources), "readback_pages": len(sources),
                                  "rejected_candidates": rejected,
                                  "learned_search_recipe": recipe_bound,
                                  "browser": "Microsoft Edge", "browser_version": version,
                                  "profile": "isolated_and_removed"},
                    evidence={"search_page": search["search_page"],
                              "sources": [{"url": item["source_url"], "sha256": item["content_sha256"],
                                           "retrieved_at": item["retrieved_at"]} for item in sources]})

    def _web_read(self, call: dict, base: dict, context: dict) -> dict:
        url, host, target = _public_url(call["args"].get("url"), context.get("allowed_domains"))
        address = _public_address(host)
        connection = _PinnedHTTPS(host, address)
        try:
            connection.request("GET", target, headers={"Host": host, "User-Agent": "MuseLocalAgent/0.1",
                                                       "Accept": "text/html,text/plain", "Accept-Encoding": "identity"})
            response = connection.getresponse()
            if response.status != 200:
                raise ValueError("http_status_" + str(response.status))
            content_type = response.getheader("Content-Type", "").lower()
            if not any(value in content_type for value in ("text/html", "text/plain", "application/xhtml+xml")):
                raise ValueError("unsupported_content_type")
            content_encoding = response.getheader("Content-Encoding", "")
            raw = response.read(MAX_WEB_READ_BYTES + 1)
            if len(raw) > MAX_WEB_READ_BYTES:
                raise ValueError("page_too_large")
        finally:
            connection.close()
        body = _decode_web_body(raw, content_encoding)
        charset = "utf-8"
        if "charset=" in content_type:
            charset = content_type.split("charset=", 1)[1].split(";", 1)[0].strip().strip("\"'")
        decoded = body.decode(charset, errors="strict")
        if any(ord(char) < 32 and char not in "\r\n\t" for char in decoded):
            raise ValueError("non_text_body_rejected")
        if "html" in content_type:
            parser = _PageText()
            parser.feed(decoded)
            extracted = "\n".join(parser.parts)
            text = extracted[:MAX_WEB_TEXT]
            title = " ".join(parser.title)[:240]
        else:
            extracted = decoded
            text = extracted[:MAX_WEB_TEXT]
            title = ""
        when = datetime.now(timezone.utc).isoformat()
        digest = hashlib.sha256(body).hexdigest()
        return dict(base, ok=True, status="COMPLETED",
                    output={"title": title, "text": text, "source_url": url,
                            "retrieved_at": when, "content_sha256": digest,
                            "text_truncated": len(extracted) > len(text),
                            "extracted_text_chars": len(extracted)},
                    verification={"http_status": 200, "public_address": True,
                                  "transfer_encoding": content_encoding or "identity",
                                  "compressed_bytes": len(raw), "decoded_bytes": len(body),
                                  "text_truncated": len(extracted) > len(text)},
                    evidence={"source_url": url, "retrieved_at": when, "content_sha256": digest})

    def _frontmost(self, call: dict, base: dict, context: dict) -> dict:
        if call["args"]:
            raise ValueError("unexpected_args")
        script = ('ObjC.import("AppKit"); var app=$.NSWorkspace.sharedWorkspace.frontmostApplication; '
                  'var info=$.NSBundle.bundleWithURL(app.bundleURL); '
                  'var category=info?info.objectForInfoDictionaryKey("LSApplicationCategoryType"):null; '
                  'JSON.stringify({name:ObjC.unwrap(app.localizedName),'
                  'bundle_id:ObjC.unwrap(app.bundleIdentifier),pid:app.processIdentifier,'
                  'category:category?ObjC.unwrap(category):""})')
        completed = subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", "-e", script],
                                   capture_output=True, text=True, timeout=3, check=False)
        if completed.returncode != 0:
            raise ValueError("frontmost_unavailable")
        data = json.loads(completed.stdout)
        if not isinstance(data, dict):
            raise ValueError("frontmost_invalid_response")
        name = str(data.get("name") or "")[:120]
        bundle = str(data.get("bundle_id") or "")[:160]
        category = str(data.get("category") or "")[:160]
        allowed = context.get("allowed_bundle_ids")
        permissions = context.get("permissions")
        if allowed is None and isinstance(permissions, dict):
            refs = permissions.get("resource_refs")
            allowed = ([value[4:] for value in refs
                        if isinstance(value, str) and value.startswith("app:")]
                       if isinstance(refs, list) else [])
        if not isinstance(allowed, list) or bundle not in allowed:
            return dict(base, status="BLOCKED", error="frontmost_app_outside_approved_scope")
        lowered = (name + " " + bundle + " " + category).lower()
        if any(word in lowered for word in ("game", "steam", "游戏", "password", "keychain",
                                             "bitwarden", "1password", "bank", "wallet", "payment")):
            return dict(base, status="BLOCKED", error="sensitive_or_game_app_excluded")
        when = datetime.now(timezone.utc).isoformat()
        return dict(base, ok=True, status="COMPLETED",
                    output={"name": name, "bundle_id": bundle, "pid": int(data["pid"]),
                            "windows": "NOT_COLLECTED"},
                    verification={"source": "NSWorkspace.frontmostApplication", "read_only": True},
                    evidence={"observed_at": when, "source": "local_appkit"})

    def _app_health(self, call: dict, base: dict, context: dict) -> dict:
        args = call["args"]
        if set(args) != {"bundle_id"} or not isinstance(args["bundle_id"], str):
            raise ValueError("app_health_args_invalid")
        bundle = args["bundle_id"]
        if (not re.fullmatch(r"[A-Za-z0-9.-]{3,160}", bundle) or "." not in bundle or
                any(word in bundle.lower() for word in ("game", "steam", "password", "keychain",
                                                       "bitwarden", "1password", "bank", "wallet", "payment"))):
            raise ValueError("sensitive_or_invalid_bundle")
        permissions = context.get("permissions")
        refs = permissions.get("resource_refs") if isinstance(permissions, dict) else None
        if not isinstance(refs, list) or "app:" + bundle not in refs:
            return dict(base, status="BLOCKED", error="app_outside_approved_scope")
        script = ('ObjC.import("AppKit"); function run(argv) {'
                  'var apps=$.NSRunningApplication.runningApplicationsWithBundleIdentifier(argv[0]);'
                  'var pids=[];for(var i=0;i<Math.min(Number(apps.count),10);i++) {'
                  'var app=apps.objectAtIndex(i);if(!Boolean(app.terminated))pids.push(Number(app.processIdentifier));}'
                  'return JSON.stringify({bundle_id:argv[0],pids:pids});}')
        completed = subprocess.run(["/usr/bin/osascript", "-l", "JavaScript", "-e", script, bundle],
                                   capture_output=True, text=True, timeout=3, check=False)
        if completed.returncode != 0 or len(completed.stdout) > 2048:
            raise ValueError("app_health_unavailable")
        data = json.loads(completed.stdout)
        if (not isinstance(data, dict) or data.get("bundle_id") != bundle or
                not isinstance(data.get("pids"), list) or len(data["pids"]) > 10 or
                any(type(pid) is not int or pid <= 0 for pid in data["pids"])):
            raise ValueError("app_health_invalid_response")
        when = datetime.now(timezone.utc).isoformat()
        return dict(base, ok=True, status="COMPLETED",
                    output={"bundle_id": bundle, "running": bool(data["pids"]),
                            "pids": data["pids"], "observed_at": when},
                    verification={"source": "NSRunningApplication", "read_only": True,
                                  "shell_used": False},
                    evidence={"observed_at": when, "source": "local_appkit"})

    def _write_artifact(self, call: dict, base: dict) -> dict:
        args = call["args"]
        parts = _safe_parts(args.get("relative_path"))
        content = args.get("content")
        if not isinstance(content, str):
            raise ValueError("content_must_be_string")
        encoded = content.encode("utf-8")
        if len(encoded) > MAX_ARTIFACT_BYTES:
            raise ValueError("artifact_too_large")
        sources = args.get("sources", [])
        if not isinstance(sources, list) or len(sources) > 16:
            raise ValueError("sources_invalid")
        for source in sources:
            if not isinstance(source, dict) or "url" not in source or "retrieved_at" not in source:
                raise ValueError("source_invalid")
            _public_url(source["url"])
            if datetime.fromisoformat(str(source["retrieved_at"]).replace("Z", "+00:00")).tzinfo is None:
                raise ValueError("source_time_requires_timezone")
        fingerprint = hashlib.sha256(json.dumps({"goal_id": call["goal_id"], "revision": call["revision"],
                                                  "capability": call["capability"], "args": args},
                                                 sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
        digest = hashlib.sha256(encoded).hexdigest()
        if self.ledger.is_symlink():
            raise ValueError("ledger_symlink_rejected")
        db = sqlite3.connect(str(self.ledger), timeout=5)
        try:
            db.execute("CREATE TABLE IF NOT EXISTS actions (action_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result TEXT)")
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("SELECT fingerprint, result FROM actions WHERE action_id=?", (call["action_id"],)).fetchone()
            if row and row[0] != fingerprint:
                raise ValueError("action_id_changed")
            if row and row[1]:
                if self._read_beneath_workspace(parts) != encoded:
                    raise ValueError("replay_readback_mismatch")
                db.commit()
                result = json.loads(row[1])
                result["evidence"]["replayed"] = True
                return result
            if not row:
                db.execute("INSERT INTO actions VALUES (?, ?, NULL)", (call["action_id"], fingerprint))
            self._write_beneath_workspace(parts, encoded)
            when = datetime.now(timezone.utc).isoformat()
            result = dict(base, ok=True, status="COMPLETED",
                          output={"relative_path": "/".join(parts), "bytes": len(encoded),
                                  "sha256": digest, "sources": sources},
                          verification={"readback_matches": True, "sha256": digest},
                          evidence={"written_at": when, "workspace": str(self.workspace)})
            db.execute("UPDATE actions SET result=? WHERE action_id=?", (json.dumps(result), call["action_id"]))
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def _write_beneath_workspace(self, parts: list[str], encoded: bytes) -> None:
        directory = os.open(str(self.workspace), os.O_RDONLY | os.O_DIRECTORY)
        try:
            for part in parts[:-1]:
                try:
                    os.mkdir(part, mode=0o700, dir_fd=directory)
                except FileExistsError:
                    pass
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                os.close(directory)
                directory = child
            try:
                fd = os.open(parts[-1], os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                             0o600, dir_fd=directory)
            except FileExistsError:
                fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
                try:
                    if os.read(fd, MAX_ARTIFACT_BYTES + 1) != encoded:
                        raise ValueError("overwrite_protection")
                finally:
                    os.close(fd)
            else:
                try:
                    with os.fdopen(fd, "wb", closefd=False) as stream:
                        stream.write(encoded)
                        stream.flush()
                        os.fsync(stream.fileno())
                finally:
                    os.close(fd)
        finally:
            os.close(directory)
        if self._read_beneath_workspace(parts) != encoded:
            raise ValueError("readback_mismatch")

    def _read_beneath_workspace(self, parts: list[str]) -> bytes:
        directory = os.open(str(self.workspace), os.O_RDONLY | os.O_DIRECTORY)
        try:
            for part in parts[:-1]:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory)
                os.close(directory)
                directory = child
            fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
            try:
                return os.read(fd, MAX_ARTIFACT_BYTES + 1)
            finally:
                os.close(fd)
        finally:
            os.close(directory)
