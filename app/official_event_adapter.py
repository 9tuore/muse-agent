"""Strict prototype bridge for reviewed Robrix2/OctoSense event envelopes.

This module does not connect to Matrix, Robrix2, or the OctoSense runtime.  It
only validates an event envelope that a separately verified host would provide
and converts it into the local ``LocalAgent`` ``message_event`` contract.

The returned metadata is deliberately explicit:

* ``adapter_status=prototype`` describes this local bridge;
* ``capability_mode=deferred_only`` prevents the envelope from implying a
  direct external capability grant; and
* ``live_status=NOT_LIVE`` records that no official host/backend was exercised.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping


ADAPTER_STATUS = "prototype"
CAPABILITY_MODE = "deferred_only"
LIVE_STATUS = "NOT_LIVE"
ALLOWED_ADAPTERS = {"robrix2_matrix", "octosense_appcard"}
ALLOWED_EVENT_TYPES = {"m.room.message"}
ALLOWED_MSGTYPES = {
    "m.text",
    "rs.robius.robrix.article_app",
    "rs.robius.robrix.mini_app",
}
REQUIRED_MEMBERSHIP = "join"


class OfficialEventAdapterError(ValueError):
    """Raised when an event is not safe to convert into a local message."""


def _require_text(event: Mapping[str, Any], key: str) -> str:
    value = event.get(key)
    if not isinstance(value, str) or not value.strip():
        raise OfficialEventAdapterError(f"{key}_required")
    return value.strip()


def _content(event: Mapping[str, Any]) -> Mapping[str, Any]:
    content = event.get("content", {})
    if content is None:
        content = {}
    if not isinstance(content, Mapping):
        raise OfficialEventAdapterError("content_invalid")
    return content


def _require_common(event: Mapping[str, Any], adapter: str) -> Dict[str, str]:
    if event.get("verified") is not True:
        raise OfficialEventAdapterError("verified_required")
    if event.get("recipient_consent") is not True:
        raise OfficialEventAdapterError("recipient_consent_required")
    membership = event.get("room_membership")
    if membership is None and isinstance(event.get("room"), Mapping):
        membership = event["room"].get("membership")
    if membership != REQUIRED_MEMBERSHIP:
        raise OfficialEventAdapterError("room_membership_join_required")
    transaction_id = _require_text(event, "transaction_id")
    room_id = event.get("room_id")
    if room_id is None and isinstance(event.get("room"), Mapping):
        room_id = event["room"].get("id")
    if not isinstance(room_id, str) or not room_id.strip():
        raise OfficialEventAdapterError("room_id_required")
    sender_id = _require_text(event, "sender_id")
    payload = _content(event)
    event_type = event.get("event_type", event.get("type"))
    if event_type not in ALLOWED_EVENT_TYPES:
        raise OfficialEventAdapterError("event_type_not_allowed")
    msgtype = event.get("msgtype", payload.get("msgtype"))
    if msgtype not in ALLOWED_MSGTYPES:
        raise OfficialEventAdapterError("msgtype_not_allowed")
    body = event.get("body", payload.get("body"))
    if not isinstance(body, str) or not body.strip():
        raise OfficialEventAdapterError("body_required")
    return {
        "transaction_id": transaction_id,
        "room_id": room_id.strip(),
        "sender_id": sender_id,
        "event_type": event_type,
        "msgtype": msgtype,
        "body": body.strip(),
        "adapter": adapter,
    }


def adapt_official_event(event: Mapping[str, Any]) -> Dict[str, Any]:
    """Validate and convert one reviewed host envelope to ``message_event``.

    The adapter intentionally accepts no raw Matrix or AppCard stream.  A
    caller must first label the envelope as one of the two reviewed adapter
    kinds and provide all verification/consent fields.  AppCard results also
    require an approved review and completed phase.
    """

    if not isinstance(event, Mapping):
        raise OfficialEventAdapterError("event_object_required")
    adapter = event.get("adapter")
    if adapter not in ALLOWED_ADAPTERS:
        raise OfficialEventAdapterError("adapter_not_allowed")
    common = _require_common(event, adapter)
    if adapter == "octosense_appcard":
        if event.get("review") != "approved":
            raise OfficialEventAdapterError("appcard_review_required")
        if event.get("phase") != "completed":
            raise OfficialEventAdapterError("appcard_completed_result_required")
        if event.get("deferred_only") is not True:
            raise OfficialEventAdapterError("appcard_deferred_only_required")

    return {
        "type": "message_event",
        "source": "robrix2",
        "adapter_verified": True,
        "adapter_kind": common["adapter"],
        "adapter_status": ADAPTER_STATUS,
        "capability_mode": CAPABILITY_MODE,
        "live_status": LIVE_STATUS,
        "message_id": common["transaction_id"],
        "transaction_id": common["transaction_id"],
        "conversation_id": common["room_id"],
        "sender_id": common["sender_id"],
        "direction": "incoming",
        "text": common["body"],
        "room_membership": REQUIRED_MEMBERSHIP,
        "event_type": common["event_type"],
        "msgtype": common["msgtype"],
        "recipient_consent": True,
    }


def adapter_metadata() -> Dict[str, str]:
    """Expose the bridge boundary for status cards and audit records."""

    return {
        "adapter_status": ADAPTER_STATUS,
        "capability_mode": CAPABILITY_MODE,
        "live_status": LIVE_STATUS,
    }
