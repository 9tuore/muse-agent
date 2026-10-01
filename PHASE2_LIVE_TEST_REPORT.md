# Muse Phase 2 实机联调报告

日期：2026-10-01。**状态：PARTIAL**。最终 Muse bundle **0.2.8**；分支 `codex/muse-official-migration`，产品修复提交 `56fec94`，测试/源码导出提交 `e64d243`。没有 push、GitHub issue 评论或正式发布。

## 版本与保护边界

- Muse main.splash SHA-256：`c3c320a89f342f95b029eef1a22d08208d8b0643f846c2f0e991d42af8ee4d6d`；bundle BLAKE3：`5ac14d5b7a80441d6779fb20bded8c9a689475d53840a6ca6e816a96c07957dd`。
- 真实运行环境：`OctoSense Muse Phase2 Live 0.2.8.app`，正常 Launch Services 打开，App Hub 从本地签名 catalog 安装。Shell Info 版本为 0.1.0；0.2.8 是 Muse bundle 版本。
- 本地 ad hoc 签名宿主可执行 SHA：`a4edbe60ca54c7c83fa497065d97a9e90b465da1d874c8d5c1076d0b46ba5bcf`。严格深度验签、EventKit 链接、Full Access 用途说明、三类资源及相对链接通过。
- OctoSense 来源是标签 7f962547 的无 .git 归档，未冒称核验 Git HEAD。App Hub 基线 e8601b80 已核实，扩展 HEAD 29bfc0f。框架来源目录缺 Git 对象，setup.py provenance 检查不通过；locked 本机构建不能代替此检查。
- `/Applications/GOSIM-Local-Agent.app` 0.3.1 最终严格验签通过，主程序 SHA `9301e64773cfa01b0a3d2319a1ba3ca889be114365d5c6d1022364f53a829583` 未变。没有修改旧安装包、生产 SQLite 或旧账号资料。

## 修复与实测

### Goal / 模型 / 存储：PASS（受限本机场景）

最终候选创建 A/B/C 三个新 Goal，各自恰好一个 completed Run；真实模型建议、绑定批准、隔离结果写入及独立读取均通过。Activity 中 Goal created → model called → Plan approved → storage write → readback 顺序与归属一致。这里的 model called 是执行前的模型建议，不能把它说成审批后调用的另一动作。

| Goal | Run | 结果 SHA-256 |
| --- | --- | --- |
| 1790863616-2241484350 | run:1790863616-4263795425 | b6608ae39ad4c901cedd2f565b395811ece5262ba1ae8e7dde2cc794c5d1355f |
| 1790863616-3706832740 | run:1790863616-3570186963 | 34eefa18f3ed541398ce7649d2cfc00e1c04d27117b896ac5793e7deeeaf5d36 |
| 1790863616-3631495218 | run:1790863616-873425009 | 706893c7c879518c0fcc7d316f04d5fb184061705e64851874791e0c58a0d715 |

长文另建 Goal 1790864128-4185189050，在实际 990×300 Shell 输入 735 字/8条，滚动计划、批准、写入和读回成功；结果 SHA `c40c82462dd01e91e1b736d2178fb48442592900f3f2d42b249b4ff0b78249e1`。此长文用例没有调用模型，不能称长文模型验证通过。

历史异常未删：0.2.4 Goal 创建 Activity 同回调超时，后改下一回调；0.2.6 模型格式失败后同 Goal 重试成功，没有重复 Run；两个历史 planned Goal 仍保留在测试账本。不是所有测试创建的 Goal 都已完成。

### Chat：PARTIAL，语义稳定性 FAIL

使用现有 Qwen3-0.6B-Q8_0 真模型，native messages 传递原生角色历史。最终候选三个独立会话共九轮均取得真实 model.complete success；观察 relay 不改请求或回复，仅记录角色、hash及指定合成问题。历史回复 SHA 与请求匹配。

指定测试“记住验证码 → 追问原值 → 不重复、问数字位数”共 **2/3** 通过。首次答“四位数字”、第三次答“4位数字”；第二次错误答“验证码有 8427 位数字”，违反位数与不重复要求。全部结果保留，不能挑通过样本标稳定 PASS。没有硬编码答案或接入新 provider。

0.2.7 实机新/切换会话清除输入、旧消息不变、空/超限输入拒绝已验；0.2.3 LOCAL 备份与旧记录迁移测试、native history 21/21 单测仅按其证据范围列出。最终 0.2.8 重启持久化通过。0.2.4 provider 断连错误为真实失败证据，不当作成功。

### Calendar：PASS（本地扩展、合成事件 CRUD）

在本人已授权 Agent 处理测试权限的前提下，通过真实 macOS Full Access 按钮获得 full_access，未修改 TCC 数据库。系统返回四个日历，选择可写“工作”。最终候选 `MUSE-CALENDAR-TEST-20261001-028` 完成 create → 独立 get → update → 独立 get → delete → 独立 get；删除后 found=false，事件已清理。

三次动作使用不同 request_id，同一真实 event_id `76046D8C-D99D-41AA-923A-763237FBDC49:D868679F-5CA6-448B-8973-B8F91336DDC6`，每次有单独精确确认。写入后应用要求独立 get 的 ID/版本/标题/时间/时区/地点匹配才记 verified；删除后要求 get found=false 且无服务错误。独立审计核对了源码 guard、持久化收据及六张截图，没有冒称重新查询 EventKit。

首次自动驱动把底部仅露9px的“新建”按钮当可点击，未找到标题控件，在外部动作前停止。驱动改为 Button 至少24px可见后，同一测试重新执行三阶段全部成功，原失败日志和截图保留。0.2.6 实际冲突阻断与0.2.7测试编号修复保留为历史证据。

未做 final LIVE 拒绝/撤销许可、write_only 升权、超时未知结果、并发版本冲突或跨崩溃重放反例；UNIT/fixture 不替代这些。单独 CRUD 没有邮件 Goal 绑定，收据 goal_id/run_id 为空，不称同任务联动通过。

### Memory / Activity：PARTIAL

来源、账户范围、更正、固定、遗忘及墓碑有真实0.2.7操作和最终0.2.8持久化证明。账本3 claims、6 sources、2 tombstones，已删记忆未复活；六个来源 content_sha256 仍为 null，旧独立版完整 Memory DSL 和旧生产资料未迁入。Activity 为 Muse 的真实动作记录，不等于全电脑感知日志。

### 重启恢复：PASS

正常退出最终打包 .app，再经 Launch Services 打开 App Hub/Muse。23 个状态/结果文件哈希完全一致；Goal 21→21、Run 19→19、Action 15→15、Memory 3→3。Activity 179条前缀完整，仅新增一条 restart restore。没有重复模型/外部动作。独立审计再次逐项核对报告与磁盘。

### UI：PARTIAL，已修复 Dock 遮挡

中文八页均在最终候选实际打开并截图。左导航/中央内容/右侧能力与结果三栏可见；全屏结果页可进入及返回。输入框底部在高窗口增加动态留白，短窗不占88px空间。五种尺寸都实际点击发送得到真模型回复：990×539、990×400、990×300、1280×800，以及请求412×892被物理桌面夹紧后的412×818。不可把412×818截图称完整412×892验收；另外 LOCAL card-host 412×892可见。

990×300内容区98pt，仍依赖滚动；没有1px内容区。独立UI审计逐张查看五图，确认输入和按钮在Dock上方。仍有独立版技能/指南布局、部分结果层级/技术字段、模型预算只读和官方Mail Host英文面板的视觉差异。before为用户交付的真实历史参考截图，本实机修复轮未新开旧版逐页拍摄。

### Mail 与邮件→日历：BLOCKED

使用官方 Host Service，不复用旧版QQ桥、不读取旧凭据。尚无已授权真实邮箱；没有真实同步/正文/发信或收件端验证。官方Host登录面板可打开，密码只由本人在该面板输入。本人测试收件地址及最终发送确认尚缺。

Host mail.send accepted 只代表SMTP受理，不代表投递。Host 当前没有线程回复头接口，界面按新邮件声明。历史 mail_demo 仅 FIXTURE；邮件→候选日程→用户确认→系统日历→结果/记忆同一个 Goal、联动恢复仍未做 LIVE。

## Gate / Secret / 源码提交

扩展 `hub check bundle --allow-unsigned` PASS（开发警告）；签名0.2.8副本在注册本地真实公钥后 PASS。默认 unsigned 或未注册签名key被正常拒绝，未绕过准入。原版Gate仍拒calendar。scan生成7问，逐问人工自审 route=human-review：publisher/support/privacy占位、真实Mail未验、模型语义及本地扩展准入须人工处理；不是正式审查通过。

源码、宿主补丁、测试与纯源码导出已准备。GitHub origin 是既有仓库，未新建、未推送、未在主办方issue提交。导出不含运行状态、私钥、模型、旧安装包或生产数据。最终文本/文件名Secret模式检查与交付哈希记录另见 evidence index；不能把模式扫描说成正式安全审计。

## 下一步

1. 本人在官方Host登录测试邮箱，提供本人收件地址；真实发送前逐项确认。
2. 补真实Mail读取/编辑草稿/确认发送/收件核验，并完成同Goal邮件→日历→结果/来源记忆及重启去重。
3. 解决小模型语义不稳定、来源hash与剩余视觉/设置差异；不靠硬编码或假按钮。
4. 补真实发布信息，确认宿主扩展准入后，确定参赛源码版本再授权push与主办方issue评论。

证据：[索引](PHASE2_LIVE_EVIDENCE_INDEX.md)、[完整验收表](PHASE2_LIVE_ACCEPTANCE.md)。
