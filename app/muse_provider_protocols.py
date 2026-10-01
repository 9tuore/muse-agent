"""Verified wire shapes for OpenAI Responses and DeepSeek Chat Completions.

Tool calls are proposals only. The caller must authorize and execute through
the Muse action bus, then send verified results in a separate model request.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, Optional


REASONING_EFFORTS = {
    ("openai_responses", "gpt-6-astra"): ("low", "medium", "high", "xhigh", "max"),
    ("openai_responses", "gpt-6-sol"): ("none", "low", "medium", "high", "xhigh", "max"),
    ("openai_responses", "gpt-6-luna"): ("none", "low", "medium", "high", "xhigh", "max"),
    ("deepseek_chat", "deepseek-flash"): ("none", "low", "high", "max"),
    ("deepseek_chat", "deepseek-v4-pro"): ("none", "low", "high", "max"),
}


def reasoning_efforts(protocol: str, model: str) -> tuple[str, ...]:
    return REASONING_EFFORTS.get((protocol, model), ())


def _tools(tools: Optional[list]) -> list:
    if tools is None:
        return []
    if not isinstance(tools, list) or len(tools) > 8:
        raise ValueError("invalid_model_tools")
    names = set()
    for item in tools:
        if (not isinstance(item, dict) or set(item) != {"name", "description", "parameters"}
                or not isinstance(item["name"], str) or not item["name"].isidentifier()
                or len(item["name"]) > 64 or item["name"] in names
                or not isinstance(item["description"], str)
                or len(item["description"]) > 500
                or not isinstance(item["parameters"], dict)
                or item["parameters"].get("type") != "object"):
            raise ValueError("invalid_model_tools")
        names.add(item["name"])
    return tools


def build_request(protocol: str, model: str, prompt: str, max_tokens: int,
                  require_json: bool, reasoning_effort: Optional[str],
                  tools: Optional[list], stream: bool) -> Dict[str, Any]:
    checked_tools = _tools(tools)
    if checked_tools and stream:
        raise ValueError("streaming_tool_continuation_unsupported")
    if reasoning_effort is not None and reasoning_effort not in reasoning_efforts(protocol, model):
        raise ValueError("reasoning_effort_unsupported")
    if protocol == "openai_responses":
        payload: Dict[str, Any] = {"model": model, "input": prompt,
                                   "max_output_tokens": max_tokens, "store": False}
        if require_json:
            payload["instructions"] = "Return exactly one valid JSON value without Markdown fences."
        if reasoning_effort:
            payload["reasoning"] = {"effort": reasoning_effort}
        if checked_tools:
            payload["tools"] = [dict(type="function", **item) for item in checked_tools]
            payload["include"] = ["reasoning.encrypted_content"]
        if stream:
            payload["stream"] = True
        return payload
    if protocol == "deepseek_chat":
        messages = []
        if require_json:
            messages.append({"role": "system", "content": "Return exactly one valid JSON value without Markdown fences."})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": model, "messages": messages, "max_tokens": max_tokens}
        if require_json:
            payload["response_format"] = {"type": "json_object"}
        if reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort
        if checked_tools:
            payload["tools"] = [{"type": "function", "function": item} for item in checked_tools]
            payload["tool_choice"] = "auto"
        if stream:
            payload["stream"] = True
            payload["stream_options"] = {"include_usage": True}
        return payload
    if reasoning_effort is not None or checked_tools or stream:
        raise ValueError("model_feature_unsupported")
    return {}


def parse_response(protocol: str, body: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(body, dict):
        raise ValueError("invalid_model_response")
    if protocol == "openai_responses":
        if body.get("status") != "completed":
            raise ValueError("model_response_incomplete")
        text_parts = []
        calls = []
        for item in body.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                        text_parts.append(part["text"])
            elif item.get("type") == "function_call":
                calls.append(_call(item.get("call_id"), item.get("name"), item.get("arguments")))
        usage = body.get("usage") or {}
        return {"text": "".join(text_parts), "tool_calls": calls,
                "prompt_tokens": usage.get("input_tokens"),
                "completion_tokens": usage.get("output_tokens"), "model": body.get("model")}
    if protocol == "deepseek_chat":
        choice = body["choices"][0]
        message = choice["message"]
        calls = [_call(item.get("id"), item.get("function", {}).get("name"),
                       item.get("function", {}).get("arguments"))
                 for item in message.get("tool_calls", [])]
        usage = body.get("usage") or {}
        return {"text": message.get("content") or "", "tool_calls": calls,
                "prompt_tokens": usage.get("prompt_tokens"),
                "completion_tokens": usage.get("completion_tokens"),
                "model": body.get("model")}
    raise ValueError("unsupported_model_protocol")


def _call(call_id: Any, name: Any, arguments: Any) -> Dict[str, Any]:
    if (not isinstance(call_id, str) or not call_id or not isinstance(name, str)
            or not name.isidentifier() or not isinstance(arguments, str)
            or len(arguments) > 16384):
        raise ValueError("invalid_model_tool_call")
    parsed = json.loads(arguments)
    if not isinstance(parsed, dict):
        raise ValueError("invalid_model_tool_call")
    return {"call_id": call_id, "name": name, "arguments": parsed}


def followup_request(protocol: str, previous_payload: Dict[str, Any],
                     previous_body: Dict[str, Any], results: list) -> Dict[str, Any]:
    if not isinstance(results, list) or not results or len(results) > 8:
        raise ValueError("invalid_tool_results")
    expected = {call["call_id"] for call in parse_response(protocol, previous_body)["tool_calls"]}
    if len(expected) != len(results) or {item.get("call_id") for item in results
                                         if isinstance(item, dict)} != expected:
        raise ValueError("tool_results_mismatch")
    for item in results:
        if not isinstance(item, dict) or set(item) != {"call_id", "output"}:
            raise ValueError("invalid_tool_results")
        if len(json.dumps(item["output"], ensure_ascii=False)) > 32768:
            raise ValueError("tool_result_too_large")
    payload = dict(previous_payload)
    if protocol == "openai_responses":
        earlier = previous_payload["input"]
        history = earlier if isinstance(earlier, list) else [{"role": "user", "content": earlier}]
        payload["input"] = (history + previous_body["output"]
                            + [{"type": "function_call_output", "call_id": item["call_id"],
                                "output": json.dumps(item["output"], ensure_ascii=False)}
                               for item in results])
    elif protocol == "deepseek_chat":
        payload["messages"] = (previous_payload["messages"]
                               + [previous_body["choices"][0]["message"]]
                               + [{"role": "tool", "tool_call_id": item["call_id"],
                                   "content": json.dumps(item["output"], ensure_ascii=False)}
                                  for item in results])
    else:
        raise ValueError("unsupported_model_protocol")
    return payload


def parse_stream(protocol: str, lines: Iterable[bytes]) -> Dict[str, Any]:
    """Collect bounded SSE to a final response, retaining provider usage."""
    total = 0
    final = None
    text_parts = []
    tools: Dict[int, Dict[str, str]] = {}
    usage = None
    model = None
    for raw in lines:
        total += len(raw)
        if total > 2 * 1024 * 1024:
            raise ValueError("model_stream_too_large")
        if not raw.startswith(b"data:"):
            continue
        data = raw[5:].strip()
        if data == b"[DONE]":
            break
        event = json.loads(data)
        if protocol == "openai_responses":
            if event.get("type") == "response.completed":
                final = event.get("response")
            elif event.get("type") in {"response.failed", "response.incomplete", "error"}:
                raise ValueError("model_stream_failed")
        elif protocol == "deepseek_chat":
            if event.get("model"):
                model = event["model"]
            if isinstance(event.get("usage"), dict):
                usage = event["usage"]
            for choice in event.get("choices", []):
                delta = choice.get("delta") or {}
                if isinstance(delta.get("content"), str):
                    text_parts.append(delta["content"])
                for call in delta.get("tool_calls", []):
                    index = call.get("index")
                    if type(index) is not int or index < 0 or index > 7:
                        raise ValueError("invalid_model_tool_call")
                    entry = tools.setdefault(index, {"id": "", "name": "", "arguments": ""})
                    if call.get("id"):
                        entry["id"] = call["id"]
                    function = call.get("function") or {}
                    entry["name"] += function.get("name") or ""
                    entry["arguments"] += function.get("arguments") or ""
        else:
            raise ValueError("unsupported_model_protocol")
    if protocol == "openai_responses":
        if final is None:
            raise ValueError("model_stream_incomplete")
        return parse_response(protocol, final)
    if usage is None:
        raise ValueError("model_stream_usage_missing")
    return {"text": "".join(text_parts),
            "tool_calls": [_call(item["id"], item["name"], item["arguments"])
                           for _, item in sorted(tools.items())],
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"), "model": model}
