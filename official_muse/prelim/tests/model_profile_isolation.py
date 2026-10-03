#!/usr/bin/env python3
"""Offline profile isolation checks. No real credentials or inference."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory'))
from prepare_candidate import copy_authorized_model_profile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    checks = {}
    with tempfile.TemporaryDirectory(prefix='muse-model-profile-') as directory:
        root = Path(directory)
        authorized = root / 'authorized'
        profile = authorized / 'home/octos-home/.octos/profiles/_main.json'
        profile.parent.mkdir(parents=True)
        config = {'config': {'llm': {'primary': {
            'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3',
            'route': {'base_url': 'https://api.minimax.cn/v1', 'api_type': 'openai'}},
            'fallbacks': []}, 'env_vars': {'SYNTHETIC_KEY': 'NOT-A-REAL-KEY'}}}
        original = json.dumps(config).encode()
        profile.write_bytes(original)
        mail = authorized / 'apps/.host/mail/private-account-state'
        mail.parent.mkdir(parents=True)
        mail.write_text('SYNTHETIC-PRIVATE-MAIL-STATE')
        private = root / 'private'
        private.mkdir()
        metadata = copy_authorized_model_profile(authorized, private)
        copied = private / 'home/octos-home/.octos/profiles/_main.json'
        checks['official_profile_bytes_preserved'] = copied.read_bytes() == original
        checks['source_not_changed'] = profile.read_bytes() == original
        checks['mail_calendar_state_not_copied'] = not (private / 'apps').exists()
        checks['private_permissions'] = private.stat().st_mode & 0o777 == 0o700 and copied.stat().st_mode & 0o777 == 0o600
        checks['metadata_has_no_credentials'] = set(metadata) == {'family_id', 'model_id', 'base_url', 'api_type'} and 'NOT-A-REAL-KEY' not in json.dumps(metadata)
        variants = {
            'fallback_rejected': lambda llm: llm['fallbacks'].append({'family_id': 'local'}),
            'unknown_endpoint_rejected': lambda llm: llm['primary']['route'].update(base_url='https://unknown.invalid/v1'),
            'insecure_endpoint_rejected': lambda llm: llm['primary']['route'].update(base_url='http://api.minimax.cn/v1'),
            'wrong_model_rejected': lambda llm: llm['primary'].update(model_id='local-default')}
        for name, mutate in variants.items():
            data = json.loads(original)
            mutate(data['config']['llm'])
            profile.write_text(json.dumps(data))
            target = root / name
            target.mkdir()
            try:
                copy_authorized_model_profile(authorized, target)
                checks[name] = False
            except RuntimeError:
                checks[name] = not any(target.iterdir())
    result = {'kind': 'OFFLINE_SYNTHETIC_MODEL_PROFILE', 'checks': checks,
              'passed': sum(checks.values()), 'failed': [k for k, v in checks.items() if not v],
              'real_model': False, 'real_credentials': False}
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return bool(result['failed'])


if __name__ == '__main__':
    raise SystemExit(main())
