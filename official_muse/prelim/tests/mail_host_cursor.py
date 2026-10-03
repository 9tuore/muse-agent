#!/usr/bin/env python3
"""Read-only source evidence and logic counterexamples; no production Rust execution."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--host-src', type=Path, required=True)
p.add_argument('--out', type=Path, required=True)
a = p.parse_args()
files = {name: (a.host_src / name).read_text() for name in ('imap.rs', 'lib.rs', 'network.rs')}
markers = {
    'imap.rs': ['uids.sort_unstable();', 'let newest = uids.last().copied().unwrap_or(last);',
                'uids.into_iter().rev().take(limit).collect()', '"last_uid": newest'],
    'lib.rs': ['imap.fetch(folder, state, 25)', 'seen.extend(messages.iter().map(|m| m["uid"].clone()));',
               'Ok(json!({"messages": messages, "state": {"seen": seen}, "reset": false}))',
               'Ok(json!({"new": new.len(), "total": total}))'],
    'network.rs': ['remaining.iter().rev().take(25)', '"has_more":remaining.len()>25'],
}
for name, required in markers.items():
    for marker in required:
        if marker not in files[name]:
            raise RuntimeError(f'Source changed; re-inspect {name}: missing verified marker')

uids = list(range(101, 131))
selected = list(reversed(uids))[:25]
cursor = max(uids)
next_selected = [uid for uid in uids if uid > cursor]
missing = sorted(set(uids)-set(selected)-set(next_selected))
assert missing == [101, 102, 103, 104, 105]
# POP accumulates downloaded IDs correctly, but its completion flag is not exposed
# to the app. Thus subsequent historical batches look like new arrivals after ready.
history = list(range(1, 31))
first = list(reversed(history))[:25]
second = [uid for uid in reversed(history) if uid not in first][:25]
assert second == [5, 4, 3, 2, 1]
report = {
    'kind': 'UNIT_SOURCE_ALGORITHM_COUNTEREXAMPLE',
    'overall_status': 'PARTIAL_HOST_COMPLETENESS_BLOCKER',
    'production_rust_executed': False, 'real_imap': False, 'real_pop3': False,
    'source': {name: {'path': str((a.host_src/name).resolve()),
        'sha256': hashlib.sha256((a.host_src/name).read_bytes()).hexdigest(),
        'verified_markers': markers[name]} for name in files},
    'imap': {'prior_last_uid': 100, 'new_uids': uids, 'limit': 25,
        'first_downloaded': selected, 'saved_last_uid': cursor,
        'second_downloaded': next_selected, 'permanently_skipped': missing,
        'finding': 'Newest-only limit advances last_uid over undownloaded UIDs; sync also discards has_more/reset.'},
    'pop3': {'initial_historical_uids': history, 'limit': 25,
        'first_history_baseline': first, 'next_historical_batch': second,
        'finding': 'Network accumulates seen, but has_more is dropped before sync response; watcher cannot distinguish later historical batch from arrivals.'},
    'ownership': 'Read-only finding. Host owner must repair transport cursor and expose completion/reset contract; incoming_mail alone cannot recover missing cache IDs.'
}
a.out.mkdir(parents=True, exist_ok=False)
(a.out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
for name in files:
    excerpts = []
    for line, content in enumerate(files[name].splitlines(), 1):
        if any(marker in content for marker in markers[name]):
            excerpts.append(f'{line}: {content}')
    (a.out/(name+'.excerpt.txt')).write_text('\n'.join(excerpts)+'\n')
print(json.dumps({'kind': report['kind'], 'skipped_uids': missing,
    'later_pop_history': second, 'production_rust_executed': False}))
