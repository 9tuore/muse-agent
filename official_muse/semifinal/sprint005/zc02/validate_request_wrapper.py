#!/usr/bin/env python3
"""Local checks against the pinned SDK guidance/origin contract; no service calls."""
import json
from pathlib import Path
from planner import decision,READ_QUERY_PREFIX,READ_QUERY_SUFFIX
HERE=Path(__file__).resolve().parent

def main():
    query=READ_QUERY_PREFIX+'{"limit":200}'+READ_QUERY_SUFFIX
    guidance={'kind':'octosense_host_guidance','boundary':'S005 synthetic boundary',
        'instructions':'Example: 精确 calendar.events 参数：{"limit":200}','skills':[]}
    request={'kind':'octosense_request','text':query}
    def wrapped(req=request,guide=guidance):
        return '[from the person: Muse] '+json.dumps(guide,ensure_ascii=False)+'\n'+json.dumps(req,ensure_ascii=False)
    def body(content,tools=True,results=()):
        return {'messages':[{'role':'user','content':content},*[{'role':'tool','content':json.dumps(r)} for r in results]],
            'tools':[{'function':{'name':'calendar_events'}}] if tools else []}
    def refused(value):
        try:decision(value);return False
        except (ValueError,TypeError):return True
    wanted={'tool':'calendar_events','args':{'limit':200},'index':0}
    checks={
        'SDK_joined_guidance_request_with_person_origin':decision(body(wrapped()))==wanted,
        'OpenAI_text_parts_same_wrapper':decision(body([{'type':'text','text':json.dumps(guidance,ensure_ascii=False)},{'type':'text','text':json.dumps(request,ensure_ascii=False)}]))==wanted,
        'native_exact_query_still_matches':decision(body(wrapped({'kind':'octosense_request','text':'精确 calendar.events 参数：{"limit":200}'})))==wanted,
        'duplicate_request_and_guidance_only_refused':refused(body(json.dumps(request)+'\n'+json.dumps(request))) and refused(body(json.dumps(guidance))),
        'unknown_kind_and_spoofed_app_scope_fields_refused':refused(body(wrapped({'kind':'other','text':query}))) and refused(body(wrapped({**request,'app':'invented','scope':'invented'}))),
        'nested_wrapper_refused':refused(body(wrapped({'kind':'octosense_request','text':json.dumps(request)}))),
        'invalid_inner_JSON_not_repaired':refused(body(wrapped({'kind':'octosense_request','text':query.replace('{"limit":200}','{limit:200}')}))),
        'actual_tool_offer_required':refused(body(wrapped(),tools=False)),
        'actual_tool_error_stops':refused(body(wrapped(),results=({'ok':False,'error':'S005 synthetic failure'},))),
        'actual_read_result_ends_without_mutation':'tool' not in decision(body(wrapped(),results=({'ok':True,'data':[]},))),
    }
    result={'kind':'PINNED_SDK_REQUEST_WRAPPER_LOCAL_CONTRACT','status':'PASS' if all(checks.values()) else 'FAIL',
        'checks':checks,'schema':{'request':{'kind':'octosense_request','text':'string <=32768 UTF8 bytes; decoded once'},
            'guidance':'optional first octosense_host_guidance object; never scanned for tool markers',
            'app_scope':'not present in serialized wrapper; broker binds app/account; payload extras refused'},
        'wire_shape_basis':'SDK guidance.rs/Kernel prompt_text and origin source; inference, not captured wire',
        'network_requests_sent':0,'root_service_deployed':False,'owner_receipts':'NOT_PROVEN'}
    (HERE/'evidence/request-wrapper-contract.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failed':[k for k,v in checks.items() if not v]}))
    return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
