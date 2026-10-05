#!/usr/bin/env python3
from pathlib import Path
import sys, json, subprocess, tarfile, zipfile, time
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[4]
sys.path.insert(0,str(ROOT/'official_muse/rc/packaging'))
import package_solid_envelope as e
from package_lean_portable import inventory,sha,verify_and_extract_zip

local=OUT/'.local-state'/('envelope-synthetic-'+str(time.time_ns()));local.mkdir(parents=True)
result={'kind':'SYNTHETIC_PACKAGING_NOT_PRODUCT','cases':[],'native_GUI_started':False}
try:
 stage=local/'内容 中文';stage.mkdir();(stage/'中文').mkdir()
 (stage/'中文/源码.txt').write_text('synthetic source\n'*100)
 (stage/'exec.sh').write_text('#!/bin/sh\necho synthetic\n');(stage/'exec.sh').chmod(0o755)
 (stage/'link').symlink_to('中文/源码.txt')
 expected=inventory(stage);outer=local/'信封 中文';outer.mkdir();payload=outer/'内容.tar.xz'
 e.write_payload(stage,payload,expected,preset=6)
 e.validate_payload(payload,stage.name,expected)
 extracted=local/'system-tar';extracted.mkdir()
 subprocess.run(['/usr/bin/tar','-xJf',str(payload),'-C',str(extracted)],check=True,capture_output=True)
 assert inventory(extracted/stage.name)==expected
 result['cases'].append({'case':'full payload native tar SHA modes Unicode exec symlink','status':'PASS'})
 command=outer/'00-展开并启动.command';command.write_text(e.bootstrap(payload.name,'0'*64,stage.name,'Muse.app'));command.chmod(0o755)
 subprocess.run(['/bin/zsh','-n',str(command)],check=True,capture_output=True)
 p=subprocess.run(['/bin/zsh',str(command),'--check-only'],capture_output=True,text=True)
 assert p.returncode and not (outer/stage.name).exists() and 'SHA256' in p.stderr
 result['cases'].append({'case':'corrupted checksum stops before extraction/open','status':'PASS_REJECTED'})
 command.write_text(e.bootstrap(payload.name,sha(payload),stage.name,'Muse.app'))
 p=subprocess.run(['/bin/zsh',str(command),'--check-only'],capture_output=True,text=True)
 assert p.returncode and inventory(outer/stage.name)==expected and not (outer/'.muse-unpack-complete').exists()
 assert '没有启动' in p.stderr
 result['cases'].append({'case':'real bootstrap restores bytes but missing synthetic app rejects without success/open','status':'PASS_REJECTED_NOT_PRODUCT'})
 # Restore a fresh top-level envelope containing only ordinary files for STORED ZIP.
 ready=local/'stored';ready.mkdir();(ready/'exec.sh').write_bytes((stage/'exec.sh').read_bytes());(ready/'exec.sh').chmod(0o755)
 (ready/'Unicode中文.txt').write_text('synthetic')
 zip_expected=inventory(ready);archive=local/'stored.zip';e.write_stored_zip(ready,archive,zip_expected)
 with zipfile.ZipFile(archive) as z:assert z.testzip() is None and all(i.compress_type==zipfile.ZIP_STORED for i in z.infolist())
 dest=local/'restored-stored';dest.mkdir();verify_and_extract_zip(archive,ready.name,zip_expected,dest)
 result['cases'].append({'case':'STORED ZIP CRC allowlist SHA modes','status':'PASS'})
 for label,name,type_,link in [('traversal',stage.name+'/../escape',tarfile.REGTYPE,''),('escaping symlink',stage.name+'/link',tarfile.SYMTYPE,'../../escape')]:
  bad=local/(label+'.tar.xz')
  with tarfile.open(bad,'x:xz') as t:
   m=tarfile.TarInfo(name);m.type=type_;m.mode=expected['link']['mode'] if link else 0o644;m.linkname=link;t.addfile(m)
  try:e.validate_payload(bad,stage.name,expected)
  except RuntimeError:result['cases'].append({'case':label,'status':'PASS_REJECTED'})
  else:raise AssertionError('Unsafe tar accepted')
 result['status']='PASS_SYNTHETIC_ONLY'
except Exception as error:
 result['status']='FAIL_RETAINED';result['error_type']=type(error).__name__;raise
finally:
 result['tool_sha256']=sha(Path(e.__file__))
 (OUT/('ENVELOPE_TEST-'+local.name+'.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 (OUT/'ENVELOPE_TEST.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(result,ensure_ascii=False,indent=2))
