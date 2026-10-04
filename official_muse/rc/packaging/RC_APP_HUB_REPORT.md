# RC App Hub 材料状态

状态：**MATERIALS_PARTIAL**。这份报告不判断总控的 T01–T20。

## 已核验

- 本地 App Hub 官方基线 `e8601b80ce104db2e48208094714bdcffdce6b5a` 未升级；官方当前 main 公开快照 `e014fa9c596cdbd95de5cf9fb2a6b4fc2b781d17` 的 Publishing/Development 文档与 SHA 已保存。
- SDK 76 个 overlay 文件和 4 个声明链接符合锁内集合；新模型日志 delta 后，五个恢复 SDK 树与当前共享 lock 匹配，bootstrap 返回 `SDK_VERIFIED / 12000 files`。
- OctoSense 与 App Hub 的 `cargo metadata --no-deps --format-version 1 --locked --offline` 实际成功，两个 Cargo.lock 前后 SHA 相同。
- 当前 bundle 的体积、main/manifest/listing 与截图 SHA 有基线记录；Privacy 仍为占位 URL，既有截图未绑定本轮最终 RC。
- 只读查找 214 个 tracked 公开 Markdown/JSON，没有发现真实 Muse Privacy URL。官方 catalog 快照无 entries；未做签名验证，不能作为 publisher 已核准证据。

## 已准备的材料

| 材料 | 文件 | 完成边界 |
| --- | --- | --- |
| 官方发布契约 | `OFFICIAL_CONTRACT.md` | 文档核对；不是本机原版 Gate PASS |
| listing 推荐 | `LISTING_RECOMMENDATIONS.md` | 草稿；未改 canonical listing |
| 两张最终 RC 截图计划 | `SCREENSHOT_PLAN.md` | 拍摄顺序与绑定字段；未拍摄 |
| reviewer 回答 | `REVIEWER_ANSWERS_DRAFT.md` | 七个答题主题；最终 packet 原题待生成 |
| Privacy | `PRIVACY_DRAFT.md` | 待本人核定处理范围/保留/联系渠道及真实公开 URL |
| Submission Issue | `SUBMISSION_ISSUE_DRAFT.md` | 未提交，最终 commit/tag/SHA 待填 |
| 人工节点 | `HUMAN_CHECKPOINTS.md` | 交总控集中处理 |
| Intel 包复用 | `PORTABLE_REUSE.md` | 旧包结构可复用，旧证据不能转成 RC PASS |

## 准入边界

当前官方文档的闭合能力集合未列 `calendar`，本地 overlay 已扩展该能力。据此推断原版准入可能拒绝，但 A4 没有执行原版 Hub，不能写“官方拒绝”或“官方通过”。保留 Calendar 并明确扩展 Host/Hub 来源；本地扩展 check/scan 的结果要独立标记。

最终 Gate/scan 必须针对总控冻结后的真实 bundle，在截图/政策/身份/完整性字段定稿后执行。完整 packet 存在 bundle 外；已登记 publisher 更新须核对 continuity。签名后检查与最终公开 commit/tag 同字节。创建 Issue 不等于上架。

## 未完成

正式 Privacy URL、本人 publisher 身份及密钥连续性决策、至少两张同 RC 真截图、最终 scan packet、完整 signed 或确认首投 unsigned 的检查，以及最终提交许可。A4 没有发布、签 canonical manifest、生成 publisher 私钥或修改共享 listing。

Host 离线测试和构建另见 `STATUS.md` 与 `HOST_BUILD_RESULTS.json`；只有实际结果存在后才能引用。完整 app 与签后 Host SHA 在 `HOST_PACKAGE_RESULT.json`，它本身也不代表业务动作成功。

后续 storage SDK 的窄测试 4/4 PASS，构建前/后 bootstrap verify 都是 12000 files。新增 Intel Host/card-host 在 `STORAGE_HOST_PACKAGE_RESULT.json` / `STORAGE_CARD_PACKAGE_RESULT.json`，两个严格 ad hoc 验签成功，card-host CLI help exit=0。它们使用 fcec896f... SDK lock，Host 4942624e... / card efd7c856...；该 build/packaging 结果不能覆盖 owner r1 的 source-preparation budget FAIL 或直接提升启动/业务结论。总控随后应用4 KiB source-preparation patch并同步锁；新SDK三个pure测试、两份Intel app及构建前后12000文件verify已实际通过，绑定最新Host938ba58a... / card52768f57...，记录CHUNK_*。旧r1 FAIL保留，补丁proposal不冒充最终源码；业务及最终clean-room仍分别等待owner证据与最终生产commit。
