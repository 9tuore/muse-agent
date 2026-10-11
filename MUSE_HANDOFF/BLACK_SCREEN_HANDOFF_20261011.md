# Muse 黑屏修复交接

用户已安排 WorkBuddy 接手黑屏。ZC-00 转向 Mail、模型协同和持续任务；当前没有 owned GUI 或 Cargo，构建与 GUI 可由修复方独占。未经同步不要重置开发分支、稳定包、生产数据或旧 dirty。

当前工具没有向 WorkBuddy 聊天发消息的通道，以本文件交接。相同副本放在用户项目根目录的 MUSE_HANDOFF，实际运行证据在下列独立开发工作区。请把修复结果写到该开发工作区的 `MUSE_HANDOFF/WORKBUDDY_BLACK_SCREEN_RESULT.md`，或提供你自己的工作目录与补丁路径。ZC-00 只读接收，再统一整合；请勿占用中央业务源码、根 Bundle 或修改中央 Git 暂存区。

## 实际现场

开发工作区 `/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松`，分支 `codex/muse-pivot-20261010`；交接前最新 HEAD b95b7b2343615b3f0a1c7654f353fcb669e4517d，Muse source86f86e3e、compacta191e735。原始完整 Host `build/muse-integrated-history-r1/octosense` SHA25630d4d35646591b5aca1d39f912338427362e7c7c478892aab7635ef2d32c5836；包内签名后 Host ec83a4f9682f75602b88f7d4cf17d3c8711e7b5034298d848735bafce685594d，签名差异不是不同源业务实现。

实际预览包 `build/muse-integrated-0.4.0-rc3-ui-r1/Muse.app`。独立数据 `build/muse-integrated-0.4.0-rc3-ui-r1/state`。默认启动与 MAKEPAD_NO_GAUSS=1/MAKEPAD_SUPERSAMPLE=1 两轮截图均全深色；不能据此确认 NoGauss 已覆盖全部合成链。真实 CGWindow6335曾 onscreen，OS 专窗截图同样深色。Remote/snap 有 AppHub 标题、Muse、Get 等40控件；普通click和hw=1均未安装/转页。无 [E] 或64ms预算错误。gpu.drawcalls 多个 main、gauss、wm_window_surface pass持续 draw_calls_done=0；gpu.hole 未打印。root只清背景，不能把控件树当界面成功。

失败证据全部在 UI-r1：01-apphub.png、04-no-gauss.png、06-os-host-black.png、black-default-host.log、black-no-gauss-host.log、black-snap.json、black-status.json。原首轮 detached Python 启动随工具父进程退出，未获得窗口；之后使用真实 exec 会话启动并实际观察。

## 源与构建控制权

配套 SDK `build/runtime-closure-full-shell-r1/sdk`，Hub sibling `hub`，中央 target `build/official-hub-rc2-target`。锁定 features 为 app-hub,octos-core,app-muse-native-prototype；不要临时切换 feature graph导致全量重编。构建用 integrated_release/build_host.py 的官方 package_env、资源模式、锁定依赖和路径重映射。

中央仍在推进独立业务代码，最终还有 Qwen fast alias 目录补丁与 Native 持续任务控制补丁需要集成。它们不会直接改你的共享 SDK。请先交出可见 UI 的修复最小单元，双方确认合入后再由中央进行一次完整候选打包；避免两边并行写同一 target。持续保持原始失败日志和各版本 SHA，不以 Remote 控件树代替 OS 可见界面。

Metal 原源 `sdk/.sources/makepad/platform/src/os/apple/metal.rs` SHA25647db4d10503ee4ed70860529f914df8b740c16f2bc04f768fcb9fb69314f5a04 已精确恢复。限量诊断备份/patch 位于 `build/muse-metal-skip-diagnostic-r1/`，候选 SHA2e052d15，只打印最多96条数字与状态，不改渲染条件。该诊断构建在用户交接时对 owned Cargo82177 发 SIGINT，177.013s、exit -2；不是编译报错，未生成诊断Host。源码恢复前核对仍为中央候选SHA，未覆盖他人变化。现有完整Host与失败证据均保留。

可首先区分 render_view 的 list order_len、retained_presentable、os_shader_id、实际resident实例、PSO与geometry跳过原因。当前没有确认根因，不建议继续盲改Cache2或重写应用。若需上述诊断，只应用保留的一文件patch，在控件树准备后启用 gpu.muse_skip，再取一次帧；输出不足不等于通过。

## 业务边界

签名目录 `build/muse-integrated-0.4.0-rc3-final/mirror` 已验证，只对配套本地Host；不是公开Hub准入。Agent exact-four/consent/Relay不绕过。root rc17、生产用户资料与历史失败不改。正式 Muse Relay、真实Mail、T18和最终20次尚未通过。

GPT开发团队与产品提供方分别配置。产品保留内置Qwen与原MiniMax-M3；hybrid代码已合入，但真实协同和持续代理未完成。Model设置/权限/可信审批不得模拟，日志不得包含Secret。

修复交付请给：最小patch、准确源码SHA、原始构建命令/log、包内实际HostSHA、OS窗口截图与按钮实操结果。共享SDK应用和正式打包由双方先明确所有权，中央最终统一整合。
