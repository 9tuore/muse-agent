# Muse · 星海队

## 1. 把对话变成可核对的行动

Muse 在 OctoSense 官方容器中提供中文 AI 对话、来信结果卡、邮件起草与确认发送、系统日历安排与改期，以及带来源、跨对话检索的全局记忆。

- 左侧：可折叠聊天历史与邮箱、日历、记忆等快捷入口。
- 中间：当前讨论和输入；新对话沿用授权范围内的相关全局记忆。
- 右侧：来信提醒、有效结果和具体动作确认，技术详情默认收起。

**当前源码候选：0.3.26-rc51 / 6b46c3c8；验收 PARTIAL。** 用户已授权 GitHub 普通同步。rc50 补全首次对话持久记录、拆分邮件来源保存与审计，并调整矮窗历史区域；rc51 将首次界面挂载与资料恢复分开，仅刷新可见页面。四种尺寸的受影响 UI 检查通过，原冷启动和模型失败仍保留。当前实机、冻结源码、压缩包及回归结论以[本轮收口报告](official_muse/rc/rc49-completion-20261006-r1/REPORT.md)为准；不把不同版本的邮件、日历节点拼成同最终整链。正式 App Hub 未提交，原二十项仍未全过。

此前已补收件声明恢复、64条记忆保存与更正、日历短回调与同事项改期绑定、缺RFC时明确选原事项，以及执行回执误冲突修复。真实同事项已完成系统创建、电脑日历外部修改、原ID改期、确认邮件到达、结果和记忆、Shell恢复；节点跨rc28/29/34/35，不冒充同最终整链通过。完整Shell默认558项单测与空target Host重建通过；第二GPT单通道实测provider失败，原二十项完整门槛仍未全过。历史入口：[rc35报告](official_muse/rc/remaining-20261005-r2/REPORT.md)和[二十项矩阵](RC_ACCEPTANCE_MATRIX.md)。

![Muse rc51 实录封面](official_muse/rc/rc49-completion-20261006-r1/media/rc51-public/Muse-rc51-cover.png)

[rc51 中文配音实录（96 秒）](official_muse/rc/rc49-completion-20261006-r1/media/rc51-public/Muse-rc51-demo.zh-CN.mp4) · [字幕](official_muse/rc/rc49-completion-20261006-r1/media/rc51-public/Muse-rc51.zh-CN.srt) · [画面与音轨核验](official_muse/rc/rc49-completion-20261006-r1/media/rc51-public/QA.json)。本轮真实内部任务与跨聊天召回；连续画面和前后截图分开标注，账号与历史邮件已遮挡。整体仍 PARTIAL，视频不冒充本轮新邮件/日历整链。

## 2. 官方源码与依赖

官方应用使用 **OctoScript / Splash / Makepad**，入口是[main.splash](official_muse/app/bundle/main.splash)，提交目录为`official_muse/app/bundle/`。可读源码位于`official_muse/app/source/main.splash`；Python为测试和构建工具，Rust为官方宿主配套扩展。

| 路径 | 用途 |
| --- | --- |
| `official_muse/app/bundle/` | 0.3.26-rc51 compact payload、manifest、listing 和资源；payload ed4874d1，listing 截图仍为有身份记录的 V12 支持材料 |
| `official_muse/global_memory.splash`、`incoming_mail.splash`、`scheduling.splash` | 全局记忆、逐封来信和安排/改期模块 |
| `dependencies.lock.json` | 五个官方SDK的固定commit、完整差异和重建树哈希 |
| `sdk-overlays/` | 可直接阅读的本地宿主/框架/准入修改，完整保留已有修复 |
| `scripts/bootstrap_sdk.py` | 从官方锁定来源恢复依赖，逐文件/模式/链接验证，不接受不匹配的树 |
| `patches/muse-source-cleanup-20261004.patch` | 历史主入口清理补丁；已集成0.3.25，保留为来源记录 |
| `official_muse/prelim/`、`ui_memory/`、`round2/`、`phase2/` | 测试、公开证据和历史失败记录 |
| `app/`、`scripts/`、`miniapp/`、`MUSE_HANDOFF/` | 保留的桌面历史源码、工具和交接 |

官方基础源码按锁定版本下载；本地Calendar、准入、模型和框架扩展可重建，但尚未声称获官方上游接受。许可见[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)，瘦身说明见[sdk-overlays/README.md](sdk-overlays/README.md)。

## 3. 构建和检查

环境：macOS、Rust、Apple Command Line Tools、Python 3。首次准备需要访问官方GitHub及Cargo依赖；无需输入私人密钥。

```sh
python3 scripts/bootstrap_sdk.py
python3 scripts/bootstrap_sdk.py --verify
cd vendor/octosense
cargo build --locked --release -p octosense --bin octosense --no-default-features --features app-hub
python3 tools/package_calendar_candidate.py --release --output ../../build/Muse-OctoSense.app
cd ../app-hub
cargo build --locked -p octosense-app-hub --bin hub
cargo build --locked -p octosense-card-host --bin card-host
cd ../..
./vendor/app-hub/target/debug/hub check official_muse/app/bundle --allow-unsigned \
  --publisher-key muse-local-rehearsal=bb05ce91333a0045f9f8187eba865f11d9e14ec636aeaee80144708984e740c5
```

四个内部`.sources/`链接由bootstrap恢复。已有vendor时脚本只核验，发现差异立即停止，保留本地修改。开发公钥不是发布私钥；开发check不代替Gate、正式发布身份、catalog、能力授权及人工审查。模型和邮箱/日历账号在官方Host设置中配置。

历史清理补丁已集成，不向当前源码重复应用。改动可读入口后，须重新生成compact bundle、stamp/签名并核验。当前源码SDK锁f487df0c相对运行Host构建锁78a5eef0只多两处test-only修正；Intel Host1d7d1674仍与原冻结生产源码绑定、严格验签通过。默认完整Shell suite 558/0通过，8项实际SDK几何窄测也通过。另一个空target release Host重编译1476.884秒PASS，复用已有Cargo/SDK缓存，未替换运行Host，不宣称全新checkout/空缓存构建。构建与旧失败见[完整测试和重建报告](official_muse/rc/remaining-20261005-r2/a4/FULL_AND_CLEAN_REPORT.md)。历史clean/磁盘失败见[源码及运行交付边界](SOURCE_DELIVERY.md)。完整运行资料不放在源码仓库。

## 4. 验收、支持与隐私

- [晨间报告](MORNING_CHAMPIONSHIP_REPORT.md)、[原二十项判定](RC_ACCEPTANCE_MATRIX.md)、[日历实际诊断](RC_CALENDAR_READONLY_REPORT.md)与[真实模型和邮箱证据](RC_FINAL_LIVE_REPORT.md)
- [历史日历修复报告](MUSE_CALENDAR_REPAIR_REPORT.md)、[历史判定](ROUND_ACCEPTANCE.md)与[历史三小时报告](THREE_HOUR_FINAL_REPORT.md)
- [源码清理报告](MUSE_CODE_CLEANUP_REPORT.md)、[SDK瘦身记录](SDK_SLIMMING_REPORT.md)和[历史截图归档](EVIDENCE_ARCHIVE.md)
- [来源和交付边界](SOURCE_DELIVERY.md)与[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json)
- [问题反馈](https://github.com/9tuore/muse-agent/issues)

仓库不包含凭据、私人邮件、生产数据库、私人实机资料、模型权重、构建缓存或安装包。真实账号录屏原件仅本地保留，公开媒体须去除账号信息。桌面候选包内置有许可证和摘要的免费 Qwen3-0.6B 及 Intel CPU runner，首次启动经官方 Host 模型配置调用；严格格式的同题测试仍为 0/2 正确，不称强模型，也不把自动配置成功当作语义通过。可在官方设置配置较强模型。`--solid-source` 打包完整冻结源码及历史证据为 tar.xz，桌面文件夹保留展开源码；源码文件集合、内容和权限独立核对，不靠删证据减小体积。

[隐私说明](docs/PRIVACY_POLICY.md)已发布到HTTPS，支持入口为[Issues](https://github.com/9tuore/muse-agent/issues)。正式 publisher 登记及独立 packet 审核仍缺；原版 Hub 拒绝本地 `calendar` capability，扩展 Gate PASS不等于上游准入。保留唯一失败证据、旧Git历史和公开Tag，不创建成功Tag。桌面ZIP要求严格小于500,000,000字节；rc51首次完整包实际527,708,351字节，大小门槛失败，完整还原与签名检查通过。正在核对整体XZ展开包，完整冻结源码、内置权重及应用保持，实际最终大小及身份以本轮 `DELIVERY.json` 为准。中文配音实录另附，完整源码内也保留媒体；未测两接收Mac。
