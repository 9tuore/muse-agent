//! L2 synthetic integration: the real service dispatch, composer, review and draft engine.
//! Only Vault/Transport and native physical input are fixture dependencies.
use super::*;
use std::{io::{BufRead,BufReader,Write},process::{Child,ChildStdin,ChildStdout,Command,Stdio},sync::atomic::{AtomicBool,AtomicUsize,Ordering},time::Duration};
const APP:&str="night004.synthetic-mail";
struct SyntheticVault;
impl Vault for SyntheticVault {
    fn put(&self,_:&vault::Place,_:&str,_:&str)->Result<(),String>{Ok(())}
    fn get(&self,_:&vault::Place,_:&str)->Result<String,String>{Ok("synthetic-fixture-only".into())}
    fn remove(&self,_:&vault::Place,_:&str){}
}
struct Recipient {child:Child,input:Option<ChildStdin>,output:BufReader<ChildStdout>}
impl Recipient {
    fn new(root:&Path)->Self {let mut child=Command::new("python3").arg(std::env::var("NIGHT004_RECEIVER_SCRIPT").expect("fixture script")).arg(root.join("receiver.json")).stdin(Stdio::piped()).stdout(Stdio::piped()).spawn().unwrap();let input=child.stdin.take();let output=BufReader::new(child.stdout.take().unwrap());Self{child,input,output}}
    fn deliver(&mut self,payload:&Value)->Result<Value,String>{writeln!(self.input.as_mut().unwrap(),"{}",json!({"payload":payload})).map_err(|e|e.to_string())?;self.input.as_mut().unwrap().flush().map_err(|e|e.to_string())?;let mut line=String::new();self.output.read_line(&mut line).map_err(|e|e.to_string())?;serde_json::from_str(&line).map_err(|e|e.to_string())}
}
impl Drop for Recipient {fn drop(&mut self){self.input.take();let _=self.child.wait();}}
struct MockTransport {receiver:Mutex<Recipient>,mode:Mutex<String>,calls:AtomicUsize,pause:AtomicBool,entered:AtomicBool,release:AtomicBool}
impl Transport for MockTransport {
    fn test(&self,_:&Value)->Result<(),String>{Ok(())}
    fn folders(&self,_:&Value)->Result<Vec<Value>,String>{Ok(vec![])}
    fn fetch(&self,_:&Value,_:&str,_:&Value)->Result<Value,String>{Ok(json!({"messages":[],"state":{},"reset":false}))}
    fn mark_seen(&self,_:&Value,_:&str,_:&Value)->Result<(),String>{Ok(())}
    fn send(&self,_:&Value,p:&Value)->Result<Value,String>{self.receiver.lock().unwrap().deliver(p)}
    fn send_checked(&self,a:&Value,p:&Value)->Result<Value,drafts::SendFailure>{self.calls.fetch_add(1,Ordering::SeqCst);let mode=self.mode.lock().unwrap().clone();if mode=="before"{return Err(drafts::SendFailure::BeforeDelivery("synthetic pre-delivery refusal".into()))}let receipt=self.send(a,p).map_err(drafts::SendFailure::Unknown)?;self.entered.store(true,Ordering::SeqCst);if self.pause.load(Ordering::SeqCst){for _ in 0..1000{if self.release.load(Ordering::SeqCst){break}std::thread::sleep(Duration::from_millis(5));}assert!(self.release.load(Ordering::SeqCst),"fixture release timeout");}if mode=="unknown"{Err(drafts::SendFailure::Unknown("synthetic receipt lost after recipient accepted".into()))}else{Ok(receipt)}}
}
#[derive(Default)]struct Surface;
impl ServiceHost for Surface {fn open_sheet(&mut self,_:String){}fn close_sheet(&mut self){}}
static NEXT:AtomicUsize=AtomicUsize::new(991_004);
struct Fixture {root:PathBuf,transport:Arc<MockTransport>,pending:Arc<Mutex<Option<public_review::ReviewRequest>>>}
impl Fixture {
    fn new()->Self {let base=PathBuf::from(std::env::var("NIGHT004_TMP_ROOT").expect("owned fixture root"));std::fs::create_dir_all(&base).unwrap();Self::at(base.join(format!("case-{}-{}",std::process::id(),NEXT.fetch_add(1,Ordering::SeqCst))))}
    fn at(root:PathBuf)->Self {std::fs::create_dir_all(&root).unwrap();let store=Store::at(&root,Arc::new(SyntheticVault));if !store.dir.join("accounts.json").exists(){store.save_accounts(&[json!({"id":"one","address":"sender@example.invalid","apps":[APP],"signed_in":1})]).unwrap();}let transport=Arc::new(MockTransport{receiver:Mutex::new(Recipient::new(&root)),mode:Mutex::new("accepted".into()),calls:AtomicUsize::new(0),pause:AtomicBool::new(false),entered:AtomicBool::new(false),release:AtomicBool::new(false)});register_with_vault(transport.clone(),Arc::new(SyntheticVault));let pending:Arc<Mutex<Option<public_review::ReviewRequest>>>=Arc::default();let capture=pending.clone();public_review::on_review(Some(Arc::new(move|request|{*capture.lock().unwrap()=Some(request);Ok("synthetic native surface".into())})));Self{root,transport,pending}}
    fn send_as(&self,app:&str,method:&str,args:Value)->usize {let heap=NEXT.fetch_add(1,Ordering::SeqCst);octosense_appstore::services::dispatch(ServiceCall{app_id:app.into(),service:method.into(),args,from_sheet:false,may_prompt:true,host_dir:self.root.clone()},heap,1,&mut Surface);heap}
    fn send(&self,method:&str,args:Value)->usize{self.send_as(APP,method,args)}
    fn wait(&self,heap:usize)->Result<Value,String>{for _ in 0..1000{if let Some((_,_,r))=octosense_appstore::services::take_replies_for(&[heap]).pop(){return r.map(|s|serde_json::from_str(&s).unwrap())}std::thread::sleep(Duration::from_millis(5));}panic!("no production dispatch reply {heap}")}
    fn ask(&self,method:&str,args:Value)->Result<Value,String>{self.wait(self.send(method,args))}
    fn args(&self)->Value{json!({"account":"one","to":"receiver@example.invalid","subject":"NIGHT004 synthetic","body":"Version one"})}
    fn review(&self,args:Value)->(usize,public_review::ReviewRequest){let heap=self.send("mail.review_send",args);let mut request=self.pending.lock().unwrap().take().unwrap();for _ in 0..1000{let _=request.result();if !request.is_preparing(){break}std::thread::sleep(Duration::from_millis(5));}assert!(!request.is_preparing());(heap,request)}
    fn status(&self,d:&Value)->Value{self.ask("mail.compose_status",json!({"account":"one","compose_id":d["compose_id"]})).unwrap()}
    fn review_args(&self,d:&Value)->Value{let mut a=self.args();a["body"]=d["body"].clone();a["compose_id"]=d["compose_id"].clone();a["expected_revision"]=d["revision"].clone();a}
    fn rows(&self)->Vec<Value>{let p=self.root.join("receiver.json");if p.exists(){serde_json::from_slice(&std::fs::read(p).unwrap()).unwrap()}else{vec![]}}
}
impl Drop for Fixture {fn drop(&mut self){self.transport.release.store(true,Ordering::SeqCst);public_review::on_review(None);drafts::on_claim(None);}}
#[test]fn l2_compose_edit_reject_cancel_accept_independent_recipient(){let f=Fixture::new();let d=f.ask("mail.compose",f.args()).unwrap();assert_eq!(d["status"],"draft");let (old_heap,mut old)=f.review(f.review_args(&d));assert!(old.can_approve());assert!(old.approve(false,true).is_err());assert!(old.approve(true,false).is_err());let mut edit=f.review_args(&d);edit["body"]=json!("Version two");let d2=f.ask("mail.compose",edit).unwrap();assert_eq!(d2["revision"],2);old.approve(true,true).unwrap();assert!(f.wait(old_heap).unwrap_err().contains("revision_conflict"));assert_eq!(f.transport.calls.load(Ordering::SeqCst),0);let (cancel_heap,mut cancelled)=f.review(f.review_args(&d2));cancelled.cancel().unwrap();assert!(f.wait(cancel_heap).unwrap_err().contains("cancelled"));assert_eq!(f.rows().len(),0);let (heap,mut approved)=f.review(f.review_args(&d2));assert!(approved.can_approve());approved.approve(true,true).unwrap();let receipt=f.wait(heap).unwrap();assert_eq!(receipt["accepted"],true);assert_eq!(receipt["compose_id"],d2["compose_id"]);assert!(approved.approve(true,true).is_err());let state=f.status(&d2);assert_eq!(state["status"],"accepted");assert_eq!(state["revision"],2);let rows=f.rows();assert_eq!(rows.len(),1);assert_eq!(rows[0]["body"],"Version two");assert_eq!(rows[0]["message_id"],state["attempts"].as_array().unwrap().last().unwrap()["payload"]["message_id"]);assert_eq!(f.transport.calls.load(Ordering::SeqCst),1);assert!(f.wait(f.send_as("other.synthetic-app","mail.compose_status",json!({"account":"one","compose_id":d2["compose_id"]}))).is_err());}
#[test]fn l2_known_failure_and_unknown_never_automatically_resubmit(){for mode in ["before","unknown"]{let f=Fixture::new();*f.transport.mode.lock().unwrap()=mode.into();let d=f.ask("mail.compose",f.args()).unwrap();let (heap,mut r)=f.review(f.review_args(&d));r.approve(true,true).unwrap();assert!(f.wait(heap).is_err());let state=f.status(&d);assert_eq!(state["status"],if mode=="before"{"failed_before_delivery"}else{"outcome_unknown"});assert_eq!(f.rows().len(),if mode=="before"{0}else{1});let (retry_heap,mut retry)=f.review(f.review_args(&d));assert!(!retry.can_approve());assert!(retry.approve(true,true).is_err());assert!(f.wait(retry_heap).is_err());assert_eq!(f.transport.calls.load(Ordering::SeqCst),1);assert_eq!(f.status(&d)["attempts"].as_array().unwrap().len(),1);}}
#[test]fn l2_persist_failure_keeps_transport_and_recipient_untouched(){let f=Fixture::new();let d=f.ask("mail.compose",f.args()).unwrap();let (heap,mut r)=f.review(f.review_args(&d));let store=Store::at(&f.root,Arc::new(SyntheticVault));let path=std::fs::read_dir(&store.dir).unwrap().flat_map(|e|std::fs::read_dir(e.unwrap().path()).into_iter().flatten()).filter_map(|e|e.ok().map(|e|e.path())).find(|p|p.file_stem()==Some(std::ffi::OsStr::new(text(&d,"draft_id")))).expect("the real persisted draft");std::fs::create_dir(path.with_extension("tmp")).unwrap();r.approve(true,true).unwrap();assert!(f.wait(heap).is_err());assert_eq!(f.transport.calls.load(Ordering::SeqCst),0);assert!(f.rows().is_empty());}
#[test]fn l2_late_reply_after_origin_closed_does_not_resend_or_publish(){let f=Fixture::new();f.transport.pause.store(true,Ordering::SeqCst);let d=f.ask("mail.compose",f.args()).unwrap();let (heap,mut r)=f.review(f.review_args(&d));r.approve(true,true).unwrap();for _ in 0..1000{if f.transport.entered.load(Ordering::SeqCst){break}std::thread::sleep(Duration::from_millis(5));}assert!(f.transport.entered.load(Ordering::SeqCst));octosense_appstore::services::cancel_heap(heap);f.transport.release.store(true,Ordering::SeqCst);for _ in 0..1000{if f.status(&d)["status"]=="accepted"{break}std::thread::sleep(Duration::from_millis(5));}assert_eq!(f.status(&d)["status"],"accepted");assert!(octosense_appstore::services::take_replies_for(&[heap]).is_empty());assert_eq!(f.rows().len(),1);assert_eq!(f.transport.calls.load(Ordering::SeqCst),1);}
#[test]fn l2_claim_guard_rejection_and_removed_grant_prevent_transport(){let f=Fixture::new();let d=f.ask("mail.compose",f.args()).unwrap();let (heap,mut r)=f.review(f.review_args(&d));drafts::on_claim(Some(Arc::new(|_,_,_|Err("synthetic host claim guard refused".into()))));r.approve(true,true).unwrap();assert!(f.wait(heap).unwrap_err().contains("claim guard"));assert_eq!(f.transport.calls.load(Ordering::SeqCst),0);drafts::on_claim(None);let (heap,mut r)=f.review(f.review_args(&d));let store=Store::at(&f.root,Arc::new(SyntheticVault));store.save_accounts(&[json!({"id":"one","address":"sender@example.invalid","apps":[],"signed_in":1})]).unwrap();r.approve(true,true).unwrap();assert!(f.wait(heap).is_err());assert!(f.rows().is_empty());}
#[test]fn l2_real_process_restart_retains_same_id_without_resubmission(){for mode in ["accepted","unknown"]{let f=Fixture::new();let root=f.root.clone();drop(f);for phase in ["send","restore"]{let result=Command::new(std::env::current_exe().unwrap()).args(["--exact","night004_l2::restart_child_driver","--ignored","--nocapture","--test-threads=1"]).env("NIGHT004_CHILD_ROOT",&root).env("NIGHT004_CHILD_PHASE",phase).env("NIGHT004_CHILD_MODE",mode).output().unwrap();std::fs::write(root.join(format!("child-{phase}.txt")),[result.stdout.as_slice(),result.stderr.as_slice()].concat()).unwrap();assert!(result.status.success(),"child {phase} failed");}let proof:Value=serde_json::from_slice(&std::fs::read(root.join("restart-proof.json")).unwrap()).unwrap();assert_eq!(proof["restored"],true);assert_eq!(proof["new_transport_calls"],0);}}
#[test]#[ignore="subprocess fixture driver; invoked only by parent with owned root"]fn restart_child_driver(){let root=PathBuf::from(std::env::var("NIGHT004_CHILD_ROOT").unwrap());let phase=std::env::var("NIGHT004_CHILD_PHASE").unwrap();let mode=std::env::var("NIGHT004_CHILD_MODE").unwrap();let f=Fixture::at(root.clone());if phase=="send"{*f.transport.mode.lock().unwrap()=mode.clone();let d=f.ask("mail.compose",f.args()).unwrap();let (heap,mut r)=f.review(f.review_args(&d));r.approve(true,true).unwrap();let result=f.wait(heap);assert_eq!(result.is_ok(),mode=="accepted");let state=f.status(&d);assert_eq!(f.rows().len(),1);std::fs::write(root.join("query.json"),state.to_string()).unwrap();}else{let prior:Value=serde_json::from_slice(&std::fs::read(root.join("query.json")).unwrap()).unwrap();let state=f.status(&prior);assert_eq!(state["compose_id"],prior["compose_id"]);assert_eq!(state["status"],prior["status"]);assert_eq!(state["attempts"],prior["attempts"]);let (heap,mut r)=f.review(f.review_args(&state));assert!(!r.can_approve());assert!(r.approve(true,true).is_err());assert!(f.wait(heap).is_err());assert_eq!(f.rows().len(),1);assert_eq!(f.transport.calls.load(Ordering::SeqCst),0);std::fs::write(root.join("restart-proof.json"),json!({"restored":true,"new_transport_calls":0,"same_compose_id":state["compose_id"],"status":state["status"],"same_message_id":state["attempts"].as_array().unwrap().last().unwrap()["payload"]["message_id"]}).to_string()).unwrap();}}

/// L3 boundary helper: actual service protocol on child stdio; decisions are explicitly synthetic.
#[test]
#[ignore = "persistent helper invoked by owned orchestration only"]
fn l3_protocol_driver() {
    let base=PathBuf::from(std::env::var("NIGHT004_TMP_ROOT").unwrap()).canonicalize().unwrap();
    let root=PathBuf::from(std::env::var("NIGHT004_L3_ROOT").unwrap());
    assert!(root.is_absolute() && root.starts_with(&base));
    let marker=root.join("night004-synthetic-state.txt");
    if root.exists(){assert_eq!(std::fs::read_to_string(&marker).unwrap(),"NIGHT004 synthetic Mail fixture only\n");}
    let f=Fixture::at(root);
    std::fs::write(marker,"NIGHT004 synthetic Mail fixture only\n").unwrap();
    for line in std::io::stdin().lock().lines() {
        let line=line.unwrap();let request:Value=serde_json::from_str(&line).unwrap();
        let id=request["id"].clone();let method=text(&request,"method");
        if method=="fixture.quit" { println!("{}",json!({"id":id,"is_ok":true,"data":{"quit":true}}));std::io::stdout().flush().unwrap();break; }
        let result=if method=="fixture.receiver" {Ok(json!({"received":f.rows(),"transport_calls":f.transport.calls.load(Ordering::SeqCst),"real_smtp_calls":0}))}
        else if method=="fixture.mode" {*f.transport.mode.lock().unwrap()=text(&request,"mode").into();Ok(json!({"mode":text(&request,"mode")}))}
        else if method=="mail.review_send" {
            let (heap,mut review)=f.review(request["args"].clone());
            if review.can_approve(){match text(&request,"decision") {
                "approve"=>{review.approve(true,true).unwrap();},
                "reject"=>{assert!(review.approve(false,true).is_err());review.cancel().unwrap();},
                _=>{review.cancel().unwrap();},
            }}
            f.wait(heap)
        }
        else if matches!(method,"mail.accounts"|"mail.compose"|"mail.compose_status"){f.ask(method,request["args"].clone())}
        else {Err("unsupported synthetic helper method".into())};
        let response=match result{Ok(data)=>json!({"id":id,"is_ok":true,"data":data}),Err(error)=>json!({"id":id,"is_ok":false,"error":error})};
        println!("{response}");std::io::stdout().flush().unwrap();
    }
}
