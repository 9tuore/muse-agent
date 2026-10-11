# Calendar → Mail 真实 Splash VM 合成 probe

本次只交 probe 与适配/预期声明，**未执行 VM**，没有新 PASS 报告，也没有重跑 100 项 Node fixture。当前正式 source SHA 为 `0c7f9812cf7319cf5120557ddef7caacfe49326c0dcbc5759e689fcac38ce9eb`，保持不修改。

文件：`calendar_mail_vm_probe.splash`、`calendar-mail-vm-expectations.json`。后者明确标记 EXPECTATIONS_ONLY / NOT_EXECUTED_BY_GPT02，所有 true 都是预期值，不能当作实测结果。中央应核实际 `probe.json` 的完整 check 集合，不能仅把出现的值都为 true 当通过。

## runner 与适配边界

只使用中央已有 `semifinal/tests/run_official_api.py --suite production --probe <本probe>`。当前读到 runner SHA `5c5b6b135387f908b1095aa1a8e9a942837053b6e5e9fbff12281a1cc1044bc8`。它截取正式源码 boot 之前的完整 prefix，仅替换 redraw/mail_redraw/set_page，把 host.request 指向 probe_transport，并沿既有 WIDGET 添加真实 Mail to/subject/body TextInput。没有新增 runner、没有替换 mail_compose_from_agent_calendar/mail_preview/mail_send_confirmed/mail_send_step/mail_compose_before_review/mail_calendar_late/mail_calendar_hold/mail_check_host_status/receipt phases/core 持久化函数。

Probe 在隔离 jail 中设置合成的 user/accounts/project/owner/chat/candidate 和已 verified Calendar 记录；调用原 core_boot_goals/core_boot_activity/core_add_goal、calendar_agent_save/mail_save 实际保存与回读。此 verified proof 是种入的合成前置状态，**不证明真实 Calendar add/get**。scope case 用原 core_upsert_goal 持久化一次版本变化；其他身份/选择变化是 fixture 全局状态。每个 case 独立重置合成 draft 与会话，保留 jail 中的已有动作和目标供最终检查；不是生产恢复操作。

Transport 只允许 runtime.list/mail.compose/mail.compose_status/mail.review_send。late compose 在真实 timer 延迟后改变合成 user_id 再返回 composer；原回调负责留下 UNKNOWN、稳定 Host ID、原 payload 和迟到回执。随后恢复合成身份，仅为原 compose_id 发一次只读 UNKNOWN 查询。普通邮件回归通过原 preview→confirm→compose→review→receipt，review 返回明确取消。响应完全合成，没有实际审阅批准或投递。

## 预期覆盖

- 有效绑定的关联草稿实际保存；recipient 空；goal/chat/candidate/事件证明完整保存；准备/预览无 Host 请求；再打开保留精确手改稿。
- add-only/accepted 未 verified 时拒绝关联草稿。
- 本人已预览之后，matter/user/project/owner/plan version 变化拒绝旧确认，草稿原文保留、无新动作或请求。
- 迟到 compose 真实 timer 回调：保存 `compose-cm-late` / revision=1，draft/action UNKNOWN；独立日志 empty goal/run / revision=0，原 payload 不变；无 review。
- 身份变化与恢复后的 UNKNOWN 均不重发；只读查询精确原账号/compose_id。
- 普通邮件原链取消后 DRAFT/正文保留，action failed。所有目标仍 planned，无 run、整体完成或收件端声明。

完整 check 名称、数量、调用顺序和 SHA 都在 expectations JSON。预期仅 5 次 transport：runtime.list、late compose、原 compose_status、ordinary compose、ordinary review_send；mail.send/model.complete 为 0。Timer watchdog/settle 上限各 100×0.04 秒；失败或超时须保留 runner report/log/state，不替换为预期 JSON。

## 中央执行入口

先核完整 source/probe SHA、协调空闲端口，沿已编译 reference Host 与既有独立 build/out/home/state 执行。示意使用中央路径；out 必须全新：

```sh
python3 official_muse/semifinal/tests/run_official_api.py \
  --suite production \
  --source official_muse/app/source/main.splash \
  --probe official_muse/semifinal/mail_integration/gpt02_recovery/calendar_mail_vm_probe.splash \
  --host build/official-hub-rc2-target/release/muse-calendar-reference-host \
  --host-cwd build/runtime-closure-full-shell-r1/sdk \
  --out build/calendar-mail-vm-new \
  --port <中央协调的空闲端口>
```

离线仅确认 source SHA、runner 替换规则、508 个其他 prefix 函数字节一致、13 个 probe 函数不覆盖生产定义、fixture 函数调用均有当前定义，以及现有三个 TextInput 注入。离线合成执行文本放在 GPT02 ignored build 副本，不写 Bundle 或正式源码；这不是 Splash 解析/执行验证。真实 VM 结果由中央记录，reference VM 通过也不能升级为完整 Host/native/SMTP 成功。
