#!/usr/bin/env python3
"""Verify real UI Goal association and ask the local model about a read-back result."""
import argparse,hashlib,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'official_muse/phase2/tests'))
sys.path.insert(0,str(Path(__file__).parent))
from remote import Remote
from visual_capture import navigate,type_multiline,shot

def main():
 p=argparse.ArgumentParser();p.add_argument('--candidate',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p.add_argument('--port',type=int,default=8413);p.add_argument('--wire',type=Path,required=True);a=p.parse_args()
 meta=json.loads((a.candidate/'candidate.json').read_text());assert meta['profile_kind']=='LOCAL_MODEL_ONLY_SYNTHETIC'
 jail=a.candidate/'private/apps/muse-goals';r=Remote(a.port);a.out.mkdir(parents=True,exist_ok=False)
 def read(n):return json.loads((jail/n).read_text())
 def selected():
  d=read('chat-sessions.json');return next(s for s in d['sessions'] if s['id']==d['selected_id'])
 def top(area):
  x,y,w,h=r.find(area)['r'];r.scroll(int(x+w-4),int(y+h/2),-10000)
 report={'source_sha256':meta['source_sha256'],'host_sha256':meta['host_sha256'],
         'kind':'LIVE_VISIBLE_SHELL_REAL_MODEL_LOCAL_GOAL_DATA','checks':{},'mail_send':False,'calendar_write':False}
 def save():(a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 try:
  origin=selected();gid=origin['goal_id'];goal=next(g for g in read('goals.json')['goals'] if g['id']==gid)
  stored=read(goal['result_path']);assert stored['task_id']==gid and goal['status']=='completed'
  navigate(r,'对话')
  # A result is shown for its associated chat, and hidden for an empty new chat.
  top('right_content')
  report['checks']['origin_result_visible']=any(w.get('t')==goal['goal'] for w in r.widgets())
  shot(r, a.out/'original-result.png')
  r.click('＋ 新对话');report['empty_session_id']=selected()['id']
  report['checks']['new_chat_has_no_goal_association']=selected()['goal_id']==''
  report['checks']['new_chat_has_no_prior_result_card']=not any(w.get('t')==goal['goal'] for w in r.widgets())
  shot(r, a.out/'new-chat-no-stale-result.png')
  top('history_list');r.click_scroll(origin['title'],'history_list');top('right_content')
  report['checks']['switch_back_restores_associated_result']=selected()['goal_id']==gid and any(w.get('t')==goal['goal'] for w in r.widgets())
  before_goals=hashlib.sha256((jail/'goals.json').read_bytes()).hexdigest();before=len(selected()['messages'])
  question='当前任务的结果有几条？请根据已读回结果回答。'
  wire_start=len(a.wire.read_text().splitlines());type_multiline(r,'goal_input',question)
  try:r.click('发送')
  except AssertionError:
   assert len(selected()['messages'])>before and selected()['messages'][before]['text']==question
  deadline=time.monotonic()+150
  while len(selected()['messages'])<before+2:
   if time.monotonic()>deadline:raise TimeoutError('Goal focus model did not return')
   time.sleep(.25)
  reply=selected()['messages'][-1]
  records=[json.loads(s) for s in a.wire.read_text().splitlines()[wire_start:]]
  prompt='\n'.join(m.get('content','') for w in records for m in w.get('messages',[]))
  report['checks']['wire_contains_actual_goal_and_readback_count']=gid in prompt and 'result_count' in prompt and str(stored['count']) in prompt
  report['checks']['question_did_not_reexecute_goal']=before_goals==hashlib.sha256((jail/'goals.json').read_bytes()).hexdigest()
  report['expected_count']=stored['count'];report['question']=question;report['actual_reply']=reply
  report['semantic_review']='pending';report['wire_requests']=len(records);report['goal_id']=gid
  shot(r, a.out/'goal-result-question.png')
  report['status']='PASS' if all(report['checks'].values()) else 'PARTIAL';save();print(json.dumps(report,ensure_ascii=False))
 except Exception as e:report['status']='ERROR';report['error']=str(e);save();raise
if __name__=='__main__':main()
