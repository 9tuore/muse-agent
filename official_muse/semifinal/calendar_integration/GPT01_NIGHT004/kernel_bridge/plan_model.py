#!/usr/bin/env python3
"""Local explicit fixture plans, actual offered tools and actual tool messages.

Protocol framing follows the SDK mock_agent_llm.py; no keys or remote provider.
This fixture chooses tools; it does not replace the original Broker user prompt.
"""
import itertools,json,os,sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
SEQ=itertools.count(1)
PLAN=Path(os.environ['NIGHT004_PLAN_FILE'])
LOG=Path(os.environ['NIGHT004_MODEL_LOG'])
RESOLVED=Path(os.environ['NIGHT004_RESOLVED_LOG'])
ALLOWED={'calendar.events','calendar.get_event','calendar.add_event','calendar.update_event','calendar.remove_event'}
def text_of(message):
 content=message.get('content')
 return ' '.join(p.get('text','') for p in content if isinstance(p,dict)) if isinstance(content,list) else (content or '')
def result_value(message):
 value=json.loads(text_of(message))
 # ToolOutcome's explicit successful envelope, when the Kernel forwards it intact.
 if isinstance(value,dict) and value.get('ok') is False:raise ValueError('Previous actual tool result failed: '+json.dumps(value.get('error')))
 if isinstance(value,dict) and value.get('ok') is True and 'data' in value:return value['data']
 return value
def resolve(value,results):
 if isinstance(value,dict) and '$tool_result' in value:
  result=results[value['$tool_result']]
  for key in value.get('path',[]):result=result[key]
  return result
 if isinstance(value,dict):return {k:resolve(v,results) for k,v in value.items()}
 if isinstance(value,list):return [resolve(v,results) for v in value]
 return value
def decide(body):
 plan=json.loads(PLAN.read_text());messages=body.get('messages',[])
 last_user=max((i for i,m in enumerate(messages) if m.get('role')=='user'),default=-1)
 results=[result_value(m) for m in messages[last_user+1:] if m.get('role')=='tool']
 steps=plan['steps'];index=len(results)
 if index>=len(steps):return {'text':'FIXTURE PLAN COMPLETE '+json.dumps(results[-1] if results else None)}
 step=steps[index];tool=step['tool'];name=tool.replace('.','_')
 offered=[t.get('function',{}).get('name') for t in body.get('tools',[]) or []]
 if tool not in ALLOWED or name not in offered:raise ValueError(f'Fixture plan tool is not actually offered: {tool}; offered={offered}')
 args=resolve(step['args'],results)
 resolved={'plan_id':plan['plan_id'],'index':index,'tool':tool,'args':args,'fixture_model':True}
 with RESOLVED.open('a') as f:f.write(json.dumps(resolved)+'\n')
 return {'tool':name,'args':args}
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_POST(self):
  body=json.loads(self.rfile.read(int(self.headers.get('content-length','0'))) or b'{}')
  try:decision=decide(body)
  except Exception as e:decision={'text':'FIXTURE PLAN ERROR '+str(e)}
  with LOG.open('a') as f:f.write(json.dumps({'request':body,'decision':decision,'fixture_model':True})+'\n')
  if 'tool' in decision:
   call={'id':f'fixture_call_{next(SEQ)}','type':'function','function':{'name':decision['tool'],'arguments':json.dumps(decision['args'])}}
   message={'role':'assistant','content':None,'tool_calls':[call]};finish='tool_calls'
  else:message={'role':'assistant','content':decision['text']};finish='stop'
  if body.get('stream'):
   self.send_response(200);self.send_header('content-type','text/event-stream');self.end_headers()
   delta={'role':'assistant'}
   if 'tool' in decision:delta['tool_calls']=[{'index':0,**call}]
   else:delta['content']=decision['text']
   for chunk in [{'choices':[{'index':0,'delta':delta,'finish_reason':None}]},{'choices':[{'index':0,'delta':{},'finish_reason':finish}],'usage':{'prompt_tokens':10,'completion_tokens':5,'total_tokens':15}}]:
    chunk.update(id='fixture',object='chat.completion.chunk',model='mock-model')
    self.wfile.write(b'data: '+json.dumps(chunk).encode()+b'\n\n')
   self.wfile.write(b'data: [DONE]\n\n');self.wfile.flush();return
  data=json.dumps({'id':'fixture','object':'chat.completion','model':'mock-model','choices':[{'index':0,'message':message,'finish_reason':finish}],'usage':{'prompt_tokens':10,'completion_tokens':5,'total_tokens':15}}).encode()
  self.send_response(200);self.send_header('content-type','application/json');self.send_header('content-length',str(len(data)));self.end_headers();self.wfile.write(data)
if __name__=='__main__':
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);print(server.server_address[1],flush=True);server.serve_forever()
