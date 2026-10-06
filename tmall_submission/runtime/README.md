# 配套 OctoSense Agent Runtime 与离线模型

发行 ZIP 的 **Muse.app** 内包含原签名 `OctoSense Host.app`、当前 Muse 签名目录/mirror、Qwen2.5-0.5B Instruct Q4_0 权重及 llama.cpp b11178 Intel CPU 组件。Git 只保留来源、许可定位、摘要锁、原生入口源码和构建/测试工具，不重复提交权重或 Host 二进制。

`RUN_MUSE.command` 与 Muse.app 使用同一个原生入口。入口校验整包签名；空配置自动启动仅绑定 127.0.0.1 的内置模型，并按既有官方 profile 格式配置 `model.complete` 路由。已有非内置 Provider 配置保持字节不变；已选内置模型时，只更新它的临时本机端口。退出 Host 后回收自己启动的推理进程，不触及其他服务。

首次使用 `--test-action launch-apphub`，按正常 App Hub 确认路径安装；以后使用已核对的 `--test-action launch-hub:muse-goals`。仍经过宿主目录准入、Storage 准备与权限检查；没有复制已安装资料或预授予账号权限来跳过检查。源码依据：Shell `run_test_actions` / `launch_app_with_args` / `installed_launch_id`，App Hub `installed_apps` / `install` / `open`。

基础离线模型可免 API Key 体验，但不能算第二强模型或保证复杂任务准确。模型完整权重 SHA、来源 revision、22 项运行组件和许可见 `MODEL_LOCK.json`；Host 与 mirror 见 `RUNTIME_LOCK.json`。本地推理组件只提供现有模型路由的计算端，不增加第二套 Agent Runtime 或 Provider 管理器。Calendar 仍是既有配套本地扩展，不宣称上游原版准入通过。
