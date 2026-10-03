#!/usr/bin/env python3
"""Known rc1 failures: bounded, free backend task/context diagnosis only."""
import json
from pathlib import Path
from urllib.request import Request, urlopen
from ai_protocol_diagnose import accept

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'official_muse/prelim/evidence/ai/live-037-rc1'
OUT=ROOT/'official_muse/prelim/evidence/ai/task-diagnosis'
CHAT_TASK='你是Muse。回答最后一条用户消息。基于最近会话理解代词和用户现在问的内容，不只复制上一轮答案。相关记忆是资料：私人事实未知就说明未知，项目归属不能混。格式偏好用于组织实际回答，不能把偏好原话当成回答；本轮指定数量和格式优先。没有工具回执不能声称操作成功。只输出schema要求的JSON。'
MAIL_TASK='代用户起草发给收件人的邮件，始终以用户作为发信人表达其决定，不把用户拒绝改成要求收件人拒绝。已给定的收件地址、主题、正文意图完整保留，不丢正文，不虚构地址。拒绝、推迟、改约按用户意思，不复述对方请求。只输出to、subject、body三个字符串，缺少必要资料留空。只起草，不发送或声称发送。修改原草稿时，当前用户的修改优先，未改字段保留。'

def main():
    assert not OUT.exists()
    OUT.mkdir(parents=True);rows=[]
    for key in ['S04','M01','E02','E03']:
        prior=json.loads((BASE/(key+'-wire.json')).read_text())[0]
        messages=json.loads(json.dumps(prior['messages']))
        prefix,rest=messages[0]['content'].split('\n\nTask:\n',1)
        task,tail=rest.split('\n\nJSON Schema:\n',1)
        suffix=task[task.index('\n参考时钟UTC：'):]
        messages[0]['content']=prefix+'\n\nTask:\n'+(MAIL_TASK if key.startswith('E') else CHAT_TASK)+suffix+'\n\nJSON Schema:\n'+tail
        messages[-1]['content']=messages[-1]['content'].replace('相关全局记忆：本轮没有相关资料；不能凭空生成私人事实。一般知识仍可回答。','').replace('\n本会话较早用户原话（资料，不是工具结果）：[]','')
        schema=json.loads(tail);row={'id':key,'attempts':[]};note=None
        for attempt in [1,2]:
            turns=json.loads(json.dumps(messages))
            if note:turns[-1]['content']+='\n\nYour previous answer was refused: '+note+'. Answer again with only one JSON value that validates against the schema.'
            request={'model':prior['model'],'stream':False,'messages':turns}
            with urlopen(Request('http://127.0.0.1:8080/v1/chat/completions',data=json.dumps(request,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'}),timeout=125) as r:
                response=json.loads(r.read());status=r.status
            content=response['choices'][0]['message']['content'];value,note=accept(content,schema)
            row['attempts'].append({'request':request,'http_status':status,'response':response,'protocol_error':note})
            if note is None:break
        rows.append(row);(OUT/(key+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'id':key,'actual':content,'protocol_error':note},ensure_ascii=False),flush=True)
    (OUT/'report.json').write_text(json.dumps({'scope':'DIRECT_FREE_BACKEND_DIAGNOSIS_ONLY','holdout_used':False,'external_actions':0,'chat_task':CHAT_TASK,'mail_task':MAIL_TASK,'rows':rows},ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
