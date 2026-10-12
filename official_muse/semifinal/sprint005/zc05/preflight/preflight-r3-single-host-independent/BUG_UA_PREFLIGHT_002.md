# UA-PREFLIGHT-002：候选已准备的引导与右栏空行动链不一致

独立PRE_FLIGHT实际复现，候选并未丢失。默认右栏行动链选中时，新会话发送“整理S005-R1资料甲、资料乙，准备一次性任务计划”，真实模型输运返回Goal候选。聊天可见回复“候选已准备，请核对右侧内容”，但右栏仍是“当前会话尚未关联事项”，没有可见候选或指向候选的提示。

随后单次点击可见“来信与结果”才显示“本次任务计划”和“打开并核对”。普通新用户收到的当前位置指引与实际右栏内容不一致，增加了继续任务的发现成本。

独立原生证据：24-goal-candidate-chat-native.png（空链与候选提示同时可见）、25-goal-candidate-results-native.png（切tab后候选可见），均已通过view_image逐图查看。ui-actions.jsonl保存单次发送和单次tab点击；readback-07-goal-candidate.json独立核对Goal0/Run0，此时没有执行是正确行为。模型响应为合成fixture，不据此判断模型推理质量。

候选身份为sprint005-preflight-r5-single-host，Main/manifest实际版本0.4.0-rc7，窗口PID49780/native786/Remote9799。不是最终冻结三轮候选，正式243格未写入结果。本工单只记录可见性与引导不一致，不推断根因或参与生产代码修改。
