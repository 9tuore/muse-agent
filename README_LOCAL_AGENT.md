# 本地常驻 Agent 第一版

当前实现由三层组成：

1. `runtime/models/Qwen3-0.6B-Q8_0.gguf`：Qwen3-0.6B 官方 GGUF 权重。
2. `runtime/llama-b11178/llama-server`：官方 `llama.cpp` Intel macOS 预编译运行时，提供仅本机监听的 OpenAI-compatible HTTP 接口。
3. `app/agent_app.py`：标准库 JSONL 常驻 Agent。它把消息送给本地模型做轻量路由，再进入任务卡、文件能力或需要确认的终端能力。

## 启动模型服务

在终端 A 保持服务运行：

```sh
./scripts/start_qwen_server.sh
```

服务只监听 `127.0.0.1:8080`。检查：

```sh
curl http://127.0.0.1:8080/health
```

## 运行 Agent

在终端 B 执行：

```sh
./scripts/run_qwen_agent_demo.sh
```

或者直接发送 JSONL 事件：

```sh
printf '%s\n' '{"type":"user_input","text":"请把会议记录保存到本地"}' '{"type":"confirm","approved":true}' \
  | LOCAL_MODEL_URL=http://127.0.0.1:8080/v1/chat/completions \
    python3 app/agent_app.py ./runtime/demo-workspace
```

## 官方边界对齐

官方资料里的链路是“意图结构化 → 宿主审核/授权 → 能力执行 → 结果回传”。本地 Agent 仍保留任务卡和显式确认；模型只能提出路由，不能跳过确认直接修改工作区或执行命令。`terminal_exec` 只执行当前工作区内的受限 argv，不启用任意外部 shell，不允许路径越界。

模型接口故障、输出格式错误或非法 route 会安全回退到规则路由。所有真实试验输出保存在 `evidence/`。

## 一步运行小程序

模型服务已经运行时，直接执行：

```sh
./scripts/run_mini_app.sh
```

这个入口会执行真实的 `health → 本地 Qwen 路由 → 用户确认 → 写入工作区 → 用户确认 → mkdir` 闭环，结果写到 `runtime/user-demo/`。

`app/octosense_appcard.json` 和 `app/octosense_appcard.py` 是接入 OctoSense AppCard 形状的本地 host adapter。它明确标记 `prototype=true`、`review=required`、`deferred_only`，不会把 Python 桥接层冒充官方冻结 schema。`app/official_event_adapter.py` 进一步校验 Robrix2/OctoSense 宿主 envelope 的 verified、recipient consent、房间 membership、事件白名单和 transaction，再送入同一条本地消息路由；适配结果固定标记 `prototype/deferred_only/NOT_LIVE`，当前不代表 live backend。

## 启动官方 OctoSense 桌面 AppCard

官方源代码与 sibling runtime 位于本机资料目录时，可以用：

```sh
./scripts/run_mini_app.sh --gui
```

这个命令最终执行官方入口 `cargo run --locked --features app-appcard -- --module appcard`，并把 Qwen 权重路径通过 `MAKEPAD_AI_CHAT_MODEL` 传入。当前 `cargo check --locked --features app-appcard` 已通过；桌面窗口是否显示取决于本机图形会话和官方 AppCard 内核配置。桥接层的 `terminal.exec` 只开放 `mkdir`、`touch`，固定工作区、无 shell、10 秒超时、8K 输出上限。

官方源码默认路径不是仓库的一部分；如路径不同，设置：

```sh
OCTOSENSE_OFFICIAL_ROOT=/path/to/work/official ./scripts/run_octosense_appcard.sh
```

已完成编译后，推荐使用后台启动入口，让桌面进程不依赖当前终端会话：

```sh
./scripts/start_octosense_appcard.sh
```

PID 保存在 `runtime/octosense.pid`，日志保存在 `runtime/octosense.log`。重复执行会复用仍在运行的进程。

如果从 Codex 或其他终端启动后窗口随会话消失，使用 macOS 应用入口：

```sh
./scripts/open_octosense_appcard.sh
```

它会生成 `runtime/OctoSense-AppCard.app` 并交给 macOS LaunchServices 打开，不依赖当前终端会话。

## 启动本地浏览器实测界面

浏览器界面提供一条更快、可重复的 `LocalAgent` 真实闭环入口。它连接本机 `llama-server` 的 Qwen3-0.6B，消息路由、文件写入和 `mkdir`/`touch` 均保留显式确认边界；官方 AppCard 桌面入口仍见上方命令。正式 `.app` 默认隐藏手动 synthetic 输入，直接走常驻事件入口；开发回归时设置 `GOSIM_DEV_UI=1` 才显示手动输入控件：

```bash
./scripts/open_local_app.sh
```

然后打开 <http://127.0.0.1:8766/>。点击“打开工作区”会在 macOS Finder 中打开固定工作区；如果端口已被占用，可以用 `LOCAL_APP_PORT=8767 ./scripts/open_local_app.sh` 启动，并访问对应端口。
