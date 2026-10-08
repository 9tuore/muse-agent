#!/usr/bin/env python3
"""Stamp/check/scan exact copied candidate with verified upstream source CLI."""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
Q=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--bundle',type=Path,required=True);p.add_argument('--sha',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();assert sha(a.bundle/'main.splash')==a.sha
out=a.out.resolve();assert out.is_relative_to(Q) and not out.exists();out.mkdir(parents=True);b=out/'bundle';shutil.copytree(a.bundle,b)
cli=Q.parent/'quality/tools/hub';binding=json.loads((Q.parent/'quality/OFFICIAL_CLI_BUILD.json').read_text());assert sha(cli)==binding['binary_sha256'];record={'official_source_commit':binding['commit'],'cli_sha256':sha(cli),'source_sha256':a.sha,'input_manifest_sha256':sha(a.bundle/'manifest.json'),'version':json.loads((b/'manifest.json').read_text())['version'],'status':'FAIL','publication':'NOT_PERFORMED','scope':'Official CLI structural/admission check and review packet; not publisher review, Shell execution or host-extension upstream acceptance.'}
for name,args in [('STAMP',['stamp',str(b)]),('CHECK',['check',str(b),'--allow-unsigned']),('SCAN',['scan',str(b),'--packet',str(out/'SCAN_PACKET.json')])]:
 proc=subprocess.run([str(cli),*args],text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/(name+'.txt')).write_text(proc.stdout);record[name.lower()+'_exit']=proc.returncode
 if proc.returncode:break
else:record['status']='PASS'
record['stamped_manifest_sha256']=sha(b/'manifest.json');record['bundle_blake3']=json.loads((b/'manifest.json').read_text())['integrity']['bundle_blake3'];(out/'report.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False));assert record['status']=='PASS'
