# 源码清单

| 项目 | 固定身份 |
| --- | --- |
| Muse 核心 | 0.3.26-rc51；产品提交 `6b46c3c8cc3ea5b5d5d9073224a3b303b8b1d109` |
| 本次包装基线 | `7175af663c55703959b481791a304196343df5b6` |
| 已有完整公开源码冻结 | `a4cf4d9e6cd3ff1067e2821a29d4e5be48d2ad39` |
| 开发源码 | `official_muse/app/source/main.splash` |
| 实际 App Hub bundle | `official_muse/app/bundle/` |
| Calendar Extension 提交 | `92b1df15112a1d5edf6336a3d3cfae181b4a99ca`；`sdk-overlays/octosense/apps/calendar/host-service/` |

此 source 目录只记录身份，不复制几百 MB SDK。下载固定源码：[GitHub 基线](https://github.com/9tuore/muse-agent/tree/7175af663c55703959b481791a304196343df5b6)。

## 官方 SDK pins

- makepad：`bf318136a375c4d1fb7ee10e13e27336b6d98744`，https://github.com/OctoSense-org/makepad
- octosense：`7f962547cd8035ed2bb05962cf7824d8aa33e3a3`，https://github.com/OctoSense-org/OctoSense
- app-hub：`e8601b80ce104db2e48208094714bdcffdce6b5a`，https://github.com/OctoSense-org/OctoSense-App-Hub
- octoscript：`68f6a9df55692b5d8ef8873a12721e279a3f40d6`，https://github.com/OctoSense-org/Octoscript
- octoscript-makepad：`019e6bf043b484676ff39d6ff5be58a1e94abed8`，https://github.com/OctoSense-org/OctoScript-Makepad

`dependencies.lock.json` 与 `sdk-overlays/` 一起复现准确依赖；根 lock 的 product_version 字段仍是历史0.3.22，实际应用版本取 bundle manifest 0.3.26-rc51，不据该历史字段回退。Host 是既有签名二进制，构建锁78a5与当前源码锁f487存在两处仅测试代码差异；本次没有重建或换 Host。

## 复现

按 [RUN_GUIDE.md](../RUN_GUIDE.md) clone、checkout固定提交、bootstrap、build、run。现有配套Runtime与正式上游Calendar准入分别记载，不能混称。

本次在全新临时目录从固定Git提取运行核心、bootstrap、锁和overlay，并逐文件核对字节、模式及overlay摘要。此检查不是全新SDK下载或完整编译；详见 SOURCE_MANIFEST.json。
