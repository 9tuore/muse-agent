# Handoff

## Task
ZC-00 统一 Muse，开发分支 codex/muse-pivot-20261010。用户要求先完善官方接口、联通和内置 Calendar，再真实验收；GPT 高速并行，三专项独立 worktree。

## Result
PARTIAL。History配套 Host30d4d356完整构建成功；四工具准入安全测试通过。尚未整包运行/真实业务通过。用户最新要求产品Qwen+云端MiniMax协同、内置持续事务AI，GPT-only仅开发团队。

## Changed
有界源准备/冷开/签名目录脚本；模型迟到身份校验；GPT 原生设置与无 Qwen 打包模式；Calendar 页官方应用级会话接线、请求持久化、未知结果不重试、原 ID 保留。Calendar Broker 终态/History 和 Mail 恢复单元在专项工作区开发。

## Tests
真实 reference VM 合成模型身份6、Calendar会话/恢复/回执19、Mail完整异步恢复37项通过，外部调用 0；VM 准备 1、streaming 5、硬时限 1、样式 6 通过，原失败保留。GPT 启动器专项 clang/9 项签名 stub Host fixture 通过。以上不是本机真实 Relay/SMTP/GPT 实调。

## Commit
e962e418 已普通推送并独立核对远端相同；GPT-03 3c5fcd17 接收为 66cf2948。中央 Calendar 单元待本次提交。

## Remaining
hybrid启动器与官方持续任务契约；签名单包 GUI；同 Muse ID 原生助手授权与 Calendar 真实工具回执/读回；Mail 原生本人登录/审阅与真实状态；同候选行动链、T18、最终20次。

## Important Boundaries
保留根 rc17、生产资料与原 dirty；旧 r8 空白证据保留。官方会话是应用级共享历史，不注入私人 Muse Memory，不宣称独立项目/上游遗忘。未知外部动作不自动重做；本人输入与可信批准不能模拟。
