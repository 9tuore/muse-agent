## ZC-00 最新接续：2026-10-11 14:15（北京时间）

用户最新修正产品运行方式：携带内置 Qwen，本地与云端协同，保留现有 MiniMax 云端；GPT-only 约束开发团队，不强制改产品云端。只提取 `config.llm` 的非秘密 metadata，已确认旧 live-acceptance-003 为 minimax-cn/MiniMax-M3，新 rc1 隔离 profile 为 local/local-default。这些是不同版本/目录，不能拼为同候选实调通过。持续任务须使用现有官方接口，hybrid 启动器正在独立开发。

最新配套完整 Host 已增量构建通过（196.977s），SHA256 `30d4d35646591b5aca1d39f912338427362e7c7c478892aab7635ef2d32c5836`，包含真实 Broker 终态与精确 History 关联；基础八文件及 History 九文件源身份已核验记录。Calendar 官方应用接线/回执19项真实参考VM合成协议 PASS，外部调用0；r5测试数据使用保留字ok导致的fixture解析失败完整保留，修正仅在fixture。Mail完整异步恢复真实参考VM37/37 PASS，仅只读合成compose_status，不证明SMTP投递。

待完成：新签名目录/单包 GUI、模型与实际凭据联通、本人原生Agent启用、内置Calendar正式Muse Relay工具与独立读回、官方Mail实机草稿/审阅/状态，以及同候选持续事务/行动链和最终回归。最新完整Host、签名和fixture结果不代替业务验收。根rc17/生产/旧dirty与失败证据保留，尚未正式发布或比赛提交。

## ZC-00 GPT 高速集成：2026-10-11（最新工程状态）

用户要求先完善联通与内置 Calendar，再进行真实验收；GPT 主导开发，现有三聊天均已设置 GPT 6.1-sol 并创建独立 worktree。开发分支 e962e418 已普通 push，独立 ls-remote 一致；main、根 rc17、生产资料与原 dirty 保留。新基础宿主 f5eb2574 完整构建成功（37m56s），exact-four/签名/撤销/他应用拒绝测试通过；已接收 Calendar History 终态补丁并在同一 target 增量构建，尚未交付正式版。

中央已接收 GPT-03 原生 GPT 启动/打包单元，整包可不携带 Qwen，缺配置打开 Models；metadata 检查不代表实调。新增 Calendar 页应用级接线：octos.session.open → octos.turn.start(trigger:app) → octos.session.history，保留请求 ID，当前回合/lane/精确工具过滤，不把模型文本当成功。未知或已结束请求不得被新 ID 覆盖；显式保留原请求后才能另写不同事项。重启只标未知，不自动派发。真实参考 Splash VM 合成协议 14 项通过，外部调用 0；不是新宿主或真实 Calendar Relay 通过。

剩余：完整宿主运行与冷开；Calendar 官方终态回执补丁/真实四工具；Mail 官方中断恢复补丁、原生登录/审阅/投递；同候选行动链与最终回归。源准备、工具上限和签名检查不能替代本人 consent 与实际业务结果。正式比赛提交/公开发布未执行。现有 GPT 配置、本人凭证与实际 GPT 模型调用待新宿主界面准备后核验。

## GPT-03 Hybrid 补丁：2026-10-11

用户纠正产品云端保留 MiniMax，GPT-only 仅开发验证。package 默认 hybrid 并继续携带 Qwen，
已有 Native 云端主配置保留；缺云端设置转 Models，Models 不启动 Qwen/改 profile。
Hybrid 启动 loopback 本地服务并跟随 Host 生命周期，仅更新既有命名 Qwen 回退路由；
云端单独 profile 原字节保留，不迁移凭证。local-model.json 区分 ready/failed/stopped 与选中状态。
16 项签名 stub Host/合成 health fixture 通过，实际 Qwen/云端协同和持续 agent 未验证。
已安全只读确认旧业务为 minimax-cn/MiniMax-M3、Native 默认 api.minimaxi.com。
GUI smoke 按指令暂停，未提交脚本保留；未占用 GUI、未运行真实模型、未 push。
