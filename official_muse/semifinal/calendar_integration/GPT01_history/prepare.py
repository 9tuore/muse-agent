from pathlib import Path
import difflib, hashlib, json, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
SDK=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/runtime-closure-full-shell-r1/sdk')
STAGE=ROOT/'build'/('gpt01-calendar-history-'+sys.argv[1])
STAGE.mkdir(parents=True,exist_ok=False)
changes={}
def edit(path,before,after):
 old,new=changes.get(path,((SDK/path).read_text(),(SDK/path).read_text()))
 assert new.count(before)==1,(path,new.count(before))
 changes[path]=(old,new.replace(before,after))
p='crates/app-peers/src/broker.rs'
edit(p,'struct InFlight {\n    reply:', 'struct InFlight {\n    calendar_receipt: Option<Value>,\n    reply:')
edit(p,'    Done(ToolOutcome),','    Done(ToolOutcome, Option<Value>),\n    Cancelled(Value),')
old,new=changes[p];new=new.replace('Occurrence::Done(_)','Occurrence::Done(_, _) | Occurrence::Cancelled(_)').replace('Occurrence::Done(outcome))','Occurrence::Done(outcome, _))');changes[p]=(old,new)
edit(p,'            st.calls.remove(call_id);\n            let waiting =', '''            let metadata = st.calls.remove(call_id).and_then(|flight| flight.calendar_receipt)
                .or_else(|| match st.occurrences.get(occurrence) {
                    Some(Occurrence::Done(_, receipt)) => receipt.clone(), _ => None,
                });
            let receipt = metadata.map(|m| crate::calendar_history::finished(m, &outcome));
            let waiting =''')
edit(p,'Occurrence::Done(outcome.clone()));','Occurrence::Done(outcome.clone(), receipt));')
edit(p,'InFlight { reply: reply.clone(), occurrence, turn_id: call.turn_id.clone() }','InFlight { calendar_receipt: crate::calendar_history::metadata(&call, st.generation), reply: reply.clone(), occurrence, turn_id: call.turn_id.clone() }')
# Avoid overlapping mutable borrow of State while constructing the insertion.
edit(p,'            if !matches!(repeat, Some(Some(_))) {\n                st.calls.insert', '            if !matches!(repeat, Some(Some(_))) {\n                let generation = st.generation;\n                st.calls.insert')
old,new=changes[p];new=new.replace('metadata(&call, st.generation)','metadata(&call, generation)');changes[p]=(old,new)
edit(p,'            flight.map(|f| f.reply)\n        };\n        if reply.is_some_and(|r| r.cancel()) {', '''            flight
        };
        if reply.is_some_and(|flight| {
            if !flight.reply.cancel() { return false; }
            if let Some(mut receipt) = flight.calendar_receipt {
                receipt["terminal"] = json!("cancelled");
                let mut st = self.lock();
                if !st.occurrences.contains_key(&flight.occurrence) {
                    st.occurrence_order.push_back(flight.occurrence.clone());
                    st.occurrences.insert(flight.occurrence, Occurrence::Cancelled(receipt));
                    while st.occurrence_order.len() > REMEMBERED {
                        if let Some(old) = st.occurrence_order.pop_front() {
                            if matches!(st.occurrences.get(&old), Some(Occurrence::Done(_, _) | Occurrence::Cancelled(_))) {
                                st.occurrences.remove(&old);
                            }
                        }
                    }
                }
            }
            true
        }) {''')
edit(p, '                None => {\n                    st.occurrences.insert(occurrence.clone(), Occurrence::Running',
 '                None | Some(Occurrence::Cancelled(_)) => {\n                    st.occurrences.insert(occurrence.clone(), Occurrence::Running')
# The existing dedupe only replays Done; Cancelled follows the original retry path.
edit(p,'    /// A call was answered: its occurrence is done,', '''    fn calendar_history(&self, session: &str, history: &mut Value) {
        let st = self.lock();
        let mut seen = std::collections::HashSet::new();
        let receipts: Vec<Value> = st.occurrence_order.iter().filter(|key| seen.insert((*key).clone())).filter_map(|key| match st.occurrences.get(key) {
            Some(Occurrence::Done(_, Some(receipt)) | Occurrence::Cancelled(receipt)) => Some(receipt.clone()),
            _ => None,
        }).collect();
        crate::calendar_history::attach(history, session, st.generation, &receipts);
    }

    /// A call was answered: its occurrence is done,''')
edit(p,'                let history = inner\n                    .request(\n                        "session/hydrate",','                let mut history = inner\n                    .request(\n                        "session/hydrate",')
edit(p,'                    .await;\n                if self.conversation {','                    .await;\n                if let Ok(value) = &mut history { inner.calendar_history(&session, value); }\n                if self.conversation {')
edit(p,'                                Ok(mut old) => {\n                                    if let Value::Array(old)', '                                Ok(mut old) => {\n                                    inner.calendar_history(lane, &mut old);\n                                    if let Some(receipts) = old["host_calendar_receipts"].as_array() {\n                                        if let Some(all) = person["host_calendar_receipts"].as_array_mut() { all.extend(receipts.iter().cloned()); }\n                                    }\n                                    if let Value::Array(old)')
edit(p,'                    let system_agent = match peer_session.clone() {\n                        Some(peer) => inner.request("session/hydrate", json!({"session_id": peer, "include": ["messages"]})).await?,','''                    let system_agent = match peer_session.clone() {
                        Some(peer) => {
                            let mut value = inner.request("session/hydrate", json!({"session_id": peer, "include": ["messages"]})).await?;
                            inner.calendar_history(&peer, &mut value);
                            value
                        },''')
edit(p,'                    history.map(|person| merged_history(person, system_agent, &requests))','''                    history.map(|mut person| {
                        if let Some(receipts) = system_agent["host_calendar_receipts"].as_array() {
                            if let Some(all) = person["host_calendar_receipts"].as_array_mut() { all.extend(receipts.iter().cloned()); }
                        }
                        if let Some(all) = person["host_calendar_receipts"].as_array_mut() {
                            if all.len() > 32 { all.truncate(32); }
                        }
                        merged_history(person, system_agent, &requests)
                    })''')
edit('crates/app-peers/src/lib.rs','#[cfg(feature = "broker")]\npub mod broker;','#[cfg(feature = "broker")]\nmod calendar_history;\n#[cfg(feature = "broker")]\npub mod broker;')
# Shell history: generic rows remain unchanged; only exact Calendar rows receive evidence text.
p='crates/shell/src/app_chat/model.rs'
edit(p,'                "tool" => items.push(Item::Tool {','''                "tool" => {
                    let name = tools.name(row, turn.as_deref());
                    let previous = self.chat.items.iter().find(|item| matches!(item,
                        Item::Tool { call_id, turn: prior, .. } if !call_id.is_empty()
                            && call_id == row["tool_call_id"].as_str().unwrap_or("") && prior == &turn));
                    let (status, detail) = super::calendar_history::row_detail(row, previous)
                        .unwrap_or((crate::system_chat::model::ToolStatus::Done, String::new()));
                    items.push(Item::Tool {''')
edit(p,'                    name: tools.name(row, turn.as_deref()),\n                    status: crate::system_chat::model::ToolStatus::Done,\n                    detail: String::new(),','                    name,\n                    status,\n                    detail,')
edit(p,'                    seq: None,\n                }),\n                _ => {}','                    seq: None,\n                });\n                },\n                _ => {}')
edit(p,'    pub fn notice(&mut self, text: impl Into<String>) {','''    pub fn load_calendar_receipts(&mut self, receipts: &Value) {
        for receipt in receipts.as_array().into_iter().flatten().take(32) {
            let Some((id, name, turn, status, detail)) = super::calendar_history::receipt_item(receipt) else { continue };
            if self.chat.items.iter().any(|item| matches!(item, Item::Tool { call_id, turn: prior, .. }
                if call_id == &id && prior.as_deref() == Some(turn.as_str()))) { continue; }
            self.chat.items.push(Item::Tool { call_id: id, name, status, detail, turn: Some(turn), seq: None });
        }
    }

    pub fn notice(&mut self, text: impl Into<String>) {''')
p='crates/shell/src/app_chat/mod.rs'
edit(p,'pub mod model;','pub mod model;\nmod calendar_history;\n#[cfg(test)]\nmod history_receipt_tests;')
edit(p,'                Ok(value) => s.conversation.load_history(&value["messages"]),','''                Ok(value) => {
                    s.conversation.load_history(&value["messages"]);
                    s.conversation.load_calendar_receipts(&value["host_calendar_receipts"]);
                },''')
edit('crates/shell/src/system_chat/model.rs','    Running,\n    Done,\n    Failed,','    Running,\n    Done,\n    Failed,\n    Unverified,')
edit('crates/shell/src/system_chat/view.rs','                        ToolStatus::Failed => "failed",','                        ToolStatus::Failed => "failed",\n                        ToolStatus::Unverified => "unverified",')
changes['crates/shell/src/app_chat/history_receipt_tests.rs']=('',(HERE/'display_tests.rs').read_text())
changes['crates/app-peers/src/calendar_history.rs']=('',(HERE/'calendar_history.rs').read_text())
changes['crates/shell/src/app_chat/calendar_history.rs']=('',(HERE/'calendar_display.rs').read_text())
patch=''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p,(a,b) in changes.items())
(HERE/'GPT01-calendar-history.patch').write_text(patch)
for p,(a,b) in changes.items():
 dest=STAGE/'sdk'/p;dest.parent.mkdir(parents=True,exist_ok=True)
 if a:dest.write_text(a)
for mode in (['-C'],[]):
 r=subprocess.run(['/usr/bin/patch',*mode,'-p1','-F','0','-i',str(HERE/'GPT01-calendar-history.patch')],cwd=STAGE/'sdk',capture_output=True,text=True)
 with (HERE/'patchcheck.log').open('a') as f:f.write(r.stdout+r.stderr)
 assert r.returncode==0,r.stderr+r.stdout
assert all((STAGE/'sdk'/p).read_bytes()==b.encode() for p,(a,b) in changes.items())
# Compile the real patched app-peers source in an isolated broker-only harness.
peer=STAGE/'app-peers';shutil.copytree(SDK/'crates/app-peers/src',peer/'src')
for p,(a,b) in changes.items():
 if p.startswith('crates/app-peers/src/'):(peer/'src'/p.removeprefix('crates/app-peers/src/')).write_text(b)
(peer/'Cargo.toml').write_text('''[package]
name="gpt01-app-peers-history-check"
version="0.0.0"
edition="2021"
[features]
default=["broker"]
broker=[]
octos-core=[]
ws=[]
[dependencies]
serde_json="=1.0.151"
tokio={version="=1.53.1",features=["rt-multi-thread","sync","time","macros"]}
log="=0.4.34"
uuid={version="=1.26.1",features=["v4"]}
''')
receipt={'state':'PATCH_PREPARED_TEST_PENDING','source_sdk':str(SDK),'worktree':str(ROOT),'isolated_target':str(STAGE/'target'),
 'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'zero_fuzz_apply':True,
 'files':[{'path':p,'before':hashlib.sha256(a.encode()).hexdigest(),'after':hashlib.sha256(b.encode()).hexdigest()} for p,(a,b) in changes.items()]}
(HERE/'RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(str(STAGE))
