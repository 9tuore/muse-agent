#!/usr/bin/env python3
"""Thin r4 evidence runner. Only genuine Makepad input and native screenshots."""
import sys,json,time
from pathlib import Path
from ua_driver import GUI,masked
HERE=Path(__file__).resolve().parent
round_id=int(sys.argv[1]); g=GUI(HERE/'handoff-r5.json','UA-BASE-05',round_id,1)
for a in json.loads(sys.argv[2]):
 kind=a[0]
 if kind=='click': print(g.click(a[1],None))
 elif kind=='type': print(g.type_text(a[1],a[2],None))
 elif kind=='scrollxy':
  g.log('scroll',x=a[1],y=a[2],dy=a[3]); g.request('/m',k='scroll',x=a[1],y=a[2],dy=a[3],precise=1)
 elif kind=='xy':
  g.log('click_sent_once',x=a[1],y=a[2],why=a[3]); g.request('/click',x=a[1],y=a[2])
 elif kind=='shot': print(g.capture(a[1]))
 elif kind=='wait': time.sleep(a[1])
 elif kind=='observe':
  rows=[{'i':w.get('i'),'ty':w.get('ty'),'r':w.get('r'),'t':masked(w.get('t','')) if w.get('ty')!='TextInput' else '[input]'} for w in g.widgets() if w.get('ty') in ['Button','Label','TextInput'] and w.get('r',[0,0,0,0])[2]>2 and w.get('r',[0,0,0,0])[3]>2]
  p=g.path/('filtered-'+str(time.time_ns())+'.json'); p.write_text(json.dumps(rows,ensure_ascii=False,indent=2)); g.log('observe',file=p.name);print(json.dumps(rows,ensure_ascii=False))
 elif kind=='readback':
  # Read only isolated Muse storage; no external commands or credentials.
  import sqlite3
  db=Path(g.cfg['data_root'])/'storage.sqlite'
  if not db.exists():
   print('STORAGE_PATH_NOT_FOUND');continue
 elif kind=='quit': g.log('normal_remote_quit');g.request('/quit')
