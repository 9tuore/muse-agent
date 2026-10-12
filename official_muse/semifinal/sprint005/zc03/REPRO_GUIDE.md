# ZC03复现与接入指南

所有命令是本组件入口，不授予GUI所有权或新的权限。7小时窗口为北京时间2026-10-12 13:11:25–20:11:25；19:11:25停止高风险，20:11:25截止，不延期、不新申请权限、不自动push。

## 固定身份与资料

Root基线8da96cfdf582fc7e7e1e8a7eda4e902f75090f6a，Main caa99c57；R5 sealed Main ef58430f、manifest7b746fb0、配套Host1eb188、Kernel56761a。Root始终唯一接入Main/Bundle和正式包。source旧rc18是准备模板，prepare_bundle会stamp实际0.4.0-rc7，R5 UI已正确；根bundle90351cba/rc17是历史保底。不要对不同层直接比较字节或将旧包成绩改成新包成绩。

只读取本机明确的源码/签包/旧公开fixture证据。性能输入是此前由Main生产save API生成的64 Memory/128 Sources、空forget原字节文件，路径在自有build或已归档gpt03_night004_perf/evidence/candidate-caa99-r1/main-state/memory.json。与生产profile无关。数据SHA、VM SHA、函数/global SHA写入报告。

## Memory候选定向复验

Root先审`skip-unrelated.patch`。它仅改gm_validate_indexed_part，batch=2、20ms、完整验证/all/correction/未知范围行为和动作恢复保持。Root接入后需重新冻结混合候选SHA，不能复用此caa99/947c报告为新混合版本。

本worktree已有actual新VM，源码与此前driver逐字相同，SDKscript163源文件构建前后不变。原缓存被清理后小型离线构建27.58秒、独立target63MiB；它不是GUI/Host构建，无共享target写入。

```sh
python3 -B official_muse/semifinal/sprint005/zc03/verify_memory_evidence.py

# 全新out；baseline/candidate必须对应evidence/source-identity.json。
python3 -B official_muse/semifinal/sprint005/zc03/run_memory_probe.py \
  --baseline build/sprint005-zc03/baseline-main.splash \
  --candidate build/sprint005-zc03/skip-unrelated-main.splash \
  --fixture-memory official_muse/semifinal/gpt03_night004_perf/evidence/candidate-caa99-r1/main-state/memory.json \
  --vm build/sprint005-zc03/vm-target/debug/zc03-sprint005-vm \
  --out build/sprint005-zc03/memory-abba-r2
```

A/B/B/A四个独立进程，每进程96个实际batch2片段和22个边界/损坏结果；无writes、Host、模型、邮件、Calendar、Kernel或GUI调用。父时钟interval含RPC/调度，新VM无64ms时间预算，系统负载未隔离。不重复14组件指标，不把CLI结果称GUI提速。

如新检出缺VM，只重建本小型纯脚本crate，独立target、offline、无incremental；先核对实际SDK路径与完整source identity，生成新binary receipt，不冒充当前337cbba7。禁用本命令中的任何Host/Kernel/全Shell构建扩展。

```sh
CARGO_INCREMENTAL=0 CARGO_PROFILE_DEV_DEBUG=0 cargo build --offline \
  --manifest-path official_muse/semifinal/sprint005/zc03/vm/Cargo.toml \
  --target-dir build/sprint005-zc03/vm-target
```

## 旧R5启动与版本审计

`audit.py`仅离线读取20轮JSON/原生PNG SHA/mtime、明确source、候选readable/signed、旧根bundle，不触碰state/profile。Root或本worktree用显式路径调用，`--out`必须不存在。输出不是新runtime次数，也不重审原生像素。

```sh
python3 -B official_muse/semifinal/sprint005/zc03/audit.py \
  --startup /绝对中央目录/build/night-004/final20-caa99-r2 \
  --source /绝对中央目录/official_muse/app/source/main.splash \
  --candidate /绝对中央目录/build/night-004/rc7-integrated-candidate-r5/candidate \
  --legacy-bundle /绝对中央目录/bundle \
  --out build/sprint005-zc03/identity-audit-new.json
```

以上`/绝对中央目录`是需由执行者替换的显式占位符，不能直接执行。已执行的实路径/结果在evidence/r5-startup-and-identity.json。21.652s是旧大规模同R5入口完整ready，12.958s是打开后PNG间隔，不可作为函数耗时；122个20ms timer只解释名义等待2.44s，剩余归因未确认。

## 有界被动观测

`observe_owned.py`只读一个Root提供的owner PID与固定exe，实际SDK proc_pidpath核路径，ps读出生时间/CPU/RSS；不读argv、profiles、业务资料，不发HTTP/input、signal、不重启。最长3600秒、最多721行、期限到即停。只输出OBSERVED_NOT_FUNCTIONAL_SOAK，Owner退出/更换/无法核身份分别记录失败，不据此宣布长期业务稳定或无泄漏。

Root在明确窗口稳定且不会马上切换owner时可按已授权PID运行；这里没有启动该Host探针。参数不用旧26569/27091猜当前owner，SHA须核当前exe。

```sh
python3 -B official_muse/semifinal/sprint005/zc03/observe_owned.py \
  --pid 实际OWNER_PID --executable /绝对冻结Host路径 --sha256 完整实际SHA256 \
  --duration 1800 --interval 5 --deadline 2026-10-12T20:11:25+08:00 \
  --out build/sprint005-zc03/owned-observation-new.json
```

占位符需由Root填入，不是已执行命令。实际工具测试只观测本测试Python进程2秒，其他为fixture错误分类；不能标成Host soak。首次测试揭示ps comm截断路径，改用SDK libproc定义后通过；失败事实与后续日志保留。

## 入口一致性最小修复

`root-entry-doc.patch`仅建议Root更新README开头：把本机未跟踪的R5配套App与历史rc17根bundle区分，写清SIMULATION_PASS/REAL_E2E_NOT_TESTED。不覆盖任一包，不自动重新签名或发布。源码旧label草稿已拒绝，因为它重复现有stamp且可能破坏将来版本替换；evidence/rejected-source-label.patch仅为拒绝记录，不可批量apply。

如Root之后选择把新候选变成真实根发布bundle，需在独立输出准备/签名/准入、记录source→stamped→signed provenance，再由Root按已有授权替换并保留旧包。此步骤未执行，GUI与业务验收不得从R5继承。

## 长期扫描风险与演示

只读发现chat_requests在进程内push，finished/cancelled未回收，chat_request_index在每次redraw扫描；重启会重置，尚无真实长会话压力结果。不要简单删除finished项：模型回调在标finished后继续使用request_index，chat_apply_payload依赖binding，需模型负责人核生命周期/软yield与晚回调。保留运行中及仍被实际候选/动作引用的绑定才可讨论有界退休。

75秒脚本见DEMO_75S.md，配套Host/fixture/人工前置准确。当前SCRIPT_READY/NOT_RECORDED；新黑绘制比较与有界surface建议见DIAGNOSTIC_PLAN.md，Root当前要求不改GPU源码，保持ROOT_CAUSE_NOT_ESTABLISHED。
