#!/usr/bin/env python3
"""Visible U04 regression and actual isolated process restart; no real Host calls."""
import argparse, hashlib, json, os, shutil, socket, subprocess, time
from pathlib import Path
from PIL import Image
from visual_capture import HOST, Remote, TRANSPORT, shot

SCENE = '''
fn u04_seed(){
 if fs.exists("u04-seed.json") { return }
 notification_enabled = false
 fs.write("notification-settings.json",{schema: 1 enabled: false}.to_json())
 mail_watch.enabled = false mail_watch_save()
 let a = chat_selected_id
 chat_sessions[chat_session_index(a)].title = "U04 原会话A" chat_save()
 ui.goal_input.set_text("U04 合成目标A") ui.source_input.set_text("ORBIT隔离资料")
 make_plan()
 let id = task.id let path = task.result_path
 let run_id = core_start_run(id,1,"u04-fixture-approved")
 let artifact = {schema: 1 task_id: id run_id: run_id count: 1 model_summary: ""
     items: [{text: "ORBIT隔离结果A"}]}
 fs.mkdir("results") fs.write(path,artifact.to_json())
 let done = core_finish_run(id,run_id,"completed",path)
 chat_restore_goal_view() set_page("Chat")
 fs.write("u04-seed.json",{session_a: a goal_id: id result_path: path done: done}.to_json())
}
start_timeout(1.0,|| u04_seed())
'''


def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--size',default='1280x800');p.add_argument('--port',type=int,default=8484);a=p.parse_args()
 a.out=a.out.resolve();a.source=a.source.resolve()
 with socket.socket() as s:
  if s.connect_ex(('127.0.0.1',a.port))==0:raise RuntimeError('Port occupied; existing process untouched')
 a.out.mkdir(parents=True,exist_ok=False);bundle=a.out/'bundle';state=a.out/'state';data=state/'muse-goals'
 shutil.copytree(a.source.parent,bundle)
 source=a.source.read_text();(bundle/'main.splash').write_text(source.replace('host.request(','visual_host(').replace('start_timeout(0.05, || boot())',TRANSPORT+'\nstart_timeout(0.05, || boot())'+SCENE))
 env=dict(os.environ,MAKEPAD_REMOTE=str(a.port));env.pop('MAKEPAD_HIDE_WINDOWS',None)
 r=Remote(a.port);proc=None;log=None;checks={};snapshots={}
 def start(label):
  nonlocal proc,log
  log=(a.out/(label+'.log')).open('w')
  proc=subprocess.Popen([str(HOST),'--bundle',str(bundle),'--app-data',str(state),'--allow-unsigned','--stamp','--size',a.size],env=env,cwd=HOST.parents[2],stdout=log,stderr=log)
  deadline=time.monotonic()+20
  while True:
   try:r.find('卡');break
   except (AssertionError,OSError):
    if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError('UI startup unavailable; inspect runtime log')
    time.sleep(.1)
  deadline=time.monotonic()+20
  while not (data/'u04-seed.json').exists():
   if proc.poll() is not None or time.monotonic()>deadline:raise RuntimeError('No seed; inspect runtime log')
   time.sleep(.1)
  time.sleep(1.5)
 def stop():
  nonlocal proc,log
  if proc is not None:
   try:r.request('/quit')
   except OSError:proc.terminate()
   proc.wait(timeout=10);proc=None;log.close()
 def capture(label,expected):
  r.click('卡');widgets=r.widgets()
  title=any(w.get('ty')=='Label' and w.get('t')=='U04 合成目标A' for w in widgets)
  item=any(w.get('ty')=='Label' and 'ORBIT隔离结果A' in w.get('t','') for w in widgets)
  empty=any(w.get('t')=='结果会出现在这里。' for w in widgets)
  checks[label]=(title and item) if expected else (not title and not item and empty)
  snapshots[label]={'goal_title_visible':title,'artifact_visible':item,'empty_hint':empty}
  shot(r,a.out/(label+'.png'));(a.out/(label+'.snap.json')).write_text(json.dumps(widgets,ensure_ascii=False,indent=2)+'\n')
  r.click('返回页面')
 def stable():
  return {str(x.relative_to(data)):hashlib.sha256(x.read_bytes()).hexdigest() for x in [data/'goals.json',data/meta['result_path']]}
 try:
  start('first-start');meta=json.loads((data/'u04-seed.json').read_text());assert meta['done']
  capture('original-goal',True)
  r.click('＋ 新对话');capture('new-empty-no-goal',False)
  r.click_scroll('U04 原会话A','history_list');capture('switch-original-restores',True)
  r.click_scroll('新对话','history_list');capture('switch-empty-again',False)
  before=stable();saved=json.loads((data/'goals.json').read_text());calls_before=json.loads((data/'visual-calls.json').read_text())
  stop();start('process-restart')
  capture('restart-empty-no-goal',False)
  r.click_scroll('U04 原会话A','history_list');capture('restart-switch-original-restores',True)
  after=stable();restored=json.loads((data/'goals.json').read_text())
  checks['goal_artifact_sha_unchanged']=before==after
  checks['goal_run_action_counts_unchanged']=[len(saved[k]) for k in ('goals','runs','actions')]==[len(restored[k]) for k in ('goals','runs','actions')]==[1,1,0]
  calls=json.loads((data/'visual-calls.json').read_text())
  forbidden=[x for x in calls+calls_before if x in ('model.complete','mail.send','calendar.create','calendar.update','calendar.delete')]
  checks['restart_no_model_or_external_write']=not forbidden
  blank=[];uniform=[]
  for f in a.out.glob('*.png'):
   im=Image.open(f).convert('RGB');n,_=max(im.getcolors(im.width*im.height))
   if n/(im.width*im.height)>.99:
    uniform.append(f.name)
    # An intentionally empty result page can be >99% background while its
    # actual header and empty hint are visible. Keep the flag and inspect
    # their top strip; a genuinely blank/occluded capture still fails.
    strip=im.crop((0,0,im.width,min(160,im.height)))
    largest,_=max(strip.getcolors(strip.width*strip.height))
    if not snapshots[f.stem]['empty_hint'] or largest/(strip.width*strip.height)>.99:blank.append(f.name)
  report={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'host_sha256':hashlib.sha256(HOST.read_bytes()).hexdigest(),'requested_size':a.size,'test_kind':'FIXTURE_VISIBLE_PROCESS_RESTART','checks':checks,'snapshots':snapshots,'before_sha':before,'after_sha':after,'host_calls':calls,'forbidden_calls':forbidden,'uniform_images':uniform,'blank_images':blank,'boundary':'Synthetic stored artifact and explicitly synthetic local approval; full production boot/UI and real process exit/relaunch, no real model/OS service.'}
  (a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
  return int(not all(checks.values()) or bool(blank) or bool(forbidden))
 except Exception as error:
  (a.out/'error.json').write_text(json.dumps({'error':str(error),'checks':checks},ensure_ascii=False,indent=2)+'\n')
  raise
 finally:stop()

if __name__=='__main__':raise SystemExit(main())
