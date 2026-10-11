# Handoff

## Task

NIGHT-004 GPT01：原生 Calendar 重叠缺口、最小 Main 提案与 guard。

## Result

PARTIAL。Root 固定 c892 的实际首次同槽操作 owner 1→2 已复现；当前提交提供未应用 Main patch。纯 VM／离线回放 49/49 PASS；真实接入后 query limit200、候选第二次选择和 full-chain 待 Root 串行验证。

## Changed

仅 GPT01_NIGHT004/overlap 提案、probe、准备脚本、证据与本 namespace 状态/交接。Main 提案 source 8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d；patch b34ac5c26e3d955dcc3358e66caa0323ed15cef2f099376967a6342e21be7ece。

## Tests

现有 frozen VM f48060d9，三进程 exit0／stderr空／RPC0，20 receipt +13 interval +16 scope/gesture 断言 PASS。正例回放未改写真实 {} receipt，同解析器的 limit200 不同 digest 必须拒绝；未伪造通过的 Host receipt。scope 使用生产函数，dispatch 只作 unit 计数。中央只读 git apply --check PASS。最初缺 --rpc 的 parent FAIL、原 ok reserved 语法失败、definitions-only 超时均保留，不计通过。细节见 overlap/README.md、VM_GUARD_RESULT.json。

## Commit

当前本地提交见 Git／聊天，未 push。

## Remaining

Root 接入、实际 source/Main SHA 重准备并签名；同槽/包含/相邻及时间/Goal/未知字段 probe；GPT02 正向 query→history settle→第二次 candidate gesture。旧 L4 中央五项实际 PASS 的证据与历史记录保留。

## Important Boundaries

手动重叠在 Calendar 合法；此提案是 snapshot 提醒与独立选择。提示词不是工具权限隔离，额外 mutation row 只能令 UNKNOWN/no第二次nativecreate，不能撤回 query 已发生的副作用。快照不预约时段、runtime不恢复审批。原 Host 门禁保留；未改共享 Main/SDK/Gate/bundle、启动 Kernel/GUI/Cargo。
