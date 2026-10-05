# Muse 视频规则与最少素材（核对版）

核对产品：rc45，产品冻结源码 d306d3c0；核对工作树 HEAD 9b83f98c。后续产品修改后需重新绑定录像、包和提交号。本次不录像、不操作正在运行的 Shell。

## 已查到的要求

| 项目 | 官方依据 | 分类/适用范围 | 当前情况 |
|---|---|---|---|
| 初赛2–3分钟演示、两张关键截图 | C2「初赛」 | 官方仓库赛程文档明确要求；该文档是9/25方案 | 当前新录像尚未核验；不能自动当作复赛视频时长 |
| 至少一次操作+可核对结果，失败或空状态 | C2「初赛」 | 文档要求 | rc37/41/45已有跨版本真实任务证据；应保留版本标签 |
| 可运行程序、公开Apache-2.0源码、固定提交、启动步骤 | C1/C3 | 官网明确交付要求 | rc45已有本地ZIP，Root正在同步公开源码；独立接收机尚未通过 |
| 复赛完整演示、正常/失败场景、队外试用、已知限制 | C2「复赛」 | 文档要求，未单独规定视频长度 | 真正队外/第二Mac验收仍缺；不能用本机包检查替代 |
| 输入/理解/计划/授权/执行/核验/后续状态 | C2「复赛」 | 文档要求 | 现有同事项链跨rc37/41/45，不能说同rc45从头整链 |
| 每项目8分钟：3演示+2Agent/贡献+2问答+1切换 | C2「线上决赛」 | 答辩安排，不等于要求上传8分钟视频 | 未排最终演示顺序 |
| 10/9 23:59冻结；10/12中午前交幻灯片/顺序/同版本备用视频 | C2 | 官方文档安排，待与最新群通知确认 | Root提示用户较早群通知为6号前，存在版本差异；不擅改冻结Tag |
| 包必须小于500MB | 未在本次官方依据中找到 | **不是已证实官方规则** | rc45外层ZIP131,297,109字节，500MB是本地工程约束 |
| 必须先AppHub上架 | C1 FAQ/C3 | 官网明确无需等待上架 | 本地catalog/check/scan只能称演练/预检 |

## 最少素材清单（建议，不新增官方要求）

1. 一张版本卡：Muse版本、源码完整SHA、Host锁与本地Calendar扩展标识、架构/macOS要求。
2. 真实可见官方Shell中Muse的主页与模型/邮箱/Calendar授权状态；输入只用合成测试资料。
3. 同一事项的输入→计划→用户决定→动作→独立读回→结果卡。须让用户明确看见选择权，不能将模型计划画面当成实际动作完成。
4. 记忆的来源页及新对话检索；展示真实来源，不用人工写好的回答替代产品模型。
5. 一个真实拒绝/空状态/失联状态及可行下一步；不能故意剪去失败来写全通过。
6. 实际重启后找回原事项与结果，说明是Shell进程重启还是整机重启。
7. 结果的独立旁证（测试账号收件或系统日历读回）；若含真实账号，发布版先脱敏并保留私有原件，记录脱敏方式。
8. 已知限制结尾：Calendar本地扩展、未上游准入、实际已测机器/模型、未通过项。
9. 两张关键真实截图及可运行ZIP、固定源码、安装说明、数据来源与限制；视频不代替这些交付物。

**录像绑定：**已有rc37创建、rc41改期、rc45结算/恢复/清理的素材可以呈现开发进展，必须在切换处标出对应版本；不能剪成「最终同版本从头成功」。若最终修复为新版本，新增录像/回归要绑定其真实提交号。保留等待和结果状态，不伪造耗时，不把fixture当在线动作。

可另准备约2–3分钟精简演示与答辩素材；这是便于使用的建议，复赛备用视频长度需以赛务最新通知为准。

## 官方依据与读取时间

本次在线读取：2026-10-06T00:53:50.732166+08:00 至 2026-10-06T00:56:03.212038+08:00（北京时间）；每文件精确时间、SHA-256、URL和状态见 [SOURCES.json](SOURCES.json)。官网直接读取 HTML 与部署脚本 `index-Dp13UqI0.js`，公开源码另按真实 `git ls-remote` main SHA 固定。GitHub API `/commits/main` 返回 HTTPError，改用公共 Git transport，不使用账号凭据。

- C1：[官网](https://create.gosim.org/agenticapp26/)；[实际官网源 App.vue](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/src/App.vue)，FAQ/共同交付。
- C2：[比赛赛程](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/docs/competition-schedule.md)，9/25方案、9/26更新；不是用户群通知。
- C3：[官方提交区](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/src/components/AppHubSubmission.vue)与[Rinx路径](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/0db87b582438f0f01534435b8537e8c89bcd303d/docs/rinx-miniapps.md)。
- C4：[报名 Issue #5](https://github.com/gosimfoundation/hackathon-agenticapp26/issues/5)，本次只核对字段，不统计其他队伍、不核实星海的报名回执。
- D1：[设计仓库 README](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/README.zh-CN.md)、[AGENTS](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/AGENTS.md)、[flows](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/flows/README.md)、[script-app FLOW](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/flows/script-app/FLOW.md)、[QUICKSTART](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/QUICKSTART.md)。
- D2：[SCRIPT-API](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/SCRIPT-API.md)、[CAPABILITIES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/CAPABILITIES.md)、[HOST-SERVICES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/HOST-SERVICES.md)、[AI-SERVICES](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/AI-SERVICES.zh-CN.md)、[PUBLISHING](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/a5a87d3c3ff305768ae46bc5f6689abb48115cc4/docs/PUBLISHING.md)。
- H1：[最新 AppHub 发布契约](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/9e7f0778429125402dcfefef95ba2b01e8de7b94/docs/PUBLISHING.md)、[app-contract manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/9e7f0778429125402dcfefef95ba2b01e8de7b94/crates/app-contract/src/manifest.rs)。
- H2：[当前锁定上游发布契约](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/e8601b80ce104db2e48208094714bdcffdce6b5a/docs/PUBLISHING.md)、[当前锁定上游 manifest](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/e8601b80ce104db2e48208094714bdcffdce6b5a/crates/app-policy/src/manifest.rs)。

分类：**强制**是对应比赛交付或Hub技术契约明确写出的条件；**建议**是准备方法；**推断**是由当前代码/证据得出的工程判断；**待确认**是规则版本、身份或真实测试尚无证据。Hub技术契约不是比赛日程或评分表。
