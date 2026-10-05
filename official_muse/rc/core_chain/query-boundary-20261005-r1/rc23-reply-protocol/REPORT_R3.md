# rc23 最终混合意图及输出协议窄域复核

状态：**FIXTURE_PASS**。时间：2026-10-05T16:57:46.435043+08:00。

本报告接替`REPORT.md`中的修复前状态。原“起草邮件＋资料整理”的测试是有效常用需求：后段整理把已选Mail覆盖成Goal，首次FAIL真实保留，不能仅换成简单输入算修好。Root已在Goal路由新增`action == ""`守卫；A2没有编辑产品。

## 修复后真正复测

真实锁定CardHost执行原生产schema路由、wrapper/context/history与隔离fs，合成Host捕获请求，无真实模型推理或邮件/日历外部动作。

| 原/补充输入 | schema路由 | 实测 |
|---|---|---|
| **原输入未换**：项目ORBIT，起草邮件给self@example.invalid，说明已完成资料整理。 | mail_compose：to/subject/body | PASS |
| 项目ORBIT，准备日历2030-06-12 15:00–15:30，事项为资料整理。 | calendar_candidate：title/start/end/time_zone/location | PASS |
| 项目ORBIT，整理资料，资料为第一条与第二条。 | goal_plan：objective/source | PASS |

**新3组 / 48条生产断言全部PASS**。三条action请求均没有附加reply协议，原query全文/授权记忆/历史保留；schema/class/task参考时钟保持预期；原args未改，focus恢复；外归属合成记忆被排除；没有Run/Action或外部服务调用。

从实际`captured-payload.json`独立读取，三组各验证精确request键、schema字段、required字段、无reply协议，另 **12条PASS**。

## 既有协议与保护证据

最终版本：`0.3.26-rc23`。

- readable `b2eff1a10be77fd6d9a27fa991f6e325730f89901aac1d8f031c21ff3394eb29`
- tested compact `2f5cbba308238839e9e45ba57befe233befc92e265ef8ee0869197009bf1ee9f`，与Root当前bundle字节一致。
- actual fixture Host `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。

`SOURCE_DIFF_R3.patch`/`BYTE_BINDING_R3.json`证明与此前rc23精确只有Goal branch一处`action==""`守卫变化，wrapper、原4格式分类回调、授权、UI与其他业务逻辑全部字节相同。普通reply（16条）、current/source guard（20条）从首轮PASS复用，**不重复声称新执行**；加新3组48条，有效6组84条生产断言。普通reply末尾协议及授权范围沿用字节绑定证据。不是全套重跑101条、也不是真实模型回归。

知识/keep语义及Mail→Calendar既有优先级从该唯一diff核对未改；本次只实测表中三条请求，不宣称所有自然语言分类完全正确。

## 保留证据与交接

首次混合Mail FAIL在`rc23-first-r1/mail/first/report.json`，其余首轮PASS也保留。中间明确邮件补测`rc23-mail-r2`保留但没有替代最终原输入回归。修复后`rc23-mixed-r3`实际3组，原输入的`intent_correct`现为true且其余断言通过。

- 当前最终报告：`REPORT_R3.md`
- 当前机器摘要/证据组合：`PUBLIC_RESULT_R3.json`、`REVIEW_RESULT_R3.json`
- 原始3组：`rc23-mixed-r3/<case>/first/report.json`、runtime.log、隔离state/payload。
- 原/新diff：`SOURCE_DIFF_R3.patch`，`BYTE_BINDING_R3.json`。
- 独立读回：`PAYLOAD_READBACK_R3.json`。

没有真实GPT回答正确性、外发、视觉、安装或全局READY结论。Root负责新变式实调。3个自己启动的Host已退出；未改主源码、Host、权限/预算、用户资料/凭据、安装、Git或共享文档。停止在本次授权边界。
