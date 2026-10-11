#[test]
fn gpt01_mutation_history_keeps_pending_rejection_and_exact_success_distinct() {
    for tool in ["calendar.update_event", "calendar.remove_event"] {
        let mut r = row("ok"); r["tool_name"] = json!(tool.replace('.', "_"));
        r["host_calendar_receipt"]["tool"] = json!(tool);
        r["content"] = json!("{\"removed\":true}");
        r["host_calendar_receipt"]["result"]["data"] = json!({"removed":true});
        assert_eq!(row_detail(&r, None).unwrap().0, ToolStatus::Done);
        for terminal in ["awaiting_confirmation", "cancelled", "error"] {
            r["host_calendar_receipt"]["terminal"] = json!(terminal);
            let expected = if terminal == "awaiting_confirmation" { ToolStatus::Unverified } else { ToolStatus::Failed };
            assert_eq!(row_detail(&r, None).unwrap().0, expected);
        }
        r["host_calendar_receipt"]["terminal"] = json!("ok");
        r["host_calendar_receipt"]["tool_call_id"] = json!("other");
        assert_eq!(row_detail(&r, None).unwrap().0, ToolStatus::Unverified);
        r["host_calendar_receipt"]["tool_call_id"] = json!("tc-1");
        assert_eq!(receipt_item(&r["host_calendar_receipt"]).unwrap().3, ToolStatus::Unverified);
    }
}
