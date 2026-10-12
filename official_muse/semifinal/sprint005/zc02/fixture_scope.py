"""Exact synthetic scope; never accept a production/legacy fixture implicitly."""
import hashlib, json
from pathlib import Path

PROFILE_MARKER = b'SPRINT005 isolated SDK GUI fixture only\n'
OWNER_MARKER = b'SPRINT005 synthetic Calendar/Mail owner fixture only\n'
ACCOUNT_SUFFIX = '@sprint005.example.invalid'
ACCOUNTS = ['gui-reader'+ACCOUNT_SUFFIX, 'gui-alt'+ACCOUNT_SUFFIX, 'receiver'+ACCOUNT_SUFFIX]
TEST_INPUT = 'SPRINT005-SYNTHETIC-ONLY'

def scope(root):
    requested = Path(root).absolute()
    resolved = requested.resolve(strict=True)
    if requested != resolved or not resolved.is_dir(): raise ValueError('Canonical nonsymlink fixture root required')
    for rel, expected in [('FIXTURE_ONLY',PROFILE_MARKER),('apps/.host/FIXTURE_ONLY',OWNER_MARKER)]:
        p = resolved/rel
        for parent in [p,*p.parents]:
            if parent == resolved.parent: break
            if parent.is_symlink(): raise ValueError('Fixture symlink refused')
        if p.read_bytes() != expected: raise ValueError('Exact SPRINT005 double markers required')
    return resolved

def atomic_json(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    tmp.replace(path)

def digest(raw): return hashlib.sha256(raw).hexdigest()
