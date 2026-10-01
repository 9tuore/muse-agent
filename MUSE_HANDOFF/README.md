# Muse 一分钟接手

这是 Muse/GOSIM 项目的统一交接文件夹。**不必读完整聊天，也不必等用户填写任务。**先看 [CURRENT_STATE.md](CURRENT_STATE.md) 的实际通过项、阻塞与下一优先级；需要分层关系时看 [ARCHITECTURE.md](ARCHITECTURE.md)，产品方向看 [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md)。根目录 `AGENTS.md` 链接到本文件夹的 [开发规则](AGENTS.md)。

截至 2026-09-29 的调查基线：仓库 `main`，代码基线 `dbd08ed`，交接包首次提交 `c068fb6`；macOS 应用版本 `0.3.1`。本机原生 App、Qwen、QQ 邮箱和受限长期 Goal 有真实本机路径；高阶模型实调、Calendar 完整读写、robrix2 与官方同任务全链不可宣称完成。当前安装应用在前次文档验证后已恢复有效签名；运行状态和 HEAD 每次都要现场重查。

**直接开工方式：**没有新的具体目标时，选 [CURRENT_STATE.md](CURRENT_STATE.md)“Next Priorities”里影响最大的非核心问题。建议先解决测试子进程在签名 `.app` 内写 `.pyc` 的问题。非核心代码、UI、连接器、插件、测试、构建和文档可按需要修改，无需先取得文件清单；明确的[核心保护区](AGENTS.md)需用户授权才改。普通开发要跑相关测试、从成品复核并回读结果；不能把模拟或窗口出现写成端到端成功。

完成后更新 `CURRENT_STATE.md`、用 [交接模板](HANDOFF_TEMPLATE.md) 记录结果并本地 Git commit。不自动 push、不动生产数据、不擅自付费或向真实联系人发测试消息。[TASK.md](TASK.md) 是可选的自主工作入口，不是开工门槛；[MODEL_TASK_GUIDE.md](MODEL_TASK_GUIDE.md) 有可直接转发的新模型启动词。
