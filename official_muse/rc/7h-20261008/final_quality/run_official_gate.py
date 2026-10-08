#!/usr/bin/env python3
"""Stamp/check/scan exact copied candidate with verified upstream source CLI."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--sha',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--structural-unsigned',action='store_true');a=p.parse_args();assert sha(a.bundle/'main.splash')==a.sha
out=a.out.resolve();assert out.is_relative_to(Q) and not out.exists();out.mkdir(parents=True);b=out/'bundle';shutil.copytree(a.bundle,b)
if a.structural_unsigned:
 manifest=json.loads((b/'manifest.json').read_text());manifest.get('integrity',{}).pop('signature',None);(b/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
cli=Q.parent/'quality/tools/hub';binding=json.loads((Q.parent/'quality/OFFICIAL_CLI_BUILD.json').read_text());assert sha(cli)==binding['binary_sha256'];record={'official_source_commit':binding['commit'],'cli_sha256':sha(cli),'source_sha256':a.sha,'input_manifest_sha256':sha(a.bundle/'manifest.json'),'version':json.loads((b/'manifest.json').read_text())['version'],'status':'FAIL','publication':'NOT_PERFORMED','scope':'Official CLI structural/admission check and review packet; not publisher review, Shell execution or host-extension upstream acceptance.'}
publisher=Path('/Users/mima0000/.codex/worktrees/muse-official-migration/Agent APP黑客松/official_muse/app/build/keys/publisher.key')
identity='muse-local-rehearsal='+subprocess.check_output([str(cli),'pubkey',str(publisher)],text=True).strip()
check_args=['--allow-unsigned'] if a.structural_unsigned else ['--publisher-key',identity]
scan_args=[] if a.structural_unsigned else ['--publisher-key',identity]
record['signature_scope']='UNSIGNED_COPY_STRUCTURAL_ONLY' if a.structural_unsigned else 'SIGNED_MANIFEST_AFTER_OFFICIAL_STAMP'
for name,args in [('STAMP',['stamp',str(b)]),('CHECK',['check',str(b),*check_args]),('SCAN',['scan',str(b),'--packet',str(out/'SCAN_PACKET.json'),*scan_args])]:
 proc=subprocess.run([str(cli),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/(name+'.txt')).write_text(proc.stdout);record[name.lower()+'_exit']=proc.returncode
 if proc.returncode:break
else:record['status']='PASS'
record['stamped_manifest_sha256']=sha(b/'manifest.json');record['bundle_blake3']=json.loads((b/'manifest.json').read_text())['integrity']['bundle_blake3'];(out/'report.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False));assert record['status']=='PASS'
