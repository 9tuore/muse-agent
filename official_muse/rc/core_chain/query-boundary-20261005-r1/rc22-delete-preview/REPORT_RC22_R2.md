# rc22-r2 完整删除核对 ID 窄域独立复核

状态：**FIXTURE_PASS**。时间：2026-10-05T16:24:12.128237+08:00。

## 实测结果

真实锁定 CardHost，生产 `calendar_delete_id_matches` 与 `calendar_preview_action`，隔离真实存储，合成所选事件与 Host transport。**15组 / 105条断言全部通过**。

| 场景 | 实测 |
|---|---|
| 完整授权ID `MUSE-IMPROVE-20261005-1525` | PASS，预览绑定所选事件/calendar/version/request |
| 不同/过时同前缀完整ID | PASS，拒绝 |
| 所选事件标题不同 | PASS，拒绝 |
| 非测试ID即使标题相同 | PASS，拒绝 |
| nil所选事件 | PASS，拒绝 |
| 仅 `MUSE-IMPROVE-` | PASS，拒绝；原rc22 FAIL已保留 |
| 截短 `MUSE-IMPROVE-20261005-15` | PASS，拒绝；原rc22 FAIL已保留 |
| PHASE2 / CALENDAR-TEST / CALENDAR-FINAL / R2 旧合法ID | 4组PASS |
| 完整ID两侧空格 / 换行 | 2组PASS |
| 输入含 `.*` / `|` 正则元字符 | 2组PASS，拒绝 |

每组验证启动资料状态、helper结果、预览结果、错误状态、精确payload绑定、Host调用为零、Run/Action为零。没有调用 `calendar_confirm_action`，没有真实查询、发送、创建或删除。最终确认源码同样调用新helper已从完整diff核对；本报告不将源码核对升级为真实确认/删除成功。

## 版本与证据绑定

- manifest：`0.3.26-rc22`
- readable：`9638ac67799d9a7f2d7d315abb41e815f3119d8db34dd03b09642f0307feca44`
- tested compact：`0ecc8b49971624b94409c6c2a8da9f148dabf2b0c55cc718a779788256a58f11`，精确匹配 Root 冻结rc22-r2。
- actual Host：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`

`SOURCE_DIFF_RC22_R2.patch` 与 `BYTE_BINDING_RC22_R2.json` 证明相对首次rc22仅新增完整ID helper、预览和最终确认调用变化，其余业务源码/UI全部字节一致。移除helper时精确忽略它新增的两条分隔换行。首次byte比较因仅移除一条空行为false，保留在`BYTE_BINDING_RC22_R2_FIRST.json`，不属于运行失败。

首次rc22实际 **5组PASS / 2组FAIL，38条PASS / 4条FAIL**，证据和`REPORT_RC22.md`/`PUBLIC_RESULT_RC22.json`未覆盖。两个失败反例在新冻结源码实际复测并通过，未修改断言为放行。

此前rc21模型诊断与rc20 101条范围检查证据只复用，未重跑全套。旧确认、防重、批准、模型、存储函数除此最小门禁调用未修改；本报告不称这些链在rc22-r2重新实测。fixture渲染和Host transport沿用既有替换，不是新UI截图/真实Shell/真实Calendar测试。

## 文件

- `rc22-fixed-r2/<case>/first/report.json`、runtime.log、隔离state：实际15组。
- `rc22-fixed-r2/summary.json`：FIXTURE_PASS。
- `PUBLIC_RESULT_RC22_R2.json`：最终机器摘要。
- `SOURCE_DIFF_RC22_R2.patch`、`BYTE_BINDING_RC22_R2.json`：源码绑定。
- `probe-r2.splash`、`run.py`：窄域复现，不调用确认。

全部自己启动的15个Host已退出；没有改main、Host、预算、安装、共享文档、Git；没有读取用户账号、凭据或生产资料。没有全局UI_PARITY/READY结论。由Root集成、提交、安装及执行真实验收。
