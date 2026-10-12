#!/usr/bin/env python3
"""One new late-response transport check; no protocol suite or SDK/GUI calls."""
import concurrent.futures,json,threading,time,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
from fixture_scope import PROFILE_MARKER,OWNER_MARKER
from serve import State,HTTP
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[3]
def main():
    root=REPO/'build/gpt02-sprint005-response-binding-r1';root.mkdir(exist_ok=False)
    (root/'apps/.host').mkdir(parents=True);(root/'FIXTURE_ONLY').write_bytes(PROFILE_MARKER);(root/'apps/.host/FIXTURE_ONLY').write_bytes(OWNER_MARKER)
    state=State(root);server=ThreadingHTTPServer(('127.0.0.1',0),HTTP);server.state=state;state.ready={'scope':'late-response unit only'}
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.server_address[1])
    def api(path,value=None):
        req=urllib.request.Request(base+path,data=json.dumps(value).encode() if value is not None else None,headers={'content-type':'application/json'})
        with urllib.request.urlopen(req,timeout=5) as r:return json.load(r)
    checks={}
    try:
        api('/__fixture/model',{'case_id':'old','response':{'reply':'old bound reply'},'delay_ms':350})
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            pending=pool.submit(api,'/v1/chat/completions',{'messages':[{'role':'user','content':'old request'}]})
            deadline=time.monotonic()+3;status={}
            while time.monotonic()<deadline:
                status=api('/__fixture/status')
                if status.get('counts',{}).get('model.response_bound',0)>=1:break
                time.sleep(0.01)
            checks['actual_old_response_binding_visible']=status.get('model_bindings',[{}])[-1].get('case_id')=='old'
            api('/__fixture/model',{'case_id':'new','response':{'reply':'new reply'},'delay_ms':0})
            fresh=api('/v1/chat/completions',{'messages':[{'role':'user','content':'new request'}]})
            old=pending.result(timeout=5)
        checks['late_old_request_keeps_original_response']=json.loads(old['choices'][0]['message']['content'])=={'reply':'old bound reply'}
        checks['new_request_uses_new_response']=json.loads(fresh['choices'][0]['message']['content'])=={'reply':'new reply'}
        bindings=api('/__fixture/status')['model_bindings'];checks['actual_two_case_hashes_different']=len(bindings)==2 and bindings[0]['response_sha256']!=bindings[1]['response_sha256']
    finally:
        server.shutdown();server.server_close();state.receiver.stdin.close();state.receiver.wait(timeout=5);state.receiver_err.close()
    result={'kind':'NEW_LATE_MODEL_FIXTURE_BINDING_HTTP_ONLY','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'sdk_gui_status':'NOT_TESTED','kernel_cargo_calls':0}
    (HERE/'evidence/late-response-binding.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks)}));return 0 if result['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
