# A4 · rc49 内置模型有界诊断

**PARTIAL。两题准确率仍为0/2；没有实施或宣称有效修复。**

错误已定位到模型生成内容：把真实Host捕获的两个完整token化提示直接交给同一runner，分别生成 `{"reply":"晴朗"}` 和 `{"reply":"7"}`。原始JSON与Host保存的文本一致，输入573/600 tokens和输出8/7 tokens也一致，`truncated=false`。这两次回放在Host/UI解析之前完成；现有解析没有把正确答案取错或截断。

实际模型是未变的Qwen3-0.6B纯Q4_K_S，SHA f755be04…ee71b；Host1d7、rc49产品e0eb5d82/compact15ea7e6d、上下文4096与预算政策未改。使用当前Desktop包的既有Host/runner，在自有8492和空凭据本地profile测试，没有代理或新增runtime，没有付费模型、邮件/系统日历写入。

## 同题对照与唯一配置尝试

| 检查 | 实际结果 | 边界 |
|---|---|---|
| 旧直连记录 | 两题关键词正确 | 问题省略了“只回答两个汉字/数字”，不能与Muse严格同题比较 |
| 本轮完整同题直连 | 天空题重复问题；算术回答“7加5等于12。” | 算术语义正确，但未满足只数字格式；不是Host调用 |
| rc49真实Host基线 | “晴朗”“7”，0/2；573/600输入与8/7输出；各attempts1 | 从自有已初始化rc48合成状态复制schema，并仅在复制fixture清空messages/proposals；不是正常fresh启动通过 |
| 唯一修复尝试 | temp0.7/top-p0.8/top-k20/min-p0/presence1.5，仍“晴朗”“7” | 官方非思考参数；实际runner日志确认生效。未采用到launcher/交付配置 |
| 两次原始提示回放 | JSON reply两项逐字匹配Host；tokens同上；无截断 | native `/completion`诊断，不伪称为model.complete或质量PASS |

[官方参数依据](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/blob/main/README.md)、[已安装runner版本的native API](https://github.com/ggml-org/llama.cpp/blob/f9af9be21/tools/server/README.md)。已核对本地官方Host源码：OpenAI读取完整message.content，解JSON后返回output.reply；当前空think前缀也来自正常模板。

可确认当前模型/量化与Muse较长任务、schema、历史上下文组合无法可靠完成这两题。未精确隔离量化损失和提示复杂度各自影响，因此不称“0.6B永远无法算7+5”。未找到可验证的route/响应字段/截断错误，无依据继续解析器或模板试错；只做1种修复尝试，停止。Root若要改善语义，需另决定产品任务约束或能力足够的模型，不能靠A4配置层假PASS。已有思考128和旧误答证据继续保留。

## 单独的空配置启动失败

fresh分支先保存只有id/title/time/messages的会话，再同步补字段。预算异常在gm_has；备份仍为最小形状，后续保存已补proposals/focus_project但缺focus_owner/goal_id。chat_ready已true，发送binding直接读focus_owner，因缺字段在model.complete之前失败。详见 [FRESH_PROFILE_CAUSE.json](FRESH_PROFILE_CAUSE.json)：包含仅自有合成资料、完整错误及e0eb5d82源码位置，精确预算耗尽触发/调用栈未记录，不能声称已修。Root主入口未改。

总共8次本地推理请求（4次真实model.complete、2次同题直连、2次native回放）。全部自有Host/runner退出；不触碰Root8493、主profile、Host/权重/预算，不push，不重包497MB ZIP。

数据：[MODEL_DIAGNOSIS.json](MODEL_DIAGNOSIS.json)；baseline/原失败、baseline-initialized/原始提示与调用、official-nonthinking/失败尝试、raw-replay/原始模型JSON均保留。回放PASS只表示证明文本匹配，不表示模型答对。
