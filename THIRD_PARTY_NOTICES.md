# 第三方源码与许可证

| 目录 | 原始来源 | 基线 |
| --- | --- | --- |
| vendor/octosense | OctoSense-org/OctoSense | 归档标签7f962547cd8035ed2bb05962cf7824d8aa33e3a3；原本没有Git对象核验 |
| vendor/app-hub | OctoSense-org/OctoSense-App-Hub | 核验基线e8601b80ce104db2e48208094714bdcffdce6b5a，隔离扩展HEAD97d75ac011818d4f8978f1a9e19cfae5e678d41d |
| vendor/makepad | OctoSense-org/makepad | runtime.json锁定bf318136a375c4d1fb7ee10e13e27336b6d98744，含 Splash 入口、Metal 回调及 storage SHA-256 交付补丁 |
| vendor/octoscript-makepad | OctoSense-org/Octoscript-Makepad | native-runtime.lock.json锁定019e6bf043b484676ff39d6ff5be58a1e94abed8 |
| vendor/octoscript | OctoSense-org/Octoscript | runtime.json锁定68f6a9df55692b5d8ef8873a12721e279a3f40d6 |

上游LICENSE、NOTICE、字体与资源许可随对应源码保留。外部Rust依赖按Cargo.lock及其许可解析。应用listing声明Apache-2.0；vendor各文件沿用上游许可证。本仓库不将本地扩展声称为官方原版已经接受。
