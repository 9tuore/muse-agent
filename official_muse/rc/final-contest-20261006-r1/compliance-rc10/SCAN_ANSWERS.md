# rc10 scan 人工审核说明

这是发布者自查答复，未宣称已获独立 reviewer 批准。

1. 产品声明与实现：main.splash 中 mail_watch_sync、mail_analysis_pump、calendar_auto_scope、calendar_finish_link、gm_retrieve、calendar_reconcile_verified 分别负责来信、限定自动安排、核验回执、相关检索与只读对账。实际状态及未通过项目见 FINAL_REPORT.md。长期 Goal 产品页已移除，保留一次性任务执行数据。
2. 平台与分类：macOS / productivity。实际配套宿主为 Intel macOS 14+；App Hub bundle 为 Splash 文本应用，不包含原生可执行文件。
3. 授权：storage 保存应用私有数据；model 通过官方 model.complete；mail 使用 Host 登录与账号授权；calendar 查询和操作所选日历；glance.publish 发布当前应用提醒卡。network.hosts 为空，没有应用自带外部网络通道。所有服务还受用户授权和实际宿主支持限制。
4. 界面：Muse 不采集邮箱授权码或模型密钥；邮箱登录由宿主 sheet 提供。系统权限由 macOS 处理。未仿冒付费或系统授权页；不替用户确认外发。合成验收自发自收来自本人明确委托。
5. 模型提示：source 中存在有界 model.complete 的 task/schema 指令，是应用发送给模型的业务输入。邮件正文始终作为外部资料处理，不执行邮件内的指令。bundle 未声明独立 agent、tools 或 skills。
6. 未见针对私人个体的侮辱、攻击或滥用文字。公开媒体已去除本人账号地址，私有资料与凭据不在提交包。
7. 路由：human-review。首次 unsigned 提交需维护者审核；macOS EventKit 目前依赖随源码交付的宿主扩展，不宣称原版 Shell 已集成；既有完整冷启动矩阵和第二个独立强模型仍有缺项。请求先审核精确 bundle 与扩展边界，必要时转为配套 Shell 集成流程。
