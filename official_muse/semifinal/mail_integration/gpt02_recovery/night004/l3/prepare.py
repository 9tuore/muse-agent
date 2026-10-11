#!/usr/bin/env python3
"""Extract exact frozen production call closure for the real CLI Splash VM."""
import argparse, hashlib, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[5]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'official_muse/prelim/tests/calendar_sync'))
from run import functions_in

p = argparse.ArgumentParser()
p.add_argument('--source', type=Path, required=True)
p.add_argument('--source-sha', required=True)
p.add_argument('--probe', type=Path, nargs='+', default=[HERE / 'mail_probe.splash'])
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
sha = lambda b: hashlib.sha256(b).hexdigest()
source = a.source.read_text()
assert sha(source.encode()) == a.source_sha, 'frozen source identity mismatch'
out = a.out.resolve(); out.relative_to(ROOT / 'build'); out.mkdir(parents=True, exist_ok=False)
original = functions_in(source)
probe = '\n'.join(path.read_text() for path in a.probe)
adapters = {
    'redraw': 'fn redraw(){}', 'mail_redraw': 'fn mail_redraw(){}',
    'set_page': 'fn set_page(next){page=next}', 'ac_refresh': 'fn ac_refresh(){}',
    'ui_layout_save': 'fn ui_layout_save(){}',
    'storage_write': 'fn storage_write(path,data){return fixture_io("write",{path:path data:data})}',
    'storage_read': 'fn storage_read(path){return fixture_io("read",{path:path})}',
}
calls = lambda text: set(re.findall(r'(?<!\.)\b([A-Za-z_][A-Za-z_0-9]*)\s*\(', text)) & set(original)
selected = calls(probe)
while True:
    expanded = set(selected)
    for name in selected - set(adapters): expanded |= calls(original[name])
    if expanded == selected: break
    selected = expanded

globals = {}
for m in re.finditer(r'^let ([A-Za-z_][A-Za-z_0-9]*)\s*=', source, re.M):
    pos, depth, quoted, escaped = m.end(), 0, False, False
    while pos < len(source):
        c = source[pos]
        if quoted:
            if escaped: escaped = False
            elif c == '\\': escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c in '{[(': depth += 1
        elif c in '}])': depth -= 1
        elif c == '\n' and depth == 0: break
        pos += 1
    globals[m[1]] = source[m.start():pos]

texts = {n: adapters.get(n, original[n]).replace('host.request(', 'fixture_transport(') for n in selected}
body = '\n'.join(texts.values()) + '\n' + probe
words = lambda text: set(re.findall(r'\b[A-Za-z_][A-Za-z_0-9]*\b', text)) & set(globals) - {'ui'}
wanted = words(body)
while True:
    expanded = wanted | words('\n'.join(globals[n] for n in wanted))
    if expanded == wanted: break
    wanted = expanded
ordered = sorted(selected, key=lambda n: source.index(original[n]))
ordered_globals = sorted(wanted, key=lambda n: source.index(globals[n]))
for name in selected - set(adapters):
    assert texts[name].replace('fixture_transport(', 'host.request(') == original[name]
prepared = (HERE/'boundaries.splash').read_text() + '\n' + '\n'.join(globals[n] for n in ordered_globals)
prepared += '\n' + '\n'.join(texts[n] for n in ordered) + '\n' + probe
(out/'executed.splash').write_text(prepared)
(out/'frozen-main.splash').write_text(source)
report = dict(source_sha256=a.source_sha, executed_sha256=sha(prepared.encode()),
              probe_sha256=sha(probe.encode()), adapters=sorted(selected & set(adapters)),
              production_function_sha256={n:sha(original[n].encode()) for n in ordered},
              production_global_sha256={n:sha(globals[n].encode()) for n in ordered_globals},
              all_other_functions_byte_equal_after_transport_normalization=True,
              boundary='Real CLI VM; IO/UI/timer/clock/approval are explicit fixture boundaries. No Kernel receipts fabricated.')
(out/'identity.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
print(json.dumps(dict(functions=len(selected), globals=len(wanted), source_sha256=a.source_sha)))
