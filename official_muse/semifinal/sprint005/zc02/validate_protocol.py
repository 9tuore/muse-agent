#!/usr/bin/env python3
"""Validate this new fixture only. Not SDK/GUI approval, baseline suites or SMTP live."""
import argparse,imaplib,json,smtplib,ssl,urllib.request
from email.message import EmailMessage
from pathlib import Path
from fixture_scope import scope,ACCOUNTS,TEST_INPUT,atomic_json

def validate(root):
    root=scope(root);ready=json.loads((root/'ready.json').read_text());base=ready['control_url'];checks={}
    def api(path,value=None):
        req=urllib.request.Request(base+path,data=json.dumps(value).encode() if value is not None else None,headers={'content-type':'application/json'})
        with urllib.request.urlopen(req,timeout=8) as r:return json.load(r)
    tls=ssl.create_default_context(cafile=str(root/'public/mail-fixture-ca.pem'))
    incoming=api('/__fixture/incoming',{'account':ACCOUNTS[0],'subject':'SPRINT005 合成来信','body':'SPRINT005 合成内容：2026-10-13 15:00会议。'})
    with imaplib.IMAP4_SSL('127.0.0.1',ready['imap_port'],ssl_context=tls) as imap:
        checks['verified_tls_imap_login']=imap.login(ACCOUNTS[0],TEST_INPUT)[0]=='OK'
        checks['actual_list_inbox_sent_archive']=len(imap.list()[1])==3
        checks['actual_select']=imap.select('INBOX')[0]=='OK'
        found=imap.uid('SEARCH',None,'UID','1:*')[1][0]
        checks['actual_stable_uid_search']=str(incoming['uid']).encode() in found.split()
        fetched=imap.uid('FETCH',str(incoming['uid']),'(BODY.PEEK[])')[1]
        checks['actual_imap_literal_contains_mime']=any(isinstance(x,tuple) and b'SPRINT005' in x[1] for x in fetched)
        checks['actual_seen_command']=imap.uid('STORE',str(incoming['uid']),'+FLAGS.SILENT','(\\Seen)')[0]=='OK'
    expected_deliveries=api('/__fixture/receiver')['count']
    for mode in ('accepted','before','unknown'):
        api('/__fixture/mode',{'case_id':'protocol-'+mode,'smtp_mode':mode})
        msg=EmailMessage();msg['From']=ACCOUNTS[0];msg['To']=ACCOUNTS[2];msg['Subject']='SPRINT005 '+mode;msg['Message-ID']='<protocol-'+mode+'@sprint005.example.invalid>';msg.set_content('SPRINT005 合成发送 '+mode)
        outcome='accepted'
        try:
            with smtplib.SMTP_SSL('127.0.0.1',ready['smtp_port'],context=tls,timeout=5) as smtp:
                smtp.login(ACCOUNTS[0],TEST_INPUT);smtp.send_message(msg)
        except smtplib.SMTPDataError:outcome='before'
        except smtplib.SMTPServerDisconnected:outcome='unknown'
        checks[mode+'_actual_wire_outcome']=outcome==mode
        actual=api('/__fixture/receiver')
        expected_deliveries+=int(mode!='before')
        checks[mode+'_independent_receiver_count']=actual['count']==expected_deliveries
    checks['receiver_does_not_hide_duplicates']=api('/__fixture/receiver')['duplicate_message_ids']=={}
    api('/__fixture/model',{'case_id':'model-contract','response':{'intent':'chat','reply':'SPRINT005 explicit fixture'}})
    checks['models_actual_endpoint']=api('/v1/models')['data'][0]['id']=='sprint005-fixture'
    out=api('/v1/chat/completions',{'model':'sprint005-fixture','messages':[{'role':'user','content':'SPRINT005'}]})
    checks['model_content_is_explicit_fixture']=json.loads(out['choices'][0]['message']['content'])['reply']=='SPRINT005 explicit fixture'
    checks['sdk_probe_ping_keeps_case_response']=api('/v1/chat/completions',{'max_tokens':1,'messages':[{'role':'user','content':'ping'}]})['choices'][0]['message']['content']=='pong'
    checks['no_external_socket_binding']=ready['imap_host']==ready['smtp_host']=='127.0.0.1'
    result={'kind':'NEW_SPRINT005_LOOPBACK_FIXTURE_PROTOCOL_TEST','status':'PASS' if all(checks.values()) else 'FAIL','checks':checks,'sdk_gui_status':'NOT_TESTED','approval_is_fixture':True,'live_smtp_sends':0}
    atomic_json(root/'protocol-validation.json',result)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args();r=validate(a.root)
    print(json.dumps({'status':r['status'],'checks':len(r['checks']),'failed':[k for k,v in r['checks'].items() if not v],'sdk_gui':'NOT_TESTED'}))
    raise SystemExit(0 if r['status']=='PASS' else 1)
