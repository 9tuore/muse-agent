# Muse 0.2.9 最终测试报告

状态：**PARTIAL**。实测日期2026-10-01至10-02，Asia/Shanghai。最终产品源17e63c5、测试4729e7a；候选SHA见[身份记录](evidence/phase2-final-029/records/candidate-provenance.json)。本文所有最终LIVE数据来自同一最终脚本，旧版本仅作历史。

## LIVE：真实可见打包OctoSense

- 经本地签名App Hub正常安装，LaunchServices启动，中文八页真实渲染。安装源与仓库源字节一致。
- Chat A/B/C共5次真实回复：A代号回忆、C隔离通过；B返回“3147”，SEMANTIC_LIMITED。逐条role/history SHA审计通过。Host JSON修复重试与应用重复user已区分；未硬编码测试答案。
- 三个模型Goal各一个完成Run。现有流程是模型建议先生成，批准绑定当前Goal/revision/result path后执行Storage/Readback；不声称批准后另启动模型。另一个679字符、2021字节、八条资料的长文Goal完成无模型Storage链。
- 4个result源SHA均匹配各自文件精确字节，来源/claim由独立MemoryGraph测试SQLite与DSL验证器接收。真实页面更正、固定、删除通过；created_at和来源历史保留；2墓碑。总4claim、3活跃。
- Activity每Goal创建/批准/写入/读回/来源记忆各一次；模型、限流、真实不可用、权限状态、重启事件有实际依据。审计42条，后续操作会增长；没有造邮件/系统日历成功事件。
- 模型不可用：只停止本轮8081转发器，保留共享8080模型；UI真实error。恢复转发器后success，失败消息对未进入下一次上下文。
- 正常重启整个Shell：7个账本/产物SHA一致；Goal4/Run4/Action0/Memory4不变；Activity只新增restart restore。原A/C会话消息SHA、pinned与墓碑保持。外部文件不存在，不能据此算Mail/Calendar防重复LIVE通过。
- Mail官方accounts真实为空；已观察并打开官方Host登录sheet标题。凭据字段未采集，登录中不截图。真实收发未执行。
- Calendar真实status=not_determined；已请求本人完整访问。本轮未创建/修改/删除任何系统事件，旧0.2.7 CRUD不计最终PASS。

## 响应式

| 请求 | 实际client | Chat内容高度 | 真发送 | Goals/Mail/Calendar、长详情滚动、返回输入 |
|---|---|---:|---|---|
| 412×892 | 412×818 | 507 | PASS | PASS，邮箱/日历为真实未授权状态 |
| 990×539 | 990×539 | 337 | PASS | PASS |
| 990×400 | 990×400 | 198 | PASS | PASS |
| 412×1100 | 412×818 | 507 | PASS | PASS，物理桌面限制 |
| 1200×700 | 1200×700 | 498 | PASS | PASS |

发送/输入位于Dock上方，宽窗右栏可见、窄窗折叠。已实际检查矮窗和宽窗PNG；未声称高窄请求实际渲染为892或1100。所有最终视觉图来自正确渲染的可见Shell，hidden仅用于功能探针。

## LOCAL / FIXTURE：不代表真实收发或系统事件

- 核心card-host契约37个布尔检查通过：3Goal/4Run，scope、旧revision/重复拒绝、未知外部动作恢复，Memory更正/固定/删除/内容hash别名阻止回流/缺hash拒绝。
- 核心四次启动：旧文件保护、重启、损坏主记录保护、备份读回，来源和活跃claim通过独立DSL/MemoryGraph测试DB。
- Native SHA九组Python对照：空串、abc、中文emoji、55/56/64字节边界、7000字节中文、4000ASCII、65536边界；65537字节拒绝。无新增capability或预算提高。
- 可见card-host三Goal/崩溃窗口恢复：原Run完成、SHA不变，time budget错误0。
- Chat legacy/backups：2会话隔离、旧chat.json不变；损坏/缺ID/缺messages恢复。
- App grant拒绝和无服务：真实card-host拒model请求、不进入Host队列；均持久化error。Calendar未获grant显示受阻且无执行确认。拒绝文案仍较笼统；TCC denied实机路径未验。
- 隔离Calendar Host单元3/3；官方Mail Host单元8/8，另2个网络/keychain测试ignored。脚本服务器/fixture不算本人邮箱收发。

## 失败与修复

1. 首轮C误选同分钟空会话：测试按实际保存顺序选按钮并断言ID，最终C通过；产品标题重复差异保留。
2. to_chars编码误作字符串导致来源拒绝：修复UTF-8摘要与hash编码校验后，重新Gate安装、重跑所有最终实机测试。
3. 第二Goal触发默认6次/分钟限流：保留错误与同Goal，冷却后真实重试，未产生重复Run。
4. 第三Goal首次截图404：动作已完成，切页重绘后重新保存截图和独立审核产物，未重复执行。
5. scan初次未注册公钥被正确拒绝：补已验证公开key后重跑，七问packet生成、自审human-review。
6. negative测试初始期待文案错误：按真实Host拒绝日志和现有“未获calendar grant”断言，保留失败记录；未改产品制造PASS。

## Gate、构建与边界

本地扩展签名check PASS；未注册key正常拒绝；stock Gate拒calendar。scan七问完整，human-review。44份候选源码模式扫描无疑似Secret，不是扫描全机器或账号凭据。旧0.3.1严格验签PASS，主程序SHA `9301e64773cfa01b0a3d2319a1ba3ca889be114365d5c6d1022364f53a829583` 不变。

Shell locked Release构建11m59s、patched card-host构建9m17s，宿主严格ad hoc验签通过。SHA/补丁与实际环境见身份记录及host_extension/README.md；本地Calendar和fs.sha256扩展未声称已获上游接受。

尚未完成：最终Calendar CRUD/readback、真实Mail收件/独立确认发送/收件端确认、Mail→Calendar同Goal及双批准、外部动作重启防重复。须完成本人节点继续，不以旧版/fixture补PASS。
