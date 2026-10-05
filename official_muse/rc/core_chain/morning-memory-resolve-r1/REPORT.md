# rc14 冲突记忆选择与显式遗忘：实际 CardHost fixture

**状态：FIXTURE_PASS_NO_REAL_MEMORY_UI_CLAIM。10组、186项检查通过；两次第二进程恢复后继续显式遗忘验证。**

这是隔离CardHost中的真实生产Memory函数与文件存储验证，不是GUI复测、真实模型推理或Mail/Calendar业务链。A2仅写本目录；Root独写产品、SDK、Git和共享矩阵。

## 身份

- rc13 readable：`53c8c0d9a0ebf2c1ec979b9e6c1a11100e6f190af94b978fe23486cb55ebe6ae`。
- rc13 compact：`754962b96f60fe2022f6f40923e478e2aa4d72f5e6a5304bc29d4bdc8007dc90`。
- rc14 readable：`2bc158c9073d8ba3dabadfb266c358273e9b274c8f147478835353402716eaae`。
- rc14 tested compact：`3a18504217c4c46313aebf12efbedba356246d4475640215d9bddfd238e67e95`。
- Root允许的CardHost：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`，位于本工作区`official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host`。
- 采用既有compact工具；本轮没有重新运行tokenizer，不把此Card当作新SDKda Shell Host。
- 完整readable去除gm_resolve及版本文字后，rc13与rc14逐字节相同。gm_forget/gm_correct/gm_access/gm_entry_access/gm_context/gm_forgotten_in分别逐函数完全同字节。

## 先复现真实失败

`rc13-baseline-r1/baseline_old/first/report.json`保留原失败。

实际步骤：gm_save旧内容→gm_correct生成一条非空历史及新来源→gm_save另一冲突内容→gm_context显示两项且requires_resolution→gm_resolve选择旧内容。

rc13调用本身返回成功、检索只见选中项，但另一项value/document/source_history被清空，来源原文清空，forget集合增加。内容保留等5项及新事件缺失共6项FAIL。旧输出为FAIL，未改标签或覆盖原存储/日志。

## rc14验收

| 组 | 首进程检查 | 第二进程检查 | 结果 |
|---|---:|---:|---|
| choose_old | 20 | 21 | PASS |
| choose_new | 20 | 21 | PASS |
| other_project | 13 | — | PASS |
| other_owner | 13 | — | PASS |
| other_account | 13 | — | PASS |
| same_id | 13 | — | PASS |
| missing_id | 13 | — | PASS |
| other_subject | 13 | — | PASS |
| other_predicate | 13 | — | PASS |
| other_user | 13 | — | PASS |

### 选择冲突内容

两项相同事实/项目/归属/account，检索先确实requires_resolution。分别选择旧/新，使用独立fixture与存储：

- gm_resolve成功，另一项resolved_by准确指向keep_id。
- 另一项document/value/deleted状态、history和source_history保持；全部sources逐字节不变，forget不增加。
- 只有选中项进入检索，冲突已解决；记录真实memory conflict resolved事件。
- 重复解决被拒绝，memory.json与activity.json字节不变。
- 独立读取memory.json与生产core_last_memory一致。

选择新内容的分支，其未选旧内容的history是**非空**；因此不是仅比较两个空数组来宣称历史保留。

### 作用域与身份守卫

不同project/owner/account/user、相同ID、不存在ID、不同subject或predicate均拒绝。拒绝前后的primary、backup、Activity、sources、forget全部保持字节一致。这验证冲突对必须位于同一事实作用域，**不表示当前焦点自动授予或撤销全局Memory读取权限**。

### 第二进程恢复与明确遗忘

选择旧与选择新两组均正常关闭第一个Card，再开第二个Card使用相同隔离state：

- 存储字节不变；resolved_by、另一值/history、全部sources、空forget准确恢复。
- 仍只检索选中项。
- 第二进程随后显式调用gm_forget(chosen)，不是在resolve阶段调用。
- chosen及resolved dependent都deleted/value空/source_ids空/source_history空/history空；所有关联source.support_excerpt清空。
- 原始旧值、旧修订值、另一冲突值均有墓碑；检索无结果。
- memory.json、memory.backup.json、memory-forget-candidate.json不含上述明文。
- 遗忘前真实gm_export再次gm_import被拒绝，主存储不变；分别重新保存旧/新文本均被墓碑拒绝，主存储不变。

fixture显式保存的baseline与遗忘前export只包含合成资料，用于验证防复活；它们是测试输入，不是生产Memory的备份或用户资料。

## 边界与证据

- 原日志、报告、source/compact/probe/manifest/state与第二进程bundle全部留存。
- 最终`rc14-r1/summary.json` SHA：`0dfc88413260272fcefbf9a1f1df29d42a4aaa55cfd45943fddcaf9a432f5ec3`。
- `PUBLIC_RESULT.json`列出逐文件路径、SHA、长度、原失败与函数差分结果。
- 既有regression_run只替换复制源码的Host transport/render/root widgets；Memory保存、更正、冲突、检索、遗忘、schema/存储函数真实执行。
- transport拒绝所有外部请求，实际请求数0；无Goal/Run/Action；默认64ms/20M/64MiB不变。
- 没有读取生产/private profile、凭据或真实联系人，也没有修改main、SDK、Git、共享矩阵或其他Agent输出。

本轮不标UI_PARITY/READY，不升级T17/T18。下一步由Root在实际rc14 Shell从原生Memory页面选择冲突项并复验可见状态。
