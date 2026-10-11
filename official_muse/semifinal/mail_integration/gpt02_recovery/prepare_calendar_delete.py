#!/usr/bin/env python3
"""Prepare deletion proposal under GPT-02; no shared main/SDK writes."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode=True
from test_recovery import function

OWN=Path(__file__).resolve().parent
BASE='e2f3ab878d7d7f77772507dc85e18cbef284cff86c2d4ee0a7e6639296107ea3'
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--sdk',type=Path,required=True)
    p.add_argument('--kernel',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();old=a.source.read_text();assert sha(old)==BASE,'source drift'
    tools=a.sdk/'apps/calendar/bundle/tools.json'
    contract=json.loads(tools.read_text());remove=next(t for t in contract['tools'] if t['name']=='calendar.remove_event')
    assert remove['input_schema']['required']==['id','expected'] and remove['confirm']=='host' and not remove['auto_approvable']
    new=old;changed=[]
    def edit(name,before,after):
        nonlocal new
        original=function(new,name);assert original.count(before)==1,(name,before)
        new=new.replace(original,original.replace(before,after,1),1);changed.append(name)
    edit('calendar_agent_tool_name','    return ""\n','    if name == "calendar.remove_event" || name == "calendar_remove_event" { return "calendar.remove_event" }\n    return ""\n')
    edit('calendar_agent_boot','fn calendar_agent_boot(){\n','fn calendar_agent_boot(){\n    calendar_agent_delete_boot()\n')
    edit('calendar_agent_project','    return true\n','    calendar_agent_delete_project(view,goal)\n    return true\n')
    edit('mail_calendar_verified','        && calendar_agent_binding_current(binding) && binding.receipt_status == "verified"',
         '        && calendar_agent_binding_current(binding) && binding.receipt_status == "verified"\n        && !calendar_agent_delete_blocks(binding)')
    fragment=(OWN/'calendar_delete_fragment.splash').read_text()
    anchor='fn calendar_agent_keep_previous(){'
    assert new.count(anchor)==1;new=new.replace(anchor,fragment+'\n'+anchor,1)
    anchor='                        Secondary{text: "回读当前请求的官方记录"'
    assert new.count(anchor)==1
    ui='''                        let delete_target = calendar_agent_delete_target()
                        if delete_target != nil {
                            Secondary{text: "选择删除当前已核验事件" on_click: || calendar_agent_delete_select()}
                        }
                        if calendar_agent_delete_selected != "" && delete_target != nil && delete_target.to_json() == calendar_agent_delete_selected {
                            Label{width: Fill text: "本人所选删除目标（稳定ID及全部事件字段）：\\n" + delete_target.expected.to_json() draw_text.color: ink draw_text.wrap: Words draw_text.text_style.font_size: 12}
                            Secondary{text: "确认删除所选事件" enabled: !calendar_agent_busy && calendar_agent_delete_writable on_click: || calendar_agent_delete_confirm()}
                        }
                        let delete_index = calendar_agent_delete_index(calendar_agent_state["binding"])
                        if delete_index >= 0 && calendar_agent_delete_current(calendar_agent_delete_state.records[delete_index]) {
                            Secondary{text: "核对原删除请求" enabled: !calendar_agent_busy on_click: || calendar_agent_delete_history(delete_index)}
                        }
'''
    new=new.replace(anchor,ui+anchor,1)
    before_names=re.findall(r'^fn (\w+)\(',old,re.M);after_names=re.findall(r'^fn (\w+)\(',new,re.M)
    untouched=[n for n in before_names if n not in changed]
    assert all(function(old,n)==function(new,n) for n in untouched)
    assert len(after_names)==len(set(after_names))
    patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/official_muse/app/source/main.splash',tofile='b/official_muse/app/source/main.splash',n=3))
    (OWN/'calendar-delete.patch').write_text(patch)
    files=[tools,a.sdk/'apps/calendar/host-service/src/lib.rs',a.sdk/'crates/app-peers/src/calendar_history.rs',a.sdk/'crates/shell/src/approvals/facts.rs',a.kernel/'crates/octos-agent/src/approval.rs',a.kernel/'crates/octos-agent/src/tools/peer_host_tool.rs']
    identity=dict(source_sha256=BASE,expected_source_sha256=sha(new),patch_sha256=sha(patch),fragment_sha256=sha(fragment),changed_functions=changed,unchanged_function_count=len(untouched),added_functions=[n for n in after_names if n not in before_names],contract_sources={str(f):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},formal_source_written=False,external_calls=0,boundary='Proposal only. Existing official get_event/remove_event relay with exact expected and args_digest. Requires Root legal fifth-tool ceiling/Broker receipt support; no direct Calendar owner call or Goal completion.')
    (OWN/'calendar-delete-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(new);print(json.dumps(identity))

if __name__=='__main__':main()
