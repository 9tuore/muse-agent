"""One actual RC6 MiniMax/local-storage Goal, Memory conflict and Shell restart.

Root's synthetic model-only profile, no Mail account or system Calendar writes.
Raw failures persist; never retry a paid call or manufacture a model answer.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import argparse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'official_muse/phase2/tests'))
sys.path.insert(0, str(ROOT/'official_muse/ui_memory/tests'))
from remote import Remote
from visual_capture import navigate, shot, type_multiline
from ai_paid_guard import PaidGuard, input_bound_check


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--candidate', type=Path, default=ROOT/'official_muse/app/build/ui-memory-20261003/candidate-037-prelim-rc6-minimax')
    parser.add_argument('--out', type=Path, default=ROOT/'official_muse/prelim/evidence/live/rc6-goal-memory-restart')
    parser.add_argument('--port', type=int, default=8412)
    parser.add_argument('--goal-query', default='为当前项目建立一次性整理计划，目标：初赛回归合成资料归档。资料：合成甲项已完成；合成乙项待确认。仅保存到应用空间。')
    args = parser.parse_args()
    assert args.port not in [8401,8413,8414], 'User and real-account windows are excluded'
    candidate = args.candidate.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    jail = candidate/'private/apps/muse-goals'
    meta = json.loads((candidate/'candidate.json').read_text())
    assert meta['profile_kind']=='AUTHORIZED_MODEL_ONLY_SYNTHETIC'
    assert hashlib.sha256((jail/'bundle/main.splash').read_bytes()).hexdigest()==meta['source_sha256']
    binary=Path(meta['host_app_path'])/'Contents/MacOS/octosense'
    assert hashlib.sha256(binary.read_bytes()).hexdigest()==meta['host_sha256']
    host_source = ROOT/'official_muse/app/build/ui-memory-20261003/mail-host-033/OctoSense'
    contract = json.loads((ROOT/'official_muse/prelim/evidence/ai/paid-runner-preparation/input-bound-contract.json').read_text())
    guard = PaidGuard(candidate, ROOT/'official_muse/app/build/ui-memory-20261003/paid-budget-20261003/global-cost-table.json', str(out))
    r = Remote(args.port)
    report = {'status': 'RUNNING', 'source_sha256': meta['source_sha256'],
        'host_sha256': meta['host_sha256'], 'kind': 'REAL_VISIBLE_SHELL_MODEL_STORAGE_MEMORY_RESTART',
        'guard_sha256': hashlib.sha256((ROOT/'official_muse/prelim/tests/ai_paid_guard.py').read_bytes()).hexdigest(),
        'turns': [], 'external_mail_or_calendar_actions': False}

    def read(name):
        return json.loads((jail/name).read_text())

    def save():
        (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def current():
        d = read('chat-sessions.json')
        return next(s for s in d['sessions'] if s['id'] == d['selected_id'])

    def focus():
        if not any(w.get('i') == 'session_focus_project' for w in r.widgets()):
            r.click('切换')
        r.set_text('session_focus_project', '合成验收')
        r.set_text('session_focus_owner', '个人')
        r.click('使用这个项目')
        assert current()['focus_project'] == '合成验收' and current()['focus_owner'] == '个人'

    def top(area):
        x,y,w,h = r.find(area)['r']
        r.scroll(int(x+w-4), int(y+h/2), -10000)

    def turn(key, text, model):
        session = current(); n = len(session['messages'])
        bound = input_bound_check(candidate, session, text, host_source, contract)
        type_multiline(r, 'goal_input', text)
        before = guard.begin(key)
        report['inflight'] = {'id': key, 'before': before, 'query': text, 'input_bound': bound}
        save()
        r.click('发送')
        deadline = time.monotonic()+150
        while len(current()['messages']) < n+2 and time.monotonic()<deadline:
            time.sleep(.25)
        pair = current()['messages'][n:n+2]
        assert len(pair)==2 and pair[0]['text']==text
        proof = guard.finish(before, text, session['id'], pair[0]['at'], model)
        item = {'id': key, 'query': text, 'answer': pair[1], 'usage': proof, 'input_bound': bound}
        report['turns'].append(item);report.pop('inflight',None);save()
        shot(r,out/(key+'.png'))
        return item

    def durable():
        names = ['goals.json','memory.json','chat-sessions.json','mail-watch.json','global-memory-settings.json','ui-layout.json']
        names += [str(p.relative_to(jail)) for p in (jail/'results').glob('*.json')]
        return {n:hashlib.sha256((jail/n).read_bytes()).hexdigest() for n in names if (jail/n).exists()}

    save()
    try:
        navigate(r,'对话');r.click('＋ 新对话');focus()
        goal_query=args.goal_query
        first=turn('goal-candidate',goal_query,True)
        card=current()['proposals'][-1]
        assert card['action']=='goal_plan' and card['state']=='candidate'
        r.click_scroll('打开并核对','right_content')
        state=read('goals.json');goal=next(g for g in state['goals'] if g['id']==state['selected_id'])
        assert goal['status']=='planned' and goal['version']==1
        report['plan']=goal;save();shot(r,out/'plan.png')
        # input.current includes goal/source/items; bound that whole JSON
        # conservatively in addition to history/Memory/framing allowances.
        goal_data=json.dumps({k:goal[k] for k in ['goal','source','items']},ensure_ascii=True)
        bound=input_bound_check(candidate,current(),goal_data,host_source,contract)
        before=guard.begin('goal-suggestion');at=time.time()
        report['inflight']={'id':'goal-suggestion','before':before,'goal_id':goal['id'],'input_bound':bound};save()
        top('detail_view');r.click_scroll('请模型给建议','detail_view')
        deadline=time.monotonic()+150
        while time.monotonic()<deadline:
            updated=next(g for g in read('goals.json')['goals'] if g['id']==goal['id'])
            if updated['model_summary']:break
            time.sleep(.25)
        else:raise TimeoutError('No stored model suggestion; do not retry')
        proof=guard.finish(before,goal['goal'],current()['id'],at,True,goal['id'])
        report['model_suggestion']={'goal':updated,'usage':proof,'input_bound':bound};report.pop('inflight',None);save()
        shot(r,out/'model-plan.png')
        r.click_scroll('批准并执行','detail_view')
        deadline=time.monotonic()+20
        while time.monotonic()<deadline:
            state=read('goals.json');done=next(g for g in state['goals'] if g['id']==goal['id'])
            if done['status']=='completed':break
            time.sleep(.1)
        else:raise TimeoutError('Actual Goal storage/readback did not complete')
        result=read(done['result_path'])
        assert result['task_id']==goal['id'] and result['count']==len(done['items'])
        report['goal_result']={'goal':done,'result':result,'state':state};save();shot(r,out/'storage-readback.png')

        navigate(r,'对话')
        turn('conflict-one','记住：收口状态=待核对',False)
        turn('conflict-two','记住：收口状态=待确认',False)
        conflict=turn('conflict-block','收口状态是什么？只根据有效记忆回答。',False)
        assert '冲突' in conflict['answer']['text']
        report['conflict_memory']=read('memory.json');save()
        navigate(r,'记忆');r.set_text('memory_search','待核对');top('page_content')
        r.click_scroll('更正 / 遗忘','page_content');top('page_content')
        type_multiline(r,'memory_correction','收口状态=已核对');r.click('保存更正')
        report['corrected_memory']=read('memory.json');save();shot(r,out/'conflict-corrected.png')
        target = next(c['document']['id'] for c in report['corrected_memory']['claims']
            if c['document']['payload']['value']=='收口状态=已核对' and not c['document']['payload']['deleted'])
        r.set_text('memory_search','已核对');top('page_content')
        r.click_scroll('更正 / 遗忘','page_content');top('page_content')
        r.click('遗忘…');r.click_scroll('确认遗忘这条记忆','page_content')
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            saved=read('memory.json')
            forgotten=next(c for c in saved['claims'] if c['document']['id']==target)
            settings=read('global-memory-settings.json')
            if forgotten['document']['payload']['deleted'] and not settings['forget_pending']:
                break
            time.sleep(.1)
        else:
            report['incomplete_forget_settings']=settings;save()
            raise RuntimeError('Forget did not commit canonically; do not treat a click or empty retrieval as PASS')
        assert forgotten['history']==[] and forgotten['source_history']==[]
        assert settings['enabled'] is True
        report['forgotten_memory']=read('memory.json');save();shot(r,out/'conflict-forgotten.png')
        navigate(r,'对话')
        before_hashes=durable();before_goal=read('goals.json');before_activity=read('activity.json')
        before_ledger=guard.ledger.read_bytes()
        report['restart_before_hashes']=before_hashes;save()
        run=subprocess.run([sys.executable,str(ROOT/'official_muse/ui_memory/launch_candidate.py'),
            '--candidate',str(candidate),'--port',str(args.port),'--restart'],capture_output=True,text=True,timeout=60)
        (out/'restart-launch.txt').write_text(run.stdout+run.stderr)
        assert run.returncode==0
        r.click('已安装');r.click('Muse');r.click('打开');r.wait_for('goal_input',30);time.sleep(1)
        after_hashes=durable();after_goal=read('goals.json');after_activity=read('activity.json')
        extra=after_activity[len(before_activity):]
        report['restart']={'hashes_before':before_hashes,'hashes_after':after_hashes,
            'durable_bytes_unchanged':before_hashes==after_hashes,'goals_runs_actions_unchanged':before_goal==after_goal,
            'model_ledger_unchanged':before_ledger==guard.ledger.read_bytes(),
            'history_prefix_unchanged':after_activity[:len(before_activity)]==before_activity,
            'extra_event_kinds':[e['kind'] for e in extra]};save()
        assert all(report['restart'][k] for k in ['durable_bytes_unchanged','goals_runs_actions_unchanged','model_ledger_unchanged','history_prefix_unchanged'])
        assert all(e['kind']=='restart restore' for e in extra)
        shot(r,out/'restart.png')
        navigate(r,'对话');r.click('＋ 新对话');focus()
        cross=turn('cross-session-after-restart','请按我保存的汇报格式回答：当前项目星尘的内部代号是什么？收口状态是什么？不知道就说明没有资料。',True)
        assert not any(value in cross['answer']['text'] for value in ['ORBIT-472','NOVA-593','收口状态=待核对','收口状态=待确认','收口状态=已核对'])
        report['retrieval_after_restart']=read('memory-retrieval-last.json')
        report['memory_after_restart']=read('memory.json')
        deleted_ids={c['document']['id'] for c in report['memory_after_restart']['claims'] if c['document']['payload']['deleted']}
        assert all(h['id'] not in deleted_ids for h in report['retrieval_after_restart']['hits'])
        preference=next(c['document']['id'] for c in report['memory_after_restart']['claims']
            if c['document']['payload']['value']=='汇报应先写结论，再列三项重点。')
        assert any(h['id']==preference for h in report['retrieval_after_restart']['hits']), 'Live global preference was not actually retrieved'
        report['status']='TECHNICAL_CHECKS_COMPLETE_SEMANTIC_REVIEW_PENDING';save()
        print(json.dumps({'status':report['status'],'goal_id':goal['id'],'internal_storage_goal_completed':True,'actual_system_chain_pending':True}))
    except Exception as error:
        guard.unknown()
        report['status']='PARTIAL';report['error']=str(error);save()
        (out/'failure.txt').write_text(traceback.format_exc())
        raise


if __name__=='__main__':
    main()
