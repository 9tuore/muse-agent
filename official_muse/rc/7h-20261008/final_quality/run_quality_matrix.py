#!/usr/bin/env python3
"""Measured process cold launches, app reopens and Shell restarts of one candidate.

Only synthetic local-model-only profiles are accepted. No model submission,
Mail send, Calendar write, production state replacement or system restart.
"""
import argparse, hashlib, json, subprocess, sys, time, traceback
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]
QUALITY = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT/'official_muse/ui_memory/tests'))
from remote import Remote

def navigate(remote,page):
    """Scroll real sidebar in small steps; avoid overshooting short clipped rows."""
    area=remote.find('shortcuts')['r'];x,y,w,h=area
    remote.scroll(int(x+w/2),int(y+h/2),-1000);time.sleep(.25)
    for scan in range(2):
        for _ in range(12):
            widgets=remote.widgets()
            target=next((v for v in widgets if v.get('ty')=='Button' and v.get('t')==page),None)
            if target and target['r'][2]>=2 and target['r'][3]>=24:
                return remote.click(page)
            dy=-40 if target and target['r'][1]<=y+1 else 40
            remote.scroll(int(x+w/2),int(y+h/2),dy);time.sleep(.2)
        # Scan the entire existing list before toggling More: it may already
        # be expanded and the requested page merely below the current viewport.
        if scan==0 and page in ['操作记录','能力授权','设置']:
            remote.click('更多')
            time.sleep(.3)
            remote.scroll(int(x+w/2),int(y+h/2),-1000);time.sleep(.25)
        else:break
    if page in ['操作记录','能力授权','设置']:
        widgets=remote.widgets()
        if not any(v.get('ty')=='Button' and v.get('t') in ['操作记录','能力授权','设置'] for v in widgets):
            remote.click('更多');time.sleep(.3)
            for _ in range(12):
                widgets=remote.widgets();target=next((v for v in widgets if v.get('ty')=='Button' and v.get('t')==page),None)
                if target and target['r'][2]>=2 and target['r'][3]>=24:return remote.click(page)
                remote.scroll(int(x+w/2),int(y+h/2),-40 if target and target['r'][1]<=y+1 else 40);time.sleep(.2)
    raise AssertionError('Visible sidebar entry unreachable after bounded two-direction scroll: '+page)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None

def array_counts(data, keys):
    # A corrupted string is not a count of task records.
    return {key: len(data.get(key, [])) if isinstance(data.get(key, []), list) else None for key in keys}

def main():
    p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--port',type=int,required=True)
    p.add_argument('--cold-count',type=int,default=10);p.add_argument('--reopen-count',type=int,default=5);p.add_argument('--restart-count',type=int,default=0);p.add_argument('--fail-fast',action='store_true')
    p.add_argument('--compact-evidence',action='store_true',help='Keep first/failure raw snapshots and PNGs; deduplicate exact source text in other success snapshots')
    a=p.parse_args()
    assert 0<=a.cold_count<=30 and 0<=a.reopen_count<=100 and 0<=a.restart_count<=20
    assert a.cold_count+a.reopen_count+a.restart_count>0
    assert a.port==8494, 'Quality owns only port 8494'
    c=a.candidate.resolve();m=json.loads((c/'candidate.json').read_text());assert m['profile_kind']=='LOCAL_MODEL_ONLY_SYNTHETIC'
    private=Path(m.get('runtime_private_path',str(c/'private')));jail=private/'apps/muse-goals'
    profile=json.loads((private/'home/octos-home/.octos/profiles/_main.json').read_text())
    assert profile['config']['llm']['primary']['route']['base_url']=='http://127.0.0.1:65534/v1'
    assert not profile['config']['llm']['fallbacks']
    assert sha(jail/'bundle/main.splash')==m['source_sha256'];assert sha(Path(m['host_app_path'])/'Contents/MacOS/octosense')==m['host_sha256']
    assert a.out.resolve().is_relative_to(QUALITY);a.out.mkdir(parents=True,exist_ok=False);remote=Remote(a.port)
    protected=['chat-sessions.json','chat-sessions.backup.json','calendar-state.json','calendar-state.backup.json','activity.json','activity.backup.json','goals.json','goals.backup.json','memory.json','memory.backup.json','mail-draft.json','mail-draft.backup.json','mail-draft-archive.json','mail-watch.json','global-memory-settings.json']
    for file in (jail/'results').rglob('*') if (jail/'results').exists() else []:
        if file.is_file(): protected.append(file.relative_to(jail).as_posix())
    before={n:sha(jail/n) for n in protected}
    ledger=private/'apps/.host/model/ledger.json';ledger_before=sha(ledger)
    activity_before=json.loads((jail/'activity.json').read_text())
    seeded_counts={}
    for filename,keys in [('chat-sessions.json',['sessions']),('goals.json',['goals','runs','actions']),('memory.json',['claims','sources','forget']),('calendar-state.json',['links','receipts','local_states']),('mail-watch.json',['accounts','alerts'])]:
        if (jail/filename).is_file():
            data=json.loads((jail/filename).read_text());seeded_counts[filename]=array_counts(data,keys)
    seeded_counts['chat_message_count']=sum(len(item['messages']) for item in json.loads((jail/'chat-sessions.json').read_text())['sessions'])
    watch=json.loads((jail/'mail-watch.json').read_text())
    seeded_counts['mail_baseline']=[{'id':item['id'],'ready':item['ready'],'seen':len(item['seen'])} for item in watch['accounts']]
    assert seeded_counts['chat_message_count'] > 0 and seeded_counts['memory.json']['claims'] > 0
    assert seeded_counts['mail_baseline'] and all(item['ready'] and item['seen'] > 0 for item in seeded_counts['mail_baseline'])
    chat_seed=json.loads((jail/'chat-sessions.json').read_text())
    selected=next(s for s in chat_seed['sessions'] if s['id']==chat_seed['selected_id'])
    assert selected.get('focus_project') and selected.get('focus_owner')
    expected_focus='当前项目 · '+selected['focus_project']+'  /  '+selected['focus_owner']
    report={'kind':'SHELL_LIVE_SYNTHETIC_FULL_PROCESS_COLD_AND_APP_REOPEN','version':m['version'],'code_commit':m['commit'],'source_sha256':m['source_sha256'],'host_sha256':m['host_sha256'],'budget_evidence':'Pinned Host binary unchanged; no claimed numeric callback budget from legacy runner','seeded_record_counts':seeded_counts,'protected_files_sha256':before,'cold':[],'reopen':[],'restart':[],'requested_counts':{'cold':a.cold_count,'reopen':a.reopen_count,'restart':a.restart_count},'computer_restart':'NOT_TESTED_REQUIRES_USER','scope':'Synthetic app state; no paid model/backend semantics or real external chain acceptance. Cold means a new Shell process, not clearing OS filesystem caches. Restart means additional explicit Shell process replacements after app-reopen tests.'}
    def save():
        # Keep the last complete observation if a new write runs out of space.
        temporary=a.out/'report.json.pending'
        temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        temporary.replace(a.out/'report.json')
    def capture(run,d):
        raw=remote.request('/snap')
        if a.compact_evidence and run['pass'] and run['index']>1:
            snapshot=json.loads(raw); source=(jail/'bundle/main.splash').read_bytes()
            def deduplicate(value):
                if isinstance(value,dict):
                    text=value.get('t')
                    if isinstance(text,str) and text.encode()==source:
                        del value['t'];value['t_source_reference']={'path':'../shared-source.splash','sha256':m['source_sha256']}
                    for item in value.values():deduplicate(item)
                elif isinstance(value,list):
                    for item in value:deduplicate(item)
            deduplicate(snapshot)
            run['raw_snapshot_sha256']=hashlib.sha256(raw).hexdigest()
            raw=json.dumps(snapshot,ensure_ascii=False).encode()
        (d/'snap.json').write_bytes(raw);(d/'log.json').write_bytes(remote.request('/log',n=300))
        remote.shot(d/'visible.png')
    if a.compact_evidence:
        (a.out/'shared-source.splash').write_bytes((jail/'bundle/main.splash').read_bytes())
        report['evidence_storage']={'snapshots':'First per mode and failures raw; other success snapshots retain all fields except exact source text referenced by SHA','pngs':'First per mode and every failure','checks':'All original page, edit, state, ledger and runtime checks unchanged'}
    def inspect(run,started,log_since=0):
        remote.wait_for(expected_focus,20)
        remote.wait_for('goal_input',20)
        run['first_content_seconds']=time.monotonic()-started
        run['selected_focus_restored']=True
        # An editable native input and meaningful labels are required; an empty
        # frame/placeholder alone is never counted as a successful launch.
        words=[w.get('t','') for w in remote.widgets() if w.get('ty')=='Label']
        assert any('当前项目' in t or t=='对话' for t in words), 'Meaningful Muse content missing'
        history_label=remote.wait_for(selected['messages'][-1]['text'],20)
        assert history_label.get('ty')=='Label' and history_label.get('t')==selected['messages'][-1]['text'], 'Latest stored chat history did not render'
        run['nonempty_chat_history_rendered']=True
        remote.set_text('goal_input','冷启动合成输入检查');assert remote.find('goal_input')['val']=='冷启动合成输入检查';remote.set_text('goal_input','')
        run['first_interactive_seconds']=time.monotonic()-started
        if m.get('expected_goal_title'):
            remote.wait_for(m['expected_goal_title'],15)
            remote.wait_for('将处理 2 条资料，保存并重新读取结果。',15)
            run['nonempty_goal_card_rendered']=True
        observed_counts={}
        for filename,keys in [('chat-sessions.json',['sessions']),('goals.json',['goals','runs','actions']),('memory.json',['claims','sources','forget']),('calendar-state.json',['links','receipts','local_states'])]:
            value=json.loads((jail/filename).read_text());observed_counts[filename]=array_counts(value,keys)
        value=json.loads((jail/'mail-watch.json').read_text())
        observed_counts['mail_baseline']=[{'id':item['id'],'ready':item['ready'],'seen':len(item['seen'])} for item in value['accounts']]
        observed_counts['chat_message_count']=sum(len(item['messages']) for item in json.loads((jail/'chat-sessions.json').read_text())['sessions'])
        run['record_counts']=observed_counts
        pages={}
        for page in ['记忆','邮箱','日历','操作记录','能力授权','设置','对话']:
            navigate(remote,page)
            if page=='记忆':
                remote.wait_for('汇报先给结论，再列三项重点',15)
                run['nonempty_memory_rendered']=True
                remote.shot(d/'memory-visible.png')
            if page=='对话':
                remote.wait_for('goal_input',15)
                remote.wait_for(selected['messages'][-1]['text'],20)
                title={'t':'对话'}
            else:
                title=remote.wait_for('page_title',15)
                expected_title='能力与授权' if page=='能力授权' else page
                deadline=time.monotonic()+15
                while title['t']!=expected_title and time.monotonic()<deadline:
                    time.sleep(.1);title=remote.find('page_title')
                assert title['t']==expected_title, 'Navigation did not change actual page title: '+page
            content=remote.wait_for('central_main',15)
            assert content['r'][2]>=2 and content['r'][3]>=2, 'Core page content clipped: '+page
            # Title updates before the dynamic Splash body finishes rendering.
            # Require the same body evidence, with visible geometry, within the
            # existing page readiness deadline instead of sampling one frame.
            body_deadline=time.monotonic()+15
            words_on_page=[]
            while time.monotonic()<body_deadline:
                words_on_page=[w.get('t','') for w in remote.widgets() if w.get('ty')=='Label' and w['r'][0]>=content['r'][0] and w['r'][0]<content['r'][0]+content['r'][2] and w['r'][1]>=262 and w['r'][2]>=2 and w['r'][3]>=2]
                if words_on_page:break
                time.sleep(.1)
            assert words_on_page, 'Core page has no visible body labels: '+page
            pages[page]={'visible':True,'actual_page_title':title['t'],'content_rect':content['r'],'body_labels':words_on_page}
            if run['index']==1: remote.shot(d/('page-'+str(len(pages))+'-visible.png'))
        run['pages']=pages;run['input_editable']=True
        logs=json.loads(remote.request('/log',since=log_since))['l']
        errors=[x for x in logs if 'budget exceeded' in x or 'source preparation failed' in x or 'no root view' in x]
        run['startup_log']=[x for x in logs if 'SPLASH_COMPILE' in x or 'splash:' in x]
        assert not errors,errors
        assert not any('[E]' in x for x in logs), [x for x in logs if '[E]' in x]
        run['changed_protected_files']={n:{'before':digest,'after':sha(jail/n)} for n,digest in before.items() if sha(jail/n)!=digest}
        run['protected_state_equal']=not run['changed_protected_files']
        run['model_ledger_equal']=sha(ledger)==ledger_before
        run['core_state_equal']=not any(n not in ['activity.json','activity.backup.json'] for n in run['changed_protected_files'])
        activity_now=json.loads((jail/'activity.json').read_text())
        additions=activity_now[len(activity_before):]
        run['activity_additions']=additions
        run['activity_increment_valid']=activity_now[:len(activity_before)]==activity_before and all(e.get('kind')=='calendar permission' and e.get('detail','').startswith('EventKit 权限 · ') and all(e.get(k,'')=='' for k in ['goal_id','run_id','request_id','account_scope']) for e in additions)
        backup_now=json.loads((jail/'activity.backup.json').read_text())
        run['activity_backup_valid']=activity_now[:len(backup_now)]==backup_now
        run['functional_checks_pass']=run['core_state_equal'] and run['model_ledger_equal'] and run['activity_increment_valid'] and run['activity_backup_valid']
        run['strict_persistence_pass']=run['protected_state_equal'] and run['model_ledger_equal']
        run['seconds']=time.monotonic()-started;run['pid']=json.loads(remote.request('/s'))['pid'];run['pass']=run['functional_checks_pass']
    save()
    def stop_on_failure(run):
        if a.fail_fast and not run['pass']:
            report['stopped_after_failure']=True;save();raise SystemExit(1)
    for i in range(a.cold_count):
        run={'index':i+1,'pass':False};report['cold'].append(run);d=a.out/f'cold-{i+1:02d}';d.mkdir();t=time.monotonic()
        try:
            command=[sys.executable,str(QUALITY/'launch_quality.py'),'--candidate',str(c),'--port',str(a.port)]
            if i or (c/'launched-by-final-quality.json').exists():command.append('--restart')
            prior_pid=report['cold'][-2].get('pid') if i else None
            proc=subprocess.run(command,text=True,capture_output=True,timeout=60);(d/'launch.txt').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
            (c/'launched-by-final-quality.json').write_text(json.dumps({'port':a.port,'host_sha256':m['host_sha256']}))
            remote.click('打开');inspect(run,t)
            if prior_pid is not None: assert run['pid']!=prior_pid, 'Cold launch reused Shell PID'
        except Exception as e:
            run['error']=str(e);run['seconds']=time.monotonic()-t;(d/'exception.txt').write_text(traceback.format_exc())
            if isinstance(e,subprocess.TimeoutExpired):
                (d/'launch.txt').write_bytes((e.stdout or b'')+(e.stderr or b''))
        try:capture(run,d)
        except Exception as e:run['capture_error']=str(e)
        save();print(json.dumps({'kind':'cold',**run},ensure_ascii=False),flush=True)
        stop_on_failure(run)
    for i in range(a.reopen_count):
        run={'index':i+1,'pass':False};report['reopen'].append(run);d=a.out/f'reopen-{i+1:02d}';d.mkdir();t=time.monotonic()
        try:
            pid=json.loads(remote.request('/s'))['pid'];offset=remote.log(300)['n'];remote.request('/k',k='down',c='KeyW',cmd=1);remote.request('/k',k='up',c='KeyW',cmd=1);time.sleep(.3)
            assert not any(w.get('i')=='goal_input' for w in remote.widgets()),'Muse did not close'
            remote.click('打开');inspect(run,t,offset);assert run['pid']==pid,'Ordinary reopen unexpectedly restarted Shell'
        except Exception as e:
            run['error']=str(e);run['seconds']=time.monotonic()-t;(d/'exception.txt').write_text(traceback.format_exc())
            if isinstance(e,subprocess.TimeoutExpired):
                (d/'launch.txt').write_bytes((e.stdout or b'')+(e.stderr or b''))
        try:capture(run,d)
        except Exception as e:run['capture_error']=str(e)
        save();print(json.dumps({'kind':'reopen',**run},ensure_ascii=False),flush=True)
        stop_on_failure(run)
    for i in range(a.restart_count):
        run={'index':i+1,'pass':False};report['restart'].append(run);d=a.out/f'restart-{i+1:02d}';d.mkdir();t=time.monotonic()
        try:
            prior_pid=json.loads(remote.request('/s'))['pid']
            command=[sys.executable,str(QUALITY/'launch_quality.py'),'--candidate',str(c),'--port',str(a.port),'--restart']
            proc=subprocess.run(command,text=True,capture_output=True,timeout=60);(d/'launch.txt').write_text(proc.stdout+proc.stderr);assert proc.returncode==0
            remote.click('打开');inspect(run,t);run['prior_pid']=prior_pid;assert run['pid']!=prior_pid,'Shell process did not restart'
        except Exception as e:
            run['error']=str(e);run['seconds']=time.monotonic()-t;(d/'exception.txt').write_text(traceback.format_exc())
            if isinstance(e,subprocess.TimeoutExpired):
                (d/'launch.txt').write_bytes((e.stdout or b'')+(e.stderr or b''))
        try:capture(run,d)
        except Exception as e:run['capture_error']=str(e)
        save();print(json.dumps({'kind':'restart',**run},ensure_ascii=False),flush=True);stop_on_failure(run)
    report['cold_pass']=sum(r['pass'] for r in report['cold']);report['reopen_pass']=sum(r['pass'] for r in report['reopen']);report['restart_pass']=sum(r['pass'] for r in report['restart']);save()
    if report['cold_pass']!=a.cold_count or report['reopen_pass']!=a.reopen_count or report['restart_pass']!=a.restart_count:raise SystemExit(1)
if __name__=='__main__':main()
