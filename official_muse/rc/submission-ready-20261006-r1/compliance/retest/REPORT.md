# 候选卡与Calendar旧测试异步维护

状态：NARROW_FIXTURE_RETEST_PASS。只改两个授权Splash测试；产品代码、Host、预算、fixture transport及其返回值均未改。没有操作Root端口，没有实际模型、邮箱、EventKit或付费调用。

## 先复现旧问题

rc46：02d6de50，source SHA `be0bb977a752e22d5115bbacae8d75231843cf750f2d86b5628ff8dd52ab35a6`。

- 原chat_proposal：ERROR/no probe report，日志明确array index 0 out of bounds(len=0)。send_chat后立即取fixture_queue[0]，模型派发尚在真实分段回调中。
- 原calendar_suite：5 PASS，unchanged、duplicate、added_conflict、removed_conflict_new_approval四FAIL。fixture_seed的2026-10-04时间已过期；confirm已分段但原脚本在同回调立即判断写入；原冲突事件缺calendar_id会触发范围拒绝，不能冒充检测到冲突。
- 原Root失败`routing-regression-r2`未删除。此目录额外保留rc46独立复现的原套件、源摘要与日志。

## 最小测试改动

1. regression_proposal等待模型请求实际入队，100次×0.05秒有界轮询，超时明确FAIL，不直接读取空数组。
2. 两套用测试时北京时间明天15–16点。候选卡的自然语言仍为“明天15点到16点”，输出日期与相对请求一致；不冻结/伪改系统时钟。
3. calendar_suite等真实pending拒绝或mutation dispatch，再检查原断言；现有transport只计数dispatch不回答，测试没有制造成功Host响应。
4. 合成冲突事件添加`calendar_id: fixture-calendar`，与实际查询范围一致。
5. 原18个候选/存储断言和9个批准/失效/防重复断言保留。数组长度检查只避免崩溃，不放宽绑定/动作限制。
6. 初次修补使用变量对象`+=`使probe输出NaN；runner按“报告不是对象”拒绝。失败原件保留，改成已验证的逐字段复制后通过；没有放宽runner。

## 最终结果

| source | 候选卡 | Calendar | 合计 |
|---|---:|---:|---:|
| rc46 / be0bb977 | 18/18 | 9/9 | 27/27 |
| rc47 / b3ab9327 | 18/18 | 9/9 | 27/27 |

rc47来源617851a8，source SHA `b3ab93278647cd51377cc1b02eab8b2f6f5c7e0d0c3aa6f4a8293e683900780d`。使用指定现有CardHost，其SHA在BASELINE.json。每次新隔离资料目录，端口8513/8514；runner关闭自己启动的进程，结束两端口均FREE。原始报告与日志见SUMMARY.json。

## 复跑

设置MUSE_CARD_HOST为已验证兼容CardHost的绝对路径，调用现有`official_muse/ui_memory/tests/regression_run.py`，指定实际候选源码、全新输出目录、未占用端口，分别`--suites chat_proposal`和`--suites calendar_suite`。不复用本轮旧输出路径，不默认使用开发机旧绝对Host路径。

边界：这是生产Splash函数+合成Host transport+真实隔离fs的逻辑回归；hidden窗口不构成视觉验收，synthetic dispatch不等于系统动作完成，队列模型响应不是实际model.complete提供商调用。不能用54条fixture PASS宣称整项产品full-chain或UI_PARITY通过。
