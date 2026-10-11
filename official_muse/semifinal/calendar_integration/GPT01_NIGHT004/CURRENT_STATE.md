# NIGHT-004 ZC01

2026-10-12：中央基线 2395a70c/main SHA768e295d。真实当前 SDK CalendarService::call、handle、storage、ui、cards 在自有 harness 编译；9 个独立进程完成创建→同 ID 回读→同 ID 更新→更新后回读→旧 expected 拒绝→外 app owner 拒绝→删除→不存在回读→再次重启不存在。创建/更新/删除跨进程持久化 PASS。构建 nice10/jobs1，复用自有335M debug target，14.481秒；完整 binary SHA/逐步请求结果在 OWNER_RESULT.json。

状态 PARTIAL：owner-service 隔离进程验证通过；真实 Relay/授权拒绝/撤销尚在处理。传输 Replier、ServiceHost、权限均为明确 fixture；没有本人真实 Agent consent、GUI、完整 Host/Kernel、模型、付费网络或用户资料操作。当前 SDK 源码按字节复制，没有改共享 SDK/main/bundle/target。旧证据不动。
