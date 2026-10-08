# Own idle runtime storage optimization

Transparent compression completed for93 eligible text/source carriers, saving24,166,400 allocated bytes (23.05MiB).197 identical PNG/JPG/SVG carriers were replaced through `/bin/cp -c -p` on the same APFS volume; duplicate logical bytes total19,829,081. Shared physical extent savings cannot be measured from each file's st_blocks and are not claimed as that logical byte total.

Every replacement preserved SHA/size/mode/owner/mtime. Image COW additionally preserved flags and exact xattrs. Both source and destination had no open handles before replacement; hardlinks, symlinks, home/.host/profiles/keys/.git and shared data were excluded. Only redundant task scratch copies were removed; unique evidence, locks, sources, images and candidate bytes remained intact. Candidate .splash files received only native transparent filesystem compression, never content edits.

The per-file private receipt remains ignored at final_quality/runtime/storage-maintenance/receipt.json and is not committed. Public runtime-summary.json contains only aggregate results and receipt hash. Existing tracked evidence has no Git diff. No tests, windows, models or permissions were invoked; original rc15/rc16 verdicts remain their original observations. Global free space rose during this interval, but concurrent work prevents attributing that whole delta to this operation.

Eligible own runtime data was only about54MiB before optimization, so this task cannot safely provide the requested additional0.5GiB. It stops after the authorized safe options without deleting unique data or touching other directories.
