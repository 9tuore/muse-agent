#!/usr/bin/env python3
"""Real loopback TLS IMAP/SMTP and explicit model fixture; no SDK store writes."""
import argparse,base64,collections,email.policy,json,re,shlex,socketserver,ssl,subprocess,sys,threading,time
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from fixture_scope import scope,atomic_json,digest,ACCOUNTS,ACCOUNT_SUFFIX,TEST_INPUT
from planner import decision

class State:
    def __init__(self,root):
        self.root=root;self.lock=threading.RLock();self.receiver_lock=threading.Lock()
        self.case_id='initial';self.smtp_mode='accepted';self.model_mode='normal';self.model_response={'intent':'chat','reply':'SPRINT005 synthetic response'};self.delay_ms=0
        self.counts=collections.Counter();self.events=root/'protocol-events.jsonl'
        self.mailboxes=json.loads((root/'mailboxes.json').read_text()) if (root/'mailboxes.json').exists() else {a:{'INBOX':[],'Sent':[],'Archive':[]} for a in ACCOUNTS}
        self.stop=threading.Event()
        self.receiver_err=(root/'receiver-stderr.log').open('a')
        self.receiver=subprocess.Popen([sys.executable,str(Path(__file__).with_name('receiver.py')),'--root',str(root)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.receiver_err,text=True)
    def event(self,name,**data):
        with self.lock:
            self.counts[name]+=1
            row={'event':name,'case_id':self.case_id,'at_ns':time.time_ns(),**data}
            with self.events.open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    def box(self,account,folder):
        with self.lock:return list(self.mailboxes[account][folder])
    def add_raw(self,account,folder,raw):
        with self.lock:
            box=self.mailboxes[account][folder];uid=max([v['uid'] for v in box] or [0])+1
            box.append({'uid':uid,'raw':base64.b64encode(raw).decode(),'seen':False})
            atomic_json(self.root/'mailboxes.json',self.mailboxes)
            return uid
    def incoming(self,v):
        account=v['account']
        if account not in ACCOUNTS:raise ValueError('Unknown synthetic account')
        sender=v.get('sender','sender'+ACCOUNT_SUFFIX)
        if not sender.endswith(ACCOUNT_SUFFIX) or any('\r' in str(x) or '\n' in str(x) for x in (sender,v['subject'])):raise ValueError('Synthetic headers required')
        msg=EmailMessage(policy=email.policy.SMTP);msg['From']=sender;msg['To']=account;msg['Subject']=v['subject']
        msg['Date']=email.utils.formatdate(localtime=False);msg['Message-ID']=f'<SPRINT005-{time.time_ns()}@sprint005.example.invalid>'
        msg.set_content(v['body']);raw=msg.as_bytes();uid=self.add_raw(account,'INBOX',raw)
        self.event('fixture.incoming',account=account,uid=uid,raw_sha256=digest(raw))
        return {'uid':uid,'raw_sha256':digest(raw),'message_id':str(msg['Message-ID'])}
    def deliver(self,raw):
        self.event('smtp.data_received',bytes=len(raw),raw_sha256=digest(raw))
        with self.receiver_lock:
            self.receiver.stdin.write(json.dumps({'raw':base64.b64encode(raw).decode(),'case_id':self.case_id})+'\n');self.receiver.stdin.flush()
            line=self.receiver.stdout.readline()
            if not line:raise RuntimeError('Independent receiver exited')
            reply=json.loads(line)
            if not reply['is_ok']:raise RuntimeError('Independent receiver refused DATA')
            return reply['data']
    def received(self):
        p=self.root/'receiver/messages.jsonl'
        rows=[json.loads(line) for line in p.read_text().splitlines()] if p.exists() else []
        ids=collections.Counter(r['message_id'] for r in rows)
        return {'source':'independent_receiver_process_log','rows':rows,'count':len(rows),'duplicate_message_ids':{k:v for k,v in ids.items() if v>1}}

class TLSServer(socketserver.ThreadingTCPServer):
    allow_reuse_address=False;daemon_threads=True
    def get_request(self):
        sock,addr=super().get_request();sock.settimeout(25)
        try:return self.context.wrap_socket(sock,server_side=True),addr
        except Exception:
            sock.close();self.state.event('tls.handshake_refused');raise
    def handle_error(self,*args):self.state.event('protocol.handler_error')

class SMTP(socketserver.StreamRequestHandler):
    def send(self,text):self.wfile.write((text+'\r\n').encode());self.wfile.flush()
    def handle(self):
        s=self.server.state;self.send('220 SPRINT005 loopback fixture ESMTP');account=None;recipients=[]
        while True:
            raw=self.rfile.readline(16384)
            if not raw:return
            line=raw.decode('ascii','replace').strip();verb,_,arg=line.partition(' ');verb=verb.upper()
            if verb in ('EHLO','HELO'):self.send('250-SPRINT005\r\n250-AUTH PLAIN\r\n250 SIZE 2000000')
            elif verb=='AUTH':
                try:
                    mechanism,_,encoded=arg.partition(' ')
                    if mechanism.upper()!='PLAIN':raise ValueError()
                    if not encoded:self.send('334 ');encoded=self.rfile.readline(16384).decode().strip()
                    _,user,password=base64.b64decode(encoded,validate=True).decode().split('\0')
                    if user not in ACCOUNTS or password!=TEST_INPUT:raise ValueError()
                    account=user;s.event('smtp.auth',account=user);self.send('235 2.7.0 synthetic authentication accepted')
                except Exception:s.event('smtp.auth_refused');self.send('535 5.7.8 synthetic authentication refused')
            elif verb=='QUIT':self.send('221 bye');return
            elif not account:self.send('530 authenticate first')
            elif verb=='MAIL':
                match=re.match(r'FROM:\s*<([^<>]+)>',arg,re.I);sender=match.group(1) if match else ''
                if sender!=account:self.send('550 synthetic sender must match account')
                else:recipients=[];self.send('250 sender accepted')
            elif verb=='RCPT':
                match=re.match(r'TO:\s*<([^<>]+)>',arg,re.I);to=match.group(1) if match else ''
                if not to.endswith(ACCOUNT_SUFFIX):s.event('smtp.external_recipient_refused');self.send('550 synthetic recipient required')
                else:recipients.append(to);self.send('250 recipient accepted')
            elif verb=='DATA':
                if not recipients:self.send('503 no recipient');continue
                with s.lock:mode=s.smtp_mode
                if mode=='before':s.event('smtp.before_data_refused');self.send('550 SPRINT005 before DATA refusal');continue
                self.send('354 send synthetic message');chunks=[];size=0
                while True:
                    chunk=self.rfile.readline(2_000_001)
                    if not chunk:return
                    if chunk==b'.\r\n':break
                    chunk=chunk[1:] if chunk.startswith(b'..') else chunk
                    size+=len(chunk)
                    if size>2_000_000:self.send('552 oversized fixture');return
                    chunks.append(chunk)
                message=b''.join(chunks)
                try:s.deliver(message)
                except Exception:s.event('smtp.receiver_refused');self.send('451 receiver unavailable');continue
                s.add_raw(account,'Sent',message)
                for to in recipients:
                    if to in ACCOUNTS:s.add_raw(to,'INBOX',message)
                if mode=='unknown':s.event('smtp.unknown_disconnect_after_receiver');return
                s.event('smtp.accepted_response');self.send('250 2.0.0 synthetic DATA accepted')
            elif verb=='RSET':recipients=[];self.send('250 reset')
            elif verb=='NOOP':self.send('250 ok')
            else:self.send('502 unsupported synthetic command')

class IMAP(socketserver.StreamRequestHandler):
    def send(self,text):self.wfile.write((text+'\r\n').encode());self.wfile.flush()
    def handle(self):
        s=self.server.state;self.send('* OK SPRINT005 IMAP4rev1');account=None;folder='INBOX'
        while True:
            raw=self.rfile.readline(16384)
            if not raw:return
            parts=shlex.split(raw.decode().strip())
            if len(parts)<2:return
            tag,cmd=parts[0],parts[1].upper();args=parts[2:]
            if cmd=='CAPABILITY':self.send('* CAPABILITY IMAP4rev1 AUTH=PLAIN');self.send(tag+' OK capability');continue
            if cmd=='LOGIN':
                if len(args)==2 and args[0] in ACCOUNTS and args[1]==TEST_INPUT:
                    account=args[0];s.event('imap.login',account=account);self.send(tag+' OK synthetic login')
                else:s.event('imap.login_refused');self.send(tag+' NO synthetic sign-in refused')
                continue
            if cmd=='LOGOUT':self.send('* BYE logout');self.send(tag+' OK logout');return
            if not account:self.send(tag+' NO authenticate first');continue
            if cmd=='LIST':
                for name,flags in [('INBOX','\\Inbox'),('Sent','\\Sent'),('Archive','\\Archive')]:self.send(f'* LIST ({flags}) "/" "{name}"')
                self.send(tag+' OK list')
            elif cmd in ('SELECT','EXAMINE'):
                folder=args[0] if args else ''
                if folder not in ('INBOX','Sent','Archive'):self.send(tag+' NO folder absent');continue
                self.send('* FLAGS (\\Seen)');self.send(f'* {len(s.box(account,folder))} EXISTS');self.send('* OK [UIDVALIDITY 5005] stable synthetic UIDs');self.send(tag+' OK [READ-WRITE] selected')
            elif cmd=='UID' and args:
                sub=args[0].upper();box=s.box(account,folder)
                if sub=='SEARCH':
                    match=re.search(r'UID\s+(\d+):',raw.decode(),re.I);floor=int(match.group(1)) if match else 1
                    found=[m['uid'] for m in box if m['uid']>=floor]
                    if not found and box:found=[max(m['uid'] for m in box)]
                    self.send('* SEARCH'+''.join(' '+str(n) for n in found));self.send(tag+' OK search')
                elif sub=='FETCH':
                    ids={int(x) for x in args[1].split(',')};body='BODY.PEEK' in raw.decode().upper()
                    for seq,m in enumerate(box,1):
                        if m['uid'] not in ids:continue
                        data=base64.b64decode(m['raw']);flags='\\Seen' if m['seen'] else ''
                        if body:
                            if 'HEADER' in raw.decode().upper():data=data.split(b'\r\n\r\n',1)[0]+b'\r\n\r\n'
                            self.wfile.write(f'* {seq} FETCH (UID {m["uid"]} BODY[] {{{len(data)}}}\r\n'.encode()+data+b')\r\n');self.wfile.flush()
                        else:self.send(f'* {seq} FETCH (UID {m["uid"]} FLAGS ({flags}) RFC822.SIZE {len(data)})')
                    s.event('imap.fetch',account=account,folder=folder,body=body);self.send(tag+' OK fetch')
                elif sub=='STORE':
                    uid=int(args[1])
                    with s.lock:
                        for m in s.mailboxes[account][folder]:
                            if m['uid']==uid:m['seen']=True
                        atomic_json(s.root/'mailboxes.json',s.mailboxes)
                    s.event('imap.seen',account=account,uid=uid);self.send(tag+' OK store')
                else:self.send(tag+' BAD unsupported UID command')
            elif cmd=='NOOP':self.send(tag+' OK noop')
            else:self.send(tag+' BAD unsupported command')

class HTTP(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def reply(self,value,code=200):
        raw=json.dumps(value,ensure_ascii=False).encode();self.send_response(code);self.send_header('content-type','application/json');self.send_header('content-length',str(len(raw)));self.end_headers();self.wfile.write(raw)
    def model_reply(self,body,message,finish):
        if not body.get('stream'):
            self.reply({'id':'sprint005-fixture','object':'chat.completion','model':'sprint005-fixture','choices':[{'index':0,'message':message,'finish_reason':finish}],'usage':{'prompt_tokens':10,'completion_tokens':5}});return
        self.send_response(200);self.send_header('content-type','text/event-stream');self.end_headers()
        delta={'role':'assistant'}
        if message.get('tool_calls'):delta['tool_calls']=[{'index':0,**c} for c in message['tool_calls']]
        else:delta['content']=message['content']
        for change,reason in [(delta,None),({},finish)]:
            chunk={'id':'sprint005-fixture','object':'chat.completion.chunk','model':'sprint005-fixture','choices':[{'index':0,'delta':change,'finish_reason':reason}]}
            self.wfile.write(b'data: '+json.dumps(chunk,ensure_ascii=False).encode()+b'\n\n')
        self.wfile.write(b'data: [DONE]\n\n');self.wfile.flush()
    def do_GET(self):
        s=self.server.state
        if self.path=='/v1/models':self.reply({'data':[{'id':'sprint005-fixture','object':'model'}]})
        elif self.path=='/__fixture/status':
            with s.lock:self.reply({'source':'actual_loopback_protocol_counters','case_id':s.case_id,'smtp_mode':s.smtp_mode,'counts':dict(s.counts),'ready':s.ready})
        elif self.path=='/__fixture/receiver':self.reply(s.received())
        else:self.reply({'error':'unknown fixture path'},404)
    def do_POST(self):
        s=self.server.state
        try:
            n=int(self.headers.get('content-length','0'))
            if not 0<n<=1_000_000:raise ValueError('Bounded request required')
            raw=self.rfile.read(n);v=json.loads(raw)
            if self.path=='/v1/chat/completions':
                s.event('model.request',request_sha256=digest(raw),bytes=len(raw))
                with s.lock:mode=s.model_mode;response=s.model_response;delay=s.delay_ms
                if delay:time.sleep(delay/1000)
                if mode=='http_error':self.reply({'error':{'message':'SPRINT005 synthetic provider failure'}},503);return
                if mode=='malformed':
                    bad=b'{SPRINT005 malformed provider response';self.send_response(200);self.send_header('content-length',str(len(bad)));self.end_headers();self.wfile.write(bad);return
                selected=None
                if v.get('tools'):
                    try:selected=decision(v)
                    except Exception as e:selected={'text':'SPRINT005 fixture planner refused: '+str(e)}
                if selected and 'tool' in selected:
                    call={'id':'sprint005-call-'+str(time.time_ns()),'type':'function','function':{'name':selected['tool'],'arguments':json.dumps(selected['args'],ensure_ascii=False)}}
                    s.event('model.tool_selected',tool=selected['tool'],args_sha256=digest(json.dumps(selected['args'],sort_keys=True,separators=(',',':')).encode()))
                    self.model_reply(v,{'role':'assistant','content':None,'tool_calls':[call]},'tool_calls');return
                if selected:response=selected['text']
                # The SDK's native provider probe asks ping/max_tokens=1; do not consume app case reply.
                content='pong' if v.get('max_tokens')==1 else (response if isinstance(response,str) else json.dumps(response,ensure_ascii=False))
                self.model_reply(v,{'role':'assistant','content':content},'stop')
            elif self.path=='/__fixture/incoming':self.reply(s.incoming(v))
            elif self.path=='/__fixture/mode':
                if v['smtp_mode'] not in ('accepted','before','unknown'):raise ValueError('Invalid SMTP mode')
                with s.lock:s.case_id=str(v['case_id']);s.smtp_mode=v['smtp_mode']
                self.reply({'configured':True,'approval_granted':False})
            elif self.path=='/__fixture/model':
                mode=v.get('mode','normal');delay=v.get('delay_ms',0)
                if mode not in ('normal','http_error','malformed') or type(delay)!=int or not 0<=delay<=5000:raise ValueError('Invalid model fixture')
                with s.lock:s.case_id=str(v['case_id']);s.model_mode=mode;s.model_response=v['response'];s.delay_ms=delay
                self.reply({'configured':True,'model_is_fixture':True})
            elif self.path=='/__fixture/stop':self.reply({'stopping':True});s.stop.set()
            else:self.reply({'error':'unknown fixture path'},404)
        except Exception as e:self.reply({'error':type(e).__name__},400)

def run(root,imap_port=0,smtp_port=0,model_port=0):
    root=scope(root);s=State(root)
    context=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);context.minimum_version=ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(str(root/'public/server.pem'),str(root/'private/server.key'))
    imap=TLSServer(('127.0.0.1',imap_port),IMAP);smtp=TLSServer(('127.0.0.1',smtp_port),SMTP);http=ThreadingHTTPServer(('127.0.0.1',model_port),HTTP)
    for server in (imap,smtp,http):server.state=s
    imap.context=smtp.context=context
    s.ready={'fixture_root':str(root),'imap_host':'127.0.0.1','imap_port':imap.server_address[1],'smtp_host':'127.0.0.1','smtp_port':smtp.server_address[1],
             'model_base_url':f'http://127.0.0.1:{http.server_address[1]}/v1','control_url':f'http://127.0.0.1:{http.server_address[1]}','accounts':ACCOUNTS,'tls_ca_sha256':digest((root/'public/mail-fixture-ca.der').read_bytes()),'scope':'synthetic transports; SDK GUI NOT_TESTED'}
    atomic_json(root/'ready.json',s.ready);print(json.dumps(s.ready),flush=True)
    threads=[]
    for server in (imap,smtp,http):
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();threads.append(thread)
    try:s.stop.wait()
    except KeyboardInterrupt:pass
    finally:
        for server in (imap,smtp,http):server.shutdown();server.server_close()
        s.receiver.stdin.close();s.receiver.wait(timeout=10);s.receiver_err.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True)
    for name in ('imap','smtp','model'):p.add_argument('--'+name+'-port',type=int,default=0)
    a=p.parse_args();run(a.root,a.imap_port,a.smtp_port,a.model_port)
