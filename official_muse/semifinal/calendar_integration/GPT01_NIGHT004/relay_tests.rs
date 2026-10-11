//! Real Relay and real approval Router; consent, grants and sheet taps below are FIXTURE authorization.
use crate::host_tools::relay::{Catalog,Env,Event,Relay};
use crate::ai_host::app_peers::host_tools::{ApprovalAnswer,CallOrigin,CallerKind,HostToolApproval,HostToolCall,ToolExecutor,ToolOutcome,ToolReply};
use crate::approvals::{Caller,RecordingRelay,RequestContext,RequestId,Route,Router,ToolSpec};
use crate::approvals::{audit::AuditLog,contacts::{ContactsGate,NoContacts},dev_hooks::FixedDevMode,rules::{ApprovalGesture,RuleStore},sheet::Answer};
use crate::peer_link::{KernelToolCall,Refused};
use serde_json::{json,Value};
use std::{collections::BTreeSet,path::PathBuf,sync::{Arc,Mutex}};
const SIX:&[&str]=&["calendar.events","calendar.get_event","calendar.add_event","calendar.update_event","calendar.remove_event","calendar.notify"];

struct FixtureWorld { router:Router, decisions:RecordingRelay, fixture_consent:bool, signed_out:bool, withdrawn:BTreeSet<String>, asked:Vec<(String,ToolSpec,Caller)> }
impl FixtureWorld {
    fn new()->Self {
        let decisions=RecordingRelay::default();
        Self {router:Router::new(RuleStore::memory(),AuditLog::memory(),Box::new(FixedDevMode::off()),ContactsGate::memory(Box::new(NoContacts)),Box::new(decisions.clone())),decisions,fixture_consent:true,signed_out:false,withdrawn:BTreeSet::new(),asked:Vec::new()}
    }
}
impl Env for FixtureWorld {
    fn admitted(&self,app:&str)->Result<(),String>{if self.withdrawn.contains(app){Err(format!("fixture withdrawn {app}"))}else{Ok(())}}
    fn consent(&self,_app:&str)->bool{self.fixture_consent}
    fn grants_all(&self,_app:&str)->bool{false}
    fn suspended(&self,_app:&str,_account:Option<&str>)->bool{self.signed_out}
    fn system_tools(&self)->BTreeSet<String>{BTreeSet::new()}
    fn tool_rule(&self,_owner:&str,_tool:&str)->(bool,bool){(true,false)}
    fn request_approval(&mut self,app:&str,tool:ToolSpec,args:Value,caller:Caller,context:RequestContext)->Route {
        self.asked.push((app.into(),tool.clone(),caller.clone()));
        self.router.request(crate::approvals::router::make_request(app,tool,args,caller,context,100,0),100)
    }
    fn withdraw_approval(&mut self,id:&RequestId,reason:&str){self.router.withdraw(id,reason,101);}
    fn has_link(&self,_app:&str)->bool{false}
    fn link_call(&mut self,_app:&str,_call:KernelToolCall)->Result<(),Refused>{panic!("No peer link in fixture")}
    fn link_cancel(&mut self,_app:&str,_call_id:&str){panic!("No peer link in fixture")}
    fn bus_call(&mut self,_id:&str,_app:&str,_tool:&str,_args:String){panic!("Calendar must use actual owner executor")}
    fn bus_cancel(&mut self,_id:&str){panic!("No AI bus in fixture")}
    fn log(&mut self,_line:String){}
    fn now(&self)->u64{100}
}

struct OwnerExecutor { root:PathBuf, calls:Arc<Mutex<Vec<Value>>> }
impl ToolExecutor for OwnerExecutor {
    fn execute(&self,call:HostToolCall,reply:ToolReply){
        assert!(reply.is_open());
        self.calls.lock().unwrap().push(json!({"owner":call.app,"caller":call.calling_app,"name":call.name,"call_id":call.call_id}));
        let method=call.name.strip_prefix("calendar.").unwrap();
        let outcome=gpt01_night004_calendar::owner_call(&self.root,&call.app,method,call.args);
        reply.finish(match outcome{Ok(value)=>ToolOutcome::Ok(value),Err(error)=>ToolOutcome::error("calendar_error",error)});
    }
}
struct Fixture { root:PathBuf, relay:Relay, world:FixtureWorld, executed:Arc<Mutex<Vec<Value>>>, trace:Vec<Value>, seq:u32 }
impl Fixture {
    fn new()->Self {
        let root=std::env::temp_dir().join(format!("gpt01-night004-relay-{}-{}",std::process::id(),std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_nanos()));
        std::fs::create_dir(&root).unwrap();
        let declarations:Value=serde_json::from_str(include_str!("../calendar-tools.json")).unwrap();
        let mut relay=Relay::default();relay.catalog=Catalog::default();
        relay.catalog.declare("os.calendar",declarations["tools"].as_array().unwrap().clone());
        relay.catalog.set_grants("muse-goals","os.calendar",SIX); // Synthetic grant, never real consent.
        let executed:Arc<Mutex<Vec<Value>>>=Arc::default();
        relay.set_executor("os.calendar",Some(Arc::new(OwnerExecutor{root:root.clone(),calls:executed.clone()})));
        Self {root,relay,world:FixtureWorld::new(),executed,trace:Vec::new(),seq:0}
    }
    fn invoke(&mut self,name:&str,args:Value,caller:&str,owner:&str,system:bool)->Value {
        self.seq+=1;let id=format!("fixture-call-{}",self.seq);
        let mut call=HostToolCall::parse(&json!({"peer":"fixture-peer","session_id":"fixture-session","turn_id":"fixture-turn","call_id":id,"tool_call_id":format!("tool-{id}"),"name":name,"app":owner,"args":args,"args_digest":crate::approvals::facts::digest(&args),"risk":"act","confirm_required":false})).unwrap();
        call.calling_app=caller.into();call.account=Some("fixture-account".into());call.origin=CallOrigin::Context;
        if system{call.caller_kind=CallerKind::System;}
        let answers:Arc<Mutex<Vec<Value>>>=Arc::default();let capture=answers.clone();
        self.relay.handle(Event::Call{call,reply:ToolReply::new(&id,move|v|capture.lock().unwrap().push(v))},&mut self.world);
        let answer=answers.lock().unwrap().last().cloned().expect("real Relay replied");
        self.trace.push(json!({"tool":name,"caller":caller,"owner":owner,"response":answer}));answer
    }
    fn call(&mut self,name:&str,args:Value)->Value{self.invoke(name,args,"card.muse-goals","os.calendar",false)}
    fn create(&mut self)->Value{
        let result=self.call("calendar.add_event",json!({"title":"Relay synthetic","start":"2026-10-13T15:00","timezone":"Asia/Shanghai","request_id":"relay-synthetic-1"}));assert_eq!(result["ok"],true);
        let id=result["data"]["id"].clone();self.call("calendar.get_event",json!({"id":id}))["data"]["event"].clone()
    }
    fn confirm_fixture(&mut self,name:&str,args:Value,approve:bool)->bool {
        self.seq+=1;let id=format!("fixture-approval-{}",self.seq);
        let approval=HostToolApproval::parse(&json!({"approval_kind":"host_tool","approval_id":id,"turn_id":"fixture-turn","typed_details":{"host_tool":{"app":"os.calendar","tool":name,"args":args,"risk":"destructive","calling_kind":"app_peer","calling_peer":"muse-goals"}}}),"fixture-session").unwrap();
        let answers:Arc<Mutex<Vec<bool>>>=Arc::default();let captured=answers.clone();
        let before=self.executed.lock().unwrap().len();
        self.relay.handle(Event::Approval{app:"card.muse-goals".into(),account:Some("fixture-account".into()),approval,answer:ApprovalAnswer::new(move|v|captured.lock().unwrap().push(v))},&mut self.world);
        assert!(answers.lock().unwrap().is_empty());assert_eq!(self.executed.lock().unwrap().len(),before);
        let sheet=self.world.router.front_sheet().expect("real approval Router surfaced a sheet");
        assert_eq!(sheet.lines[0].app,"os.calendar");assert_eq!(sheet.lines[0].tool,name);
        let sheet_id=sheet.id;let request=sheet.lines[0].request.clone();
        assert!(!self.world.asked.last().unwrap().1.auto_approvable);
        // This is a TEST gesture invoking the real Router, never a physical user approval.
        self.world.router.answer(sheet_id,&request,if approve{Answer::Once}else{Answer::Deny},&ApprovalGesture::sheet_tap(),101).unwrap();
        for (id,decision,reason) in self.world.decisions.take(){self.relay.handle(Event::Decision{id,decision,reason},&mut self.world);}
        let result=answers.lock().unwrap()[0];assert_eq!(result,approve);
        self.trace.push(json!({"fixture_host_confirmation":name,"approved":result,"real_person_consent":false}));result
    }
}
impl Drop for Fixture {
    fn drop(&mut self){
        println!("NIGHT004_TRACE {}",json!({"fixture_authorization":true,"real_person_consent":false,"steps":self.trace,"executor_calls":*self.executed.lock().unwrap()}));
        std::fs::remove_dir_all(&self.root).unwrap();
    }
}

#[test]
fn real_relay_owner_lifecycle_and_host_router_fixture_confirmation(){
    let mut f=Fixture::new();let old=f.create();let id=old["id"].clone();
    let args=json!({"id":id,"expected":old,"title":"Relay revised","start":"2026-10-13T16:00","timezone":"Asia/Shanghai"});
    assert!(f.confirm_fixture("calendar.update_event",args.clone(),true));
    let updated=f.call("calendar.update_event",args);assert_eq!(updated["ok"],true);assert_eq!(updated["data"]["event"]["id"],id);
    let current=f.call("calendar.get_event",json!({"id":id}))["data"]["event"].clone();assert_eq!(current["start"],"2026-10-13T16:00");
    assert_eq!(f.call("calendar.remove_event",json!({"id":id,"expected":old}))["error"]["kind"],"calendar_error");
    let args=json!({"id":id,"expected":current});assert!(f.confirm_fixture("calendar.remove_event",args.clone(),true));
    assert_eq!(f.call("calendar.remove_event",args)["data"]["removed"],true);
    assert_eq!(f.call("calendar.get_event",json!({"id":id}))["data"],json!({"found":false,"event":null}));
    assert!(f.executed.lock().unwrap().iter().all(|r|r["owner"]=="os.calendar"&&r["caller"]=="card.muse-goals"));
}
#[test]
fn real_relay_wrong_caller_owner_system_and_revoked_grants_refuse(){
    let mut f=Fixture::new();let args=json!({"title":"Never saved","start":"2026-10-13T15:00"});
    for (caller,owner,system) in [("card.another-app","os.calendar",false),("card.muse-goals","muse-goals",false),("system","os.calendar",true)]{
        assert_eq!(f.invoke("calendar.add_event",args.clone(),caller,owner,system)["error"]["kind"],"not_granted");
    }
    f.relay.catalog.set_grants("muse-goals","os.calendar",&[]);
    assert_eq!(f.call("calendar.add_event",args)["error"]["kind"],"not_granted");
    assert!(f.executed.lock().unwrap().is_empty());assert!(!f.root.join("calendar/events.json").exists());
}
#[test]
fn real_relay_missing_fixture_consent_or_signed_out_refuses(){
    let mut f=Fixture::new();f.world.fixture_consent=false;
    assert_eq!(f.call("calendar.events",json!({}))["error"]["kind"],"consent_pending");
    f.world.fixture_consent=true;f.world.signed_out=true;
    assert_eq!(f.call("calendar.events",json!({}))["error"]["kind"],"signed_out");
    assert!(f.executed.lock().unwrap().is_empty());
}
#[test]
fn real_relay_owner_or_caller_withdrawn_refuses(){
    let mut f=Fixture::new();
    for app in ["os.calendar","muse-goals"]{
        f.world.withdrawn.clear();f.world.withdrawn.insert(app.into());
        assert_eq!(f.call("calendar.events",json!({}))["error"]["kind"],"app_unavailable");
    }
    assert!(f.executed.lock().unwrap().is_empty());
}
#[test]
fn real_host_router_denial_and_grant_revocation_preserve_event(){
    let mut f=Fixture::new();let event=f.create();let args=json!({"id":event["id"],"expected":event});
    let bytes=std::fs::read(f.root.join("calendar/events.json")).unwrap();
    assert!(!f.confirm_fixture("calendar.remove_event",args.clone(),false));
    assert_eq!(std::fs::read(f.root.join("calendar/events.json")).unwrap(),bytes);
    assert!(f.confirm_fixture("calendar.remove_event",args.clone(),true));
    f.relay.catalog.set_grants("muse-goals","os.calendar",&[]);
    assert_eq!(f.call("calendar.remove_event",args)["error"]["kind"],"not_granted");
    assert_eq!(std::fs::read(f.root.join("calendar/events.json")).unwrap(),bytes);
}
#[test]
fn real_relay_schema_requires_expected_before_mutation_dispatch(){
    let mut f=Fixture::new();
    assert_eq!(f.call("calendar.remove_event",json!({"id":"synthetic"}))["error"]["kind"],"invalid_args");
    assert_eq!(f.call("calendar.update_event",json!({"id":"synthetic","title":"Missing snapshot","start":"2026-10-13T16:00"}))["error"]["kind"],"invalid_args");
    assert!(f.executed.lock().unwrap().is_empty());
}
