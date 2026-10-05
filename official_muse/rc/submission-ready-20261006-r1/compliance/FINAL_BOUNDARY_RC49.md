# rc49-r2 最终证据与官方边界

**状态：PARTIAL。** 最终检查对象为 rc49-r2；此前未安装、未公开的r1及其原版日志原样保留。r2只补渲染时局部捕获计划卡Goal ID/版本，不能混用r1测试或签名载荷身份。 本次分别对r1、最终r2签名Gate各执行一次原版Hub检查，独立记录可靠退出码；没有新增 fixture、模型调用、系统动作、签名或发布，没有操作运行中的8493。

## 最终 r2 版本与检查对象

- 最终 Gate：`gate-rc49-r2`，NO_PROFILE，本地候选 `0.3.26-rc49`；可读 SHA256 `2bad514d69d777fabb9ad2daf2b0aa2862555c2db5c146b22bc635b3b1e70484`，运行载荷 SHA256 `15ea7e6d2da21ce8bedbcb1e4cee1537217ee653a4f603539e51fc35cefc540f`。
- 检查前确认 r2 六文件与其mirror artifact字节相同、candidate载荷SHA相同。Gate元数据commit为 `89991aa905be2b2034c54c99465f672268ce500f`，是当时Git基线；不虚构为r2后续产品修复提交。98469官方token相等是Root既有构建记录，本次没有重跑token测试。
- 最终原版检查：[UPSTREAM_HUB_CHECK_RC49_R2.txt](UPSTREAM_HUB_CHECK_RC49_R2.txt)、[独立r2来源及退出码](UPSTREAM_HUB_CHECK_RC49_R2_PROVENANCE.json)。唯一列出的拒绝仍是calendar，直接进程返回码1。本次没有修改预算、能力、Host或原版CLI。原r1与r2各一次检查是两个不同签名载荷，不是失败后无限重试同一接口。
- [r2本地check](../gate-rc49-r2/check.txt) 和 [r2目录verify](../gate-rc49-r2/verify.txt) 保持本地扩展演练身份，不代表原版通过或正式提交。

## 已保留的 r1 版本与检查对象

- 工作区：`/Users/mima0000/.codex/worktrees/muse-rc-finalization/Agent APP黑客松`，分支 `codex/muse-rc-finalization`。
- 产品：`0.3.26-rc49`，源码修复提交 `52289f272176d1e56f04c57ef3cc611d9d45e516`。
- 可读源码 SHA256：`43ef05e424649bc663ec4c15e4b47906cbe54a35643a3228ff8bc137370d27a4`。
- 检查的签名入口 SHA256：`4fafe2a39336b8734c9e24afb58bb02df26af0de39276e69105ce2038670e468`。检查前逐个核对 Gate bundle 六文件与 mirror/artifacts/muse-goals-0.3.26-rc49.bundle 完全相同，无symlink；不把准备目录替代为签名产物。
- `gate-rc49-r1/candidate.json` 的 commit `20a58b2a...` 是生成 Gate 时的Git基线；产品修复随后提交为52289f27，产品身份以源码与运行载荷SHA及该修复提交区分，不虚构Gate元数据已重生成。
- 配套运行 Host 沿用 candidate 记录的 `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`；本次没有替换或运行Host。

## 计划卡回归（只读引用 Root 证据）

[PLAN_CARD_REGRESSION.json](../PLAN_CARD_REGRESSION.json) 与产品提交保留了同一套测试在修复前后的结果：

| 源码身份 | 结果 | 范围 |
|---|---|---|
| rc48 可读179fd6b6 | 4 PASS / 6 FAIL | 原空/手写输入条件下，执行、输入保持、来源保持、留在Chat、读回及重复拒绝失败 |
| rc49 可读43ef05e4 | 10 PASS / 0 FAIL | 同测试；真实隔离fs写入与读回，版本失效/跨聊天/重复拒绝，手写输入及来源保持 |

原首次 before-r1 相对Host路径启动失败也由Root保留，不计为执行通过。此回归用合成输入和生产函数，real_model/real_mail/real_calendar 均为false。测试Host SHA `52768f57...` 与配套Shell Host `1d7d1674...` 不同，不能混为同一实例验收。

修复仅取消计划卡确认时的异步 select_goal 路径，增加当前task/聊天绑定/planned版本守卫，暂时填入当前计划再调用已有approve，随后恢复手写输入和来源。没有修改approve本身、预算或Host；这段变更本次只读核对，未重新测试。

## 原版 Hub r1 一次实际检查（旧候选保留）

- 日志：[UPSTREAM_HUB_CHECK_RC49.txt](UPSTREAM_HUB_CHECK_RC49.txt)。
- 命令、时间、文件摘要、工具来源及直接进程返回值：[UPSTREAM_HUB_CHECK_RC49_PROVENANCE.json](UPSTREAM_HUB_CHECK_RC49_PROVENANCE.json)。
- 原版Hub二进制SHA `151e5319bb4058a0bc1ccec665be455a81dd35057a99c3ce18aa8be65e79421d`；执行前与已有 [UPSTREAM_BUILD_PROVENANCE.json](UPSTREAM_BUILD_PROVENANCE.json) 一致。它基于锁定上游 `e8601b80ce104db2e48208094714bdcffdce6b5a`，crate源码未改，独立审计workspace/Cargo.lock解析调整已有记录；不表示最新main CLI已执行。
- 此次直接 `subprocess.run(...).returncode` 为 **1**，记录不依赖最后一条shell打印的退出码。只运行一次，未重试。
- 文本结果 **REFUSED**，唯一列出的拒绝为 unknown capability `calendar`，没有列出digest/signature错误。公钥复用此前已验证的演练pubkey，不读取私钥，不产生新签名。

[gate-rc49-r1/check.txt](../gate-rc49-r1/check.txt) 中本地扩展 Hub 为 PASSED，grants storage/model/mail/calendar/glance、hosts空、agent none。其本地目录 catalog sequence81 /75entries核验和publish日志只是演练，不能称官方商店发布、独立reviewer或维护者准入。

## 实机与旧证据的边界

已只读核对 Root 提交的 [RC49_LIVE_PLAN_CARD.json](../RC49_LIVE_PLAN_CARD.json)：最终rc49-r2产品提交 `e0eb5d82bdfbcfa0a4375171ec6086e07c2ac166`，可读2bad514d、运行载荷15ea7e6d及Host1d7与最终Gate身份一致。真实Shell中Goal `1791222912-516469458` 的“确认执行这个计划”卡被点击一次，Run completed；同Goal活动记录包含批准、storage write、readback和memory saved。独立读取结果有两项，SHA256 `7b4b49b5a392ddab5a2d040137c4c29df7e4847b9e99dda208b62faddd3fa58b`，composer_preserved=true、errors=[]；该右卡执行与输入保持路径已有实机证据。本次只更新文档，没有重新执行或追加fixture。

同记录的真实模型候选响应 is_ok=true、known_usage=true、estimated=false、attempts=1，1204 input /410 output tokens；模型回执goal_id为空，仍属建Goal前候选，不写成批准后再次调用模型。actions=[]且scope明确没有新Mail/Calendar写入，**这不是最新rc49从头邮件—日历全链**。旧rc48重启、普通任务及跨聊天证据只作未改路径支持，保持原版本身份，见 [FINAL_BOUNDARY_RC48.md](FINAL_BOUNDARY_RC48.md) 及Root对应旧记录，不换成rc49重跑标签。

rc37/41/42/45外部邮件、EventKit及本人收件为跨版本历史链。rc46/47的54项fixture、rc48的10项启动恢复夹具和rc49的10项计划卡夹具分开记录，不汇总冒充同最终全链。

[OFFICIAL_REQUIREMENTS_AUDIT.md](OFFICIAL_REQUIREMENTS_AUDIT.md) 的规则/工具来源与本地扩展差异可复用；rc45包清单/签名/平台、rc48实机、旧scan与截图均不自动变成rc49完整审核。原版Calendar准入、最终单版本外部全链、接收机与完整产品/UI矩阵仍缺。保留旧失败，不宣告READY/UI_PARITY_PASS；本次只本地提交compliance证据，不改Root主文档或源码、不push。
