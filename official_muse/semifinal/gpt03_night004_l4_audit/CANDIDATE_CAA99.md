# caa99 新源码组件复验

2026-10-12 Root明确Main SHA `caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce`。先核对中央实际源码并冻结自有build，再新prepare和新进程运行；本轮 **107/107 PASS**，新证据核对PASS。4场景8阶段；实际SIGKILL、accepted后receipt OS错误、Review cancel、网关50ms截止/250ms迟到回复；新VM只读恢复同ID/payload，不重发。 本次真实截止等待52.467006ms；迟到reply实际入队晚于expired并被丢弃，无转发。

实际闭包：initial-prepare 144函数/65global；restart-prepare 285函数/155global。与8227逐项比较，只有`core_boot_goals`函数摘要改变；其余函数和全部global相同。新闭包来自caa99源码，不沿用旧执行文件，不改旧报告标签。比较见evidence/candidate-caa99-r1/closure-comparison.json。

独立归档位于evidence/candidate-caa99-r1，实际运行位于build/gpt03-night004-l4-audit/candidate-caa99-run-r1。父驱动、原raw、报告、prepared/identity及来源manifest保留；8227/c892旧证据不改。

```sh
python3 -B official_muse/semifinal/gpt03_night004_l4_audit/verify_evidence.py --evidence official_muse/semifinal/gpt03_night004_l4_audit/evidence/candidate-caa99-r1 --source-sha caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce --combined
```

同候选新执行的prepare/run参数与CANDIDATE_8227.md命令相同，只将显式SHA设为上述caa99，输出设全新目录；必须先从实际该SHA源码重新prepare。现成VM/SDK driver/Mail/receiver固定SHA守卫生效，不Cargo/重编译。

仅本组件与合成fixture证据；provider/transport/approval/UI/timer为显式fixture，SMTP0。full_chain_status=NOT_TESTED，真实Host64ms/R5 GUI由Root验证。未改Main/SDK/包/用户profile，无push。
