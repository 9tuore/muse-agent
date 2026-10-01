# Muse Phase 2 本地候选运行与验收说明

本包用于复核 **0.2.2 隔离扩展候选**。其日历接口不是未修改的 OctoSense/App Hub 官方原版已经接纳的 capability。不要覆盖 `/Applications/GOSIM-Local-Agent.app`，不要把隔离测试 HOME 指向生产用户资料。

## 内容与身份

- `app-bundle/`：Splash 应用源，四项 grant 为 `storage`、`model`、`mail`、`calendar`。`main.splash` SHA-256 `3331b7813f5439b3dcb26b1e0041535c525b560c94ac59ed88444432d6ff6de4`。
- `runtime/OctoSense Calendar Release Candidate.app`：隔离 Release 宿主，ad hoc 本地测试签名，完整日历用途文案；**不是**正式开发者签名或公证应用。包内可执行文件签名后 SHA-256 `617a2d896253c9eb6aab123464c56d947d3010e09ad759da0a1e3405b2284c14`。
- `runtime/hub`：隔离扩展 App Hub CLI。`mirror/` 是本地演练 catalog 与 signed bundle，`runtime/anchor.txt` 为公开验证锚。没有签名私钥。
- `patches/`：App Hub Gate、OctoSense EventKit/注册、Makepad Splash 启动预算的最小宿主补丁；对应锁定基线和构建命令见 `patches/README.md`。
- 根目录报告、`docs/`、`evidence/muse-ui-parity/before/`、`evidence/phase2/after/`：验收矩阵与真实窗口截图。`mail-demo-*` 是固定演示传输数据。

## 在隔离目录复核

1. 先验证 `codesign --verify --deep --strict 'runtime/OctoSense Calendar Release Candidate.app'`；再用 `runtime/hub check app-bundle --allow-unsigned` 对源清单做扩展 Gate 检查。`runtime/hub verify mirror/catalog.json --anchor 3581c1c9087a917630bc8560495189c5f1bb842a797ad5203cad0ed94ab5a840` 可校验演练目录。源清单未做正式 publisher 签名；签名演练的 artifact 在 `mirror/artifacts/muse-goals-0.2.2.bundle.pack.json`。
2. 用空白的 `OCTOSENSE_HOME` 与 `OCTOSENSE_APP_DATA` 启动隔离 `.app`，App Hub catalog 指向包内 `mirror/`。不要开启 `OCTOSENSE_DEV_MODE` 或 `--dev-grant-all`。本轮原始测试使用该包对应的 Release **裸二进制**从 App Hub 安装 0.2.2，签名 `.app` 仅完成包装和验签；包内 `.app` 的首次启动/TCC 行为仍需单独确认。
3. 验证 Chat、三个 Goal/Run、Memory、Activity、邮箱和日历页面。Goal 回归应只以真实 Shell 中的批准、模型调用、结果文件独立读回和重启后相同 SHA 判断；卡片出现或 `accepted` 不够。
4. 邮箱 LIVE 需要本人在宿主面板登录专用测试账号，并指定唯一测试收件地址/测试 ID；只有核对精确收件人、主题、正文并亲自确认后才发送。独立收件端收到对应 ID 才算投递。`mail_demo` 的 `accepted` 只是 FIXTURE。
5. 日历 LIVE 需要本人在隔离 `.app` 的 macOS TCC 弹窗决定 full access，指定测试日历/事件 ID；先查询，再逐项确认创建、修改、删除，每一步从系统日历独立读回。当前机器只返回 `write_only`，本轮没有触发授权弹窗或写入系统事件。
6. 同一真实邮件→候选日程→冲突查询→本人确认→系统事件→结果/来源记忆/Activity→重启恢复，必须在上述权限和账号就绪后独立复验。

## 当前判定

完整矩阵见 `PHASE2_PARITY_AND_FUNCTION_MATRIX.md`。Goal 模型链回归 PASS；邮箱、日历和同任务联动 LIVE BLOCKED；两轮 Chat 语义 FAIL；990×400 内容区可滚动但仅 71 点。总体 **PARTIAL**。没有正式签名、正式发布或 push。
