# Muse 官方应用 · 当前候选0.2.8

中文对话、长期目标、记忆、活动记录、邮箱、日历、能力授权、设置八页。宽窗三栏，窄/矮窗滚动；高窗口输入区避免Shell Dock遮挡。

申请storage、model、mail、calendar四项实际使用能力。Chat/Goal模型建议由官方model.complete完成；结构化结果限本应用隔离存储。Goal计划与输入绑定，用户批准后写入、独立读回并持久化Run；重启不重复动作。

Memory来源/更正/固定/墓碑与Activity只记录真实应用事件。完整Memory DSL、来源hash、可编辑模型预算和视觉仍有差异。

Mail仅使用官方Host账号登录与服务，不收密码；读取、起草、精确预览与单独确认有实现，真实账号收发及收件端尚待本人。accepted不等于投递，Host无线程回复头，因此按新邮件声明。

Calendar使用隔离EventKit最小扩展，须AppHub grant、真实TCC和单独动作批准；创建/修改/删除后独立get再核验。原版Gate不接受calendar，上游尚未接纳补丁。

最终3新Goal、Calendar合成CRUD、23文件重启及五尺寸真发送通过。Chat语义三次复测2/3，整体PARTIAL。详细验收与复现入口见 ../README.md 和仓库根目录PHASE2_LIVE_TEST_REPORT.md。没有新Capability/Phase3、正式签名、push或issue提交。
