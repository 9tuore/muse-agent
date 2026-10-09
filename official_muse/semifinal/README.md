# Muse 夜间整改入口

分支 `codex/muse-semifinal-a-20261009`，活动包仍为根目录 `bundle/` 的 rc17。可读源码中的 rc18 变更尚未准入或安装。

## 已验证范围

Mail 使用官方 `mail.compose`、`mail.review_send` 和 `mail.compose_status`，持久化宿主草稿标识和版本；旧动作日志身份保留。宿主可信前台审阅仍必须由本人完成。服务受理与收件核验分别记录。

用户选择 OctoSense 内置日历。旧私有 Calendar Host 调用已从新候选阻止；官方共享工具接入未完成。系统日历适配器只存于 `research/official-device-calendar/adapter.patch`，没有加入默认运行链。

## 可复现检查

```sh
python3 official_muse/semifinal/tests/run_official_api.py \
  --host /absolute/path/to/reference/card-host \
  --host-cwd /absolute/path/to/reference/app-hub \
  --out build/semifinal-mail-new-run --port 8658
```

使用参考 Host 的真实 Splash VM、文件 jail、计时器和应用持久化；只替换 Host transport 及三个渲染函数。所有其他生产函数逐字比对。响应来自合成协议，不能证明新版官方准入、原生确认、真实收件或日历执行。报告保留源、执行脚本、测试器与 Host 摘要。

`evidence/` 保存首轮及修复后的报告，失败记录保留。旧稳定包、旧数据和旧 Tag 不变。

## 中断恢复与冷启动复查（23:35）

`tests/run_mail_restart.py` 在两个独立参考 VM 进程之间使用真实 jailed 文件：先在官方审阅请求处丢弃合成回调，再启动恢复进程。最终 r3 的准备及六种对账变体均通过；精确受理、版本/账号/正文不匹配、未发送草稿及宿主错误分别检查。启动零重发，只读对账一次，原文和 Host ID/revision 保留，未将受理算成投递。前两轮测试支架缺少动态 View render 方法，所有逻辑断言通过但运行报错，仍判 FAIL，报告及错误日志保留。这不代替新版原生 Host 审阅或 SMTP 验收。

稳定 rc17 同源/同旧 Host 20 次完整进程冷启动通过，16 对话、256 条历史、64 条记忆均保留。首内容中位15.20秒，首次交互中位15.74秒；未提高 VM 预算、清空历史或显示空框。前轮操作记录标题先于正文刷新导致过早采样，检查器改为最多15秒等待实际非空且尺寸有效的正文，失败不删除。报告在 `evidence/cold-baseline/`；全部原始捕获归档于本地 `build/semifinal-cold-baseline-raw/`，逐文件 SHA 清单随报告保存，避免重复截图进入源码分发。**仅为 rc17 稳定基线证据，新 rc18 和新官方 Host 尚未通过20次。**
