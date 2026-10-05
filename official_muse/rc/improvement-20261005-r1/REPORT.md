# Muse 本轮改进与实测收口

状态：**PARTIAL**。本轮从真实现场继续，未宣称原二十项、第二强模型、同一最终候选邮件整链或正式 App Hub 准入全部通过。

## 当前版本与边界

- 本地分支：`codex/muse-rc-finalization`。
- 已安装应用：**0.3.26-rc24**，产品提交 `a6a1f8ba`。
- readable SHA256：`0699524137cda658040a843b5af50b57f406d691f821701032c5279796ba5c98`。
- compact SHA256：`4345edc8ce34eb4f98983537ad602c1f3be87c8b49d9eae6b37ba7ce7bc42b93`。
- 实际 Host：`3de610b8acceeefd722b58a8cc30dbf658ef2280b00c2e834fa2e6c2f0d23925`。
- SDK lock：`64ca58c7b1bb6b622657c223910964f8b4c2000577429a253b7cc73cb80598a0`。
- 保持 OctoScript/Splash、Makepad、App Hub、manifest capability 和官方存储/权限路径。QQ 登录及既有日历桥是本地最小 Host overlay，不能写成官方上游已接受。
- 在原授权测试资料目录通过真实 App Hub 更新，六份核心文件更新前后 SHA 相同；不替换生产资料，不修改旧独立安装版或稳定 0.3.25，不重写旧 Tag。

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
- 本地 stamp/sign/check PASS；scan 生成7题，未运行独立 Reviewer；本地 catalog sequence56 签名验证 PASS。不是正式 publisher/上架。
- 真实 Mail/模型/日历窗口截图放在忽略的私人测试目录；公开证据只含合成内容或哈希。复现包不包含账号、凭据、私人邮件和运行数据库。
- 桌面 `Muse-0.3.26-rc24-Intel双机复现包-2026-10-05.zip` 已生成，752,799,640字节，310项内容哈希/链接/执行权限读回通过。Root核对解压文件夹载荷与实际安装rc24一致。适用于Intel/macOS14+，两台接收机仍未实际验收；详见 `DESKTOP_DELIVERY_RC24.json`。

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
5. 同 rc24 真账号两小时稳定驻留与全新完整 clean Host 构建未补齐；沿用历史支持时注明版本。正式隐私/publisher/独立审核/媒体及最终用户摘要仍缺。

本轮仅本地小步提交；未 push、未改公开 Tag、未正式提交 App Hub。没有“排名第一”“完美”“READY”结论。
