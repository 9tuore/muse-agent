from pathlib import Path
import hashlib,json,re,shutil
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
SDK=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/runtime-closure-full-shell-r1/sdk')
STAGE=OWN/'build/gpt01-night004-calendar'
ROOT=STAGE/'relay';ROOT.mkdir(exist_ok=False)
inputs={}
def read(name):
    p=SDK/name;data=p.read_text();inputs[name]=hashlib.sha256(p.read_bytes()).hexdigest();return data
def write(name,data):
    p=ROOT/'src'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
for name in ['types','audit','contacts','facts','relay','router','rules','sheet']:
    write('approvals/'+name+'.rs',read('crates/shell/src/approvals/'+name+'.rs'))
s=read('crates/shell/src/approvals/dev_hooks.rs')
write('approvals/dev_hooks.rs',s[:s.index('fn connection(')]+s[s.index('/// The test double:'):])
s=read('crates/shell/src/approvals/mod.rs')
private=s[s.index('pub(crate) fn create_private_dir'):]
# The file ends after these two helpers; verify, do not guess additional code.
assert private.rstrip().endswith('std::fs::rename(&tmp, path)\n}')
write('approvals/mod.rs','use std::path::Path;\npub mod audit;pub mod contacts;pub mod dev_hooks;pub mod facts;pub mod relay;pub mod router;pub mod rules;pub mod sheet;pub mod types;\npub use relay::{ApprovalIntake,ApprovalRelay,RecordingRelay};\npub use router::{Route,Router};\npub use types::{Caller,Decision,RequestContext,RequestId,ToolSpec,Trigger};\npub fn now()->u64{std::time::SystemTime::now().duration_since(std::time::UNIX_EPOCH).unwrap().as_secs()}\n'+private)
for name in ['relay','schema']:
    write('host_tools/'+name+'.rs',read('crates/shell/src/host_tools/'+name+'.rs'))
s=read('crates/shell/src/peer_link/link.rs')
parts=[s[s.index('#[derive(Clone, Debug, PartialEq)]\npub enum ToolCallResult'):s.index('/// The seam home-96')],
       s[s.index('#[derive(Clone, Debug, PartialEq)]\npub struct KernelToolCall'):s.index('/// Who owns a request context')]]
w=read('crates/shell/src/peer_link/wire.rs')
risk=w[w.index('#[derive(Clone, Copy, Debug, PartialEq, Eq)]\npub enum Risk'):w.index('/// A tool call as the app gets it')]
write('peer_link.rs','use serde_json::Value;\nuse crate::approvals::{Caller,Trigger};\n'+risk+'\n'.join(parts))
write('lib.rs',(HERE/'relay_support.rs').read_text())
write('relay_tests.rs',(HERE/'relay_tests.rs').read_text())
shutil.copyfile(SDK/'apps/calendar/bundle/tools.json',ROOT/'calendar-tools.json')
peer=STAGE/'peer';shutil.copytree(SDK/'crates/app-peers/src',peer/'src')
shutil.copyfile(HERE.parent/'GPT01_calendar_crud/peer-Cargo.toml',peer/'Cargo.toml')
(ROOT/'Cargo.toml').write_text('[package]\nname="gpt01-night004-relay"\nversion="0.0.0"\nedition="2021"\n[features]\napp-hub=[]\n[dependencies]\nserde={version="=1.0.229",features=["derive"]}\nserde_json="=1.0.151"\nsha2="=0.10.9"\noctosense-app-peers={package="gpt01-app-peers-history-check",path="../peer"}\ngpt01-night004-calendar={path="../service"}\n')
(HERE/'RELAY_BASELINE.json').write_text(json.dumps({'source_sdk':str(SDK),'source_sha256':inputs,'scope':'Unchanged real Relay, Catalog, schema, approval Router/Rules/Contacts/Facts/Audit/Sheet; real CalendarService as executor. Native/file/peer endpoints excluded via explicit panic adapters. Authorization and sheet gestures are synthetic fixture only.'},ensure_ascii=False,indent=2)+'\n')
print(str(ROOT))
