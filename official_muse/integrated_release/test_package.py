#!/usr/bin/env python3
"""Signed synthetic pair fixtures; no Cargo, LaunchServices, GUI or real model."""
import contextlib
import io
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import package_app


class PairedPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='muse-paired-package-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'Signed Host.app'
        self.inner = self.source / 'Contents'
        (self.inner / 'MacOS').mkdir(parents=True)
        (self.inner / 'Resources/makepad_widgets/resources').mkdir(parents=True)
        (self.inner / 'Info.plist').write_bytes(plistlib.dumps({
            'CFBundleExecutable': 'octosense', 'CFBundleIdentifier': 'org.muse.package.fixture',
            'CFBundlePackageType': 'APPL'}))
        source_c = self.root / 'host.c'
        source_c.write_text('''#include <stdio.h>
#include <stdlib.h>
int main(int argc, char **argv) {
    for (int i=1; i<argc; ++i) puts(argv[i]);
    printf("HUB=%s\\n", getenv("OCTOSENSE_HUB"));
    printf("APP_CONFIG=%s\\n", getenv("MAKEPAD_APP_CONFIG") ? "inherited" : "unset");
    return 0;
}''')
        self.host = self.inner / 'MacOS/octosense'
        self.kernel = self.inner / 'MacOS/octos-kernel'
        subprocess.run(['clang', str(source_c), '-o', str(self.host)], check=True)
        shutil.copy2(self.host, self.kernel)
        subprocess.run(['codesign', '--force', '--sign', '-', str(self.kernel)], check=True,
                       capture_output=True)
        self.receipt = self.inner / 'Resources/octos-kernel.json'
        self.receipt.write_text(json.dumps({'revision': 'fixture-pin',
                                           'sha256': package_app.sha(self.kernel)}))
        self.asset = self.inner / 'Resources/makepad_widgets/resources/fixture-font.ttf'
        self.asset.write_bytes(b'synthetic font resource')
        host_asset = self.inner / 'Resources/octosense/resources/fixture-host.txt'
        host_asset.parent.mkdir(parents=True)
        host_asset.write_bytes(b'synthetic Host resource namespace')
        subprocess.run(['codesign', '--force', '--sign', '-', str(self.source)], check=True,
                       capture_output=True)
        self.before = {p.relative_to(self.source).as_posix(): p.read_bytes()
                       for p in self.source.rglob('*') if p.is_file()}
        self.mirror = self.root / 'mirror'
        bundle = self.mirror / 'artifacts/muse-goals-0.4.0-rc13.bundle'
        bundle.mkdir(parents=True)
        (bundle / 'manifest.json').write_text('{}')
        (bundle / 'main.splash').write_text('// fixture')
        (self.mirror / 'catalog.json').write_text('{}')
        (self.mirror / 'artifacts/muse-goals-0.4.0-rc13.bundle.pack.json').write_text('{}')
        self.output = self.root / 'candidate'
        self.state = self.root / 'existing state'
        self.state.mkdir()
        (self.state / 'fixture-data').write_bytes(b'private fixture: never package')

    def package(self, apfs_clone=False, model_source=None):
        args = ['package_app.py', '--sdk', str(self.root / 'fixture-sdk'),
                '--host', str(self.host), '--kernel', str(self.kernel),
                '--kernel-receipt', str(self.receipt), '--mirror', str(self.mirror),
                '--out', str(self.output), '--model-mode', 'gpt',
                '--paired-host-app', str(self.source), '--state-root', str(self.state)]
        if apfs_clone:
            args.append('--apfs-clone')
        if model_source is not None:
            args[args.index('--model-mode') + 1] = 'hybrid'
            args.extend(['--model-source', str(model_source)])
        helper = SimpleNamespace(kernel_tool=lambda: SimpleNamespace(octos_revision=lambda: 'fixture-pin'))
        with patch.object(sys, 'argv', args), patch.object(package_app, 'packaging', return_value=helper), \
                patch.object(package_app.subprocess, 'check_output', side_effect=AssertionError('Cargo forbidden')), \
                contextlib.redirect_stdout(io.StringIO()):
            package_app.main()

    def test_resources_and_kernel_survive_standalone_host_resign_without_cargo(self):
        self.package()
        resources = self.output / 'Muse.app/Contents/Resources'
        runtime = resources / 'host-runtime'
        self.assertFalse((resources / 'OctoSense Host.app').exists())
        self.assertFalse((runtime / 'Info.plist').exists())
        self.assertEqual((runtime / 'octosense/resources/fixture-host.txt').read_bytes(),
                         b'synthetic Host resource namespace')
        self.assertEqual((runtime / 'octos-kernel').read_bytes(), self.kernel.read_bytes())
        expected = {p.relative_to(self.inner / 'Resources').as_posix(): p.read_bytes()
                    for p in (self.inner / 'Resources').rglob('*') if p.is_file()}
        actual = {p.relative_to(runtime).as_posix(): p.read_bytes()
                  for p in runtime.rglob('*') if p.is_file()
                  and p not in (runtime / 'muse-host', runtime / 'octos-kernel')}
        self.assertEqual(actual, expected)
        self.assertEqual({p.relative_to(self.source).as_posix(): p.read_bytes()
                          for p in self.source.rglob('*') if p.is_file()}, self.before)
        subprocess.run(['codesign', '--verify', '--strict', str(runtime / 'muse-host')],
                       check=True, capture_output=True)
        record = json.loads((self.output / 'PACKAGE.json').read_text())
        self.assertEqual(record['version'], '0.4.0-rc13')
        self.assertFalse(record['reused_signed_pair'])
        self.assertTrue(record['reused_signed_kernel'])
        self.assertTrue(record['standalone_host'])
        self.assertEqual(record['source_host_sha256'], package_app.sha(self.host))
        self.assertEqual(record['host_sha256'], package_app.sha(runtime / 'muse-host'))
        self.assertNotEqual(record['source_host_sha256'], record['host_sha256'])
        self.assertEqual(record['source_kernel_sha256'], record['kernel_sha256'])
        inventory = json.loads((self.output / 'HOST_RESOURCES.json').read_text())
        self.assertEqual(inventory['makepad_widgets/resources/fixture-font.ttf'], package_app.sha(self.asset))
        self.assertNotIn('muse-host', inventory)
        self.assertNotIn('octos-kernel', inventory)
        info = plistlib.loads((self.output / 'Muse.app/Contents/Info.plist').read_bytes())
        self.assertEqual((self.output / 'Muse.app/Contents/Info.plist').read_bytes(),
                         (package_app.HERE / 'workbuddy_info.plist').read_bytes())
        self.assertEqual(info['CFBundleExecutable'], 'Launcher')
        settings = json.loads((self.output / 'Muse.app/Contents/Resources/launcher.json').read_text())
        self.assertEqual(settings['state_root'], str(self.state))
        self.assertFalse((self.output / 'Muse.app/Contents/Resources/WorkBuddy Launcher.app').exists())
        self.assertEqual(record['source_launcher_sha256'], record['packaged_launcher_sha256'])
        self.assertFalse(list(self.output.rglob('fixture-data')))
        self.assertEqual((self.state / 'fixture-data').read_bytes(), b'private fixture: never package')
        self.assertFalse((self.output / 'signed-kernel').exists())

    def test_mismatched_host_release_receipt_is_rejected_before_packaging(self):
        receipt = self.host.with_name(self.host.name + '.release-identity.json')
        receipt.write_text(json.dumps({'release_tag': 'desktop-fixture', 'sha256': '0' * 64}))
        with self.assertRaisesRegex(AssertionError, 'Host release receipt mismatch'):
            self.package()
        self.assertFalse(self.output.exists())

    @unittest.skipUnless(sys.platform == 'darwin', 'Explicit APFS clone requires macOS')
    def test_apfs_clone_hybrid_model_and_resources_are_independent(self):
        model = self.root / 'synthetic model'
        (model / 'llama').mkdir(parents=True)
        server = model / 'llama/llama-server'
        server.write_bytes(b'#!/bin/sh\nexit 99 # fixture, never invoked\n')
        server.chmod(0o751)
        weight = model / 'qwen2.5-0.5b-instruct-q4_0.gguf'
        weight.write_bytes(b'synthetic weight: no inference')
        alias = model / 'existing-weight-link'
        alias.symlink_to(weight.name)
        model_before = {p.relative_to(model).as_posix(): package_app.sha(p)
                        for p in model.rglob('*') if p.is_file()}
        self.package(apfs_clone=True, model_source=model)
        resources = self.output / 'Muse.app/Contents/Resources'
        copied_model = resources / 'local-model'
        runtime = resources / 'host-runtime'
        record = json.loads((self.output / 'PACKAGE.json').read_text())
        self.assertEqual(record['directory_copy_mode'], 'apfs_clone_requested')
        self.assertEqual(len(record['directory_copies']), 4)
        self.assertTrue(all(r['filesystem'] == 'apfs' and r['returncode'] == 0
                            for r in record['directory_copies']))
        for source, target in [(weight, copied_model / weight.name),
                               (server, copied_model / 'llama/llama-server'),
                               (self.asset, runtime / 'makepad_widgets/resources/fixture-font.ttf')]:
            self.assertEqual(package_app.sha(target), package_app.sha(source))
            self.assertNotEqual(source.stat().st_ino, target.stat().st_ino)
            self.assertEqual(target.stat().st_nlink, 1)
            self.assertEqual(source.stat().st_mode, target.stat().st_mode)
        self.assertTrue((copied_model / alias.name).is_symlink())
        self.assertEqual(os.readlink(copied_model / alias.name), weight.name)
        self.assertEqual((copied_model / alias.name).resolve(), (copied_model / weight.name).resolve())
        (copied_model / weight.name).write_bytes(b'fixture copy mutation')
        (runtime / 'makepad_widgets/resources/fixture-font.ttf').write_bytes(b'fixture resource copy mutation')
        self.assertEqual({p.relative_to(model).as_posix(): package_app.sha(p)
                          for p in model.rglob('*') if p.is_file()}, model_before)
        self.assertEqual({p.relative_to(self.source).as_posix(): p.read_bytes()
                          for p in self.source.rglob('*') if p.is_file()}, self.before)

    def test_mismatched_host_is_rejected(self):
        self.host = self.root / 'different-host'
        self.host.write_bytes(b'different fixture host')
        with self.assertRaisesRegex(AssertionError, 'Paired app Host mismatch'):
            self.package()

    def test_modified_signed_resource_is_rejected(self):
        self.asset.write_bytes(b'tampered fixture')
        with self.assertRaises(subprocess.CalledProcessError):
            self.package()

    def test_wrapper_resolves_spaces_clears_overrides_and_ignores_extra_args(self):
        self.package()
        resources = self.output / 'Muse.app/Contents/Resources'
        wrapper = self.output / 'Muse.app/Contents/MacOS/Launcher'
        log = self.state / 'logs/host.log'
        env = dict(os.environ, MAKEPAD_APP_CONFIG='poison',
                   OCTOSENSE_HUB='/wrong')
        subprocess.run(['/bin/sh', str(wrapper), '--remote=9798', '--test-action',
                        'launch-muse-native-prototype', '--test-action', 'launch-forbidden-fixture-app'],
                       env=env, check=True, capture_output=True)
        lines = log.read_text().splitlines()
        self.assertEqual(lines[:5], ['--remote=9696', '--test-action', 'launch-apphub', '--test-action', 'launch-hub:muse-goals'])
        self.assertNotIn('launch-forbidden-fixture-app', lines)
        self.assertNotIn('launch-muse-native-prototype', lines)
        self.assertNotIn('--remote=9798', lines)
        self.assertIn('HUB=' + str(resources / 'mirror'), lines)
        self.assertIn('APP_CONFIG=unset', lines)
        deadline = time.monotonic() + 5
        while list(self.state.glob('launch-*.ready')) and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertFalse(list(self.state.glob('launch-*.ready')))


if __name__ == '__main__':
    unittest.main()
