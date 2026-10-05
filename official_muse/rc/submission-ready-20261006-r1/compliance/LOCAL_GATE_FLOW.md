# 复用现有本地Gate流程（定位）

现有入口：`official_muse/ui_memory/prepare_candidate.py`。它使用本地演练身份，默认NO_PROFILE；不是正式AppHub投稿。不要在合规聊天运行签名、Key读取、publish或复制用户profile。

流程是：`hub stamp` → `hub sign-manifest --key <Root已掌握的授权本地key> --key-id muse-local-rehearsal` → `hub check --publisher-key <公开id=pubkey>` → `hub scan --packet <bundle外文件> --publisher-key <公开id=pubkey>` → 演练mirror的`hub publish` → `hub verify --anchor <演练anchor>`。代码约65–79行包含真实flags。脚本强制fresh output，Source bundle/Host/mirror可显式指定，MUSE_HUB_CLI可覆盖默认旧工具路径。

Root复用时应显式锁定当前源目录、Host、Hub和基准mirror，并检查新版本、输出candidate.json的SHA及catalog序号；不沿用脚本旧默认绝对路径，也不添加任何profile clone参数来做纯Gate。

只读check/scan定位：`official_muse/rc/packaging/package_lean_portable.py` 253–255行；公开验签参数、演练anchor与实际Hub SHA在该文件27–33行。只有public-key参数进入本审计，没有读取key文件。

本轮真实对照：HUB_COMPARISON.json。原版Hub位于compliance/.local-state/upstream-hub/target/release/hub（独立审计产物）；原版仍拒绝calendar，本地扩展的PASSED不能替代上游准入。
