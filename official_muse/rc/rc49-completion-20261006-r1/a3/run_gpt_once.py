#!/usr/bin/env python3
"""One real Muse send in an isolated Shell; HTTP observation with documented protocol limitations.
No original profile/Root port changes. Headers, URLs, keys and raw API body stay
in memory; private logs are excluded. Response bytes are forwarded unchanged.
"""
from pathlib import Path
import datetime
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
ORIGIN = ROOT/'official_muse/app/build/ui-memory-20261003/morning-final-live-r2/private'
GATE = ROOT/'official_muse/rc/submission-ready-20261006-r1/gate-rc49-r2'
REMOTE_PORT, RELAY_PORT = 8515, 8516
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
sys.path.insert(0, str(ROOT/'official_muse/phase2/tests'))
from remote import Remote


def safe_model(value):
    return value if isinstance(value, str) and re.fullmatch(r'(gpt|MiniMax|claude)[A-Za-z0-9._-]{0,96}', value) else '<not exposed or withheld>'


def main():
    for port in (REMOTE_PORT, RELAY_PORT):
        with socket.socket() as s:
            assert s.connect_ex(('127.0.0.1', port)) != 0, 'Owned port unavailable'
    stage = OUT/'.local-state/gpt-once-r3'
    assert not stage.exists(), 'Never overwrite old evidence or rerun an ambiguous send'
    stage.mkdir(parents=True, mode=0o700)
    private = stage/'private';private.mkdir(mode=0o700)
    profile = ORIGIN/'home/octos-home/.octos/profiles/_main.json'
    profile_before = sha(profile)
    data = json.loads(profile.read_text())
    llm = data['config']['llm']
    selections = [llm['primary'], *llm.get('fallbacks', [])]
    selected = [s for s in selections if s.get('family_id') == 'openai' and s.get('model_id') == 'gpt-4o']
    assert len(selected) == 1
    chosen = selected[0]
    route = chosen['route']; upstream = route['base_url'].rstrip('/')
    assert upstream.startswith('https://')
    assert route.get('api_type') == 'openai'
    # Preserve the existing credential configuration locally without resolving
    # or printing a key. Select one provider, never MiniMax fallback.
    llm['primary'] = chosen;llm['fallbacks'] = []
    route['base_url'] = f'http://127.0.0.1:{RELAY_PORT}/probe'
    dest = private/'home/octos-home/.octos/profiles/_main.json'
    dest.parent.mkdir(parents=True);dest.write_text(json.dumps(data));dest.chmod(0o600)
    jail = private/'apps/muse-goals';jail.mkdir(parents=True)
    shutil.copytree(GATE/'bundle', jail/'bundle')
    shutil.copyfile(GATE/'mirror/catalog.json', private/'apps/catalog.json')
    budget = ORIGIN/'apps/.host/model'
    shutil.copytree(budget, private/'apps/.host/model')
    (jail/'mail-watch.json').write_text(json.dumps({'schema':1,'enabled':False,'accounts':[],'alerts':[]}))
    record = {'started_beijing':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              'kind':'ACTUAL_OFFICIAL_MODEL_COMPLETE_SINGLE_PROVIDER_ONCE',
              'requested_family':'openai','requested_model':'gpt-4o','configured_candidates':1,'fallbacks':0,
              'product_commit':'e0eb5d82','payload_sha256':sha(jail/'bundle/main.splash'),
              'transparent_observer':False,'observer_modified_prompt_or_response':False,
              'mail_or_calendar_calls_authorized':False,'api_requests':[], 'ui_send_attempts':0,
              'original_profile_unchanged':False,'status':'IN_PROGRESS'}
    lock = threading.Lock()
    # This observer preserves body bytes, not response-header/redirect equivalence.
    # Existing completed attempt is diagnostic only; do not rerun to infer upstream identity.
    class Relay(BaseHTTPRequestHandler):
        def log_message(self, *unused): pass
        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length','0')))
            entry = {'requested_model':safe_model(json.loads(body).get('model'))}
            headers = {k:v for k,v in self.headers.items() if k.lower() not in ('host','content-length','connection')}
            request = Request(upstream+self.path.removeprefix('/probe'),data=body,headers=headers)
            try:
                response = urlopen(request, timeout=120)
                status, answer = response.status, response.read()
            except HTTPError as e:
                status, answer = e.code, e.read()
            except Exception:
                status, answer = 502, b'{"error":{"message":"Transparent upstream transport failed"}}'
                entry['failure_category'] = 'UPSTREAM_TRANSPORT'
            entry['http_status'] = status
            try:
                parsed = json.loads(answer)
                entry['response_model'] = safe_model(parsed.get('model'))
                u = parsed.get('usage') or {}
                entry['usage'] = {k:v for k,v in u.items() if k in ('prompt_tokens','completion_tokens','total_tokens') and isinstance(v,int)}
                if status >= 400:
                    err = parsed.get('error') or {}
                    code = err.get('code') or err.get('type')
                    entry['failure_category'] = code if code in ('invalid_api_key','authentication_error','rate_limit_exceeded','insufficient_quota','model_not_found','invalid_request_error') else 'PROVIDER_HTTP_FAILURE'
            except (ValueError,AttributeError):
                entry['response_model'] = '<not exposed or withheld>'
            with lock:record['api_requests'].append(entry)
            self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(answer)));self.end_headers();self.wfile.write(answer)
    server = ThreadingHTTPServer(('127.0.0.1',RELAY_PORT), Relay)
    thread = threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    meta = json.loads((GATE/'candidate.json').read_text())
    app = Path(meta['host_app_path']);host = app/'Contents/MacOS/octosense'
    assert sha(host) == meta['host_sha256'];record['host_sha256']=sha(host)
    env = dict(os.environ, OCTOSENSE_HOME=str(private/'home'), OCTOSENSE_APP_DATA=str(private/'apps'),
               OCTOS_APP_CORE_DIR=str(private/'home/octos-home/.octos'),OCTOSENSE_HUB=str(GATE/'mirror'),
               OCTOSENSE_HUB_ANCHOR='3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840',
               MAKEPAD_REMOTE=str(REMOTE_PORT),MAKEPAD_APP_CONFIG='{}')
    env.pop('MAKEPAD_HIDE_WINDOWS',None)
    log=(stage/'runtime.private.log').open('w')
    proc = subprocess.Popen([str(host),'--test-action','launch-apphub'],cwd=host.parent,env=env,stdout=log,stderr=subprocess.STDOUT)
    record['pid']=proc.pid
    remote = Remote(REMOTE_PORT)
    try:
        apphub_deadline=time.monotonic()+40
        while True:
            try:
                remote.find('打开')
                break
            except (OSError,AssertionError):
                if time.monotonic()>=apphub_deadline:
                    raise TimeoutError('AppHub not ready')
                time.sleep(.3)
        time.sleep(5)
        remote.click('打开')
        ready_deadline = time.monotonic()+60
        while True:
            try:
                remote.find('goal_input')
                break
            except (OSError, AssertionError):
                if time.monotonic() >= ready_deadline:
                    raise TimeoutError('Isolated Shell UI was not ready; no model send')
                time.sleep(.3)
        prompt='本次只作合成问答测试：2加3是多少？请只回答数字，不创建任务，不操作邮箱或日历。'
        remote.set_text('goal_input',prompt)
        widget=remote.find('发送');x,y,w,h=widget['r'];assert w>2 and h>2
        record['ui_send_attempts']=1
        # One raw click only: no repeat after an ambiguous remote timeout.
        try: remote.request('/click',x=int(x+w/2),y=int(y+h/2),wait=1)
        except Exception: record['ui_click_return']='AMBIGUOUS_INSPECT_DISK_NO_RESEND'
        deadline=time.monotonic()+150
        terminal=None
        while time.monotonic()<deadline:
            path=jail/'chat-sessions.json'
            if path.exists():
                sessions=json.loads(path.read_text()).get('sessions',[])
                messages=[m for s in sessions for m in s.get('messages',[]) if m.get('role')=='assistant' and m.get('state') in ('success','error')]
                if messages:terminal=messages[-1];break
            time.sleep(.3)
        trace=jail/'model-last-response.json'
        if trace.exists():
            response=json.loads(trace.read_text());record['host_trace']={k:response.get(k) for k in ('is_ok','known_usage','meta','error_code')}
        record['terminal_state']=terminal.get('state') if terminal else 'TIMEOUT'
        record['answer_is_expected_5']=bool(terminal and terminal.get('state')=='success' and terminal.get('text','').strip()=='5')
        record['status']='LIVE_COMPLETED' if terminal else 'NO_TERMINAL_NO_RESEND'
        if terminal:record['answer_sha256']=hashlib.sha256(terminal.get('text','').encode()).hexdigest()
        remote.shot(stage/'window.private.png')
    except Exception as e:
        record['status']='FAILED';record['failure_category']=type(e).__name__
    finally:
        try:remote.request('/quit')
        except Exception:proc.terminate()
        try:proc.wait(timeout=10)
        except subprocess.TimeoutExpired:proc.kill();proc.wait()
        log.close();server.shutdown();server.server_close()
        record['original_profile_unchanged']=sha(profile)==profile_before
        record['finished_beijing']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
        record['runtime_errors_present']=any(t in (stage/'runtime.private.log').read_text(errors='replace') for t in ('[E]', 'script time budget exceeded', 'SPLASH_COMPILE_FAILED'))
        (OUT/'GPT_ONCE_RESULT_R3.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
