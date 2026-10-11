#!/usr/bin/env python3
"""Native production Mail failure closure, actual helper and actual new processes."""
import argparse, hashlib, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
p = argparse.ArgumentParser()
p.add_argument('--source',type=Path,required=True)
p.add_argument('--source-sha',required=True)
p.add_argument('--runner',type=Path,required=True)
p.add_argument('--mail-binary',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a = p.parse_args()
out = a.out.resolve(); out.relative_to(ROOT/'build'); out.mkdir(parents=True,exist_ok=False)
prepared, rows = {},[]
for name in ['mail_fault','mail_fault_restart','mail_write_failure','bad_store_setup','bad_store_restart']:
    target = out/(name+'-prepare')
    result = subprocess.run([sys.executable,str(HERE/'prepare.py'),'--source',str(a.source),'--source-sha',a.source_sha,
        '--probe',str(HERE/(name+'_probe.splash')),'--out',str(target)],capture_output=True,text=True)
    (out/(name+'-prepare.log')).write_text(result.stdout+result.stderr)
    assert result.returncode == 0, 'Exact source preparation failed; see '+str(out/(name+'-prepare.log'))
    prepared[name] = target/'executed.splash'

def run(name,label,extra=()):
    target = out/label
    cmd = [sys.executable,str(HERE/'run.py'),'--prepared',str(prepared[name]),'--runner',str(a.runner),
           '--mail-binary',str(a.mail_binary),'--out',str(target),*map(str,extra)]
    result = subprocess.run(cmd,capture_output=True,text=True,timeout=140)
    (out/(label+'.log')).write_text(result.stdout+result.stderr)
    report = json.loads((target/'report.json').read_text())
    rows.append(dict(case=label,report=str(target/'report.json'),status=report['status'],exit_code=result.returncode,
                     checks=len((report.get('probe') or {}).get('checks',{})),failed=report['failed'],
                     counters=report['counters'],faults=report['faults']))
    return target

for label,mode,fault in [('accepted','accepted','none'),('before','before','none'),('unknown','unknown','none'),
                         ('parent-timeout','accepted','mail-review-timeout'),('parent-bad-json','accepted','mail-review-malformed-json')]:
    initial = run('mail_fault',label,['--mail-mode',mode,'--fault-case',fault])
    if rows[-1]['status'] == 'PASS':
        run('mail_fault_restart',label+'-restart',['--state-root',initial/'state','--mail-root',initial/'mail-state'])
run('mail_write_failure','actual-os-write-failure')
initial = run('bad_store_setup','actual-bad-store-setup')
if rows[-1]['status'] == 'PASS':
    run('bad_store_restart','actual-bad-store-restart',['--state-root',initial/'state','--mail-root',initial/'mail-state'])
report = dict(kind='NATIVE_MAIL_MEMORY_L4_COMPONENT_FIXTURE',source_sha256=a.source_sha,cases=rows,
    status='PASS' if all(row['status']=='PASS' and row['exit_code']==0 for row in rows) else 'FAIL',
    checks=sum(row['checks'] for row in rows),full_chain_status='NOT_TESTED',
    runner_sha256=hashlib.sha256(a.runner.read_bytes()).hexdigest(),mail_binary_sha256=hashlib.sha256(a.mail_binary.read_bytes()).hexdigest(),
    boundary='Production functions byte compared. Actual SDK service/independent recipient/OS writes/new processes. MockTransport/Vault/review and injected parent reply loss/decode refusal are fixtures. No Kernel/Calendar results or completion fabricated.')
(out/'summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(status=report['status'],cases=len(rows),checks=report['checks'],source_sha256=a.source_sha)))
raise SystemExit(0 if report['status']=='PASS' else 1)
