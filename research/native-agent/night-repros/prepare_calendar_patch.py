"""Prepare a local proposed upstream patch; never install or alter production."""
from pathlib import Path
import json,shutil,difflib
ROOT=Path(__file__).resolve().parents[3]
OFF=ROOT/'.local-state/native-agent-upstream/OctoSense'
PATCH=ROOT/'.local-state/night-calendar-patched'
BASE=ROOT/'.local-state/night-calendar'
shutil.copytree(BASE,PATCH,dirs_exist_ok=True)
source=(OFF/'apps/calendar/host-service/src/lib.rs').read_text()
helper = (ROOT/'research/native-agent/night-repros/upstream_get_event.rs').read_text() + '\n'
anchor='/// The service the Card runner (and the agent\'s tools) call.'
assert source.count(anchor)==1
patched=source.replace(anchor,helper+anchor).replace('"view" => ui::view(host_dir, args, now),','"view" => ui::view(host_dir, args, now),\n        "get_event" => get_event(host_dir, args),')
patched += '\n' + (ROOT/'research/native-agent/night-repros/upstream_calendar_tests.rs').read_text()
# Use the same isolated adapter-removal seam as the baseline.
a=patched.index(anchor);b=patched.index('#[cfg(test)]\nmod tests',a)
core=patched[:a].replace('use octosense_appstore::services::{HostService, Replier, ServiceCall, ServiceHost};\n','')+patched[b:]
(PATCH/'src/lib.rs').write_text(core+'\npub mod relay_catalog;\n')
tools_path='apps/calendar/bundle/tools.json'
raw=(OFF/tools_path).read_text();tools=json.loads(raw)
for tool in tools['tools']:
    if tool['name'] in ['calendar.update_event','calendar.remove_event']:tool['shareable']=True
new={'name':'calendar.get_event','description':'Read one saved local Calendar event by exact id, including an explicit absence result. Unreadable storage is an error, never absence.',
     'input_schema':{'type':'object','properties':{'id':{'type':'string','minLength':1,'maxLength':64}},'required':['id'],'additionalProperties':False},
     'output_schema':{'type':'object','properties':{'found':{'type':'boolean'},'event':{'type':'object'}},'required':['found','event'],'additionalProperties':False},
     'risk':'read','implemented_by':'host-service','shareable':True,'private_data':True}
tools['tools'].insert(1,new)
newraw=json.dumps(tools,indent=2)+'\n';(PATCH/'tools.json').write_text(newraw)
# A proposal only. Registration/owner guard/confirmation are retained unchanged.
patch=''.join(difflib.unified_diff(source.splitlines(True),patched.splitlines(True),fromfile='a/apps/calendar/host-service/src/lib.rs',tofile='b/apps/calendar/host-service/src/lib.rs'))
patch+=''.join(difflib.unified_diff(raw.splitlines(True),newraw.splitlines(True),fromfile='a/'+tools_path,tofile='b/'+tools_path))
(ROOT/'research/native-agent/patches/calendar-shared-reconciliation.patch').write_text(patch)
man=(PATCH/'Cargo.toml').read_text().replace('name = "calendar-core-repro"', 'name = "calendar-core-proposed"', 1)
man=man[:man.index('[[test]]')]+'[lib]\nname="calendar_core_repro"\n'+'''[[test]]
name="calendar_patch"
path='''+repr(str(ROOT/'research/native-agent/night-repros/calendar_patch.rs'))+'\n';(PATCH/'Cargo.toml').write_text(man)
print('Proposed patch prepared; no upstream/production files changed')
