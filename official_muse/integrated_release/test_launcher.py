#!/usr/bin/env python3
"""Exercise the real compiled launcher with a signed stub Host, never a model/GUI."""
import fcntl
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import time
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
            'CFBundleExecutable': 'Launcher', 'CFBundleIdentifier': 'org.muse.launcher.fixture',
            'CFBundlePackageType': 'APPL', 'MuseModelMode': 'gpt',
        }))
        helper = macos / 'muse-launcher'
        cls.launcher = macos / 'Launcher'
        shutil.copy2(HERE / 'workbuddy_launcher.sh', cls.launcher)
        cls.launcher.chmod(0o755)
        (cls.resources / 'launcher.json').write_text(json.dumps({'model_mode':'gpt','state_root':None}))
        subprocess.run(['clang', '-fobjc-arc', '-O2', '-framework', 'AppKit',
                        str(HERE / 'muse_launcher.m'), '-o', str(helper)], check=True)
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
#include <unistd.h>
int main(int argc, char **argv) {
    for (int i=1; i<argc; ++i) puts(argv[i]);
    const char *names[] = {"HOME", "OCTOSENSE_HOME", "OCTOS_APP_CORE_DIR", "OCTOSENSE_APP_DATA", "XDG_DATA_HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "RINX_DATA_DIR", "ROBRIX_DATA_DIR", "OCTOSENSE_DEV_MODE", "OCTOSENSE_KERNEL_BIN", "OCTOSENSE_ALLOW_ANY_KERNEL_REVISION", "OCTOSENSE_CONTAINED_APPS", "MAKEPAD_REMOTE", "MAKEPAD_APP_CONFIG", "MAKEPAD_NO_GAUSS", "MAKEPAD_DISABLE_GAUSS", "MAKEPAD_HIDE_WINDOWS", "MAKEPAD_NO_FOCUS", "OCTOS_APP_CORE_BIN", "OCTOSENSE_KERNEL_ANY_REVISION", "MAKEPAD_FOCUS", "OCTOSENSE_HUB", "OCTOSENSE_HUB_ANCHOR", "OCTOSENSE_HUB_CATALOG", "MAKEPAD_SPLASH_BUDGET_MS", "MAKEPAD_STYLE", "MAKEPAD_SPLASH_THEME", "MAKEPAD_WM_TEST_APP"};
    for (unsigned i=0; i<sizeof(names)/sizeof(names[0]); ++i) printf("%s=%s\\n", names[i], getenv(names[i]) ? getenv(names[i]) : "<unset>");
    printf("ARGC=%d\\n", argc);
    const char *pid_file = getenv("MUSE_FIXTURE_PID_FILE");
    if (pid_file) { FILE *f=fopen(pid_file,"w"); fprintf(f,"%d",getpid()); fclose(f); }
    const char *delay = getenv("MUSE_FIXTURE_HOST_DELAY");
    if (delay) { fflush(stdout); sleep(atoi(delay)); }
    return 0;
}''')
        binary = host / 'MacOS/octosense'
        subprocess.run(['clang', str(source), '-o', str(binary)], check=True)
        shutil.copy2(binary, host / 'MacOS/octos-kernel')
        (host / 'Resources/octos-kernel.json').write_text('{}')
        mirror = cls.resources / 'mirror'
        bundle = mirror / 'artifacts/muse-goals-0.4.0-rc6.bundle'
        bundle.mkdir(parents=True)
        (bundle / 'manifest.json').write_text('{}')
        (bundle / 'main.splash').write_text('// fixture')
        (mirror / 'catalog.json').write_text('{}')
        (mirror / 'artifacts/muse-goals-0.4.0-rc6.bundle.pack.json').write_text('{}')
        for item in [host / 'MacOS/octos-kernel', host.parent, helper, cls.app]:
            subprocess.run(['codesign', '--force', '--sign', '-', str(item)], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cls.hybrid_app = cls.root / 'Hybrid.app'
        shutil.copytree(cls.app, cls.hybrid_app)
        hybrid_contents = cls.hybrid_app / 'Contents'
        info = plistlib.loads((hybrid_contents / 'Info.plist').read_bytes())
        info['MuseModelMode'] = 'hybrid'
        (hybrid_contents / 'Resources/launcher.json').write_text(json.dumps({'model_mode':'hybrid','state_root':None}))
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
        self.profile = self.state / 'kernel/.octos/profiles/_main.json'
        self.owner_home = self.root / 'owner-home'
        self.owner_home.mkdir(exist_ok=True)

    def write_profile(self, primary, fallbacks=None):
        self.profile.parent.mkdir(parents=True, exist_ok=True)
        self.profile.write_text(json.dumps({'id': '_main', 'enabled': True,
            'config': {'llm': {'primary': primary, 'fallbacks': fallbacks or []},
                       'env_vars': {}, 'preserve_this': 'fixture'}, 'unknown': 'preserve'}))
        return self.profile.read_bytes()

    def launch_env(self, updates=None):
        env = dict(os.environ, MUSE_INTEGRATED_STATE=str(self.state),
                   HOME=str(self.owner_home),
                   OCTOSENSE_KERNEL_BIN='/must/not/inherit', OCTOSENSE_CONTAINED_APPS='1',
                   OCTOSENSE_ALLOW_ANY_KERNEL_REVISION='1')
        for key, value in (updates or {}).items():
            if value is None:
                env.pop(key, None)
            else:
                env[key] = value
        return env

    def launch(self, flag, hybrid=False, env_updates=None):
        env = self.launch_env(env_updates)
        launcher = self.hybrid_app / 'Contents/MacOS/Launcher' if hybrid else self.launcher
        result = subprocess.run([str(launcher)] + ([flag] if flag else []), env=env, capture_output=True,
                                text=True, timeout=30)
        deadline = time.monotonic() + 10
        while list(self.state.glob('launch-*.ready')) and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertFalse(list(self.state.glob('launch-*.ready')), 'guardian cleanup timed out')
        return result

    def messages(self, result):
        log = self.state / 'logs/launcher.log'
        return result.stdout + (log.read_text() if log.exists() else '')

    def test_check_is_read_only_without_bundled_model(self):
        result = self.launch('--check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.state.exists())
        self.assertIn('未验证模型调用', self.messages(result))

    def test_missing_profile_requires_setup_without_writing(self):
        result = self.launch('--gpt-check')
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn('GPT_SETUP_REQUIRED', self.messages(result))
        self.assertFalse(self.state.exists())

    def test_native_gpt_metadata_does_not_validate_credentials(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o'})
        result = self.launch('--gpt-check')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('GPT_CONFIG_ONLY', self.messages(result))
        self.assertIn('实调尚未验证', self.messages(result))
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
        self.assertIn('launch-muse-native-prototype', (self.state / 'logs/host.log').read_text())
        self.assertFalse((self.state / 'logs/model.log').exists())

    def test_gpt_missing_profile_keeps_native_entry_without_default_profile(self):
        result = self.launch('--gpt')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.profile.exists())
        self.assertIn('launch-muse-native-prototype', (self.state / 'logs/host.log').read_text())

    def test_gpt_launch_uses_isolated_paths_and_no_gate_overrides(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o',
            'route': {'base_url': 'https://api.openai.com/v1', 'api_type': 'responses'}})
        result = self.launch('--gpt')
        self.assertEqual(result.returncode, 0, result.stderr)
        log = (self.state / 'logs/host.log').read_text()
        self.assertIn('launch-muse-native-prototype', log)
        self.assertIn('HOME=' + str(self.owner_home), log)
        self.assertIn('OCTOS_APP_CORE_DIR=' + str(self.state / 'kernel/.octos'), log)
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
        self.assertIn('launch-muse-native-prototype', (self.state / 'logs/host.log').read_text())

    def test_previous_installed_main_is_preserved_by_native_only_startup(self):
        self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o'})
        installed = self.state / 'apps/.bundles/muse-goals/bundle/main.splash'
        installed.parent.mkdir(parents=True)
        previous = b'// Previous rc4 installed fixture; requires normal Hub update'
        installed.write_bytes(previous)
        result = self.launch('--gpt')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('launch-muse-native-prototype', (self.state / 'logs/host.log').read_text())
        self.assertEqual(installed.read_bytes(), previous)

    def test_relative_state_rejected_without_creation(self):
        self.state = Path('relative-fixture-state')
        result = self.launch('--gpt-check')
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn('必须是绝对路径', result.stderr)

    def test_hybrid_missing_cloud_keeps_native_entry_without_local_start(self):
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('HYBRID_SETUP_REQUIRED', self.messages(result))
        self.assertFalse(self.profile.exists())
        self.assertFalse((self.state / 'synthetic-local-started').exists())
        self.assertIn('launch-muse-native-prototype', (self.state / 'logs/host.log').read_text())

    def test_hybrid_gpt_profile_preserved_and_local_service_lifecycle(self):
        before = self.write_profile({'family_id': 'openai', 'model_id': 'gpt-4o'})
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertIn('HYBRID_LOCAL_READY_ONLY', self.messages(result))
        status = json.loads((self.state / 'local-model.json').read_text())
        self.assertEqual(status['service_status'], 'stopped')
        self.assertFalse(status['native_local_selected'])
        self.assertFalse(status['inference_verified'])
        self.assertTrue((self.state / 'synthetic-local-started').exists())

    def test_hybrid_preserves_existing_local_route_bytes(self):
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
        self.assertFalse(status['native_local_selected'])
        self.assertTrue(status['configured_local_selection'])
        self.assertEqual(profile['config']['llm']['fallbacks'][0]['route']['base_url'], 'http://127.0.0.1:65534/v1')

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
        self.assertIn('GPT_CONFIG_ONLY', self.messages(result))
        self.assertFalse((self.state / 'synthetic-local-started').exists())

    def test_hybrid_minimax_cloud_profile_is_byte_preserved(self):
        before = self.write_profile({'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'})
        result = self.launch(None, hybrid=True)  # Double-click/default hybrid mode, no CLI override.
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertIn('HYBRID_LOCAL_READY_ONLY', self.messages(result))
        self.assertIn('launch-muse-native-prototype', (self.state / 'logs/host.log').read_text())
        self.assertTrue((self.state / 'synthetic-local-started').exists())

    def test_hybrid_minimax_existing_local_route_preserves_primary(self):
        primary = {'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'}
        self.write_profile(primary, [{'family_id': 'local', 'model_id': 'Qwen2.5-0.5B-Instruct-Q4_0-offline'}])
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(self.profile.read_text())['config']['llm']['primary'], primary)
        self.assertFalse(json.loads((self.state / 'local-model.json').read_text())['native_local_selected'])

    def test_workbuddy_environment_layout_and_native_first_argv(self):
        removed = ['MAKEPAD_REMOTE', 'MAKEPAD_HIDE_WINDOWS', 'MAKEPAD_NO_FOCUS',
                   'MAKEPAD_NO_GAUSS', 'MAKEPAD_DISABLE_GAUSS', 'MAKEPAD_SPLASH_BUDGET_MS',
                   'MAKEPAD_STYLE', 'MAKEPAD_SPLASH_THEME', 'MAKEPAD_WM_TEST_APP',
                   'MAKEPAD_APP_CONFIG', 'OCTOSENSE_CONTAINED_APPS', 'OCTOS_APP_CORE_BIN',
                   'OCTOSENSE_KERNEL_ANY_REVISION', 'OCTOSENSE_KERNEL_BIN']
        env = {key: 'fixture-poison' for key in removed}
        env.update(MUSE_INTEGRATED_REMOTE='9693', OCTOSENSE_HUB='/fixture/wrong',
                   OCTOSENSE_HUB_ANCHOR='wrong', OCTOSENSE_HUB_CATALOG='wrong')
        result = self.launch('--models', env_updates=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = (self.state / 'logs/host.log').read_text().splitlines()
        self.assertEqual(lines[:3], ['--remote=9693', '--test-action', 'launch-muse-native-prototype'])
        self.assertIn('ARGC=4', lines)
        for key in removed:
            self.assertIn(key + '=<unset>', lines)
        expected = {'HOME': self.owner_home, 'OCTOSENSE_HOME': self.state / 'shell',
                    'OCTOS_APP_CORE_DIR': self.state / 'kernel/.octos',
                    'OCTOSENSE_APP_DATA': self.state / 'apps',
                    'RINX_DATA_DIR': self.state / 'rinx', 'ROBRIX_DATA_DIR': self.state / 'rinx',
                    'XDG_CONFIG_HOME': self.state / 'config', 'XDG_DATA_HOME': self.state / 'data',
                    'XDG_CACHE_HOME': self.state / 'cache', 'OCTOSENSE_HUB': self.resources / 'mirror'}
        for key, value in expected.items():
            self.assertIn(key + '=' + str(value), lines)
        self.assertIn('MAKEPAD_FOCUS=1', lines)
        self.assertIn('OCTOSENSE_HUB_CATALOG=legacy', lines)
        self.assertIn('OCTOSENSE_HUB_ANCHOR=543ffbe45b6700c23e1824157ea694f8bd7839090e0ede464c11758d350b1412', lines)
        self.assertFalse((self.state / 'home').exists())

    def test_default_state_is_portable_beside_app(self):
        state = self.app.parent / 'Muse Data'
        self.assertFalse(state.exists())
        result = self.launch('--models', env_updates={'MUSE_INTEGRATED_STATE': None,
                                                     'MUSE_INTEGRATED_REMOTE': None})
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = (state / 'logs/host.log').read_text().splitlines()
        self.assertEqual(lines[0], '--remote=9696')
        self.assertIn('OCTOSENSE_HOME=' + str(state / 'shell'), lines)
        self.assertIn('HOME=' + str(self.owner_home), lines)
        self.assertFalse((state / 'kernel/.octos/profiles/_main.json').exists())

    def test_packaged_state_reference_reuses_paths_without_copying_profile(self):
        before = self.write_profile({'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'})
        app = self.root / 'State reference.app'
        shutil.copytree(self.app, app)
        info_path = app / 'Contents/Info.plist'
        info = plistlib.loads(info_path.read_bytes())
        info['MuseStateRoot'] = str(self.state)
        (app / 'Contents/Resources/launcher.json').write_text(json.dumps({'model_mode':'gpt','state_root':str(self.state)}))
        info_path.write_bytes(plistlib.dumps(info))
        subprocess.run(['codesign', '--force', '--sign', '-', str(app)], check=True,
                       capture_output=True)
        env = self.launch_env({'MUSE_INTEGRATED_STATE': None})
        result = subprocess.run([str(app / 'Contents/MacOS/Launcher'), '--models'],
                                env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.read_bytes(), before)
        self.assertIn('OCTOSENSE_HOME=' + str(self.state / 'shell'),
                      (self.state / 'logs/host.log').read_text())

    def test_repository_and_packaged_script_use_same_launcher(self):
        env = self.launch_env()
        result = subprocess.run(['/bin/sh', str(HERE / 'launch_muse.sh'), str(self.app),
                                 '--check'], env=env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(self.state.exists())
        portable = self.root / 'portable package with spaces'
        portable.mkdir()
        shutil.copytree(self.app, portable / 'Muse.app')
        shutil.copy2(HERE / 'launch_muse.sh', portable / 'launch_muse.sh')
        second = subprocess.run(['/bin/sh', str(portable / 'launch_muse.sh'),
                                 str(portable / 'Muse.app'), '--check'], env=env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(second.stdout, result.stdout)
        self.assertEqual((self.app / 'Contents/MacOS/Launcher').read_bytes(),
                         (portable / 'Muse.app/Contents/MacOS/Launcher').read_bytes())
        self.assertIn('/usr/bin/open -n -W', (HERE / 'launch_muse.sh').read_text())

    def test_existing_host_and_model_errors_are_preserved(self):
        self.write_profile({'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'})
        logs = self.state / 'logs'
        logs.mkdir()
        (logs / 'host.log').write_text('previous Host error\n')
        (logs / 'model.log').write_text('previous model error\n')
        result = self.launch('--hybrid', hybrid=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((logs / 'host.log').read_text().startswith('previous Host error\n'))
        self.assertTrue((logs / 'model.log').read_text().startswith('previous model error\n'))

    def test_launcher_holds_one_host_lock_until_exit(self):
        pid_file = self.state / 'host-pid'
        env = self.launch_env({'MUSE_FIXTURE_HOST_DELAY': '3', 'MUSE_FIXTURE_PID_FILE': str(pid_file)})
        process = subprocess.Popen([str(self.launcher), '--models'], env=env,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            log = self.state / 'logs/host.log'
            limit = time.monotonic() + 5
            while not log.exists() and time.monotonic() < limit:
                time.sleep(0.02)
            self.assertTrue(log.exists())
            ready = next(self.state.glob('launch-*.ready'))
            self.assertEqual(json.loads(ready.read_text())['owner_pid'], int(pid_file.read_text()))
            duplicate = subprocess.run([str(self.launcher), '--models'], env=env,
                                       capture_output=True, text=True, timeout=5)
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertEqual(log.read_text().splitlines().count('launch-muse-native-prototype'), 1)
            with (self.state / 'launch.flock').open('r') as lock:
                with self.assertRaises(BlockingIOError):
                    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                stdout, stderr = process.communicate(timeout=10)
                self.assertEqual(process.returncode, 0, stderr)
                deadline = time.monotonic() + 5
                while ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.05)
                self.assertFalse(ready.exists())
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=10)

    def test_host_signal_exit_cleans_model_and_lock_preserving_profile(self):
        before = self.write_profile({'family_id': 'minimax-cn', 'model_id': 'MiniMax-M3'})
        env = self.launch_env({'MUSE_FIXTURE_HOST_DELAY': '30'})
        process = subprocess.Popen([str(self.hybrid_app / 'Contents/MacOS/Launcher')],
                                   env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            deadline = time.monotonic() + 8
            while not list(self.state.glob('launch-*.ready')) and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue(list(self.state.glob('launch-*.ready')))
            status = json.loads((self.state / 'local-model.json').read_text())
            process.terminate()
            process.communicate(timeout=5)
            deadline = time.monotonic() + 5
            while list(self.state.glob('launch-*.ready')) and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertFalse(list(self.state.glob('launch-*.ready')))
            self.assertEqual(self.profile.read_bytes(), before)
            with self.assertRaises(ProcessLookupError):
                os.kill(status['pid'], 0)
            with (self.state / 'launch.flock').open('r') as lock:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        finally:
            if process.poll() is None:
                process.terminate()
                process.communicate(timeout=5)


if __name__ == '__main__':
    unittest.main()
