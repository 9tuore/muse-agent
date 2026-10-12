#!/usr/bin/env python3
"""Loopback fixture controls only. No SDK approval/state mutation endpoint."""
import argparse,json,urllib.request
from pathlib import Path
from urllib.parse import urlsplit
from fixture_scope import scope
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('action',choices=['status','receiver','incoming','model','mode','stop']);p.add_argument('--json',type=Path);a=p.parse_args()
    root=scope(a.root);base=json.loads((root/'ready.json').read_text())['control_url'];parsed=urlsplit(base)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1':raise SystemExit('Loopback fixture control only')
    if a.action in ('status','receiver'):data=None
    elif a.action=='stop':data=b'{}'
    else:
        if a.json is None:raise SystemExit('Explicit fixture JSON file required')
        data=json.dumps(json.loads(a.json.read_text())).encode()
    req=urllib.request.Request(base+'/__fixture/'+a.action,data=data,headers={'content-type':'application/json'})
    with urllib.request.urlopen(req,timeout=8) as r:print(r.read().decode())
