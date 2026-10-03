# Muse 官方应用历史说明 · 0.2.8

> 本文件保留0.2.8开发说明；当前源码为0.3.16，功能、推送授权与构建入口请看仓库根README及SOURCE_DELIVERY.md。下文“尚未上传/不推送”等为历史状态。

这是参赛应用的 OctoScript / Splash 源码与配套宿主补丁。应用在 OctoSense / App Hub 中运行，使用 Makepad 布局、manifest capability、官方存储和账号权限入口。整体验收状态为 **PARTIAL**；源码整理完成不等于比赛提交或官方准入完成。

## 入口

- 应用：`official_muse/app/bundle/main.splash`；`manifest.json` 声明精确的 storage、model、mail、calendar 能力。
- 结构化 Goal/Memory 状态逻辑：`official_muse/phase2/core_logic.splash`。同一逻辑内嵌在主 Splash 中；修改后应保持两处一致并验证。
- 测试：`official_muse/phase2/tests/`，操作真实 Makepad remote 输入及隔离存储；不把 fixture 当外部成功。
- 宿主补丁与构建边界：`official_muse/phase2/host_extension/README.md`。
- 最终验收：根目录 `PHASE2_LIVE_ACCEPTANCE.md`、`PHASE2_LIVE_TEST_REPORT.md`、`PHASE2_LIVE_EVIDENCE_INDEX.md`。

源码导出只包含官方应用与配套测试/补丁，不包含旧独立版安装包、生产数据、模型权重、账号、私钥和本机构建缓存。该导出尚未上传 GitHub。

## 已实测的功能

中文八页、宽窗三栏、窄窗与矮窗滚动；真实模型对话、多会话历史；多 Goal 的计划、批准、模型建议、应用隔离写入与独立读回；来源记忆更正/置顶/遗忘；真实 Activity；系统日历查询、创建、修改、删除及每一步的独立读回。正常退出和重启后的完整结果以最终报告为准。

Mail 使用官方 Host Service。本人登录、真实收发及邮件到系统日历的同 Goal 全链尚未验收。Qwen3-0.6B 的三轮对话语义复测为 2/3，不可宣称稳定通过。模型/provider/预算 UI 仍有只读差异，来源 content_sha256 尚未补齐。

## 宿主基线与重现

宿主补丁 README 提供基线文件哈希、应用顺序、locked 构建与 `.app` 打包命令。App Hub 的精确 Git 基线为 `e8601b80ce104db2e48208094714bdcffdce6b5a`；OctoSense 归档标签为 `7f962547cd8035ed2bb05962cf7824d8aa33e3a3`，本机没有其 Git 对象核验，不能将标签当作已核实 HEAD。框架依赖由 `native-runtime.lock.json` 与对应 runtime.json 锁定。

Calendar 是隔离的 EventKit 宿主扩展，原版 App Hub Gate 仍拒绝此 capability。原生多轮 model.complete 和本机 Metal 回调修复也以独立补丁交付。上游尚未接受这些补丁；本机使用 ad hoc 测试签名，不是正式签名或发布。

从隔离扩展宿主源码构建 `hub` 和 `card-host` 后，可先运行：

```sh
"$MUSE_HUB" check official_muse/app/bundle --allow-unsigned
"$MUSE_HUB" scan official_muse/app/bundle --packet build/review.json
```

`MUSE_HUB` 指向按补丁 README 构建的扩展 CLI；原版 CLI 不能替代它验证 calendar。`--allow-unsigned` 仅用于开发源码检查。签名候选须按真实公钥注册检查；扫描生成的问题仍须人工回答，不能视作正式准入。

Shell 运行应使用新的 OCTOSENSE_HOME、OCTOSENSE_APP_DATA 与经过 Gate 的 App Hub 镜像。禁止 `--dev-grant-all` 或修改 TCC 数据库。先在应用中心安装/打开 Muse；本地模型须由宿主 profile 配置，测试使用无 Key 的本机 Qwen 服务。账号密码只进入官方 Host 登录面板。

## 实机测试示例

以下 `8401` 是测试 Shell 的 remote 端口，`$MUSE_JAIL` 指向新建的测试 app-data 中的 `muse-goals`，不使用生产目录：

```sh
python3 official_muse/phase2/tests/goal_chain.py 8401 "$MUSE_JAIL" --goal MUSE-TEST --source '合成资料。' --model --shot build/goal.png
python3 official_muse/phase2/tests/live_chat_rounds.py 8401 "$MUSE_JAIL" build/chat
python3 official_muse/phase2/tests/live_shell_layout.py 8401 build/layout --jail "$MUSE_JAIL"
python3 official_muse/phase2/tests/visible_nav.py 8401 build/pages
python3 official_muse/phase2/tests/audit_state.py "$MUSE_JAIL" --min-goals 3 --require-completed
```

日历 CRUD 驱动只允许唯一测试编号；参数/日期请先阅读脚本并人工核对。每次真实系统动作都有单独批准，失败或结果未知时不自动重做。真实邮箱测试需要本人登录和最终发送确认。

## 提交前仍须完成

补齐 Mail 与邮件→日历全链、处理模型语义稳定性及其余验收差异；补真实 publisher/support/privacy 信息；明确本地宿主扩展的主办方准入。然后确定要推送的最终版本及队伍名。当前不推送 GitHub，不在主办方 issue 留言。
