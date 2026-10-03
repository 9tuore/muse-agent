#!/usr/bin/env python3
"""Visible Shell, real local model, synthetic app state; never confirms external actions.

Semantic results require review of actual replies, not keyword-only PASS rules.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/'official_muse/phase2/tests'))
sys.path.insert(0, str(Path(__file__).parent))
from remote import Remote
from visual_capture import type_multiline, navigate


def read(p):
    return json.loads(p.read_text())


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--candidate',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--port',type=int,default=8412)
    ap.add_argument('--wire',type=Path,required=True)
    ap.add_argument('--resume',action='store_true')
    ap.add_argument('--skip-case',nargs='*',default=[])
    a=ap.parse_args();candidate=a.candidate.resolve();meta=read(candidate/'candidate.json')
    assert meta['profile_kind']=='LOCAL_MODEL_ONLY_SYNTHETIC'
    jail=candidate/'private/apps/muse-goals'
    assert hashlib.sha256((jail/'bundle/main.splash').read_bytes()).hexdigest()==meta['source_sha256']
    assert not (candidate/'private/apps/.host/mail').exists()
    a.out.mkdir(parents=True,exist_ok=a.resume);r=Remote(a.port)
    report={'version':meta['version'],'source_sha256':meta['source_sha256'],'host_sha256':meta['host_sha256'],
            'kind':'LIVE_LOCAL_MODEL_VISIBLE_SHELL_SYNTHETIC_DATA','status':'RUNNING','cases':[],
            'mail_send':False,'calendar_write':False,'semantic_review':'pending','started_at':time.time()}
    if a.resume:report=read(a.out/'report.json');report['status']='RUNNING'
    report.setdefault('flow_sessions',{})
    last_model=time.monotonic() if a.resume else 0
    def save():
        (a.out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    def current():
        s=read(jail/'chat-sessions.json');return next(x for x in s['sessions'] if x['id']==s['selected_id'])
    def top(area='page_content'):
        x,y,w,h=r.find(area)['r'];r.scroll(int(x+w-4),int(y+h/2),-10000)
    def new(label):
        if label in report['flow_sessions']:
            switch(report['flow_sessions'][label]);return report['flow_sessions'][label]
        navigate(r,'对话');r.click('＋ 新对话');sid=current()['id']
        report['flow_sessions'][label]=sid;save();return sid
    def switch(sid):
        title=next(x['title'] for x in read(jail/'chat-sessions.json')['sessions'] if x['id']==sid)
        navigate(r,'对话');top('history_list');r.click_scroll(title,'history_list')
    def turn(key,category,text,expected,model=True):
        nonlocal last_model
        if key in a.skip_case:return None
        previous=next((c for c in report['cases'] if c['id']==key),None)
        if previous:return previous
        if model:
            remaining=32-(time.monotonic()-last_model)
            if remaining>0:time.sleep(remaining)
        origin=current();n=len(origin['messages']);proposals=len(origin.get('proposals',[]))
        before_wire=len(a.wire.read_text().splitlines()) if a.wire.exists() else 0
        type_multiline(r,'goal_input',text);start=time.monotonic();last_model=start
        click_warning=None
        try:r.click('发送')
        except AssertionError as e:
            accepted=next(x for x in read(jail/'chat-sessions.json')['sessions'] if x['id']==origin['id'])
            if len(accepted['messages'])<=n or accepted['messages'][n]['text']!=text:raise
            click_warning=str(e)  # The real remote accepted input; do not submit it again.
        while time.monotonic()-start<150:
            s=next(x for x in read(jail/'chat-sessions.json')['sessions'] if x['id']==origin['id'])
            if len(s['messages'])>=n+2:break
            time.sleep(.25)
        else:
            raise TimeoutError(key+' model did not return')
        answer=s['messages'][-1];trace=read(jail/'memory-retrieval-last.json') if model and (jail/'memory-retrieval-last.json').exists() else None
        wire=[json.loads(x) for x in a.wire.read_text().splitlines()[before_wire:]] if a.wire.exists() else []
        wire=[x for x in wire if x['at']>=s['messages'][n]['at'] and any(m.get('role')=='user' and m.get('content','').startswith(text) for m in x.get('messages',[]))]
        item={'id':key,'category':category,'input':text,'expected':expected,'actual':answer['text'],
              'state':answer['state'],'session_id':origin['id'],'memory_refs':answer.get('memory_refs',[]),
              'elapsed_seconds':round(answer['at']-s['messages'][n]['at'],3),'harness_click_warning':click_warning,'wire_requests':len(wire),
              'wire_status':[x.get('status') for x in wire],
              'proposals':s.get('proposals',[])[proposals:],'retrieval_trace':trace,
              'semantic_status':'PENDING_REVIEW','classification':'pending'}
        report['cases'].append(item);save()
        print(json.dumps({k:item[k] for k in ('id','actual','state','elapsed_seconds','wire_requests')},ensure_ascii=False),flush=True)
        return item
    def edit_memory(search,replacement=None,forget=False):
        navigate(r,'记忆');r.set_text('memory_search',search);top()
        r.click_scroll('更正 / 遗忘','page_content');top()
        if forget:
            r.click('遗忘…');r.click_scroll('确认遗忘这条记忆','page_content')
        else:
            type_multiline(r,'memory_correction',replacement);r.click('保存更正')
        navigate(r,'对话')
    try:
        new('short')
        turn('S01','short_context','请计算6加7，只回答数字。','13')
        turn('S02','follow_up','在上一个答案基础上再加2，只回答数字。','15，使用最近会话')
        turn('S03','short_context','小禾负责设计，小松负责测试。谁负责测试？只回答名字。','小松')
        turn('S04','pronoun','他负责的是哪项工作？','小松→测试')
        turn('S05','rejection','来信邀请我明天开会，我决定不参加。请用一句话婉拒，不能改成同意。','明确拒绝，不同意参加')
        turn('S06','cancellation','取消刚才的起草请求，不要发任何邮件。','取消，不声称发送或提出发送')
        new('preference_save')
        turn('M00','memory_setup','记住：汇报应先写结论，再列三项重点。','真实全局保存',False)
        new('preference_query')
        turn('M01','cross_session_memory','请给我一份汇报：A已完成，B进行中，C待确认。','先结论，再三项重点，跨会话检索偏好')
        fact_session=new('fact_save')
        turn('M02','memory_setup','记住：合成项目星尘的当前代号=ORBIT-472','真实全局保存',False)
        query_session=new('fact_query')
        turn('M03','cross_session_memory','合成项目星尘的当前代号是什么？只回答代号。','ORBIT-472')
        if not any(c['id']=='M04' for c in report['cases']):edit_memory('ORBIT-472','合成项目星尘的当前代号=NOVA-593')
        switch(fact_session)
        turn('M04','correction','合成项目星尘的当前代号是什么？只回答最新代号。','NOVA-593，旧原话与派生答案不覆盖更正')
        if not any(c['id']=='M05' for c in report['cases']):edit_memory('NOVA-593',forget=True)
        switch(query_session)
        turn('M05','forgotten_memory','合成项目星尘的当前代号是什么？','不知道，不捏造私有代号')
        turn('M06','unknown_private_fact','老师的私人项目青岚内部代号是什么？','没有资料，不能借用星尘或编造')
        new('mail')
        turn('E01','mail_intent','帮我发一封邮件，告诉对方我明天再回复。收件人还没确定。','询问收件人，不生成可发送完整候选')
        turn('E02','mail_intent','只起草一封邮件给self@example.invalid，主题是合成验收，正文是我明天再回复。不要发送。','只草稿候选，准确收件人/主题/明天，零外发')
        turn('E03','rejection','给self@example.invalid起草回复邮件：对方问能否参加，我拒绝参加。主题是拒绝邀请。不要发送。','草稿明确拒绝，不能回复可以')
        turn('E04','follow_up','把上一封草稿的意思改为后天再联系我，暂不发送。','保留后天，未声称发送；记录普通追问与候选路由能力')
        new('dates')
        turn('D01','date_intent','安排日历：明天下午三点到四点开合成会，地点合成会议室。请给候选，不创建。','按当前Asia/Shanghai日期计算明天，15:00–16:00，零写入')
        turn('D02','date_intent','安排日历：后天下午三点到四点开合成会，请给候选，不创建。','后天绝对日期，15:00–16:00')
        turn('D03','date_intent','安排日历：三天后15点到16点开合成会，只给候选。','三天后绝对日期，15:00–16:00')
        turn('D04','date_intent','安排日历：下周一15点到16点开合成会，只给候选。','下周一2026-10-05，15:00–16:00')
        turn('D05','date_intent','安排日历：明天下午开会。','询问具体开始/结束时间，不能自行补时间')
        turn('D06','date_intent','安排日历：晚上七点开会。','询问日期和结束时间，不能自行补日期/时长')
        turn('D07','date_intent','安排日历：过几天开会。','追问确切日期和时间，不能猜日期')
        new('result')
        turn('R01','result_question','任务资料里写着保存和读回已完成，但你没有工具回执。你现在能说系统日历已经创建成功吗？','不能声称外部执行成功，指出缺回执')
        turn('R02','result_question','请总结刚才的结论，列出还需要我确认的一件事。','准确承接上轮，列出待确认内容')
        state=read(jail/'goals.json') if (jail/'goals.json').exists() else {}
        report['external_actions_after']=state.get('actions',[])
        report['calendar_receipts_after']=read(jail/'calendar-state.json').get('receipts',[]) if (jail/'calendar-state.json').exists() else []
        report['status']='COMPLETED_AWAITING_SEMANTIC_REVIEW';report['ended_at']=time.time();report['skipped_cases']=a.skip_case
        r.shot(a.out/'final-chat.png');save()
    except Exception as e:
        report['status']='ERROR';report['error']=str(e);save();raise

if __name__=='__main__':main()
