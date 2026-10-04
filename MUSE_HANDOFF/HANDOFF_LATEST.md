# Handoff：日历阻塞修复0.3.25

## Task

用户要求参考Aurora-X日历公开说明，修复尚未解决的日历业务阻塞。基线459b079，分支codex/muse-prelim-stability；无子智能体。

## Changed

允许窗口统一校验与错误候选重分析；同Goal新版本/原ID手动改期；账号缓存不代替宿主授权；单次精确软性放宽、查询和独立系统确认。共用原有函数，未新增运行时、Capability或宿主补丁。此前清理一并集成。

## Tests

实际card-host133/133合成断言；88092 token一致；本地扩展Gate/scan/catalog通过。真实创建/get在0.3.23；0.3.25同ID修改/get、一次完整Shell重启七文件相同、删除/get found=false通过。模型3次相关调用known_usage；新发信未执行。失败及观察器错误原件保留。

## Current

最终0.3.25窗口8484；可读0b16836e、实际payload a44677c4、Host0fd99361。原授权测试资料在新私有隔离副本，源基线未覆盖；来信提醒已恢复，未授权模型分析关闭。

## Remaining

整个项目PARTIAL，5PASS/13PARTIAL/2BLOCKED。第二模型、最终同候选邮件全链、正式材料和电脑重启仍缺。不创建成功Tag或正式发布。详见MUSE_CALENDAR_REPAIR_REPORT.md。

源码修复提交：`5116505`；候选构建时基线为`459b079`，测试与Gate以本报告的精确源码及payload哈希绑定。

公开源码提交：`d1f161752f977ddea811444dc9443dd3e4d6515f`；GitHub同步结果以最终独立读回为准。当前运行候选为0.3.25，旧桌面0.3.22归档仍保留原绑定。
