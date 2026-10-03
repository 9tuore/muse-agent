"""Fault fixtures from a receipt produced by the real current gm_forget.

No external action, model or production data. Each run has its own copied jail.
"""
import hashlib
import json
from pathlib import Path
import argparse

from memory_runtime import ROOT, run


def main():
    base = ROOT/'official_muse/prelim/evidence/memory/forget-conflict'
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=base/'recovery-visible')
    args = parser.parse_args()
    seed = base/'after-current-core-visible/state/muse-goals'
    before = (base/'before/state/muse-goals/memory.json').read_bytes()
    clean = (seed/'memory.json').read_bytes()
    receipt = json.loads((seed/'memory-forget-commit.json').read_text())
    assert hashlib.sha256(before).hexdigest() == receipt['before_sha256']
    assert hashlib.sha256(clean).hexdigest() == receipt['clean_sha256']
    assert (seed/'memory.backup.json').read_bytes() == clean
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    main_source = (ROOT/'official_muse/app/bundle/main.splash').read_text()
    module = (ROOT/'official_muse/global_memory.splash').read_text()
    core = main_source[main_source.index('let runs = []'):main_source.index('// BEGIN GLOBAL_MEMORY')]
    source = out/'current-core-source.splash'
    source.write_text('let goals = []\nlet selected_id = ""\nlet task = nil\nlet activity = []\nlet memory = []\nlet page = ""\nfn redraw(){}\nfn set_page(next){page=next}\n'+core+'// BEGIN GLOBAL_MEMORY\n'+module+'\nstart_timeout(0.05, || boot())\n')
    variants = ['before_primary', 'after_primary', 'previously_disabled',
        'missing_receipt', 'preparing_receipt', 'wrong_profile', 'wrong_hash',
        'stale_primary', 'dirty_pre_global', 'missing_target', 'malformed_backup', 'unknown_phase', 'preparing_dirty_backup', 'requires_migration']
    summary = {'status': 'RUNNING', 'scope': 'CURRENT_MEMORY_CORE_AND_MODULE/FIXTURE: real visible card-host, synthetic copied data, mocked render/transport',
        'main_sha256': hashlib.sha256(main_source.encode()).hexdigest(),
        'core_sha256': hashlib.sha256(core.encode()).hexdigest(),
        'module_sha256': hashlib.sha256(module.encode()).hexdigest(), 'cases': {}}
    for mode in variants:
        case = out/mode
        jail = case/'state/muse-goals'
        jail.mkdir(parents=True)
        settings = json.loads((seed/'global-memory-settings.json').read_text())
        settings.update(enabled=False, forget_pending=True)
        intent = dict(receipt)
        primary = clean if mode == 'after_primary' else before
        backup = clean
        if mode == 'previously_disabled': intent['enabled'] = False
        if mode == 'preparing_receipt': intent['phase'] = 'preparing'
        if mode == 'unknown_phase': intent['phase'] = 'unrecognized'
        if mode == 'preparing_dirty_backup': intent['phase'] = 'preparing'; backup = before
        if mode == 'wrong_profile': intent['user_id'] = 'user:other-profile'
        if mode == 'wrong_hash': intent['clean_sha256'] = '0'*64
        if mode == 'missing_target': intent['id'] = 'memory:missing-target'
        if mode == 'stale_primary': primary = before + b'\n'
        if mode == 'dirty_pre_global': (jail/'memory.pre-global.json').write_bytes(before)
        if mode == 'malformed_backup':
            backup = b'{"schema":1,"claims":[null],"sources":[],"forget":[]}'
            intent['clean_sha256'] = hashlib.sha256(backup).hexdigest()
        if mode == 'requires_migration':
            changed = json.loads(clean)
            changed['claims'][0].pop('memory_type')
            backup = json.dumps(changed, ensure_ascii=False, separators=(',', ':')).encode()
            intent['clean_sha256'] = hashlib.sha256(backup).hexdigest()
        (jail/'memory.json').write_bytes(primary)
        (jail/'memory.backup.json').write_bytes(backup)
        (jail/'global-memory-settings.json').write_text(json.dumps(settings))
        (jail/'forget-target.json').write_bytes((seed/'forget-target.json').read_bytes())
        if mode != 'missing_receipt': (jail/'memory-forget-commit.json').write_text(json.dumps(intent))
        result = run(case, port=8482, probe='memory_forget_recovery', main_source=source, visible=True)
        expected = mode in ['before_primary', 'after_primary', 'previously_disabled', 'preparing_receipt']
        if expected:
            assert result['boot'] and result['target_deleted'] and not result['pending'], result
            assert result['enabled'] == intent['enabled'], result
            assert result['settings']['forget_pending'] is False
            saved = json.loads((jail/'memory.json').read_text())
            assert all(c['document']['payload']['deleted'] for c in saved['claims'][-2:])
            assert all(c['history'] == [] for c in saved['claims'][-2:])
            assert saved['claims'][0]['document']['payload']['value'] == '汇报应先写结论，再列三项重点。'
            assert saved['claims'][2]['document']['payload']['deleted'] is False
            assert '收口状态' not in result['context']['text']
            if intent['enabled']: assert '汇报应先写结论' in result['context']['text']
            else: assert result['context']['hits'] == []
        else:
            assert not result['boot'] and not result['enabled'] and result['pending'], result
            assert result['primary_unchanged'] and (jail/'memory.json').read_bytes() == primary
            assert result['context']['hits'] == []
        assert result['no_external_transport']
        summary['cases'][mode] = {'status': 'PASS', 'expected_recovery': expected,
            'boot': result['boot'], 'primary_unchanged': result['primary_unchanged'],
            'enabled': result['enabled'], 'pending': result['pending'], 'target_deleted': result['target_deleted']}
        (out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
        print(mode, 'PASS', flush=True)
    summary['status'] = 'PASS_FIXTURE_ONLY'
    (out/'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__': main()
