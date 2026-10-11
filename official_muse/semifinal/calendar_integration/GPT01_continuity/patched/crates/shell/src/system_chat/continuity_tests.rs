//! Scripted OUP fixture. No kernel, provider, timer, GUI, or external action.
use super::continuity::{Action, Policy, INTERVAL_SECONDS, PROMPT};
use super::session::{Closed, Command, Connector, Driver, Link, Recv, SystemHost, Unavailable, SYSTEM_PROFILE, SYSTEM_SESSION};
use super::model::Phase;
use serde_json::{json, Value};
use std::collections::VecDeque;
use std::sync::{Arc, Mutex};
use std::time::Duration;

#[derive(Default)]
struct Script {
    sent: Vec<(String, Value)>, inbox: VecDeque<String>, loops: Vec<Value>,
    close: bool, lose_create: bool, bad_control: bool, control_error: bool,
    bad_list: bool, foreign_list: bool, policy: bool, wrong_policy: bool,
    override_control: Option<Value>,
}
#[derive(Clone, Default)]
struct Fake(Arc<Mutex<Script>>);
impl Fake {
    fn sent(&self, method: &str) -> Vec<Value> { self.0.lock().unwrap().sent.iter().filter(|(m, _)| m == method).map(|(_, p)| p.clone()).collect() }
    fn notify(&self, method: &str, params: Value) { self.0.lock().unwrap().inbox.push_back(json!({"method":method,"params":params}).to_string()); }
}
fn record(id: &str, status: &str) -> Value {
    json!({"loop_id":id,"session_id":SYSTEM_SESSION,"profile_id":SYSTEM_PROFILE,"prompt":PROMPT,
        "mode":"fixed_interval","interval_seconds":INTERVAL_SECONDS,"status":status,
        "next_run_at_ms":4000000000000i64,"last_run_at_ms":null,"expires_at_ms":4000000000000i64,
        "created_at_ms":1,"updated_at_ms":2})
}
struct FakeLink(Fake);
impl Link for FakeLink {
    fn send(&mut self, frame: String) -> Result<(), Closed> {
        let v: Value = serde_json::from_str(&frame).unwrap();
        let method = v["method"].as_str().unwrap();
        let mut s = self.0.0.lock().unwrap();
        s.sent.push((method.into(),v["params"].clone()));
        let result = match method {
            "session/open" => json!({"opened":{"session_id":SYSTEM_SESSION}}),
            "session/hydrate" => json!({"messages":[]}),
            "loop/list" if s.bad_list => json!({}),
            "loop/list" => json!({"session_id":if s.foreign_list { "other:api:session" } else { SYSTEM_SESSION },"profile_id":SYSTEM_PROFILE,"loops":s.loops}),
            "loop/create" if !s.bad_control && !s.control_error => {
                let r=record("real-loop-7","active");s.loops.push(r.clone());
                if s.lose_create { s.lose_create=false;s.close=true;return Ok(()); }
                json!({"ok":true,"session_id":SYSTEM_SESSION,"profile_id":SYSTEM_PROFILE,"loop_id":"real-loop-7","loop":r})
            }
            "loop/pause" | "loop/resume" | "loop/delete" if !s.bad_control && !s.control_error => {
                let id=v["params"]["loop_id"].as_str().unwrap();
                let status=match method { "loop/pause"=>"paused", "loop/resume"=>"active", _=>"deleted" };
                let r=record(id,status);
                s.loops.retain(|r| r["loop_id"] != id);
                if status!="deleted" {s.loops.push(r.clone());}
                json!({"ok":true,"session_id":SYSTEM_SESSION,"deleted":status=="deleted","loop_id":id,"loop":r})
            }
            _ => json!({}),
        };
        let result = if method.starts_with("loop/") && method != "loop/list" {
            s.override_control.clone().unwrap_or(result)
        } else { result };
        let reply = if method.starts_with("loop/") && method!="loop/list" && s.control_error {
            json!({"id":v["id"],"error":{"code":-32000,"message":"loop request refused"}})
        } else {json!({"id":v["id"],"result":result})};
        s.inbox.push_back(reply.to_string());Ok(())
    }
    fn recv(&mut self, _: Duration) -> Recv {
        let mut s=self.0.0.lock().unwrap();
        if s.close {s.close=false;return Recv::Closed(Closed {restarted:true,why:"fixture restart".into()});}
        s.inbox.pop_front().map(Recv::Frame).unwrap_or(Recv::Idle)
    }
}
impl Connector for Fake {
    fn connect(&mut self) -> Result<Box<dyn Link>,Unavailable> {Ok(Box::new(FakeLink(self.clone())))}
}
impl SystemHost for Fake {
    fn declarations(&self) -> Vec<Value> {Vec::new()}
    fn continuity_model_label(&self) -> Option<String> {Some("fixture / no-network-model".into())}
    fn continuity_policy(&self) -> Result<Policy,String> {
        let s=self.0.lock().unwrap();
        if !s.policy {return Err("fixture: enforced cost policy missing".into());}
        Ok(Policy {profile_id:SYSTEM_PROFILE.into(),model_label:if s.wrong_policy {"wrong-model".into()} else {"fixture / no-network-model".into()},cost_limit_label:"fixture only, zero network calls".into()})
    }
}
fn settle(d: &mut Driver) {for _ in 0..30 {d.step(Duration::ZERO);}}
fn opened(policy: bool, loops: Vec<Value>) -> (Driver,Fake) {
    let fake=Fake::default();{let mut s=fake.0.lock().unwrap();s.policy=policy;s.loops=loops;}
    let mut d=Driver::with_system_host(Box::new(fake.clone()),Box::new(fake.clone()));
    d.command(Command::Open);settle(&mut d);(d,fake)
}
fn act(d: &mut Driver,a: Action) {d.command(Command::Continuity(a));settle(d);}

#[test]
fn continuity_default_is_disabled_and_list_is_not_create() {
    let (mut d,f)=opened(false,vec![]);
    assert!(d.model.continuity.checked);
    assert!(d.model.continuity.policy.is_err());
    assert!(d.model.continuity.controls().iter().any(|(_,a,enabled)| *a==Action::Enable && !enabled));
    act(&mut d,Action::Enable);
    assert!(f.sent("loop/create").is_empty());
    assert!(d.model.continuity.error.is_some());
    assert_eq!(f.sent("loop/list").len(),1);
}
#[test]
fn continuity_creation_needs_gesture_and_uses_only_official_fields() {
    let (mut d,f)=opened(true,vec![]);
    assert!(f.sent("loop/create").is_empty());
    act(&mut d,Action::Enable);
    let calls=f.sent("loop/create");assert_eq!(calls.len(),1);
    assert_eq!(calls[0],json!({"session_id":SYSTEM_SESSION,"profile_id":SYSTEM_PROFILE,"prompt":PROMPT,"mode":"fixed_interval","interval_seconds":INTERVAL_SECONDS}));
    assert_eq!(d.model.continuity.loop_id.as_deref(),Some("real-loop-7"));
    assert_eq!(d.model.continuity.record.as_ref().unwrap().status,"active");
    assert!(f.sent("turn/start").is_empty());assert!(f.sent("loop/fire_now").is_empty());
    act(&mut d,Action::Enable);assert_eq!(f.sent("loop/create").len(),1);
}
#[test]
fn continuity_close_keeps_active_driver_and_person_turn_separate() {
    let (mut d,f)=opened(true,vec![]);act(&mut d,Action::Enable);
    d.command(Command::Close);assert!(d.is_connected());
    assert!(f.sent("loop/pause").is_empty());assert!(f.sent("turn/interrupt").is_empty());
    d.command(Command::Open);d.command(Command::Send("person's own request".into()));settle(&mut d);
    assert_eq!(f.sent("turn/start").len(),1);
    act(&mut d,Action::Pause);assert!(f.sent("turn/interrupt").is_empty());
    assert!(matches!(d.model.phase(),Phase::Running {..}));
}
#[test]
fn continuity_pause_resume_delete_use_real_id_and_do_not_interrupt() {
    let (mut d,f)=opened(true,vec![record("existing-42","active")]);
    act(&mut d,Action::Pause);assert_eq!(d.model.continuity.record.as_ref().unwrap().status,"paused");
    act(&mut d,Action::Resume);assert_eq!(d.model.continuity.record.as_ref().unwrap().status,"active");
    act(&mut d,Action::Delete);assert!(d.model.continuity.loop_id.is_none());
    for method in ["loop/pause","loop/resume","loop/delete"] {assert_eq!(f.sent(method),vec![json!({"loop_id":"existing-42","session_id":SYSTEM_SESSION,"profile_id":SYSTEM_PROFILE})]);}
    assert!(f.sent("turn/interrupt").is_empty());assert!(f.sent("loop/create").is_empty());
}
#[test]
fn continuity_pause_and_delete_remain_available_without_billing_policy() {
    let (mut d,f)=opened(false,vec![record("approved-old-loop","active")]);
    act(&mut d,Action::Pause);assert_eq!(f.sent("loop/pause").len(),1);
    act(&mut d,Action::Resume);assert!(f.sent("loop/resume").is_empty());
    act(&mut d,Action::Delete);assert_eq!(f.sent("loop/delete").len(),1);
}
#[test]
fn continuity_pausing_closed_idle_pane_releases_link_only_after_reply() {
    let (mut d,f)=opened(true,vec![record("loop-live","active")]);d.command(Command::Close);assert!(d.is_connected());
    d.command(Command::Continuity(Action::Pause));assert!(d.is_connected());settle(&mut d);
    assert!(!d.is_connected());assert!(f.sent("turn/interrupt").is_empty());
}
#[test]
fn continuity_reconnect_reads_original_id_without_create_or_resume() {
    let (mut d,f)=opened(true,vec![record("original-1","active")]);d.command(Command::Close);
    f.0.lock().unwrap().close=true;d.step(Duration::ZERO);assert!(!d.is_connected());
    d.retry_now();settle(&mut d);
    assert!(d.is_connected());assert_eq!(d.model.continuity.loop_id.as_deref(),Some("original-1"));
    assert_eq!(f.sent("loop/list").len(),2);assert!(f.sent("loop/create").is_empty());assert!(f.sent("loop/resume").is_empty());
}
#[test]
fn continuity_lost_create_reply_is_resolved_by_list_not_retried() {
    let (mut d,f)=opened(true,vec![]);f.0.lock().unwrap().lose_create=true;
    act(&mut d,Action::Enable);assert!(d.model.continuity.uncertain);
    d.command(Command::Close);d.retry_now();settle(&mut d);
    assert_eq!(d.model.continuity.loop_id.as_deref(),Some("real-loop-7"));
    assert!(!d.model.continuity.uncertain);assert!(d.is_connected());
    assert_eq!(f.sent("loop/create").len(),1);
}
#[test]
fn continuity_unknown_create_empty_reply_and_empty_list_never_recreate() {
    let (mut d,f)=opened(true,vec![]);f.0.lock().unwrap().bad_control=true;
    act(&mut d,Action::Enable);assert!(d.model.continuity.uncertain);assert!(d.model.continuity.loop_id.is_none());
    act(&mut d,Action::Enable);assert_eq!(f.sent("loop/create").len(),1);
    assert!(d.model.continuity.error.as_deref().unwrap().contains("重复创建"));
    assert!(d.model.continuity.label().contains("未确认"));
}
#[test]
fn continuity_rpc_errors_are_not_success_and_do_not_retry_create() {
    let (mut d,f)=opened(true,vec![]);f.0.lock().unwrap().control_error=true;
    act(&mut d,Action::Enable);assert!(d.model.continuity.uncertain);assert!(!d.model.continuity.checked);
    act(&mut d,Action::Enable);assert_eq!(f.sent("loop/create").len(),1);
}
#[test]
fn continuity_missing_known_id_blocks_recreation_and_unrelated_adoption() {
    let (mut d,f)=opened(true,vec![record("original-1","paused")]);
    f.0.lock().unwrap().loops=vec![record("unrelated-new-id","active")];
    act(&mut d,Action::Refresh);assert_eq!(d.model.continuity.loop_id.as_deref(),Some("original-1"));
    assert!(d.model.continuity.record.is_none());act(&mut d,Action::Enable);
    assert!(f.sent("loop/create").is_empty());
}
#[test]
fn continuity_malformed_foreign_and_duplicate_lists_block_creation() {
    for case in 0..3 {
        let (mut d,f)=opened(true,vec![]);
        {let mut s=f.0.lock().unwrap();match case {0=>s.bad_list=true,1=>s.foreign_list=true,_=>s.loops=vec![record("a","active"),record("b","active")]};}
        act(&mut d,Action::Enable);assert!(f.sent("loop/create").is_empty());assert!(!d.model.continuity.checked);assert!(d.model.continuity.error.is_some());
    }
}
#[test]
fn continuity_bad_pause_ack_is_unknown_and_keeps_connection() {
    let (mut d,f)=opened(true,vec![record("loop-live","active")]);f.0.lock().unwrap().bad_control=true;
    act(&mut d,Action::Pause);assert!(d.model.continuity.uncertain);assert!(!d.model.continuity.checked);
    d.command(Command::Close);assert!(d.is_connected());assert!(d.model.continuity.label().contains("未确认"));
}
#[test]
fn continuity_policy_must_match_current_primary_model() {
    let (mut d,f)=opened(true,vec![]);f.0.lock().unwrap().wrong_policy=true;
    act(&mut d,Action::Enable);assert!(f.sent("loop/create").is_empty());assert!(d.model.continuity.policy.is_err());
}
#[test]
fn continuity_fired_is_only_a_signal_and_does_not_complete_a_turn() {
    let (mut d,f)=opened(true,vec![record("loop-live","active")]);
    f.notify("loop/fired",json!({"session_id":SYSTEM_SESSION,"profile_id":SYSTEM_PROFILE,"loop_id":"loop-live","fire":{"queued":true}}));settle(&mut d);
    assert_eq!(f.sent("loop/list").len(),2);assert!(f.sent("turn/start").is_empty());assert!(d.model.items.is_empty());
    f.notify("loop/fired",json!({"session_id":"foreign:api:session","loop_id":"loop-live"}));settle(&mut d);
    assert_eq!(f.sent("loop/list").len(),2);
}
#[test]
fn continuity_reconnect_paused_record_is_not_automatically_resumed() {
    let (mut d,f)=opened(true,vec![record("loop-live","active")]);d.command(Command::Close);
    {let mut s=f.0.lock().unwrap();s.loops=vec![record("loop-live","paused")];s.close=true;}
    d.step(Duration::ZERO);d.retry_now();settle(&mut d);
    assert_eq!(d.model.continuity.record.as_ref().unwrap().status,"paused");assert!(!d.is_connected());assert!(f.sent("loop/resume").is_empty());
}
#[test]
fn continuity_expired_paused_record_cannot_resume() {
    let mut r=record("expired","paused");r["expires_at_ms"]=json!(1);
    let (mut d,f)=opened(true,vec![r]);act(&mut d,Action::Resume);
    assert!(f.sent("loop/resume").is_empty());assert!(d.model.continuity.error.is_some());
}
#[test]
fn continuity_close_default_idle_pane_still_releases_connection() {
    let (mut d,_)=opened(false,vec![]);d.command(Command::Close);assert!(!d.is_connected());
}
#[test]
fn continuity_enable_queued_before_open_is_not_lost() {
    let f=Fake::default();f.0.lock().unwrap().policy=true;
    let mut d=Driver::with_system_host(Box::new(f.clone()),Box::new(f.clone()));
    d.command(Command::Continuity(Action::Enable));settle(&mut d);
    assert_eq!(f.sent("loop/create").len(),1);assert!(d.is_connected());
    assert_eq!(d.model.continuity.loop_id.as_deref(),Some("real-loop-7"));
}
#[test]
fn continuity_pause_queued_while_initial_list_is_in_flight_is_not_lost() {
    let f=Fake::default();f.0.lock().unwrap().loops=vec![record("old-approved","active")];
    let mut d=Driver::with_system_host(Box::new(f.clone()),Box::new(f.clone()));
    d.command(Command::Open);d.step(Duration::ZERO);
    assert!(d.model.continuity.busy);d.command(Command::Continuity(Action::Pause));settle(&mut d);
    assert_eq!(f.sent("loop/pause").len(),1);assert_eq!(d.model.continuity.record.as_ref().unwrap().status,"paused");
    assert!(f.sent("turn/interrupt").is_empty());
}
#[test]
fn continuity_repeated_enable_while_busy_never_duplicates_create() {
    let (mut d,f)=opened(true,vec![]);
    d.command(Command::Continuity(Action::Enable));
    d.command(Command::Continuity(Action::Enable));
    d.command(Command::Continuity(Action::Enable));settle(&mut d);
    assert_eq!(f.sent("loop/create").len(),1);assert!(!d.model.continuity.busy);
}
#[test]
fn continuity_matching_prompt_with_foreign_profile_is_rejected() {
    let mut r=record("foreign-record","active");r["profile_id"]=json!("other-profile");
    let (mut d,f)=opened(true,vec![r]);
    assert!(!d.model.continuity.checked);assert!(d.model.continuity.loop_id.is_none());
    act(&mut d,Action::Enable);assert!(f.sent("loop/create").is_empty());
}
#[test]
fn continuity_close_after_pause_waits_for_person_turn_terminal() {
    let (mut d,f)=opened(true,vec![record("loop-live","active")]);
    d.command(Command::Send("person's turn".into()));settle(&mut d);
    let turn=f.sent("turn/start")[0]["turn_id"].clone();
    act(&mut d,Action::Pause);d.command(Command::Close);assert!(d.is_connected());
    f.notify("turn/completed",json!({"session_id":SYSTEM_SESSION,"turn_id":turn}));settle(&mut d);
    assert!(!d.is_connected());assert!(f.sent("turn/interrupt").is_empty());
}

#[test]
fn continuity_control_outer_scope_id_and_false_ok_cannot_claim_success() {
    for case in 0..4 {
        let (mut d,f)=opened(true,vec![]);
        let mut v=json!({"ok":true,"session_id":SYSTEM_SESSION,"profile_id":SYSTEM_PROFILE,"loop_id":"real-loop-7","loop":record("real-loop-7","active")});
        match case {0=>v["session_id"]=json!("foreign:api:session"),1=>v["profile_id"]=json!("foreign-profile"),2=>v["loop_id"]=json!("other-id"),_=>v["ok"]=json!(false)}
        f.0.lock().unwrap().override_control=Some(v);act(&mut d,Action::Enable);
        assert!(d.model.continuity.loop_id.is_none());assert!(d.model.continuity.uncertain);assert!(!d.model.continuity.checked);
        assert!(d.model.continuity.error.is_some());assert_eq!(f.sent("loop/create").len(),1);
    }
}
