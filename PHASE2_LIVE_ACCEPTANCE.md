# Phase 2 最终实机验收矩阵

最终候选 Muse 0.2.8；整体 **PARTIAL**。LIVE指真实可见OctoSense Shell，LOCAL/UNIT/FIXTURE/HISTORICAL不升级为LIVE。原0.2.2矩阵保留为历史。详细实际结果见 [报告](PHASE2_LIVE_TEST_REPORT.md)。

| 项目 | 最终结果 | 证据性质 | 证据与边界 |
| --- | --- | --- | --- |
| 启动/App Hub安装 | PASS | LIVE | 正常打包.app、签名本地catalog、0.2.8 manifest与源哈希一致 |
| Chat空态 | PASS | LIVE/HISTORICAL | 0.2.8窗口测试新会话起始空态；旧独立before为历史 |
| AI真实对话 | PASS | LIVE | 最终9轮model.complete均success |
| 多轮语义稳定 | FAIL | LIVE | 指定三轮复测2/3；repeat-2位数与禁止重复失败 |
| 会话隔离/输入校验 | PASS（有限） | LIVE7/LOCAL3 | 0.2.7新/切换草稿清空、消息保持、空/超限拒绝；最终8独立会话与重启 |
| 多Goal/Plan/Approval | PASS（受限） | LIVE | 最终3新Goal、各1Run；精确批准后写入/读回 |
| 模型建议/Result | PASS | LIVE | 3结果带真实模型建议，源/目标/Run绑定与SHA匹配 |
| Error | PASS（有限） | LIVE/HISTORICAL | 最终Chat真实语义错答保留；0.2.4provider断连、0.2.6格式错误和超限UI |
| restart restore | PASS | LIVE | 最终23哈希不变；计数不变；Activity只新增restore |
| Goals列表/详情 | PASS | LIVE | 最终页面截图及3Goal完成、结果核对 |
| Memory页面 | PASS | LIVE | 最终可进入，已更正/删除状态持久化 |
| Memory完整迁移 | PARTIAL | LIVE7/8 | 来源/更正/置顶/墓碑；6来源hash为空、完整DSL及旧资料未迁 |
| Activity页面/归属 | PASS（Muse范围） | LIVE | 最终180事件；关联错配0；不含整台电脑观察 |
| Capability/Settings | PARTIAL | LIVE | grants真实只读；模型/provider/预算不可编辑 |
| Mail连接入口 | PASS | LIVE | 官方Host空登录面板可打开；本人未登录 |
| 真实Mail读取/起草/发信/投递 | BLOCKED | LIVE缺失 | 需本人邮箱、本人地址与最终发送确认；demo为FIXTURE |
| Calendar权限 | PASS（当前full_access） | LIVE | 真实TCC、4日历；拒绝/撤销/升权反例未实测 |
| Calendar CRUD/独立读回 | PASS（合成事件） | LIVE | 最终create/get/update/get/delete/get；事件已清理 |
| Calendar冲突/版本/重放反例 | PARTIAL | HISTORICAL/UNIT | 0.2.6真实冲突阻断；其余未final LIVE |
| 邮件→日历同Goal/联动恢复 | BLOCKED | LIVE缺失 | 单独Calendar收据goal/run为空，不充当同任务 |
| 八页中文/三栏 | PASS（结构） | LIVE | 最终八页与全屏结果页；Host登录英文未改 |
| 窄/宽/矮窗 | PASS（实际可达尺寸） | LIVE | 五尺寸真发送；请求412×892实际412×818；990×300内容98pt |
| 完整412×892 | PARTIAL | LOCAL | card-host完整尺寸可见；真实Shell受物理桌面夹紧 |
| 长文本多卡片 | PASS（存储UI） | LIVE | 735字8项、990×300、滚动批准与读回；没有长文模型调用 |
| 核心卡片逐态1:1 | PARTIAL | LIVE/源码 | Plan/Approval/Result/Error/Memory/Activity/Capability存在；每类六状态非全实测 |
| 独立版视觉1:1 | PARTIAL | HISTORICAL+LIVE | before历史真实参考；仍有技能/设置/结果层级差异 |
| 扩展hub check | PASS（本地） | LOCAL/LIVE | unsigned开发检查、真实注册key签名检查；7问自审human-review |
| 原版calendar准入 | FAIL/预期拒绝 | LOCAL | 本地扩展尚未获上游接受 |
| 源码/GitHub准备 | PARTIAL | LOCAL | 可导出纯源码；真实publisher、扩展准入、剩余验收未完成；未push/评论 |
| 旧独立版保护 | PASS | LOCAL | 严格验签与主程序SHA不变；不改生产数据 |

只有剩余LIVE闭环、语义及1:1差异解决后才能UI_PARITY_PASS。本轮不能标全功能完善。
