#!/usr/bin/env python3
"""Repeatable M01-M12 module evidence; explicitly separates pending UI/model semantics."""
from copy import deepcopy
import hashlib
import json
import shutil
from datetime import datetime
from memory_runtime import ROOT, run as host_run
def run(output, port=8482, probe="memory_suite"):
    return host_run(output,port,probe.replace("memory_","memory_regression_",1))

OUT = ROOT / 'official_muse/prelim/evidence/memory' / ('acceptance-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')))

def jail(name):
    p = OUT / name / 'state/muse-goals'
    p.mkdir(parents=True, exist_ok=True)
    return p

def check(report, exclude=()):
    checks = {k: v for k, v in report.items() if isinstance(v, bool) and k not in exclude}
    assert checks and all(checks.values()), {k: v for k, v in checks.items() if not v}
    return len(checks)

def main():
    lifecycle = run(OUT / 'lifecycle', probe='memory_lifecycle')
    lifecycle_restart = run(OUT / 'lifecycle', probe='memory_lifecycle_restart')
    lifecycle_forgotten = run(OUT / 'lifecycle', probe='memory_lifecycle_forgotten')
    legacy_append = run(OUT / 'legacy-append', probe='memory_legacy_append')
    first = run(OUT / 'suite')
    count = check(first) + check(legacy_append) + check(lifecycle) + check(lifecycle_restart) + check(lifecycle_forgotten)
    restart = run(OUT / 'suite', probe='memory_restart')
    count += check(restart)
    original = jail('suite')
    settings = json.loads((original / 'global-memory-settings.json').read_text())
    exported = json.loads((original / 'memory-roundtrip.json').read_text())
    imported_jail = jail('roundtrip')
    write_json(imported_jail / 'global-memory-settings.json', settings)
    write_json(imported_jail / 'import-fixture.json', exported)
    imported = run(OUT / 'roundtrip', probe='memory_import_copy')
    count += check(imported)
    foreign_jail = jail('foreign')
    write_json(foreign_jail / 'import-fixture.json', exported)
    foreign = run(OUT / 'foreign', probe='memory_foreign')
    count += check(foreign)
    assert foreign['profile_id'] != restart['profile_id']
    pending_jail = jail('pending')
    pending_settings = deepcopy(settings)
    pending_settings['forget_pending'] = True
    write_json(pending_jail / 'global-memory-settings.json', pending_settings)
    shutil.copy2(original / 'memory.json', pending_jail / 'memory.json')
    pending_before = (pending_jail / 'memory.json').read_bytes()
    pending = run(OUT / 'pending', probe='memory_pending')
    count += check(pending)
    assert (pending_jail / 'memory.json').read_bytes() == pending_before
    # Populate the maximum existing core capacity on a synthetic COPY, then
    # retrieve in the real runtime. No implementation of retrieval in Python.
    large = json.loads((original / 'memory.json').read_text())
    template = deepcopy(large['claims'][0])
    source_template = deepcopy(large['sources'][0])
    for i in range(64-len(large['claims'])):
        c, s = deepcopy(template), deepcopy(source_template)
        sid = f'source:budget:{i}'
        cid = f'memory:budget:{i}'
        value = f'预算星尘记录第{i}条合成资料，只能相关检索使用。'
        c['document'].update(id=cid, revision=1)
        c['document']['scope'].update(project_id='星尘', owner_id='用户')
        c['document']['payload'].update(value=value, subject_id='预算星尘', predicate=f'记录{i}', source_ids=[sid], relations=[])
        c.update(memory_type='fact', source_history=[sid], history=[])
        s.update(source_id=sid, content_sha256=hashlib.sha256(value.encode()).hexdigest(), support_excerpt=value)
        s['scope'] = deepcopy(c['document']['scope'])
        large['claims'].append(c)
        large['sources'].append(s)
    budget_jail = jail('budget')
    write_json(budget_jail / 'global-memory-settings.json', settings)
    write_json(budget_jail / 'memory.json', large)
    budget = run(OUT / 'budget', probe='memory_budget')
    count += check(budget)
    assert budget['count'] == 64
    # A real pre-global schema copy. Preserve exact source bytes/hashes.
    legacy_claim = deepcopy(template)
    legacy_source = deepcopy(source_template)
    legacy_value = '旧式合成项目资料'
    legacy_claim['document']['payload']['value'] = legacy_value
    legacy_source.update(content_sha256=hashlib.sha256(legacy_value.encode()).hexdigest(), support_excerpt=legacy_value)
    legacy_claim = {k: legacy_claim[k] for k in ('document','pinned','source_history')}
    for target in (legacy_claim['document']['scope'], legacy_source['scope']):
        for key in ('user_id','project_id','owner_id'): target.pop(key, None)
    legacy = {'schema': 1, 'claims':[legacy_claim], 'sources':[legacy_source], 'forget':[]}
    migrated_jail = jail('migration')
    write_json(migrated_jail / 'memory.json', legacy)
    legacy_bytes = (migrated_jail / 'memory.json').read_bytes()
    migration = run(OUT / 'migration', probe='memory_migration')
    count += check(migration)
    assert (migrated_jail / 'memory.pre-global.json').read_bytes() == legacy_bytes
    # Rollback uses a separate synthetic jail with untouched original bytes.
    rollback_jail = jail('rollback')
    (rollback_jail / 'memory.json').write_bytes(legacy_bytes)
    write_json(rollback_jail / 'global-memory-settings.json', json.loads((migrated_jail / 'global-memory-settings.json').read_text()))
    rollback = run(OUT / 'rollback', probe='memory_migration')
    count += check(rollback)
    reports = {'suite':first, 'restart':restart, 'budget':budget, 'migration':migration, 'rollback':rollback,
               'roundtrip':imported, 'foreign':foreign, 'pending':pending, 'legacy_append':legacy_append,
               'lifecycle':lifecycle, 'lifecycle_restart':lifecycle_restart, 'lifecycle_forgotten':lifecycle_forgotten}
    for field in ('main_source_sha256', 'core_sha256', 'module_sha256', 'host_sha256'):
        assert all(item[field] == first[field] for item in reports.values()), 'source/runtime changed during acceptance: ' + field
    result = {'boolean_checks_passed':count, 'main_source_sha256':first['main_source_sha256'], 'scope':'LOCAL/FIXTURE actual card-host, synthetic copies, no model/Host services',
              'module_sha256':first['module_sha256'], 'core_sha256':first['core_sha256'],
              'M01_M07':'PASS retrieval/storage fixtures', 'M08':'PENDING parent async integration',
              'M09':'PASS memory restart; conversation list belongs to parent', 'M10':'PASS 64-entry memory context budget',
              'M11':'PASS copied migration/snapshot/rollback/import/profile isolation',
              'M12':'PASS same-authority projection; actual UI belongs to visual executor',
              'MODEL_SEMANTICS':'NOT_TESTED', 'PROMPT_TRANSPORT':'PENDING final candidate',
              'overall':'PARTIAL', 'reports':reports}
    (OUT / 'acceptance.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'reports'}, ensure_ascii=False, indent=2))

if __name__ == '__main__': main()
