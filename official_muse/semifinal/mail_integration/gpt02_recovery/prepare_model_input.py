#!/usr/bin/env python3
"""Prepare a source-pinned model.complete proposal; never edit formal main."""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import sys
sys.dont_write_bytecode = True
from test_recovery import function

OWN = Path(__file__).resolve().parent
BASE = '0c7f9812cf7319cf5120557ddef7caacfe49326c0dcbc5759e689fcac38ce9eb'
SDK = '79ce9ed937208d8df1dca27110001c7af1c0bc365a4a605c1154b57053d7d2fe'
sha = lambda text: hashlib.sha256(text.encode()).hexdigest()

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--sdk-contract', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    old = a.source.read_text()
    sdk = a.sdk_contract.read_text()
    assert sha(old) == BASE, 'source drift: prepare again by named function'
    assert sha(sdk) == SDK, 'SDK contract drift'
    new = old
    replacements = {'muse_model_request': [
        ('            payload.messages.push({role: "user" content: turn})\n',
         '            payload.messages.push({role: "user" content: turn})\n'
         '            payload.input = {messages: payload.messages}\n'),
        ('        host.request("model.complete",payload,fn(r){\n',
         '        // The official service accepts input data, not top-level chat messages.\n'
         '        let model_payload = {task: payload.task input: payload.input schema: payload.schema}\n'
         '        if gm_has(payload,"class") { model_payload.class = payload.class }\n'
         '        if gm_has(payload,"allow_urls") { model_payload.allow_urls = payload.allow_urls }\n'
         '        host.request("model.complete",model_payload,fn(r){\n'),
    ]}
    for name, changes in replacements.items():
        original = function(old, name)
        changed = original
        for before, after in changes:
            assert changed.count(before) == 1
            changed = changed.replace(before, after)
        new = new.replace(original, changed, 1)
    names = re.findall(r'^fn (\w+)\(', old, re.M)
    untouched = [name for name in names if name not in replacements]
    assert all(function(old, name) == function(new, name) for name in untouched)
    patch = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True),
        fromfile='a/official_muse/app/source/main.splash',
        tofile='b/official_muse/app/source/main.splash', n=3))
    (OWN/'model-input.patch').write_text(patch)
    identity = dict(source_sha256=BASE, expected_source_sha256=sha(new),
        patch_sha256=sha(patch), sdk_contract_sha256=SDK,
        base_central_head='88e5ba28911bbd066e3dc448243d5fbb8a8aa3ce',
        changed_functions=list(replacements), unchanged_function_count=len(untouched),
        applied_to_formal_source=False,
        boundary='Move existing chat history/current context into input.messages. No SDK, identity, usage or policy changes.')
    (OWN/'model-input-identity.json').write_text(json.dumps(identity, indent=2)+'\n')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(new)
    print(json.dumps(identity))

if __name__ == '__main__':
    main()
