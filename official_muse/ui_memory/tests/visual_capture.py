#!/usr/bin/env python3
"""Visible official card-host UI, synthetic authorized services; no external actions."""
import argparse, hashlib, json, os, shutil, socket, struct, subprocess, sys, time
from pathlib import Path
from urllib.error import HTTPError
from PIL import Image, ImageChops
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'official_muse/phase2/tests'))
from remote import Remote
HOST=Path(os.environ.get('MUSE_CARD_HOST', '/Users/mima0000/.codex/worktrees/muse-official-migration/phase2-host/OctoSense/target/release/card-host'))
TRANSPORT='''
let visual_calls = []
fn visual_host(service,args,cb){
 visual_calls.push(service)
 fs.write("visual-calls.json",visual_calls.to_json())
 if service == "mail.accounts" { cb({is_ok: true data: []}) return }
 if service == "calendar.status" { cb({is_ok: true data: {permission: "full_access" calendars: [{id: "synthetic-calendar" title: "合成验收日历" writable: true}]}}) return }
 if service == "calendar.list" {
  let matching = []
  for event in calendar_events {
   if event.calendar_id == args.calendar_id && calendar_iso_utc(event.start) < calendar_iso_utc(args.end)
      && calendar_iso_utc(event.end) > calendar_iso_utc(args.start) { matching.push(event) }
  }
  cb({is_ok: true data: {events: matching truncated: false}}) return
 }
 cb({is_ok: false error: "合成视觉环境不提供此操作。"})
}
'''
def navigate(r,page):
 if any(w.get('i') == 'shortcuts' for w in r.widgets()):
  x,y,w,h=r.find('shortcuts')['r']
  r.scroll(int(x+w/2),int(y+h/2),-500)
  return r.click_scroll(page,'shortcuts')
 for _ in range(12):
  try:
   w=r.find(page)
   if w['r'][2]>2 and w['r'][3]>=24: return r.click(page)
  except AssertionError: pass
  r.scroll(50,180,90)
 raise AssertionError('Navigation remains unreachable: '+page)
def type_multiline(r,key,value):
 # Remote.set_text uses unmodified End (verified LineEnd in this runtime).
 # For multiline input, advance through observed characters to the last line
 # before clearing; do not mistake the helper's partial clear for a UI defect.
 widget=r.find(key);x,y,w,h=widget['r']
 r.request('/click',x=int(x+w/2),y=int(y+h/2))
 for _ in widget['val']: r.request('/k',k='down',c='ArrowDown')
 r.request('/k',k='down',c='End')
 for _ in widget['val']: r.request('/k',k='down',c='Backspace')
 r._wait_value(key,'')
 r.request('/t',t=value)
 r._wait_value(key,value)
def shot(r,path):
 for attempt in range(3):
  try: r.shot(path);return
  except HTTPError as error:
   body=error.read().decode(errors='replace')
   print('Screenshot attempt',attempt+1,'HTTP',error.code,body,flush=True)
   if error.code != 404 or attempt == 2: raise
   r.widgets();time.sleep(.3)
def body_area(r,page):
 names={'对话':'chat_body','长期目标':'goals_body','记忆':'memory_body','活动记录':'activity_body','操作记录':'activity_body',
        '邮箱':'mail_list_body','日历':'calendar_editor','能力授权':'capabilities_body','设置':'settings_body'}
 name=names[page]
 return name if any(w.get('i')==name for w in r.widgets()) else 'page_content'
def first_screen(r,page):
 titles={'长期目标':'目标与持续任务','记忆':'全局记忆','活动记录':'活动记录','操作记录':'操作记录',
         '邮箱':'收件箱','日历':'系统日历','能力授权':'能力与授权','设置':'邮箱'}
 area=body_area(r,page);rect=r.find(area)['r']
 labels=[w for w in r.widgets() if w.get('ty')=='Label' and w.get('t')==titles[page]
         and w['r'][2]>2 and w['r'][3]>2 and rect[1]-1<=w['r'][1]<rect[1]+80]
 return {'body':area,'body_rect':rect,'title':titles[page],'title_at_first_screen':bool(labels)}
def reachable(r,key,area):
 # The centre may be inside the nested original-body scroll view. Use the
 # outer pane's padding to bring its reply/collapse controls into view.
 for _ in range(24):
  try:
   widget=r.find(key)
   if widget['r'][2]>=2 and widget['r'][3]>=24: return widget
  except AssertionError: pass
  x,y,w,h=r.find(area)['r'];r.scroll(int(x+w-4),int(y+h/2),120)
 raise AssertionError('Control unreachable in outer pane: '+key)
def click_scroll_edge(r,key,area):
 reachable(r,key,area);r.click(key)
def long_mail_check(r,out):
 area='right_page_content'
 checks={}
 checks['original_default_collapsed']=any(w.get('t')=='展开原邮件全文' for w in r.widgets()) and not any(w.get('t')=='收起原邮件' for w in r.widgets())
 click_scroll_edge(r,'展开原邮件全文',area)
 # Keep the outer pane at its first screen before inspecting the nested view.
 x,y,w,h=r.find(area)['r'];r.scroll(int(x+w-4),int(y+h/2),-10000)
 labels=[w for w in r.widgets() if w.get('ty')=='Label' and w.get('t','').startswith('合成验收段落：') and len(w.get('t',''))>300]
 # In a short viewport the collapse button is below the nested body; its
 # absence from /snap is not a failure to expand. It is reached below.
 checks['original_expanded']=bool(labels)
 shot(r,out/'mail-original-expanded.png')
 if labels:
  rect=labels[0]['r'];checks['original_visible_rect']=rect
  checks['original_bounded_height']=64<=rect[3]<=220
  x,y,w,h=rect
  for _ in range(3):r.scroll(int(x+w/2),int(y+h/2),300)
  shot(r,out/'mail-original-scrolled.png')
  checks['original_scroll_image_changed']=ImageChops.difference(Image.open(out/'mail-original-expanded.png').convert('RGB'),Image.open(out/'mail-original-scrolled.png').convert('RGB')).getbbox() is not None
 click_scroll_edge(r,'收起原邮件',area)
 checks['original_collapsed_again']=any(w.get('t')=='展开原邮件全文' for w in r.widgets()) and not any(w.get('t')=='收起原邮件' for w in r.widgets())
 shot(r,out/'mail-original-collapsed.png')
 click_scroll_edge(r,'回复这封邮件',area)
 checks['reply_opens_intent']=r.find('mail_reply_intent_page').get('val')=='请礼貌说明改约。'
 checks['reply_input_rect']=r.find('mail_reply_intent_page')['r']
 shot(r,out/'mail-reply-intent.png')
 return checks
def collapsed_navigate(r,page):
 if not any(w.get('i')=='shortcuts' for w in r.widgets()):r.click('☰')
 navigate(r,page);r.click('‹')
def column_checks(r,out,size):
 checks={}
 r.click('‹')
 checks['left_collapsed']=any(w.get('t')=='☰' for w in r.widgets())
 shot(r,out/'columns-left-collapsed.png')
 r.click('☰')
 checks['left_reexpanded']=any(w.get('i')=='shortcuts' for w in r.widgets())
 shot(r,out/'columns-left-expanded.png')
 if int(size.split('x')[0])>740:
  r.click('收起')
  checks['right_collapsed']=not any(w.get('i')=='right_column' and w['r'][2]>2 for w in r.widgets())
  shot(r,out/'columns-right-collapsed.png')
  r.click('›')
  checks['right_reexpanded']=any(w.get('i')=='right_column' and w['r'][2]>2 for w in r.widgets())
  shot(r,out/'columns-right-expanded.png')
 else:
  checks['right_boundary']='Width <=740 uses zero-width result column; full result page is exercised separately.'
 return checks
def form_checks(r,out):
 checks={}
 r.click('返回页面')
 if any(w.get('t')=='收起' for w in r.widgets()):r.click('收起')
 collapsed_navigate(r,'日历')
 checks['calendar_sidebar_collapsed']=any(w.get('t')=='☰' for w in r.widgets())
 click_scroll_edge(r,'＋ 新建日程','calendar_editor')
 values={'calendar_title':'MUSE-UI-FIXTURE-NO-WRITE','calendar_start':'2026-10-05T15:00:00+08:00',
         'calendar_end':'2026-10-05T16:00:00+08:00','calendar_timezone':'Asia/Shanghai','calendar_location':'合成会议室'}
 readback={}
 for key,value in values.items():
  reachable(r,key,'calendar_editor');r.set_text(key,value)
  readback[key]=r.find(key).get('val')==value
 checks['calendar_fields_readback']=all(readback.values());checks['calendar_field_readbacks']=readback
 (out/'form-partial.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
 click_scroll_edge(r,'查询当前候选冲突','calendar_editor')
 click_scroll_edge(r,'预览精确日历操作','calendar_editor')
 confirm=reachable(r,'确认执行这项系统日历操作','calendar_editor')
 checks['calendar_confirmation_reachable']=confirm['r'][2]>=2 and confirm['r'][3]>=24
 checks['calendar_confirmation_rect']=confirm['r'];checks['calendar_confirm_clicked']=False
 shot(r,out/'calendar-confirmation-reachable.png')
 collapsed_navigate(r,'邮箱')
 checks['mail_sidebar_collapsed']=any(w.get('t')=='☰' for w in r.widgets())
 click_scroll_edge(r,'写新邮件','mail_list_body')
 for key,value in {'mail_to':'recipient@example.invalid','mail_subject':'合成长正文编辑，不发送'}.items():
  reachable(r,key,'mail_form_scroll');r.set_text(key,value)
 reachable(r,'mail_body','mail_form_scroll')
 body=''.join('合成邮件编辑正文第'+str(i)+'段：ORBIT资料仅用于本地UI验收，保留换行，不发送。\n' for i in range(8))
 type_multiline(r,'mail_body',body)
 checks['mail_long_body_readback']=r.find('mail_body').get('val')==body
 checks['mail_body_rect']=r.find('mail_body')['r']
 shot(r,out/'mail-long-body-edit.png')
 send=r.find('发送邮件')
 checks['mail_preview_control_reachable']=send['r'][2]>=2 and send['r'][3]>=24
 checks['mail_preview_control_rect']=send['r'];checks['mail_send_clicked']=False
 return checks
def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--size',default='1400x900');p.add_argument('--port',type=int,default=8484);p.add_argument('--keep',action='store_true');p.add_argument('--pages',nargs='+');p.add_argument('--long',action='store_true');p.add_argument('--forms',action='store_true');p.add_argument('--scene',type=Path);a=p.parse_args()
 a.out=a.out.resolve();a.source=a.source.resolve()
 if a.out.exists() and any(a.out.iterdir()): raise FileExistsError('Preserve evidence; choose a new output directory: '+str(a.out))
 with socket.socket() as probe:
  if probe.connect_ex(('127.0.0.1',a.port))==0: raise RuntimeError('Remote port already in use; leave that process untouched.')
 a.out.mkdir(parents=True,exist_ok=True);bundle=a.out/'bundle';state=a.out/'state'
 shutil.copytree(a.source.parent,bundle,dirs_exist_ok=True)
 manifest_path=bundle/'manifest.json'
 manifest=json.loads(manifest_path.read_text());manifest['integrity'].pop('signature',None)
 manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 source=a.source.read_text()
 scene=(a.scene or Path(__file__).with_name('visual_scene.splash')).read_text() if a.long else ''
 seeded='\nstart_timeout(1.0, || visual_seed())' if a.long else ''
 (bundle/'main.splash').write_text(source.replace('host.request(','visual_host(').replace('start_timeout(0.05, || boot())',TRANSPORT+scene+'\nstart_timeout(0.05, || boot())'+seeded))
 r=Remote(a.port)
 log=(a.out/'runtime.log').open('w');env=dict(os.environ,MAKEPAD_REMOTE=str(a.port));env.pop('MAKEPAD_HIDE_WINDOWS',None)
 proc=subprocess.Popen([str(HOST),'--bundle',str(bundle),'--app-data',str(state),'--allow-unsigned','--stamp','--size',a.size],env=env,cwd=HOST.parents[2],stdout=log,stderr=log)
 try:
  for _ in range(100):
   try:r.find('对话');break
   except (AssertionError,OSError):time.sleep(.1)
  else:raise RuntimeError((a.out/'runtime.log').read_text()[-4000:])
  time.sleep(1.5)
  input_check={}
  if a.long:
   typed='合成键盘输入第一行\n第二行保留，不发送。'
   try:
    type_multiline(r,'goal_input',typed)
    input_check={'typed_readback':r.find('goal_input').get('val')==typed,'rect':r.find('goal_input')['r']}
   except AssertionError as error: input_check={'error':str(error)}
  shot(r,a.out/'chat.png')
  (a.out/'chat.snap.json').write_text(json.dumps(r.widgets(),ensure_ascii=False,indent=2)+'\n')
  if a.long:
   x,y,w,h=r.find(body_area(r,'对话'))['r']
   for _ in range(3): r.scroll(int(x+w/2),int(y+h/2),300)
   shot(r,a.out/'chat-scrolled.png')
  pages=a.pages or ['长期目标','记忆','活动记录','邮箱','日历','能力授权','设置']
  captures=['chat']
  entry_checks={}
  for page in pages:

   navigate(r,page)
   time.sleep(.35);shot(r,a.out/(page+'.png'));captures.append(page)
   (a.out/(page+'.snap.json')).write_text(json.dumps(r.widgets(),ensure_ascii=False,indent=2)+'\n')
   if a.long:entry_checks[page]=first_screen(r,page)
   if a.long:
    area=body_area(r,page)
    try:
     x,y,w,h=r.find(area)['r']
     if w>2 and h>2:
      for _ in range(3): r.scroll(int(x+w/2),int(y+h/2),300)
      shot(r,a.out/(page+'-scrolled.png'))
    except AssertionError: pass
  interactions={}
  if a.long and any(w.get('i') == 'shortcuts' for w in r.widgets()):
   navigate(r,'对话')
   try:
    interactions['columns']=column_checks(r,a.out,a.size)
    r.click('‹');time.sleep(.2);shot(r,a.out/'chat-sidebar-collapsed.png')
    interactions['sidebar_collapsed']=any(w.get('t')=='☰' for w in r.widgets())
    r.click('卡');time.sleep(.2);shot(r,a.out/'result-fullwidth.png')
    interactions['result_fullwidth']=r.find('right_page')['r']
    if any(w.get('t')=='展开原邮件全文' for w in r.widgets()):
     interactions['long_mail']=long_mail_check(r,a.out)
    if a.forms:interactions['forms']=form_checks(r,a.out)
   except AssertionError as error:
    interactions['error']=str(error)
    shot(r,a.out/'interaction-error.png')
    (a.out/'interaction-error.snap.json').write_text(json.dumps(r.widgets(),ensure_ascii=False,indent=2)+'\n')
  # The old narrow sidebar may have scrolled past Chat; no need to return.
  calls_path=state/'muse-goals/visual-calls.json'
  calls=json.loads(calls_path.read_text()) if calls_path.exists() else []
  report={'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'size':a.size,'test_kind':'FIXTURE_VISIBLE_CARD_HOST','captures':captures,'external_actions':False,'png_pixels':list(struct.unpack('>II',(a.out/'chat.png').read_bytes()[16:24])),'long_scene':a.long,'host_calls':calls,'unexpected_side_effects':[c for c in calls if c in ['model.complete','mail.send','calendar.create','calendar.update','calendar.delete']],'interactions':interactions,'input_check':input_check,'page_entry_checks':entry_checks}
  (a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
  if a.keep:print('PID',proc.pid,flush=True);return
 finally:
  if not a.keep:
   try:r.request('/quit')
   except OSError:proc.terminate()
   proc.wait(timeout=10)
if __name__=='__main__':main()
