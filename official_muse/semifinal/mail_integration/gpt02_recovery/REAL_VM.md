# GPT-02 真实Splash异步回执链（2026-10-11）

固定端口9695，独立worktree/build/out/home/state，MAKEPAD_HIDE_WINDOWS=1，不抢前台。只读中央指定reference binary与SDK cwd，无Cargo/模型/真实Host业务、账号、审批或外发。

结果：before-r3 33/37，四个目标失败：投递前失败仍UNKNOWN，draft/action/run-goal未恢复、没有MAIL_NOT_SENT；after-r1 37/37。前后PID69017/69199均remote_quit、exit0，退出后完整日志无[E]/script time budget exceeded。after日志保留一条527ms Startup ui-hang诊断（非Script错误，本文不证明GUI性能）。

实际生产路径：mail_check_host_status→mail_host_receipt_status（仅修补后）→mail_send_receipt_step分phase→mail_save/core_finish_action/core_finish_run/core_record_event及独立磁盘readback。没有替换这些函数；仅沿原runner替换redraw/mail_redraw/set_page与Host transport。`all_other_functions_byte_equal=true`。

每轮5个case：可靠failed_before_delivery、outcome_unknown、正文错配、revision错配、accepted+receipt。每轮只有5次mail.compose_status；compose/review/send=0。失配UNKNOWN留原draft/action/run/goal；可靠投递前失败恢复DRAFT且action/run/goal failed；accepted不转verified/run completed或收件成功。精确正文、Host compose_id/revision、原action payload、磁盘goals/mail-draft和MAIL_NOT_SENT activity均检查。

Host SHA78ab9efce55cb692552a3566e7b579d2e8c304eadfd6b107c51b2efb027e34db。原源66ea3932…；修补源cc3f17cd…（完整SHA见real_vm_summary.json）。probe SHA3d0868dc226b6a610aadf13367cfb3ccea09fe7f22f9ed0bf76c2f22e7a24121。两个源副本在build/gpt02-receipt-sources-r1，仅副本应用提案；正式main未改。

实际命令（--source前后分别before.splash/after.splash；--out分别before-r3/after-r1，复测需新out）：
```sh
python3 official_muse/semifinal/mail_integration/gpt02_recovery/run_real_vm_chain.py \
 --host '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/official-hub-rc2-target/release/muse-calendar-reference-host' \
 --host-cwd '/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松/build/runtime-closure-full-shell-r1/sdk' \
 --source build/gpt02-receipt-sources-r1/after.splash \
 --probe official_muse/semifinal/mail_integration/gpt02_recovery/receipt_chain_probe.splash \
 --out build/gpt02-receipt-vm-after-new --port 9695
```

wrapper只复用中央现有run_official_api.main，ROOT置为独立worktree；Popen cleanup替换为核own PID后Remote quit，退出后再扫日志，无生产流程修改。模块禁止写pycache。中央runner完整SHA、probe/source/执行源码身份都在每轮report。只有status transport回合是假数据；native fs与真实Splash解析/执行/异步timers/持久化函数均实际运行。

失败保留：before-r1合成compose_id含underscore违反现有校验，未保存draft后fixture读nil；before-r2修正时使用了此VM无array.join的fixture语法，手动核own PID后正常quit，wrapper将外部停止记录unclean。两者不作为产品失败；报告/日志完整保留。最终probe改用合法hyphen case/ID，不减断言。before-r3为唯一产品失败基线，after-r1为修补通过。

证据在evidence/real-vm/：包含四轮report/log、最终前后probe.json/goals.json/mail-draft.json及实际存在的activity.json；均合成数据，无账号/密码。real_vm_summary.json独立核report哈希、调用数、清洁退出及断言数量。

边界：这是实际reference VM的生产函数恢复链，仍非完整r8/统一rc2 Host准入、Muse账号许可、native Person或SMTP验收。此前source→claim幂等检查仍是Node投影fixture，不借本次结果改称Memory真实VM已通过。中央可以将本链结果作为Mail补丁实际VM证据，再在同候选完整Host收口。
