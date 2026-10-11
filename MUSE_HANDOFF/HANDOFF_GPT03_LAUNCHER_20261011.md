# Handoff

## Task

GPT-03；独立 worktree gpt03-launcher-preflight，基线 e962e418。接通 GPT 开发验证的原生模型配置入口。

## Result

PARTIAL。新增 --gpt/--gpt-check；GPT 打包模式不含 Qwen，缺配置进入 Models，GPT 配置仅标 CONFIG_ONLY。--models 不启动离线模型、不写 profile；Host HOME 使用独立目录。

## Changed

integrated_release/muse_launcher.m、package_app.py、test_launcher.py、README.md 及 CURRENT_STATE。

## Tests

2026-10-11 clang 本机编译通过，只有两条原有 unused 参数 warning；test_launcher.py 九项签名 stub Host fixture 通过。首轮 helper 重复 mkdir 错误已修复。package_app.py --help、git diff --check 通过。现场默认独立目录无 profile，未读取秘密。

## Commit

本地提交随交付回复给出；未 push。

## Remaining

中央接收后以 --model-mode gpt 打最终包；本人在 Models 输入凭证并保存 OpenAI/GPT 官方路由，退出后重开。最终 Host GUI、联网与 GPT 实调未验证。

## Important Boundaries

主源、root bundle、SDK、Cargo target、生产资料未改；没有启动真实 Host/模型或占用 GUI。fixture 只验证启动器，配置识别不证明凭证有效或动作完成。

## Calendar 会话短审查（2026-10-11，只读）

中央 main.splash 初读 fd086929，末读 8240b3ad（中间已补 row.is_object guard）。三项问题仍存在，行号针对末读 SHA：

- **P1 · UNKNOWN 被覆盖**（543-554、10375）：submit 只拦 busy/writable；失败或重启后 unknown 且 busy=false，重复提交生成新 ID，覆盖唯一旧记录，可能重复创建且丢失原对账键。最小修复：unknown/in_flight 禁止派发；保留旧记录，先只读对账。另开不同请求必须显式并保存旧记录，不能隐式当重试。
- **P2 · 跨账号显示旧正文**（499-507、10379-10380）：History 阻止账号不符的新读取，但没有清除旧 reply/evidence；页面仅按非空显示旧正文。最小修复：显示条件加入 state.user_id/accounts 与当前身份相等；不符时隐藏正文并提示原请求账号，不删除历史。
- **P2 · 重绘丢输入**（8872、10374）：TextInput 在 calendar_panel.on_render 中且无 text/on_change 状态绑定。现场 SDK `.sources/makepad/widgets/src/view.rs:248-257,970-978` 明确普通 render 重建子控件；任意 redraw 或 History 完成会重置草稿。最小修复：将输入放到一次挂载区，或用独立 draft + text/on_change 保留；加 is_multiline:true，当前默认单行（text_input.rs:575-576）。text() API 已核实存在（2397）。

trigger:app、turn/thread 冲突拒绝、person lane/role/tool_call_id 筛选、迟到身份回调拒绝均有明确源码检查。report.json 实列 12 个 checks，不代表本机官方服务成功；其中 no_replay 只测 boot 不自动调用，没有测 UNKNOWN 后再次 submit。建议只补三项窄回归：UNKNOWN 手动重提保留 ID/零派发、账号变化隐藏旧正文、输入后 redraw 保留草稿。未执行新模型/GUI/VM测试，未修改中央源。

### 最新复核：141be24c（2026-10-11）

原 P1 UNKNOWN 覆盖已修复：函数和按钮限 idle/blocked，显式 keep_previous 保存原 ID/turn/status/身份，32 条满后拒绝继续归档；没有自动派发或标 verified。中央 r3 report 的 source_sha256 与现场一致，14 checks 全真、零外部调用；本聊天仅读取报告，未重跑。

剩余两个 P2 仍存在：10399-10400 旧正文未按身份限制显示；10393 输入仍在动态 render 且未绑定草稿。沿用前述最小建议。

新增 **P2 · 同 schema 旧记录被拒绝**（480-490）：previous_requests 现在必填，但 r1 保存文件实际为 schema:1/status:unknown 且没有该字段，符合旧合法格式；升级后 boot 会设置 writable=false、停止全部新请求。最小修复：旧 schema:1 的其他字段校验通过且仅缺 previous_requests 时，补 []，保留 request_id/turn/status/身份；字段存在但非数组或超限仍拒绝。新增一项旧记录恢复 fixture 即可，不删除旧记录、不重派。

### Hybrid 交付（2026-10-11，覆盖早前产品 GPT-only 方向）

用户已纠正云端仍保留 MiniMax，GPT-only 仅开发验证。现场只提取指定旧 profile 的 family_id/model_id/route.base_url 元数据：minimax-cn/MiniMax-M3，route 省略，Native 默认 api.minimaxi.com；未读取 env_vars 或解析凭证。没有把旧业务与新隔离候选混称同版。

package 默认 hybrid，要求公开模型输入，保留 offline/gpt；--hybrid 接受已有 Native 云端主配置，缺失转真实 Models。Models 不启动本地服务、不改 profile。Hybrid 启动包内 loopback Qwen 服务；cloud-only profile 原字节保留，只用 plutil 就地更新既存命名 Qwen 回退端点，不添加提供方、不修改云端 primary、不迁移凭证。state/local-model.json 记录 ready/failed/stopped、native_local_selected、inference_verified:false。显式 --gpt 优先于 hybrid 包设置，不启动本地；混合/MiniMax profile 不会被改写，应由本人另配独立 GPT-only 验证 state。

真实编译启动器 + 签名 stub Host + 合成 health endpoint 16/16 PASS，包括 MiniMax 保留/本地路由、设置及 GPT override。没有执行真实 Qwen 或云端推理。仅原有两条 unused 参数 warning；Python help/syntax 与 diff 检查通过。

官方 `_main` primary/fallbacks 与 model.complete 类别排序/回退支持双提供方可用，不支持应用指定独立本地后台模型；Contained prepare 明确不产生回合。没有发明持续后台配置或付费轮询。中央后续须分别验证真实 local health/存活与退出清理、两端各一次有界推理的 Host 归因、本人启用后既存 agent 事件入口的响应，才能宣称持续协同。未自动批准、发信或写日历。

GUI smoke 草稿按新指令暂停，仍未提交/实跑，不随本补丁提交。

按中央签名边界补充 PACKAGE.json：source_host_sha256 固定输入 Host，签名前核对暂存副本；host_sha256 记录包内签名后实际执行字节，并附边界说明。未重新构建/打整包，中央最终运行使用 signed hash。
