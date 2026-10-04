# 日历真实只读诊断与原生 JSON 修复

状态：**已复现并修复源码；新宿主集成与新权限下 LIVE 复验待完成**。不是 T18 全链 PASS。

## 实际系统读取

按本人授权，使用原已授权 OctoSense 宿主 `0fd9936126acad3a5c61ac1e7a477ba2c9393d740572ec517472f52da9181047` 查询“工作”日历：2026-10-07 00:00 至 2026-10-10 00:00，Asia/Shanghai。

系统返回 full_access，calendar.list `is_ok=true`，events 为真实空数组，起止与目标日历正确。但是 `truncated` 是 JSON 数字 **0**。官方应用的严格 `is_bool()` 校验拒绝结果，实际界面显示系统查询失败。先前两次找不到范围输入是测试脚本滚动位置错误；随后提交的这次才是实际业务返回错误，全部保留。

另开隔离只读诊断应用，仍使用同一个旧宿主及其系统身份，没有复制凭据、请求 TCC、发信、模型调用或 Calendar mutation。实际响应明确证实错误位于宿主序列化，而不是系统登录或没有读取权限。

- 原始 query SHA：`d0f4056db3d715792d47a9844bd9544e843edddede9d8cbf11cca80edb4d907b`。
- 原始 status SHA：`2f723a62592d12763a9d32e6cc539a3ae44a480389771cc4680e89eb4ff6c2e1`。
- 私有原始响应：`official_muse/app/build/ui-memory-20261003/rc5-calendar-readonly-old-host-diagnostic-r1/private/apps/muse-goals/`。
- 摘要：同目录外 `diagnostic-summary.json`。诊断 source634337a5，不是最终产品source5092becd，不能混算为最终候选实测。

## 原因与最小修复

EventKit Objective-C 桥使用 `@(found.count > limit)`。C 比较表达式的类型是 int，Foundation 把它装箱为 NSNumber 数字，JSON输出0/1。接口契约要求布尔值。

仅将该项改为 `found.count > limit ? @YES : @NO`。应用 `calendar_sync_event_valid`、`calendar_list_events` 的严格校验、权限、范围、截断拒绝、批准和独立读回均不改。不在应用层把任意数字当布尔值，也没有新增服务或第二运行时。

修改位置：`sdk-overlays/octosense/apps/calendar/host-service/src/eventkit.m`，同步到固定 SDK，更新锁内该文件摘要与 OctoSense tree SHA。

## 真实 Foundation 回归

`official_muse/rc/startup/calendar_boolean_serialization.m` 用已安装 Apple Clang16编译并实际运行，无 EventKit 或系统权限调用。独立 JSON 解析检查固定结果是 CFBoolean，并核对count0、100、101边界：

| count / limit100 | 原实现 | 修复实现 |
| --- | --- | --- |
| 0 | 数字0 | false |
| 100 | 数字0 | false |
| 101 | 数字1 | true |

三种对照全部通过，exit0。SDK完整12,000文件验证通过。新SDK锁 `da756dde48232ccc9a3ec642cf206a0872e1731d4f0c0d55b2490de281a810cc`；桥文件 `6c51230d3dab93b2d320bc2f0ad12bfec2d01a1766d74ec862af1e0942261029`。

## 尚需集成与限制

产品Splash入口保持b486/source5092becd不变。旧Host938ba58a的30冷/20重开/20Shell重启已经完成，是此单行SDK修复前的支持证据；新Host必须记录新SHA并重新绑定验证，不能直接覆盖成新Host PASS。先前稳定版UI查询失败及真实Mail soak原生绘制错误均保留。

新宿主实际系统权限not_determined，夜间不替本人授予。待新Host编译和签名后仍需本人在系统窗口授权，才能对最终候选再次读取并执行精确日历写入。当前没有创建、修改或删除任何用户事件。
