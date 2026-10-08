#!/usr/bin/env python3
"""Non-disclosing review of current release sources and seven-hour public diff."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
# Scope deliberately excludes historical/private fixtures, profiles and build data.
paths=[ROOT/'official_muse/app/source/main.splash',ROOT/'official_muse/app/bundle/main.splash',ROOT/'official_muse/global_memory.splash',ROOT/'official_muse/core.splash',ROOT/'official_muse/scheduling.splash',ROOT/'official_muse/incoming_mail.splash',ROOT/'official_muse/app/bundle/manifest.json',ROOT/'dependencies.lock.json']
changed=subprocess.check_output(['git','diff','--name-only','5126afc4'],cwd=ROOT,text=True).splitlines()
for name in changed:
 p=ROOT/name
 if name.startswith('sdk-overlays/') or (name.startswith('official_muse/rc/7h-20261008/') and p.suffix in ['.py','.md','.rs','.kt','.java','.sh']):paths.append(p)
patterns={'private_key_header':re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),'service_token':re.compile(r'\b(?:sk-[A-Za-z0-9_-]{24,}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{50,}|AKIA[0-9A-Z]{16})\b')}
files={};findings=[]
for p in sorted(set(paths)):
 if not p.is_file():continue
 if any(s in p.parts for s in ['runtime','.local-state','vendor']):continue
 data=p.read_bytes();files[str(p.relative_to(ROOT))]=hashlib.sha256(data).hexdigest()
 try:text=data.decode('utf-8')
 except UnicodeDecodeError:continue
 for lineno,line in enumerate(text.splitlines(),1):
  for kind,pattern in patterns.items():
   if pattern.search(line):findings.append({'path':str(p.relative_to(ROOT)),'line':lineno,'kind':kind})
v={'scope':'Current release business source/manifest/dependency lock and seven-hour source changes; excludes private/historical runtime and caches. No secret values emitted. This is a bounded static check, not a general penetration test.','git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'checked_file_sha256':files,'credential_pattern_findings':findings,'status':'PASS' if not findings else 'REVIEW_REQUIRED'}
(Q/'STATIC_REVIEW.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'files':len(files),'findings':findings,'status':v['status']},ensure_ascii=False))
