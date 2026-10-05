# Muse 本轮改进与实测收口

状态：**PARTIAL**。本轮从真实现场继续，未宣称原二十项、第二强模型、同一最终候选邮件整链或正式 App Hub 准入全部通过。

## 当前版本与边界

- 本地分支：`codex/muse-rc-finalization`。
- 已安装应用：**0.3.26-rc27**，产品提交 `17698129`。
- readable SHA256：`96ebb52f70a6cbf2050b14468e2eef2d8334e4cd5c4db18539e43c5bd67b4c05`。
- compact SHA256：`e5461fd7ecc1b32ee0e82019ac478b1f691d5137f18d2ac41a1d7e4f6ecd18af`。
- 实际 Host：`1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`。
- SDK lock：`78a5eef0b1af8eb82cd28e464d5681e6e3b0685e63719207d1a77e4ffdd706d6`。
- 保持 OctoScript/Splash、Makepad、App Hub、manifest capability 和官方存储/权限路径。QQ 登录及既有日历桥是本地最小 Host overlay，不能写成官方上游已接受。
- 在原授权测试资料目录通过真实 App Hub 更新，六份核心文件更新前后 SHA 相同；不替换生产资料，不修改旧独立安装版或稳定 0.3.25，不重写旧 Tag。

## 2026-10-05 傍晚：遮挡、点击及普通问答修复

- **侧栏**：历史列表为滚动条留12px空间。真实原生鼠标点击长标题以及首/尾可见“删除”→预览→取消通过，16个对话与历史保留。A2另有25条生产fixture及独立持久读回；不是实际删除用户对话。
- **Dock**：OctoSense StyleSpec只把自身底部保留高度0改88；其他7种风格逐字节不变。真实SDK几何旧6PASS/2FAIL→新8PASS，新Host增量构建146.43秒与严格验签通过，全SDK12000文件验证。真实Shell1400×809最大化、恢复、再最大化、输入读回通过；Dock顶721、发送按钮底680，保留41px。全Shell Cargo单测被已有launcher命名空间错误阻塞，不能标全套通过。补丁是本地最小宿主扩展，不是官方上游准入。
- **状态问题**：原“日历创建失败…能说已经安排好吗？请解释。”误变创建候选，rc25失败保留。只扩chat_status_question的尾部解释后缀，明确起草/安排/整理和修改候选对照保持。rc26-r1实际3组52条＋10独立读回PASS，当前rc27按字节绑定复用，未重复执行。
- **时间分隔符**：支持常见15:00–15:30及带空格格式；新分支必须含两侧完整时钟。rc26仅加字符后缺右钟2FAIL保留且未安装。rc27同原失败文本及变式实际新34条＋5独立读回PASS，原候选同ID改地点保时间。没有扩大整个legacy parser的通过结论。
- **真实模型**：最终rc27恢复官方GUI的MiniMax M3首选，以原问题单次提交。一次尝试、非估算用量，回答“不能”，保留创建失败、缺系统回执和独立读回三项原因。旧GPT连接845ms及两次attempts2/estimatedtrue均保留，不能证明独立GPT语义通过。
- **安装/恢复**：通过同一资料目录真实App Hub安装rc27，六份核心文件安装及首次Shell重启SHA完全相同；随后真实Chat仅产生预期的新问答，不声称所有文件此后仍无变化。93,304官方tokens逐项等价，local signed check/catalog sequence59 PASS，scan7题未运行独立Reviewer。
- **连接边界**：新签名Host识别已有QQ账号，但当前收信同步尚未取得完成回执；缓存提醒不替代新同步。日历最初not_determined，已请求本人系统允许；最新实际只读检查已显示完整访问，未代点系统决定。原精确合成事件已清理，没有重新创建。

最新证据：`UI_RC25_VISIBLE_RESULT.json`、`UI_DOCK_RC25_LIVE.json`、`UI_RC27_LIVE.json`、`MODEL_STATUS_RC27_LIVE.json`、`RC27_DELTA_BINDING.json`、`local-install-rc27-r1/`；生产fixture报告在`../core_chain/query-boundary-20261005-r1/rc26-status-question/REPORT_RC27.md`。以下rc24及更早节点保留自己的身份。

## 实际改动

### 界面与邮箱

左侧保留对话、邮箱、日历、记忆，次级入口收进“更多”；统一暗色、间距与较柔和卡片。输入区聚焦聊天，结果区可收起，原邮件全文可展开并滚动，技术细节默认隐藏。对话标题保持最多两行、54px 等高和完整原始存储，删除按钮明确可见。没有恢复长期目标产品页。

QQ 登录只输入邮箱地址与**授权码**，展示获取授权码说明，采用 QQ IMAP/SMTP/POP 端口；网络登录使用完整邮箱地址，移除单独用户名。官方窗口实际打开，邮箱同步已成功。Host 两处修改、冻结 SDK、构建和验签记录在 `../packaging/qq-login-20261005-r1/`；22 项串行回归通过，原并行失败保留。

### 记忆驱动安排与卡片安全

安排查询范围与当前来源、最新澄清绑定；精确时间不因无关“菜单任选”扩大整日，软偏好与硬范围相交，浮点时间保持精度。最多两条候选、目标日历、项目/归属、引用有效性和旧候选失效守卫保留。rc20 实际 Card 15 组、101 检查、5 次第二进程恢复通过；没有冒充真实日历替代时段实测。

删除合成日历事件须使用标题中的完整测试 ID。修复前只有前缀/截短 ID 也能预览的失败保留；rc22-r2 15 组、105 检查通过，预览及最终确认共用谓词。

### 聊天

显式起草邮件或日历安排不能再被后段“整理资料”覆盖成 Goal。原失败邮件输入、混合日历和普通整理三组实测共48断言、12独立 payload/schema 检查通过。

普通聊天发送副本中的历史 assistant 用现有 JSON 序列化包装成单字段 `reply`，避免裸文本历史与当前输出协议不一致；原聊天记录、检索筛选、原参数及 Mail/Calendar/Goal 协议保持。rc24 六个窄场景106断言、25独立读回通过，包含引号、实际换行、反斜线和中文。

真实原长问在 rc23 的 GPT/M3 首选均 `invalid_json`，失败未删除。rc24 使用**原问题，不额外要求用户写 JSON**，M3 首选一次尝试成功，回答保留缺工具调用、系统回执和独立读回的原因；一句概括继续一次尝试成功。GPT 首选也有有效回答，但 `attempts=2`、用量为估算，Host 未回报 provider ID，**无法排除 fallback，不能算第二强模型独立通过**。结束时已通过官方模型设置恢复 M3 首选。

独立复核三条实际安全合成回答：语义3/3 PASS，未发现grounding失败；GPT标签项的“按未完成处理”只能作尚未验收的保守处理，更精确是“未确认”。这三条成功不证明历史包装是唯一根因，也不升级旧完整题集。

## 真实日历链

用户指定的 `MUSE-IMPROVE-20261005-1525`，只在“工作”日历操作：

1. 2026-10-06 15:00–15:30，北京时间，地点 Muse synthetic acceptance，创建**一次**，独立 `calendar.get` 全字段核对。
2. 同一 event ID 改为 16:00–16:30，修改**一次**，独立 get 核对新版本与字段。
3. Muse 10月6日日期视图显示真实事件 16:00–16:30。
4. 事件仍存在时重启 Shell：五份核心文件 SHA 不变、两个日历回执、动作身份保持、零重放。
5. 按授权删除**一次**，独立 get 明确 `found=false`；已清理合成事件。

这是 **rc22 的独立 Calendar 真机序列**。rc23/24 只改 Chat 协议及 About 版本，可按源码差异复用受影响范围以外证据；没有把它改名成 rc24 的 Mail→Goal→Calendar→回复同最终整链。

更新前 snapshot 变化导致零点击、驱动误查合并回执字段及日期 widget ID 冲突等原失败均保留，没有重放外部操作。详见 `CALENDAR_LIVE_RC22.json` 和 `ROOT_FAILURES.md`。

## 视觉、Gate 与证据

- 正确可见的官方 card-host：990×539、1400×760、990×380；412×892 实际被桌面限制为412×817，记录实际尺寸，未伪报请求尺寸。
- 六页、长文本、原信全文、草稿编辑、两侧收起、结果页及确认控件可达。合成视觉环境没有点击真实写入。
- rc24 UI 版本文字归一后与已验证渲染段逐字节一致：`UI_RENDERER_BINDING_RC24.json`。
- 官方 tokenizer：readable/compact **93,296 tokens 逐项相等**。
- 本地 stamp/sign/check PASS；scan 生成7题，未运行独立 Reviewer；历史 rc24 本地 catalog sequence56 签名验证 PASS；当前rc27为sequence59。不是正式 publisher/上架。
- 真实 Mail/模型/日历窗口截图放在忽略的私人测试目录；公开证据只含合成内容或哈希。复现包不包含账号、凭据、私人邮件和运行数据库。
- 历史桌面 `Muse-0.3.26-rc24-Intel双机复现包-2026-10-05.zip` 已生成，752,799,640字节，310项内容哈希/链接/执行权限读回通过。Root核对解压文件夹载荷与实际安装rc24一致。适用于Intel/macOS14+，两台接收机仍未实际验收；详见 `DESKTOP_DELIVERY_RC24.json`。

关键索引：

- `MODEL_RC23_OBSERVED.json`：原模型失败与格式控制，控制不替代原输入。
- `MODEL_RC24_REVIEW_INPUT.json`：本轮安全合成回答及实际元数据。
- `../core_chain/query-boundary-20261005-r1/rc24-history-protocol/REPORT.md`：106+25窄域 fixture。
- `../core_chain/query-boundary-20261005-r1/rc23-reply-protocol/REPORT_R3.md`：原混合意图失败的真实复测。
- `../core_chain/query-boundary-20261005-r1/REPORT_RC20.md`：安排范围及恢复。
- `../core_chain/query-boundary-20261005-r1/rc22-delete-preview/REPORT_RC22_R2.md`：完整测试 ID。
- `visual-990-final-r4/`、`visual-narrow-final/`、`visual-wide-final/`、`visual-short-final-r3/`：真实可见前后与交互截图。
- `gate-rc24-r1/GATES.json`、`local-install-rc24/installed.json`：实际冻结与安装身份。

## 未完成项

1. 原二十项仍按完整规则保守为5 PASS / 14 PARTIAL / 1 BLOCKED，新增节点通过不等于整项通过。
2. 同一最终候选的两封来信→项目记忆安排→原事项改期→关联回复到达→恢复→跨对话记忆整链未完成。旧测试信的本人收件核对尚待事实答复；没有点击“本人已核对”或绕过未知投递保护，未新增真实发信。
3. 第二强模型独立语义验收、原冻结题集缺项未完成，不能用“账号已授权”或连接成功代替。
4. macOS 日历窗口可见、从电脑日历外部修改后的刷新、OS 重启及两台接收机实测未完成。EventKit/get 成功不替代这些证据。
5. 同 rc27 真账号两小时稳定驻留与全新完整 clean Host 构建未补齐；沿用历史支持时注明版本。正式隐私/publisher/独立审核/媒体及最终用户摘要仍缺。

本轮仅本地小步提交；未 push、未改公开 Tag、未正式提交 App Hub。没有“排名第一”“完美”“READY”结论。
