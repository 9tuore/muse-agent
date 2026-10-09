"""Check proposed patch scope, application and tested-core correspondence."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'research/native-agent'
OFF=ROOT/'.local-state/native-agent-upstream/OctoSense'
PATCH=OUT/'patches/calendar-shared-reconciliation.patch'
paths=['apps/calendar/host-service/src/lib.rs','apps/calendar/bundle/tools.json']
with tempfile.TemporaryDirectory(prefix='calendar-review-apply-') as tmp:
    checkout=Path(tmp)
    subprocess.run(['git','init','-q',tmp],check=True)
    for path in paths:
        dest=checkout/path;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(OFF/path,dest)
    subprocess.run(['git','apply','--check',str(PATCH)],cwd=checkout,check=True)
    subprocess.run(['git','apply',str(PATCH)],cwd=checkout,check=True)
    # Raw two-file diff, no personal paths/extra Gate/runtime file changes.
    changed=[line[6:] for line in PATCH.read_text().splitlines() if line.startswith('+++ b/')]
    assert changed==paths,changed
    applied=(checkout/paths[0]).read_text()
    anchor="/// The service the Card runner (and the agent's tools) call."
    a=applied.index(anchor);b=applied.index('#[cfg(test)]\nmod tests',a)
    expected_core=applied[:a].replace('use octosense_appstore::services::{HostService, Replier, ServiceCall, ServiceHost};\n','')+applied[b:]
    tested=(ROOT/'.local-state/night-calendar-patched/src/lib.rs').read_text()
    assert tested==expected_core+'\npub mod relay_catalog;\n'
    assert json.loads((checkout/paths[1]).read_text())==json.loads((ROOT/'.local-state/night-calendar-patched/tools.json').read_text())
    assert 'if app != APP' in applied
    result={'patch_sha256':hashlib.sha256(PATCH.read_bytes()).hexdigest(),
            'upstream_commit':'3a4d1e1e557750eac69b412f34d36021306ea654',
            'changed_upstream_paths':changed,'apply_check':'PASS','tested_core_matches_applied_patch':'PASS',
            'owner_guard':'RETAINED','native_host':'NOT_TESTED','gate_changed':False}
    (OUT/'night-repros/calendar-review-patch-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
