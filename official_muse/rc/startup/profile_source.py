#!/usr/bin/env python3
"""Generate a diagnostic-only source copy; production entry stays untouched."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = args.source.read_text()
    wrappers = {
        'ui_layout_boot': '', 'notification_boot': '', 'chat_boot_data': '',
        'core_boot_activity': '', 'core_boot_memory': '', 'core_boot_goals': '',
        'gm_boot': '', 'gm_boot_part': 'phase,start',
        'gm_finish_boot': 'saved,generated_profile', 'calendar_boot': '',
        'boot_restore': 'boot_error', 'mail_watch_boot': '', 'redraw': '',
    }
    diagnostic = '''let rc_started = time_now()
let rc_profile = {schema: 1 diagnostic_only: true stages: {}}
fn rc_record(name,started){
    let elapsed = (time_now() - started) * 1000
    if rc_profile.stages[name] == nil { rc_profile.stages[name] = [] }
    rc_profile.stages[name].push(elapsed)
    rc_profile.elapsed_ms = (time_now() - rc_started) * 1000
    fs.write("rc-startup-profile.json",rc_profile.to_json())
}
'''
    wrapper_source = ''
    for name, params in wrappers.items():
        pattern = r'\bfn ' + re.escape(name) + r'\('
        source, count = re.subn(pattern, 'fn rc_impl_' + name + '(', source)
        if count != 1:
            raise RuntimeError(f'Expected one definition: {name}, got {count}')
        wrapper_source += (f'fn {name}({params}){{ let began = time_now() '
                       f'let value = rc_impl_{name}({params}) '
                       f'rc_record("{name}",began) return value }}\n')
    startup = 'start_timeout(0.05, || boot())'
    if source.count(startup) != 1:
        raise RuntimeError('Verified startup marker missing')
    source = source.replace(startup, wrapper_source + startup)
    marker = 'SolidView{width: Fill height: Fill flow: Right container_id: @muse_shell'
    if source.count(marker) != 1:
        raise RuntimeError('Verified root expression missing')
    source = source.replace(marker, 'let rc_ui_started = time_now()\nlet rc_root = ' + marker)
    source += '\nrc_record("ui_construction",rc_ui_started)\nrc_root\n'
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(diagnostic + source)
    args.out.with_suffix('.profile.json').write_text(json.dumps({
        'diagnostic_only': True,
        'production_source_sha256': hashlib.sha256(args.source.read_bytes()).hexdigest(),
        'diagnostic_source_sha256': hashlib.sha256(args.out.read_bytes()).hexdigest(),
        'stages': list(wrappers) + ['ui_construction'],
        'timing': 'Inclusive stage wall time; diagnostic file writes excluded from own stage, included in parents.',
    }, indent=2) + '\n')


if __name__ == '__main__':
    main()
