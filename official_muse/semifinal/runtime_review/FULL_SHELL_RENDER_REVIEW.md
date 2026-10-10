# ZC-04 完整Shell正文渲染定点审查

**结论：可见验收BLOCKED，根因UNKNOWN；未建立P0，不可写PASS。** 已看两张原PNG、快照/日志及当前remote/Metal/module_view源码。只读Pillow统计原像素，无截图编辑；未操作GUI、调用remote、启动宿主、编译或点击consent。r2 Host41198bb8来自launch回执，本轮不重验中央构建/Kernel。输入SHA见同名JSON。

## 确认的区别

Calendar status PID13442、窗口w0/1400×807、PNG2800×1614一致。快照模块矩形[54,76,990,603]、month_title=October 2026、status=Your schedule…及日期均有非零布局；日志有os.calendar加载/16686字节Splash eval，未见相关panic/shader error。这证明源码/布局与owner UI只读响应存在，不证明GPU可见或calendar.events/Relay。按dpi2检查整模块ROI[108,152,2088,1358]，2387880像素仅一种RGB(16,19,21)：正文确实没进此PNG，不只是看不清字。

Native PNG不是“全空”：consent说明和Allow白字确实画出，正文深色低对比；ROI有289颜色。该图证明Shell批准层至少部分绘制，但未见可辨认Native正文；consent未Allow时不能据此判定Native获服务失败。两现象不可合并为同一黑屏原因。

## 捕获与渲染路径

remote.rs:909–938在独立macOS使用window drawable，不走CGWindow截图；macos.rs:504–529先处理pending Draw、编shader再呈现，cx_api.rs:2073重paint主pass及child passes；metal.rs:build_screenshot_struct在同呈现command buffer把源texture blit到共享texture并交付pixels。screen.json明确capture_kind=pixels，因此不是读取空CGWindow图。CG onScreenOnly无ownedPID只表示未在其可见集合，不能证明display睡眠，更不能单独解释这个Metal空白。

macos_window.rs:339–347中MAKEPAD_HIDE_WINDOWS只要变量**存在**就不orderFront（即使值0）；--remote则允许无焦点可见。launch回执未完整记录继承该变量，当前visibility未知。module_view.rs:537起画ground，再在实例isolate/clip中draw root；snapshot仅保存CPU widget Area/文字，不验证GPU像素。源码未给出可直接确认的业务根因，禁止先改Calendar协议或批准门禁。

## 最小可证伪检查（本轮未执行）

1. 中央只记录owned launch的HIDE_WINDOWS/NO_FOCUS存在性、窗口all与onScreen/occlusion；不输出全环境，不唤醒或接管用户显示。变量缺省且确实在screen仍空，排除单纯hidden解释。
2. 同一PID/w0连续保存/s、/snap和3帧/gseq；读/shader/consts核对根/正文/批准层颜色、clip及pass。若连续PNG仍纯色而layout稳定，排除仅初帧加载迟到；完整子pass重paint已有代码，不能先归咎“remote只画bar”。
3. 用户自然唤醒后对照实际窗口与同帧/g：glass有正文而/g空→捕获/合成；两者均空→绘制/主题/clip路径；唤醒后均恢复才支持环境关联。此检查无需Allow或模型。
4. 若两者空，再查module root draw list/pass attachment/isolate、背景fill及ShellTokens。Native图Allow文字有而card填充难辨，优先检查批准层主题/填充；不可据此断言已定位shader缺陷。

当前按P1可见交付/可读批准阻塞处理，不是已证明P0权限绕过/数据损坏；没有可信本人批准继续HUMAN_REQUIRED，fixture可继续但不充当真实UI/Relay验收。中文/history/scroll新候选需重新绑定新Host证据，不得覆盖r2旧失败。
