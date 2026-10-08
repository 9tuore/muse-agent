#!/usr/bin/env python3
"""Compare exact restore function bodies and named-call closure across freeze."""
from pathlib import Path
import re,json,hashlib,difflib
ROOT=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
old=ROOT/'build/7h-storage-shape-r1/compact/main.splash';new=ROOT/'build/7h-focus-r2/compact/main.splash'
a,b=old.read_text(),new.read_text()
def funcs(text):
 out={}
 for m in re.finditer(r'(?m)^fn\s+(\w+)\s*\(',text):
  pos=text.find('{',m.end());depth=0;quote=None;escape=False;comment=False;i=pos
  while i<len(text):
   c=text[i]
   if comment:
    if c=='\n':comment=False
   elif quote:
    if escape:escape=False
    elif c=='\\':escape=True
    elif c==quote:quote=None
   elif text[i:i+2]=='//':comment=True;i+=1
   elif c in ['"',"'"]:quote=c
   elif c=='{':depth+=1
   elif c=='}':
    depth-=1
    if depth==0:out[m.group(1)]=text[m.start():i+1];break
   i+=1
 return out
fa,fb=funcs(a),funcs(b);changed={n for n in set(fa)|set(fb) if fa.get(n)!=fb.get(n)}
roots=['core_goals_valid','core_restore_goals','chat_restore','chat_state_valid','chat_entry_valid','chat_session_valid','core_restore_memory','gm_validate','gm_validate_part','mail_watch_state_valid','calendar_state_valid','calendar_restore'];todo=roots[:];closure=set()
while todo:
 n=todo.pop()
 if n in closure:continue
 closure.add(n)
 for body in [fa.get(n,''),fb.get(n,'')]:todo.extend(x for x in re.findall(r'\b(\w+)\s*\(',body) if x in fa or x in fb)
v={'old_source_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'final_source_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'changed_functions':sorted(changed),'restore_roots':roots,'transitive_functions_compared':sorted(closure),'changed_in_restore_closure':sorted(closure&changed),'scope':'Eight actual old-Host storage scenarios reused only for unchanged restore logic, not represented as new Host reruns. Final UI/live cold matrix separate.'}
(Q/'storage-reuse-rc16.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
(Q/'frozen-rc16-source.diff').write_text(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='cceeaa009',tofile='cef7d576')))
print(json.dumps({'final_sha':v['final_source_sha256'],'changed_functions':v['changed_functions'],'changed_in_restore_closure':v['changed_in_restore_closure']}))
