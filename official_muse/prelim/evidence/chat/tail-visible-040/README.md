# 新消息必定可见（0.3.16）

日期：2026-10-03 19:30–20:20 · 用例 `official_muse/prelim/tests/chat_tail_visible.py`

## 要解决的问题

「发出新消息后应该能直接看到新发的消息」。0.3.15 只做到了「发消息不再弹回第一条」，
但如果你原本滚在看更早的位置，新气泡仍会落在可视区下方。

## 这个运行时为什么不能直接滚到底

翻过锁定构建的源码（`makepad-splash-budget`）：

- 脚本调 `ui.x.y(...)` 最终走 `Widget::script_call`。`View` 只应答
  `set_visible` / `is_visible` / `render`；`Widget` 只额外给
  `set_visible` / `visible` / `set_text` / `text`。全仓库没有任何
  `live_id!(set_scroll_pos)` 之类的脚本入口 → **脚本滚不了**。
- `ScrollBar.scroll_pos` 是 `#[rust]` 字段（`widgets/src/scroll_bar.rs`），
  `Apply::Reload` 不清它，脚本也写不了它。
- 但它在**每帧绘制**时会钳位：

  ```rust
  self.view_total = view_total.y;
  self.view_visible = view_visible.y;
  self.scroll_pos = self.scroll_pos.min(self.view_total - self.view_visible).max(0.);
  ```

  也就是说：**内容装得下时，偏移量必然是 0**；而「以最新一条结尾的列表」的 0 偏移，
  正好就是最新那一条所在的位置。

## 改法

不再试图去命令滚动，而是让**尾部一定装得下**：

- `chat_window` 数组只装最近几条消息，`chat_list` 渲染它而不是 `messages`；
- `chat_window_tail_start()` 从最新一条往回累加估算高度，装不下就停；
- 每条消息**必然保留**，即使它自己就比面板高（那种情况只能手动滚，保持今天的退路）；
- 消息数变化时（发消息、回复到达、切换对话）`chat_window_sync()` 重新贴到尾；
  翻页不改消息数，所以翻回去的人不会被拽走；
- 顶部给「↑ 更早的 N 条 / 回到最新」翻页行；
- `align: Align{y: 1.0}` 让窗口短于面板时贴着输入框，而不是浮在标题下面。

因为面板里内容装得下，ScrollBars 的钳位会把任何残留偏移归零 —— 连「先滚过再发消息」
这种顺序也不会把新消息留在屏幕外。

## 实测（真窗口 card-host，990x546，合成宿主，隔离 app-data）

窗口尺寸就是 Shell 里那张卡的实际尺寸，所以面板与真机一致：**510x405**。

| 阶段 | 面板里画出来的行 | 是否在面板内 |
|---|---|---|
| 14 条种子消息 | `chat_tail 合成消息 13 / 十三`、`14 / 十四` | 都在（末条底边正好落在面板底边） |
| 点「↑ 更早的 12 条」 | `5 / 五`、`6 / 六`、`7 / 七` | 翻页可读到更早内容 |
| 点「回到最新」 | 回到 `13`、`14` | — |
| 发送「chat_tail 发送测试」 | 你 / `chat_tail 发送测试` + Muse / 回复 | 都在 |
| 回复到达后 | 发送的那条**仍在屏幕上** | 都在 |

`report.json` 里 `failed: []`；`runtime.log` 无 `[E]`。

## 已知取舍（如实记录）

面板只有 405pt 高，而真实消息最长 268 字（≈8 行、224pt）。所以尾部窗口通常只有
**最后 1–2 条**（正好是「你刚发的那条 + 回复」）。要看到更多历史必须用顶部翻页行 ——
面板装不下就是装不下，应用侧无法凭空变高。想在同一块面板里多显示，只有改气泡本身
（把用户气泡里 32pt 的「记住这条」挪进角色行、缩小内边距）或者把窗口做大。

## 与旧用例的关系

`official_muse/prelim/tests/chat_scroll_visible.py` 在本版被移除：它断言的是
「发消息后滚动位置保持不变」，那正是本版**故意**要改掉的行为（现在会主动贴到尾）。
它的意图由 `chat_tail_visible.py` 接管，且断言更强（直接量控件矩形是否落在面板内）。
