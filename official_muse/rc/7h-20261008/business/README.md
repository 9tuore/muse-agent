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
| `failure.splash / mail_accepted_receipt_failure` | 邮件被接受而回执保存失败，保留防重放记录；需 `--fault-storage` |
| `interrupted_send.splash` → `interruption_restart.splash` | 实际终止持有发送回调的进程，再启动恢复为 UNKNOWN，禁止盲重发 |

`failure.splash` 的 seed 使用完整 chain 的隔离 state。`--case` 选择表中 case。
`interruption_restart.splash` 使用 `interrupted_send.splash` 或 `mail_accepted_receipt_failure` 的 state。

## 当前阶段

隔离脚本已实现，Python 语法与入口参数检查通过。实际 VM 执行等待总控恢复兼容 card-host，尚未据此标 PASS。
已有源代码审查指出：rc10 的 standalone delete 收据失败后复用读回 helper 会在 action 已 verified 时被 accepted 前置条件阻止；必须真实复现并由总控修复，不能重复 delete 完成回执。
