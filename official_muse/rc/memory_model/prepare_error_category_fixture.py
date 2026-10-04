#!/usr/bin/env python3
"""Extract verified suggested functions into existing Card fixture, no product edit."""
from pathlib import Path
import argparse,hashlib,json,shutil
OWN=Path(__file__).resolve().parent;ROOT=OWN.parents[2]
EXPECTED='977c00ec5fe6e7191946af84a68a62023e14e3a5f14e603cfff398f8efe6d25a'
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args()
src=ROOT/a.source;source=src.read_text();sha=lambda b:hashlib.sha256(b).hexdigest()
if sha(src.read_bytes())!=EXPECTED:raise SystemExit('Suggested source changed; no fixture prepared')
def extract(text,name):
 start=text.index('fn '+name+'(');brace=text.index('{',start);depth=1;quoted=False;escaped=False;pos=brace+1
 while depth:
  c=text[pos]
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='{':depth+=1
  elif c=='}':depth-=1
  pos+=1
 return text[start:pos]
names=['model_error_code','model_user_error','storage_write','storage_read','gm_object','gm_get','gm_has','gm_text','gm_string']
functions={n:extract(source,n) for n in names}
old=(OWN/'clarification-review-readable-r1/main.splash').read_text();control=extract(old,'model_user_error')
# Exactly reverse the two new UI branches to bind all old mappings byte-for-byte.
restored=functions['model_user_error']
for line in ['    if raw.search("refused:") == 0 { return "模型未接受这次请求，未采用结果。请调整需求后重试。" }\n','    if raw.search("truncated:") == 0 { return "模型回复未完整生成，未采用结果。请缩短问题，或在宿主中切换模型后重试。" }\n']:
 if restored.count(line)!=1:raise SystemExit('Expected single new UI branch absent')
 restored=restored.replace(line,'',1)
if restored!=control:raise SystemExit('Unrelated existing UI map changed')
marker='host.request("model.complete",payload,fn(r){';start=source.index(marker)+len(marker)
finish='storage_write("model-last-response.json",trace.to_json())';end=source.index(finish,start)+len(finish)
trace=source[start:end]
projection='fn fixture_trace_projection(r){\nlet request_at=1\nlet query_hash=fs.sha256("synthetic-query")\nlet session_id="chat:synthetic-error"\nlet goal_id=""\nlet current=fn(){return true}\n'+trace+'\nreturn storage_read("model-last-response.json").parse_json()\n}'
base=OWN/'rc5v15-empty-tombs-delta-r1/source-bundle';out=OWN/a.out;out.mkdir(exist_ok=False)
for name in ['manifest.json','listing.json','assets/icon.svg']:
 target=out/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(base/name,target)
minimal='let storage_fault_count=0\nlet storage_last_fault=nil\nlet actions=[]\n'+ '\n'.join(functions.values())+'\n'+control.replace('fn model_user_error(','fn old_model_user_error_control(',1)+'\n'+projection+'\nfn redraw(){}\nfn set_page(next){}\nfn calendar_enabled(){return false}\nfn boot(){}\nstart_timeout(0.05,||boot())\n'
(out/'main.splash').write_text(minimal)
binding={'suggested_readable_source_sha256':EXPECTED,'minimal_extracted_source_sha256':sha(minimal.encode()),'source_functions_copied_exactly':{n:sha(v.encode()) for n,v in functions.items()},'old_UI_control_sha256':sha(control.encode()),'reverse_only_refused_truncated_branches_restores_old_UI_function_exactly':True,'trace_callback_prefix_copied_exactly_through_storage_write_sha256':sha(trace.encode()),'trace_projection_is_fixture_only':True,'fixture_defined_request_current_context_and_widget_stubs':True,'whole_muse_model_request_send_chat_not_executed':True,'no_real_host_model_callback_or_inference':True,'no_media_copies':True}
(OWN/'ERROR_CATEGORY_FIXTURE_SOURCE_BINDING.json').write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'suggested_source_sha256':EXPECTED,'minimal_bytes':len(minimal.encode()),'minimal_source_sha256':binding['minimal_extracted_source_sha256']}))
