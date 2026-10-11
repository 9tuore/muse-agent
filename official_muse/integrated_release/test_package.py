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
        bundle = self.mirror / 'artifacts/muse-goals-0.4.0-rc6.bundle'
        bundle.mkdir(parents=True)
        (bundle / 'manifest.json').write_text('{}')
        (bundle / 'main.splash').write_text('// fixture')
        (self.mirror / 'catalog.json').write_text('{}')
        (self.mirror / 'artifacts/muse-goals-0.4.0-rc6.bundle.pack.json').write_text('{}')
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
        self.assertEqual(record['version'], '0.4.0-rc6')
        self.assertFalse(record['reused_signed_pair'])
        self.assertTrue(record['reused_signed_kernel'])
        self.assertTrue(record['standalone_host'])
        self.assertEqual(record['source_host_sha256'], package_app.sha(self.host))
        self.assertEqual(record['host_sha256'], package_app.sha(runtime / 'muse-host'))
        self.assertNotEqual(record['source_host_sha256'], record['host_sha256'])
