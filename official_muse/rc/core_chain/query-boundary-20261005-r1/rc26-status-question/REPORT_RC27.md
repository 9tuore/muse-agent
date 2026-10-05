# rc27 状态询问与 en-dash 最终窄域复核

状态：**FIXTURE_PASS_RC27**。时间：2026-10-05T18:40:56.401932+08:00。

## 本次真正新执行

只跑两个真实锁定CardHost窄fixture，synthetic Host模型回调，实际生产时间guard/候选生成→同ID修改→持久读回。**34条生产断言全PASS，另5条独立持久读回PASS**。

| 输入/对照 | 实测 |
|---|---|
| 完整en-dash `15:00–15:30` | clear/candidate guard通过；原准备输入确实创建candidate并同ID revision2改地点，保原起止时间 |
| 带空格 `15:00 – 15:30` | PASS |
| 原ASCII `-` / `~` / 到 / 至 / em-dash `—` | 5个完整格式PASS |
| `15:00–` 缺右钟 | 拒绝PASS，原rc26-r2两条失败现以同文本修复 |
| `–15:30` 缺左钟 | 拒绝PASS |
| 完全缺范围 | 拒绝PASS |
| `15:00 – 1` 右侧只有一位数字 | 拒绝PASS |
| `15:00 – 15:3` 右侧分钟不完整 | 拒绝PASS |

对于不完整用户输入，既调用input_clear也给合成完整model payload调用candidate_input_error，必须拒绝，即不能仅因模型补字段就通过检查。没有执行这些候选到系统。实际Calendar编辑是产品send_chat/candidate真实运行，模型响应是明确synthetic，不冒充GPT/真实日历。

独立读回候选：单候选、revision2、candidate状态、地点改合成B且start/end保持、最后assistant成功确认，各5检查通过。

## 原状态问题证据复用

原问题不变：只依据记录回答：日历工具报告创建失败，没有系统回执，也没有独立读回。现在能向用户说日程已经安排好吗？请解释。

rc25固定baseline误判calendar_candidate、解释后缀6输入共18断言FAIL保留；rc26-r1同probe实际3组52断言与10独立读回PASS，含原句/请解释/请简要说明/说明原因/解释原因/分析原因、明确起草/安排/整理、问号后请求创建负例、实际Mail/Calendar候选修改。

`BYTE_BINDING_RC27.json`：rc26-r1到当前rc27整源码仅 `chat_calendar_input_clear` 的新增完整en-dash分支和About版本不同；status helper与模型wrapper/权限/候选编辑等全部字节相同。r1 **52/10证据复用、未重复执行**。与本次34/5有Calendar语义重合，**不相加成总检查数**。这只证明路由/fixture，不证明真实模型已正确回答状态问题。

## 失败留痕

- `rc25-baseline-r1`：原status误路由及最初en-dash准备被guard拒绝；实际错误“请补充明确的开始和结束时间。”保留。
- `rc25-baseline-v2`：支持格式“到”的编辑对照PASS及status反例保留。
- `rc26-fixed-r1`：status修复3组PASS。
- `rc26-endash-r2`：只增加分隔字符后完整en-dash通过，但缺右钟仍input_clear true/候选guard空，**26PASS/2FAIL**，保留不覆盖，Root未安装该失败版本。
- `rc27-fixed-r1`：同不完整输入重新拒绝，原en-dash准备及新控制实测PASS。

没有把换setup当修复，不修改旧失败或期待答案。

## 版本与复现

- manifest：`0.3.26-rc27`。
- readable：`96ebb52f70a6cbf2050b14468e2eef2d8334e4cd5c4db18539e43c5bd67b4c05`。
- tested compact：`e5461fd7ecc1b32ee0e82019ac478b1f691d5137f18d2ac41a1d7e4f6ecd18af`，精确Root rc27冻结。
- actual fixture Host：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`，路径在summary；default已清理，使用明确仍可执行的自有锁定Host。

实际文件：`rc27-fixed-r1/<case>/first/report.json`、runtime.log、隔离state；`SOURCE_DIFF_RC27.patch`、`BYTE_BINDING_RC27.json`、`CANDIDATE_READBACK_RC27.json`、`PUBLIC_RESULT_RC27.json`。复现使用`run.py`配冻结source/SHA/Host、`probe-rc27.splash`，`--cases time_formats edit_calendar`，输出本目录新的子目录。

## 限制

这是有限时间格式/解释后缀回归，不是完整自然语言时间parser，也没有更改或检验所有legacy范围安全边界。未全套重跑101项/模型题集，未操作8493/8484/外发或真实系统日历；未改主文件、Host、权限、预算、Git/安装/生产资料。两个自启Host已退出。真实模型回答、最新Shell视觉与安装由Root验收，不宣告整体UI_PARITY/READY。
