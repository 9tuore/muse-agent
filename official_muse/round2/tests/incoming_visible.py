#!/usr/bin/env python3
"""Visible production UI with synthetic incoming Host responses, never real mail."""
import json,os,shutil,subprocess,sys,time,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'phase2/tests'))
from remote import Remote
from runtime_probe import HOST,replace_function
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'official_muse/app/build/incoming018/visible'
TRANSPORT='''
let incoming_ui_sync = 0
let incoming_ui_sent = 0
let incoming_ui_models = 0
fn incoming_ui_host(service,args,callback){
    if service == "mail.accounts" { callback({is_ok: true data: [{id: "fixture-account" address: "self@example.invalid"}]}) return }
    if service == "mail.sync" { incoming_ui_sync = incoming_ui_sync + 1 callback({is_ok: true data: {new: 1 total: 2}}) return }
    if service == "mail.list" {
        let items = [{id: "old" sender: "历史合成发件人" subject: "历史邮件" time: 1790940000}]
        if incoming_ui_sync >= 2 { items.push({id: "new-1" sender: "张小明（合成测试）" subject: "周五讨论项目时间" time: 1790940000}) }
        if incoming_ui_sync >= 5 { items.push({id: "new-2" sender: "李小雨（合成测试）" subject: "周五会议邀请" time: 1790940000}) }
        callback({is_ok: true data: {messages: items total: items.len()}}) return
    }
    if service == "mail.message" { callback({is_ok: true data: {id: args.message address: "sender@example.invalid" sender: "合成发件人" subject: "周五会议邀请" body: "请问周五下午是否有空？"}}) return }
    if service == "model.complete" { incoming_ui_models = incoming_ui_models + 1 fs.write("synthetic-model-count.json",incoming_ui_models.to_json()) callback({is_ok: true data: {output: {subject: "回复：周五会议邀请" body: "感谢邀请，周五下午有空。"}}}) return }
    if service == "mail.send" { incoming_ui_sent = incoming_ui_sent + 1 fs.write("synthetic-send-count.json",incoming_ui_sent.to_json()) callback({is_ok: true data: {accepted: true}}) return }
    callback({is_ok: false error: "合成 UI 环境不提供此服务。"})
}
'''
def reach(r,key,area):
    a=r.find(area)['r'];r.scroll(int(a[0]+a[2]*.75),int(a[1]+a[3]/2),-100000)
    for _ in range(60):
        try:
            w=r.find(key);x,y,width,height=w['r']
            if width>=2 and height>=28 and y>=a[1]+5 and y+height<=a[1]+a[3]-15:return
        except AssertionError:pass
        r.scroll(int(a[0]+a[2]*.75),int(a[1]+a[3]/2),70)
    raise AssertionError('unreachable '+key)
def run(size,port):
    work=OUT/size;work.mkdir(parents=True,exist_ok=True)
    if (work/'state').exists():raise RuntimeError('fresh fixture output directory required')
    shutil.copytree(ROOT/'official_muse/app/bundle',work/'bundle',dirs_exist_ok=True)
    source=(ROOT/'official_muse/app/bundle/main.splash').read_text()
    adapted=source.replace('host.request(','incoming_ui_host(')
    adapted=replace_function(adapted,'mail_watch_schedule','fn mail_watch_schedule(){ start_timeout(2.0,|| { mail_watch_schedule() mail_watch_poll() }) }')
    adapted=adapted.replace('start_timeout(0.05, || boot())',TRANSPORT+'\nstart_timeout(0.05, || boot())',1)
    (work/'bundle/main.splash').write_text(adapted)
    jail=work/'state/muse-goals';jail.mkdir(parents=True,exist_ok=True)
    initial={'account':'','to':'','subject':'','body':'','status':'DRAFT','preview':'','attempt':'','request_id':'','accepted_at':0,'verified_at':0,'verified_id':'','link_goal_id':'','link_event_id':'','link_run_id':'','incoming_key':''}
    initial.update({'incoming_key':'','status':'DRAFT','account':'fixture-account','to':'old@example.invalid','subject':'另一封未发送草稿','body':'保留这封旧草稿。','attempt':'','request_id':''})
    (jail/'mail-draft.json').write_text(json.dumps(initial,ensure_ascii=False))
    r=Remote(port)
    with (work/'runtime.log').open('w') as log:
        proc=subprocess.Popen([str(HOST),'--bundle',str(work/'bundle'),'--app-data',str(work/'state'),'--allow-unsigned','--stamp','--size',size],cwd=HOST.parents[2],env=dict(os.environ,MAKEPAD_REMOTE=str(port)),stdout=log,stderr=log)
        try:
            for _ in range(100):
                try:
                    state=json.loads((jail/'mail-watch.json').read_text())
                    if state['alerts']:break
                except (OSError,ValueError):pass
                time.sleep(.1)
            else:raise RuntimeError('incoming card not created; inspect runtime.log')
            assert state['alerts'][0]['message_id']=='new-1'
            if size.startswith('412'):
                r.click('来信提醒 · 1');pane='right_page_content';field='mail_reply_intent_page'
            else:pane='right_content';field='mail_reply_intent'
            reach(r,'回复这封邮件',pane);assert r.find('请问周五下午是否有空？');r.shot(work/'incoming-card.png')
            reach(r,'不予回复',pane);r.click('不予回复')
            assert json.loads((jail/'mail-watch.json').read_text())['alerts'][0]['status']=='dismissed'
            for _ in range(100):
                state=json.loads((jail/'mail-watch.json').read_text())
                if len(state['alerts'])==2:break
                time.sleep(.1)
            else:raise RuntimeError('second incoming card absent')
            reach(r,'回复这封邮件',pane);r.click('回复这封邮件')
            reach(r,field,pane);r.set_text(field,'感谢邀请，说明周五下午有空。');r.shot(work/'reply-intent.png')
            reach(r,'按我的意思起草回复',pane);r.click('按我的意思起草回复')
            for _ in range(80):
                draft=json.loads((jail/'mail-draft.json').read_text())
                if draft['body']=='感谢邀请，周五下午有空。':break
                time.sleep(.1)
            else:raise RuntimeError('draft absent')
            assert draft['to']=='sender@example.invalid'
            assert not (jail/'synthetic-send-count.json').exists()
            assert not any(w.get('t')=='新邮件草稿' for w in r.widgets())
            if not size.startswith('412'):assert r.find('page_title').get('t')=='对话'
            body_field='mail_reply_body_page' if size.startswith('412') else 'mail_reply_body'
            reach(r,'重新起草',pane);r.click('重新起草');time.sleep(.2)
            reach(r,field,pane);r.set_text(field,'不好意思，周五不方便。')
            count_before=json.loads((jail/'synthetic-model-count.json').read_text())
            reach(r,'自己写回复（不调用 AI）',pane);r.click('自己写回复（不调用 AI）');time.sleep(.2)
            assert json.loads((jail/'synthetic-model-count.json').read_text())==count_before
            assert json.loads((jail/'mail-draft.json').read_text())['body']=='不好意思，周五不方便。'
            reach(r,body_field,pane);r.set_text(body_field,'不好意思，周五不方便，感谢邀请。')
            reach(r,'确认发送',pane);r.shot(work/'exact-send-confirmation.png')
            assert not (jail/'synthetic-send-count.json').exists()
            r.click('确认发送');time.sleep(.2)
            assert json.loads((jail/'synthetic-send-count.json').read_text())==1
            assert json.loads((jail/'mail-draft.json').read_text())['status']=='accepted'
            report={'size':size,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'test_kind':'FIXTURE','visible_card':True,'declined_without_send':True,'asked_intent':True,'draft_sender_bound':True,'stays_in_chat':True,'inline_regenerate':True,'inline_edit':True,'source_body_visible':True,'manual_skips_model':True,'manual_literal_body':True,'single_send_confirmation':True,'no_send_before_confirmation':True,'confirmed_synthetic_send_count':1,'external_send':False}
            (work/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
            return report
        finally:
            try:r.request('/quit')
            except OSError:proc.terminate()
            proc.wait(timeout=10)
OUT.mkdir(parents=True,exist_ok=True)
sizes=[sys.argv[2]] if len(sys.argv)>2 else ['990x539','412x892']
results=[run(size,8479) for size in sizes]
(OUT/'report.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))
