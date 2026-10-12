#!/usr/bin/env python3
"""Actual compiled launcher flow, isolated stub Host/health service; no GUI/AI.

Only the duplicate-Host process probe and shared mutex filename are isolated in
the build snapshot, so this fixture cannot interfere with a real running Muse.
All profile/bootstrap/port code is the supplied production source unchanged.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
import uuid

MODEL = 'Qwen2.5-0.5B-Instruct-Q4_0-offline'


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--original-tests', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    source = a.source.read_text()
    token = uuid.uuid4().hex
    with tempfile.TemporaryDirectory(prefix='muse-local-bootstrap-code-') as temp:
        snapshot = Path(temp)
        private = source.replace('@"/Contents/Resources/host-runtime/muse-host"', '@"/fixture-no-real-host-probe"')
        private = private.replace('@"muse-integrated-host.flock"', f'@"muse-local-fixture-{token}.flock"')
        (snapshot / 'muse_launcher.m').write_text(private)
        shutil.copy2(a.original_tests.parent / 'workbuddy_launcher.sh', snapshot)
        spec = importlib.util.spec_from_file_location('launcher_fixture', a.original_tests)
        fixture = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fixture)
        fixture.HERE = snapshot

        class FreshLocal(fixture.LauncherTests):
            def local(self, port, family='local'):
                return {'family_id': family, 'model_id': MODEL,
                        'route': {'base_url': f'http://127.0.0.1:{port}/v1', 'api_type': 'openai'}}

            def available_port(self):
                with socket.socket() as s:
                    s.bind(('127.0.0.1', 0))
                    return s.getsockname()[1]

            def check_fresh(self, flag):
                result = self.launch(flag, hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                self.assertTrue(self.profile.exists(), self.messages(result))
                profile = json.loads(self.profile.read_text())
                self.assertEqual(profile['id'], '_main')
                self.assertEqual(profile['name'], 'Main')
                self.assertTrue(profile['enabled'])
                self.assertRegex(profile['created_at'], r'^2026-')
                self.assertEqual(profile['created_at'], profile['updated_at'])
                self.assertNotIn('env_vars', profile['config'])
                self.assertEqual(profile['config']['llm']['fallbacks'], [])
                selection = profile['config']['llm']['primary']
                self.assertEqual(selection['family_id'], 'local')
                self.assertEqual(selection['model_id'], MODEL)
                self.assertEqual(selection['route']['api_type'], 'openai')
                status = json.loads((self.state / 'local-model.json').read_text())
                self.assertEqual(selection['route']['base_url'], status['route_base_url'])
                self.assertTrue(status['native_profile_created'])
                self.assertTrue(status['configured_local_selection'])
                self.assertFalse(status['inference_verified'])
                self.assertEqual(self.profile.stat().st_mode & 0o777, 0o600)
                self.assertFalse(list(self.profile.parent.glob('*.tmp')))
                self.assertTrue((self.state / 'synthetic-local-started').exists())

            def test_bootstrap_explicit_hybrid(self):
                self.check_fresh('--hybrid')

            def test_bootstrap_default_hybrid(self):
                self.check_fresh(None)

            def test_fresh_restart_preserves_bytes_and_port(self):
                self.check_fresh(None)
                before = self.profile.read_bytes()
                first = json.loads((self.state / 'local-model.json').read_text())
                result = self.launch(None, hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                second = json.loads((self.state / 'local-model.json').read_text())
                self.assertEqual(second['route_base_url'], first['route_base_url'])
                self.assertEqual(self.profile.read_bytes(), before)
                self.assertFalse(second['native_profile_created'])

            def test_existing_local_primary_starts_without_cloud(self):
                port = self.available_port()
                before = self.write_profile(self.local(port))
                result = self.launch(None, hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                self.assertTrue((self.state / 'synthetic-local-started').exists())
                self.assertEqual(self.profile.read_bytes(), before)
                status = json.loads((self.state / 'local-model.json').read_text())
                self.assertEqual(status['route_base_url'], f'http://127.0.0.1:{port}/v1')

            def test_cloud_and_local_fallback_keep_both_and_port(self):
                port = self.available_port()
                before = self.write_profile({'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'}, [self.local(port)])
                result = self.launch(None, hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                self.assertEqual(self.profile.read_bytes(), before)
                status = json.loads((self.state / 'local-model.json').read_text())
                self.assertEqual(status['route_base_url'], f'http://127.0.0.1:{port}/v1')

            def test_cloud_without_local_is_byte_preserved(self):
                before = self.write_profile({'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'})
                result = self.launch(None, hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                self.assertEqual(self.profile.read_bytes(), before)
                self.assertFalse(json.loads((self.state / 'local-model.json').read_text())['configured_local_selection'])

            def test_existing_empty_profile_is_not_bootstrapped(self):
                before = self.write_profile({})
                result = self.launch(None, hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                self.assertEqual(self.profile.read_bytes(), before)
                self.assertFalse((self.state / 'synthetic-local-started').exists())

            def test_models_fresh_skips_local_and_profile(self):
                result = self.launch('--models', hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                self.assertFalse(self.profile.exists())
                self.assertFalse((self.state / 'synthetic-local-started').exists())

            def test_occupied_port_is_actionable_and_keeps_profile(self):
                with socket.socket() as occupied:
                    occupied.bind(('127.0.0.1', 0))
                    occupied.listen()
                    port = occupied.getsockname()[1]
                    before = self.write_profile(self.local(port))
                    result = self.launch(None, hybrid=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('已被占用', self.messages(result))
                self.assertIn('--models', self.messages(result))
                self.assertFalse((self.state / 'synthetic-local-started').exists())
                self.assertEqual(self.profile.read_bytes(), before)

            def test_remote_local_route_never_retargeted(self):
                local = self.local(8100)
                local['route']['base_url'] = 'https://example.invalid/v1'
                before = self.write_profile(local)
                result = self.launch(None, hybrid=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('--models', self.messages(result))
                self.assertEqual(self.profile.read_bytes(), before)

            def test_broken_symlink_profile_is_not_missing(self):
                self.profile.parent.mkdir(parents=True)
                target = self.state / 'nonexistent-profile-target'
                self.profile.symlink_to(target)
                result = self.launch(None, hybrid=True)
                self.assertEqual(result.returncode, 0, self.messages(result))
                self.assertTrue(self.profile.is_symlink())
                self.assertFalse(target.exists())
                self.assertFalse((self.state / 'synthetic-local-started').exists())

        names = [n for n in FreshLocal.__dict__ if n.startswith('test_')]
        # Existing regressions stay at their original expectations.
        names += ['test_corrupt_profile_is_preserved', 'test_hybrid_models_entry_does_not_start_or_modify_local_profile',
                  'test_explicit_gpt_overrides_hybrid_package_without_local_start',
                  'test_gpt_missing_profile_keeps_native_entry_without_default_profile',
                  'test_check_is_read_only_without_bundled_model']
        suite = unittest.TestSuite(FreshLocal(n) for n in names)
        with (out / 'unittest.log').open('w') as log:
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
        receipt = {'level': 'COMPILED_LAUNCHER_STUB_HOST_AND_HEALTH_NOT_GUI_NOT_INFERENCE',
                   'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                   'fixture_source_sha256': hashlib.sha256(private.encode()).hexdigest(),
                   'isolated_paths': ['duplicate host process probe', 'per-user launcher mutex filename'],
                   'tests': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
                   'status': 'PASS' if result.wasSuccessful() else 'FAIL',
                   'test_ids': [f'FreshLocal.{n}' for n in names]}
        (out / 'receipt.json').write_text(json.dumps(receipt, indent=2))
        print(json.dumps(receipt))
        return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
