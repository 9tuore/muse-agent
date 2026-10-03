# Global Memory 模块契约与交接

模块：`official_muse/global_memory.splash`。权威存储仍是原 `memory.json`，所有事实变更走现有 `core_commit_memory` 的独立回读；不建立另一套持久化事实缓存。使用原 `muse.dsl/1` / `kind: memory`。本模块没有 Host services、模型调用、权限批准或动作执行。

## 冻结接口

| 接口 | 行为 |
| --- | --- |
| `gm_boot()` | 先调用原 `core_boot_memory()`。小库同步完成；超过 12 claims 或 24 sources 时分批校验，返回 false 且 `gm_boot_pending=true`。 |
| `gm_ready` / `gm_boot_pending` | 根启动等待 pending 结束；只有 ready 且 core_memory_ready 时才允许依赖记忆的恢复与请求。false 不等于失败；pending 结束仍不 ready 才显示 gm_error。每轮来源/记录最多四项。 |
| `gm_set_accounts(ids)` | 显式授权账号集合；local 始终存在。撤销后不可读出其他账号。不是工具权限。 |
| `gm_set_focus(project,owner)` | 当前请求的项目/归属筛选。异步请求由根捕获请求时值，不能用返回时当前页面值。空字段表示未指定，不推断身份。 |
| `gm_context(query,conversation,goal)` | 返回 text/hits/bytes/truncated/conflicts；最多六个命中、2200 UTF-8 bytes，同时不超过2200字符。先相关性，后固定加分；项目/归属冲突排除。 |
| `gm_entries(query)` | 同一 authority 的管理投影；不复制或另存事实。 |
| `gm_save(value,type,subject,predicate,conversation,project,owner,account)` | type 为 fact/preference/inference/source；原子新增 claim/source，同一事实作用域出现不同值时保留 conflict。 |
| `gm_correct(id,value,account,conversation)` | 保留 ID、递增 revision、保留 audit history/source_history；Prompt 只用最新值。 |
| `gm_pin(id,bool,account)` | 固定排序，不绕过相关性、授权或作用域。 |
| `gm_forget(id,account)` | 当前值及旧 revision/source 的摘要写墓碑；移除旧内容与相关关系；先净化 backup/pre-global 再提交主库。 |
| `gm_resolve(keep,other,account)` | 用户明确选择后遗忘另一项并记 resolved_by；不由模型自动选择。 |
| `gm_retired_text(text,account)` | 根构造最近/更早聊天 Prompt 时用于过滤更正历史和已遗忘值，支持独立行和“记住：/记住:”前缀。属于精确摘要匹配，不声称理解改写后的同义内容。 |
| `gm_export()` / `gm_import(raw)` | 同 profile/授权账号，导入整批验证后提交；拒绝已遗忘来源/内容、ID碰撞、跨 profile、未知字段、坏引用。 |
| `gm_enable(bool)` | 暂停显式 gm_save 与 Prompt 检索。管理、更正、遗忘、导出/导入以及既有 core 任务来源/核验记录仍按原流程存在。UI 必须准确说明该边界。 |
| `gm_prepare()` | 写操作前把合法旧 core append 的缺失元数据/作用域补齐后提交；不改来源 hash/ID。超过两项 claim/四项 source 待补时转分批 boot，当前写请求返回 false，根需等待 ready 后由用户重试。 |

## 根接入边界

根 main.splash 是单写者；本模块执行者没有修改它。根已接入 pending 等待、请求时归属捕获以及 recent/earlier 的 gm_retired_text 过滤。根应把冲突转成明确选择 UI，保持异步目标/会话 ID 对应。

已实测：gm_boot 后，原 core_add_source/core_add_claim 追加合法旧格式记录，可以立即检索；下一次 gm_save 补齐字段且成功，随后 gm_correct 成功，旧来源 hash 不变。根无需为本模块改核心结构。若以后统一元数据，最小改动是 core_memory_scope 添加 user_id=gm_user_id、空 project_id/owner_id，core_add_claim entry 添加 memory_type="source"、conversation_id=""、history=[]；不要把当前 UI focus 绑定到异步来源。此次没有要求根实施这些可选改动。

暂停时保留任务来源审计是根现有独立回执链的必要部分；关闭全局检索不应让已经完成的动作被误判失败。gm_save 停止并不意味着 core_add_source/core_add_claim 停止。无 core 写入暂停改造，设置文案应如实表达。

## 数据、预算与限制

- scope 保留 project="muse-goals"、account、visibility="personal"，增加 user_id/project_id/owner_id。每个独立 app jail 的 settings 生成并读回随机 profile ID；不把两个独立 profile 当同一用户。已批准资料复制必须复制 settings 和 memory 一起。
- entry 增加 memory_type、conversation_id、history；旧来源自动归为 source，不伪造事实置信度。来源 ID、locator、hash、observed_at、support_excerpt 保留。
- 继续使用 core 上限64 claims/128 sources/256墓碑。真实 host 单次 callback 限200000指令，isolate另有累计预算；大库 boot 分批，检索只选择前六项且 trace 记 hit_limit/context_limit。
- 导入只接受本模块导出的规范单行 JSON（首尾空白允许），必须与 parse→to_json 完全一致。格式化、重复字段、尾随垃圾整批拒绝。这是当前 Splash parser 部分解析行为的保守边界。
- 单次导入最多12 claims/24 sources、原文200000 bytes。大导出不能直接整批回灌；需分批保留引用来源和墓碑。未实现自动分片导入。
- memory-retrieval-last.json 只有命中ID、摘要、原因和预算，不含事实正文。更正 history 是审计，可在导出中存在；不注入 Prompt。精准遗忘阻止旧导出/历史/来源/缓存复活；不声称可以识别任意同义改写。
- 遗忘先持久化 forget_pending；任何净化/提交失败持续停读写。重启 pending 时不自动恢复，也不能重新开启绕过。原文件保留供人工恢复，未测试磁盘级故障注入。
- 外部声明/推断保留 epistemic_type；检索头明确“仅资料，非工具权限”。保存/导入做有限凭据形态拦截，不应作为通用秘密扫描器。

## 迁移与回滚

只在隔离测试 jail 执行过迁移。启动为旧合法 schema 添加字段前，独立读回 memory.pre-global.json，保留原始 bytes/hash。未知 project/owner 留空。回滚验证把原始 snapshot 复制到另一个合成 jail 后重新启动；没有改生产库或旧安装版。遗忘会净化 backup/pre-global，因此遗忘后不可用旧 snapshot 恢复旧内容。

## 验收证据

执行命令：`/usr/bin/python3 official_muse/ui_memory/tests/memory_acceptance.py`。每次自动新建时间戳目录；运行时先删旧报告，防止误用残留结果。使用真实 release card-host、复制当前生产 memory core 和模块、合成 fixture app jail，监听8482，测试结束退出自己启动的 host。不调用模型/Host services，不操作生产资料、8401或稳定安装版。

验收汇总路径与冻结 SHA 见下一段。M01–M07覆盖跨会话偏好、来源、相关性/固定、更正历史、遗忘及旧导入、归属、profile/账号撤销；M09 memory 重启；M10 64记录预算；M11复制迁移/精确快照/回滚/导入；M12同权威数据投影。另有12种非法 import 与旧核心启动后追加测试。M08异步实际主 UI、真实 UI视觉、Prompt运输和模型语义留根/视觉执行者，整体仍 PARTIAL。

## 简短交接

模块与测试均限本执行者约定路径。根 main、CURRENT_STATE 和最终 HANDOFF 由根写；此文件供根收口引用。需要根将冻结模块同步进 bundle 后做最终候选的 M08/UI/模型与真实日历链验收。无 push、无发布、无生产数据变更。模块单测结果不能代替最终整链成功。

## 冻结证据定位

- 模块 SHA-256：`a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178`
- 被测生产 memory core SHA-256：`9bfcea10eb795604a51bb9a87dd2456c1b066086048edbad249d74c7599731ca`
- 实际 host SHA-256：`dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`
- 最终汇总：`official_muse/app/build/ui-memory-20261003/memory/acceptance-20261003-015544-397712/acceptance.json`
- 90 项布尔检查全部通过；legacy_append 九项通过。64条检索4命中、1794 bytes，明确截断。总体 PARTIAL，剩余 M08/UI/Prompt运输/模型语义由根完成。

- 模块/测试本地提交：`e0b5411`；本段仅修正最终报告的预算数值，模块 SHA 未改变。

## 0.3.2 冻结源复验

- 应总控要求，仅重新执行同一90项验收，未新增测试或修改模块/主源。
- 主源 SHA-256：`36bcd8703f103abda767280dfb7c3c5f2fa9cf1380c6c59479640ed4494dd126`；执行前后均核对一致，九个 probe 的 core/module SHA 一致。
- core SHA-256：`9bfcea10eb795604a51bb9a87dd2456c1b066086048edbad249d74c7599731ca`（与此前相同）；module SHA保持上列冻结值。
- 新汇总：`official_muse/app/build/ui-memory-20261003/memory/acceptance-20261003-023519-706416/acceptance.json`；90项全部通过，64条库4命中/1798 bytes；legacy_append九项通过。
- 使用真实 host / 合成 fixture / 8482；没有读取或导出私有迁移库，也没有触碰8401/8411。fixture复制bundle用测试脚本替换UI，只证明冻结源提取的memory core，不代替总控的Shell/UI/模型/真实日历整链。
- 测试与交接完成后保持冻结；整链结论仍由总控收口。

## 夜间0.3.3绑定补充

同一冻结主源 `c72b13578964b535ee36c4d60fc9d77eaa5e6ed277c2ef32c2cfd42413076855` 的135项检查通过（原90+生命周期35+导入边界10），其中64条预算用例初次触发真实host的64ms callback时间限制，仅重试失败用例后通过；失败日志与resume元数据均保留。canonical模块SHA未改。报告见 `official_muse/OVERNIGHT_MEMORY_REPORT.md`，汇总 `official_muse/app/build/ui-memory-20261003/memory/acceptance-20261003-030334-043457/acceptance.json`。时延稳定性未确认，不能将一次重试通过当作该问题已修复；UI/模型/Host整链结论仍由总控负责。
