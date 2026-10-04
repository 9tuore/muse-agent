# 第三方源码与许可证

| 目录 | 原始来源 | 基线 |
| --- | --- | --- |
| vendor/octosense | OctoSense-org/OctoSense | 归档标签7f962547cd8035ed2bb05962cf7824d8aa33e3a3；原本没有Git对象核验 |
| vendor/app-hub | OctoSense-org/OctoSense-App-Hub | 核验基线e8601b80ce104db2e48208094714bdcffdce6b5a，隔离扩展HEAD97d75ac011818d4f8978f1a9e19cfae5e678d41d |
| vendor/makepad | OctoSense-org/makepad | runtime.json锁定bf318136a375c4d1fb7ee10e13e27336b6d98744，含 Splash 入口、Metal 回调及 storage SHA-256 交付补丁 |
| vendor/octoscript-makepad | OctoSense-org/Octoscript-Makepad | native-runtime.lock.json锁定019e6bf043b484676ff39d6ff5be58a1e94abed8 |
| vendor/octoscript | OctoSense-org/Octoscript | runtime.json锁定68f6a9df55692b5d8ef8873a12721e279a3f40d6 |

已包含的上游LICENSE和NOTICE文本保留在对应源码中；字体与其他资源许可沿用各自来源，未在本次补充中逐项复核。外部Rust依赖按Cargo.lock及其许可解析。应用listing声明Apache-2.0；vendor各文件沿用上游许可证。本仓库不将本地扩展声称为官方原版已经接受。

## 本地补充的标准许可证文本

以下文件使用匹配SDK中已有的标准Apache License 2.0文本，与`vendor/octosense/LICENSE`逐字相同，SHA256为`cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`。文本只有标准条款及附录示例，没有填入其他应用的作者或版权信息。

- 根`LICENSE`：根据Muse现有`official_muse/app/bundle/listing.json`的`Apache-2.0`声明补充许可证文本；第三方目录继续适用各自许可证。
- `vendor/app-hub/LICENSE`：根据该快照中app-policy、app-hub和card-host的Cargo.toml所声明的`Apache-2.0`补充标准文本；不声称从上游取回了原有LICENSE或NOTICE。
- `vendor/makepad/libs/i_overlay/LICENSE-APACHE`：根据所含`i_overlay` **7.0.3** 的Cargo.toml中`MIT OR Apache-2.0`声明，补充Apache-2.0选项的标准文本。原许可声明保持不变；这不是从7.0.3上游取回的许可文件，也不把Makepad版权声明用作iOverlay作者归属。

本次没有新增未核实的版权人、年份或NOTICE，没有替换已有版权声明。具体作者版权归属和额外NOTICE要求未在此补充中逐项核验；附标准许可文本不构成完整许可证合规保证。

本地源码准备修正：从匹配锁定SDK原样恢复`vendor/makepad/libs/i_overlay/src/build/`的七个Rust源码，并在根.gitignore加入该源码目录的精确例外；`vendor/octosense/tools/package_calendar_candidate.py`的Makepad资源路径改为仓库内`.sources/makepad/widgets/resources`。未改动这些Rust源码的内容，也未改变第三方依赖版本。
