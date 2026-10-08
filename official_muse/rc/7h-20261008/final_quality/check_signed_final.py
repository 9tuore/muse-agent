#!/usr/bin/env python3
"""Independent signed gate: exact Root bundle copy, no stamp or signing."""
import hashlib,json,shutil,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=ROOT/'official_muse/app/build/ui-memory-20261003/7h-live-candidate-r7/bundle'
out=Q/'official-signed-rc15-r4';assert not out.exists();out.mkdir()
b=out/'bundle';shutil.copytree(source,b)
assert sha(b/'main.splash')=='cef7d576b2de31e5c22a813e70e68370ff0ddd043ef1bbcd57acae75eb81b546'
cli=Q.parent/'quality/tools/hub';binding=json.loads((Q.parent/'quality/OFFICIAL_CLI_BUILD.json').read_text());assert sha(cli)==binding['binary_sha256']
identity=(Q.parent/'source-component-r1/local-publisher-public.txt').read_text().strip();assert identity and '\n' not in identity
before={p.relative_to(b).as_posix():sha(p) for p in b.rglob('*') if p.is_file()}
record={'source_sha256':sha(b/'main.splash'),'source_manifest_sha256':sha(source/'manifest.json'),'cli_sha256':sha(cli),'version':json.loads((b/'manifest.json').read_text())['version'],'status':'FAIL','scope':'Official independent check/scan of exact signed Root bundle; no stamp/sign/mutation/publication. Not upstream Calendar host extension acceptance.'}
for label,args in [('CHECK',['check',str(b),'--publisher-key',identity]),('SCAN',['scan',str(b),'--packet',str(out/'SCAN_PACKET.json'),'--publisher-key',identity])]:
 proc=subprocess.run([str(cli),*args],text=True,capture_output=True);(out/(label+'.txt')).write_text(proc.stdout+proc.stderr);record[label.lower()+'_exit']=proc.returncode
 if proc.returncode:break
else:record['status']='PASS'
record['bundle_unchanged']=before=={p.relative_to(b).as_posix():sha(p) for p in b.rglob('*') if p.is_file()}
(out/'report.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False));assert record['status']=='PASS' and record['bundle_unchanged']
