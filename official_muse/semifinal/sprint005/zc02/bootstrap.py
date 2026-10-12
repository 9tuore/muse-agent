#!/usr/bin/env python3
"""Create only a brand-new synthetic root; no profile or credential import."""
import argparse, os, subprocess
from pathlib import Path
from fixture_scope import PROFILE_MARKER,OWNER_MARKER,atomic_json,digest

def bootstrap(root):
    root=Path(root).absolute()
    if root.exists() or root.is_symlink(): raise ValueError('New root required; never replace an existing profile')
    parent=root.parent.resolve(strict=True)
    if root.parent != parent: raise ValueError('Canonical parent required')
    root.mkdir(mode=0o700)
    (root/'apps/.host').mkdir(parents=True)
    (root/'FIXTURE_ONLY').write_bytes(PROFILE_MARKER)
    (root/'apps/.host/FIXTURE_ONLY').write_bytes(OWNER_MARKER)
    private=root/'private';private.mkdir(mode=0o700)
    public=root/'public';public.mkdir()
    ca='''[req]
distinguished_name=dn
x509_extensions=ca
prompt=no
[dn]
CN=SPRINT005 SYNTHETIC TEST CA
[ca]
basicConstraints=critical,CA:TRUE
keyUsage=critical,keyCertSign,cRLSign
subjectKeyIdentifier=hash
'''
    leaf='''[req]
distinguished_name=dn
prompt=no
[dn]
CN=127.0.0.1
[leaf]
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=IP:127.0.0.1,DNS:localhost
'''
    (private/'ca.cnf').write_text(ca);(private/'server.cnf').write_text(leaf)
    commands=[['req','-x509','-newkey','rsa:2048','-nodes','-days','2','-config',str(private/'ca.cnf'),'-keyout',str(private/'ca.key'),'-out',str(public/'mail-fixture-ca.pem')],
      ['req','-new','-newkey','rsa:2048','-nodes','-config',str(private/'server.cnf'),'-keyout',str(private/'server.key'),'-out',str(private/'server.csr')],
      ['x509','-req','-in',str(private/'server.csr'),'-CA',str(public/'mail-fixture-ca.pem'),'-CAkey',str(private/'ca.key'),'-set_serial','5005','-days','2','-extfile',str(private/'server.cnf'),'-extensions','leaf','-out',str(public/'server.pem')],
      ['x509','-in',str(public/'mail-fixture-ca.pem'),'-outform','DER','-out',str(public/'mail-fixture-ca.der')]]
    for args in commands:
        result=subprocess.run(['openssl',*args],capture_output=True,preexec_fn=lambda:os.umask(0o077))
        if result.returncode: raise RuntimeError('Synthetic certificate generation failed; no key material printed')
    for name in ('ca.key','server.key'):(private/name).chmod(0o600)
    atomic_json(root/'mail-fixture.json',{'protocol':'SPRINT005_MAIL_TLS_FIXTURE_V1','ca_sha256':digest((public/'mail-fixture-ca.der').read_bytes())})
    atomic_json(root/'launch-environment.json',{'MUSE_INTEGRATED_STATE':str(root),'OCTOSENSE_MAIL_VAULT':'file','OCTOSENSE_LLM_VAULT':'file','OCTOS_APP_CORE_DIR':str(root/'kernel/.octos')})
    return root

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    print(bootstrap(a.root))
