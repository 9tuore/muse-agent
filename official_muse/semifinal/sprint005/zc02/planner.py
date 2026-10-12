"""Kernel tool choice fixture. Actual results only; no approval or receipt creation."""
import json
MARKERS=['精确 calendar.events 参数：','精确 calendar.add_event 参数：','2. calendar.update_event 精确参数：','2. calendar.remove_event 参数：']

def text_of(message):
    value=message.get('content')
    return ' '.join(v.get('text','') for v in value if isinstance(v,dict)) if isinstance(value,list) else (value or '')

def plan_from_prompt(text):
    found=[m for m in MARKERS if m in text]
    if not found:return None
    if len(found)!=1 or text.count(found[0])!=1:raise ValueError('Ambiguous native prompt')
    marker=found[0];args,_=json.JSONDecoder().raw_decode(text.split(marker,1)[1].lstrip())
    if not isinstance(args,dict):raise ValueError('Object arguments required')
    if marker==MARKERS[0]:
        if set(args)-{'from','to','limit'}:raise ValueError('Invalid events arguments')
        if 'limit' in args and (type(args['limit'])!=int or not 1<=args['limit']<=200):raise ValueError('Invalid events limit')
        return [('calendar.events',args)]
    if marker==MARKERS[1]:
        if set(args)!={'title','start','end','timezone','location','notes','request_id'}:raise ValueError('Invalid add arguments')
        return [('calendar.add_event',args),('calendar.get_event',{'id':{'$tool_result':0,'path':['id']}})]
    expected=args.get('expected');keys={'id','request_id','title','start','end','timezone','location','notes'}
    if not isinstance(expected,dict) or set(expected)!=keys or args.get('id')!=expected.get('id'):raise ValueError('Original expected/id required')
    tool='calendar.update_event' if marker==MARKERS[2] else 'calendar.remove_event'
    required={'id','expected','title','start','end','timezone','location','notes'} if marker==MARKERS[2] else {'id','expected'}
    if set(args)!=required:raise ValueError('Invalid mutation arguments')
    return [('calendar.get_event',{'id':args['id']}),(tool,args),('calendar.get_event',{'id':args['id']})]

def decision(body):
    messages=body.get('messages',[]);last=max((i for i,m in enumerate(messages) if m.get('role')=='user'),default=-1)
    if last<0:return None
    plan=plan_from_prompt(text_of(messages[last]))
    if plan is None:return None
    results=[]
    for row in messages[last+1:]:
        if row.get('role')=='tool':
            value=json.loads(text_of(row))
            if isinstance(value,dict) and value.get('ok') is False:raise ValueError('Actual tool error stops fixture plan')
            if isinstance(value,dict) and value.get('ok') is True and 'data' in value:value=value['data']
            results.append(value)
    if len(results)>=len(plan):return {'text':'SPRINT005 fixture tool plan complete; use actual Broker receipts.'}
    tool,args=plan[len(results)];name=tool.replace('.','_')
    offered=[t.get('function',{}).get('name') for t in body.get('tools',[]) or []]
    if name not in offered:raise ValueError('Actual Kernel did not offer the selected tool')
    if args.get('id',{}).__class__ is dict and '$tool_result' in args.get('id',{}):
        ref=args['id'];value=results[ref['$tool_result']]
        for key in ref['path']:value=value[key]
        args={'id':value}
    return {'tool':name,'args':args,'index':len(results)}
