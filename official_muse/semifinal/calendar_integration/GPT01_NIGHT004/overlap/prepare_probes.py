#!/usr/bin/env python3
"""Prepare exact closures with the existing official preparer, in own build only.

Starts no VM/service/Kernel/build. Only the official output jail is redirected
to this worktree's build directory. All extraction/assertions/adapters stay exact.
"""
import argparse,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[4]
CENTRAL=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
PREPARER=CENTRAL/'official_muse/semifinal/mail_integration/gpt02_recovery/night004/l3/prepare.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--source-sha',required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--baseline-only',action='store_true')
    a=p.parse_args(); root=a.out.resolve();root.relative_to(OWN/'build');root.mkdir(parents=True,exist_ok=False)
    assert sha(a.source)==a.source_sha
    common='native_overlap_probe.splash'
    specs={name:[name+'_slot.splash',common] for name in ['same','contained','adjacent']}
    if not a.baseline_only:
        specs.update({name:['same_slot.splash',common,'guard_'+name+'.splash','preflight_guard_probe.splash'] for name in ['time_change','different_goal']})
        specs.update({name:[name+'.splash','preflight_unknown_probe.splash'] for name in ['unknown_timezone','unknown_no_end']})
    program=PREPARER.read_text(); needle="out.relative_to(ROOT / 'build')"
    assert program.count(needle)==1
    adapted=program.replace(needle,"out.relative_to(Path("+repr(str(OWN/'build'))+"))")
    records=[]
    for name,files in specs.items():
        target=root/name
        sys.argv=[str(PREPARER),'--source',str(a.source),'--source-sha',a.source_sha,
            '--probe',*[str(HERE/n) for n in files],'--out',str(target)]
        exec(compile(adapted,str(PREPARER),'exec'),{'__file__':str(PREPARER),'__name__':'__main__'})
        identity=json.loads((target/'identity.json').read_text())
        records.append({'case':name,'prepared':str(target/'executed.splash'),'executed_sha256':sha(target/'executed.splash'),
            'identity_sha256':sha(target/'identity.json'),'function_count':len(identity['production_function_sha256']),
            'global_count':len(identity['production_global_sha256']),'exact_function_assertions':identity['all_other_functions_byte_equal_after_transport_normalization']})
    record={'status':'PREPARED_NOT_RUN','source':str(a.source),'source_sha256':a.source_sha,'official_preparer':str(PREPARER),
        'official_preparer_sha256':sha(PREPARER),'only_preparer_change':'Output jail redirected to own build',
        'cases':records,'boundary':'No VM/services/Kernel/GUI/build. Prepared final output is compact; original data remains parent logs. Root must execute on separately cloned cases and exact signed candidate.'}
    (root/'preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))

if __name__=='__main__':main()
