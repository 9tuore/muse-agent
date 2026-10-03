#!/usr/bin/env python3
"""Copy a release bundle and trim comments/spacing, preserving lines and strings."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

p = argparse.ArgumentParser()
p.add_argument('--source', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
source = (a.source / 'main.splash').read_text()
# This narrow transform refuses raw multiline literals instead of trimming their contents.
quoted = escaped = False
for line in source.splitlines(True):
    i = 0
    while i < len(line):
        c = line[i]
        if not quoted and line[i:i+2] == '//':
            break
        if not quoted and line[i:i+2] == '/*':
            raise ValueError('Block comment metadata is unsupported; compacting is refused.')
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        i += 1
    if quoted:
        raise ValueError('Multiline literal: source is preserved; compacting is refused.')
shutil.copytree(a.source, a.out)
lines = []
for line in source.splitlines(True):
    line = line.lstrip(' \t')
    chars = []
    quoted = escaped = False
    i = 0
    while i < len(line):
        c = line[i]
        if not quoted and line[i:i+2] == '//':
            if line.endswith('\n'):
                chars.append('\n')
            break
        if quoted:
            if escaped:
                escaped = False
            elif c == '\\':
                escaped = True
            elif c == '"':
                quoted = False
        elif c == '"':
            quoted = True
        elif c in ' \t':
            end = i + 1
            while end < len(line) and line[end] in ' \t':
                end += 1
            before = chars[-1] if chars else ''
            after = line[end] if end < len(line) else ''
            operators = '=<>+*-!/|.&:'
            operator_edge = (before in operators or after in operators) and not (
                before in operators and after in operators)
            if (before == '-' and after.isdigit()) or (before.isdigit() and after == '.') or (before == '.' and after.isdigit()):
                operator_edge = False
            if (before in '(){}[],;' or after in '(){}[],;' or operator_edge):
                i = end
                continue
        chars.append(c)
        i += 1
    lines.append(''.join(chars))
compact = ''.join(lines)
(a.out / 'main.splash').write_text(compact)
print(json.dumps({'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                  'artifact_sha256': hashlib.sha256(compact.encode()).hexdigest(),
                  'bytes_before': len(source.encode()), 'bytes_after': len(compact.encode()),
                  'transform': 'Remove line comments, indentation and spacing at delimiters outside strings; line endings and strings preserved.'}))
