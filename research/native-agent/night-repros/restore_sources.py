"""Restore only hash-pinned small source inputs, never a complete SDK or runtime."""
from pathlib import Path
import hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'research/native-agent'
inputs=[]
for item in json.loads((OUT/'night-policy-sources.json').read_text()):
    inputs.append((item,ROOT/'.local-state/night-policy'/item['path']))
for item in json.loads((OUT/'upstream-sources.json').read_text()):
    inputs.append((item,ROOT/'.local-state/native-agent-upstream'/item['repository']/item['path']))
for item in json.loads((OUT/'night-calendar-sources.json').read_text()):
    inputs.append((item,ROOT/'.local-state/native-agent-upstream/OctoSense'/item['path']))
for item,path in inputs:
    data=path.read_bytes() if path.exists() else urllib.request.urlopen(item['url'],timeout=30).read()
    assert hashlib.sha256(data).hexdigest()==item['sha256'],path
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['blob'],path
    if not path.exists():
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
print(f'{len(inputs)} pinned input records checked/restored; no production writes')
