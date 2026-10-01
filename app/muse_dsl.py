"""Versioned data contracts shared by Goal, Memory, and Capability.

Documents describe requests and records. They never carry host approval.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


SCHEMA_VERSION = "muse.dsl/1"
MAX_DOCUMENT_BYTES = 64 * 1024
_IDENTIFIER = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,159}\Z")
_CAPABILITY = re.compile(r"[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*\Z")
_SCHEMA_FILES = {
    "memory": "muse_memory_schema.json",
    "capability": "muse_capability_schema.json",
}


class DslValidationError(ValueError):
    pass


def _timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str) or len(value) > 40:
        raise DslValidationError(field + ":date_time_required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DslValidationError(field + ":date_time_required") from exc
    if parsed.tzinfo is None:
        raise DslValidationError(field + ":timezone_required")
    return parsed


def _identifier(value: Any, field: str) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.fullmatch(value):
        raise DslValidationError(field + ":invalid_id")


def _finite(value: Any, depth: int = 0) -> None:
    if depth > 16:
        raise DslValidationError("document_too_deep")
    if isinstance(value, float) and not math.isfinite(value):
        raise DslValidationError("nonfinite_number")
    if isinstance(value, dict):
        for item in value.values():
            _finite(item, depth + 1)
    elif isinstance(value, list):
        for item in value:
            _finite(item, depth + 1)


def _unique_pairs(pairs: list[tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DslValidationError("duplicate_json_key:" + key)
        result[key] = value
    return result


def decode_document(raw: str | bytes) -> Dict[str, Any]:
    if not isinstance(raw, (str, bytes)) or len(raw.encode("utf-8") if isinstance(raw, str) else raw) > MAX_DOCUMENT_BYTES:
        raise DslValidationError("document_too_large")
    try:
        document = json.loads(raw, object_pairs_hook=_unique_pairs,
                              parse_constant=lambda _: (_ for _ in ()).throw(DslValidationError("nonfinite_number")))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise DslValidationError("invalid_json") from exc
    validate_document(document)
    return document


def encode_document(document: Dict[str, Any]) -> str:
    validate_document(document)
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def validate_document(document: Dict[str, Any]) -> None:
    if not isinstance(document, dict):
        raise DslValidationError("document_must_be_object")
    expected = {"schema_version", "kind", "id", "revision", "scope", "created_at", "updated_at", "origin", "payload"}
    if set(document) != expected:
        raise DslValidationError("envelope_fields_invalid")
    if document["schema_version"] != SCHEMA_VERSION:
        raise DslValidationError("unsupported_schema_version")
    kind = document["kind"]
    if not isinstance(kind, str) or kind not in {"goal", "memory", "capability"}:
        raise DslValidationError("unsupported_kind")
    _identifier(document["id"], "id")
    if type(document["revision"]) is not int or document["revision"] < 1:
        raise DslValidationError("revision_invalid")
    scope = document["scope"]
    if not isinstance(scope, dict) or set(scope) != {"project", "account", "visibility"}:
        raise DslValidationError("scope_invalid")
    for key, value in scope.items():
        _identifier(value, "scope." + key)
    if scope["visibility"] not in {"personal", "project", "shared"}:
        raise DslValidationError("scope_visibility_invalid")
    created = _timestamp(document["created_at"], "created_at")
    updated = _timestamp(document["updated_at"], "updated_at")
    if updated < created:
        raise DslValidationError("updated_before_created")
    origin = document["origin"]
    if not isinstance(origin, dict) or set(origin) != {"type", "ref"}:
        raise DslValidationError("origin_invalid")
    if origin["type"] not in {"user", "model", "local_runtime", "import", "plugin"}:
        raise DslValidationError("origin_type_invalid")
    _identifier(origin["ref"], "origin.ref")
    payload = document["payload"]
    if not isinstance(payload, dict):
        raise DslValidationError("payload_must_be_object")
    _finite(document)
    try:
        size = len(json.dumps(document, ensure_ascii=False, allow_nan=False).encode("utf-8"))
    except (TypeError, ValueError, RecursionError) as exc:
        raise DslValidationError("document_not_json") from exc
    if size > MAX_DOCUMENT_BYTES:
        raise DslValidationError("document_too_large")
    if kind == "goal":
        from muse_goals import GoalValidationError, _check_schema

        schema = json.loads(Path(__file__).with_name("muse_goal_schema.json").read_text(encoding="utf-8"))
        try:
            _check_schema(payload, schema)
        except GoalValidationError as exc:
            raise DslValidationError("goal:" + str(exc)) from exc
        if payload["goal_id"] != document["id"] or payload["revision"] != document["revision"]:
            raise DslValidationError("goal_identity_mismatch")
    else:
        from muse_goals import GoalValidationError, _check_schema

        schema = json.loads(Path(__file__).with_name(_SCHEMA_FILES[kind]).read_text(encoding="utf-8"))
        try:
            _check_schema(payload, schema)
        except GoalValidationError as exc:
            raise DslValidationError(kind + ":" + str(exc)) from exc
        if kind == "memory":
            _validate_memory(document)
        else:
            _validate_capability(document)


def _validate_memory(document: Dict[str, Any]) -> None:
    payload = document["payload"]
    for field in ("subject_id", "predicate"):
        _identifier(payload[field], field)
    for source_id in payload["source_ids"]:
        _identifier(source_id, "source_id")
    for relation in payload["relations"]:
        _identifier(relation["target_id"], "relation.target_id")
        if relation["target_id"] == document["id"]:
            raise DslValidationError("self_relation_invalid")
    if payload["deleted"]:
        if payload["value"] or payload["source_ids"] or payload["relations"]:
            raise DslValidationError("deleted_memory_must_be_redacted")
    elif not payload["value"]:
        raise DslValidationError("memory_value_required")
    if not payload["deleted"] and payload["epistemic_type"] in {"fact", "external_claim", "user_statement"} and not payload["source_ids"]:
        raise DslValidationError("source_required")
    _timestamp(payload["observed_at"], "observed_at")
    for field in ("valid_from", "valid_until"):
        if payload[field] is not None:
            _timestamp(payload[field], field)
    if payload["valid_from"] and payload["valid_until"] and (
        _timestamp(payload["valid_until"], "valid_until") < _timestamp(payload["valid_from"], "valid_from")
    ):
        raise DslValidationError("invalid_validity_range")


def _validate_capability(document: Dict[str, Any]) -> None:
    payload = document["payload"]
    if payload["capability_id"] != document["id"] or not _CAPABILITY.fullmatch(payload["capability_id"]):
        raise DslValidationError("capability_identity_mismatch")
    if any(not isinstance(value, str) or not value or len(value) > 160 for value in payload["required_permissions"]):
        raise DslValidationError("permissions_invalid")
    if payload["adapter"] == "eval" or payload["adapter"].startswith("shell"):
        raise DslValidationError("untrusted_adapter")


def goal_document(spec: Dict[str, Any], *, created_at: str, updated_at: str,
                  scope: Dict[str, str] | None = None, origin: Dict[str, str] | None = None) -> Dict[str, Any]:
    document = {
        "schema_version": SCHEMA_VERSION, "kind": "goal", "id": spec["goal_id"],
        "revision": spec["revision"],
        "scope": scope or {"project": "gosim-muse", "account": "local", "visibility": "personal"},
        "created_at": created_at, "updated_at": updated_at,
        "origin": origin or {"type": "local_runtime", "ref": "muse-goal-store"},
        "payload": spec,
    }
    validate_document(document)
    return document
