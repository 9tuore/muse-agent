"""Use verified official pure-crate sources with harness-only Cargo manifests.
Official .rs sources are not edited. Optional GUI dependency is not resolved.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]
BUILD=ROOT/'.local-state/night-policy'
for item in json.loads((ROOT/'research/native-agent/night-policy-sources.json').read_text()):
    data=(BUILD/item['path']).read_bytes()
    assert hashlib.sha256(data).hexdigest()==item['sha256'], item['path']
(BUILD/'Cargo.toml').write_text('[workspace]\nresolver="2"\nmembers=["crates/app-policy","crates/app-contract"]\n[patch.crates-io]\noctosense-app-contract={path="crates/app-contract"}\n')
(BUILD/'crates/app-contract/Cargo.toml').write_text('''[package]
name="octosense-app-contract"
version="1.10.0"
edition="2021"
[dependencies]
serde={version="1",features=["derive"]}
serde_json="1"
blake3="1"
url="2"
''')
(BUILD/'crates/app-policy/Cargo.toml').write_text('''[package]
name="octosense-app-policy"
version="0.1.0"
edition="2021"
[dependencies]
octosense-app-contract="1.10.0"
serde={version="1",features=["derive"]}
serde_json="1"
[features]
default=[]
splash=[]
[[test]]
name="muse_namespace"
path='''+repr(str(ROOT/'research/native-agent/night-repros/namespace.rs'))+'\n')
print('25 official source checks PASS; no source edits')

for name in ['namespace_portable', 'calendar_schema', 'five_tools']:
    with (BUILD/'crates/app-policy/Cargo.toml').open('a') as f:
        f.write('\n[[test]]\nname="'+name+'"\npath='+repr(str(ROOT/'research/native-agent/night-repros'/(name+'.rs')))+'\n')
