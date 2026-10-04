# 0.3.22 开发源码交付

2026-10-04。总体验收PARTIAL；至少18/20门槛未达到。最新真实payload和匹配宿主逐文件SHA绑定。最终版本一次真实冷启动，旧0.3.20 10+5作为支持证据。源码、评审和运行宿主分开，排除账号、凭据、生产数据库、模型权重、缓存和私密实机截图。未正式申请App Hub；旧Tag不动。

官方应用入口仍为OctoScript/Splash，配套Calendar/框架/模型Rust扩展未宣称官方上游已接纳。

# Muse 参赛源码交付 · 0.3.19（PARTIAL）

- 仓库：https://github.com/9tuore/muse-agent，分支 `main`。
- 产品提交：`b0708d8620ae0cd84f231a36081ba2578f064b79`；启动器提交：`54f0e97`。
- 导出来源：`67612e99b406593a1da840f7a0a68cc9966b4ab6`。本人2026-10-04要求“先同步到GitHub”，单独交付当前开发源码，产品仍PARTIAL。
- 官方入口：`official_muse/app/bundle/main.splash`，语言 **OctoScript / Splash**。
- 可读源 SHA256：`a490c2731986593921768a2d95884525e79e72c05b67aac5a6400bc7d2e408bc`。
- 实测compact源 SHA256：`1bdcb11de319d56268e4e8952cc25ae349e853d6c33656cf713c69a4c018b682`；此前官方tokenizer核对86343个token、字符串及换行标记一致。公开bundle保留可读源，未包含安装包。
- 公开bundle重新stamp、按已有开发身份签名并check通过：`muse-goals 0.3.19 — PASSED`；BLAKE3为`1f0db6c5d401fab733542aa8df4cc66fe8f4709d0c7d51434ba4594b84aeb762`。仅本地扩展Gate，不等于官方原版接纳Calendar或正式发布。
- 配套Shell SHA256：`a86364ccb3b4733d24193159fea264d19379df511b5943c6aa513cd09e2f816e`；card-host SHA256：`c2dd49332dffce99023264d2fec636fcae2529e3a082ee14494532cec46b0e61`。二进制不上传。

## 本次同步

当前官方应用、安排/改期模块、全局记忆与来信模块、测试和脱敏报告同步到仓库。完整锁定vendor保留，实际配套Host的3个变动文件原样同步：EventKit忙闲/全天/循环元数据、发信引用检查、收信In-Reply-To字段。

此前源码完整性修正保留：i_overlay七个Rust源文件、仓库内相对资源路径、标准许可证文本及四个内部依赖链接。打包路径修正与原本地构建目录的相邻路径差异单独记录，不冒充Host业务逻辑差异。

## 实际验收边界

**5 PASS / 11 PARTIAL / 3 BLOCKED / 1 FAIL，整体PARTIAL。**

0.3.19窄/宽/矮窗输入修复及编辑清空通过；最后完整冷启动仍触发官方64ms预算，主界面未载入，不宣称稳定恢复通过。0.3.18真实新信卡、一次手写回复与本人收件确认、同ID日历CRUD/独立get/清理及两次相关重启保留为版本绑定的节点证据；未改392业务函数与匹配Host的支持复用不冒充同候选完整执行。

111项确定性安排断言、Memory25项真实本地存储/更正/遗忘/恢复、发送防重复负例及原生标题可见验证各有明确范围。附加失败与原失败保留。最终同事项邮件→日历→回复→重启→跨对话模型召回尚未完成；模型S03格式错误及缺失用量未解决，收费暂停；独立第二模型通道尚未配置。

完整判定见[ROUND_ACCEPTANCE.md](ROUND_ACCEPTANCE.md)，简报见[THREE_HOUR_FINAL_REPORT.md](THREE_HOUR_FINAL_REPORT.md)。公开摘要位于`official_muse/prelim/evidence/three-hour-0318/`；原始失败证据与私人实机资料留本机，未以脱敏摘要覆盖原记录。

## 源码与隐私

`SOURCE_MANIFEST.json`列出来源、逐文件SHA256与相对链接，不包含自身哈希。未复制原开发Git历史、凭据、账号配置、私人邮件、生产数据库、私人实机截图、付费账表、模型权重、运行缓存或构建输出。本次同步没有操作用户窗口、发送邮件、修改日历或调用付费模型。

普通快进同步main，不覆盖历史，不改旧Tag，不创建成功Tag，不发布应用，不重复评论比赛issue。源码同步完成与二十项产品全过分别报告。
