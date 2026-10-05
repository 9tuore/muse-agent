# OctoSense 工作区 / Dock 只读审查

结论：冻结SDK中，OctoSense内部Dock覆盖窗口底部是现有样式策略的直接结果。最小合理修复点为 **desktop.rs 中 OctoSense 样式的 reserved_height**，使其与Dock实际占用的88个逻辑像素一致；不需要给Muse composer塞一块固定空白。

## 已核实调用链

1. crates/shell/src/desktop.rs:165–179明确采用overlay策略，OctoSense reserved_height=0。
2. 同文件shelf_geometry:927/942令Dock顶部为H−88、高78，底边距10。
3. desk.rs:1689先保存完整desk_rect；1729扣除reserved_height，随后扣gaps_out，交layout.rects。
4. desktop_layout.rs:55最大化直接取该area；吸附也以它为边界。
5. lib.rs:619–642的App::desk_area从原desk_rect独立扣同一个reserved_height，用于交互/吸附等几何。两处是同一工作区的不同消费者，不是重复扣减。

同一坐标系下，最大化窗口外沿底部=H−reserved−gaps_out，Dock顶=H−88。当前reserved=0且gaps_out不足88时存在纵向重叠；reserved=88则窗口底部位于Dock顶部再向上一个gaps_out。

## 最小修复边界

把受影响的DesktopStyle::OctoSense行reserved_height改为88.0，同步改overlay注释及既有测试reserved数组的对应值。StyleTween::reserved_height已统一服务绘制与交互，无需在desk.rs/lib.rs分别硬编码。不要只修绘制一侧，避免拖拽/吸附与实际窗口尺寸不同。

88来自当前78高+10底边距，不是任意安全垫；不要在下游再扣一次。此修改影响同样式所有应用及初始/受限浮窗尺寸，而非只影响Muse。自由浮窗fit仍只保证标题栏可抓取，允许主体越界，本修复不承诺所有自由浮窗都完整避开Dock。如果必须只改变最大化/吸附而保留普通窗口overlay，则需要更大的统一workarea设计，不是本轮最小方案。

本结论针对OctoSense内部shelf。未查看截图或运行时样式，不能把它直接当macOS系统Dock诊断；Macos样式也为0，但不自动扩大修改范围。

## 现有测试入口（均未运行）

SDK根目录的workspace已包含octosense-shell，包名已从Cargo.toml核实。可使用：

~~~sh
cargo test -p octosense-shell --lib desktop::tests::
cargo test -p octosense-shell --lib desktop_layout::tests::
cargo test -p octosense-shell --lib snap::tests::
~~~

直接相关既有测试：

- desktop.rs:297 specs_reproduce_the_literal_arrays_for_every_style：样式预留值及tween。
- desktop.rs:435 shelf_geometry_reads_the_table：Dock位置应保持不变。
- desktop_layout.rs:77 maximize_and_minimize_keep_restore_rect_and_stack。
- desktop_layout.rs:94 shrinking_the_workarea_keeps_windows_reachable。
- desktop_layout.rs:104 snapping_keeps_restore_size_and_tracks_a_resized_workarea。
- snap.rs:284 edges_and_corners_use_the_workarea。

现有断言主要覆盖旧常量和给定area；最窄补充是在已有样式/布局测试处检查OctoSense最大化与底部吸附外沿不超过Dock顶，restore矩形不变，相关样式过渡保持一致。构建环境未验证，不声称以上命令已通过。

## Sidebar重叠的独立边界

只读了冻结Makepad依赖中的ScrollBars/ScrollBar绘制逻辑：内容与滚动条共享视口矩形，竖条绘制在右侧bar_size宽带内，默认bar_size=10。不能仅凭“reserved in layout”注释假设业务行自动留出可点击空隙。

合理的局部修复是在Muse历史列表的行/内容容器右侧留出实际滚动条宽度加少量间距，让删除按钮退到该区域左边；不应因此全局改滚动条。当前主题实际宽度及Muse最新行布局未在本轮核对，所以这是有源码依据的布局方向，不是已复现的按钮命中结论。

验收由Root复用现有UI流程：历史足够长产生滚动条、窄/宽sidebar、删除点击与滚动拖拽各自命中。无需重复全语义评测。

所有源码SHA及精确路径见同名JSON。未编辑SDK/主源码/宿主、未运行测试/模型/GUI、未接触8493/8484或用户数据。
