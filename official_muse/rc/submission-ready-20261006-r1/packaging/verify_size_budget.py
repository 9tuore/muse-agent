#!/usr/bin/env python3
"""Measure a private feasibility ZIP without dropping any prior source/evidence.

The prior rc45 ZIP is retained in full; its app is replaced by the tested copy
with the new launcher and complete local-model dependency closure. This private
size probe is not a frozen rc46 delivery and is never placed on the Desktop.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import stat
import sys
import zipfile

sys.dont_write_bytecode = True
E = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('package', ROOT / 'official_muse/rc/packaging/package_lean_portable.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
BASE = Path('/Users/mima0000/Desktop/Muse-0.3.26-rc45-Intel精简运行与源码-d306d3c0-2026-10-06.zip')
APP = E / '.local-state/native-test/Muse 0.3.26-rc45.app'
OUTPUT = E / '.local-state/size-feasibility-rc45.zip'


def main():
    assert p.sha(BASE) == 'cbda5d0d46e0ea596c66ae395e6c997ccc514e11b91b971ed4a9aeb7be4da940'
    app_files = p.inventory(APP)
    preserved = {}
    written = {}
    with zipfile.ZipFile(BASE) as old, zipfile.ZipFile(OUTPUT, 'x', zipfile.ZIP_DEFLATED, compresslevel=6) as new:
        prefix = old.infolist()[0].filename
        app_prefix = prefix + APP.name + '/'
        for entry in old.infolist():
            if entry.filename.startswith(app_prefix):
                continue
            with old.open(entry) as source:
                data = source.read()
            new.writestr(entry, data)
            if not entry.is_dir():
                preserved[entry.filename] = hashlib.sha256(data).hexdigest()
        new.writestr(zipfile.ZipInfo(app_prefix), b'')
        for rel, item in sorted(app_files.items()):
            name = app_prefix + rel + ('/' if item['kind'] == 'dir' else '')
            zi = zipfile.ZipInfo(name)
            zi.create_system = 3
            kind = {'dir': stat.S_IFDIR, 'file': stat.S_IFREG, 'symlink': stat.S_IFLNK}[item['kind']]
            zi.external_attr = (kind | item['mode']) << 16
            if item['kind'] == 'dir':
                new.writestr(zi, b'')
            elif item['kind'] == 'symlink':
                data = item['target'].encode()
                new.writestr(zi, data)
                written[name] = item['sha256']
            else:
                zi.compress_type = zipfile.ZIP_DEFLATED
                with (APP / rel).open('rb') as source, new.open(zi, 'w') as destination:
                    shutil.copyfileobj(source, destination, 1048576)
                written[name] = item['sha256']
    with zipfile.ZipFile(OUTPUT) as z:
        assert z.testzip() is None
        for name, digest in {**preserved, **written}.items():
            h = hashlib.sha256()
            with z.open(name) as source:
                for block in iter(lambda: source.read(1048576), b''):
                    h.update(block)
            assert h.hexdigest() == digest, name
        member_count = len(z.infolist())
    size = OUTPUT.stat().st_size
    result = dict(status='PASS' if size < 500000000 else 'FAIL',
        scope='private rc45 size feasibility, not final rc46 delivery',
        strict_limit_bytes=500000000, zip_bytes=size, headroom_bytes=500000000-size,
        zip_sha256=p.sha(OUTPUT), members=member_count, compression='ordinary ZIP deflate level 6',
        preserved_prior_non_app_members=len(preserved), all_prior_source_and_reports_preserved=True,
        all_new_app_files_and_symlinks_verified=True,
        model_bytes=341454496, model_quality='basic offline fallback; not strong',
        final_zip_built=False, video_included=False, video_external_if_over_budget=True)
    (E / 'SIZE_FEASIBILITY.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(result), flush=True)
    assert result['status'] == 'PASS'


if __name__ == '__main__':
    main()
