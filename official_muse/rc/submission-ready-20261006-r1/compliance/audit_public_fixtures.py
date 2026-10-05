#!/usr/bin/env python3
"""Read-only Git-tree dependency audit; no UI, model or service calls."""
import argparse, json, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--ref',default='HEAD');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
sha=subprocess.check_output(['git','rev-parse',a.ref],cwd=a.repo,text=True).strip()
tracked=set(subprocess.check_output(['git','ls-tree','-r','--name-only',sha],cwd=a.repo,text=True).splitlines())
paths=[
'official_muse/ui_memory/tests/regression_result_receipt.py',
'official_muse/rc/remaining-20261005-r2/a2/run_receipt.py',
'official_muse/rc/remaining-20261005-r2/a2/receipt.splash',
'official_muse/rc/remaining-20261005-r2/a2/capacity-r1/first/state/muse-goals/memory.json',
'official_muse/rc/remaining-20261005-r2/a2/capacity-canonical-header-r1/first/state/muse-goals/memory.json',
'official_muse/rc/remaining-20261005-r2/a2/capacity-canonical-header-r1/first/state/muse-goals/memory.backup.json',
'official_muse/rc/remaining-20261005-r2/a2/capacity-canonical-header-r1/first/state/muse-goals/global-memory-settings.json',
'official_muse/rc/remaining-20261005-r2/a2/capacity-canonical-header-r1/first/state/muse-goals/activity.json']
rows=[dict(path=x,in_git_tree=x in tracked,exists_locally=(a.repo/x).is_file()) for x in paths]
report=dict(kind='READ_ONLY_PUBLIC_FIXTURE_DEPENDENCY_AUDIT',source_commit=sha,status='PORTABLE' if all(x['in_git_tree'] for x in rows) else 'NOT_PORTABLE',dependencies=rows,additional_runtime_dependency='run_receipt.HOST hardcodes packaging/.local-state/chunk-delta-r2/.../card-host; needs explicitly supplied compatible runtime',no_runtime_or_user_state_read=True)
a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(status=report['status'],missing=[x['path'] for x in rows if not x['in_git_tree']]),ensure_ascii=False))
