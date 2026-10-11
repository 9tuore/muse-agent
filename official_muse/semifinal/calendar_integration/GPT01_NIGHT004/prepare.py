from pathlib import Path
import hashlib,json,shutil,subprocess
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
CENTRAL=Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
SDK=CENTRAL/'build/runtime-closure-full-shell-r1/sdk'
STAGE=OWN/'build/gpt01-night004-calendar'
STAGE.mkdir(parents=True,exist_ok=False)
service=STAGE/'service'
shutil.copytree(SDK/'apps/calendar/host-service/src',service/'src/calendar')
shutil.copytree(SDK/'apps/calendar/host-service/resources',service/'src/resources')
shutil.copyfile(HERE/'service_adapter.rs',service/'src/lib.rs')
shutil.copyfile(HERE/'owner_main.rs',service/'src/main.rs')
(service/'Cargo.toml').write_text('[package]\nname="gpt01-night004-calendar"\nversion="0.0.0"\nedition="2021"\n[dependencies]\nserde={version="=1.0.229",features=["derive"]}\nserde_json="=1.0.151"\nchrono={version="=0.4.45",features=["serde"]}\nchrono-tz="=0.10.4"\n')
data={'central_baseline':json.loads((CENTRAL/'build/night-004/baseline/identity.json').read_text()),'source_sdk':str(SDK),'stage':str(STAGE),'source_sha256':{str(p.relative_to(service/'src')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (service/'src/calendar').glob('*.rs')},'authorization':'Synthetic fixture only; no real person consent','shared_writes':False,'gui':False}
(HERE/'BASELINE.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'stage':str(STAGE),'central_head':data['central_baseline']['head']}))
