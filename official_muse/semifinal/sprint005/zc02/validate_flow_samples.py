#!/usr/bin/env python3
"""Static actual-field contracts only; not SDK or GUI execution."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
    p=HERE/'flows';catalog=json.loads((p/'catalog.json').read_text());checks={}
    fields={'chat_reply':{'reply':1200},'chat_goal_plan':{'objective':40,'source':1000},'goal_summary':{'summary':45},
            'chat_calendar':{'title':200,'start':80,'end':80,'time_zone':80,'location':200},
            'chat_mail_candidate':{'to':200,'subject':200,'body':1200},'mail_reply_editor':{'subject':180,'body':1800}}
    for row in catalog['fixtures']:
        value=json.loads((p/row['file']).read_text());response=value['response'];kind=row['kind']
        if kind in fields:
            limits=fields[kind];valid=isinstance(response,dict) and set(response)==set(limits)
            valid=valid and all(type(response[k])==str and len(response[k])<=limit for k,limit in limits.items())
            if kind=='goal_summary':valid=valid and len(response['summary'].encode())<=180
            checks[row['file']+'_actual_schema_fields_limits']=valid
        elif kind=='mail_calendar_policy':
            limits={'title':160,'start':40,'end':40,'time_zone':80,'location':160,'question':300,'duration_quote':160}
            policy=response['policy'];keys={'search_start','search_end','time_zone','reason','hard_windows','preferred_windows'}
            valid=set(response)==set(limits)|{'policy','duration_changed'} and type(response['duration_changed'])==bool
            valid=valid and all(type(response[k])==str and len(response[k])<=limit for k,limit in limits.items()) and set(policy)==keys
            valid=valid and all(type(policy[k])==str for k in ('search_start','search_end','time_zone','reason')) and len(policy['reason'])<=800
            valid=valid and all(isinstance(policy[k],list) and len(policy[k])<=16 and all(set(w)=={'start','end'} and all(type(v)==str for v in w.values()) for w in policy[k]) for k in ('hard_windows','preferred_windows'))
            checks[row['file']+'_actual_schema_fields_limits']=valid
        else:checks[row['file']+'_negative_explicitly_classified']=kind in ('provider_negative','output_negative')
        checks[row['file']+'_bounded_control']=type(value['delay_ms'])==int and 0<=value['delay_ms']<=5000 and value['mode'] in ('normal','http_error','malformed')
    result={'kind':'STATIC_ZC05_MODEL_FLOW_SAMPLE_CONTRACT','main_sha256':catalog['main_sha256'],'fixtures':len(catalog['fixtures']),'checks':checks,'status':'PASS' if all(checks.values()) else 'FAIL','sdk_gui_status':'NOT_TESTED','kernel_cargo_calls':0}
    (HERE/'evidence/flow-sample-contract.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'fixtures':result['fixtures'],'checks':len(checks),'failed':[k for k,v in checks.items() if not v]}))
    return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
