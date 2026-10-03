#!/usr/bin/env python3
"""Narrow source-boundary checks; not a live startup or sandbox-security test."""
from pathlib import Path
import hashlib,json,os
r=Path(__file__).resolve().parents[3];e=r/'official_muse/prelim/evidence/startup-host';i=json.loads((e/'source-index.json').read_text());src=Path(i['source_sdk']);snap=Path(i['snapshot_sdk'])
def entries(root):
 out={}
 for directory,dirs,files in os.walk(root,followlinks=False):
  for name in dirs+files:
   p=Path(directory)/name;rel=str(p.relative_to(root))
   if p.is_symlink():out[rel]=('link',str(p.readlink()))
   elif p.is_file():out[rel]=('file',hashlib.sha256(p.read_bytes()).hexdigest())
 return out
before=entries(src);after=entries(snap);changed=[k for k in sorted(before.keys()|after.keys()) if before.get(k)!=after.get(k)]
assert changed==['widgets/src/splash.rs'],changed
b=(src/'widgets/src/splash.rs').read_text();a=(snap/'widgets/src/splash.rs').read_text();body='        eval_out = Some(cx.with_script_vm_id(vm_id, |vm| {'
assert b.split(body,1)[1]==a.split(body,1)[1]
start=a.index('        if let Some(sheet)=sheet {',a.index('let mut eval_out = None'))
trusted=a[start:a.index(body,start)]
assert trusted.count('with_script_vm_id_trusted')==1
assert 'eval_with_append_source' not in trusted and 'script_mod' not in trusted and 'handle_event(' not in trusted
assert 'crate::script_eval!(vm, {mod.res = nil});' in trusted
assert '#[rust]\n    stylesheet:' in a
for rel in ['widgets/src/widget_async.rs','platform/script/src/vm.rs']:
 assert (src/rel).read_bytes()==(snap/rel).read_bytes()
budget=(snap/'widgets/src/widget_async.rs').read_text()
budget=budget[budget.index('fn with_splash_budget<R>'):budget.index('pub trait CxSplashVmExt')]
assert budget.count('Duration::from_millis(64)')==2 and '\n        512,\n' in budget
assert 'const SPLASH_EVAL_INSTRUCTION_LIMIT: usize = 200_000;' in a
info={'kind':'SOURCE_BOUNDARY_CHECK_NOT_RUNTIME_PASS','changed_files':changed,'file_entries':len(before),'app_body_and_events_exact_bytes_unchanged':True,'theme_branch_trusted_only':True,'temporary_font_resolver_still_removed':True,'budget_implementations_identical':True,'entry_budget_durations_ms':[64,64],'entry_budget_check_interval':512,'app_eval_instruction_limit':200000,'sdk_versions_not_changed':True,'original_splash_sha256':hashlib.sha256(b.encode()).hexdigest(),'snapshot_splash_sha256':hashlib.sha256(a.encode()).hexdigest()}
(e/'boundary-check.json').write_text(json.dumps(info,indent=2)+'\n');print(json.dumps(info))
