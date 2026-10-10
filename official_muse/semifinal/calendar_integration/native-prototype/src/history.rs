//! Display only authoritative tool rows of this context's most recent turn.
use serde_json::Value;

const MAX_ROWS: usize = 4096;
const MAX_BODY_BYTES: usize = 4096;
const MAX_DISPLAY_BYTES: usize = 8192;
const MAX_RECORDS: usize = 4;

fn valid_id(id: &str) -> bool {
    !id.is_empty() && id.len() <= 256 && !id.chars().any(|c| c.is_control() || c.is_whitespace())
}

fn optional_id(value: Option<&Value>) -> Result<Option<&str>, &'static str> {
    match value {
        None | Some(Value::Null) => Ok(None),
        Some(Value::String(id)) if valid_id(id) => Ok(Some(id)),
        _ => Err("回合身份字段类型或内容无效"),
    }
}

pub fn calendar_evidence(history: &Value, turn: &str) -> String {
    match render(history, turn) {
        Ok(text) => text,
        Err(reason) => format!("读取证据不足：{reason}。不能据此认定读取成功或工具未执行。"),
    }
}

fn render(history: &Value, turn: &str) -> Result<String, &'static str> {
    if !valid_id(turn) {
        return Err("缺少有效的回合 ID");
    }
    let rows = history.get("messages").and_then(Value::as_array).ok_or("History 未提供 messages")?;
    if rows.len() > MAX_ROWS {
        return Err("历史行数超过展示上限");
    }
    let mut text = String::from("本 App 最近回合的工具历史正文（不是模型回复；不代表 Relay/Person 验收通过）：\n");
    let mut count = 0;
    for row in rows {
        // Broker merges both lanes. Do not confuse a system-agent lane or old turn.
        if row["role"] != "tool" || row["lane"] != "person" {
            continue;
        }
        let turn_id = optional_id(row.get("turn_id"))?;
        let thread_id = optional_id(row.get("thread_id"))?;
        if matches!((turn_id, thread_id), (Some(a), Some(b)) if a != b) {
            return Err("turn_id 与 thread_id 矛盾");
        }
        // Only a missing/null turn_id permits thread_id fallback.
        let row_turn = turn_id.or(thread_id);
        if row_turn != Some(turn) {
            continue;
        }
        let name = row.get("tool_name").and_then(Value::as_str).ok_or("工具行缺少正式 tool_name")?;
        if name != "calendar.events" {
            continue;
        }
        let id = row.get("tool_call_id").and_then(Value::as_str).filter(|id| !id.is_empty() && id.len() <= 256)
            .ok_or("工具行缺少有效 call_id")?;
        let body = row.get("content").and_then(Value::as_str).filter(|body| !body.is_empty())
            .ok_or("工具行缺少正文")?;
        if body.len() > MAX_BODY_BYTES || count == MAX_RECORDS {
            return Err("工具正文或记录数超过展示上限，未截断为成功证据");
        }
        count += 1;
        text.push_str(&format!("\n回合：{turn}\n调用：{id}\n工具：{name}\n正文：\n{body}\n"));
        if text.len() > MAX_DISPLAY_BYTES {
            return Err("展示字节超过上限");
        }
    }
    if count == 0 {
        return Err("没有找到可关联的 calendar.events 工具正文");
    }
    Ok(text)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn tool() -> Value {
        json!({"role":"tool", "lane":"person", "thread_id":"t1",
               "tool_call_id":"c1", "tool_name":"calendar.events", "content":"{\"events\":[]}"})
    }

    #[test]
    fn exact_tool_body_is_kept_but_assistant_text_is_excluded() {
        let history = json!({"messages":[
            {"role":"assistant", "lane":"person", "thread_id":"t1", "content":"MODEL_CLAIM"}, tool()
        ]});
        let output = render(&history, "t1").unwrap();
        assert!(output.contains("调用：c1"));
        assert!(output.contains("{\"events\":[]}"));
        assert!(!output.contains("MODEL_CLAIM"));
    }

    #[test]
    fn another_turn_or_lane_cannot_supply_current_evidence() {
        let mut old = tool();
        old["thread_id"] = json!("old");
        let mut other_lane = tool();
        other_lane["lane"] = json!("system_agent");
        assert!(render(&json!({"messages":[old, other_lane]}), "t1").is_err());
    }

    #[test]
    fn missing_fields_and_large_body_are_not_accepted() {
        let mut missing = tool();
        missing.as_object_mut().unwrap().remove("tool_call_id");
        assert!(render(&json!({"messages":[missing]}), "t1").is_err());
        let mut large = tool();
        large["content"] = json!("x".repeat(MAX_BODY_BYTES + 1));
        assert!(render(&json!({"messages":[large]}), "t1").is_err());
    }

    #[test]
    fn missing_null_or_matching_ids_preserve_exact_binding() {
        let mut row = tool();
        for turn_id in [Value::Null, json!("t1")] {
            row["turn_id"] = turn_id;
            assert!(render(&json!({"messages":[row.clone()]}), "t1").is_ok());
        }
        row["thread_id"] = Value::Null;
        assert!(render(&json!({"messages":[row]}), "t1").is_ok());
    }

    #[test]
    fn conflicting_or_malformed_identity_never_falls_back() {
        let mut conflict = tool();
        conflict["turn_id"] = json!("t1");
        conflict["thread_id"] = json!("different");
        assert!(render(&json!({"messages":[conflict]}), "t1").is_err());
        for invalid in [json!(7), json!(true), json!([]), json!({}), json!(""),
                        json!(" "), json!("t\n1"), json!("x".repeat(257))] {
            let mut row = tool();
            row["turn_id"] = invalid.clone();
            assert!(render(&json!({"messages":[row]}), "t1").is_err());
            let mut row = tool();
            row["turn_id"] = json!("t1");
            row["thread_id"] = invalid;
            assert!(render(&json!({"messages":[row]}), "t1").is_err());
        }
    }
}
