# rc49 T19 独立可见验收

结论：**PARTIAL**。实际 990×380 的左侧历史区仅 40 点高，初始画面没有标题/删除按钮，容不下完整的 54 点行。不能将本轮记为 T19 全通过。没有修改产品源码。

| 请求尺寸 | `/s` 实际尺寸 | PNG 像素 | 初始完整标题数 | 结果 |
|---|---|---|---|---|
| 1400×760 | 1400×760 | 2800×1520 | 4 | 本轮交互通过 |
| 990×539 | 990×539 | 1980×1078 | 2 | 本轮交互通过；不满足四条同时可见的解释 |
| 990×380 | 990×380 | 1980×760 | 0 | 历史区域失败；输入/折叠/正文滚动通过 |
| 412×892 | 412×809 | 824×1618 | 5 | 实际尺寸交互通过；未达到请求高度 |

在宽、普通、实际窄窗口中，原生点击首尾标题正确选中对应完整标题；首尾删除预览打开并取消；16 条历史完整标题和内容保留（忽略既有保存逻辑更新的时间戳）。行间距实测 58=源码 54 行高+4 间距，Remote 按钮内部矩形高 48。截图人工核对短标题一行、长标题两行省略和独立删除热区。所有尺寸输入框真实输入/回读、空消息发送校验、左侧折叠/恢复通过；宽度大于 740 的窗口还通过右侧折叠/恢复。长正文滚动前后 RGB 像素不同。窄窗口展开时输入宽 91，折叠后 231；该场景不代表手机适配。

## 确定问题与最小修改边界

复现：运行 `python3 official_muse/rc/rc49-completion-20261006-r1/a2/t19_visible.py 990x380 new-run`；使用冻结 rc49 的 16 条合成对话，打开左栏。`history_list=[12,113,194,40]`，见 `visible-990x380-r1/expanded.png` 和同名快照。

只读定位：冻结 readable-rc49-r2/main.splash 的 8701 行 history_list 使用剩余高度，8714 行历史行高 54，8726 行 shortcuts 采用 `clamp(205px,40cqh,280px)`。这会在矮窗口把历史区挤小。建议主界面 owner 只调整 sidebar 内导航与历史区的高度分配，矮窗口减少导航区占用或收纳导航，并给历史列表留完整行的空间。若“四条同时可见”适用于所有尺寸，需要保留至少四行及分组标题的空间，不能只降低测试门槛。没有替 owner 实施该修改。

## 来源与执行边界

- 基线 branch `codex/muse-rc-finalization`，HEAD `d2b14b24f389f432b5fa7b380d859ae5cf006acc`，候选 rc49/e0eb5d82。
- 原始可读源码 SHA256 `2bad514d69d777fabb9ad2daf2b0aa2862555c2db5c146b22bc635b3b1e70484`。完整生产 payload SHA 由本轮 BASELINE 提供，本测试运行的是可读源加 fixture 注入，不声称运行原始 payload 字节。
- 最终 card-host 为已有签名应用 `.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app`，可执行 SHA256 `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。包归属见 packaging/CHUNK_CARD_PACKAGE_RESULT.json。它不是 Root 当前 Shell 的二进制，因此这不是最终 Shell 全链证据。
- 实测 `--help` 支持 `--bundle/--app-data/--allow-unsigned/--stamp/--size`。Remote 源码及实际 `/s` 均验证 `w[].sz/px/dpi/pos`；`/w` 只有 maximize，没有任意设置尺寸接口。每个尺寸串行启动独立窗口。
- fixture 只增加合成 16 对话/长正文，并将 `host.request` 替换成已有 visual_host；全部账号查询返回空。端口 8517，各 case 独立状态目录；未连接 8493，未读写主 profile，未调用模型、发邮件或改系统日历。每个自建进程均在 finally 关闭。
- 首轮 warm-test card-host 使用 011c81a1…，无焦点截图空白；r2 捕获缺按钮层。保留为无效视觉证据，正式结果使用上述 packaged Host。早期脚本错误也保留：误把按钮 48 当行 54；短标题被过滤造成 116 间距；裁剪标题形成 53 间距；RGBA 差分 alpha 为零误判无滚动。最终脚本纠正这些问题，未把它们算成产品问题。
- 最终四组目录：wide r4、990×539 r1、990×380 r1、412×892 r2。旧 report 不覆盖。证据哈希见 EVIDENCE_SHA256.json；所有 profile/source copies/runtime logs 留本地，Git 只收脚本、报告、快照及合成截图。

原标准依据 ROUND_ACCEPTANCE.md T19（短1/长2、省略、54等高、全文、选择删除热区、4可见 fixture）及 RC_ACCEPTANCE_MATRIX.md 的 16 标题、首尾操作、宽/矮/窄和实际高度限制。本轮不重做视频、不操作真实邮箱/日历、不提高预算、不推送。
