#!/usr/bin/env python3
"""Reproduce interruption after the first durable write, without user data."""
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'official_muse/ui_memory/tests'))
import regression_run

out = HERE / sys.argv[1]
out.mkdir(exist_ok=False)
probe = out / 'probe.splash'
probe.write_text('''
fn first_chat_probe(){
    let started = chat_boot_data()
    let snapshot = fs.read("chat-sessions.json").parse_json()
    let first = snapshot.sessions[0]
    let complete = first["focus_project"].is_string() && first["focus_owner"].is_string()
        && first["goal_id"].is_string() && first["proposals"].is_array()
    fs.write("probe.json",{first_write_complete: complete initial_chat_saved: started && snapshot.sessions.len()==1
        selected_id_matches: snapshot.selected_id==first.id messages_preserved: first.messages.len()==0}.to_json())
}
start_timeout(0.1, || first_chat_probe())
''')
source = (subprocess.check_output(['git', 'show', 'e0eb5d82:official_muse/app/source/main.splash'], cwd=ROOT).decode()
          if sys.argv[1].startswith('first-chat-before') else (ROOT / 'official_muse/app/source/main.splash').read_text())
# Stop at the real first-write boundary, before the later migration callback.
source = regression_run.existing.replace_function(source, 'chat_boot_finish', 'fn chat_boot_finish(){ return true }')
result = regression_run.run_suite('model_suite', source, ROOT / 'official_muse/app/bundle', out / 'first', 8510, probe)
(out / 'report.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
