from pathlib import Path
import difflib, hashlib, json, subprocess
ROOT = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
OUT = ROOT / 'official_muse/semifinal/calendar_integration'
BASE = ROOT / 'build/runtime-closure-full-shell-r1'
STAGE = OUT / 'INTEGRATED_PATCHCHECK'
STAGE.mkdir(exist_ok=False)
changes = {'hub': {}, 'sdk': {}, 'witness': {}}
def edit(group, tree, path, before, after):
    key = (tree, path)
    original, current = changes[group].get(key, ((BASE/tree/path).read_text(), (BASE/tree/path).read_text()))
    assert current.count(before) == 1, (group, path, current.count(before))
    changes[group][key] = (original, current.replace(before, after))
helper = '''
// A compiled host ceiling, separate from the person's agent consent. The
// embedding explicitly enables it at startup; standalone AppStore stays off.
static MUSE_CALENDAR_ENABLED: std::sync::atomic::AtomicBool =
    std::sync::atomic::AtomicBool::new(false);
const MUSE_CALENDAR_TOOLS: &[&str] = &[
    "calendar.events", "calendar.get_event", "calendar.add_event", "calendar.notify",
];

pub fn set_muse_calendar_integration_enabled(enabled: bool) {
    MUSE_CALENDAR_ENABLED.store(enabled, std::sync::atomic::Ordering::Release);
}

/// Call only after catalog authentication and the embedding's sequence floor.
/// Every agent admission recomputes this ceiling, including when disabled.
/// This neither sets consent nor grants a raw Calendar service capability.
pub fn configure_muse_calendar_offers(store: &mut Store) -> Result<(), String> {
    const APP: &str = "muse-goals";
    if !MUSE_CALENDAR_ENABLED.load(std::sync::atomic::Ordering::Acquire)
        || !store.entry(APP).is_some_and(|entry| entry.status.is_offered())
    {
        return store.set_agent_tool_offers(APP, &[]);
    }
    if let Err(error) = store.set_agent_tool_offers(APP, MUSE_CALENDAR_TOOLS) {
        store.set_agent_tool_offers(APP, &[])?;
        return Err(error);
    }
    Ok(())
}
'''
edit('hub', 'hub', 'crates/appstore/src/lib.rs', '\npub fn set_data_root(root: PathBuf) {', helper+'\npub fn set_data_root(root: PathBuf) {')
edit('hub', 'hub', 'crates/app-hub-app/src/catalog.rs',
'                    .and_then(|()| self.remember_sequence(self.store.catalog().unwrap().sequence))',
'                    .and_then(|()| self.remember_sequence(self.store.catalog().unwrap().sequence))\n                    .and_then(|()| octosense_appstore::configure_muse_calendar_offers(&mut self.store))')
edit('hub', 'hub', 'crates/app-hub-app/src/catalog.rs',
'            self.store = candidate;\n            self.persistence_failed = false;',
'            octosense_appstore::configure_muse_calendar_offers(&mut candidate)?;\n            self.store = candidate;\n            self.persistence_failed = false;')
edit('sdk', 'sdk', 'crates/shell/src/apps.rs',
'    ONCE.call_once(|| {\n        crate::ai_host::set_model_grants',
'    ONCE.call_once(|| {\n        #[cfg(any(feature = "app-hub", native_mobile))]\n        octosense_appstore::set_muse_calendar_integration_enabled(true);\n        crate::ai_host::set_model_grants')
edit('sdk', 'sdk', 'crates/shell/src/host_tools/admission.rs',
'    )?;\n    store.may_run(app).map_err',
'    )?;\n    octosense_appstore::configure_muse_calendar_offers(&mut store)?;\n    store.may_run(app).map_err')
edit('sdk', 'sdk', 'crates/shell/src/glance_card.rs',
'            )?;\n            store.may_run(app)?',
'            )?;\n            octosense_appstore::configure_muse_calendar_offers(&mut store)?;\n            store.may_run(app)?')
witness = '''        // Metadata only, after the broker stamped and checked this call.
        // Relay authorization/results remain on the existing audited path.
        if app_of_peer(&call.calling_app) == "muse-goals" && call.app == "os.calendar"
            && matches!(call.name.as_str(), "calendar.events" | "calendar.get_event"
                | "calendar.add_event" | "calendar.notify")
        {
            let id = |value: &str| {
                if !value.is_empty() && value.len() <= 256
                    && value.bytes().all(|b| b.is_ascii_alphanumeric()
                        || matches!(b, b'-' | b'_' | b'.' | b':' | b'#'))
                { value.to_owned() } else { "[missing/invalid]".to_owned() }
            };
            let metadata = serde_json::json!({
                "phase": "broker_checked_received",
                "caller": "app/muse-goals", "owner": "os.calendar", "tool": call.name,
                "call_id": id(&call.call_id), "tool_call_id": id(&call.tool_call_id),
                "session_id": id(&call.session_id), "turn_id": id(&call.turn_id),
                "context_id": call.context_id.as_deref().map(id),
                "client": call.client.as_deref().map(id),
                "account": if call.account.as_deref() == Some("device") { "device" } else { "[other]" },
                "origin": format!("{:?}", call.origin), "trigger": call.trigger.as_str(),
                "args_digest": crate::approvals::facts::digest(&call.args),
                "limit": if call.name == "calendar.events" { call.args.get("limit").and_then(Value::as_u64) } else { None },
            });
            makepad_widgets::log!("[muse-calendar-call-map] {metadata}");
        }
'''
edit('witness', 'sdk', 'crates/shell/src/host_tools/mod.rs',
'    fn tool_call(&self, call: HostToolCall, reply: ToolReply) {\n        submit(Event::Call { call, reply });',
'    fn tool_call(&self, call: HostToolCall, reply: ToolReply) {\n'+witness+'        submit(Event::Call { call, reply });')
receipt = {'state':'PROPOSED_NOT_COMPILED_NOT_LIVE', 'checks':[], 'patches':{},
           'writes':'only new INTEGRATED_* under calendar_integration',
           'cargo_gui_model_calendar_git_executed':False}
for group, files in changes.items():
    diff = ''.join(''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='a/'+path, tofile='b/'+path)) for (tree,path),(old,new) in files.items())
    patch = OUT / ('INTEGRATED_'+group.upper()+'.patch')
    patch.write_text(diff)
    sandbox = STAGE / group
    sandbox.mkdir()
    for (tree,path),(old,new) in files.items():
        dest = sandbox/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(old)
    checked = subprocess.run(['/usr/bin/patch','-C','-p1','-F','0','-i',str(patch)],cwd=sandbox,capture_output=True,text=True)
    applied = subprocess.run(['/usr/bin/patch','-p1','-F','0','-i',str(patch)],cwd=sandbox,capture_output=True,text=True)
    matched = all((sandbox/path).read_bytes() == new.encode() for (tree,path),(old,new) in files.items())
    assert checked.returncode == applied.returncode == 0 and matched
    receipt['patches'][patch.name] = hashlib.sha256(patch.read_bytes()).hexdigest()
    receipt['checks'].append({'group':group,'dry_run_exit':checked.returncode,'apply_exit':applied.returncode,'byte_match':matched,
        'files':[{'tree':tree,'path':path,'before_sha256':hashlib.sha256(old.encode()).hexdigest(),'after_sha256':hashlib.sha256(new.encode()).hexdigest()} for (tree,path),(old,new) in files.items()]})
    (OUT/('INTEGRATED_'+group.upper()+'_PATCHCHECK.log')).write_text(checked.stdout+checked.stderr+applied.stdout+applied.stderr)
(OUT/'INTEGRATED_RESULT.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt,indent=2))
