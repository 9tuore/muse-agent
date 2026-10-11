//! Existing real Relay/Schema/Router/CalendarService, with explicit synthetic transport/scope.
use crate::host_tools::relay::{Catalog,Env,Event,Relay};
use crate::ai_host::app_peers::host_tools::{ApprovalAnswer,CallOrigin,HostToolApproval,HostToolCall,ToolExecutor,ToolOutcome,ToolReply};
use crate::approvals::{Caller,RecordingRelay,RequestContext,RequestId,Route,Router,ToolSpec};
use crate::approvals::{audit::AuditLog,contacts::{ContactsGate,NoContacts},dev_hooks::FixedDevMode,rules::{ApprovalGesture,RuleStore},sheet::Answer};
use crate::peer_link::{KernelToolCall,Refused};
use serde_json::{json,Value};
use std::{collections::BTreeSet,path::{Path,PathBuf},sync::{Arc,Mutex}};
const TOOLS:&[&str]=&["calendar.events","calendar.get_event","calendar.add_event","calendar.update_event","calendar.remove_event"];

fn scoped_root(root:&Path)->Result<PathBuf,String>{
    let root=root.canonicalize().map_err(|e|format!("Fixture root unavailable: {e}"))?;
    let own=Path::new(env!("CARGO_MANIFEST_DIR")).ancestors().nth(3).unwrap().join("build/night-004");
    let central=Path::new("/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/night-004");
    let under=[own.as_path(),central].iter().any(|base|base.canonicalize().is_ok_and(|base|root.starts_with(&base)&&root!=base));
    if !under||!root.join("FIXTURE_ONLY").is_file(){return Err("Only marked isolated build/night-004 roots may be used".into());}
    // The real service opens these paths: do not let a fixture point them outside its root.
    for name in ["calendar","calendar/events.json","calendar/cards.json"]{
        let path=root.join(name);
        if std::fs::symlink_metadata(&path).is_ok_and(|m|m.file_type().is_symlink()){
            return Err(format!("Fixture store path is a symlink: {name}"));
        }
    }
    Ok(root)
}
struct World{router:Router,decisions:RecordingRelay,consent:bool,signed_out:bool,withdrawn:BTreeSet<String>,logs:Vec<String>,approval_trace:Vec<Value>}
impl World{
    fn new()->Self{let decisions=RecordingRelay::default();Self{
        router:Router::new(RuleStore::memory(),AuditLog::memory(),Box::new(FixedDevMode::off()),ContactsGate::memory(Box::new(NoContacts)),Box::new(decisions.clone())),
        decisions,consent:false,signed_out:false,withdrawn:BTreeSet::new(),logs:Vec::new(),approval_trace:Vec::new()}}
}
impl Env for World{
    fn admitted(&self,app:&str)->Result<(),String>{if self.withdrawn.contains(app){Err(format!("synthetic fixture withdrawn {app}"))}else{Ok(())}}
    fn consent(&self,_app:&str)->bool{self.consent}
    fn grants_all(&self,_app:&str)->bool{false}
    fn suspended(&self,_app:&str,_account:Option<&str>)->bool{self.signed_out}
    fn system_tools(&self)->BTreeSet<String>{BTreeSet::new()}
    fn tool_rule(&self,_owner:&str,_tool:&str)->(bool,bool){(false,false)}
    fn request_approval(&mut self,app:&str,tool:ToolSpec,args:Value,caller:Caller,context:RequestContext)->Route{
        self.router.request(crate::approvals::router::make_request(app,tool,args,caller,context,100,0),100)}
    fn withdraw_approval(&mut self,id:&RequestId,reason:&str){self.router.withdraw(id,reason,101);}
    fn has_link(&self,_app:&str)->bool{false}
    fn link_call(&mut self,_app:&str,_call:KernelToolCall)->Result<(),Refused>{Err(Refused::NotConnected)}
    fn link_cancel(&mut self,_app:&str,_call_id:&str){}
    fn bus_call(&mut self,_id:&str,_app:&str,_tool:&str,_args:String){unreachable!("Only Calendar methods are accepted")}
    fn bus_cancel(&mut self,_id:&str){}
    fn log(&mut self,line:String){self.logs.push(line)}
    fn now(&self)->u64{100}
}
struct Owner{root:PathBuf,calls:Arc<Mutex<Vec<Value>>>}
impl ToolExecutor for Owner{
    fn execute(&self,call:HostToolCall,reply:ToolReply){
        self.calls.lock().unwrap().push(json!({"owner":call.app,"caller":call.calling_app,"tool":call.name,"args":call.args}));
        let outcome=scoped_root(&self.root).and_then(|root|gpt01_night004_calendar::owner_call(&root,&call.app,call.name.strip_prefix("calendar.").unwrap(),call.args));
        reply.finish(match outcome{Ok(v)=>ToolOutcome::Ok(v),Err(e)=>ToolOutcome::error("calendar_error",e)});
    }
}
pub struct Session{root:PathBuf,relay:Relay,world:World,executed:Arc<Mutex<Vec<Value>>>,seq:u64}
impl Session{
    pub fn new(root:&Path)->Result<Self,String>{
        let root=scoped_root(root)?;
        let declarations:Value=serde_json::from_str(include_str!("../calendar-tools.json")).unwrap();
        let mut relay=Relay::default();relay.catalog=Catalog::default();
        relay.catalog.declare("os.calendar",declarations["tools"].as_array().unwrap().clone());
        let executed:Arc<Mutex<Vec<Value>>>=Arc::default();
        relay.set_executor("os.calendar",Some(Arc::new(Owner{root:root.clone(),calls:executed.clone()})));
        Ok(Self{root,relay,world:World::new(),executed,seq:0})
    }
    pub fn call(&mut self,request:Value)->Value{
        let before=self.executed.lock().unwrap().len();self.world.logs.clear();self.world.approval_trace.clear();
        let result=self.invoke(&request);let calls=self.executed.lock().unwrap();
        let outcome=match result{Ok(v)=>v,Err(e)=>json!({"ok":false,"error":{"kind":"fixture_protocol","message":e}})};
        let count=std::fs::read(self.root.join("calendar/events.json")).ok().and_then(|b|serde_json::from_slice::<Vec<Value>>(&b).ok()).map(|v|v.len());
        json!({"is_ok":outcome["ok"].as_bool().unwrap_or(false),"data":outcome.get("data").cloned().unwrap_or(Value::Null),
            "error":outcome.get("error").cloned().unwrap_or(Value::Null),"result":outcome,
            "fixture":{"authorization":"synthetic","scope":"synthetic","approval_gestures":"synthetic","kernel":false},
            "approval_trace":self.world.approval_trace,
            "executor_calls":&calls[before..],"store_event_count":count,"relay_logs":self.world.logs})
    }
    fn invoke(&mut self,request:&Value)->Result<Value,String>{
        scoped_root(&self.root)?;
        let raw=request["method"].as_str().ok_or("method must be a string")?;
        let method=if raw.starts_with("calendar."){raw.to_string()}else{format!("calendar.{raw}")};
        if !TOOLS.contains(&method.as_str()){return Err("Only Calendar create/get/update/remove/events are accepted; no Kernel/session/history adapter exists".into());}
        let args=request.get("args").cloned().ok_or("args required")?;
        let scope=request["scope"].as_object().ok_or("Explicit synthetic scope required")?;
        let caller=scope.get("caller").and_then(Value::as_str).unwrap_or("card.muse-goals");
        let owner=scope.get("owner").and_then(Value::as_str).unwrap_or("os.calendar");
        let account=scope.get("account").and_then(Value::as_str).unwrap_or("fixture-account");
        self.world.consent=scope.get("fixture_consent").and_then(Value::as_bool)==Some(true);
        self.world.signed_out=scope.get("signed_out").and_then(Value::as_bool)==Some(true);
        self.world.withdrawn=scope.get("withdrawn").and_then(Value::as_array).into_iter().flatten().filter_map(Value::as_str).map(str::to_string).collect();
        self.relay.catalog.set_grants("muse-goals","os.calendar",if scope.get("granted").and_then(Value::as_bool)==Some(true){TOOLS}else{&[]});
        self.seq+=1;let id=format!("fixture-{}-{}",std::process::id(),self.seq);
        let write=matches!(method.as_str(),"calendar.add_event"|"calendar.update_event"|"calendar.remove_event");
        if write{
            let answer=request["fixture_approval"].as_str().ok_or("Writes require explicit fixture_approval once or deny")?;
            if !["once","deny"].contains(&answer){return Err("fixture_approval must be once or deny".into());}
            let approval=HostToolApproval::parse(&json!({"approval_kind":"host_tool","approval_id":id,
                "turn_id":format!("fixture-turn-{id}"),"typed_details":{"host_tool":{"app":owner,"tool":method,"args":args,
                "risk":"destructive","calling_kind":"app_peer","calling_peer":caller}}}),"fixture-session").ok_or("Invalid fixture host approval shape")?;
            let decisions:Arc<Mutex<Vec<bool>>>=Arc::default();let captured=decisions.clone();
            self.relay.handle(Event::Approval{app:caller.into(),account:Some(account.into()),approval,
                answer:ApprovalAnswer::new(move|v|captured.lock().unwrap().push(v))},&mut self.world);
            if let Some(sheet)=self.world.router.front_sheet().cloned(){
                for line in sheet.lines{
                    let pending=self.world.router.pending_request(&line.request).cloned().ok_or("Approval no longer pending")?;
                    if pending.app!=owner||pending.tool.name!=method||pending.args!=args{return Err("Approval arguments changed".into());}
                    self.world.router.answer(sheet.id,&line.request,if answer=="once"{Answer::Once}else{Answer::Deny},&ApprovalGesture::sheet_tap(),101)?;
                    self.world.approval_trace.push(json!({"sheet_id":sheet.id,"request":line.request.0,"owner":pending.app,"tool":pending.tool.name,"args":pending.args,"caller":pending.caller.as_audit(),"approved":answer=="once","fixture_gesture":true}));
                }
                for (id,decision,reason) in self.world.decisions.take(){self.relay.handle(Event::Decision{id,decision,reason},&mut self.world);}
            }
            if decisions.lock().unwrap().last()!=Some(&true){return Ok(json!({"ok":false,"error":{"kind":"fixture_approval_refused","message":"Real Relay/Router did not approve this fixture write"}}));}
            if request["revoke_after_approval"].as_bool()==Some(true){self.relay.catalog.set_grants("muse-goals","os.calendar",&[]);}
        }
        let mut call=HostToolCall::parse(&json!({"peer":"fixture-peer","session_id":"fixture-session","turn_id":format!("fixture-turn-{id}"),
            "call_id":id,"tool_call_id":format!("tool-{id}"),"name":method,"app":owner,"args":args,
            "args_digest":crate::approvals::facts::digest(&args),"risk":if write{"act"}else{"read"},"confirm_required":false}))?;
        call.calling_app=caller.into();call.account=Some(account.into());call.origin=CallOrigin::Context;
        let responses:Arc<Mutex<Vec<Value>>>=Arc::default();let captured=responses.clone();
        self.relay.handle(Event::Call{call,reply:ToolReply::new(&id,move|v|captured.lock().unwrap().push(v))},&mut self.world);
        let response=responses.lock().unwrap().last().cloned().ok_or("Real Relay did not synchronously reply")?;
        Ok(response)
    }
}
