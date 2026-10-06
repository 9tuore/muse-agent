# AI 实践

Muse 采用本地执行与云端模型协同的架构。云端模型经官方 `model.complete` 负责自然语言理解、事项提取、候选生成和回复草拟。本地 Muse 负责按授权检索长期记忆、关联原事项、保持任务状态；OctoSense Agent Runtime 负责权限、邮箱与 EventKit 日历宿主、执行和 Secret 隔离。

模型建议经过结构化校验、确定性规则与必要的用户确认，才可进入真实执行。系统结果需要独立读取核对；任务、确认与防重复记录用于重启恢复。模型没有邮箱授权码、API Key 或直接的系统权限。

MiniMax-M3 已有真实调用证据。本次包内置离线 Qwen2.5-0.5B Instruct 并自动接入同一官方 model.complete；基础体验无需 Key 或额外下载，不算第二个强模型。复杂任务可在官方模型设置切换更强 Provider，原有配置保持。

表单文本：[300 字版本](FORM_AI_PRACTICE_300.txt)。
