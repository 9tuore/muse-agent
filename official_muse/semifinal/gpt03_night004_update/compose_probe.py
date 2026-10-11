#!/usr/bin/env python3
"""Combine an isolated patch with its explicitly frozen central wall dependency."""
from pathlib import Path
import importlib.util
import sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.dont_write_bytecode = True
helper = Path('/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/official_muse/semifinal/tests/run_official_api.py')
spec = importlib.util.spec_from_file_location('helpers', helper)
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)
source = (ROOT / 'build/gpt03-night004/update-main.splash').read_text()
wall = (HERE / 'wall-dependency.splash').read_text().rstrip()
source = helpers.replace_function(source, 'calendar_agent_wall', wall)
(ROOT / 'build/gpt03-night004/update-with-wall.splash').write_text(source)
