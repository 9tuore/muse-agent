# NIGHT-004 原始模型 JSON → SDK → Main 机制

2026-10-12 04:14（Asia/Shanghai），GPT03。**本机制3场景54/54 PASS**，补上上一单元L4的“直接注入invalid_output只能证明Main处理、缺SDK原始坏输出解析”边界。没有改Main/SDK/包，没有Cargo、Kernel或GUI启动，HTTP/SMTP/模型费用均0。仅新增自有测试命名空间及本地commit。

## 实际路径及身份

Main固定源码SHA `c892bff3a0148e78727d257acc8bb381258b6b01c3f6dcfb9b4888a0aac22ae4`。从该实际源提取203个生产函数、88个global；除既有7个IO/UI renderer适配与`host.request→fixture_transport`边界外，生产函数逐字相等，identity包含逐函数SHA。执行的是原`send_chat → muse_model_request → model.complete → 原callback`，没有手工填写候选、成功解析结果或终态Action。

实际SDK输入由官方`octosense_appstore::services::dispatch`派发`model.complete`，经原`ModelService/media::dispatch → Request::from_args → ModelHost::complete → wire::parse → accept → Schema/Refusal`。provider仅提供明确合成HTTP响应字节；SDK自行读取其中model content、拆code fence、解析JSON、重试、记账并返回原错误。parent将实际SDK reply原样交给Main。

使用中央已经存在的SDK库，未编译或修改SDK：

- `build/official-hub-rc2-target/release/deps/liboctosense_llm_service-fc8ea196a57e5038.rlib`，SHA **`bb55fd81aad6b606017e19a87681d5fae28fc03af4c702309a883235c0a0fee1`**，运行前后相同。
- 该库的Cargo fingerprint引用的serde_json、llm-config及appstore依赖指纹逐一匹配，选择对应现成rlib。SDK源快照取自实际`build/runtime-closure-full-shell-r1/sdk`；mod/wire/schema/ledger/media原文件SHA和编译库指纹均保存。工作区overlay与该已编译SDK的文件并不全部相同，未把overlay当成运行结果。
- `complete/mod.rs` SHA `79ce9ed937208d8df1dca27110001c7af1c0bc365a4a605c1154b57053d7d2fe`；`wire.rs` SHA `b39678d6ad5252ff99fbeaa828e2f651fcfdce6f65f27125621e6df0fd1d9725`。源mtime早于库；相关文件原字节快照保留。
- `rustc 1.98.1`仅把自有小stdio driver链接到上述现成SDK库，未调用Cargo、改共享target或重建冻结包。driver二进制SHA **`85ccc7cbcc27ce5a29a708fad28f771a4ec452fa75641756f990849320c05c14`**。链接完成本身只记`LINKED_NOT_RUNTIME_TESTED`；以下实际执行才赋予机制PASS。
- 现成VM SHA `f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351`，实际Mail helper SHA `ba37b915b24917be68964c10c38409169b7162489fbd2de22c082a1e05055367`。

## 实际结果

| 场景 | 原始model字节及SDK行为 | Main最终状态 | 检查 |
| --- | --- | --- | ---: |
| `invalid-calendar` | 原始1字节`{`，SHA `021fb596db81e6d02bf3d2586ee3981fe519f275c0ac9ca76bbcf2ebb4097d96`；原Main日程请求的schema由SDK接收。SDK实际尝试2次，第二次request含修复说明；终态Err=`invalid_output: The model's answer was refused twice: it was not valid JSON.` | 原请求finished、原聊天回复error；持久化trace为invalid_output/invalid_json；proposals/Goal/Run/Action/Memory均0。 | 19 PASS |
| `invalid-mail-fenced` | 原始30字节带json code fence但缺闭合花括号的输出，SHA `59b768b01884f6f27f39815928fb49c752e8e876ee5538d7d22c7642770c2f5a`。SDK自行去fence、两次拒绝，返回同一合法Err；没有由parent生成invalid_output。 | 原邮件起草请求finished、回复error，实际chat-sessions.json仍无候选。没有Mail compose/review或发送。 | 19 PASS |
| `valid-control` | 原始合法JSON `{"reply":"synthetic decoded control"}`；实际SDK一次解析成功，返回原Ok及meta；Main原callback显示同一reply。 | 回复success、已落盘；没有候选/Goal/Run/Action及外部效果。此项是合成合法输出对照，不是实际模型推理。 | 16 PASS |

两次坏输出的SDK真实ledger：逻辑call=1、provider attempts=2、fixture token usage=240；合法对照attempt=1、usage=120。该usage来自明确fixture响应，未发生真实付费请求。原始坏model bytes、原始provider外层响应bytes、两次实际SDK发送request、SDK stdio原Err/Ok及Main实际model payload均保留。

执行端在坏输出处进入原聊天的**error**，原请求结束；解析失败发生在候选/执行创建前，因此Goal/Run/Action为0。没有为了满足标签而制造`failed`或UNKNOWN Action，更没有完成Goal/Run/Memory。Main原API确实将两种SDK错误分类为`invalid_json`，原消息和trace已实际落盘。三个场景的Calendar调用、Mail compose/review、实际transport、收件均0。

SDK子进程分别88991/89022/89042，Main VM88995/89024/89047，Mail88994/89023/89045，全部正常exit0。通过条件还包含实际SDK错误、原始bytes一致、真实重试及原Main状态/副作用，不仅检查退出码。

`verify_evidence.py`已另核对原始SDK stdout的Err/Ok与parent转发帧、model字节与provider envelope、两次修复request、已落盘chat/trace及零副作用，PASS；不额外增加54项运行计数。

## 边界与接续

实际过程是已有SDK的服务派发、wire decoder、JSON/schema validator、Refusal formatter、重试/ledger，以及官方VM中的原Main callback和实际文件读写。provider bytes、合成model grant、UI/timer/clock为fixture；只配置显式keyless fixture provider，没有读真人profile或Vault。实际Mail helper仅查询合成账号/收件计数。

这补齐**L4无效原始模型JSON的模拟机制证据**，不代表真人模型、真实网络、完整签名GUI或REAL_E2E_PASS。Calendar overlap由GPT01准备，本单元未重复。L4整体是否收口仍由Root根据该项接收复验及Calendar冲突证据决定。

原107项持久化/计时故障的报告和`14e0384`提交保持原字节；本目录是新单元，没有回写旧报告。Root可直接复用已链接driver运行同c892源码，命令见README.md。

## 2026-10-12 caa99 新执行

54/54 PASS；新prepare/新进程/新归档，只有core_boot_goals摘要改变。详见CANDIDATE_CAA99.md与evidence/candidate-caa99-r1。旧证据不改，Host64ms/GUI/full-chain不计入。
