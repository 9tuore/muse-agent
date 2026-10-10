# Full Shell render review — R2

**结论：VISIBLE_ACCEPTANCE_BLOCKED；ROOT_CAUSE_UNKNOWN；NO_P0_ESTABLISHED。** 一次定点只读复核已完成。新增证据使“仅 CGWindow/remote 截图异常、只抓到初帧”的解释不再充分。发现一个有代码依据的共享 shader 缓存候选，但没有运行时错误命中证据，不能称已定位或已修复。

本轮只读现有 PNG/JSON/源码，报告是唯一写入。未操作 GUI/remote、编译、运行 Cargo/Git、启动宿主、访问 r3 构建会话、点击 Allow 或调用模型。未碰稳定 503。源码来自 `build/runtime-closure-full-shell-r1/sdk` 当前现场；其对应 r2 二进制的逐文件构建 provenance 本轮未复验，下面的行号和 SHA 是本轮源码观察，不等同于冻结二进制证明。

## 新证据与边界

- `all-window-probe.json` 回执记录 owned IDs 2734/2735、launcher 已清除 HIDE_WINDOWS/NO_FOCUS；`os-window-captures.json` 两次 OS 抓取 exit=0。回执自身仍写 visibility_not_verified，本轮没有人工玻璃屏观察。
- 已看 `os-window-2734.png`：确为带系统标题栏的 OctoSense 窗口，Shell bar 文本存在，正文没有控件。保守中部 ROI `[440,350,2055,1225]` 共 1,413,125 像素，只有 RGB(14,16,17)。OS 色彩管理下的值不应与原始 Metal RGB 强行相等。
- `three-frames-r2.json` 成功 n=3/every_ms=500，均 capture_kind=pixels。保存的 frame-0/1/2 三张 SHA 完全相同：`b2ccb7902f6012081d46b826a0df75bed00119974b5fc6e536a14b544833f741`；每张中部 ROI `[420,322,1959,1129]` 的 1,241,973 像素只有 RGB(16,19,21)。本轮不删除首轮失败记录；具体首轮 404 由中央报告，本轮成功回执中没有该请求原文。
- OS 与 Metal 路径都显示正文空白，说明问题已进入呈现/绘制候选范围；不证明具体 shader、驱动、clip 或 pass 已定位。此前 Native consent 的深色文字和白色 Allow 实际可见，证明一些文字绘制仍有效；没有 Allow 授权或业务成功证据。
- `/shader/consts` 只列带标注 table constants 的 shader（remote.rs:1928–1945），不是全部 shader/PSO/geometry 成功列表。已有五条结果不能证明其它 fill shader 成功或缺失。

## 模块与共享绘制：已核实的路径

`crates/shell/src/module_view.rs:537–557` 先开 turtle、读取实例 theme.color_bg_app 并绘制 DrawColor ground；`624` 在 contain/实例 isolate 中 `root.draw_walk_all`；`630–669` 恢复 ModalBounds、失败时 stop，再结束 turtle。ground 的 draw 在 root 调用之前、实例 theme 查询结束之后。当前 ground 与窗口 clear 同色时，纯色截图不能证明 ground 本身成功。

`module_host.rs:191–204` 的 enter_isolate/leave_isolate 是本文件记录链接归属的包装；真正 VM 切换由 `widget_async.rs:1780–1839` 的 with_isolate 管理。两者不是同一个 enter 函数，不应把这里误判为双重 heap 切换 bug。成功 draw 不走 unwind_to；ModalBounds 主要限定模态范围，不等同于独立 GPU pass。`View::draw_walk`（view.rs:1125–1335）根据 optimize 开普通、draw-list 或 texture 路径；布局/Area 能存在而 GPU draw 被跳过，因此快照并非像素证明。

填充路径存在共同基底，但不是同一个 pixel shader：

| 使用处 | 实际绘制 | 依赖与限制 |
| --- | --- | --- |
| module ground | DrawColor.draw_abs | draw_quad.rs:73–78 的纯色 premultiplied pixel；DrawQuad vertex/clip/instances |
| RectView | View.draw_bg / DrawQuad 派生 pixel | view_ui.rs:100–149 的 SDF fill；color_2=-1 默认禁用渐变；show_bg=true |
| Shell solid / scrim | DrawShellFill | ui.rs:38–44 的纯色 premultiply；solid 在 alpha<=0 或 size<=0 返回 |
| consent card | ShellDraw.card_faded | ui.rs:1443：glass→DrawShellGlass，flat→DrawShellChrome；不能未经 material 证据称它必然是 DrawShellFill |
| Native/Bar 文字 | DrawText | 独立 text vertex/pixel/实例字段；仍使用 geom.QuadVertex/QuadGeom |

consent 先 scrim、再 card、后文本与按钮（approvals/view.rs:704–745），文字低对比可能来自 theme/material 与缺失 fill 的组合。ShellTokens.with_palette（shell/mod.rs:472–503）会同时替换 popup background/text/border；card 的实际 material 分支本轮没有运行时值。Bar 背景（bar.rs:661）在 glass 模式也会主动设透明。因此不能把 bar 背景与桌面同色单独当作填充失败。

DrawText（draw_text.rs:554–564）同样引用 QuadGeom；geometry_gen.rs:341–360 已将标准几何放在 Cx 共享槽、各 VM 使用 borrowed handle。此源码已有防止 isolate 释放标准几何的保护，不能把“所有 QuadGeom 丢失”当作首选定论。文字可见也反对整个 GPU/字体/四边形资源全失效的说法，但不排除特定 shader mapping/clip/实例上传错误。

Metal render_view 的静默跳过条件（metal.rs:569–732）包括 retained 不可呈现、os_shader_id=None、实例驻留数=0、PSO Err、geometry_id=None/stale/布局不匹配；没有 shader error 日志不能排除这些条件。PSO pending 则置 paint_dirty，pipeline 成功回调发 SignalToUI（3661–3665），enqueue 失败还有 retry_metal_pipelines（2018）。故“异步 shader 首帧未完成”不应直接定为永久黑屏原因。

## 最具体的代码候选：函数缓存缺少 VM 身份

**已确认代码事实，未确认本次命中：**

1. 每个 isolate 用新的 ScriptVmBase::new，拥有自己的 ScriptCode.bodies（widget_async.rs:595–610；vm.rs:1934、1998）。ScriptIp 仅包含 body/index，to_u40 仅拼这两个数字，没有 VM/heap 身份（value.rs:20–46）。
2. DrawVars::compute_shader_functions_hash（draw_vars.rs:1301–1333）只遍历方法名和 ScriptIp 数值生成 hash，没有 heap_key、函数内容或 IO 布局。同名方法和相同 VM 内位置在不同 heap 中不保证是同一函数/同一 shader。
3. CxDrawShaders.cache_functions_to_shader 是 Cx 全局 LiveIdMap（draw_shader.rs:107）。Metal Cache 1 已使用 `(heap_key, io_self)`，但 Cache 2（metal.rs:3279–3290）只按上述 fnhash 查询，命中后直接 finalize_cached_shader 并 return，跳过实际 Metal 源码生成与精确代码 cache。
4. finalize_cached_shader（draw_vars.rs:1337–1350）复用旧 mapping 的 dynamic instance slots、shader id、geometry id。若跨 heap 的位置碰撞发生，可能让仍有布局的控件使用不对应的 shader/实例布局，影响不止 module，也可能影响以后注册/首次绘制的主 VM 填充。

这是一条可证伪的候选机制，并非日志已证实的碰撞。还没有抓到 fnhash→不同 heap/不同生成源码 的实际成对记录。禁止据此升级为已确认权限漏洞/P0，或直接对外宣布渲染根因。

## 给中央的一个可逆验证

**优先做一次“只绕过 Metal Cache 2 查询”的隔离候选对照。** 在 `.sources/makepad/platform/src/os/apple/metal.rs` 的 `DrawVars::compile_shader` 暂时绕过 3280–3290 的 `cache_functions_to_shader.get(&fnhash)` 命中/return 块；保留 heap-key object cache、fnhash 计算/写入、生成 shader 与后续 Combined Metal 源码精确 cache（3394–3412），不改 theme、模块 draw、consent、权限或业务。这是诊断建议，本轮没有应用或编译。不要把它顺手塞入正在编译的 r3；独立保存 diff、Host hash、同样的 fresh-home launch/只读 Calendar 和未 Allow 的 consent 证据，再回退该单点。

判断标准：

- 新候选 Calendar 正文和 consent 填充恢复，且布局一致：显著支持函数缓存错误复用；仍需记录一次旧/新 shader 源码或 mapping 差异后才能确认为根因。仅“重新构建后好了”不足够。
- 正文与 fill 仍空：该候选不足以解释故障，保持 UNKNOWN；不要继续无限改 cache。下一条具体信息应是该模块/consent draw 的 shader id、instance count/slots、PSO 状态、geometry layout 与 clip/pass 实值，而不是更多 CPU widget 快照。
- 只修复其中一项：按结果拆分，不能称共享根因已证明。

暂不建议只给函数 hash 加 heap 地址当最终修复：heap_key 文档仅承诺存活期间唯一，widget_async.rs:659 明确有地址重用；长生命周期缓存的失效规则需单独核实。绕过 Cache 2 可避开这一诊断歧义，同时保持精确生成代码 cache。

## 现有测试/参考版本能证明什么

已看 `typed_vertex_test.rs` 的 typed_quad_pod_layout_matches_gpu_stride、f32_quad_and_typed_quad_geometries_stage 等：检查 CPU packing/staging，不证明本机 Metal 像素。`widget_async.rs` 的 isolate 进入/恢复、second_isolate_render_commits 测试检查 VM/树/host response，不是本机 GPU framebuffer 对照。`system_app_theme_tests.rs` 的 news_source_tabs_read_on_the_page_in_light_and_dark 检查颜色值与计算对比度；ShellDraw.measure 测试甚至特意断言不产生 glyph pixels。这些测试存在，本轮未运行，不能代替当前可见验收。

同 checkout 的 `.sources/makepad/apps/wm/src/module_view.rs:270–328` 有 WindowFrame/texture capture 后呈现路径；当前 SDK shell module_view 直接 inline root。它们是两个实现，不是已确认的 r2 前后版本回归；不可直接移植来宣称修复。

## 本轮读取关键源码 SHA256

- `crates/shell/src/module_view.rs`: `792b0c7e53684885411c552651905d9225cdeed147dcc10ac9f6ac98941d670d`
- `crates/shell/src/shell/ui.rs`: `e238671c9b4bf777a71804b5d4e0637f28825da5eb382937297cec9083d17eaf`
- `.sources/makepad/platform/src/draw_vars.rs`: `6dbd6b81fcca67a9bbcf69ab6b8c24aa28f8a1310dd8119830fb613597ba3660`
- `.sources/makepad/platform/src/os/apple/metal.rs`: `47db4d10503ee4ed70860529f914df8b740c16f2bc04f768fcb9fb69314f5a04`
- `.sources/makepad/platform/script/src/value.rs`: `0fc7544e202217544045e27614bb5bcb54f79bc9fd2584c19a5fcb6fbafbce16`
- `.sources/makepad/draw/src/geometry/geometry_gen.rs`: `259a6139017331bc572bdf5c078d920a164505a62430d6eca33cf2809d321c94`
