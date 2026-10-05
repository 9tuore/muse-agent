#!/usr/bin/env python3
"""Independent readback of owned synthetic forget/isolation runs only."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'forget-final-r1'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    state = OUT / 'choose_old/first/state/muse-goals'
    names = ['memory.json', 'memory.backup.json', 'memory-forget-candidate.json']
    raw = {n: (state/n).read_bytes() for n in names}
    d = json.loads(raw['memory.json'])
    values = ['合成事实甲最初提案', '合成事实甲更新为周六', '合成事实乙最新为周日']
    hashes = {digest(v.encode()) for v in values}
    checks = {
        'two_claims_retained_as_deleted': len(d['claims']) == 2 and all(c['document']['payload']['deleted'] for c in d['claims']),
        'values_cleared': all(c['document']['payload']['value'] == '' for c in d['claims']),
        'history_cleared': all(c['history'] == [] for c in d['claims']),
        'source_history_cleared': all(c['source_history'] == [] for c in d['claims']),
        'source_ids_cleared': all(c['document']['payload']['source_ids'] == [] for c in d['claims']),
        'relations_cleared': all(c['document']['payload']['relations'] == [] for c in d['claims']),
        'three_sources_sanitized': len(d['sources']) == 3 and all(s['support_excerpt'] == '' for s in d['sources']),
        'all_three_values_tombstoned': {t['content_sha256'] for t in d['forget']} == hashes,
        'all_sources_have_tombstones': {s['source_id'] for s in d['sources']} <= {t['source_id'] for t in d['forget']},
        'primary_backup_exact_equal': raw['memory.json'] == raw['memory.backup.json'],
        'three_product_snapshots_clean': all(all(v.encode() not in b for v in values) for b in raw.values()),
    }
    scope = d['claims'][0]['document']['scope']
    checks['scope_retained_consistently'] = all(c['document']['scope'] == scope for c in d['claims']) and all(s['scope'] == scope for s in d['sources']) and all(t['scope'] == scope for t in d['forget'])
    for case in ['other_project', 'other_owner']:
        s = HERE / f'forget-final-r2/{case}/first/state/muse-goals'
        base = json.loads((s/'resolve-baseline.json').read_text())
        for name, field in [('memory.json','memory_bytes'),('memory.backup.json','backup_bytes'),('activity.json','activity_bytes')]:
            checks[f'{case}_{name}_unchanged'] = (s/name).read_text() == base[field]
        docs = json.loads((s/'memory.json').read_text())['claims']
        scopes = [c['document']['scope'] for c in docs]
        key = 'project_id' if case == 'other_project' else 'owner_id'
        checks[f'{case}_distinct_scopes_retained'] = len(scopes) == 2 and scopes[0][key] != scopes[1][key]
    result = {'status': 'PASS' if all(checks.values()) else 'FAIL', 'passed': sum(checks.values()), 'failed': [k for k,v in checks.items() if not v], 'checks': checks, 'snapshot_sha256': {n: digest(b) for n,b in raw.items()}, 'fixture_only': True, 'scope': 'Product primary/backup/forget-candidate cleanup only; pre-forget synthetic exports and diagnostic baselines deliberately retained. No production data.'}
    (OUT/'READBACK.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    race = {}
    for case in ['other_project','other_owner']:
        s = OUT / f'{case}/first/state/muse-goals'
        base = json.loads((s/'resolve-baseline.json').read_text())
        before = json.loads(base['activity_bytes'])
        after = json.loads((s/'activity.json').read_text())
        added = after[len(before):]
        race[case] = {'original_failed_assertion':'guard_activity_unchanged','baseline_count':len(before),'final_count':len(after),'prefix_unchanged':after[:len(before)]==before,'added_event_kinds':[e['kind'] for e in added],'only_deferred_save':len(added)==1 and added[0]['kind']=='memory saved'}
    (OUT/'ORIGINAL_ACTIVITY_RACE.json').write_text(json.dumps(race,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'passed':result['passed'],'failed':result['failed'],'original_race':race}))
    return int(result['status'] != 'PASS')

if __name__ == '__main__':
    raise SystemExit(main())
