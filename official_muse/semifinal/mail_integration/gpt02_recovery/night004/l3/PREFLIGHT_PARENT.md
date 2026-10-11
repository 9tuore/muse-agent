# 8227 preflight：原生L3调用适配

2026-10-12 GPT02，**PREPARED_NOT_TESTED**，实际Kernel/VM/GUI/Cargo调用0。已只读核Root正式源并冻结SHA `8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`。Root按此源重新签名并提供实际config；旧c892/cdb运行结果只作旧证据，不计入新源通过。

## 四个初始探针的唯一流程增量

full-chain、update-Deny、CAS、delete的首次候选创建前，新增相同`native_create_preflight()`；随后原`calendar_agent_submit_candidate()`保留，成为独立第二次候选操作。

1. 第一次原生产submit_candidate只产生query。必须turn_completed、binding=nil、实际preflight.status=ready且preflight_current()；UNKNOWN立即使探针FAIL并停止，不进入create。
2. 再读实际history，由原生产preflight_query校验`{"limit":200}`的唯一events回执及身份/digest；独立owner events在前后均为空且相同，Goal/Run/Memory不变。实际history/receipt/owner观察保存到probe observations。
3. 显式UI结清手势仅设置history_settle=true并调用原history；其生产回调完成归档。必须idle、preflight仍ready/current，最后一条previous_request保留原query request/turn及binding=nil。
4. 独立第二次原submit_candidate沿原add/get-only创建，必须request/turn与preflight不同，生产preflight.status为consumed；其余创建核验、改期、Deny/CAS、Mail、删除及完成门禁逐字保留。

full-chain原通用`{}` query和archive仍是另一条独立turn，不把它当候选preflight。preflight只观察生产状态，不赋ready/idle/verified，不stub binding、不补history或receipt。Deny模式下query仍Once，原update才Deny。

## 恢复与准备产物

四个restart probe源码逐字未改；它们原有持久创建/更新/删除及重复确认守卫仍适用。preflight是runtime检查，不在checkpoint中造恢复结果。八个程序均按新8227源重新prepare，非adapter生产函数字节一致。

根为GPT02 worktree的`build/`，各目录含executed.splash、identity.json、frozen-main.splash：

| 用例 | 初始目录 / 函数数 | 恢复目录 / 函数数 |
| --- | --- | --- |
| full-chain | gpt02-night004-preflight-full-prepare-8227-r2 / 277 | gpt02-night004-preflight-full-restart-prepare-8227-r1 / 317 |
| update-Deny | gpt02-night004-preflight-deny-prepare-8227-r2 / 250 | gpt02-night004-preflight-deny-restart-prepare-8227-r1 / 328 |
| CAS | gpt02-night004-preflight-cas-prepare-8227-r2 / 250 | gpt02-night004-preflight-cas-restart-prepare-8227-r2 / 328 |
| delete | gpt02-night004-preflight-delete-prepare-8227-r1 / 238 | gpt02-night004-preflight-delete-restart-prepare-8227-r1 / 324 |

Root也可对相同八个原probe文件用现成prepare.py的--source/--source-sha/--probe/--out在中央新目录重准备；CAS恢复实际文件名是`native_cas_restart_probe.splash`。其他run.py参数和各用例的Once/Deny、state/mail/owner边界沿用KERNEL_PARENT、DENY_PARENT、FAULT_PARENT、DELETE_PARENT。本轮parent/run/plan parser逐字未改。

## 静态证据

`preflight-static-evidence/`：源适配契约33/33、既有parser44/44、八份逐函数/全局identity及manifest。契约将四个新增段移除后逐字比较HEAD原probe，证明其余完整流程保留；四helper相同、四restart未变，8227实际生产query prompt解析为唯一events `{limit:200}`，原text/trigger保留且fixture Once。既有44项parser输入来自中央旧c892实际候选，8227生产prompt在33项中另行核对；未借旧runtime升级新源结论。

保留prepare-r1-path-error：第一次CAS恢复误用了不存在的`native_cas_fault_restart_probe.splash`，实际FileNotFoundError，未进入运行；核现场名称后在新r2目录准备成功。早期prepare目录及全部旧证据不覆盖。本轮未运行Splash VM或真实preflight/full-chain，最终运行结论由Root按新签名候选串行验证。
