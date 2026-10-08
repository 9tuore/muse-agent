# Lossless evidence filesystem compression

2026-10-09T03:26:31+08:00. No tests were rerun and no new PASS was asserted. Existing rc15/rc16 evidence paths, bytes, modes and logical lengths remain unchanged. Git reports no difference in existing tracked evidence.

The first9KB isolated copy preserved SHA/mode/size/owner/mtime but saved no blocks and was discarded without replacing the original (`receipt.json`). A506KB isolated copy then preserved those properties and lowered blocks992→296; it was safely atomically substituted (`probe-large.json`). Only after this verified probe did the batch proceed.

36 files including the probe were compressed, saving8,941,568 allocated bytes (8.53MiB). All final replacements were independently reread and hash/mode/size/block checked (`verification.json`). Batch scanned191 eligible files; no-gain files and files already compressed remained untouched. No symlink/hardlink/open file was replaced; lsof checked before copying and again immediately before replacement. Insufficient scratch space would stop the batch.

Scope was closed, single-link JSON/log/txt evidence in final_quality only. Candidate/bundle directories, ignored runtime/profile state, screenshots and source files were excluded. Temporary duplicate scratch copies alone were removed; unique evidence was never deleted. Compression is native APFS/HFS transparent compression through verified `/usr/bin/ditto --hfsCompression --noclone`. Existing test judgments are original observations, not new verification claims.

The536MB directory is mostly outside the requested text-file scope, so this action cannot reclaim gigabytes. Filesystem gain is calculated from summed st_blocks changes; global free space is affected by concurrent work and is not attributed to this task.
