#!/usr/bin/env python3
"""Compact only synthetic probe text; keep production tail definitions byte-exact."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
sys.dont_write_bytecode = True
from test_recovery import function

OWN = Path(__file__).resolve().parent
ROOT = OWN.parents[3]
COMPACTOR = ROOT / 'official_muse/ui_memory/compact_bundle.py'
COMPACTOR_SHA = '2abe13a909dc0d320e65cdb43b6e1dc4f338e4a128f3d965223fd03b72485349'
sha = lambda text: hashlib.sha256(text.encode()).hexdigest()

def significant(text):
    """Compare literal bytes and non-whitespace bytes; not an official tokenizer."""
    chars = []
    literals = []
    i = 0
    while i < len(text):
        if text[i:i+2] == '//':
            end = text.find('\n',i)
            i = len(text) if end < 0 else end
            continue
        if text[i:i+2] == '/*':
            raise ValueError('Block comments are unsupported by the verified compactor')
        if text[i] == '"':
            start = i
            i += 1
            while i < len(text):
                if text[i] == '\\': i += 2
                elif text[i] == '"': i += 1; break
                else: i += 1
            else: raise ValueError('Unterminated literal')
            value = text[start:i]
            literals.append(value)
            chars.append(value)
            continue
        if not text[i].isspace(): chars.append(text[i])
        i += 1
    return ''.join(chars),literals

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True)
    a = p.parse_args()
    expected = json.loads((OWN/'calendar-mail-vm-expectations.json').read_text())
    source = a.source.read_text()
    assert sha(source) == expected['source_sha256'], 'Formal source drift'
    assert hashlib.sha256(COMPACTOR.read_bytes()).hexdigest() == COMPACTOR_SHA, 'Compactor drift'
    readable = (OWN/'calendar_mail_vm_probe.splash').read_text()
    assert sha(readable) == expected['probe_sha256'], 'Readable probe drift'
    marker = '// END VERBATIM PRODUCTION TAIL DEPENDENCIES\n\n'
    assert readable.count(marker) == 1
    split = readable.index(marker) + len(marker)
    production,synthetic = readable[:split],readable[split:]
    assert sha(production) == expected['verbatim_tail_block_sha256']
    with tempfile.TemporaryDirectory(prefix='gpt02-probe-compact-',dir=ROOT/'build') as d:
        folder = Path(d)/'source'
        folder.mkdir()
        (folder/'main.splash').write_text(synthetic)
        out = Path(d)/'compact'
        run = subprocess.run([sys.executable,str(COMPACTOR),'--source',str(folder),'--out',str(out)],check=True,capture_output=True,text=True)
        transform = json.loads(run.stdout)
        compact = production + (out/'main.splash').read_text()
    assert significant(readable) == significant(compact), 'Literal/non-whitespace byte mismatch'
    assert readable.count('\n') == compact.count('\n'), 'Line boundary drift'
    copied = expected['verbatim_production_tail_functions']
    for name,digest in copied.items():
        original = function(source,name)
        assert function(readable,name) == original == function(compact,name)
        assert sha(original) == digest
    artifact = OWN/'calendar_mail_vm_compact.splash'
    artifact.write_text(compact)
    identity = dict(kind='COMPACT_APPEND_PREPARATION_ONLY',vm_status='NOT_EXECUTED',source_sha256=sha(source),
        readable_probe_sha256=sha(readable),compact_probe_sha256=sha(compact),compactor_sha256=COMPACTOR_SHA,
        bytes_before=len(readable.encode()),bytes_after=len(compact.encode()),saved_bytes=len(readable.encode())-len(compact.encode()),
        production_tail_bytes_unchanged=True,production_tail_function_sha256=copied,literal_bytes_equal=True,
        non_whitespace_non_comment_bytes_equal=True,line_boundaries_equal=True,official_tokenizer_executed=False,
        synthetic_transform=transform,expected_checks_unchanged=expected['expected_check_count'],
        runner_change_required=False,host_budget_changed=False,
        boundary='Only the synthetic appended probe is compacted with existing compact_bundle.py. Production prefix and copied tail function bytes stay unchanged. Not a VM result or proof that startup budget is resolved.')
    (OWN/'calendar-mail-vm-compact-identity.json').write_text(json.dumps(identity,indent=2)+'\n')
    print(json.dumps({k:identity[k] for k in ['bytes_before','bytes_after','saved_bytes','compact_probe_sha256','expected_checks_unchanged','vm_status']}))

if __name__ == '__main__': main()
