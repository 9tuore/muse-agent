#!/usr/bin/env python3
"""Emit digest-only proposals; never apply to framework/source/build."""
import difflib,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OWN=Path(__file__).resolve().parent
old=ROOT/'sdk-overlays/makepad/widgets/src/splash_storage.rs'
text=old.read_text()
helper=text[text.index('fn file_sha256('):text.index('pub fn script_mod(',text.index('fn file_sha256('))]
methods=text[text.index('    // Local UTF-8 provenance digest;'):text.index('    vm.add_method(fs, id_lut!(read),',text.index('    // Local UTF-8 provenance digest;'))]
assert 'root_for_vm(vm).is_none()' in methods and 'target(vm, path)' in methods
assert 'MAX_FILE_BYTES + 1' in helper and 'sha256_hash(&bytes)' in helper
report={'status':'PROPOSED_NOT_APPLIED_NOT_COMPILED','source_overlay_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),'targets':{}}
for name,rel in [('reference','hub-contract-sdk/makepad'),('full_shell','official-rc2-source/.sources/makepad')]:
 root=ROOT/'.local-state'/rel
 p=root/'widgets/src/splash_storage.rs'
 original=p.read_text()
 assert 'id_lut!(sha256)' not in original and 'id_lut!(sha256_file)' not in original
 assert 'pub fn sha256_hash' in (root/'platform/network/src/digest.rs').read_text()
 assert original.count('pub fn script_mod(vm: &mut ScriptVm) {')==1
 modified=original
 if name == 'full_shell':
  assert 'fn open_storage_file(' in original and 'fn read_storage_bytes(' in original
  selected_helper = """fn file_sha256(real: &Path) -> Result<String, String> {
    let bytes = read_storage_bytes(real)?;
    let digest = crate::makepad_platform::makepad_network::digest::sha256_hash(&bytes);
    Ok(digest.iter().map(|byte| format!("{byte:02x}")).collect())
}

"""
 else:
  selected_helper = helper.replace('    let file = std::fs::File::open(real)', '    use std::io::Read;\n    let before = std::fs::symlink_metadata(real).map_err(|_| "file not readable".to_string())?;\n    if !before.is_file() { return Err("not a regular file".to_string()); }\n    let file = std::fs::File::open(real)', 1)
  assert selected_helper.index('symlink_metadata') < selected_helper.index('File::open')
 marker='/// Registers the jailed `fs` module into an isolate VM.\npub fn script_mod(vm: &mut ScriptVm) {'
 assert marker in modified
 modified=modified.replace(marker,selected_helper+marker,1)
 modified=modified.replace('    let fs = vm.new_module(id!(fs));\n','    let fs = vm.new_module(id!(fs));\n\n'+methods,1)
 patch=''.join(difflib.unified_diff(original.splitlines(True),modified.splitlines(True),fromfile='a/widgets/src/splash_storage.rs',tofile='b/widgets/src/splash_storage.rs'))
 out=OWN/f'fs-sha256-{name}.patch';out.write_text(patch)
 report['targets'][name]={'path':str(p),'before_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'proposed_sha256':hashlib.sha256(modified.encode()).hexdigest(),'patch_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'dependency_change':False,'special_file_guard':'reuse read_storage_bytes/open_storage_file' if name=='full_shell' else 'symlink_metadata before open + fd metadata after open','race_free':False}
(OWN/'sha256_patch_identity.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
