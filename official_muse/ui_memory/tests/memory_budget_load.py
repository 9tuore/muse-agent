#!/usr/bin/env python3
"""Exactly three independent real-host attempts of the previously failed fixture."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
from memory_runtime import ROOT, HOST, run

FIXTURE = ROOT / 'official_muse/app/build/ui-memory-20261003/memory/acceptance-20261003-030334-043457/budget/state'
FROZEN_MAIN = 'c72b13578964b535ee36c4d60fc9d77eaa5e6ed277c2ef32c2cfd42413076855'
FROZEN_GM = 'a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    out = ROOT / 'official_muse/app/build/ui-memory-20261003/memory' / ('budget-load-' + datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    out.mkdir(parents=True)
    assert sha(ROOT / 'official_muse/app/bundle/main.splash') == FROZEN_MAIN
    assert sha(ROOT / 'official_muse/global_memory.splash') == FROZEN_GM
    original_hash = sha(FIXTURE / 'muse-goals/memory.json')
    settings_hash = sha(FIXTURE / 'muse-goals/global-memory-settings.json')
    attempts = []
    for number in range(1, 4):
        assert sha(ROOT / 'official_muse/app/bundle/main.splash') == FROZEN_MAIN
        attempt_out = out / ('attempt-' + str(number))
        shutil.copytree(FIXTURE, attempt_out / 'state')
        assert sha(attempt_out / 'state/muse-goals/memory.json') == original_hash
        assert sha(attempt_out / 'state/muse-goals/global-memory-settings.json') == settings_hash
        before_load = os.getloadavg()
        started = time.monotonic()
        result = None
        error = None
        try:
            result = run(attempt_out, 8482, 'memory_budget_load')
        except RuntimeError as exc:
            error = str(exc)
        elapsed_ms = (time.monotonic() - started) * 1000
        log = attempt_out / 'memory_budget_load.log'
        log_text = log.read_text() if log.exists() else ''
        bools = {k:v for k,v in (result or {}).items() if isinstance(v,bool)}
        passed = bool(result) and bool(bools) and all(bools.values())
        attempt = {'number':number, 'pass':passed, 'host_attempt_elapsed_ms':elapsed_ms,
                   'context_elapsed_ms':result.get('context_elapsed_ms') if result else None,
                   'host_callback_time_limit_ms':64, 'host_time_limit_hit':'script time budget exceeded' in log_text,
                   'instruction_limit_hit':'instruction limit' in log_text,
                   'load_average_before':before_load, 'load_average_after':os.getloadavg(),
                   'input_memory_sha256':original_hash, 'input_settings_sha256':settings_hash,
                   'log':str(log.relative_to(ROOT)), 'result':result, 'error':error}
        attempts.append(attempt)
        (out / 'attempts.json').write_text(json.dumps(attempts, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps({k:v for k,v in attempt.items() if k not in ('result','error')},ensure_ascii=False),flush=True)
    assert sha(ROOT / 'official_muse/app/bundle/main.splash') == FROZEN_MAIN
    assert sha(ROOT / 'official_muse/global_memory.splash') == FROZEN_GM
    summary = {'attempt_count':3, 'passed':sum(a['pass'] for a in attempts),
               'failed':sum(not a['pass'] for a in attempts), 'main_source_sha256':FROZEN_MAIN,
               'module_sha256':FROZEN_GM, 'host_sha256':sha(HOST), 'fixture_memory_sha256':original_hash,
               'scope':'LOCAL/FIXTURE: actual independent hosts, identical copied fixture, port8482; no model/Host services',
               'measurement':'context_elapsed_ms measures only gm_context via native time_now; host_attempt_elapsed_ms includes startup/boot/report/quit and the 25s missing-report deadline on failure.',
               'limitation':'Three passes would not establish all-load stability; context elapsed is unavailable when host budget aborts the callback. Load average is observational, not a controlled CPU-load experiment.',
               'attempts':attempts}
    path=out / 'summary.json'
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
    print('SUMMARY:',path,flush=True)

if __name__ == '__main__': main()
