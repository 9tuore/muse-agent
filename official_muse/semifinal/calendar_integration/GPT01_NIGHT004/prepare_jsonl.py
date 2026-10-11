from pathlib import Path
import shutil
HERE=Path(__file__).resolve().parent
OWN=HERE.parents[3]
root=OWN/'build/gpt01-night004-calendar/relay'
for name in ['relay_jsonl.rs','jsonl_main.rs']:
 shutil.copyfile(HERE/name,root/'src'/name)
p=root/'src/lib.rs';s=p.read_text()
if 'pub mod relay_jsonl;' not in s:p.write_text(s+'\npub mod relay_jsonl;\n')
p=root/'Cargo.toml';s=p.read_text()
if 'gpt01-night004-relay-jsonl' not in s:p.write_text(s+'\n[[bin]]\nname="gpt01-night004-relay-jsonl"\npath="src/jsonl_main.rs"\n')
print(str(root))
