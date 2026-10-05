"""Deterministic synthetic profiles; no private runtime or build-output dependency."""
import copy
import hashlib
import json
from pathlib import Path


def encoded(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def profile(case):
    if case not in ("linked63_dense", "linked64", "linked63_completed_dense"):
        raise ValueError("Unsupported receipt fixture")
    template = json.loads(Path(__file__).with_name("fixtures").joinpath("receipt-template.json").read_text())
    count = 64 if case == "linked64" else 63
    memory = {"schema": 1, "claims": [], "sources": [], "forget": []}
    for n in range(count):
        source, claim = copy.deepcopy(template["source"]), copy.deepcopy(template["claim"])
        value = f"合成收件恢复容量记录{n}"
        sid = "a2-mail-source" if n == 0 else "source:calendar:a2-calendar-run" if n == 1 else f"a2-source-{n}"
        source.update(source_id=sid, locator=f"a2-synthetic:receipt:{n}", support_excerpt=value,
                      content_sha256=hashlib.sha256(value.encode()).hexdigest())
        source["scope"].update(account="synthetic-account", project_id="a2-project", owner_id="a2-owner")
        claim["document"].update(id=f"a2-memory-{n}", scope=copy.deepcopy(source["scope"]))
        claim["document"]["payload"].update(subject_id=f"a2-subject-{n}", value=value, source_ids=[sid])
        claim["source_history"] = [sid]
        if case == "linked64" and n == 63:
            claim["document"]["id"] = "memory:result:a2-run"
            claim["document"]["payload"].update(subject_id="a2-goal", predicate="verified_result")
        memory["sources"].append(source)
        memory["claims"].append(claim)
    goal = dict(id="a2-goal", version=1, status="running", archived=False, updated_at=1,
                project_id="a2-project", owner_id="a2-owner", result_path="results/a2-linked.json")
    run = dict(id="a2-run", goal_id="a2-goal", plan_revision=1, status="running",
               result_path=goal["result_path"], started_at=1, finished_at=0, request_id="a2-mail-request")
    action = dict(id="a2-mail-request", goal_id="a2-goal", run_id="a2-run", plan_revision=1,
                  service="mail.send", target_scope="synthetic-account", status="accepted", started_at=1,
                  finished_at=2, payload_json=encoded(dict(to="self@example.invalid", subject="MUSE-R2-A2-RECEIPT")))
    goals = dict(schema=2, goals=[goal], runs=[run], actions=[action], selected_id="a2-goal")
    if case.endswith("_dense"):
        for n in range(1, 32):
            goals["goals"].append(dict(goal, id=f"a2-historical-goal-{n}", status="completed", result_path=f"results/a2-historical-{n}.json"))
        for n in range(1, 128):
            gid, rid, aid = f"a2-historical-goal-{1+n%31}", f"a2-historical-run-{n}", f"a2-historical-request-{n}"
            goals["runs"].append(dict(run, id=rid, goal_id=gid, status="completed", request_id=aid, finished_at=2))
            goals["actions"].append(dict(action, id=aid, goal_id=gid, run_id=rid, status="verified"))
    draft = dict(account="synthetic-account", to="self@example.invalid", subject="MUSE-R2-A2-RECEIPT 合成收件声明",
                 body="这是独立 fixture 合成邮件，没有实际投递。", status="accepted", preview="", attempt="a2-attempt",
                 request_id="a2-mail-request", accepted_at=2, verified_at=0, verified_id="", link_goal_id="a2-goal",
                 link_event_id="a2-event", link_run_id="a2-run", incoming_key="")
    sessions = [dict(id=f"a2-chat-{n}", title=f"合成对话{n}", created_at=1, updated_at=1,
                     focus_project="a2-project", focus_owner="a2-owner", goal_id="", proposals=[],
                     messages=[dict(role="user", text=f"合成用户消息{n}", state="success", at=1),
                               dict(role="assistant", text=f"合成助手消息{n}", state="success", at=1)]) for n in range(16)]
    link = dict(goal_id="a2-goal", account_id="synthetic-account", message_id="a2-mail-message", source_id="a2-mail-source",
                source_claim_id="a2-memory-0", status="verified", event_id="a2-event", calendar_id="a2-calendar",
                run_id="a2-calendar-run", candidate_revision=1, candidate=dict(title="合成日程", start="2026-10-06T15:00:00+08:00",
                end="2026-10-06T16:00:00+08:00", time_zone="Asia/Shanghai", location="合成地点"))
    return {"memory.json": memory, "global-memory-settings.json": dict(schema=1, enabled=True,
            user_id=template["source"]["scope"]["user_id"], forget_pending=False), "goals.json": goals, "mail-draft.json": draft,
            "chat-sessions.json": dict(schema=1, selected_id="a2-chat-0", sessions=sessions),
            "activity.json": [dict(kind="synthetic_seed", detail=f"合成初始事件{n}", at=1) for n in range(8)],
            "calendar-state.json": dict(schema=1, links=[link], receipts=[], local_states=[])}
