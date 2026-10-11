#!/usr/bin/env python3
"""Prepare a SHA-bound patch in an owned SDK source snapshot and extracted Rust fixture."""
from pathlib import Path
import argparse,difflib,hashlib,json,re
P=Path(__file__).resolve().parent
ROOT=P.parents[4]
sha=lambda b:hashlib.sha256(b).hexdigest()
def function(s,name):
    m=re.search(r'(?:pub )?fn '+name+r'\(',s)
    if not m: raise ValueError(name)
    start=m.start(); brace=s.index('{',m.end()); depth=1; end=brace+1
    while depth:
        depth+=(s[end]=='{')-(s[end]=='}');end+=1
    return s[start:end]
a=argparse.ArgumentParser();a.add_argument('--sdk',type=Path,required=True);a.add_argument('--out',type=Path,required=True);v=a.parse_args()
out=v.out.resolve();out.relative_to(ROOT/'build');out.mkdir(parents=True,exist_ok=False)
rel='crates/shell/src/app_storage/'
original=(v.sdk/(rel+'lifecycle.rs')).read_bytes()
assert sha(original)=='4f419e46c142f927ff6163595db9b1f5615c5d8431949c18715b319f460e7f3f','lifecycle source drift'
s=original.decode();old='    if storage.is_signed_out(app, Some(account)) {\n';new='    let lifecycle_account = if storage.spec(app).accounts { Some(account) } else { None };\n    if storage.is_signed_out(app, lifecycle_account) {\n'
assert s.count(old)==1
patched=s.replace(old,new)
assert function(s,'mail_claim_allowed')==function(patched,'mail_claim_allowed')
test_original=(v.sdk/(rel+'lifecycle_tests.rs')).read_bytes();t=test_original.decode()
for label,app in [('mail-send-claim','os.mail'),('public-mail-send-claim','sample.mail')]:
    marker=f'    let home = Scratch::new("{label}");\n    let host = storage(&home.0);\n'
    assert t.count(marker)==1
    t=t.replace(marker,marker+f'    host.set_spec("{app}", StorageSpec {{ accounts: true, ..Default::default() }});\n')
t+=(P/'native-tests.rs').read_text()
identity={'kind':'owned SDK targeted source snapshot; production and native-test patch','files':[],'central_sdk_modified':False,'harness':'actual source functions; storage/layout/admission/grants/active_account adapters; no Shell runtime or persistence'}
patch=''
for name,before,after in [('lifecycle.rs',original,patched.encode()),('lifecycle_tests.rs',test_original,t.encode())]:
    path=rel+name;dest=out/'sdk'/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(after)
    patch+=''.join(difflib.unified_diff(before.decode().splitlines(True),after.decode().splitlines(True),fromfile='a/'+path,tofile='b/'+path,n=0))
    identity['files'].append({'path':path,'before_sha256':sha(before),'after_sha256':sha(after)})
(P/'lifecycle-account.patch').write_text(patch)
mod=(v.sdk/(rel+'mod.rs')).read_text()
assert sha(mod.encode())=='c0864f33290faf309c0595e7fe69828c30b34712c78204ead3bde021f4f33c61','Storage source drift'
methods='\n'.join(function(mod,n) for n in ['key','sign_out','sign_in','is_signed_out','installed'])
identity['storage_source_sha256']=sha(mod.encode())
for phase,lifecycle in [('before',s),('after',patched)]:
    crate=out/phase; (crate/'src').mkdir(parents=True)
    rust=(P/'fixture.rs').read_text().replace('// INSERT_SOURCE_METHODS',methods).replace('// INSERT_SOURCE_GUARDS','\n'.join(function(lifecycle,n) for n in ['mail_claim_allowed','mail_account_claim_allowed']))
    (crate/'src/lib.rs').write_text(rust)
    (crate/'Cargo.toml').write_text('[package]\nname="mail-lifecycle-key-fixture"\nversion="0.1.0"\nedition="2021"\n[workspace]\n')
    identity[phase+'_fixture_sha256']=sha(rust.encode())
(P/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
print(json.dumps(identity,indent=2))
