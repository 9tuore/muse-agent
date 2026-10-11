#!/usr/bin/env python3
"""Exercise the real compiled launcher with a signed stub Host, never a model/GUI."""
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


class LauncherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='muse-gpt-launcher-')
        cls.root = Path(cls.temp.name)
        cls.app = cls.root / 'Muse.app'
        contents = cls.app / 'Contents'
        macos = contents / 'MacOS'
        macos.mkdir(parents=True)
        cls.resources = contents / 'Resources'
        cls.resources.mkdir()
        (contents / 'Info.plist').write_bytes(plistlib.dumps({
            'CFBundleExecutable': 'muse-launcher', 'CFBundleIdentifier': 'org.muse.launcher.fixture',
            'CFBundlePackageType': 'APPL', 'MuseModelMode': 'gpt',
        }))
        cls.launcher = macos / 'muse-launcher'
        subprocess.run(['clang', '-fobjc-arc', '-O2', '-framework', 'AppKit',
                        str(HERE / 'muse_launcher.m'), '-o', str(cls.launcher)], check=True)
        host = cls.resources / 'OctoSense Host.app/Contents'
        (host / 'MacOS').mkdir(parents=True)
        (host / 'Resources').mkdir()
        (host / 'Info.plist').write_bytes(plistlib.dumps({
            'CFBundleExecutable': 'octosense', 'CFBundleIdentifier': 'org.muse.host.fixture',
            'CFBundlePackageType': 'APPL',
        }))
        source = cls.root / 'host.c'
        source.write_text('''#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    for (int i=1; i<argc; ++i) puts(argv[i]);
    const char *names[] = {"HOME", "OCTOSENSE_HOME", "OCTOS_APP_CORE_DIR", "OCTOSENSE_APP_DATA", "XDG_DATA_HOME", "OCTOSENSE_DEV_MODE", "OCTOSENSE_KERNEL_BIN", "OCTOSENSE_ALLOW_ANY_KERNEL_REVISION", "OCTOSENSE_CONTAINED_APPS"};
    for (int i=0; i<9; ++i) printf("%s=%s\\n", names[i], getenv(names[i]) ? getenv(names[i]) : "<unset>");
    return 0;
}''')
        binary = host / 'MacOS/octosense'
        subprocess.run(['clang', str(source), '-o', str(binary)], check=True)
        shutil.copy2(binary, host / 'MacOS/octos-kernel')
        (host / 'Resources/octos-kernel.json').write_text('{}')
        mirror = cls.resources / 'mirror'
        bundle = mirror / 'artifacts/muse-goals-0.4.0-rc3.bundle'
        bundle.mkdir(parents=True)
        (bundle / 'manifest.json').write_text('{}')
        (bundle / 'main.splash').write_text('// fixture')
        (mirror / 'catalog.json').write_text('{}')
        (mirror / 'artifacts/muse-goals-0.4.0-rc3.bundle.pack.json').write_text('{}')
        for item in [host / 'MacOS/octos-kernel', host.parent, cls.app]:
            subprocess.run(['codesign', '--force', '--sign', '-', str(item)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.state = self.root / self._testMethodName
        self.profile = self.state / 'home/octos-home/.octos/profiles/_main.json'

    def write_profile(self, primary, fallbacks=None):
        self.profile.parent.mkdir(parents=True, exist_ok=True)
        self.profile.write_text(json.dumps({'id': '_main', 'enabled': True,
            'config': {'llm': {'primary': primary, 'fallbacks': fallbacks or []},
                       'env_vars': {}, 'preserve_this': 'fixture'}, 'unknown': 'preserve'}))
        return self.profile.read_bytes()

    def launch(self, flag):
        env = dict(os.environ, MUSE_INTEGRATED_STATE=str(self.state),
                   OCTOSENSE_KERNEL_BIN='/must/not/inherit', OCTOSENSE_CONTAINED_APPS='1',
                   OCTOSENSE_ALLOW_ANY_KERNEL_REVISION='1')
        return subprocess.run([str(self.launcher), flag], env=env, capture_output=True,
                              text=True, timeout=30)

    def test_check_is_read_only_without_bundled_model(self):
        result = self.launch('--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.state.exists())
        self.assertIn('未验证模型调用', result.stdout)

    def test_missing_profile_requires_setup_without_writing(self):
        result = self.launch('--gpt-check')
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn('GPT_SETUP_REQUIRED', result.stdout)
        self.assertFalse(self.state.exists())

    def test_native_gpt_metadata_does_not_validate_credentials(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o'})
        result = self.launch('--gpt-check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('GPT_CONFIG_ONLY', result.stdout)
        self.assertIn('实调尚未验证', result.stdout)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertFalse((self.state / 'launch.flock').exists())

    def test_compatible_and_non_gpt_fallbacks_are_rejected(self):
        for primary, fallbacks in [
            ({'family_id': 'local', 'model_id': 'gpt-4o', 'route': {'api_type': 'openai'}}, []),
            ({'family_id': 'openai', 'model_id': 'gpt-4o', 'route': {'base_url': 'http://127.0.0.1:8080/v1'}}, []),
            ({'family_id': 'openai', 'model_id': 'gpt-4o'}, [{'family_id': 'local', 'model_id': 'Qwen2.5-0.5B-Instruct-Q4_0-offline'}]),
            ({'family_id': 'openai', 'model_id': 'gpt-4o'}, ['malformed']),
        ]:
            before = self.write_profile(primary, fallbacks)
            result = self.launch('--gpt-check')
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertEqual(self.profile.read_bytes(), before)

    def test_models_preserves_existing_profile_and_skips_qwen(self):
        before = self.write_profile({'family_id': 'local', 'model_id': 'Qwen2.5-0.5B-Instruct-Q4_0-offline'})
        result = self.launch('--models')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertIn('launch-ai-providers', (self.state / 'logs/host.log').read_text())
        self.assertFalse((self.state / 'logs/model.log').exists())

    def test_gpt_missing_profile_opens_models_without_default_profile(self):
        result = self.launch('--gpt')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.profile.exists())
        self.assertIn('launch-ai-providers', (self.state / 'logs/host.log').read_text())

    def test_gpt_launch_uses_isolated_paths_and_no_gate_overrides(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o',
            'route': {'base_url': 'https://api.openai.com/v1', 'api_type': 'responses'}})
        result = self.launch('--gpt')
        self.assertEqual(result.returncode, 0, result.stderr)
        log = (self.state / 'logs/host.log').read_text()
        self.assertIn('launch-apphub', log)
        self.assertIn('HOME=' + str(self.state), log)
        self.assertIn('OCTOS_APP_CORE_DIR=' + str(self.state / 'home/octos-home/.octos'), log)
        self.assertIn('OCTOSENSE_APP_DATA=' + str(self.state / 'apps'), log)
        self.assertIn('OCTOSENSE_DEV_MODE=0', log)
        self.assertIn('OCTOSENSE_KERNEL_BIN=<unset>', log)
        self.assertIn('OCTOSENSE_ALLOW_ANY_KERNEL_REVISION=<unset>', log)
        self.assertIn('OCTOSENSE_CONTAINED_APPS=<unset>', log)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertFalse((self.state / 'logs/model.log').exists())

    def test_corrupt_profile_is_preserved(self):
        self.profile.parent.mkdir(parents=True)
        self.profile.write_text('invalid fixture')
        result = self.launch('--gpt')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_text(), 'invalid fixture')
        self.assertIn('launch-ai-providers', (self.state / 'logs/host.log').read_text())

    def test_relative_state_rejected_without_creation(self):
        self.state = Path('relative-fixture-state')
        result = self.launch('--gpt-check')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('必须是绝对路径', result.stderr)


if __name__ == '__main__':
    unittest.main()
