#!/usr/bin/env python3
"""Keep transitive production Memory functions byte-exact, omit unrelated UI/startup."""
import argparse,hashlib,json,re,sys
from pathlib import Path
P=Path(__file__).resolve().parent
ROOT=P.parents[4]
sys.path.insert(0,str(ROOT/'official_muse/prelim/tests/calendar_sync'))
from run import functions_in
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--probe',type=Path);a=p.parse_args()
out=a.out.resolve();out.relative_to(ROOT/'build');out.mkdir(parents=True,exist_ok=False)
source=a.source.read_text();funcs=functions_in(source)
probe=a.probe.read_text() if a.probe else (ROOT/'official_muse/ui_memory/tests/memory_suite.splash').read_text()
if not a.probe:
 probe=probe[:probe.index('start_timeout(0.1,')]
 marker='fs.write("memory-report.json",mr.to_json())';assert probe.count(marker)==1
 probe=probe.replace(marker,'let checks = {}\n    for key value in mr { if value.is_bool() { checks[key] = value } }\n    fs.write("probe.json",{checks: checks calls: [] observations: mr}.to_json())')
 probe+='\nfn probe_transport(method,args,cb){ cb({is_ok:false error:"Memory fixture forbids external transport"}) }\nstart_timeout(0.1,||memory_stage_one())\n'
else:probe+='\nfn probe_transport(method,args,cb){ cb({is_ok:false error:"Memory fixture forbids external transport"}) }\n'
# Break long synthetic stages into timer turns; production functions/budgets are untouched.
synthetic=functions_in(probe)
anchors={
 'memory_stage_one':['    let entries = gm_entries','    let result_M04_corrected','    let result_M05_forget','    let before = fs.read'],
 'memory_auth':['    let result_stop = gm_enable(false)'],
 'memory_stage_two':['    gm_set_focus("天文","老师")'],
 'memory_conflict':['    let mine = gm_entries'],
}
for name,marks in anchors.items():
 if name not in synthetic:continue
 original=synthetic[name];body=original[original.index('{')+1:-1]
 positions=[0]+[body.index(m) for m in marks]+[len(body)]
 stages=[]
 for i in range(len(positions)-1):
  block=body[positions[i]:positions[i+1]]
  if i and 'ctx' in block and 'let ctx' not in block:block='    let ctx = {}\n'+block
  if i<len(positions)-2:block+='\n    fs.write("memory-progress.json",mr.to_json())\n    start_timeout(0.15,||'+name+'_split_'+str(i+1)+'())\n'
  stages.append('fn '+(name if i==0 else name+'_split_'+str(i))+'(){\n'+block+'\n}')
 probe=probe.replace(original,'\n'.join(stages))

# Select actual functions transitively; no replacement of the Memory implementation.
selected=set(re.findall(r'\b([A-Za-z_][A-Za-z_0-9]*)\s*\(',probe))&set(funcs)
selected|={'redraw','mail_redraw','set_page'}
while True:
 new=set(selected)
 for n in selected:new|=set(re.findall(r'(?<!\.)\b([A-Za-z_][A-Za-z_0-9]*)\s*\(',funcs[n]))&set(funcs)
 # Renderer bodies are replaced by the existing runner, so exclude their UI dependencies.
 for n in ('redraw','mail_redraw','set_page'):new.discard(n)
 new|={'redraw','mail_redraw','set_page'}
 # Do not traverse renderer bodies on the next pass.
 deps=set()
 for n in selected-{'redraw','mail_redraw','set_page'}:deps|=set(re.findall(r'(?<!\.)\b([A-Za-z_][A-Za-z_0-9]*)\s*\(',funcs[n]))&set(funcs)
 new=selected|deps
 if new==selected:break
 selected=new
# Top-level let declarations, including multiline expressions; actual literal bytes retained.
globals={}
for m in re.finditer(r'^let ([A-Za-z_][A-Za-z_0-9]*)\s*=',source,re.M):
 pos=m.end();depth=0;quoted=False;escaped=False
 while pos<len(source):
  c=source[pos]
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c in '{[(':depth+=1
  elif c in '}])':depth-=1
  elif c=='\n' and depth==0:break
  pos+=1
 globals[m[1]]=source[m.start():pos]
text='\n'.join(funcs[n] for n in selected-{'redraw','mail_redraw','set_page'})+'\n'+probe
wanted=set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b',text))&set(globals)
while True:
 new=wanted|set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b','\n'.join(globals[n] for n in wanted)))&set(globals)
 if new==wanted:break
 wanted=new
ordered=sorted(selected,key=lambda n:source.index(funcs[n]));ordered_globals=sorted(wanted,key=lambda n:source.index(globals[n]))
subset='\n'.join(globals[n] for n in ordered_globals)+'\n'+'\n'.join(funcs[n] for n in ordered)+'\nstart_timeout(0.05, || boot())\n'
(out/'memory-source.splash').write_text(subset);(out/'memory-probe.splash').write_text(probe);(out/'frozen-main.splash').write_text(source)
sha=lambda s:hashlib.sha256(s.encode()).hexdigest()
report={'source_sha256':sha(source),'subset_sha256':sha(subset),'probe_sha256':sha(probe),'production_functions':{n:sha(funcs[n]) for n in ordered},'production_globals':{n:sha(globals[n]) for n in ordered_globals},'renderer_substitutions':['redraw','mail_redraw','set_page'],'memory_functions_unchanged':True,'full_main_ui_not_executed':True}
(out/'identity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if not a.probe:(P/'memory-identity.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'functions':len(selected),'globals':len(wanted),'subset_bytes':len(subset.encode()),'source_sha256':sha(source)}))
