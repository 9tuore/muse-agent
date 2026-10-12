# 新黑桌面对照与有界诊断

当前状态 `ROOT_CAUSE_NOT_ESTABLISHED`。本文件不是已应用修复，ZC03没有操作任何窗口、写SDK或构建Host。Root/ZC05负责9799，生产原图不进入本目录或公开素材。

## 14:52 更新：rc8准备与单Host新入口

Root新双Startup/同合成state/单Host初始化的28170/native741原图已由ZC03实际查看，完整Muse/Ocean/chrome可见。它否定新入口必然黑，也不定并行/GPU根因；无新SDK/GPU修复。Root实际providers/Test Connection在loopback仅计数+1/Connected3ms，不是MiniMax或真实云业务。启动器跨profile互斥与退出等待26项是签名stub，不扩为长期稳定证明。

Root已接Memory947，当前Root现场HEAD16fa2cc5（继c716886f/25bb163e）；rc8准备身份：upstream947c、stamped readable a5af07e9、compact0491807b。三层7项只读核对通过，stage仍PREPARED_NOT_ADMITTED，不称rc8已GUI三轮/正式上架。R5保底与原旧证据保留。CA测试Host由Root在独立SDK/target编译，诊断目前只建议有界实际pass/texture/clip绑定，不改GPU。

## 实际观察与不能推出的结论

ZC03已查看纯合成r1的Consent、AppsMenu、关闭Consent后的原生图：顶栏与overlay可见，桌面壁纸、窗口chrome、AppHub/Muse正文黑；反射树存在且给出正常clipped布局。Host日志已有module create、字体安装、Main eval，无script time budget exceeded或[E]行。日志没有逐producer/consumer的texture/clip记录，不能宣布是哪一个pass失败。

Root实际Omarchy及MAKEPAD_NO_GAUSS=1/MAKEPAD_SUPERSAMPLE=1对照仍黑，bar外观变化证明开关生效。它们不能称修复，不重复试。176个包内渲染资源与R5字节一致的核对发生在分工收窄前；资源/Models后续归ZC01。

Root报告并由ZC03查看的native-original-one-process-restart原生图：同original R5/同合成state/同flags，在两个Host都graceful退出后重新启动一个Host，Ocean、chrome、原型正文可见。首次Deny也已持久化，这是带共同变化的条件，尚不足认定并行或GPU原因。它仅证明原型可见，不是AppHub/完整Muse或业务PASS。此为较早原型对照；上方14:52更新另记新双启动完整Muse的原生观察。

Launcher有精确入口差异：R5 `launch-muse-native-prototype`，新clone `launch-apphub`＋`launch-hub:muse-goals`。shell/lib.rs run_test_actions在Startup初始化末尾直接launch；普通菜单路径则在运行后的输入事件中launch。记录这个变量，不能凭差异认定它是根因。

## 源码确认的绘制链

实际路径是sdk/crates/shell/src，而不是另一套.sources/makepad/apps/wm实现。WmDesk.draw_walk从Scope取得WmState并产生targets；draw_tile在rounding或warp需要时打开WindowFrame。Frame先记录chrome和模块root，end恢复父pass，再由draw_window_surface_band绑定frame.texture到draw_phone槽0、opacity=1/y_flip=0并画consumer quad。composing启用时还有BackdropCompositor；Window级Gauss是另一层，不能将最终window pass没出现正文文字视为模块缺失。

来源：desk.rs draw_tile约1139/1226/1340/1350；dock_warp.rs WindowFrame.begin/end约147/166；module_view.rs draw_walk约537；desk/phone.rs draw_window_surface_band约111。位置按当前SDK源码，后续patch须重新定位。

widget_tree.rs的/snap坐标已使用Area::clipped_rect并应用最终draw-list view_transform；这是有效CPU布局/命中依据，仍不是producer纹理含像素或最终呈现成功的证据。

## 仅在Root再次得到单Host、同state/同flags仍黑时

先保存该轮owner PID、Host/Launcher/Main/manifest SHA、实际原生window ID、flags、原图和完整日志。健康/黑对照保持同资料、相同入口与方法；不复制生产profile，不将empty data和64/128规模速度比较。

现成`/trace?topics=gpu.pass`只给pass debug_name和GPU耗时；MAKEPAD_WM_TRACE_WARP只给capture rect/begin/end。可供Root短时观察，但不能据此推出texture或clip身份，不需要先改GPU。

若确需Root独立诊断候选，最小观测边界应为每client最多2次、最多4clients/16行，默认关闭，仅数字/rect/IDs，不打印source、正文、profile或凭据。绑定以下实际字段，禁止硬编码pass44/16或texture序号：

- producer：client ID、WindowFrame.pass_id()、pass.debug_name、frame.texture().texture_id()、draw_rect和dpi。
- consumer：当前draw-list ID及cx.draw_lists[list].draw_pass_id，draw_phone.draw_vars.draw_shader_id/geometry_id/area；texture_slots[0].as_ref().map(|texture| texture.texture_id())，与producer texture比较。
- clip：consumer Area.is_valid/rect/clipped_rect；模块draw_bg的shader/geometry/Area及clipped_rect、父list/pass，区分模块实际recorded area和父consumer。
- capture为None时仍记录模块背景/父list/pass，不能因为Omarchy跳过WindowFrame就漏掉inline路径。

这些字段/方法已在现场DrawVars、Area、WindowFrame、CxDrawList定义和现有使用处核实；尚无诊断patch、编译或实际日志。Root当前要求暂停GPU源码改写，先完成受控对照。如果单Host路径持续可见，可将单Host操作作为本次验收约束，但不能宣布软件根因或永久修复。

## 启动计时的边界

旧R5 20轮full ready中位21.652s；after-open PNG到native-initial PNG中位12.958s，只是含轮询/输入/截图的恢复等待区间。64/128、空forget的gm_boot安排122个串行20ms片段，名义delay合计2.44s，不等于实测总耗时。macOS start_timeout传入实际delay，NSTimer未见100ms硬下限；不猜有固定100ms限速。

现成timer trace只覆盖paint-clock timer0/指针capture timer，拆live_edit/net/pad/paint/gc；不直接逐条测gm_boot Script timeout。Memory裁剪patch仅删相反阶段无效遍历，同数据CLI验证独立交付。GUI/64ms性能改进仍待Root同方法实测，旧不复现N00414报告不改标签。
