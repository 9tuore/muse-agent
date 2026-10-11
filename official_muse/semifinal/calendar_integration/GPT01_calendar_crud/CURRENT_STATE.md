# GPT01 Calendar CRUD 当前状态

2026-10-11：响应“优先搞定日历新建、删除等真实调动功能”，只在 codex/gpt01-calendar-history 自有 worktree 形成三个最小增量。状态 TARGETED_FIXTURE_PASS_LIVE_CRUD_PENDING。本轮 17 项历史/回执与 4 项真实 owner-service 合成数据 Rust fixture 通过，共 21 PASS / 0 FAIL。没有共享 SDK、Hub、主线、bundle、Host 二进制或用户数据写入。

当前正式名字是 calendar.remove_event，不存在 calendar.delete_event。已有 owner-service 支持 add_event、update_event、remove_event、get_event；更新/删除工具声明要求 expected 快照、destructive、confirm:host、auto_approvable:false。服务 remove_event 保留 own UI 的可选 expected 行为，本补丁不改变该兼容入口；跨 app Agent 通过现有严格 schema 必须提供 expected。

候选将 Muse manifest/Host ceiling、Broker receipt、历史显示与调用映射日志从四个工具扩展到六个。owner handler、Relay 授权、原有确认机制和服务存储实现未重写。AGENT 文档明确完整快照、全字段更新、本人确认、精确回读与未知结果对账；过期快照不自动重试。

验证 BASELINE.json 的 11 项 before SHA 全部匹配，再在各对应根目录零模糊 dry-run/apply；三个 patch 已通过自有副本应用及 after 字节比对。BASELINE.source_heads 是包含源码目录的项目 Git HEAD，不能误称 SDK/Hub 的独立官方 upstream revision。

原可工作 artifacts-rc3 Host 指纹 ec83a4f9、Kernel 指纹 56761a9f 已只读计算完整 SHA。现有 Host 构建回执记录 aec5dda8，与工作 Host 不同；尚未从观察到的回执建立原工作 Host 的源码构建环境。Host 增量须由中央沿该实际环境编译/签名/配对，不能拿不同源码构建或另一启动方法直接换包。

未完成：原配对 Host 的源码构建环境定位、签名 catalog fixture 的实际重跑、真实 Host/Relay 本人确认、官方 Agent 同身份 CRUD full-chain、GUI 与换包。这里的 21 PASS 是明确临时数据 fixture；不代表本机用户日历已 CRUD 成功，也不代表 OS/Google Calendar 同步。

Kernel 构建已因本次优先级切换暂停，源码、1.4GiB target 与两轮日志保留；暂停证据在 ../GPT01_continuity/integration。第二轮状态 BUILD_PAUSED_BY_USER_CALENDAR_PRIORITY，未得到完整 binary 或正式 RPC PASS。本任务不恢复该构建。未 push。
