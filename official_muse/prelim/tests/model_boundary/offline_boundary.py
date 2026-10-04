#!/usr/bin/env python3
"""Source-bound Python fixtures, not execution of the Rust SDK or a live model.

`legacy` mirrors the inspected OpenAI path. `candidate` is an explicit proposed
policy: one Host-owned format retry, no unknown-result transport fallback,
strict usage completeness, unchanged reply schema. No network or account I/O.
"""
import argparse
import hashlib
import json
from pathlib import Path

SDK_SHA = {
    "mod.rs": "6e3a8a1287b2a253eda3fd69c4aa9c9bd46141079c7533bd6f2119dc4b409075",
    "wire.rs": "3af912428fdef0a1ea086076e3f328a339aadb878a9ad86b42ac988d3b594dd2",
    "schema.rs": "6a4ade8e629c6f46f01150c019a382e92d2bff6b2c1cb3a3e06a09e7756ea2d7",
    "ledger.rs": "b619ab20e7f4a15f8d4c3983958acba8a255df1fc8570fb22fb9f97ff04eaaa0",
}
REPLY_MAX = 1200  # main.splash:6258, Unicode scalars, not UTF-8 bytes.
OUTPUT_MAX = 16384  # complete/mod.rs:91, after unwrap_json.


def unwrap(text):
    text = text.strip()
    if text.startswith("<think>") and "</think>" in text:
        text = text.split("</think>", 1)[1].strip()
    if text.startswith("```"):
        rest = text[3:]
        for prefix in ("json", "JSON"):
            if rest.startswith(prefix):
                rest = rest[len(prefix):]
                break
        if rest.rstrip().endswith("```"):
            return rest.rstrip()[:-3].strip()
    return text


def accept(text):
    """Only the verified Muse plain-chat schema subset, with its existing cap."""
    text = unwrap(text)
    if len(text.encode()) > OUTPUT_MAX:
        return "OUTPUT_TOO_LARGE"
    try:
        value = json.loads(text)
    except ValueError:
        return "MODEL_NON_JSON"
    if (type(value) is not dict or set(value) != {"reply"}
            or type(value["reply"]) is not str or len(value["reply"]) > REPLY_MAX):
        return "SCHEMA_MISMATCH"
    if any(part in value["reply"].lower() for part in ("http://", "https://", "www.")):
        return "URL_REJECTED"
    return "VALID"


def envelope(content, *, finish="stop", refusal=None, usage=True, **tokens):
    body = {"choices": [{"message": {"content": content}, "finish_reason": finish}]}
    if refusal is not None:
        body["choices"][0]["message"]["refusal"] = refusal
    if usage:
        body["usage"] = {"prompt_tokens": 17, "completion_tokens": 9, **tokens}
    return {"status": 200, "body": body}


def decode(event, strict):
    """OpenAI-only fixture extraction. Provider metadata is synthetic here."""
    if "transport_error" in event:
        return event["transport_error"], None, None
    if not 200 <= event["status"] < 300:
        return "PROVIDER_HTTP_ERROR", None, None
    body = event["body"]
    if type(body) is not dict:
        return "PROVIDER_NON_JSON", None, None
    raw = body.get("usage", {})
    if type(raw) is not dict:
        raw = {}
    inp, out = raw.get("prompt_tokens"), raw.get("completion_tokens")
    inp_ok = type(inp) is int and 0 <= inp <= 2**64-1
    out_ok = type(out) is int and 0 <= out <= 2**64-1
    used = (inp, out if out_ok else 0) if inp_ok and (out_ok or not strict) else None
    choices = body.get("choices")
    choice = choices[0] if type(choices) is list and choices and type(choices[0]) is dict else {}
    message = choice.get("message", {})
    if type(message) is not dict:
        message = {}
    text = message.get("content")
    if strict and (message.get("refusal") or choice.get("finish_reason") == "content_filter"):
        return "LEGAL_REFUSAL", used, None
    if strict and choice.get("finish_reason") == "length":
        return "TRUNCATED", used, None
    if type(text) is not str or not text.strip():
        return "EMPTY_OUTPUT", used if strict else None, None
    return accept(text), used, text


def run(events_by_provider, *, candidate=False, retry_budget=True, external_actions=0,
        current=True, permission=True, unknown_before=False):
    """Two explicitly different fixture flows; neither claims to run production."""
    posts, ledger_tokens, usage_in, usage_out = 0, 0, 0, 0
    all_known, format_retries = True, 0
    output, reported_attempts, result = None, None, "PROVIDER_ERROR"
    if candidate and (unknown_before or not current or not permission):
        return {"classification": "PRE_SEND_BLOCKED", "posts": 0, "format_retries": 0,
                "logical_calls": 0, "known_usage": False, "usage": None, "ledger_tokens": 0,
                "callback_meta": None, "reported_attempts": None, "external_actions": external_actions}
    for events in events_by_provider:
        for attempt in (1, 2):
            if attempt > len(events):
                event = {"transport_error": "NETWORK_UNKNOWN"}
            else:
                event = events[attempt-1]
            posts += 1
            result, used, text = decode(event, strict=candidate)
            send_failed = result in {"NETWORK_UNKNOWN", "NETWORK_TIMEOUT", "PROVIDER_HTTP_ERROR",
                                     "PROVIDER_NON_JSON", "EMPTY_OUTPUT"}
            if used is not None:
                usage_in += used[0]
                usage_out += used[1]
                if candidate or not send_failed:
                    ledger_tokens += used[0] + used[1]
            else:
                if candidate or not send_failed:
                    all_known = False
                if text is not None and not send_failed:
                    # Synthetic byte fallback illustrates estimated=true only.
                    estimated_input = len("fixture system".encode())//3
                    estimated_output = len(text.encode())//3
                    usage_in += estimated_input
                    usage_out += estimated_output
                    ledger_tokens += estimated_input + estimated_output
            if not candidate and send_failed:
                break  # Inspected SDK moves to the next provider.
            if result == "VALID":
                output = json.loads(unwrap(text))
                reported_attempts = posts if candidate else attempt
                break
            safe_retry = (result in {"MODEL_NON_JSON", "SCHEMA_MISMATCH"} and all_known
                          and retry_budget and not external_actions and current and permission)
            if candidate and (format_retries >= 1 or not safe_retry):
                break
            if not candidate and attempt == 2:
                break
            format_retries += 1
        if candidate or output is not None or not send_failed:
            break
    known = all_known and (candidate or output is not None)
    meta_present = known if candidate else output is not None
    meta = {"input_tokens": usage_in, "output_tokens": usage_out, "estimated": not all_known} if meta_present else None
    return {"classification": result, "posts": posts, "format_retries": format_retries,
            "logical_calls": 1, "known_usage": known, "usage": meta,
            "ledger_tokens": ledger_tokens, "callback_meta": meta,
            "reported_attempts": reported_attempts, "external_actions": external_actions}


def fixtures():
    good = envelope('{"reply":"合成内容甲"}')
    bad = envelope("synthetic non-JSON reply")
    schema_bad = envelope('{"reply":7}')
    rows = []

    def check(name, providers, expected, **options):
        result = run(providers, **options)
        for key, value in expected.items():
            assert result[key] == value, (name, key, result[key], value)
        rows.append({"id": name, "result": result, "assertions": len(expected), "status": "PASS"})

    check("legacy_schema_failure", [[schema_bad, schema_bad]],
          {"posts": 2, "logical_calls": 1, "ledger_tokens": 52, "known_usage": False, "callback_meta": None})
    check("legacy_format_repair", [[bad, good]], {"posts": 2, "format_retries": 1, "reported_attempts": 2, "known_usage": True})
    check("legacy_refusal_loses_usage", [[envelope(None, refusal="Synthetic safe refusal")]],
          {"posts": 1, "ledger_tokens": 0, "known_usage": False})
    check("legacy_truncated_valid_json_is_accepted", [[envelope('{"reply":"synthetic"}', finish="length")]],
          {"classification": "VALID", "posts": 1})
    fallback = [[bad, {"transport_error": "NETWORK_TIMEOUT"}], [bad, good]]
    check("legacy_provider_reset_and_attempt_underreport", fallback,
          {"posts": 4, "format_retries": 2, "reported_attempts": 2, "known_usage": True})
    incomplete = envelope('{"reply":"synthetic"}');del incomplete["body"]["usage"]["completion_tokens"]
    check("legacy_missing_output_claims_nonestimated_zero", [[incomplete]],
          {"known_usage": True, "usage": {"input_tokens": 17, "output_tokens": 0, "estimated": False}})
    check("candidate_valid", [[good]], {"posts": 1, "known_usage": True, "classification": "VALID"}, candidate=True)
    check("candidate_safe_format_repair", [[bad, good]],
          {"posts": 2, "format_retries": 1, "ledger_tokens": 52, "known_usage": True}, candidate=True)
    check("candidate_schema_repair", [[schema_bad, good]], {"posts": 2, "format_retries": 1}, candidate=True)
    check("candidate_repeat_schema_failure_keeps_known_failure_usage", [[schema_bad, schema_bad]],
          {"classification": "SCHEMA_MISMATCH", "posts": 2, "known_usage": True, "ledger_tokens": 52}, candidate=True)
    check("candidate_retry_cannot_reset_on_provider_fallback", fallback,
          {"posts": 2, "format_retries": 1, "known_usage": False, "classification": "NETWORK_TIMEOUT"}, candidate=True)
    check("candidate_provider_refusal", [[envelope(None, refusal="Synthetic safe refusal"), good]],
          {"classification": "LEGAL_REFUSAL", "posts": 1, "format_retries": 0, "known_usage": True}, candidate=True)
    check("candidate_content_filter", [[envelope(None, finish="content_filter"), good]],
          {"classification": "LEGAL_REFUSAL", "posts": 1}, candidate=True)
    check("candidate_truncated_invalid_json", [[envelope('{"reply":', finish="length"), good]],
          {"classification": "TRUNCATED", "posts": 1, "known_usage": True}, candidate=True)
    check("candidate_truncated_complete_json", [[envelope('{"reply":"synthetic"}', finish="length"), good]],
          {"classification": "TRUNCATED", "posts": 1}, candidate=True)
    check("candidate_timeout_unknown", [[{"transport_error": "NETWORK_TIMEOUT"}, good]],
          {"classification": "NETWORK_TIMEOUT", "posts": 1, "known_usage": False}, candidate=True)
    check("candidate_http_error", [[{"status": 429, "body": {"error": "synthetic"}}, good]],
          {"classification": "PROVIDER_HTTP_ERROR", "posts": 1, "known_usage": False}, candidate=True)
    check("candidate_provider_envelope_nonjson", [[{"status": 200, "body": "not JSON"}, good]],
          {"classification": "PROVIDER_NON_JSON", "posts": 1, "known_usage": False}, candidate=True)
    check("candidate_no_usage_no_paid_retry", [[envelope("bad", usage=False), good]],
          {"posts": 1, "known_usage": False, "format_retries": 0}, candidate=True)
    check("candidate_missing_output_not_known", [[incomplete]], {"known_usage": False, "usage": None}, candidate=True)
    negative = envelope('{"reply":"synthetic"}', completion_tokens=-1)
    check("candidate_negative_usage_not_known", [[negative]], {"known_usage": False}, candidate=True)
    boolean = envelope('{"reply":"synthetic"}', prompt_tokens=True)
    check("candidate_boolean_usage_not_known", [[boolean]], {"known_usage": False}, candidate=True)
    check("candidate_no_budget_no_retry", [[bad, good]], {"posts": 1, "format_retries": 0}, candidate=True, retry_budget=False)
    check("candidate_existing_unknown_prevents_send", [[good]], {"posts": 0, "logical_calls": 0}, candidate=True, unknown_before=True)
    check("candidate_stale_identity_prevents_send", [[good]], {"posts": 0}, candidate=True, current=False)
    check("candidate_permission_rejection_prevents_send", [[good]], {"posts": 0}, candidate=True, permission=False)
    check("candidate_prior_external_action_prevents_retry", [[bad, good]], {"posts": 1, "format_retries": 0}, candidate=True, external_actions=1)
    check("candidate_unwanted_url_not_repaired", [[envelope('{"reply":"https://example.invalid"}'), good]],
          {"classification": "URL_REJECTED", "posts": 1}, candidate=True)
    check("candidate_oversized_output_not_repaired", [[envelope('"' + 'x'*OUTPUT_MAX + '"'), good]],
          {"classification": "OUTPUT_TOO_LARGE", "posts": 1}, candidate=True)
    check("candidate_missing_required", [[envelope('{}'), good]], {"posts": 2, "format_retries": 1}, candidate=True)
    check("candidate_additional_property_not_accepted", [[envelope('{"reply":"x","sent":true}'), schema_bad]],
          {"classification": "SCHEMA_MISMATCH", "posts": 2}, candidate=True)
    check("candidate_unicode_scalars_at_cap", [[envelope(json.dumps({"reply": "界"*REPLY_MAX}, ensure_ascii=False))]],
          {"classification": "VALID", "posts": 1}, candidate=True)
    check("candidate_unicode_over_cap_not_silently_truncated", [[envelope(json.dumps({"reply": "界"*(REPLY_MAX+1)}, ensure_ascii=False)), schema_bad]],
          {"classification": "SCHEMA_MISMATCH", "posts": 2}, candidate=True)
    check("candidate_legal_refusal_inside_valid_schema", [[envelope('{"reply":"资料不足，不能确定。"}')]],
          {"classification": "VALID", "posts": 1, "format_retries": 0}, candidate=True)
    check("candidate_code_fence_and_think_supported", [[envelope('<think>synthetic</think>\n```json\n{"reply":"fixture"}\n```')]],
          {"classification": "VALID", "posts": 1}, candidate=True)
    check("candidate_semantic_claim_is_not_external_execution", [[envelope('{"reply":"已修改日历"}')]],
          {"classification": "VALID", "posts": 1, "external_actions": 0}, candidate=True)
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    hashes = {name: hashlib.sha256((args.sdk_root/name).read_bytes()).hexdigest() for name in SDK_SHA}
    assert hashes == SDK_SHA, "SDK changed: re-inspect before interpreting fixture evidence"
    rows = fixtures()
    report = {"kind": "FIXTURE_PYTHON_SOURCE_BOUND_NOT_RUST_NOT_LIVE", "status": "PASS",
              "cases": rows, "passed": len(rows), "assertions": sum(r["assertions"] for r in rows),
              "sdk_sha256": hashes, "fixture_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "paid_calls": 0, "network_calls": 0, "external_actions_created": 0,
              "candidate_is_proposed_only": True,
              "limits": "OpenAI fixture and plain-chat reply schema subset only; no Rust build, SDK runtime, provider, semantic or full-chain success claim."}
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: report[k] for k in ("kind", "status", "passed", "assertions", "paid_calls")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
