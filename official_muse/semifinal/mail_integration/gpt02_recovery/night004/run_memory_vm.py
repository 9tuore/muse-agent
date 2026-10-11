#!/usr/bin/env python3
"""Use verified current runner, with outputs confined to this owned worktree."""
import importlib.util,sys
from pathlib import Path
sys.dont_write_bytecode=True
runner=Path(sys.argv[1]).resolve(strict=True)
sys.argv=[str(runner)]+sys.argv[2:]
spec=importlib.util.spec_from_file_location('night004_real_vm_runner',runner)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.ROOT=Path(__file__).resolve().parents[5]
raise SystemExit(module.main())
