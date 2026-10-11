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
        subprocess.run(['codesign', '--force', '--sign', '-', str(self.source)], check=True,
                       capture_output=True)
        self.before = {p.relative_to(self.source).as_posix(): p.read_bytes()
                       for p in self.source.rglob('*') if p.is_file()}
        self.mirror = self.root / 'mirror'
        bundle = self.mirror / 'artifacts/muse-goals-0.4.0-rc5.bundle'
        bundle.mkdir(parents=True)
        (bundle / 'manifest.json').write_text('{}')
        (bundle / 'main.splash').write_text('// fixture')
        (self.mirror / 'catalog.json').write_text('{}')
        (self.mirror / 'artifacts/muse-goals-0.4.0-rc5.bundle.pack.json').write_text('{}')
        self.output = self.root / 'candidate'
        self.state = self.root / 'existing state'
        self.state.mkdir()
        (self.state / 'fixture-data').write_bytes(b'private fixture: never package')

    def package(self):
        args = ['package_app.py', '--sdk', str(self.root / 'fixture-sdk'),
                '--host', str(self.host), '--kernel', str(self.kernel),
                '--kernel-receipt', str(self.receipt), '--mirror', str(self.mirror),
                '--out', str(self.output), '--model-mode', 'gpt',
                '--paired-host-app', str(self.source), '--state-root', str(self.state)]
        helper = SimpleNamespace(kernel_tool=lambda: SimpleNamespace(octos_revision=lambda: 'fixture-pin'))
        with patch.object(sys, 'argv', args), patch.object(package_app, 'packaging', return_value=helper), \
                patch.object(package_app.subprocess, 'check_output', side_effect=AssertionError('Cargo forbidden')), \
                contextlib.redirect_stdout(io.StringIO()):
            package_app.main()

    def test_signed_pair_copies_exact_bytes_without_cargo_or_resigning(self):
        self.package()
        copied = self.output / 'Muse.app/Contents/Resources/OctoSense Host.app'
        after = {p.relative_to(copied).as_posix(): p.read_bytes()
                 for p in copied.rglob('*') if p.is_file()}
        self.assertEqual(after, self.before)
        record = json.loads((self.output / 'PACKAGE.json').read_text())
        self.assertEqual(record['version'], '0.4.0-rc5')
        self.assertTrue(record['reused_signed_pair'])
        self.assertEqual(record['source_host_sha256'], record['host_sha256'])
        self.assertEqual(record['source_kernel_sha256'], record['kernel_sha256'])
        inventory = json.loads((self.output / 'HOST_RESOURCES.json').read_text())
        self.assertEqual(inventory['makepad_widgets/resources/fixture-font.ttf'], package_app.sha(self.asset))
        info = plistlib.loads((self.output / 'Muse.app/Contents/Info.plist').read_bytes())
        self.assertEqual(info['CFBundleVersion'], '5')
        self.assertEqual(info['MuseHostLaunchMethod'], 'workbuddy')
        self.assertEqual(info['MuseStateRoot'], str(self.state))
        self.assertFalse(list(self.output.rglob('fixture-data')))
        self.assertEqual((self.state / 'fixture-data').read_bytes(), b'private fixture: never package')
        self.assertFalse((self.output / 'signed-kernel').exists())

    def test_mismatched_host_is_rejected(self):
        self.host = self.root / 'different-host'
        self.host.write_bytes(b'different fixture host')
        with self.assertRaisesRegex(AssertionError, 'Paired app Host mismatch'):
            self.package()

    def test_modified_signed_resource_is_rejected(self):
        self.asset.write_bytes(b'tampered fixture')
        with self.assertRaises(subprocess.CalledProcessError):
            self.package()

    def test_wrapper_resolves_spaces_clears_overrides_and_preserves_argv(self):
        self.package()
        resources = self.output / 'Muse.app/Contents/Resources'
        wrapper = resources / 'WorkBuddy Launcher.app/Contents/MacOS/Launcher'
        log = self.root / 'fixture-host.log'
        env = dict(os.environ, MUSE_HOST_LOG=str(log), MAKEPAD_APP_CONFIG='poison',
                   OCTOSENSE_HUB='/wrong')
        subprocess.run(['/bin/sh', str(wrapper), '--remote=9696', '--test-action',
                        'launch-muse-native-prototype', '--test-action', 'launch-hub:muse-goals'],
                       env=env, check=True, capture_output=True)
        lines = log.read_text().splitlines()
        self.assertEqual(lines[:5], ['--remote=9696', '--test-action',
                                    'launch-muse-native-prototype', '--test-action', 'launch-hub:muse-goals'])
        self.assertIn('HUB=' + str(resources / 'mirror'), lines)
        self.assertIn('APP_CONFIG=unset', lines)


if __name__ == '__main__':
    unittest.main()
