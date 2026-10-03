# Muse

## 把对话变成可核对的行动

Muse 是 **GOSIM Agentic App 2026** 参赛项目，由「星海」团队开发。它在 OctoSense 官方容器中提供中文 AI 对话、邮件提醒与回复、系统日历操作、带来源的全局记忆和可核对的任务结果。

**当前官方应用源码：0.3.16 · 总体验收：PARTIAL**

- 左侧：可折叠对话历史，以及邮箱、日历、记忆、操作记录、能力授权和设置入口。
- 中间：聚焦当前讨论的聊天与输入；新消息显示在当前聊天末尾，历史可翻页查看。
- 右侧：有效结果卡、来信提醒和具体动作确认，技术详情默认收起。
- 新对话沿用同一用户授权范围内的全局记忆，每轮只检索相关内容，保留项目与归属边界。
- 长期目标产品页面已移除；一次性任务的计划、批准、执行、结果、记忆和恢复保留，历史数据保留。

![合成新来信自动结果卡](official_muse/prelim/evidence/fix-guide-0313/mail-visible-final/automatic-incoming-card.png)

*真实可见 card-host 截图，0.3.13 合成邮箱输入；展示来信卡交互，不作为0.3.16真实邮件验收。*

## 核心功能与当前修复

| 模块 | 实现与边界 |
| --- | --- |
| Chat | 使用官方 `model.complete`，保存对话，支持具名删除确认；0.3.16 改进新消息与回复的可见性 |
| 邮箱 | 官方 Host 登录、读取正文、自动来信卡、按意图起草或手写回复、逐项确认发送；0.3.14 修正真实Host的字符串时间字段兼容 |
| 系统日历 | 使用配套 EventKit 宿主扩展；查询、候选确认、创建/修改/删除及独立读回，不能把本地模拟当系统完成 |
| 全局记忆 | 真实存储、来源、归属、有界检索、更正和遗忘；冲突保留并要求处理 |
| 一次性任务 | 计划/批准/执行/结果/验证/恢复与防重复；外部动作以实际服务回执及独立读回为准 |
| 交互稳定性 | 16个对话后有明确删除入口；Mail慢操作使用单后台线程和8项队列，避免钥匙串等待卡住UI |

本仓库保留源码、相关测试与真实通过/失败记录。**上传源码不代表20项产品验收已全部通过。** 旧候选的模型、邮件、日历和重启证据不能代替0.3.16完整链验证；本次上传没有重新执行真实外发、日历写入或付费模型测试。

Calendar及配套宿主/框架补丁是本地扩展，尚未被官方上游接受。本地扩展 `hub check` 通过也不等于官方原版已接纳；本机运行包采用开发用 ad hoc 签名。

## 完整源码

| 路径 | 内容 |
| --- | --- |
| `official_muse/app/bundle/` | 当前0.3.16 Splash入口、manifest、listing与资源 |
| `official_muse/global_memory.splash`、`incoming_mail.splash` | 记忆DSL与来信模块源码；实际应用入口仍是bundle/main.splash |
| `official_muse/ui_memory/`、`prelim/`、`round2/`、`phase2/` | 迭代源码、测试、宿主补丁与可公开证据 |
| `vendor/octosense/` | 实际配套完整宿主源码，包含Mail后台工作队列与系统日历服务 |
| `vendor/app-hub/` | 配套App Hub源码与本地Calendar准入扩展 |
| `vendor/makepad/` | 锁定框架源码，含当前Host采用的可信模块启动补丁 |
| `vendor/octoscript/`、`vendor/octoscript-makepad/` | 配套语言和脚本运行时源码 |
| `app/`、`scripts/`、`miniapp/`、`patches/` | 保留的桌面版源码、脚本、测试与历史补丁 |
| `MUSE_HANDOFF/` | 开发规则、历史状态与交接资料 |
| `SOURCE_MANIFEST.json` | 来源版本、文件SHA256与四个相对依赖链接 |

凭据、账号配置、生产数据库、私密实机截图、模型权重、编译缓存与安装包不上传。第三方来源与许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 构建

环境：macOS、Rust工具链、Apple Command Line Tools；外部Cargo依赖按锁文件获取。四个 `.sources/` 链接均指向本仓库内部对应vendor目录。

```sh
cd vendor/octosense
cargo build --locked --release -p octosense --bin octosense --no-default-features --features app-hub
python3 tools/package_calendar_candidate.py --release --output ../../build/Muse-OctoSense.app
cd ../app-hub
cargo build --locked -p octosense-app-hub --bin hub
cargo build --locked -p octosense-card-host --bin card-host
cd ../..
```

当前bundle带有本地开发签名，核对时需显式提供它的公开验证密钥：

```sh
./vendor/app-hub/target/debug/hub check official_muse/app/bundle --allow-unsigned \
  --publisher-key muse-local-rehearsal=bb05ce91333a0045f9f8187eba865f11d9e14ec636aeaee80144708984e740c5
```

上面仅含公钥，不含发布私钥。开发检查不代替真实安装所需的Gate、catalog与能力授权；禁止通过 `dev-grant-all` 绕过。模型在官方Host设置中配置，账号密码/授权码只输入官方Host面板。

仓库是完整源码快照，不包含上游Git对象；不宣称上游Git provenance检查已通过。构建运行仍须按照[宿主说明](official_muse/phase2/host_extension/README.md)和对应测试文档确认环境。桌面历史入口见[本地运行说明](README_LOCAL_AGENT.md)。

## 版本与证据

- [当前源码交付](SOURCE_DELIVERY.md)
- [本轮修补指南核对](MUSE_FIX_GUIDE_AUDIT.md)
- [0.3.16聊天末尾可见测试](official_muse/prelim/evidence/chat/tail-visible-040/README.md)
- [0.3.13稳定性与来信卡证据](official_muse/prelim/evidence/fix-guide-0313/README.md)
- [开发规则与后续GitHub同步](MUSE_HANDOFF/AGENTS.md)

用户已授权：**每次完成版本更新后同步源码、提交并推送本仓库main，随后核对远端HEAD**。保留失败证据和验收边界，不上传私人运行资料，不覆盖远端历史或公开Tag。
