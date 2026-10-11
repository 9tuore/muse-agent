"""Rebuild the minimal diff, dry-run it on copied baselines, prepare a narrow fixture harness."""
from pathlib import Path
import difflib,hashlib,json,shutil,subprocess
HERE=Path(__file__).resolve().parent
BASE=HERE/'baseline';PATCHED=HERE/'patched'
meta=json.loads((HERE/'BASELINE.json').read_text())
for path,sha in meta['sha256'].items():
    assert hashlib.sha256((BASE/path).read_bytes()).hexdigest()==sha,path
files=sorted(p.relative_to(PATCHED).as_posix() for p in PATCHED.rglob('*.rs'))
changes={p:((BASE/p).read_text() if (BASE/p).exists() else '',(PATCHED/p).read_text()) for p in files}
changes={p:(a,b) for p,(a,b) in changes.items() if a!=b}
patch=''.join(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='a/'+p,tofile='b/'+p)) for p,(a,b) in changes.items())
(HERE/'GPT01-continuity.patch').write_text(patch)
check=HERE/'patchcheck';shutil.rmtree(check,ignore_errors=True);shutil.copytree(BASE,check)
outputs=[]
for args in (['-C'],[]):
    r=subprocess.run(['/usr/bin/patch',*args,'-p1','-F','0','-i',str(HERE/'GPT01-continuity.patch')],cwd=check,text=True,capture_output=True)
    outputs.append(r.stdout+r.stderr);assert r.returncode==0,outputs[-1]
assert all((check/p).read_text()==b for p,(_,b) in changes.items())
(HERE/'patchcheck.log').write_text(''.join(outputs)+'PASS: zero-fuzz dry-run, apply, byte comparison against patched snapshot.\n')
harness=HERE/'harness';(harness/'src/system_chat').mkdir(parents=True,exist_ok=True)
# Real peer contracts and tool reply implementation; no broker, core, or runtime dependency.
for name in ['contract','host_tools']:
    src=HERE/'support'/(name+'.rs');shutil.copy2(src,harness/f'src/{name}.rs')
for name in ['model','session','continuity','continuity_tests']:
    src=PATCHED/f'crates/shell/src/system_chat/{name}.rs'
    text=src.read_text()
    if name=='session':
        text=text.replace('makepad_widgets::log!','log::info!').replace('crate::host_tools::','crate::shell_host_tools::')
    (harness/f'src/system_chat/{name}.rs').write_text(text)
for file,sha in meta['harness_support_sha256'].items():
    assert hashlib.sha256((HERE/'support'/file).read_bytes()).hexdigest()==sha,file
strip=(HERE/'support/strip_note.rs').read_text()
cap=str(meta['session_tool_cap'])
(harness/'src/lib.rs').write_text('''#![allow(unexpected_cfgs)]
pub mod contract;
pub use contract::*;
pub mod host_tools;
pub mod ai_host { pub mod app_peers { pub use crate::{host_tools, TurnTrigger}; } }
// Doubles for shell discovery; fixture SystemHost provides all policy/grants.
pub mod shell_host_tools {
    pub fn ensure_loaded(_: &str) {}
    pub fn owner_of(_: &str) -> Option<String> { None }
    pub fn declaration(_: &str, _: &str) -> Option<serde_json::Value> { None }
}
pub mod agents {
    pub fn declarations() -> Vec<serde_json::Value> { Vec::new() }
'''+strip+'''
}
pub mod system_chat {
    pub mod continuity;
    pub mod model;
    pub mod session;
    pub mod grants {
        pub const MAX_SESSION_TOOLS: usize = '''+cap+''';
        pub fn host_tools() -> Vec<String> { Vec::new() }
        pub fn is_engine_tool(_: &str) -> bool { false }
    }
    #[cfg(test)] mod continuity_tests;
}
''')
(harness/'Cargo.toml').write_text('''[package]
name="gpt01-continuity-check"
version="0.0.0"
edition="2021"
[dependencies]
serde_json="=1.0.151"
log="=0.4.34"
''')
(HERE/'RESULT.json').write_text(json.dumps({'state':'CODE_PREPARED_FIXTURE_TEST_PENDING','baseline':meta,
    'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),'zero_fuzz_apply':True,
    'changed_files':[{ 'path':p, 'before_sha256':hashlib.sha256(a.encode()).hexdigest() if a else None,
                       'after_sha256':hashlib.sha256(b.encode()).hexdigest()} for p,(a,b) in changes.items()],
    'harness_adapters':['real peer contract and host_tools; makepad log macro becomes log::info',
                        'shell grant/tool-discovery doubles; actual Driver, model, loop controls, tests unchanged',
                        'kernel cfg is off; Native profile-file reader, view.rs and mod.rs are not typechecked by this harness'],
    'live_model_calls':0,'gui_runs':0,'shared_sdk_writes':0,'product_status':'PARTIAL_COST_GATE_NOT_CONNECTED'},indent=2)+'\n')
print(f'Prepared {len(changes)}-file patch; harness: {harness}')
