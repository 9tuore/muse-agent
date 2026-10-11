# Native L3父驱动交付

状态 **PREPARED/PARTIAL**，真实Kernel接入和后半程尚未由GPT02执行。生产源固定为中央dabfe65b，不改main。Root报告唯一release Shell binary已编译R5并实际通过组件CRUD/Deny；full signed bundle首轮仍缺真实Mail方法registry，修正由GPT01/中央进行。本目录不删除manifest要求，不绕过admission。

## 中央运行入口

沿用README的prepare/run两阶段。初始 `--probe` 选本目录native_full_chain_probe.splash；恢复选native_restart_probe.splash。恢复轮必须新out，复用初始实际state/mail-state和同一Kernel fixture config。不能复用未完成初始轮而缺checkpoint的状态。

run.py新增四个参数，必须一起显式给出：

```text
--kernel-bridge CENTRAL/official_muse/semifinal/calendar_integration/GPT01_NIGHT004/kernel_bridge/bridge.py
--kernel-test-binary CENTRAL/build/official-hub-rc2-target/release/deps/octosense_shell-72365014b64f3f98
--kernel-binary CENTRAL/build/muse-integrated-0.4.0-rc6-standalone-r2/Muse.app/Contents/Resources/host-runtime/octos-kernel
--kernel-config CONFIG.json
--timeout-seconds 600
```

CENTRAL为 `/Users/mima0000/.codex/worktrees/muse-semifinal-a-20261009/Agent APP黑客松`；含空格路径需正常引用。config按GPT01 CLI_PROTOCOL.md提供fixture_root、signed_bundle、mirror、main_sha256、anchor_public。Root负责建立CENTRAL/build/night-004下带FIXTURE_ONLY的新Kernel root与公开签名候选。anchor_public是Root明确提供的64位公开anchor；父驱动不寻找凭据。当前signed_bundle为Root rc7-integrated-candidate-r1/candidate/bundle，mirror为相邻mirror，main_sha256是签名compact实际e5949844，不填upstream dabfe。

对于compact候选，父驱动核对公开bundle-identity.json（或config显式candidate_identity路径）、upstream SHA、readable SHA、签名main SHA、唯一显示版本替换，并在自己的out调用仓库实际compact CLI重放；压缩结果必须逐字等于公开signed main。当前实际映射dabfe65b→422b5d1d→e5949844已验证，错误signed SHA拒绝；这只是候选源码映射，不是admission/Kernel运行通过。

Root重新签名completion新候选后，重新prepare其实际upstream源码和SHA，config/mirror/bundle必须一起更新，新的Kernel root避免替换已有候选。旧R5 binary若再编译，父驱动每轮复制其实际字节并记录SHA，不混用其他版本报告。

## 实际协议处理

kernel_rpc.py冻结GP01 bridge.py/plan_model.py与实际Shell test binary。fixture.ready必须带正确compact source SHA及固定Kernel56761a9f。每个request_id关联实际reply；父进程仅去除传输method/request_id，is_ok/data/error、历史及回执值不修改。原payload.text/trigger/绑定字段保持；只在父请求增加fixture_tool_plan/fixture_approval，完整原payload和实际发出请求都写kernel-parent-requests.jsonl。

创建plan取原生产prompt的精确add JSON，随后get(id)的id引用实际前一个tool message返回值。改期plan取原prompt完整update DTO，按get旧→update同ID→get新。expected是本人所选并已核验的旧八字段原快照；不把第一次get发现的外部变化替换进expected，真实CAS应拒绝差异。失败tool消息由GPT01实际模型fixture停止，不合成结果。所有历史都来自实际octos.session.history；重启后原Kernel hydrate仅作为独立历史证据，不插入当前Broker回执，不写kernel_persisted。

初始probe执行原Mail读取/Memory/hash、gm_context、chat_add_proposal/chat_apply_proposal、native create。第二封合成cached Mail再经原Memory与chat_add_proposal追加同Goal候选，原select/confirm/history同ID改期，验证旧计划/旧手写草稿失效与正文保留。新Mail只能从生产latest authority创建；fixture只填写独立收件地址及测试ID，再原preview/review/MockTransport/独立收件/verify_received。Goal、Run、完成Memory和Calendar/Mail行动链是必选检查，缺口保持false/FAIL；不调用fixture写完成状态或legacy Calendar direct cap。

恢复probe启动新VM/Mail/recipient/Kernel进程；原Store/owner独立get及原Kernel session hydrate、新chat gm_context、旧chat actionchain均需真实记录。没有完成Memory/Goal仍FAIL；缺checkpoint明确FAIL。后台poll timers保留排队，未声称后台运行通过。

## GPT02实际定向验证

- Python三个文件语法检查通过；fixture plan parser15/15（真实观察到的生产候选作输入，解析与拒绝检查；Kernel/Calendar调用0）。
- dabfe真实CLI VM→实际Mail cached read→生产Memory→实际chat_add_proposal→单一Goal前四检查通过；无Kernel参数时open明确unconfigured、候选blocked、native create false、full_chain NOT_TESTED，无VM stderr。首轮fixture输入缺明确日期时间被生产入口拒绝，后改明确合成原文，旧build日志保留。
- 新进程、空状态恢复probe明确拒绝缺checkpoint，未创建完成/历史，无VM stderr。
- 上述公开候选实际compact重放逐字通过；旧L2 binary6b67963a和实际Mail runtime ba37b915 SHA未变。

kernel-driver-evidence保留10个report/stdout/stderr文件与SHA清单；初始整链、第二封信、真实Kernel回包、实际重启整链尚未执行，不可称全链PASS。源码交付让中央立即接入已编译bridge；completion生产缺口归GPT03，不在本单元改动。
