"""Correlate observed Octos AppUI frames with one Muse Goal; grant no authority.

The caller must supply frames from its connected official Octos transport. This
module only records identity evidence. Muse Goal approval and capability
execution remain with GoalStore and ApprovedActionBus.
"""

from __future__ import annotations

import copy
import uuid
from typing import Any, Mapping


class OfficialSessionError(ValueError):
    """An official frame conflicts with the bound Goal or transport state."""


def _text(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise OfficialSessionError(name + "_required")
    return value


class OfficialGoalSession:
    """Track one real session/turn from session/open through its terminal event."""

    def __init__(self, *, goal_id: str, revision: int, plan_digest: str,
                 session_id: str):
        self.goal_id = _text(goal_id, "goal_id")
        if type(revision) is not int or revision < 1:
            raise OfficialSessionError("revision_invalid")
        self.revision = revision
        self.plan_digest = _text(plan_digest, "plan_digest")
        self.session_id = _text(session_id, "session_id")
        self.profile_id: str | None = None
        self.turn_id: str | None = None
        self.turn_started = False
        self.terminal: str | None = None
        self.session_result: dict | None = None
        self.approvals: dict[str, dict] = {}
        self.replay_lossy = False

    def accept_session_open(self, reply: Mapping[str, Any]) -> None:
        result = reply.get("result") if isinstance(reply, Mapping) else None
        opened = result.get("opened") if isinstance(result, Mapping) else None
        if not isinstance(opened, Mapping) or opened.get("session_id") != self.session_id:
            raise OfficialSessionError("session_open_mismatch")
        profile_id = _text(opened.get("active_profile_id"), "active_profile_id")
        if self.profile_id is not None and self.profile_id != profile_id:
            raise OfficialSessionError("session_profile_changed")
        self.profile_id = profile_id

    def accept_turn_start(self, turn_id: str, reply: Mapping[str, Any]) -> None:
        if self.profile_id is None or self.turn_id is not None:
            raise OfficialSessionError("turn_start_out_of_order")
        try:
            uuid.UUID(turn_id)
        except (TypeError, ValueError, AttributeError) as exc:
            raise OfficialSessionError("turn_id_invalid") from exc
        if not isinstance(reply, Mapping) or reply.get("result") != {"accepted": True}:
            raise OfficialSessionError("turn_not_accepted")
        self.turn_id = turn_id

    def observe(self, frame: Mapping[str, Any]) -> str:
        if not isinstance(frame, Mapping):
            raise OfficialSessionError("frame_invalid")
        method, params = frame.get("method"), frame.get("params")
        if not isinstance(method, str) or not isinstance(params, Mapping):
            raise OfficialSessionError("notification_invalid")
        if params.get("session_id") != self.session_id:
            return "OTHER_SESSION"
        if method == "protocol/replay_lossy":
            self.replay_lossy = True
            return "REPLAY_LOSSY"
        tracked = {"turn/started", "turn/completed", "turn/error", "approval/requested",
                   "approval/decided", "approval/cancelled"}
        if method not in tracked:
            return "IGNORED"
        if self.turn_id is None or params.get("turn_id") != self.turn_id:
            raise OfficialSessionError("turn_mismatch")
        if method == "turn/started":
            if self.terminal is not None:
                raise OfficialSessionError("turn_already_terminal")
            self.turn_started = True
            return "TURN_STARTED"
        if not self.turn_started:
            raise OfficialSessionError("turn_not_started")
        if method in {"turn/completed", "turn/error"}:
            terminal = "COMPLETED" if method == "turn/completed" else "ERROR"
            if self.terminal is not None and self.terminal != terminal:
                raise OfficialSessionError("conflicting_terminal")
            parsed_result = None
            if terminal == "COMPLETED":
                result = params.get("session_result")
                if isinstance(result, Mapping) and isinstance(result.get("message_id"), str) and \
                        result["message_id"] and type(result.get("committed_seq")) is int and \
                        result["committed_seq"] >= 0:
                    parsed_result = {"message_id": result["message_id"],
                                     "committed_seq": result["committed_seq"]}
            if self.terminal is not None and self.session_result != parsed_result:
                raise OfficialSessionError("conflicting_terminal_result")
            self.terminal = terminal
            self.session_result = parsed_result
            return "TURN_" + terminal
        approval_id = _text(params.get("approval_id"), "approval_id")
        try:
            uuid.UUID(approval_id)
        except (ValueError, AttributeError) as exc:
            raise OfficialSessionError("approval_id_invalid") from exc
        if method == "approval/requested":
            tool_name = _text(params.get("tool_name"), "tool_name")
            if approval_id in self.approvals:
                if self.approvals[approval_id]["tool_name"] != tool_name:
                    raise OfficialSessionError("conflicting_approval_request")
                return "APPROVAL_REQUESTED"
            if self.terminal is not None:
                raise OfficialSessionError("approval_after_terminal")
            self.approvals[approval_id] = {"tool_name": tool_name,
                                           "decision": None, "client_response": False}
            return "APPROVAL_REQUESTED"
        approval = self.approvals.get(approval_id)
        if approval is None:
            raise OfficialSessionError("approval_not_requested")
        if method == "approval/cancelled":
            if approval["decision"] not in {None, "cancelled"}:
                raise OfficialSessionError("approval_already_decided")
            if self.terminal is not None and approval["decision"] != "cancelled":
                raise OfficialSessionError("approval_after_terminal")
            approval["decision"] = "cancelled"
            return "APPROVAL_CANCELLED"
        decision = params.get("decision")
        if decision not in {"approve", "deny"} or approval["decision"] not in {None, decision}:
            raise OfficialSessionError("approval_decision_invalid")
        client_response = params.get("auto_resolved") is False and \
            bool(_text(params.get("decided_by"), "decided_by"))
        if approval["decision"] is not None and approval["client_response"] != client_response:
            raise OfficialSessionError("conflicting_approval_decision")
        if self.terminal is not None and approval["decision"] is None:
            raise OfficialSessionError("approval_after_terminal")
        approval["decision"] = decision
        approval["client_response"] = client_response
        return "APPROVAL_DECIDED"

    def evidence(self) -> dict:
        return {"goal_id": self.goal_id, "revision": self.revision,
                "plan_digest": self.plan_digest, "official_session_id": self.session_id,
                "official_profile_id": self.profile_id, "official_turn_id": self.turn_id,
                "official_terminal": self.terminal, "official_session_result": self.session_result,
                "official_approvals": copy.deepcopy(self.approvals), "replay_lossy": self.replay_lossy,
                "client_approval_observed": not self.replay_lossy and any(
                    value["decision"] == "approve" and value["client_response"]
                    for value in self.approvals.values()),
                # A client can call approval/respond without a user gesture.
                # The official wire therefore cannot attest human approval.
                "manual_approval_observed": False,
                "authority": "NONE"}
