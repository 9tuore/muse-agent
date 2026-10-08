#!/usr/bin/env python3
"""Quit only the assigned quality remote port, independently verify release."""
import argparse,json,socket,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'official_muse/phase2/tests'));from remote import Remote
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert a.out.resolve().is_relative_to(Q)
r=Remote(8494);pid=json.loads(r.request('/s'))['pid'];start=time.monotonic();outcome='response'
try:r.request('/quit')
except Exception as e:outcome=type(e).__name__
while time.monotonic()-start<15:
 with socket.socket() as s:
  s.settimeout(.2);alive=s.connect_ex(('127.0.0.1',8494))==0
 if not alive:break
 time.sleep(.1)
a.out.write_text(json.dumps({'pid':pid,'port':8494,'port_closed':not alive,'quit_outcome':outcome,'seconds':time.monotonic()-start},indent=2)+'\n');assert not alive
