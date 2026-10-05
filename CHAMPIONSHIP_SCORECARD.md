# 当前验收与独立内部评分 · rc10

**PARTIAL：原20项5PASS/14PARTIAL/1BLOCKED；A74/100、B73/100。** 两位既有真实聊天分别按原子项权重审阅已保存的证据，没有按95分目标调整。不是官方评分、比赛排名或独立重跑实机。产品A=6fd5b54b；当前完整28输入、70启动/100重开/7200秒合成驻留与本地Goal/Memory节点有各自范围；最终真Mail/Calendar同事项全链仍未过。

| A维度 | 得分 | B维度 | 得分 |
|---|---:|---|---:|
| 任务完成 | 17/25 | 任务实现 | 18/25 |
| 可靠运行 | 15/20 | 可靠性 | 17/20 |
| 人机协作 | 13/15 | 人机协作 | 11/15 |
| 项目反哺 | 10/15 | 官方适配 | 12/15 |
| ROM/系统突破 | 7/10 | 复现交付 | 7/15 |
| 效果证据 | 12/15 | 差异化 | 8/10 |
| **合计** | **74/100** | **合计** | **73/100** |

A最终只把长运行子项1/4调整为2/4，B只把长运行1/4调整为3/4；独立判断不同。241样本合成2h不等于真实账号后端、OS重启或第二Mac。Root资源恢复与后续源码导出发生在评审截点以后，不能自动加分。B此前ENOSPC原子保存失败及其后只做落盘恢复的记录保留。

精确26子项、扣分依据、源码/Host身份、首次与最终截点和实际soakSHA见[内部A](official_muse/rc/memory_model/RC10_INTERNAL_A_REVIEW.md)及[内部B](official_muse/rc/core_chain/RC10_INTERNAL_B_REVIEW.md)。正式发布者、隐私政策、独立Hub reviewer、当前业务视频、完整clean Host及T18尚缺。

---

## 历史评分：以下rc9和更早记录不代表当前候选

# 验收与评分记录 · rc9

当前候选PARTIAL，原20项5PASS/14PARTIAL/1BLOCKED。两位已有真实聊天分别独立审阅公开/合成证据，内部A70/B70；这是保守估计，不是官方评分或比赛排名。审阅截点均未给100重开、2h未完成项目加分；后续新证据不自动抬分。没有95/READY/冠军的证据。

A评阅：official_muse/rc/memory_model/RC9_INTERNAL_A_REVIEW.md/.json；B评阅：official_muse/rc/core_chain/RC9_INTERNAL_B_REVIEW.md/.json。逐小项有分值、commit/文件/测试/SHA与扣分，独立审閱不等于独立运行重测。

## 当前内部 A / B

| A维度 | 得分 | B维度 | 得分 |
| --- | ---: | --- | ---: |
| 任务完成 | 17/25 | 任务实现 | 17/25 |
| 可靠运行 | 13/20 | 可靠性 | 15/20 |
| 人机协作 | 12/15 | 人机协作 | 11/15 |
| 项目反哺 | 10/15 | 官方适配 | 12/15 |
| ROM/系统突破 | 7/10 | 复现交付 | 7/15 |
| 效果证据 | 11/15 | 差异化 | 8/10 |
| **合计** | **70/100** | **合计** | **70/100** |

主要扣分：最终真实Mail/Calendar完整业务链缺失；Calendar桥源码未进Host；原28步骤两模型尚待；clean/电脑重启/第二Mac/ARM和412×892原尺寸未过；正式publisher/政策/实际视频与独立评审缺项。五已过项目与局部实测不填满其余门槛。

## 历史内部估计（V15/b486，不改证据版本）

| A维度 | 上限 | 分 | 已计证据 / commit与文件 | 扣分原因 |
| --- | ---: | ---: | --- | --- |
| 任务完成 | 25 | 14 | b48618ac；RC_FINAL_LIVE_REPORT：3次真实M3跨对话、2次Goal、本地独立读回/首重启；稳定0.3.25真实自发自收 | 同最终候选Mail→Calendar→改期→回复未完成；自由聊天准确性/第二模型未全过 |
| 可靠运行 | 20 | 14 | b48618ac；COLD_START_PROFILE：30/20/20全PASS；f98277d6 core 20fault+3恢复 | 最终合成2h进行中；旧真Mail5357s原生绘制FAIL；电脑重启/clean未过 |
| 人机协作 | 15 | 11 | f98277d6；core_chain/PUBLIC_TEST_SUMMARY：25稿件+6新进程、防重复、过期批准；原生标题本人确认 | 最终真实手写稿/外发确认连续体验待；窄高footer被Dock遮挡 |
| 项目反哺 | 15 | 11 | aacc8d17、852fa951、92b1df15；sdk-overlays与Calendar贡献草稿、真实Foundation回归 | 上游未接受；新Host未完成；没有已合并贡献证据 |
| ROM/系统突破 | 10 | 7 | 官方Splash/OctoSense/model.complete；RC_CALENDAR_READONLY_REPORT真实EventKit读取、真实mail.message | 本地扩展不等于官方原版准入；最终Calendar系统写入链缺失 |
| 效果证据 | 15 | 9 | RC_EVIDENCE_INDEX：原生真实截图、SHA、原失败保留；CHAMPIONSHIP_DEMO脚本 | 无最终实际短视频；媒体不能拼旧版当同链；clean/第二Mac未验证 |
| **合计** | **100** | **66** | **逐项相加** | **不宣称第一/冠军/READY** |

| B维度 | 上限 | 分 | 已计证据 / commit与文件 | 扣分原因 |
| --- | ---: | ---: | --- | --- |
| 任务实现 | 25 | 14 | b48618ac；RC_ACCEPTANCE_MATRIX原20项5PASS/13PARTIAL/2BLOCKED | T17/T18未过；真实日历桥源码修复尚未进入运行包 |
| 可靠性 | 20 | 14 | COLD_START_PROFILE、core故障/首次恢复；原预算保持 | 2h尚在进行；真实Mail原生绘制FAIL；电脑重启未做 |
| 人机协作 | 15 | 11 | 同A的人机边界、两行等高标题、六页短/宽窗口实测 | 同最终外部整链/窄高原尺寸未过 |
| 官方适配 | 15 | 12 | f98277d6/92b1df15；固定五官方SDK、manifest、真实model.complete、LOCAL_EXTENDED_HUB | Calendar/文件摘要是本地扩展；正式publisher/政策/官方准入未齐 |
| 复现交付 | 15 | 7 | A4 CLEAN_ROOM_R2_FINAL_AUDIT：新Git/SDK/CargoHome、12000文件验证、下载完成；暖包严格签名 | 完整clean build受磁盘中止；ARM、第二Mac、92b1新Host未完成；源码与旧运行必须分开 |
| 差异化 | 10 | 7 | f98277d6；来源记忆、同事项原事件绑定/25稿件与102安排fixture | 真实原事件改期链待；概念/fixture不满分 |
| **合计** | **100** | **65** | **逐项相加** | **不等于正式评委评分** |

来源身份：产品b48618ac；Calendar一行修复92b1df15；测试记录f98277d6。详细SHA与失败索引见RC_CODE_FREEZE、RC_EVIDENCE_INDEX。最后soak完成后只按实际结果更新；不能为了目标95而放宽标准。
