"""Compile original pure Calendar/relay logic; remove only Host registration adapter.
Not a native shell/relay integration or model test. No mock Calendar implementation.
"""
from pathlib import Path
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[3]
ORIGINAL = ROOT / '.local-state/native-agent-upstream/OctoSense'
BUILD = ROOT / '.local-state/night-calendar'
BUILD.mkdir(exist_ok=True)
(BUILD / 'src').mkdir(exist_ok=True)
(BUILD / 'resources').mkdir(exist_ok=True)
source = (ORIGINAL / 'apps/calendar/host-service/src/lib.rs').read_text()
import_line = 'use octosense_appstore::services::{HostService, Replier, ServiceCall, ServiceHost};\n'
assert source.count(import_line) == 1
begin = source.index('/// The service the Card runner (and the agent\'s tools) call.')
end = source.index('#[cfg(test)]\nmod tests', begin)
core = source[:begin].replace(import_line, '') + source[end:]
(BUILD / 'src/lib.rs').write_text(core)
for name in ['ui.rs', 'cards.rs']:
    shutil.copyfile(ORIGINAL / 'apps/calendar/host-service/src' / name, BUILD / 'src' / name)
for name in ['event.card', 'agenda.card']:
    shutil.copyfile(ORIGINAL / 'apps/calendar/host-service/resources' / name, BUILD / 'resources' / name)
relay = (ORIGINAL / 'crates/shell/src/host_tools/relay.rs').read_text()
def method(signature):
    start = relay.index(signature)
    brace = relay.index('{', start)
    depth = 1
    end = brace + 1
    while depth:
        if relay[end] == '{': depth += 1
        if relay[end] == '}': depth -= 1
        end += 1
    return relay[start:end]
methods = [method(x) for x in ['pub fn grant(', 'pub fn entry(', 'fn shareable(', 'pub fn may_call(']]
# Only two data fields required by these exact production methods are retained.
catalog = '''use serde_json::Value;
use std::collections::{BTreeMap, BTreeSet};
const TOOLBOX: &str = "toolbox";
#[derive(Default)]
pub struct Catalog {
    pub tools: BTreeMap<String, Vec<Value>>,
    grants: BTreeMap<String, BTreeSet<(String, String)>>,
}
impl Catalog {
''' + '\n'.join(methods) + '\n}\n'
(BUILD / 'src/relay_catalog.rs').write_text(catalog)
with (BUILD / 'src/lib.rs').open('a') as f: f.write('\npub mod relay_catalog;\n')
(BUILD / 'Cargo.toml').write_text('''[workspace]
[package]
name = "calendar-core-repro"
version = "0.0.0"
edition = "2021"
[dependencies]
chrono = "0.4"
chrono-tz = "0.10"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
[[test]]
name = "calendar_boundaries"
path = ''' + repr(str(ROOT / 'research/native-agent/night-repros/calendar.rs')) + '\n')
provenance = {'layer': 'ISOLATED_ORIGINAL_RUST_CORE', 'host_registration_adapter': 'REMOVED_NOT_TESTED',
              'runtime': 'NO_HOST_NO_MODEL', 'core_sha256': hashlib.sha256(core.encode()).hexdigest(),
              'relay_methods': [hashlib.sha256(m.encode()).hexdigest() for m in methods],
              'calendar_handle_ui_cards': 'original unchanged', 'fixture_data': 'synthetic isolated temp directory'}
(ROOT / 'research/native-agent/night-repros/calendar-extraction.json').write_text(json.dumps(provenance, indent=2)+'\n')
print(BUILD)
