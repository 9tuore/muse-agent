# 官方规则与证据核对交接

范围：compliance/内只读核对、文档、窄脚本；未改产品、Host、SDK、主状态、包装，也未操作8493。

已完成：当前部署官网+固定官方源码/技术契约核对；视频阶段规则与最少素材；rc45实际上游/扩展双CLI检查；公开测试依赖定位及Root修复working-tree核对；隐私政策草案；所有来源URL/读取时间/SHA留痕。

结论：PARTIAL。原版Hub仅calendar拒绝；本地扩展Hub同一签名交付包通过。AppHub官方上限是受限bundle8MiB，不是外层ZIP500MB。官网无需先上架，但公开Apache2.0源码、实际运行与证据仍必需。群通知和9/25赛程文档时间差异未由赛务澄清。rc45真实链跨版本，同最终候选从头整链、第二Mac等仍缺；最终新版需重新绑定证据。

Root接手：审阅PRIVACY_POLICY_DRAFT.md，正式发布政策并替换listing；提交测试便携修复后核对公开树；新候选Gate/运行/截图/包的统一版本；与媒体聊天按VIDEO_REQUIREMENTS_AND_MATERIALS.md准备。修复新版不改写本审计rc45证据。

复现：python3 audit_public_fixtures.py --repo <worktree> --ref 9b83f98c --out <new-report.json>；这是旧公开树缺项检查，新的wrapper不应继续使用旧A2依赖表作为全量测试。Hub实际命令见HUB_COMPARISON.json，构建方法/工具链/源码来源见UPSTREAM_BUILD_PROVENANCE.json。

没有正式商店提交、签名或公开操作；Root已单独收到用户同步GitHub的授权并执行，合规聊天没有push。
