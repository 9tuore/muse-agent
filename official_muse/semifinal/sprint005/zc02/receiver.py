#!/usr/bin/env python3
"""Independent DATA receiver process. Append every delivery, including duplicates."""
import argparse,base64,email.policy,json,sys,time
from email.parser import BytesParser
from fixture_scope import scope,digest,ACCOUNT_SUFFIX

def receive(root, value):
    raw=base64.b64decode(value['raw'],validate=True)
    if len(raw)>2_000_000: raise ValueError('Oversize synthetic message')
    msg=BytesParser(policy=email.policy.default).parsebytes(raw)
    to=email.utils.getaddresses(msg.get_all('to',[]))
    if not to or any(not a.endswith(ACCOUNT_SUFFIX) for _,a in to): raise ValueError('Synthetic recipients only')
    body=msg.get_body(preferencelist=('plain',)) if msg.is_multipart() else msg
    text=body.get_content() if body else ''
    log=root/'receiver/messages.jsonl';log.parent.mkdir(exist_ok=True)
    row={'source':'independent_receiver_process','at_ns':time.time_ns(),'case_id':value['case_id'],
         'message_id':str(msg.get('message-id','')),'to':[a for _,a in to],'subject':str(msg.get('subject','')),
         'body_sha256':digest(text.encode()),'raw_sha256':digest(raw),'bytes':len(raw)}
    if not row['message_id']: raise ValueError('Actual Message-ID required')
    with log.open('a') as f:f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush()
    return row

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();root=scope(a.root)
    for line in sys.stdin:
        try: out={'is_ok':True,'data':receive(root,json.loads(line))}
        except Exception as e:out={'is_ok':False,'error':type(e).__name__}
        print(json.dumps(out),flush=True)
