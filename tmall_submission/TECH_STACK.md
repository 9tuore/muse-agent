# 实际技术栈

- **OctoSense Agent Runtime**：固定源码 pin，加已有本地扩展；不增加第二套 Runtime。
- **OctoScript / Splash**：实际 App Hub bundle 为 `official_muse/app/bundle/main.splash`。
- **Makepad**：原生渲染，保持当前 UI，不迁移 Web / Electron / Tauri。
- **model.complete**：官方宿主模型代理；当前真实主模型 **MiniMax-M3**。配置的 OpenAI 路由此前返回 HTML，尚无第二强模型通过证据。
- **Mail Host Service**：账号授权、收件同步与确认发送，凭据只在宿主。
- **EventKit Calendar Extension**：目标日历查询、创建、同事件改期、删除与独立读回；配套本地扩展。
- **Local Memory DSL / 官方 Storage**：相关检索、来源、归属、更正、遗忘与跨聊天使用。
- **macOS**：本次现成 Runtime 是 Intel x86_64，完整日历授权路径要求 macOS 14+。
- **Qwen2.5-0.5B Instruct Q4_0 / llama.cpp b11178**：本次发行包内置权重、Intel CPU 推理组件与许可，首次自动配置到官方 model.complete；基础离线模型，复杂语义仍有限，不算强模型。

依赖与源码 pin 见 [SOURCE_MANIFEST.md](source/SOURCE_MANIFEST.md)。
