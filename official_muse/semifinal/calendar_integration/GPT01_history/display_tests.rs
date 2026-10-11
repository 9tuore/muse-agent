use super::calendar_history::{receipt_item,row_detail};
use crate::system_chat::model::{Item, ToolStatus};
use serde_json::{json, Value};
fn receipt(terminal:&str)->Value { json!({"source":"broker_tool_result","caller":"card.muse-goals",
    "owner":"os.calendar","tool":"calendar.events","session_id":"s1","turn_id":"t1",
    "call_id":"ptc-1","tool_call_id":"tc-1","terminal":terminal,"kernel_persisted":true,
    "result":{"ok":terminal=="ok","data":{"events":[]},"error":{"kind":"not_granted","message":"permission refused"}}}) }
fn row(terminal:&str)->Value { json!({"role":"tool","thread_id":"t1","tool_call_id":"tc-1",
    "tool_name":"calendar_events","content":"{\"events\":[]}","host_calendar_receipt":receipt(terminal)}) }
#[test] fn exact_history_success_and_ids_are_visible() {
    let (status,detail)=row_detail(&row("ok"),None).unwrap();assert_eq!(status,ToolStatus::Done);
    assert!(detail.contains("ptc-1")&&detail.contains("tc-1")&&detail.contains("events"));
}
#[test] fn rejection_cancel_and_missing_receipt_do_not_become_done() {
    for terminal in ["error","cancelled"] { assert_eq!(row_detail(&row(terminal),None).unwrap().0,ToolStatus::Failed); }
    let mut r=row("ok");r.as_object_mut().unwrap().remove("host_calendar_receipt");
    assert_eq!(row_detail(&r,None).unwrap().0,ToolStatus::Unverified);
    let prior=Item::Tool{call_id:"tc-1".into(),name:"calendar.events".into(),turn:Some("t1".into()),seq:None,
        status:ToolStatus::Failed,detail:"cancelled by the person".into()};
    let (state,detail)=row_detail(&r,Some(&prior)).unwrap();assert_eq!(state,ToolStatus::Failed);assert!(detail.contains("cancelled"));
}
#[test] fn wrong_turn_and_tool_cannot_borrow_receipt() {
    let mut r=row("ok");r["turn_id"]=json!("other");assert_eq!(row_detail(&r,None).unwrap().0,ToolStatus::Unverified);
    r["turn_id"]=Value::Null;r["host_calendar_receipt"]["tool_call_id"]=json!("other");assert_eq!(row_detail(&r,None).unwrap().0,ToolStatus::Unverified);
    r["tool_name"]=json!("calendar.remove_event");assert!(row_detail(&r,None).is_none());
}
#[test] fn host_success_without_kernel_row_is_unverified_and_error_preserved() {
    assert_eq!(receipt_item(&receipt("ok")).unwrap().3,ToolStatus::Unverified);
    let (_,_,_,status,detail)=receipt_item(&receipt("error")).unwrap();assert_eq!(status,ToolStatus::Failed);
    assert!(detail.contains("not_granted")&&detail.contains("permission refused"));
}
#[test] fn oversized_result_is_unverified_and_never_partially_shown() {
    let mut r=row("ok");r["content"]=json!("PRIVATE_LONG_CONTENT".repeat(1100));
    let (status,detail)=row_detail(&r,None).unwrap();assert_eq!(status,ToolStatus::Unverified);assert!(!detail.contains("PRIVATE_LONG_CONTENT"));
}
#[test] fn actual_conversation_reload_keeps_body_and_terminal_failure() {
    use super::model::Conversation;
    let mut c=Conversation::new("Muse");
    for _ in 0..2 { c.load_history(&json!([row("error")])); }
    assert_eq!(c.chat.items.len(),1);
    assert!(matches!(&c.chat.items[0],Item::Tool{status:ToolStatus::Failed,detail,..}
        if detail.contains("ptc-1")&&detail.contains("events")));
}
#[test] fn receipt_only_then_persisted_history_does_not_duplicate_a_call() {
    use super::model::Conversation;
    let mut c=Conversation::new("Muse");
    c.load_history(&json!([]));c.load_calendar_receipts(&json!([receipt("ok")]));
    assert!(matches!(&c.chat.items[0],Item::Tool{status:ToolStatus::Unverified,..}));
    c.load_history(&json!([row("ok")]));c.load_calendar_receipts(&json!([receipt("ok")]));
    assert_eq!(c.chat.items.len(),1);assert!(matches!(&c.chat.items[0],Item::Tool{status:ToolStatus::Done,..}));
}
#[test] fn unrelated_tools_keep_existing_history_behavior() {
    use super::model::Conversation;
    let mut c=Conversation::new("News");c.load_history(&json!([{"role":"tool","thread_id":"n1",
        "tool_call_id":"n-call","tool_name":"news.list","content":"unchanged"}]));
    assert!(matches!(&c.chat.items[0],Item::Tool{status:ToolStatus::Done,detail,..} if detail.is_empty()));
}
