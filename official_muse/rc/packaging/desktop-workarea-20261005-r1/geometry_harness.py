#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,runpy
HERE=Path(__file__).resolve().parent
CACHE=Path('/private/tmp/muse-morning-clean-019dc303-20261005/checkout')
SDK=CACHE/'vendor/octosense'
def generate(label):
 desktop=(SDK/'crates/shell/src/desktop.rs').read_text()
 types=desktop.split('#[cfg(test)]\nmod tests {',1)[0]
 body=desktop.split('#[cfg(test)]\nmod tests {',1)[1].split('\n}\n\nuse crate::desk::WmState;',1)[0]
 wanted={'dock_styles_keep_maximized_and_snapped_windows_above_shelf',
  'dock_workarea_tracks_bottom_shelves_during_style_transitions',
  'interrupted_switch_starts_from_the_visible_mix_and_lands_exactly',
  'specs_reproduce_the_literal_arrays_for_every_style',
  'the_glass_share_is_octosense_within_the_floating_chrome',
  'a_glass_chrome_inset_needs_a_glass_material','shelf_geometry_reads_the_table',
  'chrome_follows_the_flag_for_styles_with_both_appearances'}
 tests=[];found=set()
 for part in body.split('    #[test]\n')[1:]:
  name=re.search(r'fn (\w+)',part).group(1)
  if name in wanted:found.add(name);tests.append('    #[test]\n'+part)
 assert found==wanted
 shelf=desktop[desktop.index('fn shelf_geometry('):desktop.index('\n/// Center the icon and its running indicator')]
 style=(SDK/'crates/shell/src/octosense/style.rs').read_text().split('\npub fn load_sheet(',1)[0]
 snap=(SDK/'crates/shell/src/snap.rs').read_text()
 zone=snap[snap.index('#[derive(Clone, Copy, Debug, PartialEq, Eq)]'):snap.index('\npub fn edge_zone(')]
 ui=(SDK/'crates/shell/src/shell/ui.rs').read_text()
 rect=ui[ui.index('pub fn rect('):ui.index('\n/// Shrink a rect on every side')]
 desk=(SDK/'crates/shell/src/desk.rs').read_text()
 constants='\n'.join(re.search(r'^pub const '+name+r':.*?;',desk,re.M).group() for name in ['BORDER_SIZE','GAPS_OUT'])
 program=('extern crate makepad_widgets;\n'
  +'mod octosense { pub mod style {\n'+style+'\n}}\n'
  +'mod desk {\n'+constants+'\n}\n'
  +'mod shell { pub mod ui { use makepad_widgets::*;\n'+rect+'\n}}\n'
  +'#[path = '+json.dumps(str(SDK/'crates/shell/src/layout.rs'))+'] mod layout;\n'
  +'#[path = '+json.dumps(str(SDK/'crates/shell/src/desktop_layout.rs'))+'] mod desktop_layout;\n'
  +'mod snap { use crate::layout::LRect;\n'+zone+'\n}\n'
  +'mod desktop {\n'+types+'\nuse crate::shell::ui::rect;\n'+shelf
  +'\n#[cfg(test)] mod tests { use super::*;\n'+''.join(tests)+'\n}\n}\n')
 source=HERE/('geometry-'+label+'.rs')
 source.write_text(program)
 deps=CACHE/'build/clean-target/release/deps'
 libraries=sorted(deps.glob('libmakepad_widgets-*.rlib'),key=lambda p:p.stat().st_mtime,reverse=True)
 assert libraries
 binary=HERE/('geometry-tests-'+label)
 command=['rustc','--edition=2021','--test',str(source),'-L','dependency='+str(deps),'--extern','makepad_widgets='+str(libraries[0]),'-o',str(binary)]
 inputs=['crates/shell/src/desktop.rs','crates/shell/src/desktop_layout.rs','crates/shell/src/layout.rs','crates/shell/src/snap.rs','crates/shell/src/octosense/style.rs','crates/shell/src/shell/ui.rs','crates/shell/src/desk.rs']
 report={'scope':'extracted actual SDK style/table/tween/shelf, actual full desktop/layout data structures and actual snap geometry; linked real cached Makepad types; no mock geometry',
  'tests':sorted(found),'source_inputs':{p:hashlib.sha256((SDK/p).read_bytes()).hexdigest() for p in inputs},
  'generated_harness':str(source),'generated_harness_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
  'Makepad_rlib':str(libraries[0]),'compile_command':command,
  'full_shell_cargo_suite':'BLOCKED_UNRELATED_launcher_test_super_menu_namespace_error',
  'GUI_runtime_or_external_actions':'NOT_RUN'}
 (HERE/('geometry-inputs-'+label+'.json')).write_text(json.dumps(report,indent=2)+'\n')
 return command,binary
if __name__=='__main__':
 runner=runpy.run_path(str(HERE/'run_step.py'))
 command,binary=generate('original')
 result=runner['run']('geometry-original-compile',command)
 assert result['exit_code']==0 and not result['guard_stop']
 result=runner['run']('geometry-original-regression',[str(binary),'desktop::tests::','--test-threads=1'])
 log=(HERE/'geometry-original-regression.log').read_text()
 print(log)
 assert result['exit_code']!=0 and 'test result: FAILED' in log and '6 passed; 2 failed' in log, 'Require real assertion failures, not compilation failure'
