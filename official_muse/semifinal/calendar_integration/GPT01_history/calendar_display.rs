//! Display only actual Calendar history/results; never infer success from prose.
use serde_json::Value;
use crate::system_chat::model::{Item, ToolStatus, redact_secrets};

fn canonical(name: &str) -> Option<&'static str> {
    match name {
        "calendar.events" | "calendar_events" => Some("calendar.events"),
        "calendar.get_event" | "calendar_get_event" => Some("calendar.get_event"),
        "calendar.add_event" | "calendar_add_event" => Some("calendar.add_event"),
        "calendar.notify" | "calendar_notify" => Some("calendar.notify"), _ => None,
    }
}
fn turn(row: &Value) -> Option<&str> {
    match (row["turn_id"].as_str(), row["thread_id"].as_str()) {
        (Some(a), Some(b)) if a != b => None,
        (Some(a), _) | (_, Some(a)) if !a.is_empty() => Some(a), _ => None,
    }
}
fn valid(receipt: &Value) -> bool {
    receipt["source"] == "broker_tool_result" && receipt["owner"] == "os.calendar"
        && matches!(receipt["caller"].as_str(), Some("muse-goals" | "card.muse-goals"))
        && receipt["tool"].as_str().and_then(canonical).is_some()
        && ["call_id", "tool_call_id", "turn_id", "session_id"].iter().all(|key|
            receipt[*key].as_str().is_some_and(|id| !id.is_empty() && id.len() <= 256
                && !id.chars().any(|c| c.is_control() || c.is_whitespace())))
}
fn state(receipt: &Value, persisted: bool) -> ToolStatus {
    match receipt["terminal"].as_str() {
        Some("error" | "cancelled") => ToolStatus::Failed,
        Some("ok") if persisted && receipt["result"]["ok"] == true
            && receipt["result_omitted"] != true => ToolStatus::Done,
        _ => ToolStatus::Unverified,
    }
}
fn label(receipt: &Value) -> String {
    format!("call_id={} · tool_call_id={} · terminal={}",
        receipt["call_id"].as_str().unwrap_or("[missing]"),
        receipt["tool_call_id"].as_str().unwrap_or("[missing]"),
        receipt["terminal"].as_str().unwrap_or("unverified"))
}
pub(super) fn row_detail(row: &Value, previous: Option<&Item>) -> Option<(ToolStatus, String)> {
    let name = row["tool_name"].as_str().or_else(|| row["name"].as_str()).and_then(canonical)?;
    let body = row["content"].as_str().unwrap_or("");
    let receipt = &row["host_calendar_receipt"];
    let bound = valid(receipt) && receipt["kernel_persisted"] == true
        && turn(row).is_some_and(|t| receipt["turn_id"] == t)
        && receipt["tool_call_id"] == row["tool_call_id"] && receipt["tool"] == name;
    let status = if bound && body.len() <= 16 * 1024 { state(receipt, true) }
        else if matches!(previous, Some(Item::Tool { status: ToolStatus::Failed, .. })) { ToolStatus::Failed }
        else { ToolStatus::Unverified };
    let provenance = if bound { label(receipt) } else { "Host terminal receipt unavailable".to_owned() };
    let body = if body.len() <= 16 * 1024 { body } else { "[result omitted: exceeds 16 KiB]" };
    let prior_failure = match previous {
        Some(Item::Tool { status: ToolStatus::Failed, detail, .. }) if !bound => format!(" · {detail}"),
        _ => String::new(),
    };
    Some((status, redact_secrets(&format!("{provenance}{prior_failure}\n{body}"))))
}
pub(super) fn receipt_item(receipt: &Value) -> Option<(String, String, String, ToolStatus, String)> {
    if !valid(receipt) { return None; }
    let result = if receipt["result_omitted"] == true { "[result omitted: exceeds 16 KiB]".into() }
        else if receipt["result"].is_object() { receipt["result"].to_string() }
        else { "[no tool result]".into() };
    Some((receipt["tool_call_id"].as_str()?.into(), receipt["tool"].as_str()?.into(),
        receipt["turn_id"].as_str()?.into(), state(receipt, false),
        redact_secrets(&format!("Host receipt · {} · History persistence unverified\n{result}", label(receipt)))))
}
