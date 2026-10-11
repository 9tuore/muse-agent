#!/usr/bin/env python3
"""Apply one frozen Qwen catalog insertion; never read or write a profile."""
import argparse
import difflib
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import tempfile

HERE = Path(__file__).resolve().parent
TARGET = 'apps/ai-providers/config/data/model_catalog.json'
BASELINE_SHA = '65ee8b16156b33705e9937b8c9dc926e27aa247e30c7689f5ce3185313b91bf6'
PATCHED_SHA = '744ae46b6026ddd152b6c86f63f6acb918b05115d239eecbcb06064e271945a9'
PATCH_SHA = 'cf881e50ee6b22cd7b83ff673eb421e54f1218eeb0426aebd0cc997801d71a53'
MODEL = 'Qwen2.5-0.5B-Instruct-Q4_0-offline'
ENTRY = {'provider': 'local/' + MODEL, 'type': 'fast', 'default': False,
         'cost_in': 0, 'cost_out': 0, 'context_window': 4096}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def artifacts():
    manifest = json.loads((HERE / 'manifest.json').read_text())
    expected = {'schema': 1, 'target': TARGET, 'baseline_sha256': BASELINE_SHA,
                'patched_sha256': PATCHED_SHA, 'patch_sha256': PATCH_SHA,
                'entry': ENTRY, 'endpoint_field': 'route_base_url'}
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError('routing manifest differs from the frozen contract')
    patch = (HERE / 'qwen-fast.patch').read_bytes()
    if sha(patch) != PATCH_SHA:
        raise ValueError('patch SHA mismatch')
    return patch


def launcher_contract(source):
    """Static source check, not a running daemon or model inference check."""
    aliases = re.findall(r'NSString\s*\*modelID\s*=\s*@"([^"]+)";', source)
    contexts = re.findall(r'@"--ctx-size"\s*,\s*@"(\d+)"', source)
    markers = ['@"--alias", modelID', '@"--host", @"127.0.0.1"',
               'int port = localPort();', 'address.sin_addr.s_addr = htonl(INADDR_LOOPBACK)',
               'bind(fd, (struct sockaddr *)&address, size)',
               'getsockname(fd, (struct sockaddr *)&address, &size)',
               '@"http://127.0.0.1:%d", port',
               '@"--port", [NSString stringWithFormat:@"%d", port]',
               '@"base_url":base, @"route_base_url":[base stringByAppendingString:@"/v1"]',
               'updateLocalRoute(profilePath,llm,[base stringByAppendingString:@"/v1"])']
    if aliases != [MODEL] or contexts != ['4096'] or any(m not in source for m in markers):
        raise ValueError('launcher alias, ctx4096 or dynamic /v1 route contract changed')
    return {'model_id': MODEL, 'context_window': 4096,
            'provider_endpoint_field': 'route_base_url', 'static_only': True}


def patched_bytes(original):
    patch = artifacts()
    actual = sha(original)
    if actual == PATCHED_SHA:
        raise ValueError('catalog already patched; repeated application refused')
    if actual != BASELINE_SHA:
        raise ValueError('baseline SHA mismatch; catalog drift refused')
    text = original.decode('utf-8')
    anchor = '    {\n      "provider": "local/local-default",\n'
    if text.count(anchor) != 1:
        raise ValueError('expected one catalog insertion point')
    insert = '\n'.join('    ' + line for line in json.dumps(ENTRY, indent=2).splitlines()) + ',\n'
    result = text.replace(anchor, insert + anchor, 1)
    # Reproduce the exact unified diff: no fuzzy patch or unchecked substitute.
    reproduced = ''.join(difflib.unified_diff(
        text.splitlines(keepends=True), result.splitlines(keepends=True),
        fromfile='a/' + TARGET, tofile='b/' + TARGET)).encode('utf-8')
    if reproduced != patch or sha(result.encode('utf-8')) != PATCHED_SHA:
        raise ValueError('patch reproduction or patched SHA mismatch')
    return result.encode('utf-8')


def run(mode, target):
    artifacts()
    launcher = (HERE.parent / 'muse_launcher.m').read_text()
    contract = launcher_contract(launcher)
    if target.name != 'model_catalog.json' or target.is_symlink() or not target.is_file():
        raise ValueError('target must be an existing regular model_catalog.json, not a symlink')
    original = target.read_bytes()
    if mode == 'verify':
        if sha(original) != PATCHED_SHA:
            raise ValueError('patched SHA mismatch')
    else:
        result = patched_bytes(original)
        if mode == 'apply':
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=target.parent, prefix='.qwen-fast-', delete=False) as out:
                    temporary = Path(out.name)
                    os.fchmod(out.fileno(), stat.S_IMODE(target.stat().st_mode))
                    out.write(result)
                    out.flush()
                    os.fsync(out.fileno())
                if target.is_symlink() or target.read_bytes() != original:
                    raise ValueError('catalog changed during preparation; write refused')
                os.replace(temporary, target)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
            if sha(target.read_bytes()) != PATCHED_SHA:
                raise ValueError('post-write verification failed')
    return {'status': mode.upper() + '_PASS', 'baseline_sha256': BASELINE_SHA,
            'patched_sha256': PATCHED_SHA, 'launcher': contract}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['check', 'apply', 'verify'])
    parser.add_argument('catalog', type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.mode, args.catalog), ensure_ascii=False))
    except (OSError, ValueError) as error:
        parser.exit(2, 'REFUSED: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
