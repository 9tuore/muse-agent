# 修补指南审计：0.3.13

最终产品 `9a4a496`，宿主补丁 `39d9479`。本轮修复与UI/线程验收通过，真实新来信仍待本人钥匙串节点；整体二十项仍PARTIAL。完整结论见仓库根 `MUSE_FIX_GUIDE_AUDIT.md`。

## 当前候选证据

| 证据 | 实际范围 |
|---|---|
| compact-final.json / token-equivalence-final.json | 可读源1079e80→artifact e52fe5e，75718个官方token及换行标记一致 |
| functional-final/summary.json | 当前生产函数连接12、收信15、对话管理17通过；隔离fs，合成Host |
| visible-990-final/、visible-narrow-final/ | 当前可见card-host具名确认、取消、指定删除、新建及真实进程重启；窄窗实际412×813 |
| mail-visible-final/ | 当前可见新信自动卡/正文/回复按钮与断开卡8项；合成输入，无模型或外发 |
| rust-tests.log / rust-test-binding.json | 匹配源码18通过2ignored；真实Gmail/钥匙串测试未执行，非cargo全workspace测试 |
| patch-replay.json / source-binding.json | Mail补丁在隔离基线重放后与编译源一致；单线程、8项队列、授权复查 |
| host-artifact.json | 实际匹配Release构建与本地adhoc严格验签；非官方上游已接受 |
| live-native-check.json / native-thread-excerpt.txt | 当前真实Shell主线程可响应；钥匙串等待位于octos-mail；无预算错误、四数据hash不变 |
| live-shell-0313.png | 真实Shell当前画面，仅现有合成测试内容；不是新邮件成功截图 |
| check.txt / verify.txt | 本地扩展hub check PASS，签名目录sequence44通过，未远程发布 |

## 失败保留

- before-test.log：旧Mail源码阻塞派发的真实失败。
- functional/：相对路径造成manifest找不到，未运行断言；failure-cause.json区分为驱动错误。
- functional-r2/management/：旧card-host的64ms启动预算失败。
- visible-990/：取消后卡片残留和按钮偏小的真实UI失败，修补后重新运行。
- visible-990-r2/：产品行为已通过，报告驱动误将 `/s` 字节当作对象，完整失败报告保留。
- native-harness-notes.json：实机About未滚到及阻塞进程退出/提前启动的处理记录。

早期 `compact.json`、`token-equivalence.json`、`management-final/` 属于1205e6d前一中间字节，最终以文件名final及e52fe5e绑定为准。没有删除或把失败报告改成通过。未提交fixture bundle或state的副本；这些本地原文件继续保留。

## 宿主复现边界

`mail-ui-worker.patch` 基于已完成中文登录表单与 `mail-sync-stability.patch` 的matched Mail源码。应用前核对 lib.rs SHA256 `bdb01de9125b5f15438133ec4ce513d6eaba4d6b96badb8ab2a8eaff158708a4`，从OctoSense根执行 `git apply --check` 后应用；应用后SHA为 `11f979af5861b339e721b49b49d3ca67b9ec26d8b491da088c7c8d8a5e2a5a92`。本轮实际隔离重放已通过。

构建沿用 `prelim/tests/mail_host_build.sh` 和原locked/offline依赖。配套当前Shell还包含已交付的 `incoming-trusted-module-startup.patch`；仅可信主题/原生能力注册采用可信入口，应用正文/事件仍64ms、深度512。构建时在匹配SDK应用该补丁，结束后原SDK源码已恢复，避免影响别的构建。源码、宿主补丁和成品SHA都要配对，不能把未应用补丁的旧Host称当前版本。

运行包本机路径：`official_muse/app/build/ui-memory-20261003/mail-worker-audit/OctoSense Muse 邮箱稳定版.app`。复用的本人授权测试profile与原账号未导出；钥匙串授权不得自动点击。真实收信、真实投递和日历写入不能用上面的合成测试替代。
