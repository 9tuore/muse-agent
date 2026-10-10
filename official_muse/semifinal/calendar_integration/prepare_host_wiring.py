"""Prepare a default-empty host-only wiring proposal; never run Cargo."""
import argparse
import difflib
import hashlib
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent


def prepare(hub, sdk, r3, out):
    assert 'build' in out.resolve().parts
    out.mkdir(parents=True, exist_ok=False)
    for name in ['app-contract', 'app-policy', 'app-hub', 'appstore', 'app-hub-app']:
        shutil.copytree(hub / 'crates' / name, out / 'crates' / name)
    before = {}
    after = {}

    def edit(tree, relative, old, new):
        key = (tree, relative)
        root = hub if tree == 'hub' else sdk
        before.setdefault(key, (root / relative).read_text())
        text = after.get(key, before[key])
        assert text.count(old) == 1, f'Unexpected baseline: {relative}: {old[:50]}'
        after[key] = text.replace(old, new)

    client = 'crates/app-hub/src/client.rs'
    before['hub', client] = (hub / client).read_text()
    after['hub', client] = (r3 / client).read_text()
    edit('hub', client, 'use std::collections::BTreeMap;', '''use std::collections::BTreeMap;
use std::sync::{Arc, Mutex};

/// One host-owned in-process configuration shared by Store instances.
/// Empty by default, never exposed through a script service or persisted
/// as user authorization. Updates must pass Store's authenticated setter.
#[derive(Clone, Default)]
pub struct AgentToolOffers(Arc<Mutex<BTreeMap<String, Vec<String>>>>);
''')
    edit('hub', client, '    agent_tool_offers: BTreeMap<String, String>,', '    agent_tool_offers: AgentToolOffers,')
    edit('hub', client, '            agent_tool_offers: BTreeMap::new(),', '            agent_tool_offers: AgentToolOffers::default(),')
    start = after['hub', client].index('    /// Host-only ceiling for one authenticated store app')
    end = after['hub', client].index('    /// Bind this device', start)
    old = after['hub', client][start:end]
    new = '''    /// Attach the embedding's shared configuration before using this Store.
    pub fn with_agent_tool_offers(mut self, offers: AgentToolOffers) -> Self {
        self.agent_tool_offers = offers;
        self
    }

    /// Replace one authenticated app's exact host ceiling. Not user consent
    /// or a Relay grant. An empty set revokes across every sharing instance.
    pub fn set_agent_tool_offers(&mut self, app_id: &str, tools: &[&str]) -> Result<(), String> {
        if !tools.is_empty() {
            if app_id.starts_with("os.") { return Err("a store offer cannot name a system app".into()); }
            octosense_app_policy::check_reserved_id(app_id)?;
            let entry = self.entry(app_id).ok_or_else(|| format!("{app_id} is not in the verified catalog"))?;
            if !entry.status.is_offered() { return Err(format!("{app_id} is withdrawn")); }
            if entry.manifest.integrity.signature.is_none() && entry.manifest.integrity.github.is_none() {
                return Err("an additional agent offer requires an authenticated manifest".into());
            }
            octosense_app_policy::verify::verify_manifest(&entry.manifest, &self.publisher_keys())?;
        }
        let mut offers = self.agent_tool_offers.0.lock()
            .map_err(|_| "host agent-tool offer configuration is unavailable".to_string())?;
        if tools.is_empty() { offers.remove(app_id); }
        else { offers.insert(app_id.into(), tools.iter().map(|tool| (*tool).to_string()).collect()); }
        Ok(())
    }

    pub fn set_agent_tool_offer(&mut self, app_id: &str, tool: Option<&str>) -> Result<(), String> {
        match tool {
            Some(tool) => self.set_agent_tool_offers(app_id, &[tool]),
            None => self.set_agent_tool_offers(app_id, &[]),
        }
    }

    fn limits_for(&self, app_id: &str) -> Result<HostLimits, String> {
        let mut limits = self.limits.clone();
        let offers = self.agent_tool_offers.0.lock()
            .map_err(|_| "host agent-tool offer configuration is unavailable".to_string())?;
        if let Some(tools) = offers.get(app_id) {
            for tool in tools {
                if !limits.offered_tools.contains(tool) { limits.offered_tools.push(tool.clone()); }
            }
        }
        Ok(limits)
    }

    /// Resolve reviewed catalog permissions for display/install consent,
    /// with the same current ceiling used by install and launch. This does
    /// not verify downloaded bytes or replace install_staged/may_run.
    pub fn resolve_offered_policy(&self, app_id: &str) -> Result<AppPolicy, String> {
        let entry = self.entry(app_id).ok_or_else(|| format!("{app_id} is not in the verified catalog"))?;
        if !entry.status.is_offered() { return Err(format!("{app_id} is withdrawn")); }
        octosense_app_policy::verify::verify_manifest(&entry.manifest, &self.publisher_keys())?;
        octosense_app_policy::policy::resolve(&entry.manifest, &self.limits_for(entry.app_id())?)
    }

'''
    edit('hub', client, old, new)
    text = after['hub', client]
    assert text.count('&self.limits_for(entry.app_id())') == 4
    # The new display helper already has ?, while the three r3 sites do not.
    after['hub', client] = re.sub(r'&self\.limits_for\(entry\.app_id\(\)\)(?!\?)',
        '&self.limits_for(entry.app_id())?', text)
    edit('hub', 'crates/app-hub/src/lib.rs', '    PreparedLaunch, Store,', '    AgentToolOffers, PreparedLaunch, Store,')
    appstore = 'crates/appstore/src/lib.rs'
    edit('hub', appstore, 'static DATA_ROOT: OnceLock<Mutex<Option<PathBuf>>> = OnceLock::new();', '''static DATA_ROOT: OnceLock<Mutex<Option<PathBuf>>> = OnceLock::new();
static STORE_AGENT_OFFERS: OnceLock<octosense_app_hub::AgentToolOffers> = OnceLock::new();

/// The host's Store factory. Every installed-app path shares the same
/// default-empty offer configuration, existing host ceilings and API list.
/// The host may update it through an authenticated Store setter after
/// accepting its catalog and checking the existing channel sequence floor.
/// No script service, environment toggle or durable authorization is added.
pub fn host_store(anchor: &str, root: &std::path::Path) -> Store {
    Store::new(anchor, root, HostLimits::default())
        .with_host_api_versions(crate::host_api::available_versions())
        .with_agent_tool_offers(STORE_AGENT_OFFERS.get_or_init(Default::default).clone())
}''')
    edit('hub', appstore, 'Store::new(&anchor, &self.app_data_root, HostLimits::default()).with_host_api_versions(crate::host_api::available_versions())', 'host_store(&anchor, &self.app_data_root)')
    card = 'crates/appstore/src/cardapp.rs'
    edit('hub', card, 'Store::new(&anchor, &root, HostLimits::default())\n                    .with_host_api_versions(crate::host_api::available_versions())', 'crate::host_store(&anchor, &root)')
    edit('hub', card, 'use octosense_app_hub::Store;\n', '')
    edit('hub', card, 'use octosense_app_policy::HostLimits;\n', '')
    catalog = 'crates/app-hub-app/src/catalog.rs'
    edit('hub', catalog, 'Store::new(&anchor, &root, HostLimits::default()).with_host_api_versions(octosense_appstore::host_api::available_versions())', 'octosense_appstore::host_store(&anchor, &root)')
    edit('hub', catalog, 'octosense_app_policy::policy::resolve(&entry.manifest, &HostLimits::default())\n                    .ok()?;', 'self.store.resolve_offered_policy(&listing.app_id).ok()?;')
    edit('hub', catalog, 'octosense_app_policy::policy::resolve(&entry.manifest, &HostLimits::default())?;', 'self.store.resolve_offered_policy(&consent.app_id)?;')
    admission = 'crates/shell/src/host_tools/admission.rs'
    edit('desktop', admission, '''octosense_app_hub::Store::new(
        anchor,
        root,
        octosense_app_contract::HostLimits::default(),
    )
    .with_host_api_versions(octosense_appstore::host_api::available_versions())''', 'octosense_appstore::host_store(anchor, root)')
    glance = 'crates/shell/src/glance_card.rs'
    edit('desktop', glance, '''octosense_app_hub::Store::new(&anchor, &root, octosense_app_contract::HostLimits::default())
                .with_host_api_versions(octosense_appstore::host_api::available_versions())''', 'octosense_appstore::host_store(&anchor, &root)')
    tests_rel = 'crates/app-hub/tests/per_app_offer.rs'
    before['hub', tests_rel] = ''
    test = (r3 / tests_rel).read_text()
    assert test.count('    apps: Vec<Fixture>,') == 1
    test = test.replace('    apps: Vec<Fixture>,', '    apps: Vec<Fixture>,\n    anchor_public_hex: String,')
    test = test.replace('        let store = Store::new(&anchor.public_hex(),', '        let anchor_public_hex = anchor.public_hex();\n        let store = Store::new(&anchor_public_hex,')
    test = test.replace('Self { apps, store, catalog, signer, certificate }', 'Self { apps, anchor_public_hex, store, catalog, signer, certificate }')
    after['hub', tests_rel] = test + (HERE / 'shared_offer_tests.rs').read_text()
    patches = {'hub': '', 'desktop': ''}
    for (tree, relative), text in after.items():
        patches[tree] += ''.join(difflib.unified_diff(before[tree,relative].splitlines(True), text.splitlines(True),
            fromfile=('a/'+relative) if before[tree,relative] else '/dev/null', tofile='b/'+relative))
        if tree == 'hub': (out / relative).write_text(text)
    for tree, patch in patches.items():
        (HERE / f'{tree}-shared-host-wiring.patch').write_text(patch)
    workspace = (hub / 'Cargo.toml').read_text()
    workspace = re.sub(r'members = \[.*?\]', 'members = ["crates/app-contract","crates/app-policy","crates/app-hub","crates/appstore","crates/app-hub-app"]', workspace, count=1, flags=re.S)
    workspace = re.sub(r'path = "(\.\./[^"]+)"', lambda m:'path = '+json.dumps(str((hub / m[1]).resolve())), workspace)
    (out / 'Cargo.toml').write_text(workspace)
    shutil.copyfile(r3 / 'Cargo.lock', out / 'Cargo.lock')
    result = {'kind':'SHARED_HOST_WIRING_PREPARED_NOT_COMPILED','source_head':'Hub95e4831/Desktop4ccf8e0',
        'patch_sha256':{tree:hashlib.sha256(patch.encode()).hexdigest() for tree,patch in patches.items()},
        'total_tests':10,'new_tests':2,'cargo_started':False,'default_offer':'EMPTY','formal_status':'BLOCKED'}
    (HERE / 'host-wiring-preparation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    p=argparse.ArgumentParser()
    for name in ['hub','sdk','r3','out']: p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args(); prepare(a.hub.resolve(),a.sdk.resolve(),a.r3.resolve(),a.out.resolve())
