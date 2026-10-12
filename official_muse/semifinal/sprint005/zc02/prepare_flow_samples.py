#!/usr/bin/env python3
"""Explicit control responses, never preseed GUI state or call a service."""
import argparse,hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main(source_path,source_sha):
    source=Path(source_path).read_bytes();assert hashlib.sha256(source).hexdigest()==source_sha,'Explicit live source identity mismatch'
    out=HERE/'flows';out.mkdir(exist_ok=True);catalog=[]
    def sample(name,kind,response,round_=None,delay=0,mode='normal'):
        file=name+'.json';value={'case_id':'S005-'+name,'response':response,'mode':mode,'delay_ms':delay}
        (out/file).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
        catalog.append({'file':file,'kind':kind,'round':round_,'mode':mode,'delay_ms':delay})
    for r in (1,2,3):
        label=f'S005-R{r}';hour=14+r;start=f'2026-10-13T{hour:02}:00:00+08:00';end=f'2026-10-13T{hour:02}:30:00+08:00'
        sample(f'chat-r{r}','chat_reply',{'reply':f'{label} 合成回复。若要保存资料，请使用用户消息的“记住这条”；本回复不表示已保存或执行。'},r)
        sample(f'goal-plan-r{r}','chat_goal_plan',{'objective':f'{label}资料整理','source':f'{label}资料甲；{label}资料乙'},r)
        sample(f'goal-summary-r{r}','goal_summary',{'summary':f'{label}先核对资料，再按类别整理。'},r)
        sample(f'calendar-r{r}','chat_calendar',{'title':label+'合成会议','start':start,'end':end,'time_zone':'Asia/Shanghai','location':label+'合成会议室'},r)
        sample(f'chat-mail-r{r}','chat_mail_candidate',{'to':'receiver@sprint005.example.invalid','subject':label+'合成邮件','body':label+'合成资料已整理，请核对。'},r)
        sample(f'mail-accept-r{r}','mail_reply_editor',{'subject':label+'回复约定','body':'可以，就按来信提议安排。'},r)
        sample(f'mail-decline-r{r}','mail_reply_editor',{'subject':label+'回复邀请','body':'不好意思，这次不方便，先不约了。'},r)
        sample(f'mail-time-r{r}','mail_reply_editor',{'subject':label+'修改约定','body':'改成后天19点见，可以吗？'},r)
        policy={'search_start':start,'search_end':end,'time_zone':'Asia/Shanghai','reason':label+'仅按明确合成约定，无另选时间授权。','hard_windows':[{'start':start,'end':end}],'preferred_windows':[{'start':start,'end':end}]}
        sample(f'mail-calendar-policy-r{r}','mail_calendar_policy',{'title':label+'合成会议','start':start,'end':end,'time_zone':'Asia/Shanghai','location':label+'合成会议室','question':'','duration_changed':False,'duration_quote':'','policy':policy},r)
    sample('calendar-edit-16','chat_calendar',{'title':'S005-R1合成会议','start':'2026-10-13T16:00:00+08:00','end':'2026-10-13T16:30:00+08:00','time_zone':'Asia/Shanghai','location':'S005-R1合成会议室'})
    sample('calendar-ambiguous','chat_calendar',{'title':'S005合成会议','start':'','end':'','time_zone':'Asia/Shanghai','location':''})
    sample('chat-mail-edit','chat_mail_candidate',{'to':'receiver@sprint005.example.invalid','subject':'S005-R1合成邮件','body':'S005-R1补充了合成资料丙，请核对。'})
    sample('goal-plan-edit','chat_goal_plan',{'objective':'S005-R1资料整理','source':'S005-R1资料甲；S005-R1资料乙；S005-R1资料丙'})
    sample('late-chat','chat_reply',{'reply':'S005-LATE 原请求合成回复；应按原会话与scope绑定处理。'},delay=4500)
    sample('late-calendar','chat_calendar',{'title':'S005-LATE合成会议','start':'2026-10-13T15:00:00+08:00','end':'2026-10-13T15:30:00+08:00','time_zone':'Asia/Shanghai','location':'S005-LATE合成会议室'},delay=4500)
    sample('late-mail','mail_reply_editor',{'subject':'S005-LATE旧稿','body':'不好意思，这次不方便，先不约了。'},delay=4500)
    sample('late-goal-summary','goal_summary',{'summary':'S005-LATE 原目标整理建议。'},delay=4500)
    sample('provider-http-error','provider_negative',{},mode='http_error')
    sample('provider-wire-malformed','provider_negative',{},mode='malformed')
    sample('output-not-json','output_negative','SPRINT005 deliberately not JSON')
    sample('output-extra-field','output_negative',{'reply':'S005 valid reply field','unexpected':True})
    (out/'catalog.json').write_text(json.dumps({'main_sha256':source_sha,'fixtures':catalog,'schema_source_functions':{'chat_reply':'chat_model_config','chat_goal_plan':'chat_model_config','chat_calendar':'chat_model_config','chat_mail_candidate':'chat_model_config','goal_summary':'ask_model','mail_reply_editor':'mail_model_draft','mail_calendar_policy':'calendar_model_candidate'},'gui_kernel_executed':False},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'fixtures':len(catalog),'main_sha256':source_sha,'business_data_written':False}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--source-sha',required=True);a=p.parse_args();main(a.source,a.source_sha)
