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
