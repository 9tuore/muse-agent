# 固定SDK请求包装（fixture parser）

依据实际 fixture-ca-sdk/crates/app-peers/src/guidance.rs:109–132，turn_input生成两个TEXT part：

```json
{"kind":"octosense_host_guidance","boundary":"...","instructions":"...","skills":[]}
{"kind":"octosense_request","text":"用户原始请求"}
```

固定Kernel prompt_text用换行拼接文本，label_prompt在前面加文档定义的 `[from the person: 标签]` 等origin标记；OpenAI纯文本路径发送该字符串。parser也支持OpenAI文本part数组，使用同一解包规则。

只接受最多一个可选guidance对象、一个request对象，request精确kind/text字段且text≤32768 UTF8 bytes；不扫描guidance中的示例。只解一层，不修复非法JSON、不接受嵌套request/额外app或scope字段。该SDK序列化包装本身没有app/account字段，scope由broker绑定，fixture parser不冒充授权或改变工具策略。工具仍须实际offered，错误结果仍停止。

本次具体wire全文未保存；包装归因来自现场SDK代码、实际UI合法ASCII引号及原生JSONDecode错误，属于源码推断。10个定向本地case通过，未发HTTP/GUI请求，无owner PASS。

Root部署planner.py后，仅在已完成回合、无SMTP时按已授权流程重启fixture输运，保留原protocol log，再由ZC05提交不同的新只读task；不重发旧请求。本批没有新instrumentation或服务重启。
