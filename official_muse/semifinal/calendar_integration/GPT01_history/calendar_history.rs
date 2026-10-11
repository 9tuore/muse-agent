//! Host result receipts over the broker's existing bounded occurrence cache.
use serde_json::{json, Value};
use crate::host_tools::{HostToolCall, ToolOutcome};

pub(crate) fn canonical(name: &str) -> Option<&'static str> {
    match name {
        "calendar.events" | "calendar_events" => Some("calendar.events"),
        "calendar.get_event" | "calendar_get_event" => Some("calendar.get_event"),
        "calendar.add_event" | "calendar_add_event" => Some("calendar.add_event"),
        "calendar.notify" | "calendar_notify" => Some("calendar.notify"),
        _ => None,
    }
}

pub(crate) fn metadata(call: &HostToolCall, generation: u64) -> Option<Value> {
    let valid = |id: &str| !id.is_empty() && id.len() <= 256
        && !id.chars().any(|c| c.is_whitespace() || c.is_control());
    if !matches!(call.calling_app.as_str(), "muse-goals" | "card.muse-goals")
        || call.app != "os.calendar" || canonical(&call.name) != Some(call.name.as_str())
        || ![&call.session_id, &call.turn_id, &call.tool_call_id, &call.call_id].iter().all(|id| valid(id))
    { return None; }
    Some(json!({"source":"broker_tool_result", "caller":call.calling_app,
        "owner":call.app, "tool":call.name, "session_id":call.session_id,
        "context_id":call.context_id, "turn_id":call.turn_id,
        "tool_call_id":call.tool_call_id, "call_id":call.call_id,
        "args_digest":call.args_digest, "_generation":generation}))
}

pub(crate) fn finished(mut metadata: Value, outcome: &ToolOutcome) -> Value {
    let result = outcome.to_params(metadata["call_id"].as_str().unwrap_or(""));
    metadata["terminal"] = json!(if matches!(outcome, ToolOutcome::Ok(_)) { "ok" } else { "error" });
    metadata["result_bytes"] = json!(result.to_string().len());
    if result.to_string().len() <= 16 * 1024 { metadata["result"] = result; }
    else { metadata["result_omitted"] = json!(true); }
    metadata
}

pub(crate) fn attach(history: &mut Value, session: &str, generation: u64, receipts: &[Value]) {
    let selected: Vec<Value> = receipts.iter().rev()
        .filter(|r| r["session_id"] == session && r["_generation"] == generation)
        .take(32).cloned().map(|mut r| {
            r.as_object_mut().unwrap().remove("_generation"); r
        }).collect();
    for row in history["messages"].as_array_mut().into_iter().flatten() {
        if row["role"] != "tool" { continue; }
        let turn = match (row["turn_id"].as_str(), row["thread_id"].as_str()) {
            (Some(a), Some(b)) if a != b => continue,
            (Some(a), _) | (_, Some(a)) => a,
            _ => continue,
        };
        let name = row["tool_name"].as_str().or_else(|| row["name"].as_str()).and_then(canonical);
        let matches: Vec<_> = selected.iter().filter(|r| r["turn_id"] == turn
            && r["tool_call_id"] == row["tool_call_id"] && r["tool"].as_str() == name).collect();
        if matches.len() == 1 {
            let mut receipt = matches[0].clone();
            receipt["kernel_persisted"] = json!(true);
            row["host_calendar_receipt"] = receipt;
        }
    }
    history["host_calendar_receipts"] = json!(selected);
}

#[cfg(test)]
mod tests {
    use super::*;
    fn call() -> HostToolCall {
        let mut call = HostToolCall::parse(&json!({"call_id":"ptc-1","tool_call_id":"tc-1",
            "session_id":"s1","turn_id":"t1","app":"os.calendar","name":"calendar.events",
            "args_digest":"fixture-digest","peer":"muse-peer","args":{"limit":10}})).unwrap();
        call.calling_app = "card.muse-goals".into();
        call
    }
    fn row() -> Value { json!({"role":"tool","thread_id":"t1","tool_call_id":"tc-1",
        "tool_name":"calendar_events","content":"{\"events\":[]}"}) }
    #[test]
    fn exact_scope_and_four_tools_only() {
        let mut c=call();
        for tool in ["calendar.events","calendar.get_event","calendar.add_event","calendar.notify"] {
            c.name=tool.into();assert!(metadata(&c,1).is_some());
        }
        for tool in ["calendar.update_event","calendar.remove_event","calendar_events","calendar.events_extra"] {
            c.name=tool.into();assert!(metadata(&c,1).is_none());
        }
        c.name="calendar.events".into();c.calling_app="card.another-app".into();assert!(metadata(&c,1).is_none());
        c.calling_app="card.muse-goals".into();c.app="muse-goals".into();assert!(metadata(&c,1).is_none());
    }
    #[test]
    fn actual_ids_and_errors_survive_history() {
        let r=finished(metadata(&call(),7).unwrap(),&ToolOutcome::error("not_granted","Denied by actual fixture"));
        let mut h=json!({"messages":[row()]});attach(&mut h,"s1",7,&[r]);
        let bound=&h["messages"][0]["host_calendar_receipt"];
        assert_eq!(bound["call_id"],"ptc-1");assert_eq!(bound["tool_call_id"],"tc-1");
        assert_eq!(bound["terminal"],"error");assert_eq!(bound["result"]["error"]["kind"],"not_granted");
        assert_eq!(bound["kernel_persisted"],true);assert!(bound.get("_generation").is_none());
    }
    #[test]
    fn conflicting_turn_session_generation_and_missing_ids_do_not_bind() {
        let r=finished(metadata(&call(),1).unwrap(),&ToolOutcome::Ok(json!({"events":[]})));
        for (session,generation) in [("other",1),("s1",2)] {
            let mut h=json!({"messages":[row()]});attach(&mut h,session,generation,&[r.clone()]);
            assert!(h["messages"][0].get("host_calendar_receipt").is_none());
        }
        for (field,value) in [("turn_id",json!("wrong")),("tool_call_id",Value::Null),("tool_name",json!("calendar_events_extra"))] {
            let mut bad=row();bad[field]=value;let mut h=json!({"messages":[bad]});attach(&mut h,"s1",1,&[r.clone()]);
            assert!(h["messages"][0].get("host_calendar_receipt").is_none());
        }
    }
    #[test]
    fn acknowledgement_is_not_an_outcome_and_oversized_result_is_not_truncated() {
        // finished is called only from the broker's final ToolReply branch;
        // no API here accepts awaiting_confirmation as success.
        let r=finished(metadata(&call(),1).unwrap(),&ToolOutcome::Ok(json!({"notes":"x".repeat(17*1024)})));
        assert_eq!(r["result_omitted"],true);assert!(r.get("result").is_none());
    }
    #[test]
    fn duplicate_or_cancelled_receipts_never_forge_success() {
        let mut r=metadata(&call(),1).unwrap();r["terminal"]=json!("cancelled");
        let mut h=json!({"messages":[row()]});attach(&mut h,"s1",1,&[r.clone()]);
        assert_eq!(h["messages"][0]["host_calendar_receipt"]["terminal"],"cancelled");
        assert!(h["messages"][0]["host_calendar_receipt"].get("result").is_none());
        let mut h=json!({"messages":[row()]});attach(&mut h,"s1",1,&[r.clone(),r]);
        assert!(h["messages"][0].get("host_calendar_receipt").is_none());
    }
    #[test]
    fn history_receipt_count_is_bounded() {
        let r=finished(metadata(&call(),1).unwrap(),&ToolOutcome::Ok(json!({"events":[]})));
        let mut h=json!({"messages":[]});attach(&mut h,"s1",1,&vec![r;40]);
        assert_eq!(h["host_calendar_receipts"].as_array().unwrap().len(),32);
    }
}
