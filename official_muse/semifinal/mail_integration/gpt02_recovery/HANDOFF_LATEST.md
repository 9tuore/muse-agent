# Handoff

## Task
GPT-02，codex/gpt02-mail-memory-recovery；正式source0c7f9812。制作Calendar→Mail绑定的真实Splash VM合成probe供中央执行。

## Result
PARTIAL：probe与适配/预期已交，VM执行未做。

## Changed
calendar_mail_vm_probe.splash、calendar-mail-vm-expectations.json、CALENDAR_MAIL_VM_PROBE.md。仅自有目录；正式0c7源码未改。

## Tests
只离线核source SHA、现有runner替换规则及widget、508其他prefix函数字节不变、13 probe函数无覆盖。未执行VM/GUI/Cargo/Node，无新测试结果报告。预期仅5次合成transport、无legacy send或model；完整check集合见expectations。

## Commit
本地提交见最终回复，未push。

## Remaining
中央用已有run_official_api.py/已编译referenceHost协调执行，比较完整预期checks并保留实际report/log/state。

## Important Boundaries
Calendar verified是合成seed，不是真实add/get证明；Mail/core原函数实际路径由中央VM验证。仅UI三函数/transport适配，隔离jail、真实timer/JSON读回。Expectations不是PASS，未真实审批、发送、模型或秘密操作。
