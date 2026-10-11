#[test]
fn gpt01_mutation_receipts_bind_only_exact_terminal_calls() {
    for tool in ["calendar.update_event", "calendar.remove_event"] {
        let mut c = call(); c.name = tool.into();
        let receipt = finished(metadata(&c, 3).unwrap(), &ToolOutcome::Ok(json!({"removed":true})));
        let mut r = row(); r["tool_name"] = json!(tool.replace('.', "_"));
        let mut h = json!({"messages":[r.clone()]}); attach(&mut h, "s1", 3, &[receipt.clone()]);
        assert_eq!(h["messages"][0]["host_calendar_receipt"]["terminal"], "ok");
        assert_eq!(h["messages"][0]["host_calendar_receipt"]["tool"], tool);
        r["tool_call_id"] = json!("different-call");
        let mut h = json!({"messages":[r]}); attach(&mut h, "s1", 3, &[receipt]);
        assert!(h["messages"][0].get("host_calendar_receipt").is_none());
        let rejected = finished(metadata(&c, 3).unwrap(), &ToolOutcome::error("declined", "fixture physical approval declined"));
        assert_eq!(rejected["terminal"], "error");
        assert_eq!(rejected["result"]["error"]["kind"], "declined");
    }
}
