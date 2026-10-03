# 夜间全局记忆验收

当前结论：同一冻结0.3.3源的135项检查通过，其中64条预算用例初次触发真实64ms callback时间限制，仅重试该失败用例后通过。首次失败保留；整体PARTIAL，不宣称时延稳定或完整真实UI/模型/Host链通过。没有重新实现模块。canonical `global_memory.splash` SHA-256 保持 `a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178`。

## 本轮范围与证据边界

继续已有90例，只补真实缺口：固定排序跨重启、修订来源链/时间、越权修改不写入、非法时间/来源引用/JSON边界导入。全部运行真实 release card-host 的 Splash逻辑、复制生产memory core、隔离合成fixture app jail、端口8482；不调用模型或Host services。主main.splash仅总控修改，本执行者没有写它，也未读取私有profile副本。

“附件”用合成资料字符串及conversation来源模拟记忆输入，验证 storage→retrieve→context→correct→pin→forget→restart。未宣称验证真实文件附件解析、UI上传、邮件投递或日历动作。时间验证覆盖带时区时间戳、civil日期、修订时间/来源保留；valid_from/valid_until字段当前只校验格式，没有当前时刻有效期筛选，因此本报告不声称实现过期记忆自动隐藏。

## 覆盖核对

| 环节/隔离 | 已有90例 | 本轮补充 |
| --- | --- | --- |
| 存储/权威回读 | 原子claim+source、core独立回读、合法旧core append | 合成资料hash/摘要/locator/来源时间一致 |
| retrieve/context | 跨会话、相关性、64条预算、trace截断 | 更正后仅当前值入context |
| correct | revision/history、旧聊天过滤 | created_at保留、observed_at/updated_at对应、旧来源hash和revision source链 |
| pin | 固定调用、不能绕过项目相关性 | 返回成功、排序、跨重启恢复，不跨项目/归属 |
| forget/restart | 墓碑、backup/旧导入、profile、重启 | 先更正固定再重启遗忘，再重启检查旧/新两版防重新索引、来源摘要清空、另一条固定保留 |
| account/user | 跨账号/profile读取与撤销 | 越账号更正、越profile取消固定/遗忘拒绝且主库字节不变 |
| source | schema/来源碰撞/hash/缺失引用 | 来源project/owner不匹配、source_history缺失引用整批拒绝 |
| time/import | timestamp元数据与12种非法导入 | 缺timezone、非闰年2月29日、2月30日、24点时间、pinned类型、尾随JSON、重复字段拒绝 |

## 开发期补缺口结果

下列是开发期新增用例验证，不冒充最终0.3.3整批结果：

- `memory_lifecycle`：19/19 PASS。
- `memory_lifecycle_restart`：9/9 PASS。
- `memory_lifecycle_forgotten`：7/7 PASS。
- 扩展后的 `memory_suite`：58/58 PASS，其中新增10种导入边界断言。
- 生命周期报告：`official_muse/app/build/ui-memory-20261003/memory/overnight-lifecycle-development/memory_lifecycle-result.json`及同目录 restart/forgotten报告。
- 导入报告：`official_muse/app/build/ui-memory-20261003/memory/overnight-import-development/memory_suite-result.json`。
- 被测core SHA：`9bfcea10eb795604a51bb9a87dd2456c1b066086048edbad249d74c7599731ca`；实际host SHA：`dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`。

最终驱动实测135项（原90+生命周期35+非法导入10）。驱动新增每个probe的main_source_sha256，并强制全部probe的main/core/module/host SHA一致；源或runtime在验收过程中变化时不会输出成功汇总。

## 最终0.3.3绑定

- 主源SHA-256：`c72b13578964b535ee36c4d60fc9d77eaa5e6ed277c2ef32c2cfd42413076855`；执行前后核对一致，12个probe报告的main/core/module/host SHA均一致。
- 总控冻结产品提交：`8dc4752`；测试补缺口提交：`d46f459`。被测memory core及模块SHA与上列一致。
- 最终汇总：`official_muse/app/build/ui-memory-20261003/memory/acceptance-20261003-030334-043457/acceptance.json`。
- 实际135项布尔检查通过；本輪64条检索4命中/1798 bytes，hit/context预算通过并明确截断。
- 首次失败日志：`official_muse/app/build/ui-memory-20261003/memory/acceptance-20261003-030334-043457/budget/memory_budget-initial-time-limit-failure.log`；错误为 `script time budget exceeded`，发生在gm_context→gm_score→gm_access访问检查期间。真实host的64ms硬回调时间限制定义于 `widgets/src/widget_async.rs:457-460`；并非指令额度错误，也没有延长host预算。
- 初次整批在budget停止；此前九个成功probe没有重跑。只重试失败budget，再补未执行的migration/rollback两个probe，逐份核对SHA后合并实际结果。resume元数据与初次失败保存在汇总里，初次运行日志仍保留。
- canonical模块没有改；一次重试通过不能证明任意运行负载下均满足64ms，具体首次超时原因未确定。大库时延稳定性留总控后续收口；不把测试等待超时延长当作产品修复。
- UI/异步路由、Prompt运输、模型语义及真实Host整链由总控和对应执行者负责；本fixture结论仍PARTIAL。

## 简短交接与待办

模块没有变更，源SHAs冻结。所有测试文件在本执行者memory*路径；没有push，没有永久Memory写入，没有真实发信/日历写改删/账号修改/新授权/密码或付费测试。用户参与的审批与完整真实整链仅记待办，今晚不询问、不代操作。根负责最终CURRENT_STATE/HANDOFF及最终候选收口。

## 有限三次大库时延复测

按总控限定只运行已失败过的同一64条fixture三次，未重复135整套；每次独立host、相同jail数据副本、8482，完成三次即停止。仅诊断probe添加两次time_now读数，canonical模块和主源均未改。

| 尝试 | 结果 | context耗时 ms | host尝试总耗时 s | 触发64ms |
| --- | --- | --- | --- | --- |
| 原最终整批首次 | FAIL | 未记录 | 未记录 | 是；原日志保留 |
| 原失败用例重试 | PASS | 未记录 | 未记录 | 否 |
| 本轮独立1 | PASS | 14.731 | 3.533 | 否 |
| 本轮独立2 | PASS | 15.888 | 3.229 | 否 |
| 本轮独立3 | PASS | 10.412 | 3.516 | 否 |

- 本轮3/3 PASS，0次失败。没有再次触发时间预算，未改模块或降低宿主限制。
- context耗时为同一probe中gm_context前后native time_now差值；host总耗时为Python monotonic，包含启动/分批boot/报告/退出，不能与64ms callback直接比较。此前两次没有该测量，因此不事后补造elapsed。
- 三次复制输入memory SHA-256均为 `a8cdda5740e0e1e3f0ad9dc19ef269add4cbe4bb6fd5ef9a3ec13595e869a722`，settings SHA亦一致，64记录/同query不变。主源 `c72b13578964b535ee36c4d60fc9d77eaa5e6ed277c2ef32c2cfd42413076855`、canonical模块 `a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178` 均核对一致。
- 系统load average（1/5/15分钟）仅只读观察，三次开始值分别为 15.341/49.066/43.846；14.673/48.368/43.629；14.673/48.368/43.629；未人为增加/减少负载，不足以证明超时原因或所有负载稳定性。初次超时原因仍未证实。
- 新汇总与逐次日志：`official_muse/app/build/ui-memory-20261003/memory/budget-load-20261003-031432-886752/summary.json`；每次日志/实际结果路径均写入summary。此前首次失败及重试证据继续保留；总体PARTIAL边界不变。未接触8412真实模型进程，三次后已停止。

## 0.3.4 仅源绑定核对

- 冻结产品提交 `77fbf40`；main SHA-256 `d2c047154a810ac04bf1acd3993ba0ba92db3afe487854b859eb9361d2906d83`。本轮没有启动host或执行fixture，新增测试执行次数为0。
- embedded GM与canonical按现有sync_modules.py的 `rstrip()+换行` 规则完全一致；两者字节SHA均为 `a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178`。
- 使用memory_runtime.py相同切片和初始化前缀提取core，SHA `9bfcea10eb795604a51bb9a87dd2456c1b066086048edbad249d74c7599731ca`，与033被测core相同。实际card-host文件SHA `dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`，亦相同。
- 033原报告、首次超时日志、三次budget load结果与日志共9文件逐一核对SHA及长度，保持不变，未回写旧报告。135项检查和3/3 load通过继续标注为033证据；三次context为14.731/15.888/10.412ms，首次64ms超时原因仍未证实，不能声称所有负载稳定。
- 034只能复用相同core/module/host的模块级fixture结论；未重跑034整套，不证明034完整UI、model、Prompt运输或新Host链，root负责新实际模型/Host证据。
- 核对元数据：`official_muse/app/build/ui-memory-20261003/memory/source-bindings/034-module-binding.json`；033原证据基线保持不变。本执行者核对完成后停止。

## 0.3.5 最终静态绑定

- 冻结产品提交 `4135d0c`；main SHA-256 `0e4c26dcdc0760a12cc2bb545cea2eb42e4170fba86f14974edbb992339332f7`。本次仅静态核对，新增测试执行次数0，没有重跑135整套或三次负载。
- canonical与embedded GM字节SHA均保持 `a7e10973d6bd7b39ceedb805c04f4b77dbd754a3317a63b56bf228adad57d178`；同一测试提取规则下core SHA仍为 `9bfcea10eb795604a51bb9a87dd2456c1b066086048edbad249d74c7599731ca`。
- 原fixture card-host文件SHA仍为 `dcebb3e8a4c50b6702526b52d8aaa3a015e63feba8159b8aff9682cd9ea83987`。这仅核对原fixture host；新的真实Shell Host及实际模型链由root另行验收，不能把旧host fixture冒充新Host全链。
- 033的9份原证据逐一SHA/长度核对不变；033基线和034绑定JSON在本次核对前后字节完全相同，035另存新记录。135项与3/3负载仍标注为033证据，首次64ms超时原因仍未确定。
- 最终元数据：`official_muse/app/build/ui-memory-20261003/memory/source-bindings/035-module-binding.json`。034旧绑定不回写；035复用仅限相同core/module/原fixture-host的模块级结论，不证明035完整UI/model/Prompt或新Host链。
- 本执行者静态核对完成后冻结停止；root负责总报告和当前实际模型/新Host证据。
