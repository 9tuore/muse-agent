# 7H 业务隔离验证

本目录只负责隔离测试。真实邮箱外发、系统日历写入、白名单和 20 封计数由总控负责。

## 实际验证边界

`run.py` 对输入 bundle 做不可变快照，以实际官方 `card-host` 执行完整生产函数。
仅替换 Host transport、最小控件及 UI/授权显示入口；每次输出生产函数保留审计、源码与运行二进制 SHA。
使用真实 VM、异步 timer、应用沙箱 fs 和写后读回，不改脚本执行预算。
`--fault-storage` 额外在指定单一路径的写入前返回 I/O 失败，其他 fs 仍实际执行。

Mail、Model、Calendar 的服务回复在本目录全部为合成数据。收件端副本也是隔离 transport 的独立数据读取。
这些结果最高只能称 `DRY_RUN_PASS`，不能代替 SMTP/IMAP、模型推理、EventKit、正常全界面或真实授权验收。

## 入口

提供总控固定后的 bundle 和实际已构建 Host 路径，勿用已删除的历史绝对路径。

```sh
python3 official_muse/rc/7h-20261008/business/run.py \
  --source-bundle <candidate-bundle> --host <reference-card-host> \
  --host-cwd <host-resource-workspace> \
  --probe official_muse/rc/7h-20261008/business/chain.splash \
  --out official_muse/rc/7h-20261008/business/.local-state/chain-r1
```

第二个进程用 `restart.splash` 和 `--seed <chain-r1/state>`，核对状态恢复与新空白对话相关记忆检索。
每个失败用新目录运行；保存日志、阶段、状态和 summary，不覆盖旧样本。

## 故障矩阵

| Probe / case | 要验证的行为 |
|---|---|
| `chain.splash` | 首封来信来源、范围记忆、候选、确认、创建与 get、第二封关联、同 ID 改期、回复确认、合成收件读取、来源记忆 |
| `restart.splash` | 新进程恢复，旧批准不能重放，新空白对话召回同范围事实，不向老师/其他项目泄漏 |
| `failure.splash / ambiguous_matter` | 多个原事项匹配时不猜测 |
| `failure.splash / external_version` | 批准期间原事件外部版本变化，不执行旧更新 |
| `failure.splash / revoked_approval` | 预检查期间撤销批准，不执行旧更新 |
| `failure.splash / malformed_model` | 格式错误分类回复不产生候选或外部动作 |
| `failure.splash / late_model` | 目标取消后迟到模型不能复活目标 |
| `failure.splash / storage_failure` | 单路径存储失败保留原记忆并回退；需 `--fault-storage` |
| `failure.splash / delete_receipt_failure` | 独立读回后收据写入失败，只读恢复记账而不再次删除；需 `--fault-storage` |
| `failure.splash / delete_accept_failure` | 系统接受后动作记录写入失败，不重复删除；需 `--fault-storage` |
| `failure.splash / delete_unknown` | 返回丢失而系统已删除，先读回核对再恢复记账 |
| `failure.splash / delete_unknown_still_present` | UNKNOWN 后读回仍存在，保留 UNKNOWN，不生成成功收据，不重发删除 |
| `failure.splash / linked_memory_failure` | Run 已完成且 link 已 verified，但来源记忆失败；只读恢复不能再次完成 Run 或更新事件；需 `--fault-storage` |
| `failure.splash / linked_result_failure` | 系统事件已 verified，产物保存失败；重启/只读恢复后正确完成本地结果；需 `--fault-storage` |
| `failure.splash / mail_accepted_receipt_failure` | 邮件被接受而回执保存失败，保留防重放记录；需 `--fault-storage` |
| `interrupted_send.splash` → `interruption_restart.splash` | 实际终止持有发送回调的进程，再启动恢复为 UNKNOWN，禁止盲重发 |

`failure.splash` 的 seed 使用完整 chain 的隔离 state。`--case` 选择表中 case。
`interruption_restart.splash` 使用 `interrupted_send.splash` 或 `mail_accepted_receipt_failure` 的 state。

## 当前阶段

兼容 `card-host` 已实际构建并执行。基线 rc10 完整链 18/18、重启和跨对话 10/10 通过；真实生产函数隔离复现了删除回执缺失、删除已接受但动作落盘失败、日历结果已 verified 但来源记忆缺失这三种恢复缺陷。
总控实现修复；r2 定向测试中两种关联任务恢复各 13/13，删除三种恢复各 10/10。
检查了收尾标记、原产物字节不漂移、重复恢复活动/记忆/目标稳定，以及系统动作不重放。详见 `RECOVERY_EVIDENCE.json`。

一次三进程矩阵启动中有一个官方 Splash 编译超时，未执行该场景，保留 ERROR 及日志。
最终矩阵改为串行启动，继续使用原官方预算，不隐藏编译失败。
原错误和失败样本保存在 `.local-state/`；它们与后续通过样本分开。

## 同一候选矩阵

`run_matrix.py` 先冻结一份完整 bundle，后续 18 个场景都使用同一份源码，输出每次输入、Host、probe 和执行包 SHA 及函数保留审计。
包含新进程重启、关联恢复、UNKNOWN、防重复、存储故障、批准变化和模型服务错误；场景未执行或断言未过时输出 `PARTIAL`。

```sh
python3 official_muse/rc/7h-20261008/business/run_matrix.py \
  --source-bundle <final-candidate-bundle> --host <reference-card-host> \
  --host-cwd <host-resource-workspace> \
  --out official_muse/rc/7h-20261008/business/.local-state/final-matrix-r1
```

候选新恢复接口用 `--delete-reconcile` 验证，`--require-settlement` 验证来源记忆与结果都落盘后才产生 `settled_request_id`。
`malformed_model` 是官方服务“结构输出格式错误”分类的应用处理验证，不能据此声称已经测试真实 Model Host 的格式校验或模型推理。
