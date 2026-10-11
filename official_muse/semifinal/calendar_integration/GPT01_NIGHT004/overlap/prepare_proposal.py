#!/usr/bin/env python3
"""Build an unapplied Main patch from the exact c892 source; no shared writes."""
import argparse,difflib,hashlib,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
OWN=HERE.parents[4]
BASE_SHA='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'
sha=lambda b:hashlib.sha256(b).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    raw=a.source.read_text(); assert sha(raw.encode())==BASE_SHA,'Fixed source changed'
    out=a.out.resolve(); out.relative_to(OWN/'build'); out.mkdir(parents=True,exist_ok=False)
    library=(HERE/'native_preflight_proposal.splash').read_text().split('\n',1)[1]
    s=raw
    def replace(old,new):
        nonlocal s
        assert s.count(old)==1,old[:90]
        s=s.replace(old,new)
    replace('fn calendar_agent_submit_candidate(){',library+'\nfn calendar_agent_submit_candidate(){')
    old='    calendar_agent_submit_bound("仅创建下列精确候选，不改期、不发送邮件。",calendar_agent_candidate)'
    hook='''    if calendar_agent_busy || !calendar_agent_writable { return }
    if calendar_agent_state.status != "idle" && calendar_agent_state.status != "blocked" {
        calendar_agent_notice = "请先回读并结清当前查询，再单独确认候选。" redraw() return
    }
    if !calendar_agent_preflight_current() {
        calendar_agent_preflight = {status:"query" candidate_json:calendar_agent_candidate.to_json()
            request_id:"" turn_id:"" session_id:"" tool_call_id:"" events:[] conflicts:[] reason:""}
        calendar_agent_submit("仅查询官方日历事件列表以核对当前候选的重叠；不新增、改期、删除、通知或发送邮件。精确 calendar.events 参数：{\\"limit\\":200}")
        return
    }
    if calendar_agent_preflight.status != "ready" {
        calendar_agent_notice = calendar_agent_preflight_notice() redraw() return
    }
    // This distinct gesture explicitly accepts the displayed snapshot/overlap.
    // Consume the check before the existing native create path; never auto-retry.
    calendar_agent_preflight.status = "consumed"
'''
    replace(old,hook+old)
    old='    if binding != nil {\n        calendar_agent_state.binding = binding.to_json().parse_json()'
    replace(old,'    if binding == nil && calendar_agent_preflight.status == "query" { calendar_agent_preflight.request_id = id }\n'+old)
    old='        if settle { calendar_agent_settle_if_resolved(completed,failed,unverified,query_only) }'
    replace(old,'        calendar_agent_preflight_history(r.data)\n'+old+'\n        if calendar_agent_preflight_current() { calendar_agent_notice = calendar_agent_preflight_notice() }')
    replace('Secondary{text: "核对后提交当前事项候选"','Secondary{text: calendar_agent_candidate_submit_label()')
    label='official_muse/app/source/main.splash'
    patch=''.join(difflib.unified_diff(raw.splitlines(True),s.splitlines(True),fromfile='a/'+label,tofile='b/'+label))
    (out/'proposed-main.splash').write_text(s)
    (HERE/'native_preflight_main.patch').write_text(patch)
    record={'status':'UNAPPLIED_PROPOSAL','base_source_sha256':BASE_SHA,'proposed_source_sha256':sha(s.encode()),
        'patch_sha256':sha(patch.encode()),'patch_lines':len(patch.splitlines()),'proposal_source':str(out/'proposed-main.splash'),
        'shared_source_edited':False,'sdk_edited':False,'package_created':False}
    (out/'identity.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))

if __name__=='__main__':main()
