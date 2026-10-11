#!/usr/bin/env python3
"""Require the edit request and active candidate to match the original event Goal."""
from pathlib import Path
import difflib
import hashlib
import importlib.util
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENTRAL = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松')
spec = importlib.util.spec_from_file_location('helpers', CENTRAL / 'official_muse/semifinal/tests/run_official_api.py')
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
base = (ROOT / 'build/gpt03-night004/combined-apply/official_muse/app/source/main.splash').read_text()
assert hashlib.sha256(base.encode()).hexdigest() == 'd065ad15ebeef1e67d69ef4e3c722f2b76cf03e7a0ab325fc2b29073b10dfba5'
function = helpers.functions_in(base)['chat_add_proposal']
anchor = '        chat_sessions[index].proposals.push({id: request_id session_id: session_id'
guard = '''        let active = chat_active_candidate(session_id)
        if active == nil || active.id != request.candidate_id
            || (gm_has(request,"goal_id") && request.goal_id != "" && request.goal_id != authority.current_binding.goal_id)
            || (gm_has(active,"goal_id") && active.goal_id != "" && active.goal_id != authority.current_binding.goal_id)
            || (active.id != authority.current_binding.candidate_id
                && (!gm_has(active,"goal_id") || active.goal_id != authority.current_binding.goal_id)) { return false }
'''
assert function.count(anchor) == 1
patched_function = function.replace(anchor, guard + anchor)
source = helpers.replace_function(base, 'chat_add_proposal', patched_function)
after = helpers.functions_in(source)
assert [key for key, body in helpers.functions_in(base).items() if body != after[key]] == ['chat_add_proposal']
(ROOT / 'build/gpt03-night004-regression/guard-main.splash').write_text(source)
(HERE / 'edit-goal-binding.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True), source.splitlines(True),
    fromfile='a/official_muse/app/source/main.splash', tofile='b/official_muse/app/source/main.splash')))
print(hashlib.sha256(source.encode()).hexdigest())
