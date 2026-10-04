#!/usr/bin/env python3
"""Frozen old/new modules and identical synthetic input; no model or services."""
import hashlib
import json
import shutil

from memory_runtime import ROOT, run

BASE = ROOT / 'official_muse/prelim/evidence/memory/relevance'
OUT = BASE / 'budget-isolation'
SEED = BASE / 'budget-control/before/state/muse-goals'


def main():
    if OUT.exists():
        raise RuntimeError('preserve existing isolation evidence; choose a new OUT before rerun')
    OUT.mkdir(parents=True)
    seed_hashes = {name: hashlib.sha256((SEED / name).read_bytes()).hexdigest()
                   for name in ('memory.json', 'global-memory-settings.json')}
    result = {'scope': 'LOCAL/FIXTURE diagnostics only; direct_retrieval skips global boot and retains boot=false',
              'seed_sha256': seed_hashes, 'runs': {}}
    for mode in ('normal', 'direct_retrieval'):
        for version in ('before', 'final'):
            output = OUT / mode / version
            jail = output / 'state/muse-goals'
            jail.mkdir(parents=True)
            for name in seed_hashes:
                shutil.copy2(SEED / name, jail / name)
                assert hashlib.sha256((jail / name).read_bytes()).hexdigest() == seed_hashes[name]
            (jail / 'memory-budget-isolated-mode.json').write_text(json.dumps({'mode': mode}))
            module = BASE / (version + '-module.splash')
            item = {'module_sha256': hashlib.sha256(module.read_bytes()).hexdigest()}
            try:
                item['report'] = run(output, probe='memory_budget_isolated', module_source=module)
                item['status'] = 'RESULT'
            except Exception as exc:
                item['status'] = 'RUNTIME_FAILED'
                item['error'] = str(exc)
            stage = jail / 'memory-budget-isolated-stage.json'
            if stage.exists():
                item['last_stage'] = json.loads(stage.read_text())
            result['runs'][mode + '/' + version] = item
            (OUT / 'summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
            print(mode, version, item['status'], item.get('last_stage'), flush=True)


if __name__ == '__main__':
    main()
