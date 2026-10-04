## 当前覆盖说明（2026-10-04）

用户最新门槛为至少18/20，逐项标准和未测状态保留；允许有限相关真实模型调用，旧S03 UNKNOWN账保留。正式政策/身份/准入与最终摘要确认未豁免。以下早期检查表的20/20及暂停收费表述仅为历史。当前仍PARTIAL。

# App Hub 提交草案（未提交）

状态：`DRAFT_ONLY / PRODUCT_PARTIAL / FINAL_CANDIDATE_PENDING`。本文件供总控和本人审阅，不能直接作为已完成的提交材料。整理时间：2026-10-04，北京时间；本轮T0为11:50:54。

12:22 Root续令：最终代码尚未冻结，保留既有0.3.19归档，不再生成大归档。最终导出接口与Root显式改动清单见[README](README.md)；最后一小时的人为缺项和工程门禁集中见[一次确认清单](LAST_HOUR_CONFIRMATION.md)。脚本的离线fixture/选择规则验证不提升产品验收，不代替新干净SDK构建。

## 当前事实与正式发布缺项

| 项目 | 已核对或待补 |
| --- | --- |
| 已公开开发源码 | https://github.com/9tuore/muse-agent/tree/4ff717d030aa52c22534dbbb9605eb31e4ac224b ，版本0.3.19；这是基线，不是本轮最终发布commit |
| bundle路径 | `official_muse/app/bundle/`；入口 `main.splash`，应用ID `muse-goals` |
| 最终版本 / commit / Tag | 待总控最终候选和本人确认；不创建成功Tag，不覆盖旧Tag |
| 发布者显示名 | 本人已决定：**星海队**；当前listing仍为模板，待总控应用最终变更 |
| Support | 本人已决定：https://github.com/9tuore/muse-agent/issues |
| 既有正式隐私政策 | **URL待本人提供或总控确认**。公开白名单181个小型文档/JSON/文本中仅找到example.com模板；没有找到政策文件名。未读取私人运行资料，未新造政策 |
| 公开开发身份 | 当前manifest `key_id=muse-local-rehearsal`；公开README列出的Ed25519公钥SHA256指纹为 `6e4865002119aa933c18939f3744201754d29a9983815169cdcc93e2e3ac23f5`。这不是已确认的正式发布身份 |
| 正式签名 / unsigned首投 | 待本人决定；未生成、寻找、读取或导出私钥，未签名 |
| 配套Host | Muse使用本地Calendar/EventKit Host和框架扩展；须随提交说明其来源、平台和构建路径。不能声称官方原版已接纳Calendar |
| agent | 现有manifest为null；不为提交凭空增加agent字段 |
| 能力与Gate | 当前基线声明storage/model/mail/calendar/glance；最终逐项grant及原版/扩展Gate输出待总控复核。当前calendar含本地扩展边界 |
| 原20项 | 基线5 PASS / 11 PARTIAL / 3 BLOCKED / 1 FAIL；T17第二模型仍BLOCKED，最后完整冷启动未通过64ms预算。后续仅按新证据更新 |
| 最终截图与录屏 | 待最终稳定候选完成后由总控采集；本草案没有把旧图、合成图或独立节点录像当作本轮最终证据 |
| 最终扫描 / 审核答案 | 待最终bundle的真实scan；生成packet不等于独立审核通过 |
| 公开发布 | 没有提交Issue、发布catalog、上传包或推送；正式动作由总控在本人最终确认后执行 |

## 正式Issue待填内容

拟标题：`Submit muse-goals <FINAL_VERSION>`。

- Repository：`https://github.com/9tuore/muse-agent`
- Final tag：`PENDING`
- Final full commit SHA：`PENDING`
- Bundle path：`official_muse/app/bundle/`
- Publisher identity / public key，或本人明确选择的首投unsigned：`PENDING`
- Exact final bundle digest、完整 `hub check` 输出与实际grants：`PENDING`
- Final `hub scan` questions及逐题答案：`PENDING`
- Final真实截图 / 录屏 / 输入与动作结果证据：`PENDING`
- 配套Calendar Host源码锁定、macOS依赖、构建命令、本地扩展与官方原版差异：参考上述固定开发源码的 `README.md`、`SOURCE_DELIVERY.md`、`THIRD_PARTY_NOTICES.md`，最终更新待总控。

## 已观察的扫描问题，供最终复核

读取的是本机0.3.19 `three-hour-ui-dev9-resize/review-packet.json`，实际有7题。下列是中文核对提示，不是外部审查结论；最终packet变化时应以新题目为准。

| 核对点 | 当前可诚实填写的边界 |
| --- | --- |
| 产品声明是否成立 | 总体PARTIAL，最后完整冷启动失败；不能勾选完整通过 |
| 平台和类别是否吻合 | 只声明已测试的macOS；productivity；最终候选待复核 |
| 能力和访问Host是否必要 | 明确storage/model/mail/glance与本地Calendar的用途；最终逐项grant、网络Host和可见功能对照待核验 |
| 是否仿冒系统界面或误导 | 当前未做最终独立视觉审核；不能用旧窗口出现替代核验 |
| 是否存在面向助手的隐藏指令 | 最终源码和数据待按实际scan核验，不臆造通过 |
| 是否有辱骂或针对私人个体的内容 | 最终源码与数据待核验 |
| 审核路径与理由 | 当前至少需要human-review：原20项未全过、隐私URL/身份/最终媒体未齐、本地Host扩展未被官方接受 |

## 官方依据与后续门禁

2026-10-04已读取官方当前文档；读取时间不是所用SDK版本升级证据。本机继续绑定原锁定SDK，未升级依赖或预算。

- [Publishing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/PUBLISHING.md)：bundle只放应用文本/资源；首次签名可选、已有登记身份须连续；现行通道是公开固定源码后提交Issue，由维护者审核发布。
- [交付路径](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/main/docs/DEVELOPMENT.md)：本地原生服务需要配套Shell源码/构建说明，不能打进Hub脚本bundle。
- [应用设计流](https://github.com/OctoSense-org/OctoScript-App-Design-Flow/blob/main/README.zh-CN.md)：应用开发和素材入口。
- [比赛提交说明](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/app-hub-submission.md)：完整源码、真实运行与平台/权限说明是可独立核对的材料。

满足本人原20项全部PASS、稳定最终候选、隐私政策、身份、媒体、精确字节的Gate/scan与本人最后明确确认后，才由总控推进正式Issue。签名后任何资源变化都需重新stamp、签名和check。提交Issue、维护者通过和catalog上架应分别记录；没有官方通过不能称已上架。
