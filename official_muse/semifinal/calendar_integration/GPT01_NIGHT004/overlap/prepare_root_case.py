#!/usr/bin/env python3
"""Root-only fixture copying. Starts no VM, service, Kernel, GUI or build."""
import argparse,hashlib,json,shutil
from pathlib import Path

CENTRAL=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
BASE=CENTRAL/'build/night-004/native-l3-central-r4'
OWNER_SHA='103a5a86b630f772b0c560541a48a856cd1f9b300183baf4088d651b9017668a'
SOURCE_SHA='c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4'
MAIN_SHA='cdb1412b14a25fdbb8f97681e7fe344c855a0adaac50c26ded5eb17f876108d7'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,required=True,help='New directory directly under central build/night-004')
    p.add_argument('--source-sha',default=SOURCE_SHA,help='Explicit current Main source identity; defaults to fixed c892')
    p.add_argument('--main-sha256',default=MAIN_SHA,help='Explicit existing signed candidate identity; defaults to fixed cdb141')
    p.add_argument('--kernel-config',type=Path,help='Root existing public candidate config for post-integration probes; creates no package')
    a=p.parse_args();out=a.out.absolute()
    assert not out.exists() and not out.is_symlink(),'Never overwrite a prior case'
    assert out.parent.resolve(strict=True)==(CENTRAL/'build/night-004').resolve(strict=True)
    state=BASE/'initial/state';mail=BASE/'initial/mail-state';store=BASE/'kernel-state/apps/.host/calendar/events.json'
    assert (state/'FIXTURE_ONLY').read_text()=='NIGHT004 CLI VM fixture only\n'
    assert (BASE/'kernel-state/FIXTURE_ONLY').is_file() and (BASE/'kernel-state/apps/.host/FIXTURE_ONLY').is_file()
    assert not any(s.is_symlink() for src in (state,mail) for s in [src,*src.rglob('*')]),'Fixture copy refuses symlinks'
    assert not store.is_symlink() and sha(store)==OWNER_SHA
    checkpoint=json.loads((state/'l3-native-checkpoint.json').read_text())
    assert checkpoint['event']['id']=='ev-1791775730787' and len(json.loads(store.read_text()))==1
    report=json.loads((BASE/'initial/report.json').read_text())
    assert report['status']=='PASS' and report['source_identity']['source_sha256']==SOURCE_SHA
    cfg=json.loads((a.kernel_config or BASE/'initial/kernel-helper/config.json').read_text())
    assert cfg['main_sha256']==a.main_sha256 and sha(Path(cfg['signed_bundle'])/'main.splash')==a.main_sha256
    assert sha(CENTRAL/'official_muse/app/source/main.splash')==a.source_sha,'Explicit current Main source identity differs'
    out.mkdir(exist_ok=False)
    shutil.copytree(state,out/'state');shutil.copytree(mail,out/'mail-state')
    kernel=out/'kernel-state';owner=kernel/'apps/.host/calendar';owner.mkdir(parents=True)
    shutil.copy2(store,owner/'events.json')
    (kernel/'FIXTURE_ONLY').write_text('NIGHT004 synthetic overlap Root fixture only\n')
    (kernel/'apps/.host/FIXTURE_ONLY').write_text('Synthetic fixture only\n')
    cfg['fixture_root']=str(kernel)
    (out/'kernel-config.json').write_text(json.dumps(cfg,ensure_ascii=True,indent=2)+'\n')
    record={'state':'FIXTURE_PREPARED_NO_RUNTIME','baseline':str(BASE),'owner_sha256':OWNER_SHA,
        'event_id':checkpoint['event']['id'],'goal_count':1,'run_count':1,'memory_count':3,
        'main_sha256':a.main_sha256,'source_sha256':a.source_sha,'kernel_ledger_copied':False,
        'state_root':str(out/'state'),'mail_root':str(out/'mail-state'),'kernel_config':str(out/'kernel-config.json')}
    (out/'fixture-preparation.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))

if __name__=='__main__':main()
