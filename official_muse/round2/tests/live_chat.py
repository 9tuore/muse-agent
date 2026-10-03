#!/usr/bin/env python3
"""Twelve synthetic rounds in an isolated visible Shell and actual local model."""
import argparse,json,re
from pathlib import Path
import sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase2/tests'))
from remote import Remote
from live_chat_final import selected,top

ROOT=Path(__file__).resolve().parents[3]
p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8490)
p.add_argument('--jail',type=Path,default=ROOT/'official_muse/app/build/round2/isolated-apps/muse-goals')
p.add_argument('--output',type=Path,default=ROOT/'official_muse/app/build/round2/live-chat')
a=p.parse_args();OUT=a.output;JAIL=a.jail
candidate=json.loads((ROOT/'official_muse/round2/candidate.json').read_text())
import hashlib
assert hashlib.sha256((JAIL/'bundle/main.splash').read_bytes()).hexdigest()==candidate['bundle_files_sha256']['main.splash'], 'installed candidate differs'
OUT.mkdir(parents=True,exist_ok=True);r=Remote(a.port);r.click('对话');top(r);r.click('新对话')
old_id=selected(JAIL)['id'];records=[];last=0
rounds=['My project codename is ORBIT.','请用一句话说明变量。','2 加 3 是多少？','把 morning 翻译为中文。','给一个简短的待办建议。',
        'Correction: codename is NOVA, not ORBIT.','请用一句话解释数组。','Do not repeat the sensitive synthetic string TEST-R2-SECRET.',
        '给一个水果例子。','给一个旅行用品例子。','What is the current codename?',
        'Without repeating the sensitive synthetic string, how many hyphens does it contain?']
def turn(question):
    global last
    cooldown=32-(time.monotonic()-last)
    if cooldown>0:time.sleep(cooldown)
    count=len(selected(JAIL)['messages']);r.set_text('goal_input',question);r.click('发送');last=time.monotonic()
    until=time.monotonic()+150
    while time.monotonic()<until:
        current=selected(JAIL)
        if len(current['messages'])>=count+2:
            answer=current['messages'][-1]
            rec={'question':question,'answer':answer['text'],'state':answer['state'],'session_id':current['id']}
            records.append(rec);(OUT/'progress.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
            print(json.dumps({'turn':len(records),'state':answer['state'],'answer':answer['text']},ensure_ascii=False),flush=True)
            return rec
        time.sleep(.25)
    raise TimeoutError('model response absent')
for index,q in enumerate(rounds):
    turn(q)
    if index in (0,5,10,11):r.shot(OUT/f'round-{index+1}.png')
before=selected(JAIL)['messages'];top(r);r.click('新对话');new_id=selected(JAIL)['id']
turn('What is the current codename?')
data=json.loads((JAIL/'chat-sessions.json').read_text());old=next(s for s in data['sessions'] if s['id']==old_id)
top(r)
peers=[s for s in data['sessions'] if s['id']!=data['selected_id'] and s['title']==old['title']]
assert len(peers)==1, 'ambiguous session title; do not choose another session'
area=r.find('page_content')['r']
for _ in range(50):
    buttons=[w for w in r.widgets() if w.get('ty')=='Button' and w.get('t','').startswith(old['title']+' · ')]
    if buttons and buttons[0]['r'][3]>=24 and buttons[0]['r'][1]+buttons[0]['r'][3]<=area[1]+area[3]-10:
        r.click(buttons[0]['t']);break
    r.scroll(int(area[0]+area[2]-4),int(area[1]+area[3]/2),80)
else:raise AssertionError('test session not reachable')
assert selected(JAIL)['id']==old_id
assert selected(JAIL)['messages']==before
turn('What is the current codename?')
checks={'all_calls_success':all(x['state']=='success' for x in records),'correction_recall':'NOVA' in records[10]['answer'].upper(),
        'no_sensitive_repeat':'TEST-R2-SECRET' not in records[11]['answer'],
        'sensitive_hyphen_count':bool(re.search(r'(?:2|两|二)\s*(?:个|条|hyphen|连字符)',records[11]['answer'],re.I)),
        'new_session_acknowledges_no_basis':any(x in records[12]['answer'].lower() for x in ['不知道','未知','不清楚','未提供','没有','不确定',"don't have information",'do not know']),
        'new_session_isolated':'NOVA' not in records[12]['answer'].upper() and 'ORBIT' not in records[12]['answer'].upper(),
        'switch_recall':'NOVA' in records[13]['answer'].upper()}
report={'candidate':candidate['muse_commit'],'bundle_version':candidate['bundle_version'],'round_count':12,
        'kind':'SHELL_LIVE','checks':checks,'turns':records,'CHAT_CONTEXT_TRANSPORT':'see relay wire.jsonl',
        'FACT_RECALL':'PASS' if checks['correction_recall'] and checks['switch_recall'] else 'MODEL_LIMITATION',
        'INSTRUCTION_FOLLOWING':'PASS' if checks['no_sensitive_repeat'] and checks['sensitive_hyphen_count'] else 'MODEL_LIMITATION',
        'MODEL_LIMITATION':not all(checks.values())}
(OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
