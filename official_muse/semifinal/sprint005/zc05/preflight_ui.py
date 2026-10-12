#!/usr/bin/env python3
"""One preflight native UI step after the caller has viewed its source PNG."""
import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
SHARED = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
sys.path.insert(0, str(SHARED / 'official_muse/phase2/tests'))
from ua_gui import GUIEvidence, now, require, widgets_digest

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--handoff', required=True)
parser.add_argument('--attempt', required=True)
parser.add_argument('--image', required=True)
parser.add_argument('--observed', required=True)
parser.add_argument('--key', required=True)
parser.add_argument('--pane', default='card')
parser.add_argument('--next', required=True)
parser.add_argument('action', choices=['click', 'type', 'scroll'])
parser.add_argument('--value', default='')
parser.add_argument('--dy', type=int, default=80)
args = parser.parse_args()
g = GUIEvidence(args.handoff, args.attempt)
require(g.identity['acceptance_phase'] == 'PRE_FLIGHT_BUG_DISCOVERY_NOT_THREE_ROUND_ACCEPTANCE', 'Preflight-only helper')
template = g.path / Path(args.image).with_suffix('.visual-template.json').name
proof = json.loads(template.read_text())
rows = json.loads(sorted(g.path.glob('snap-*.json'))[-1].read_text())['s']
require(widgets_digest(rows) == proof['widgets_sha256'], 'Source capture snapshot differs; capture/view current UI first')
controls = [w for w in rows if w.get('ty') == ('TextInput' if args.action == 'type' else 'Button')
            and (w.get('i') == args.key or w.get('t') == args.key)]
if args.action != 'scroll':
    require(len(controls) == 1, 'Caller must select one exact visible control')
    panes = [w for w in rows if w.get('i') == args.pane and w.get('w') == controls[0]['w']]
    require(len(panes) == 1, 'Missing exact corresponding pane')
    proof['controls'] = [{'key': args.key, 'rect': controls[0]['r'], 'pane_rect': panes[0]['r'], 'fully_visible': True}]
proof.update(inspected_at_utc=now(), observed=args.observed)
proof_path = g.path / Path(args.image).with_suffix('.visual-inspected.json').name
proof_path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
if args.action == 'click':
    g.click(args.key, args.pane, proof_path)
elif args.action == 'type':
    g.type(args.key, args.value, args.pane, proof_path)
else:
    g._journal({'event': 'VIEWED_NATIVE_SCROLL_PANE', 'image': args.image, 'observed': args.observed})
    g.scroll(args.key, args.dy)
print(g.capture(args.next))
for w in json.loads(sorted(g.path.glob('snap-*.json'))[-1].read_text())['s']:
    if w.get('ty') == 'TextInput' or w.get('ty') == 'Button' and w.get('t') == args.key:
        print({k:v for k,v in w.items() if k in ('i','ty','r','w','enabled','val') or k == 't' and w.get('ty') == 'Button'})
