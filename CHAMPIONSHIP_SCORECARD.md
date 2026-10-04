# Muse 内部证据评分 · 0.3.26-rc5

**状态PARTIAL；工程自评A 66/100、B 65/100。** 数字是按下述缺项扣分的保守内部估计，不是赛事官方分数、统计评测或真实排名。用户提供的其他AI基准A第一约85、B第一档约88不是同一候选实测；当前证据不足以达到这些目标，不标HARD TARGET或EXCELLENT。

每项使用固定权重；fixture仅计对应守卫/协议的部分支持，不能获得真实动作整链分。长运行尚未完成，新Calendar桥没有完整编译，分数先按缺项计。没有重新读取竞争作品。

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
