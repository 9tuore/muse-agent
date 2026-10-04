# 2026-10-05 04:45 · rc7最小问询与错误可观测修复

当前分支codex/muse-rc-finalization；产品0.3.26-rc7，可读92c4838e/compactac689fb0，官方tokenizer91041 tokens完全相等。新改动仅缺日期时提前同时问日期、typed enum-only失败类别trace、官方refused/truncated准确中文提示及版本标签；其他字节逆向恢复与b9cf完全一致，模型payload/预算、权限、Goal、Memory与系统动作没有变更。A2原3FAIL→32PASS，A3 26类别/trace+16提示PASS（都是fixture）。实际rc7模型/启动/长运行将单独检验，不把fixture当真实整链。

b9cf真实Memory更正/遗忘/跨对话和Goal/独立读回/首次Shell重启PASS；b9冷2源码准备124.194ms失败、M3 S02/M2.7 D07服务失败均保留，错误原因UNKNOWN。旧V15合成7200.3s/240样本PASS，只作旧版支持。旧真实Mail5357s绘制层FAIL仍保留。SDK日历桥92b1/锁da756dde尚未进入Host938/旧锁3f；完整新Host/clean重建容量不足，600MiB门禁不变。稳定0.3.25和生产资料保护，无push/tag/正式Hub提交。

# Muse夜间交接

## Task

codex/muse-rc-finalization，保护0.3.25与旧rc5；递增0.3.26-rc6，SDK桥修复92b1df15。

## Result

PARTIAL，5PASS/13PARTIAL/2BLOCKED。原20项不降低。

## Changed

在上述稳定性修复上，Calendar合法澄清状态保留受限上下文，后续明确日期覆盖旧模糊日期，支持只补年月日。作用域/过期记忆/遗忘、确认与防重复保留。readable47c56065，payloadf5cd33b7；Host938/SDK3f未换。

## Tests

旧rc5有70次启动、真实记忆/Goal与重启支持证据，真Mail5357s绘制FAIL保留。日程诊断真实M3五步通过三张候选日期核对，无系统写入；Card澄清147项，日期11变体分源186项，最新五组83项/新进程恢复通过。纯日期首FAIL已修，旧失败不删。rc6 Hub check/scan、90918 Token一致过，最终启动/模型/重启/2h待。

## Commit

本地小步；未push、Tag、正式发布。

## Remaining

最终rc6验证，第二强模型、同候选外部整链、电脑重启、clean构建、新Host/系统权限、正式材料。

## Important Boundaries

fixture不算系统成功；稳定邮件不拼成V15整链；源码桥已修不等于旧Host已集成。晨间队列见根报告。
