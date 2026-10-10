"""Generate only a reviewed-native-grant owner preparation patch."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def prepare(sdk):
    relative = 'crates/shell/src/host_tools/mod.rs'
    before = (sdk / relative).read_text()
    old = '''    fn declarations(&self, app_id: &str, account: &str) -> Result<Vec<Value>, String> {
        let app = app_of_peer(app_id).to_string();
        #[cfg(any(feature = "app-hub", native_mobile))]
        admission::check(&app)?;
        ensure_loaded(app_id);
'''
    added = '''        // A native peer already has its reviewed grants in Catalog::shipped,
        // but ensure_loaded only prepares contained callers. Load the system
        // owners of those grants before registering native peer declarations.
        // This installs owner executors, never grants or caller identities.
        #[cfg(any(feature = "app-hub", native_mobile))]
        if let Some(native) = crate::native_apps::find(&app) {
            let owners: BTreeSet<&str> = native.grants.iter()
                .map(|(owner, _)| *owner).filter(|owner| owner.starts_with("os.")).collect();
            for owner in owners {
                admission::check(owner)?;
                let ready = with_relay(|r| r.catalog.knows(owner) && r.has_executor(owner));
                if !ready { script_apps::load(owner)?; }
            }
        }
'''
    assert before.count(old) == 1, 'Review changed Shell declarations before applying'
    after = before.replace(old, old + added)
    patch = ''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),
        fromfile='a/'+relative,tofile='b/'+relative))
    (HERE/'native-granted-owner-preparation.patch').write_text(patch)
    result = {'task':'MUSE-MULTIAGENT-EFFICIENCY-001/ZC-01',
        'kind':'ACTUAL_SHELL_NATIVE_DECLARATIONS_PATCH_NOT_COMPILED',
        'baseline_source_sha256':hashlib.sha256(before.encode()).hexdigest(),
        'projected_source_sha256':hashlib.sha256(after.encode()).hexdigest(),
        'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),
        'writes_native_registry':False,'adds_grants':False,'touches_relay_identity_checks':False,
        'cargo_started':False,'host_execution':'NOT_RUN','status':'BLOCKED'}
    (HERE/'NATIVE_OWNER_PATCH_RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('--sdk',type=Path,required=True)
    prepare(p.parse_args().sdk.resolve())
