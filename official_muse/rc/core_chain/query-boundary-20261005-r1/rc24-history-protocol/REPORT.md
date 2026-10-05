# rc24 普通回复历史 JSON 协议窄域独立复核

状态：**FIXTURE_PASS**。完成：2026-10-05T17:16:03.977500+08:00。

## 实际范围

实际锁定CardHost运行生产 `muse_model_request`、`chat_model_config`、`chat_model_history`、记忆检索与chat保存，Host transport合成捕获请求，隔离fs实际写入和独立读取。沿用既有fixture根widgets、redraw/set_page/calendar_enabled/mail_redraw替换；隐藏窗口不是视觉证据。**没有真实模型推理、邮件/日历外部动作。**

**6个窄场景 / 106条生产断言全部PASS**，另从实际payload和持久消息独立Python读回 **25条PASS**。这个106是本次六场景中的断言数，不是全套101项重跑。

| 场景 | 实测 |
|---|---|
| 普通reply，历史assistant数字文本`56`与引号、真实LF换行、反斜线、中文 | 只请求副本assistant content转换为单字段JSON reply字符串，parse_json回原文，PASS |
| Calendar＋资料整理 | 保calendar_candidate，历史assistant保持原裸文本，最后user不加reply协议，PASS |
| 原混合Mail＋已完成资料整理 | 保mail_compose，原历史和动作schema不改，PASS |
| 普通Goal资料整理 | 保goal_plan，原历史和动作schema不改，PASS |
| current=false | 0 Host请求、0model，PASS |
| source_account未授权 | cancelled、0model，PASS |

普通reply的两个assistant历史轮次被验证为精确`{reply: original_content}.to_json()`；user历史顺序和内容保持。独立读回再次证明JSON只有reply键且类型string，`56`没有变成JSON number；引号/实际字符10换行/单个反斜线/中文都与持久原文一致。三类action历史仍为原文本而非JSON包装。

所有六组原args、内存messages/chat_sessions、`chat-sessions.json`及backup字节保持不变。只是请求副本变换，原对话显示/存储未改。每组两条同主题合成Memory：当前项目归属资料正确纳入，外项目/归属资料排除；query完整保留，focus恢复；原schema/class/task参考时钟和payload字段保持预期。

## 来源与版本

- manifest：`0.3.26-rc24`
- readable：`0699524137cda658040a843b5af50b57f406d691f821701032c5279796ba5c98`
- tested compact：`4345edc8ce34eb4f98983537ad602c1f3be87c8b49d9eae6b37ba7ce7bc42b93`，与Root冻结 `improvement-20261005-r1/compact-rc24-r1` 精确匹配。
- actual Host：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`
- 运行时默认预算没改；本次生产源码仍由Root管理，A2没有Git写入。

`SOURCE_DIFF.patch` / `BYTE_BINDING.json`：相对rc23-r2，除wrapper请求历史格式与唯一About版本号外其余业务/UI源码字节相同。wrapper模型响应整个区域（四类格式分类、known_usage、存储、记忆有效性和callback）精确字节一致，复用原rc21诊断，未重新执行四类响应；rc23混合路由与rc20 101范围证据保留，无全套重跑。

## 可复现证据与限制

`rc24-first-r1/<case>/first/report.json`、runtime.log、隔离state中 `captured-payload.json`/`chat-sessions.json`：六个真实fixture运行。

- `rc24-first-r1/summary.json`：FIXTURE_PASS、106断言。
- `PAYLOAD_READBACK.json`：独立25检查。
- `PUBLIC_RESULT.json`：机器摘要。
- `probe.splash`、`run.py`：只跑六个窄场景；合成transport不回模型结果，不执行外部动作。

此次没有失败结果；既有rc23原失败证据未动。自己启动的6个Host均由runner退出。没有改产品、Host、Git、安装、预算、权限、账号/凭据或生产资料。没有 Secret采集或真实模型输出；不证明实际GPT/M3解决invalid_json，不宣告UI_PARITY/READY。Root负责真实原失败问题实调。
