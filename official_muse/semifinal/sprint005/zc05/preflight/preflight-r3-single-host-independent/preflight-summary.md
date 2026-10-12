# 单Host独立PRE_FLIGHT实际观察

结论：Muse正文实际可见；聊天、同范围新会话记忆检索、记忆更正/遗忘及纯本地Goal批准执行均有真实GUI与独立持久化读回。发现两处可见引导/结果投影问题，已即时给Root最小证据。正式三轮未开始，本批不写243格。

实际执行以ui-actions.jsonl和35张逐图view_image查看的原生PNG为准。所有输入用当前唯一控制、w、完整rect发一次；未自动重试业务点击。模型样本仅通过已授权model control配置，业务动作均由UI发起。

- Chat：P1/合成归属1表单保存，真实model输运回包；固定fixture回复不当作记忆答案。
- Memory：原话SHA与实际memory/source SHA一致；同范围新会话真实retrieval命中原ID/revision/source；更正同ID revision2/history1且新值SHA一致；取消遗忘保留，明确确认后deleted、value/history/source_refs清除检查成立。
- Goal：候选阶段Goal0/Run0，打开后planned；暂停/恢复、模型建议没有执行；单次批准后实际Goal completed/Run1，独立产物含两条原资料。初始截图running，随后仅只读等待再观察到原生成功/结果已核验，未重发。
- UA-PREFLIGHT-002：聊天称核对右侧内容但当前空行动链没有候选；切“来信与结果”才可见。
- UA-PREFLIGHT-003：已核验本地Goal在行动链仍仅“当前计划 / 待核验”，无执行/读回节点。
- Calendar：进入真实官方Calendar页并填写只读events查询，但Root要求切最终freeze前尚未提交，NOT_TESTED_NOT_SUBMITTED；没有session/turn/owner结论。
- Mail、跨项目P2隔离、重启恢复和Calendar写操作未执行。

/s实际PID49780/window0尺寸1400×805、px2800×1610、dpi2核对后，单次正常/quit返回ok1，随后9799无LISTEN PID；GUI已回交ZC-00。未访问9696、未直接写业务JSON/DB、未进行账号/生产授权。

独立工作树被另一清理聊天删除历史文件后，只恢复了本Agent已提交的helper/矩阵/文档；Root明确允许使用其现有remote.py作为UI依赖，未restore/stage其他被删文件。身份为0.4.0-rc7/R5单Host预检，最终固定候选需另测。
