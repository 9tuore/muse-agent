# rc50 增量修复与失败边界

总体 **PARTIAL**。这一步没有新系统日历写入或新发信。

- 新对话的首次持久写入即带完整 proposals/focus_project/focus_owner/goal_id，避免补字段前中断留下半形状记录。真实 card-host fixture 在首次写入边界停止：旧版3PASS/1FAIL，修后4PASS；不替代完整冷启动。
- 邮件→候选的链接保存与 Goal 审计分成独立短回调，既有 source/Goal/revision/account/session 守卫不变。当前 compact 的4项生产函数 fixture 通过，源 claim 及审计一次保存，排队一个模型请求，零日历/邮件写入。
- 左快捷区占高从205..280缩为80..205，仍可滚动。a2/rc50/FINAL_REPORT.md 的四尺寸可见 fixture 通过；412×892请求实际412×809。原生标题/存储路径未改。

readable `0e705f33c36c77e32c335c1489a7ebe047a2e6476a473a4678cbffb767ca480f`，compact `15ba9ea00f55079a1243ca1dfab9b266b23e434855b69bd49cd13fb9d524d471`，官方token98488相等。Host `1d7d1674`、capability、预算及权限未变。本地扩展Gate/check/scan/catalog通过，仅演练签名；不代表原版calendar准入。

真实授权隔离候选已更新，32个应用数据文件在初次替换前后保持；随后rc50-r2 Shell重启五个非轮询持久文件/模型ledger及8条提醒键-状态-正文摘要保持，mail-watch原始文件随正常同步改变，不能写六文件全保持。新的合成源信在rc49只发一次并实际同步出结果卡；rc50-r1真实M3整理出10月8日15:00–15:30候选，目标工作日历真实查询无冲突，只给一个核验时段。预览 waiting_user 及重启恢复均有记录。新事件没有批准，未写入；本人收件声明没有代填。

A4 当前rc50-r2严格实机冷启动8/10、普通关闭重开5/5，原失败保留：一次UI整树eval预算中断，另一次启动导航失败待分类。此前多个旧全链fixture异步时序及source preparation失败同样保留，不计通过。Root继续在隔离rc51试验一次原生mount和仅活动页面刷新，未经验证不覆盖本步结果。

第二GPT单通道在旧rc49载体实际请求一次，无fallback，HTTP200/text-html/1166字节，Host provider错误；需要正确API配置，当前T17未过。内置0.6B两题实际仍0/2，不称强模型。T18没有同最终全链；不重标跨版本链、OS重启或正式上架。旧安装/生产/稳定0.3.25/旧Tag与dirty baseline保留；只按本人既有授权正常同步源码。
