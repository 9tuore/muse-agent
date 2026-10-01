"""Persisted model selection and bounded OpenAI-compatible generation for Muse."""

from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from muse_model_costs import CostLedger
from muse_keychain import get_password, set_password
from muse_provider_protocols import (build_request, followup_request, parse_response,
                                     parse_stream, reasoning_efforts)


DEFAULT_SETTINGS: Dict[str, Any] = {
    "version": 3,
    "mode": "local",
    "profiles": {
        "local-default": {
            "protocol": "openai_compatible",
            "endpoint": "http://127.0.0.1:8080/v1/chat/completions",
            "model": "local",
            "keychain_service": "",
            "keychain_account": "",
        },
        "high-default": {
            "protocol": "openai_compatible",
            "endpoint": "",
            "model": "",
            "keychain_service": "",
            "keychain_account": "",
        },
    },
    "active_local": "local-default",
    "active_high": "high-default",
    "backup_high": "",
    "selected_reasoning_effort": {},
    "purpose_routes": {},
    "cloud_data_allowed": False,
    "allow_unknown_cost": False,
    "daily_remote_call_limit": 0,
    "daily_token_limit": 20000,
    "per_goal_token_limit": 10000,
    "max_tokens_per_call": 1024,
    "timeout_seconds": 60,
}

HIGH_PURPOSES = {"goal_plan", "goal_compile", "research", "research_synthesis", "complex_reasoning"}

_CLOUD_SENSITIVE = (
    re.compile(r"-----BEGIN (?:[A-Z ]+ )?PRIVATE KEY-----", re.IGNORECASE),
    re.compile(r"\b(?:sk|sk-proj|sk-ant|sk-or)-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._~-]{12,}\b", re.IGNORECASE),
    re.compile(r"(?:api[_ -]?key|password|passwd|secret|access[_ -]?token|auth[_ -]?code|验证码|授权码)\s*[\"']?\s*[:=：]\s*[\"']?[^\s\"',;}]{6,}", re.IGNORECASE),
)


def _cloud_sensitive(payload: Dict[str, Any]) -> bool:
    serialized = json.dumps(payload, ensure_ascii=False)
    return any(pattern.search(serialized) for pattern in _CLOUD_SENSITIVE)


class ModelGateway:
    """Use one selected model slot, with explicit cloud and budget boundaries."""

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.settings_path = self.workspace / ".muse_model_settings.json"
        self.usage_path = self.workspace / ".muse_model_usage.json"
        self.lock_path = self.workspace / ".muse_model_usage.lock"
        self.costs = CostLedger(self.workspace)
        self.key_bindings_path = self.workspace / ".muse_model_key_bindings.json"
        self._pending_tools: Dict[str, Dict[str, Any]] = {}

    @staticmethod
    def _origin(endpoint: str) -> str:
        parsed = urllib.parse.urlsplit(endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("invalid_model_endpoint")
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        return f"{parsed.scheme}://{parsed.hostname.lower()}:{port}"

    @staticmethod
    def _base_url_without_operation(endpoint: str) -> bool:
        # This client posts to the configured URL directly; unlike an SDK it
        # does not append /chat/completions or /responses to a /v1 base URL.
        return urllib.parse.urlsplit(endpoint).path.rstrip("/") == "/v1"

    def configure_pricing(self, *, profile_id: str, model: str, origin: str,
                          input_cny_per_million: Any, output_cny_per_million: Any,
                          source: str, confirmed: bool) -> Dict[str, Any]:
        settings = self.get_settings()
        profile = settings["profiles"].get(profile_id)
        if profile is None or model != profile["model"] or origin != self._origin(profile["endpoint"]):
            raise ValueError("price_profile_mismatch")
        if self._is_loopback(profile["endpoint"]):
            raise ValueError("local_model_has_no_remote_price")
        return self.costs.configure_price(
            profile_id=profile_id, model=model, protocol=profile["protocol"], origin=origin,
            input_cny_per_million=input_cny_per_million,
            output_cny_per_million=output_cny_per_million, source=source, confirmed=confirmed)

    def cost_status(self) -> Dict[str, Any]:
        return self.costs.status()

    def pricing_status(self) -> Dict[str, Any]:
        return {"prices": self.costs.prices(), "budget": self.cost_status()}

    def profile_capabilities(self, profile_id: str) -> Dict[str, Any]:
        settings = self.get_settings()
        profile = settings["profiles"].get(profile_id)
        if profile is None:
            raise ValueError("model_slot_not_found")
        efforts = reasoning_efforts(profile["protocol"], profile["model"])
        return {"profile_id": profile_id, "model": profile["model"],
                "protocol": profile["protocol"], "reasoning_efforts": list(efforts),
                "selected_reasoning_effort": settings["selected_reasoning_effort"].get(profile_id),
                "reasoning_supported": bool(efforts),
                "tools_supported": profile["protocol"] in {"openai_responses", "deepseek_chat"},
                "stream_supported": profile["protocol"] in {"openai_responses", "deepseek_chat"}}

    def continue_tool_calls(self, proposal_id: str, results: list) -> Dict[str, Any]:
        """Return verified tool results to the provider; never execute a tool here."""
        if not isinstance(proposal_id, str):
            return self._blocked("invalid_tool_proposal")
        pending = self._pending_tools.pop(proposal_id, None)
        if pending is None or time.monotonic() > pending["expires_at"]:
            return self._blocked("tool_proposal_expired")
        return self.generate(pending["prompt"], purpose=pending["purpose"],
                             require_json=pending["require_json"], max_tokens=pending["max_tokens"],
                             goal_id=pending["goal_id"], budget_bucket=pending["budget_bucket"],
                             reasoning_effort=pending["reasoning_effort"], tools=pending["tools"],
                             _continuation=(pending, results))

    def set_profile_secret(self, profile_id: str, secret: str) -> Dict[str, Any]:
        if not isinstance(secret, str) or not secret.strip() or len(secret) > 4096:
            raise ValueError("invalid_model_secret")
        settings = self.get_settings()
        profile = settings["profiles"].get(profile_id)
        if profile is None or not profile["endpoint"] or self._is_loopback(profile["endpoint"]):
            raise ValueError("remote_profile_required")
        origin = self._origin(profile["endpoint"])
        service = "org.gosim.local-agent.model." + profile_id
        try:
            set_password(service, profile_id, secret)
        except (OSError, ValueError) as exc:
            raise ValueError("keychain_write_failed") from exc
        bindings = self._read_key_bindings()
        bindings[profile_id] = origin
        temporary = self.key_bindings_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(bindings, sort_keys=True) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        os.replace(temporary, self.key_bindings_path)
        profiles = copy.deepcopy(settings["profiles"])
        profiles[profile_id]["keychain_service"] = service
        profiles[profile_id]["keychain_account"] = profile_id
        self.update_settings({"profiles": profiles})
        return {"profile_id": profile_id, "origin": origin, "has_secret": True}

    def _read_key_bindings(self) -> Dict[str, str]:
        if not self.key_bindings_path.exists():
            return {}
        try:
            bindings = json.loads(self.key_bindings_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ValueError("invalid_key_binding_state") from exc
        if not isinstance(bindings, dict) or any(not isinstance(k, str) or
                                                  not isinstance(v, str) for k, v in bindings.items()):
            raise ValueError("invalid_key_binding_state")
        return bindings

    def get_settings(self) -> Dict[str, Any]:
        if not self.settings_path.exists():
            return copy.deepcopy(DEFAULT_SETTINGS)
        try:
            settings = json.loads(self.settings_path.read_text(encoding="utf-8"))
            if isinstance(settings, dict) and settings.get("version") == 1:
                settings.setdefault("selected_reasoning_effort", {})
                settings["version"] = 2
            if isinstance(settings, dict) and settings.get("version") == 2:
                settings.setdefault("backup_high", "")
                settings["version"] = 3
            self._validate_settings(settings)
            return settings
        except (OSError, ValueError, TypeError):
            raise ValueError("invalid_model_settings")

    def update_settings(self, changes: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(changes, dict) or any(key not in DEFAULT_SETTINGS for key in changes):
            raise ValueError("invalid_model_settings")
        settings = self.get_settings()
        settings.update(changes)
        if type(settings["version"]) is int and settings["version"] in {1, 2}:
            settings["version"] = 3
        try:
            self._validate_settings(settings)
        except (TypeError, KeyError) as exc:
            raise ValueError("invalid_model_settings") from exc
        temporary = self.settings_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(settings, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        os.replace(temporary, self.settings_path)
        return settings

    @staticmethod
    def _is_loopback(endpoint: str) -> bool:
        host = (urllib.parse.urlsplit(endpoint).hostname or "").lower()
        return host in {"localhost", "127.0.0.1", "::1"}

    @classmethod
    def _validate_settings(cls, settings: Dict[str, Any]) -> None:
        if not isinstance(settings, dict) or set(settings) != set(DEFAULT_SETTINGS):
            raise ValueError("invalid_model_settings")
        if settings["version"] != 3 or settings["mode"] not in {"local", "high", "mixed", "custom"}:
            raise ValueError("invalid_model_mode")
        profiles = settings["profiles"]
        if not isinstance(profiles, dict) or not 1 <= len(profiles) <= 8:
            raise ValueError("invalid_model_profiles")
        for profile_id, profile in profiles.items():
            if not isinstance(profile_id, str) or not profile_id or len(profile_id) > 64:
                raise ValueError("invalid_model_profile_id")
            if not isinstance(profile, dict) or set(profile) != {
                "protocol", "endpoint", "model", "keychain_service", "keychain_account"
            }:
                raise ValueError("invalid_model_profile")
            if profile["protocol"] not in {"openai_compatible", "anthropic_messages",
                                           "openai_responses", "deepseek_chat"}:
                raise ValueError("unsupported_model_protocol")
            endpoint = profile["endpoint"]
            if not isinstance(endpoint, str) or len(endpoint) > 2048:
                raise ValueError("invalid_model_endpoint")
            if endpoint:
                parsed = urllib.parse.urlsplit(endpoint)
                if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password or parsed.fragment or parsed.query:
                    raise ValueError("invalid_model_endpoint")
                if parsed.scheme == "http" and not cls._is_loopback(endpoint):
                    raise ValueError("remote_model_requires_https")
            for key in ("model", "keychain_service", "keychain_account"):
                if not isinstance(profile[key], str) or len(profile[key]) > 160:
                    raise ValueError("invalid_model_profile")
            service, account = profile["keychain_service"], profile["keychain_account"]
            if bool(service) != bool(account) or (service and (
                service != "org.gosim.local-agent.model." + profile_id or account != profile_id
            )):
                raise ValueError("keychain_ref_outside_project")
        if settings["active_local"] not in profiles or settings["active_high"] not in profiles:
            raise ValueError("model_slot_not_found")
        backup = settings["backup_high"]
        if not isinstance(backup, str) or (backup and (
            backup not in profiles or backup == settings["active_high"]
        )):
            raise ValueError("backup_model_slot_invalid")
        selected = settings["selected_reasoning_effort"]
        if not isinstance(selected, dict) or any(
            profile_id not in profiles or not isinstance(effort, str) or
            effort not in reasoning_efforts(profiles[profile_id]["protocol"], profiles[profile_id]["model"])
            for profile_id, effort in selected.items()
        ):
            raise ValueError("reasoning_effort_unsupported")
        local_endpoint = profiles[settings["active_local"]]["endpoint"]
        if local_endpoint and not cls._is_loopback(local_endpoint):
            raise ValueError("local_model_requires_loopback")
        routes = settings["purpose_routes"]
        if not isinstance(routes, dict) or len(routes) > 32 or any(
            not isinstance(purpose, str) or not purpose or len(purpose) > 80 or slot not in {"local", "high"}
            for purpose, slot in routes.items()
        ):
            raise ValueError("invalid_purpose_routes")
        for key in ("cloud_data_allowed", "allow_unknown_cost"):
            if type(settings[key]) is not bool:
                raise ValueError("invalid_model_settings")
        for key, upper in (("daily_remote_call_limit", 1000), ("daily_token_limit", 1000000), ("per_goal_token_limit", 1000000), ("max_tokens_per_call", 8192), ("timeout_seconds", 120)):
            value = settings[key]
            if type(value) is not int or not 0 <= value <= upper or (key != "daily_remote_call_limit" and value == 0):
                raise ValueError("invalid_model_budget")

    @staticmethod
    def _blocked(error: str, provider: str = "none", model: str = "") -> Dict[str, Any]:
        return {"ok": False, "status": "BLOCKED", "text": "", "provider": provider,
                "model": model, "usage": {"cost": "unknown"}, "error": error}

    def _slot(self, settings: Dict[str, Any], purpose: str) -> str:
        mode = settings["mode"]
        if mode == "high":
            return "high"
        if mode == "local":
            return "local"
        if mode == "custom":
            return settings["purpose_routes"].get(purpose, "local")
        return "high" if purpose in HIGH_PURPOSES else "local"

    @contextmanager
    def _usage_lock(self):
        with self.lock_path.open("a+") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _read_usage(self) -> Dict[str, Any]:
        today = datetime.now(timezone.utc).date().isoformat()
        if not self.usage_path.exists():
            return {"day": today, "used_tokens": 0, "used_by_goal": {}, "remote_calls": 0, "reservations": {}}
        try:
            state = json.loads(self.usage_path.read_text(encoding="utf-8"))
            if state.get("day") != today:
                return {"day": today, "used_tokens": 0, "used_by_goal": {}, "remote_calls": 0, "reservations": {}}
            if (type(state.get("used_tokens")) is int and type(state.get("remote_calls")) is int
                    and isinstance(state.get("used_by_goal"), dict) and isinstance(state.get("reservations"), dict)):
                return state
        except (OSError, ValueError, TypeError):
            pass
        raise ValueError("invalid_model_usage_state")

    def _write_usage(self, state: Dict[str, Any]) -> None:
        temporary = self.usage_path.with_suffix(".tmp")
        temporary.write_text(json.dumps(state, sort_keys=True) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        os.replace(temporary, self.usage_path)

    def _reserve(self, settings: Dict[str, Any], token_limit: int, prompt: str, remote: bool, goal_id: Optional[str]) -> Optional[str]:
        reserve = max(1, (len(prompt) + 3) // 4) + token_limit
        with self._usage_lock():
            state = self._read_usage()
            active = state["reservations"]
            outstanding = sum(item["tokens"] for item in active.values())
            remote_outstanding = sum(bool(item["remote"]) for item in active.values())
            if state["used_tokens"] + outstanding + reserve > settings["daily_token_limit"]:
                return None
            if goal_id:
                goal_outstanding = sum(item["tokens"] for item in active.values() if item.get("goal_id") == goal_id)
                if state["used_by_goal"].get(goal_id, 0) + goal_outstanding + reserve > settings["per_goal_token_limit"]:
                    return None
            if remote and state["remote_calls"] + remote_outstanding >= settings["daily_remote_call_limit"]:
                return None
            reservation_id = uuid.uuid4().hex
            active[reservation_id] = {"tokens": reserve, "remote": remote, "goal_id": goal_id}
            self._write_usage(state)
            return reservation_id

    def _settle(self, reservation_id: str, actual_tokens: int) -> None:
        with self._usage_lock():
            state = self._read_usage()
            item = state["reservations"].pop(reservation_id, None)
            if item is None:
                return
            charged = max(0, actual_tokens)
            state["used_tokens"] += charged
            if item.get("goal_id"):
                goal_id = item["goal_id"]
                state["used_by_goal"][goal_id] = state["used_by_goal"].get(goal_id, 0) + charged
            state["remote_calls"] += int(item["remote"])
            self._write_usage(state)

    def _release(self, reservation_id: str) -> None:
        with self._usage_lock():
            state = self._read_usage()
            state["reservations"].pop(reservation_id, None)
            self._write_usage(state)

    @staticmethod
    def _keychain_password(profile: Dict[str, str]) -> Optional[str]:
        service, account = profile["keychain_service"], profile["keychain_account"]
        if not service or not account:
            return None
        try:
            return get_password(service, account)
        except (OSError, ValueError, UnicodeError):
            return None

    @staticmethod
    def _request_body(protocol: str, model: str, prompt: str, token_limit: int,
                      require_json: bool, provider_payload: Dict[str, Any]) -> Dict[str, Any]:
        if provider_payload:
            return provider_payload
        if protocol == "anthropic_messages":
            body = {"model": model, "max_tokens": token_limit,
                    "messages": [{"role": "user", "content": prompt}]}
            if require_json:
                body["system"] = "Return exactly one valid JSON value without Markdown fences."
            return body
        messages = []
        if require_json:
            messages.append({"role": "system", "content": "Return exactly one valid JSON value without Markdown fences."})
        messages.append({"role": "user", "content": prompt})
        return {"model": model, "messages": messages, "max_tokens": token_limit,
                "temperature": 0 if require_json else 0.3}

    def preview_cloud_request(self, prompt: str, *, purpose: str,
                              require_json: bool = False, max_tokens: int = 512,
                              reasoning_effort: Optional[str] = None,
                              tools: Optional[list] = None, stream: bool = False) -> Dict[str, Any]:
        """Return the exact unsigned body for a UI preview; never send or persist it."""
        if not isinstance(prompt, str) or not prompt.strip() or not isinstance(purpose, str) or not purpose.strip():
            return self._blocked("invalid_model_request")
        if type(max_tokens) is not int or max_tokens < 1:
            return self._blocked("invalid_max_tokens")
        try:
            settings = self.get_settings()
            slot = self._slot(settings, purpose)
            profile_id = settings["active_" + slot]
            profile = settings["profiles"][profile_id]
            endpoint, model, protocol = profile["endpoint"], profile["model"], profile["protocol"]
            if not endpoint or not model:
                return self._blocked("model_slot_not_configured", profile_id, model)
            if self._is_loopback(endpoint):
                return self._blocked("cloud_preview_requires_remote", profile_id, model)
            if self._base_url_without_operation(endpoint):
                return self._blocked("model_endpoint_incomplete", profile_id, model)
            token_limit = min(max_tokens, settings["max_tokens_per_call"])
            effort = (reasoning_effort if reasoning_effort is not None else
                      settings["selected_reasoning_effort"].get(profile_id))
            provider_payload = build_request(protocol, model, prompt, token_limit,
                                             require_json, effort, tools, stream)
            body = self._request_body(protocol, model, prompt, token_limit,
                                      require_json, provider_payload)
            if _cloud_sensitive(body):
                return self._blocked("cloud_sensitive_content", profile_id, model)
            backup_id = settings["backup_high"] if slot == "high" else ""
            backup = settings["profiles"][backup_id] if backup_id else None
            backup_body = None
            if (backup and backup["endpoint"] and backup["model"] and
                    self._origin(backup["endpoint"]) == self._origin(endpoint) and
                    backup["protocol"] == protocol):
                try:
                    backup_effort = (reasoning_effort if reasoning_effort is not None else
                                     settings["selected_reasoning_effort"].get(backup_id))
                    backup_payload = build_request(protocol, backup["model"], prompt,
                                                   token_limit, require_json, backup_effort,
                                                   tools, stream)
                    backup_body = self._request_body(protocol, backup["model"], prompt,
                                                     token_limit, require_json, backup_payload)
                except ValueError:
                    pass
            destination = {
                "profile_id": profile_id, "endpoint": endpoint, "protocol": protocol,
                "model": model,
                "backup": ({"profile_id": backup_id, "endpoint": backup["endpoint"],
                            "protocol": backup["protocol"], "model": backup["model"]}
                           if backup else None),
            }
            fingerprint = hashlib.sha256(json.dumps(
                {"destination": destination, "body": body,
                 "backup_body": backup_body, "purpose": purpose},
                ensure_ascii=False, sort_keys=True, separators=(",", ":")
            ).encode("utf-8")).hexdigest()
            return {"ok": True, "status": "PREVIEW", "route": slot,
                    "destination": destination, "request_body": body,
                    "backup_request_body": backup_body,
                    "request_bytes": len(json.dumps(body, ensure_ascii=False).encode("utf-8")),
                    "sha256": fingerprint}
        except (ValueError, KeyError, TypeError) as exc:
            return self._blocked(str(exc) if isinstance(exc, ValueError) else "invalid_model_request")

    def generate(
        self, prompt: str, *, purpose: str, require_json: bool = False,
        max_tokens: int = 512, goal_id: Optional[str] = None,
        budget_bucket: Optional[str] = None,
        reasoning_effort: Optional[str] = None, tools: Optional[list] = None,
        stream: bool = False,
        cloud_preview_sha256: Optional[str] = None,
        local_messages: Optional[list] = None,
        _continuation: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        request = dict(purpose=purpose, require_json=require_json, max_tokens=max_tokens,
                       goal_id=goal_id, budget_bucket=budget_bucket,
                       reasoning_effort=reasoning_effort, tools=tools, stream=stream,
                       cloud_preview_sha256=cloud_preview_sha256,
                       local_messages=local_messages,
                       _continuation=_continuation)
        primary = self._generate_once(prompt, **request)
        failover_errors = {"provider_auth_failed", "provider_rate_limited",
                           "provider_overloaded", "provider_temporarily_unavailable",
                           "URLError", "TimeoutError", "ConnectionResetError",
                           "ConnectionRefusedError", "RemoteDisconnected"}
        if (_continuation is not None or stream or primary.get("route") != "high"
                or primary.get("status") != "UNAVAILABLE"
                or primary.get("error") not in failover_errors):
            return primary
        try:
            settings = self.get_settings()
            backup_id = settings["backup_high"]
            primary_id = settings["active_high"]
            if not backup_id or primary.get("provider") != primary_id:
                return primary
            source = settings["profiles"][primary_id]
            backup = settings["profiles"][backup_id]
            if (not source["endpoint"] or not backup["endpoint"]
                    or self._origin(source["endpoint"]) != self._origin(backup["endpoint"])
                    or source["protocol"] != backup["protocol"]):
                primary["fallback"] = {"attempted": False, "error": "backup_scope_mismatch"}
                return primary
            guard = (primary_id, self._origin(source["endpoint"]), source["protocol"],
                     backup["endpoint"], backup["model"])
        except (ValueError, KeyError, TypeError):
            primary["fallback"] = {"attempted": False, "error": "backup_settings_unavailable"}
            return primary
        if cloud_preview_sha256 is not None:
            refreshed = self.preview_cloud_request(prompt, purpose=purpose,
                                                   require_json=require_json,
                                                   max_tokens=max_tokens,
                                                   reasoning_effort=reasoning_effort,
                                                   tools=tools, stream=stream)
            if refreshed.get("sha256") != cloud_preview_sha256:
                primary["fallback"] = {"attempted": False, "error": "cloud_preview_changed"}
                return primary
        secondary = self._generate_once(prompt, **request, _profile_override=backup_id,
                                        _fallback_guard=guard)
        if secondary.get("status") == "BLOCKED":
            primary["fallback"] = {"attempted": False, "profile_id": backup_id,
                                   "error": secondary.get("error")}
            return primary
        secondary["fallback"] = {"attempted": True, "from_profile_id": primary_id,
                                 "primary_error": primary.get("error")}
        return secondary

    def _generate_once(
        self, prompt: str, *, purpose: str, require_json: bool = False,
        max_tokens: int = 512, goal_id: Optional[str] = None,
        budget_bucket: Optional[str] = None,
        reasoning_effort: Optional[str] = None, tools: Optional[list] = None,
        stream: bool = False,
        cloud_preview_sha256: Optional[str] = None,
        local_messages: Optional[list] = None,
        _continuation: Optional[tuple] = None,
        _profile_override: Optional[str] = None,
        _fallback_guard: Optional[tuple] = None,
    ) -> Dict[str, Any]:
        if not isinstance(prompt, str) or not prompt.strip() or not isinstance(purpose, str) or not purpose.strip():
            return self._blocked("invalid_model_request")
        if goal_id is not None and (not isinstance(goal_id, str) or len(goal_id) > 128):
            return self._blocked("invalid_goal_id")
        try:
            settings = self.get_settings()
        except ValueError:
            return self._blocked("invalid_model_settings")
        slot = self._slot(settings, purpose)
        profile_id = _profile_override or settings["active_" + slot]
        if _profile_override is not None and (
            slot != "high" or _fallback_guard is None or
            settings["backup_high"] != _profile_override or
            settings["active_high"] != _fallback_guard[0]
        ):
            return self._blocked("backup_route_changed")
        profile = settings["profiles"][profile_id]
        endpoint, model = profile["endpoint"], profile["model"]
        if not endpoint or not model:
            return self._blocked("model_slot_not_configured", profile_id, model)
        if _profile_override is not None and (
            self._origin(endpoint) != _fallback_guard[1] or
            profile["protocol"] != _fallback_guard[2] or
            endpoint != _fallback_guard[3] or model != _fallback_guard[4]
        ):
            return self._blocked("backup_scope_mismatch", profile_id, model)
        remote = not self._is_loopback(endpoint)
        if remote and self._base_url_without_operation(endpoint):
            return self._blocked("model_endpoint_incomplete", profile_id, model)
        if remote and not settings["cloud_data_allowed"]:
            return self._blocked("cloud_data_not_allowed", profile_id, model)
        if remote and settings["daily_remote_call_limit"] == 0:
            return self._blocked("remote_call_budget_exhausted", profile_id, model)
        if type(max_tokens) is not int or max_tokens < 1:
            return self._blocked("invalid_max_tokens", profile_id, model)
        token_limit = min(max_tokens, settings["max_tokens_per_call"])
        protocol = profile["protocol"]
        if local_messages is not None:
            if (remote or protocol != "openai_compatible" or require_json or tools or stream
                    or _continuation is not None or cloud_preview_sha256 is not None
                    or not isinstance(local_messages, list) or not 1 <= len(local_messages) <= 6
                    or not isinstance(local_messages[-1], dict)
                    or local_messages[-1].get("role") != "user"
                    or any(not isinstance(item, dict) or item.get("role") not in
                           {"system", "user", "assistant"} or not isinstance(item.get("content"), str)
                           or not item["content"].strip() or len(item["content"]) > 1600
                           for item in local_messages)):
                return self._blocked("invalid_local_chat_messages", profile_id, model)
        if reasoning_effort is None:
            reasoning_effort = settings["selected_reasoning_effort"].get(profile_id)
        try:
            provider_payload = build_request(protocol, model, prompt, token_limit,
                                             require_json, reasoning_effort, tools, stream)
            if local_messages is not None:
                provider_payload = {"model": model, "messages": local_messages,
                                    "max_tokens": token_limit, "temperature": 0.3}
            if _continuation is not None:
                pending, results = _continuation
                if pending["profile_id"] != profile_id or pending["model"] != model or \
                        pending["protocol"] != protocol:
                    raise ValueError("tool_profile_changed")
                provider_payload = followup_request(protocol, pending["payload"],
                                                    pending["body"], results)
            payload = self._request_body(protocol, model, prompt, token_limit,
                                         require_json, provider_payload)
        except (ValueError, TypeError) as exc:
            return self._blocked(str(exc) if isinstance(exc, ValueError) else
                                 "invalid_model_request", profile_id, model)
        if remote:
            if _cloud_sensitive(payload):
                return self._blocked("cloud_sensitive_content", profile_id, model)
            if cloud_preview_sha256 is not None and _continuation is None:
                preview = self.preview_cloud_request(prompt, purpose=purpose,
                                                     require_json=require_json,
                                                     max_tokens=max_tokens,
                                                     reasoning_effort=reasoning_effort,
                                                     tools=tools, stream=stream)
                expected = (preview.get("backup_request_body") if _profile_override else
                            preview.get("request_body"))
                if preview.get("sha256") != cloud_preview_sha256 or expected != payload:
                    return self._blocked("cloud_preview_changed", profile_id, model)
        price = None
        bucket = budget_bucket or ("goal" if goal_id else "integration")
        if remote:
            try:
                origin = self._origin(endpoint)
                price = self.costs.price_for(profile_id, model, profile["protocol"], origin)
                if self._read_key_bindings().get(profile_id) != origin:
                    return self._blocked("keychain_origin_mismatch", profile_id, model)
            except ValueError as exc:
                return self._blocked(str(exc), profile_id, model)
        secret = self._keychain_password(profile) if remote and profile["keychain_service"] else None
        if remote and not secret:
            return self._blocked("keychain_secret_unavailable", profile_id, model)
        usage_prompt = json.dumps(provider_payload, ensure_ascii=False) if provider_payload else prompt
        try:
            reservation_id = self._reserve(settings, token_limit, usage_prompt, remote, goal_id)
        except (OSError, ValueError, TypeError, KeyError):
            return self._blocked("invalid_model_usage_state", profile_id, model)
        if reservation_id is None:
            return self._blocked("model_budget_exhausted", profile_id, model)
        money_reservation_id = None
        if remote:
            try:
                # Byte length plus protocol overhead conservatively bounds the
                # tokenized request for the plain-text protocols used here.
                input_bound = len(json.dumps(provider_payload or {"prompt": prompt},
                                             ensure_ascii=False).encode("utf-8")) + 1024
                money_reservation_id, _ = self.costs.reserve(price, input_bound, token_limit, bucket)
            except ValueError as exc:
                self._release(reservation_id)
                return self._blocked(str(exc), profile_id, model)
        actual_tokens = max(1, (len(prompt) + 3) // 4)
        started = time.monotonic()
        try:
            headers = {"Content-Type": "application/json"}
            if protocol == "anthropic_messages":
                headers["anthropic-version"] = "2023-06-01"
                if secret:
                    headers["x-api-key"] = secret
            else:
                if secret:
                    headers["Authorization"] = "Bearer " + secret
            request = urllib.request.Request(endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
            opener = urllib.request.build_opener(_NoRedirect())
            with opener.open(request, timeout=settings["timeout_seconds"]) as response:
                if stream:
                    parsed = parse_stream(protocol, response)
                    body = {}
                else:
                    body = json.loads(response.read(2 * 1024 * 1024).decode("utf-8"))
                    parsed = (parse_response(protocol, body)
                              if provider_payload and protocol != "openai_compatible" else None)
            if parsed is not None:
                text = parsed["text"]
                tool_calls = parsed["tool_calls"]
                prompt_tokens = parsed["prompt_tokens"]
                completion_tokens = parsed["completion_tokens"]
                returned_model = parsed["model"] or model
            elif protocol == "anthropic_messages":
                text = "".join(block.get("text", "") for block in body["content"] if block.get("type") == "text")
                tool_calls = []
            else:
                text = body["choices"][0]["message"]["content"]
                tool_calls = []
            if not isinstance(text, str) or (not text.strip() and not tool_calls):
                raise ValueError("empty_model_response")
            text = text.strip()
            if require_json and not tool_calls:
                json.loads(text)
            if parsed is None:
                reported = body.get("usage") if isinstance(body.get("usage"), dict) else {}
                prompt_tokens = reported.get("input_tokens" if protocol == "anthropic_messages" else "prompt_tokens")
                completion_tokens = reported.get("output_tokens" if protocol == "anthropic_messages" else "completion_tokens")
                returned_model = body.get("model") or model
            if type(prompt_tokens) is int and type(completion_tokens) is int and prompt_tokens >= 0 and completion_tokens >= 0:
                actual_tokens = prompt_tokens + completion_tokens
                source = "provider_reported"
            else:
                actual_tokens += max(1, (len(text) + 3) // 4)
                source = "estimated"
            cost = "unknown"
            if remote:
                if source != "provider_reported":
                    raise ValueError("provider_usage_missing")
                cost = {"currency": "CNY", "micros": self.costs.settle(
                    money_reservation_id, price, prompt_tokens, completion_tokens)}
                money_reservation_id = None
            proposal_id = None
            if tool_calls:
                proposal_id = uuid.uuid4().hex
                self._pending_tools[proposal_id] = {
                    "profile_id": profile_id, "model": model, "protocol": protocol,
                    "prompt": prompt, "purpose": purpose, "require_json": require_json,
                    "max_tokens": max_tokens, "goal_id": goal_id,
                    "budget_bucket": budget_bucket, "reasoning_effort": reasoning_effort,
                    "tools": tools, "payload": payload, "body": body,
                    "expires_at": time.monotonic() + 300}
            return {
                "ok": not tool_calls, "status": "TOOL_PROPOSAL" if tool_calls else "COMPLETED", "text": text,
                "tool_calls": tool_calls, "proposal_id": proposal_id,
                "provider": profile_id, "model": returned_model,
                "route": slot, "goal_id": goal_id,
                "usage": {"prompt_tokens": prompt_tokens if source == "provider_reported" else None,
                          "completion_tokens": completion_tokens if source == "provider_reported" else None,
                          "total_tokens": actual_tokens, "source": source, "cost": cost,
                          "latency_ms": round((time.monotonic() - started) * 1000)},
            }
        except urllib.error.HTTPError as exc:
            error = {400: "provider_invalid_request", 401: "provider_auth_failed",
                     402: "provider_balance_exhausted", 429: "provider_rate_limited",
                     408: "provider_temporarily_unavailable",
                     500: "provider_temporarily_unavailable",
                     502: "provider_temporarily_unavailable",
                     503: "provider_overloaded",
                     504: "provider_temporarily_unavailable"}.get(exc.code, "provider_http_error")
            return {"ok": False, "status": "UNAVAILABLE", "text": "", "provider": profile_id,
                    "model": model, "route": slot, "usage": {"cost": "uncertain"}, "error": error}
        except (OSError, ValueError, KeyError, IndexError, TypeError, AttributeError) as exc:
            known = {"empty_model_response", "provider_usage_missing", "model_response_incomplete",
                     "model_stream_incomplete", "model_stream_failed", "model_stream_usage_missing",
                     "model_stream_too_large", "invalid_model_tool_call", "invalid_model_response"}
            error = str(exc) if isinstance(exc, ValueError) and str(exc) in known else type(exc).__name__
            return {"ok": False, "status": "UNAVAILABLE", "text": "", "provider": profile_id,
                    "model": model, "route": slot, "usage": {"cost": "unknown"},
                    "error": error}
        finally:
            if money_reservation_id is not None:
                self.costs.uncertain(money_reservation_id)
            self._settle(reservation_id, actual_tokens)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None
