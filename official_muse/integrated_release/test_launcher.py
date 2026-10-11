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
        host = cls.resources / 'host-runtime'
        host.mkdir()
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
        binary = cls.root / 'stub-octosense'
        subprocess.run(['clang', str(source), '-o', str(binary)], check=True)
        subprocess.run(['codesign', '--force', '--sign', '-', '--identifier',
                        'org.xinghai.muse.paired-host', str(binary)], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        shutil.copy2(binary, host / 'muse-host')
        shutil.copy2(binary, host / 'octos-kernel')
        (host / 'octos-kernel.json').write_text('{}')
        mirror = cls.resources / 'mirror'
        bundle = mirror / 'artifacts/muse-goals-0.4.0-rc6.bundle'
        bundle.mkdir(parents=True)
        (bundle / 'manifest.json').write_text('{}')
        (bundle / 'main.splash').write_text('// fixture')
        (mirror / 'catalog.json').write_text('{}')
        (mirror / 'artifacts/muse-goals-0.4.0-rc6.bundle.pack.json').write_text('{}')
        for item in [host / 'octos-kernel', helper, cls.app]:
