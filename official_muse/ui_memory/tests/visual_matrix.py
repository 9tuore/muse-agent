#!/usr/bin/env python3
"""Serial visible screenshots of one immutable source snapshot; no private data.

Visible card-host windows must be serialized: a second window can occlude the
first and produce white/partial grabs. Different remote ports do not fix that.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from PIL import Image


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--port', type=int, default=8484)
    p.add_argument('--long', action='store_true')
    p.add_argument('--forms', action='store_true')
    p.add_argument('--sizes', nargs='+', default=['1400x900', '990x539', '990x400', '412x892', '1200x760'])
    a = p.parse_args()
    a.out = a.out.resolve()
    a.out.mkdir(parents=True, exist_ok=False)
    snapshot = a.out / 'source-bundle'
    shutil.copytree(a.source.resolve().parent, snapshot)
    source = snapshot / a.source.name
    results = {}
    for size in a.sizes:
        command = [sys.executable, str(Path(__file__).with_name('visual_capture.py')), '--source', str(source),
                   '--out', str(a.out / size), '--size', size, '--port', str(a.port)]
        if a.long:
            command.append('--long')
        if a.forms:
            command.append('--forms')
        completed = subprocess.run(command, capture_output=True, text=True)
        (a.out / size / 'driver.log').write_text(completed.stdout + completed.stderr)
        report = a.out / size / 'report.json'
        result = json.loads(report.read_text()) if report.exists() else {'status': 'ERROR'}
        result['exit_code'] = completed.returncode
        result['blank_images'] = []
        result['ui_check_failures'] = []
        if a.long and report.exists():
            if not result.get('input_check', {}).get('typed_readback'):
                result['ui_check_failures'].append('keyboard_readback')
            for page, entry in result.get('page_entry_checks', {}).items():
                if not entry['title_at_first_screen']:
                    result['ui_check_failures'].append('page_first_screen:' + page)
            interactions = result.get('interactions', {})
            if interactions.get('error'):
                result['ui_check_failures'].append('interaction:' + interactions['error'])
            for key, value in interactions.get('columns', {}).items():
                if isinstance(value, bool) and not value:
                    result['ui_check_failures'].append('columns:' + key)
            for key, value in interactions.get('long_mail', {}).items():
                if isinstance(value, bool) and not value:
                    result['ui_check_failures'].append('long_mail:' + key)
            for key, value in interactions.get('forms', {}).items():
                if isinstance(value, bool) and not value and not key.endswith('_clicked'):
                    result['ui_check_failures'].append('forms:' + key)
        for image_path in (a.out / size).glob('*.png'):
            image = Image.open(image_path).convert('RGB')
            count, color = max(image.getcolors(image.width * image.height))
            if count / (image.width * image.height) > .99:
                result['blank_images'].append(image_path.name)
        # Nonblank pixels are a capture-quality check, never a UI PASS.
        results[size] = result
        print(size, json.dumps({'exit_code': completed.returncode, 'blank_images': result['blank_images'],
                                'unexpected_side_effects': result.get('unexpected_side_effects'),
                                'interactions': result.get('interactions')}, ensure_ascii=False), flush=True)
        (a.out / 'matrix.json').write_text(json.dumps({'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
           'scope': 'FIXTURE_VISIBLE_CARD_HOST; visual review and final frozen candidate still required',
           'sizes': results}, ensure_ascii=False, indent=2) + '\n')
    return int(any(r['exit_code'] or r['blank_images'] or r.get('unexpected_side_effects') or r['ui_check_failures'] for r in results.values()))


if __name__ == '__main__':
    raise SystemExit(main())
