# Handoff

## Task
ZC-00：统一 rc4 候选、复用 WorkBuddy 可见宿主、继续官方业务验收。

## Result
PARTIAL。签名 hybrid 单包已生成；原 WorkBuddy 入口重启后可见，本人Install和Native Allow已完成；完整Muse打开，官方Calendar只读真实调用通过。

## Changed
正式 main 当前事项→官方 Calendar 精确读回→可选 Mail 草稿已接入；统一 Launcher/仓库脚本/GitHub 回归接收。仅向原 WorkBuddy Launcher 添加三个公开目录变量，原字节备份保留，Host/STATE/HOME 未替换。

## Tests
完整 Host Release、paired-host gate、整包 deep/strict 签名通过；Launcher21、Qwen目录12、Calendar参考VM19、Mail参考VM37通过，均不证明业务投递。GitHub run38122820596实际SUCCESS。新增40项参考VM探针尚无PASS；旧解析失败日志保留。

## Commit
真实Calendar.events完成1/失败0/未核验0，Broker持久回执见workbuddy-rc4-calendar-readonly-live.json；无外部写入与SMTP。本节点正常推开发分支并核对远端；正式 main 源SHA0c7f9812，签名目录引用72f7b1ef。

## Remaining
实际Calendar新建/精确读回、Mail/模型/行动链业务，持续 Kernel权威配额，T18与同候选20冷启动。新包宿主首屏需修复，现场继续保留可见 WorkBuddy Host。

## Important Boundaries
当前可见Host ec83a4f9 与新包d273ebf3不是同一二进制，不能拼接验收。生产数据/旧dirty/旧证据不动；不公开发布或比赛提交。
