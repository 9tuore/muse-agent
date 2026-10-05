#!/usr/bin/env python3
"""Static byte comparison only; does not execute fixtures or runtime services."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = 'official_muse/app/source/main.splash'


def functions(source):
    out = {}
    for match in re.finditer(r'^fn (\w+)\(', source, re.M):
        start = source.index('{', match.end())
        depth = 0
        quote = False
        escape = False
        comment = False
        for i in range(start, len(source)):
            ch = source[i]
            if comment:
                if ch == '\n':
                    comment = False
                continue
            if quote:
                if escape:
                    escape = False
                elif ch == '\\':
                    escape = True
                elif ch == '"':
                    quote = False
                continue
            if ch == '"':
                quote = True
            elif source[i:i+2] == '//':
                comment = True
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    out[match[1]] = hashlib.sha256(source[match.start():i+1].encode()).hexdigest()
                    break
        else:
            raise ValueError('Unterminated top-level function')
    return out


def audit():
    current = subprocess.check_output(['git', 'show', 'e0eb5d82:'+SOURCE], cwd=ROOT).decode()
    new = functions(current)
    rows = []
    for ref in ['617851a8', '89bfd399', '52289f27']:
        old_source = subprocess.check_output(['git', 'show', ref+':'+SOURCE], cwd=ROOT).decode()
        old = functions(old_source)
        shared = sorted(old.keys() & new.keys())
        rows.append({'source_commit': ref, 'source_sha256': hashlib.sha256(old_source.encode()).hexdigest(),
                     'compared_functions': len(shared),
                     'unchanged': [{'function': k, 'sha256': new[k]} for k in shared if old[k] == new[k]],
                     'changed': [k for k in shared if old[k] != new[k]],
                     'missing_or_added': sorted(old.keys() ^ new.keys())})
    return {'kind': 'STATIC_FUNCTION_BYTES_REUSE_SUPPORT_NOT_NEW_TEST',
            'target_commit': 'e0eb5d82', 'target_source_sha256': hashlib.sha256(current.encode()).hexdigest(),
            'comparisons': rows,
            'limits': ['Only top-level function bytes; globals, UI callback bindings, transport, Host and data are not proven equivalent.',
                       'Supports reuse of unchanged function assertions with their original version; never converts an old whole-suite PASS into a final run.',
                       'Changed startup/approval/UI paths require their current real evidence; no new fixture was run.']}


if __name__ == '__main__':
    print(json.dumps(audit(), ensure_ascii=False, indent=2))
