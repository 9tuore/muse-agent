#!/usr/bin/env python3
"""Install test-only code into the second copy, preserving frozen Host source."""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / 'official_muse/app/build/ui-memory-20261003/mail-host-033/OctoSense'
COPY = SOURCE.parent.parent / 'host-mail-format-tests/OctoSense'
REL = Path('apps/mail/host-service/src/lib.rs')
before = (SOURCE / REL).read_text()
assert (COPY / REL).read_text() == before, 'refuse to patch an already modified copy'
after = before + '\n#[cfg(test)]\nmod overnight_mail_formats;\n'
(COPY / REL).write_text(after)
test_file = HERE / 'overnight_mail_formats.rs'
(COPY / REL.parent / test_file.name).write_bytes(test_file.read_bytes())
patch = ''.join(difflib.unified_diff(before.splitlines(keepends=True), after.splitlines(keepends=True),
                                   fromfile='a/'+str(REL), tofile='b/'+str(REL)))
new_rel = str(REL.parent / test_file.name)
patch += ''.join(difflib.unified_diff([], test_file.read_text().splitlines(keepends=True),
                                    fromfile='/dev/null', tofile='b/'+new_rel))
(HERE / 'test-only.patch').write_text(patch)
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(COPY / 'apps/mail/host-service/src/network.rs') == sha(SOURCE / 'apps/mail/host-service/src/network.rs')
(HERE / 'test_source.json').write_text(json.dumps({
    'frozen_source': str(SOURCE), 'test_source': str(COPY),
    'frozen_lib_sha256': sha(SOURCE / REL), 'network_sha256': sha(SOURCE / 'apps/mail/host-service/src/network.rs'),
    'test_module_sha256': sha(test_file), 'patch_sha256': sha(HERE / 'test-only.patch'),
    'logic_changed': False, 'release_rebuilt': False,
}, indent=2) + '\n')
print('Only cfg(test) module added to second source copy.')
