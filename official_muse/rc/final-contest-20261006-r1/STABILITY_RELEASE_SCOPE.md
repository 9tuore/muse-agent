# 参赛运行范围与清理核对

截止：2026-10-06 23:30，北京时间。运行候选保持0.3.27-rc10的已校验字节。

## 已执行的分发清理

- 运行时App Hub载荷仅六份允许文件（Splash入口、manifest、listing、图标、两张真实截图）。
- Host与离线推理文件依照固定清单和SHA保留必要依赖，不以删除依赖或模型换取体积达标。
- 实验候选、失败探针、fixture、私人模型配置、账号资料、生产数据库、构建缓存不作为运行载荷安装。源码和历史测试材料独立提供；旧失败记录保留。
- 传输包489,595,070字节，完整恢复与五项入口保护检查通过。

## 不盲删的依据

六个在主程序内仅出现定义的辅助函数，经跨文件核对仍由既有日历就绪、记忆隔离、迁移和恢复测试调用：page_calendar_readiness、page_mail_readiness、gm_forgotten_text、gm_context、chat_boot、chat_earlier_context。因此未删除这些测试依赖，也未删除核心计划/确认/独立读回/防重复。

实际仍有日历删除后Activity回执的脚本预算故障；仅删除Activity或独立读回会造成假成功。保留accepted记录和精确合成事件ID，禁止重放delete，等待只读对账。现有正常聊天、邮箱、创建/改期和记忆不因“清理”回退。此项不能报告已修复，整体仍PARTIAL。

## 提交

GitHub main和v0.3.27-rc10已同步。App Hub issues/112已提交human-review，维护者尚未上架。配套EventKit宿主扩展范围和缺项已披露。
