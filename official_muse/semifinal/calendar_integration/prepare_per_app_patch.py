"""Prepare the actual Store patch/tests in ignored build; never run Cargo."""
import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent


def prepare(hub, output):
    relative = 'crates/app-hub/src/client.rs'
    before = (hub / relative).read_text()
    after = before

    def replace(old, new):
        nonlocal after
        assert after.count(old) == 1, f'Unexpected Store baseline: {old[:60]}'
        after = after.replace(old, new)

    replace('    limits: HostLimits,\n', '    limits: HostLimits,\n    agent_tool_offers: BTreeMap<String, String>,\n')
    replace('            limits,\n', '            limits,\n            agent_tool_offers: BTreeMap::new(),\n')
    insertion = '''    /// Host-only ceiling for one authenticated store app, never a grant.
    /// Empty by default. None revokes; other app ceilings are unchanged.
    /// Embeddings must revalidate admission after a host configuration change.
    pub fn set_agent_tool_offer(&mut self, app_id: &str, tool: Option<&str>) -> Result<(), String> {
        let Some(tool) = tool else {
            self.agent_tool_offers.remove(app_id);
            return Ok(());
        };
        if app_id.starts_with("os.") { return Err("a store offer cannot name a system app".into()); }
        octosense_app_policy::check_reserved_id(app_id)?;
        let entry = self.entry(app_id).ok_or_else(|| format!("{app_id} is not in the verified catalog"))?;
        if !entry.status.is_offered() { return Err(format!("{app_id} is withdrawn")); }
        if entry.manifest.integrity.signature.is_none() && entry.manifest.integrity.github.is_none() {
            return Err("an additional agent offer requires an authenticated manifest".into());
        }
        octosense_app_policy::verify::verify_manifest(&entry.manifest, &self.publisher_keys())?;
        self.agent_tool_offers.insert(app_id.into(), tool.into());
        Ok(())
    }

    fn limits_for(&self, app_id: &str) -> HostLimits {
        let mut limits = self.limits.clone();
        if let Some(tool) = self.agent_tool_offers.get(app_id) {
            if !limits.offered_tools.contains(tool) { limits.offered_tools.push(tool.clone()); }
        }
        limits
    }

'''
    replace('    /// Bind this device\'s implemented API versions.', insertion+'    /// Bind this device\'s implemented API versions.')
    replace('&staged_json, &digest, &self.limits, &self.publisher_keys()', '&staged_json, &digest, &self.limits_for(entry.app_id()), &self.publisher_keys()')
    replace('&text, &digest, &self.limits, &self.publisher_keys()', '&text, &digest, &self.limits_for(entry.app_id()), &self.publisher_keys()')
    replace('        octosense_app_policy::verify::verify_manifest(&entry.manifest, &self.publisher_keys())?;\n        Ok(())',
            '        octosense_app_policy::verify::verify_manifest(&entry.manifest, &self.publisher_keys())?;\n        octosense_app_policy::policy::resolve(&entry.manifest, &self.limits_for(entry.app_id()))?;\n        Ok(())')
    test = (HERE / 'per_app_offer_tests.rs').read_text()
    patch = ''.join(difflib.unified_diff(before.splitlines(True), after.splitlines(True), fromfile='a/'+relative,tofile='b/'+relative))
    patch += ''.join(difflib.unified_diff([], test.splitlines(True), fromfile='/dev/null', tofile='b/crates/app-hub/tests/per_app_offer.rs'))
    (HERE / 'hub-per-app-store-offer.patch').write_text(patch)
    output.mkdir(parents=True, exist_ok=False)
    for crate in ['app-contract', 'app-policy', 'app-hub']:
        shutil.copytree(hub / 'crates' / crate, output / 'crates' / crate)
    workspace = '''[workspace]
resolver = "2"
members = ["crates/app-contract", "crates/app-policy", "crates/app-hub"]
[patch.crates-io]
octosense-app-contract = {path = "crates/app-contract"}
[patch."https://github.com/OctoSense-org/Octoscript.git"]
octoscript-ui-l0 = {path = L0PATH}
'''.replace('L0PATH', json.dumps(str((hub.parent / 'octoscript/crates/octoscript-ui-l0').resolve())))
    (output / 'Cargo.toml').write_text(workspace)
    shutil.copyfile(hub / 'Cargo.lock', output / 'Cargo.lock')
    done = subprocess.run(['git', 'apply', '--unsafe-paths', '-'], input=patch, text=True, cwd=output, capture_output=True)
    assert done.returncode == 0, done.stderr
    identity = {'kind':'ACTUAL_STORE_PATCH_PREPARED_NOT_COMPILED',
                'baseline_client_sha256': hashlib.sha256(before.encode()).hexdigest(),
                'patch_sha256':hashlib.sha256(patch.encode()).hexdigest(),
                'tests':8, 'cargo_started':False}
    (HERE / 'per-app-preparation.json').write_text(json.dumps(identity,indent=2)+'\n')
    print(json.dumps(identity))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--hub', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    assert 'build' in a.out.resolve().parts, 'Prepared code must stay in ignored build'
    prepare(a.hub.resolve(), a.out.resolve())
