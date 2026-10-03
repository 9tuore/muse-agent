# 把 Muse 交给新 AI

任何具备本机仓库访问能力的模型都可从 [README.md](README.md) 开始。默认无需你填写目标、文件清单或重复解释项目；它应在非核心范围自主选择下一项。更强模型适合核心设计或官方链路的分析；其他模型可以直接做 UI、连接器、插件、日历、浏览器、打包、测试和安装。无论模型名称，都以当前代码与真实测试为准。

## 可直接发送的启动提示词

```text
接续当前 Muse/GOSIM 项目。仓库根目录有 AGENTS.md，交接资料集中在 MUSE_HANDOFF/。
先读 MUSE_HANDOFF/README.md 和 MUSE_HANDOFF/CURRENT_STATE.md，核对 branch、HEAD、git status；只在需要时读 MUSE_HANDOFF/ARCHITECTURE.md 与目标代码。
无需等我分配 TASK 或允许文件。若我没有另给具体目标，请从 MUSE_HANDOFF/CURRENT_STATE.md 的优先级中自行选择一个最值得做的非核心问题，直接修复、实测、更新状态并本地提交。
核心保护清单见 AGENTS.md；未经我明确要求不要改核心或生产数据。不擅自付费、提权、公开或给真实联系人发测试消息。fixture、编译和界面存在不能冒充 live 完成。
最终简要告诉我改了什么、怎样验证、哪些仍没完成、提交号。
```
