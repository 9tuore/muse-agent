#!/usr/bin/env python3
"""Relay only the isolated Round2 synthetic Shell to the existing keyless local model."""
import argparse
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
import time
from urllib.request import Request,urlopen
from urllib.error import HTTPError

p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--port',type=int,default=8083)
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
class Relay(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def do_POST(self):
        data=self.rfile.read(int(self.headers['Content-Length']));body=json.loads(data)
        record={'at':time.time(),'messages':body.get('messages',[]),'model':body.get('model')}
        try:
            r=urlopen(Request('http://127.0.0.1:8080'+self.path,data=data,headers={'Content-Type':'application/json'}),timeout=125)
            status,answer=r.status,r.read()
        except HTTPError as e:status,answer=e.code,e.read()
        except Exception as e:status,answer=502,json.dumps({'error':'local model unavailable'}).encode()
        record['status']=status
        try:record['response']=json.loads(answer)
        except ValueError:record['response']='non-json response'
        with (a.output/'wire.jsonl').open('a') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
        self.send_response(status);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(answer)
print('Round2 synthetic model relay listening',flush=True)
ThreadingHTTPServer(('127.0.0.1',a.port),Relay).serve_forever()
