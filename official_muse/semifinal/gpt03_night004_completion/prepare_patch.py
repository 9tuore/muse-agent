#!/usr/bin/env python3
"""Build a native Calendar/Mail completion proposal on frozen dabfe65b."""
from pathlib import Path
import difflib
import hashlib
import importlib.util
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('helpers', '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/semifinal/tests/run_official_api.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
base = (ROOT / 'build/gpt03-night004-completion/baseline.splash').read_text()
assert hashlib.sha256(base.encode()).hexdigest() == 'dabfe65bbb859e51db5cc2b9eea59855024af927f8bfbe548fa86f50ded95a6d'
functions = helpers.functions_in(base)
entry = functions['mail_finish_linked_result']
old = 'if gm_has(mail_draft,"official_calendar") { return mail_calendar_current(mail_draft) }'
assert entry.count(old) == 1
source = helpers.replace_function(base, 'mail_finish_linked_result', entry.replace(old, 'if gm_has(mail_draft,"official_calendar") { return mail_finish_native_result() }'))
current = functions['calendar_agent_update_current']
old = '    return goal != nil && goal.to_json() == record.goal_json && goal.status == "planned"'
new = '    if goal != nil && goal.to_json() == record.goal_json && goal.status == "planned" { return true }\n    return mail_native_completion_matches(goal,record)'
assert current.count(old) == 1
source = helpers.replace_function(source, 'calendar_agent_update_current', current.replace(old, new))
marker = 'fn mail_finish_linked_result(){'
assert source.count(marker) == 1
source = source.replace(marker, (HERE / 'completion.splash').read_text() + '\n' + marker)
after = helpers.functions_in(source)
assert sorted(k for k in functions if functions[k] != after[k]) == ['calendar_agent_update_current', 'mail_finish_linked_result']
(ROOT / 'build/gpt03-night004-completion/proposed.splash').write_text(source)
patch = ''.join(difflib.unified_diff(base.splitlines(True), source.splitlines(True),
    fromfile='a/official_muse/app/source/main.splash', tofile='b/official_muse/app/source/main.splash'))
(HERE / 'native-mail-completion.patch').write_text(''.join('\n' if line == ' \n' else line for line in patch.splitlines(True)))
print(hashlib.sha256(source.encode()).hexdigest())
