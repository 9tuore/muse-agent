#!/usr/bin/env python3
"""Central use only: run a compiled helper test with per-child outer timeout."""
import argparse,hashlib,json,os,subprocess,tempfile
from pathlib import Path
OWN=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--test-binary',type=Path,required=True)
p.add_argument('--sha256',required=True,help='Expected central test-binary identity')
p.add_argument('--timeout',type=float,default=3)
a=p.parse_args()
binary=a.test_binary.resolve(strict=True)
assert hashlib.sha256(binary.read_bytes()).hexdigest()==a.sha256
assert 0<a.timeout<=10
listed=subprocess.run([str(binary),'--list'],capture_output=True,text=True,timeout=a.timeout,check=True)
tests=[line.removesuffix(': test') for line in listed.stdout.splitlines() if line.endswith('digest_special_file_tests::special_file_child: test')]
assert len(tests)==1, 'Exact proposed test must be compiled in before invoking'
records=[]
with tempfile.TemporaryDirectory(prefix='digest-special-',dir=OWN) as folder:
    root=Path(folder); jail=root/'jail';jail.mkdir()
    outside=root/'outside.txt';outside.write_text('synthetic-only')
    fifo=jail/'fifo';os.mkfifo(fifo)
    directory=jail/'directory';directory.mkdir()
    link=jail/'symlink';link.symlink_to(outside)
    for kind,path in [('fifo',fifo),('directory',directory),('symlink',link)]:
        env=dict(os.environ,MUSE_DIGEST_SPECIAL_PATH=str(path))
        try:
            result=subprocess.run([str(binary),tests[0],'--exact','--test-threads=1'],env=env,capture_output=True,text=True,timeout=a.timeout)
            records.append({'case':kind,'exit_code':result.returncode,'status':'PASS_REJECTED' if result.returncode==0 else 'FAIL'})
        except subprocess.TimeoutExpired:
            records.append({'case':kind,'status':'FAIL_TIMEOUT','timeout_seconds':a.timeout})
report={'status':'PASS_COMPONENT' if all(r['status']=='PASS_REJECTED' for r in records) else 'FAIL_COMPONENT','binary_sha256':a.sha256,'cases':records,'boundary':'Compiled file_sha256 helper subprocess, not a VM/jail/GUI/Memory/native-Mail acceptance.'}
print(json.dumps(report,indent=2))
raise SystemExit(0 if report['status']=='PASS_COMPONENT' else 1)
