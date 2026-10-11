#!/usr/bin/env python3
"""Offline tests; supplied source catalog is read once, mutations use temp copies."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import apply_qwen_fast as routing


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='muse-routing-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.catalog = self.root / 'model_catalog.json'
        self.catalog.write_bytes(BASELINE)

    def cli(self, mode):
        return subprocess.run([sys.executable, str(routing.HERE / 'apply_qwen_fast.py'),
                               mode, str(self.catalog)], capture_output=True, text=True)

    def test_real_cli_roundtrip_and_permissions(self):
        self.catalog.chmod(0o640)
        for mode in ['check', 'apply', 'verify']:
            result = self.cli(mode)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], mode.upper() + '_PASS')
            if mode == 'check':
                self.assertEqual(self.catalog.read_bytes(), BASELINE)
        self.assertEqual(routing.sha(self.catalog.read_bytes()), routing.PATCHED_SHA)
        self.assertEqual(self.catalog.stat().st_mode & 0o777, 0o640)

    def test_only_one_row_added_all_existing_models_unchanged(self):
        original = json.loads(BASELINE)
        patched = json.loads(routing.patched_bytes(BASELINE))
        self.assertEqual(patched['updated_at'], original['updated_at'])
        rows = patched['models']
        self.assertEqual(sum(row['provider'] == routing.ENTRY['provider'] for row in rows), 1)
        self.assertEqual([row for row in rows if row['provider'] != routing.ENTRY['provider']], original['models'])
        self.assertEqual(next(row for row in rows if row['provider'] == routing.ENTRY['provider']), routing.ENTRY)

    def test_unified_patch_applies_with_git_to_temporary_sdk(self):
        sdk = self.root / 'sdk'
        target = sdk / routing.TARGET
        target.parent.mkdir(parents=True)
        target.write_bytes(BASELINE)
        for check in [True, False]:
            args = ['git', 'apply'] + (['--check'] if check else []) + [str(routing.HERE / 'qwen-fast.patch')]
            result = subprocess.run(args, cwd=sdk, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(routing.sha(target.read_bytes()), routing.PATCHED_SHA)

    def test_repeat_application_refused_without_writing(self):
        self.assertEqual(self.cli('apply').returncode, 0)
        before = self.catalog.read_bytes()
        result = self.cli('apply')
        self.assertEqual(result.returncode, 2)
        self.assertIn('already patched', result.stderr)
        self.assertEqual(self.catalog.read_bytes(), before)

    def test_drift_and_duplicate_refused_without_writing(self):
        for modified in [BASELINE + b' ', BASELINE.replace(b'"local/local-default"',
                              b'"local/Qwen2.5-0.5B-Instruct-Q4_0-offline"', 1)]:
            with self.subTest(sha=routing.sha(modified)):
                self.catalog.write_bytes(modified)
                self.assertEqual(self.cli('apply').returncode, 2)
                self.assertEqual(self.catalog.read_bytes(), modified)

    def test_verify_rejects_unpatched_catalog(self):
        self.assertEqual(self.cli('verify').returncode, 2)
        self.assertEqual(self.catalog.read_bytes(), BASELINE)

    def test_tampered_patch_and_manifest_refused(self):
        folder = self.root / 'artifacts'
        folder.mkdir()
        original_manifest = (routing.HERE / 'manifest.json').read_bytes()
        original_patch = (routing.HERE / 'qwen-fast.patch').read_bytes()
        for changed in ['patch', 'manifest']:
            with self.subTest(changed=changed):
                (folder / 'manifest.json').write_bytes(original_manifest)
                (folder / 'qwen-fast.patch').write_bytes(original_patch)
                if changed == 'patch':
                    (folder / 'qwen-fast.patch').write_bytes(original_patch + b' ')
                else:
                    manifest = json.loads(original_manifest)
                    manifest['entry']['type'] = 'strong'
                    (folder / 'manifest.json').write_text(json.dumps(manifest))
                with mock.patch.object(routing, 'HERE', folder), self.assertRaises(ValueError):
                    routing.patched_bytes(BASELINE)

    def test_replace_failure_keeps_original_and_cleans_temp(self):
        with mock.patch.object(routing.os, 'replace', side_effect=OSError('synthetic replace failure')):
            with self.assertRaises(OSError):
                routing.run('apply', self.catalog)
        self.assertEqual(self.catalog.read_bytes(), BASELINE)
        self.assertEqual(list(self.root.glob('.qwen-fast-*')), [])

    def test_concurrent_change_refused_without_overwriting_new_bytes(self):
        changed = BASELINE + b'\n'
        def change_after_flush(_fd):
            self.catalog.write_bytes(changed)
        with mock.patch.object(routing.os, 'fsync', side_effect=change_after_flush):
            with self.assertRaisesRegex(ValueError, 'changed during preparation'):
                routing.run('apply', self.catalog)
        self.assertEqual(self.catalog.read_bytes(), changed)
        self.assertEqual(list(self.root.glob('.qwen-fast-*')), [])

    def test_symlink_and_profile_path_refused(self):
        link = self.root / 'linked' / 'model_catalog.json'
        link.parent.mkdir()
        link.symlink_to(self.catalog)
        other = self.root / '_main.json'
        other.write_text('{"synthetic":true}')
        for path in [link, other]:
            with self.subTest(path=path.name), self.assertRaises(ValueError):
                routing.run('apply', path)
        self.assertEqual(self.catalog.read_bytes(), BASELINE)
        self.assertEqual(other.read_text(), '{"synthetic":true}')

    def test_launcher_alias_dynamic_route_and_ctx4096(self):
        source = (routing.HERE.parent / 'muse_launcher.m').read_text()
        self.assertEqual(routing.launcher_contract(source)['provider_endpoint_field'], 'route_base_url')
        version_pattern = r'(muse-goals-\d+\.\d+\.\d+-rc)(\d+)'
        self.assertRegex(source, version_pattern)
        version_change = re.sub(version_pattern, lambda m: m[1] + str(int(m[2]) + 1), source)
        self.assertEqual(routing.launcher_contract(version_change), routing.launcher_contract(source))
        for changed in [source.replace('NSString *modelID = @"' + routing.MODEL + '";',
                                       'NSString *modelID = @"local-default";'),
                        source.replace('@"--ctx-size", @"4096"', '@"--ctx-size", @"8192"'),
                        source.replace('@"route_base_url":[base stringByAppendingString:@"/v1"]',
                                       '@"route_base_url":base')]:
            with self.subTest(), self.assertRaises(ValueError):
                routing.launcher_contract(changed)

    def test_existing_stable_rank_selects_fast_local_strong_cloud(self):
        rows = json.loads(routing.patched_bytes(BASELINE))['models']
        tiers = {row['provider']: row.get('type') for row in rows}
        cloud, local = 'minimax-cn/MiniMax-M3', routing.ENTRY['provider']
        self.assertEqual(tiers['local/local-default'], 'strong')
        for requested, expected in [('fast', [local, cloud]), ('strong', [cloud, local])]:
            def rank(provider):
                tier = tiers.get(provider)
                return 0 if tier == requested else 1 if tier is not None else 2
            self.assertEqual(sorted([cloud, local], key=rank), expected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--catalog', type=Path, required=True)
    parser.add_argument('--result', type=Path)
    args = parser.parse_args()
    BASELINE = args.catalog.read_bytes()
    if routing.sha(BASELINE) != routing.BASELINE_SHA:
        parser.exit(2, 'REFUSED: test input must match the frozen baseline SHA\n')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(RoutingTests))
    if args.result:
        args.result.write_text(json.dumps({
            'status': 'OFFLINE_FIXTURE_PASS' if result.wasSuccessful() else 'OFFLINE_FIXTURE_FAIL',
            'tests_run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
            'baseline_sha256': routing.sha(BASELINE), 'patched_sha256': routing.PATCHED_SHA,
            'source_catalog_unchanged': args.catalog.read_bytes() == BASELINE,
            'launcher_source_sha256': routing.sha((routing.HERE.parent / 'muse_launcher.m').read_bytes()),
            'boundary': 'Temporary catalog application and static launcher checks; no Rust, GUI, provider requests, profile save or end-to-end acceptance.'
        }, indent=2) + '\n')
    sys.exit(0 if result.wasSuccessful() else 1)
