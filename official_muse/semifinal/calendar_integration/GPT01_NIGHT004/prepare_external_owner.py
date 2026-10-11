"""Extend only the existing owned small helper stage; verify service source."""
import hashlib,json,shutil
from pathlib import Path
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
SDK=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/runtime-closure-full-shell-r1/sdk')
stage=OWN/'build/gpt01-night004-calendar/service'
source={}
for name in ('lib.rs','ui.rs','cards.rs','gpt01_crud_tests.rs'):
    official=SDK/'apps/calendar/host-service/src'/name
    copied=stage/'src/calendar'/name
    assert copied.read_bytes()==official.read_bytes(),f'Calendar source drift: {name}'
    source[name]=hashlib.sha256(copied.read_bytes()).hexdigest()
shutil.copyfile(HERE/'external_owner_main.rs',stage/'src/external_owner_main.rs')
manifest=stage/'Cargo.toml'
entry='\n[[bin]]\nname="gpt01-night004-external-owner"\npath="src/external_owner_main.rs"\n'
if 'name="gpt01-night004-external-owner"' not in manifest.read_text():manifest.write_text(manifest.read_text()+entry)
print(json.dumps({'service_sources_match_actual_sdk':source,'stage':str(stage),'shared_writes':False}))
