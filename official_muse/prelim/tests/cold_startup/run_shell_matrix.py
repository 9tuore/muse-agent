#!/usr/bin/env python3
"""Ten process cold launches and five ordinary app reopens of one real Shell.

Only synthetic local-model-only profiles are accepted. No model submission,
Mail send, Calendar write, production state replacement or system restart.
"""
import argparse, hashlib, json, subprocess, sys, time, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT/'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT/'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import navigate

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--port',type=int,required=True);a=p.parse_args()
    assert 8480<=a.port<=8499
    c=a.candidate.resolve();m=json.loads((c/'candidate.json').read_text());assert m['profile_kind']=='LOCAL_MODEL_ONLY_SYNTHETIC'
    private=Path(m.get('runtime_private_path',str(c/'private')));jail=private/'apps/muse-goals'
    profile=json.loads((private/'home/octos-home/.octos/profiles/_main.json').read_text())
    assert profile['config']['llm']['primary']['route']['base_url']=='http://127.0.0.1:65534/v1'
    assert not profile['config']['llm']['fallbacks']
    assert sha(jail/'bundle/main.splash')==m['source_sha256'];assert sha(Path(m['host_app_path'])/'Contents/MacOS/octosense')==m['host_sha256']
    a.out.mkdir(parents=True,exist_ok=False);remote=Remote(a.port)
    protected=['chat-sessions.json','chat-sessions.backup.json','calendar-state.json','calendar-state.backup.json','goals.json','goals.backup.json','memory.json','memory.backup.json','mail-draft.json','mail-draft.backup.json','mail-draft-archive.json']
    before={n:sha(jail/n) for n in protected}
    ledger=private/'apps/.host/model/ledger.json';ledger_before=sha(ledger)
    seeded_counts={}
    for filename,keys in [('chat-sessions.json',['sessions']),('goals.json',['goals','runs','actions']),('memory.json',['claims','sources','forget']),('calendar-state.json',['links','receipts','local_states'])]:
        if (jail/filename).is_file():
            data=json.loads((jail/filename).read_text());seeded_counts[filename]={key:len(data.get(key,[])) for key in keys}
    chat_seed=json.loads((jail/'chat-sessions.json').read_text())
    selected=next(s for s in chat_seed['sessions'] if s['id']==chat_seed['selected_id'])
    assert selected.get('focus_project') and selected.get('focus_owner')
    expected_focus='当前项目 · '+selected['focus_project']+'  /  '+selected['focus_owner']
    report={'kind':'SHELL_LIVE_SYNTHETIC_FULL_PROCESS_COLD_AND_APP_REOPEN','version':m['version'],'code_commit':m['commit'],'source_sha256':m['source_sha256'],'host_sha256':m['host_sha256'],'wall_budget_ms':64,'seeded_record_counts':seeded_counts,'protected_files_sha256':before,'cold':[],'reopen':[],'computer_restart':'NOT_TESTED_REQUIRES_USER','scope':'Synthetic app state; no paid model/backend semantics or real external chain acceptance.'}
    def save(): (a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def inspect(run,started,log_since=0):
        remote.wait_for(expected_focus,20)
        remote.wait_for('goal_input',20)
        run['selected_focus_restored']=True
        # An editable native input and meaningful labels are required; an empty
        # frame/placeholder alone is never counted as a successful launch.
        words=[w.get('t','') for w in remote.widgets() if w.get('ty')=='Label']
        assert any('当前项目' in t or t=='对话' for t in words), 'Meaningful Muse content missing'
        remote.set_text('goal_input','冷启动合成输入检查');assert remote.find('goal_input')['val']=='冷启动合成输入检查';remote.set_text('goal_input','')
        pages={}
        for page in ['记忆','邮箱','能力授权','设置','对话']:
            navigate(remote,page);pages[page]=True
        run['pages']=pages;run['input_editable']=True
        logs=json.loads(remote.request('/log',since=log_since))['l']
        errors=[x for x in logs if 'budget exceeded' in x or 'source preparation failed' in x or 'no root view' in x]
        run['startup_log']=[x for x in logs if 'SPLASH_COMPILE' in x or 'splash:' in x]
        assert not errors,errors
        run['protected_state_equal']=all(sha(jail/n)==digest for n,digest in before.items())
        run['model_ledger_equal']=sha(ledger)==ledger_before
        assert run['protected_state_equal'] and run['model_ledger_equal']
        run['seconds']=time.monotonic()-started;run['pid']=json.loads(remote.request('/s'))['pid'];run['pass']=True
    for i in range(10):
        run={'index':i+1,'pass':False};report['cold'].append(run);d=a.out/f'cold-{i+1:02d}';d.mkdir();t=time.monotonic()
        try:
            command=[sys.executable,str(ROOT/'official_muse/ui_memory/launch_candidate.py'),'--candidate',str(c),'--port',str(a.port)]
            if i:command.append('--restart')
            proc=subprocess.run(command,text=True,capture_output=True,timeout=40);(d/'launch.txt').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
            remote.click('打开');inspect(run,t)
        except Exception as e:run['error']=str(e);run['seconds']=time.monotonic()-t;(d/'exception.txt').write_text(traceback.format_exc())
        try:(d/'snap.json').write_bytes(remote.request('/snap'));(d/'log.json').write_bytes(remote.request('/log',n=300));remote.shot(d/'visible.png')
        except Exception as e:run['capture_error']=str(e)
        save();print(json.dumps({'kind':'cold',**run},ensure_ascii=False),flush=True)
    for i in range(5):
        run={'index':i+1,'pass':False};report['reopen'].append(run);d=a.out/f'reopen-{i+1:02d}';d.mkdir();t=time.monotonic()
        try:
            pid=json.loads(remote.request('/s'))['pid'];offset=remote.log(300)['n'];remote.request('/k',k='down',c='KeyW',cmd=1);remote.request('/k',k='up',c='KeyW',cmd=1);time.sleep(.3)
            assert not any(w.get('i')=='goal_input' for w in remote.widgets()),'Muse did not close'
            remote.click('打开');inspect(run,t,offset);assert run['pid']==pid,'Ordinary reopen unexpectedly restarted Shell'
        except Exception as e:run['error']=str(e);run['seconds']=time.monotonic()-t;(d/'exception.txt').write_text(traceback.format_exc())
        try:(d/'snap.json').write_bytes(remote.request('/snap'));(d/'log.json').write_bytes(remote.request('/log',n=300));remote.shot(d/'visible.png')
        except Exception as e:run['capture_error']=str(e)
        save();print(json.dumps({'kind':'reopen',**run},ensure_ascii=False),flush=True)
    report['cold_pass']=sum(r['pass'] for r in report['cold']);report['reopen_pass']=sum(r['pass'] for r in report['reopen']);save()
    if report['cold_pass']!=10 or report['reopen_pass']!=5:raise SystemExit(1)
if __name__=='__main__':main()
