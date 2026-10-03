#!/usr/bin/env python3
"""Synthetic-only visible Shell checks. Uses actual model/Goal/storage, no external writes.

Run only against the isolated signed candidate prepared by prepare_candidate.py.
Mail/calendar side effects require separate, precise human confirmations.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/phase2/tests'))
from remote import Remote
sys.path.insert(0, str(Path(__file__).parent))
from visual_capture import shot


def read(jail, name):
    return json.loads((jail / name).read_text())


def wait(check, seconds=145):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        value = check()
        if value:
            return value
        time.sleep(.25)
    raise TimeoutError('Candidate state did not reach the expected condition')


def selected(jail):
    data = read(jail, 'chat-sessions.json')
    return next(s for s in data['sessions'] if s['id'] == data['selected_id'])


def top(remote, area='page_content'):
    x, y, w, h = remote.find(area)['r']
    remote.scroll(int(x+w/2), int(y+h/2), -10000)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8411)
    p.add_argument('--stage', choices=('chat', 'goals', 'snapshot'), required=True)
    args = p.parse_args()
    candidate = args.candidate.resolve()
    jail = candidate / 'private/apps/muse-goals'
    manifest = read(candidate, 'candidate.json')
    source_hash = hashlib.sha256((jail / 'bundle/main.splash').read_bytes()).hexdigest()
    assert source_hash == manifest['source_sha256'], 'Installed bytes differ from candidate'
    args.out.mkdir(parents=True, exist_ok=False)
    r = Remote(args.port)
    report = {'source_sha256': source_hash, 'version': manifest['version'],
              'kind': 'VISIBLE_OCTOSENSE_SHELL_LIVE', 'checks': {}, 'records': [],
              'mail_send': False, 'calendar_write': False}

    def save():
        (args.out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')

    def turn(question, model=True):
        origin = selected(jail)
        count = len(origin['messages'])
        r.set_text('goal_input', question)
        r.click('发送')
        answer = wait(lambda: next((s['messages'][-1] for s in read(jail,'chat-sessions.json')['sessions']
                                   if s['id'] == origin['id'] and len(s['messages']) >= count+2), None))
        record = {'session_id': origin['id'], 'question': question, 'answer': answer['text'],
                  'state': answer['state'], 'model_expected': model}
        report['records'].append(record)
        save()
        print(json.dumps(record, ensure_ascii=False), flush=True)
        return record

    try:
        if args.stage == 'chat':
            r.click_scroll('对话','shortcuts')
            r.click('＋ 新对话')
            a = selected(jail)['id']
            turn('记住：合成项目星尘的当前代号=ORBIT-472', False)
            report['checks']['memory_saved_actual_storage'] = any(
                c['document']['payload']['value'] == '合成项目星尘的当前代号=ORBIT-472'
                for c in read(jail,'memory.json')['claims'])
            r.click('＋ 新对话')
            b = selected(jail)['id']
            answer = turn('合成项目星尘的当前代号是什么？请只回答代号。')
            report['checks']['cross_session_model_call_success'] = answer['state'] == 'success' and a != b
            report['checks']['cross_session_model_semantics'] = 'ORBIT-472' in answer['answer']
            shot(r, args.out / 'cross-session-memory.png')
            r.click_scroll('记忆','shortcuts')
            r.set_text('memory_search','ORBIT-472')
            top(r)
            r.click_scroll('更正 / 遗忘','page_content')
            top(r)
            r.set_text('memory_correction','合成项目星尘的当前代号=NOVA-593')
            r.click('保存更正')
            report['checks']['correction_revision_and_history'] = any(
                c['document']['payload']['value'] == '合成项目星尘的当前代号=NOVA-593'
                and c['document']['revision'] == 2 and c.get('history')
                for c in read(jail,'memory.json')['claims'])
            shot(r, args.out / 'corrected-memory.png')
            r.click_scroll('对话','shortcuts')
            # Choose the original session by its persisted deterministic title.
            original = next(s for s in read(jail,'chat-sessions.json')['sessions'] if s['id'] == a)
            top(r,'history_list')
            r.click_scroll(original['title'],'history_list')
            time.sleep(32)  # Existing free local model service rate gate.
            corrected = turn('合成项目星尘的当前代号是什么？请只回答最新代号。')
            report['checks']['original_session_uses_latest_memory'] = 'NOVA-593' in corrected['answer'] and 'ORBIT-472' not in corrected['answer']
            shot(r, args.out / 'original-session-corrected.png')
            r.click_scroll('记忆','shortcuts')
            r.set_text('memory_search','NOVA-593')
            top(r)
            r.click_scroll('更正 / 遗忘','page_content')
            top(r)
            r.click('遗忘…')
            r.click_scroll('确认遗忘这条记忆','page_content')
            data = read(jail,'memory.json')
            report['checks']['forget_scrubs_value_and_keeps_tombstone'] = any(
                c['document']['payload']['deleted'] and not c['document']['payload']['value']
                for c in data['claims']) and bool(data['forget'])
            shot(r, args.out / 'forgotten-memory.png')
            r.click_scroll('对话','shortcuts')
            original_b = next(s for s in read(jail,'chat-sessions.json')['sessions'] if s['id'] == b)
            top(r,'history_list')
            r.click_scroll(original_b['title'],'history_list')
            time.sleep(32)
            forgotten = turn('合成项目星尘的当前代号是什么？')
            report['checks']['forgotten_derived_reply_not_recalled'] = forgotten['state'] == 'success' and all(
                value not in forgotten['answer'] for value in ('ORBIT-472','NOVA-593'))
            report['checks']['forgotten_memory_not_in_retrieval'] = not read(jail,'memory-retrieval-last.json')['hits']
            shot(r, args.out / 'forgotten-cross-session.png')
        elif args.stage == 'goals':
            for n in (1, 2):
                r.click_scroll('对话','shortcuts')
                r.click('＋ 目标')
                title = f'MUSE-UI-GLOBAL 合成任务 {n}'
                r.set_text('goal_input',title)
                r.set_text('source_input',f'合成项目第{n}项；核对后保留结果；禁止真实发信和改日历')
                r.click('生成计划')
                goal = wait(lambda: next((g for g in read(jail,'goals.json')['goals'] if g['goal'] == title),None),20)
                gid = goal['id']
                if n == 1:
                    time.sleep(32)
                    r.click_scroll('请模型给建议','detail_view')
                    goal = wait(lambda: next((g for g in read(jail,'goals.json')['goals']
                                             if g['id'] == gid and g.get('model_summary')),None))
                    report['checks']['goal_actual_model_complete'] = bool(goal['model_summary'])
                r.click_scroll('批准并执行','detail_view')
                goal = wait(lambda: next((g for g in read(jail,'goals.json')['goals']
                                         if g['id'] == gid and g['status'] == 'completed'),None),30)
                result = read(jail,goal['result_path'])
                state = read(jail,'goals.json')
                report['checks'][f'goal_{n}_independent_readback'] = result['task_id'] == gid and any(
                    run['goal_id'] == gid and run['status'] == 'completed' for run in state['runs'])
                report['records'].append({'goal_id':gid,'version':goal['version'],'path':goal['result_path'],
                                          'sha256':hashlib.sha256((jail/goal['result_path']).read_bytes()).hexdigest()})
                shot(r, args.out / f'goal-{n}.png')
                save()
            r.click_scroll('长期目标','shortcuts')
            shot(r, args.out / 'multiple-goals.png')
        else:
            names = ['goals.json','memory.json','chat-sessions.json','ui-layout.json','global-memory-settings.json']
            names += [str(p.relative_to(jail)) for p in (jail/'results').glob('*.json')]
            report['hashes'] = {name:hashlib.sha256((jail/name).read_bytes()).hexdigest() for name in names if (jail/name).exists()}
            state = read(jail,'goals.json')
            report['counts'] = {key:len(state.get(key,[])) for key in ('goals','runs','actions')}
            report['activity'] = [e['kind'] for e in read(jail,'activity.json')]
            shot(r, args.out / 'snapshot.png')
        report['status'] = 'PASS' if all(report['checks'].values()) else 'PARTIAL'
        save()
    except Exception as error:
        report['status'] = 'ERROR'
        report['error'] = str(error)
        save()
        raise


if __name__ == '__main__':
    main()
