# UA-PREFLIGHT-003：已核验本地Goal在行动链仍只显示待核验计划

独立PRE_FLIGHT实际复现。同一纯本地storage单步Goal通过真实GUI生成计划、暂停、恢复、获取模型建议，再单次批准执行。任务详情和结果卡随后实际显示“成功”“结果已核验”“整理2条资料”；独立实际文件读回确认Goal completed、Run1及含两条原资料的结果产物。

在该事项中单次点击“行动链”，右栏仅显示一个“事项·当前计划 / 待核验”节点，没有该次执行或独立读回节点。左侧同一任务详情同时显示已核验结果，二者给普通用户的完成信息不一致。

独立原生证据：32-goal-glance-closed-native.png（完整成功结果卡）、33-goal-action-chain-native.png（成功详情与待核验行动链并列），均已通过view_image逐图查看。readback-10-goal-artifact.json记录实际Goal ID、项目/归属、completed、Run1、结果路径和产物SHA256；ui-actions.jsonl保存单次批准和单次tab切换。首次执行截图30处于running，随后仅作只读等待并在31/32图观察到成功，未重发批准或安全重试。

候选为sprint005-preflight-r5-single-host，实际0.4.0-rc7，PID49780/native786/Remote9799；不是正式冻结三轮候选。此票仅针对已独立核验的纯本地storage任务，不把外部Mail/Calendar completed视为verified，不推断根因，不参与生产修复。
