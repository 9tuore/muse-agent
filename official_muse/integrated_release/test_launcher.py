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
        cls.hybrid_app = cls.root / 'Hybrid.app'
        shutil.copytree(cls.app, cls.hybrid_app)
        hybrid_contents = cls.hybrid_app / 'Contents'
        info = plistlib.loads((hybrid_contents / 'Info.plist').read_bytes())
        info['MuseModelMode'] = 'hybrid'
        (hybrid_contents / 'Info.plist').write_bytes(plistlib.dumps(info))
        local = hybrid_contents / 'Resources/local-model'
        (local / 'llama').mkdir(parents=True)
        stub = local / 'llama/llama-server'
        # Synthetic health endpoint only, not Qwen inference or a cloud request.
        stub.write_text('''#!/usr/bin/python3
import os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
Path(os.environ['HOME'], 'synthetic-local-started').write_text('fixture only')
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200 if self.path == '/health' else 404)
        self.end_headers()
        self.wfile.write(b'fixture')
    def log_message(self, *args): pass
port=int(sys.argv[sys.argv.index('--port')+1])
HTTPServer(('127.0.0.1', port), Handler).serve_forever()
''')
        stub.chmod(0o755)
        (local / 'qwen2.5-0.5b-instruct-q4_0.gguf').write_text('Synthetic fixture, not model weights')
        subprocess.run(['codesign', '--force', '--sign', '-', str(cls.hybrid_app)], check=True,
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

    def launch(self, flag, hybrid=False):
        env = dict(os.environ, MUSE_INTEGRATED_STATE=str(self.state),
                   OCTOSENSE_KERNEL_BIN='/must/not/inherit', OCTOSENSE_CONTAINED_APPS='1',
                   OCTOSENSE_ALLOW_ANY_KERNEL_REVISION='1')
        launcher = self.hybrid_app / 'Contents/MacOS/muse-launcher' if hybrid else self.launcher
        return subprocess.run([str(launcher)] + ([flag] if flag else []), env=env, capture_output=True,
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

    def test_hybrid_missing_cloud_opens_models_without_local_start(self):
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('HYBRID_SETUP_REQUIRED', result.stdout)
        self.assertFalse(self.profile.exists())
        self.assertFalse((self.state / 'synthetic-local-started').exists())
        self.assertIn('launch-ai-providers', (self.state / 'logs/host.log').read_text())

    def test_hybrid_gpt_profile_preserved_and_local_service_lifecycle(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o'})
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertIn('HYBRID_LOCAL_READY_ONLY', result.stdout)
        status = json.loads((self.state / 'local-model.json').read_text())
        self.assertEqual(status['service_status'], 'stopped')
        self.assertFalse(status['native_local_selected'])
        self.assertFalse(status['inference_verified'])
        self.assertTrue((self.state / 'synthetic-local-started').exists())

    def test_hybrid_updates_only_existing_local_selection(self):
        primary = {'family_id': 'openai', 'model_id': 'gpt-4o', 'route': {'api_type': 'responses'}}
        self.write_profile(primary, [{'family_id': 'local', 'model_id': 'Qwen2.5-0.5B-Instruct-Q4_0-offline',
            'route': {'base_url': 'http://127.0.0.1:65534/v1', 'api_type': 'openai'}}])
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        profile = json.loads(self.profile.read_text())
        self.assertEqual(profile['config']['llm']['primary'], primary)
        self.assertEqual(profile['config']['env_vars'], {})
        self.assertEqual(profile['config']['preserve_this'], 'fixture')
        status = json.loads((self.state / 'local-model.json').read_text())
        self.assertTrue(status['native_local_selected'])
        self.assertEqual(profile['config']['llm']['fallbacks'][0]['route']['base_url'], status['route_base_url'])

    def test_hybrid_models_entry_does_not_start_or_modify_local_profile(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o'},
            [{'family_id': 'local', 'model_id': 'Qwen2.5-0.5B-Instruct-Q4_0-offline'}])
        result = self.launch('--models', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertFalse((self.state / 'synthetic-local-started').exists())

    def test_explicit_gpt_overrides_hybrid_package_without_local_start(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o'})
        result = self.launch('--gpt', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertIn('GPT_CONFIG_ONLY', result.stdout)
        self.assertFalse((self.state / 'synthetic-local-started').exists())

    def test_hybrid_minimax_cloud_profile_is_byte_preserved(self):
        before = self.write_profile({'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'})
        result = self.launch(None, hybrid=True)  # Double-click/default hybrid mode, no CLI override.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertIn('HYBRID_LOCAL_READY_ONLY', result.stdout)
        self.assertIn('launch-apphub', (self.state / 'logs/host.log').read_text())
        self.assertTrue((self.state / 'synthetic-local-started').exists())

    def test_hybrid_minimax_existing_local_route_preserves_primary(self):
        primary = {'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'}
        self.write_profile(primary, [{'family_id': 'local', 'model_id': 'Qwen2.5-0.5B-Instruct-Q4_0-offline'}])
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.profile.read_text())['config']['llm']['primary'], primary)
        self.assertTrue(json.loads((self.state / 'local-model.json').read_text())['native_local_selected'])


if __name__ == '__main__':
    unittest.main()
