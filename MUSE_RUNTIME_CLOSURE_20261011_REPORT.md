# MUSE-RUNTIME-CLOSURE-NIGHT-002

状态：开发中 / PARTIAL。开始北京时间2026-10-10 23:41:52，07:00冻结大改，08:00停止交付。

## 当前十项实况

1. 完整新Host：metadata已成功、Desktop正在实际串行编译；旧稳定Host276b2b68与活动rc17保留。
2. Muse本人ID的Calendar Relay：BLOCKED，组件检查不代替实际调用。
3. 内置Calendar查询/创建/同ID修改/删除：已有组件证据；完整Muse候选尚未验收。
4. Mail compose/review_send/status：应用协议已有；新完整宿主未运行，原生审阅仍需可信本人动作。
5. 行动链：开发源已有真实状态投影；尚未进入活动根包。
6. 根bundle晋级：未进行；rc17原字节保留。
7. 同候选最终20次：未开始；待核心冻结及宿主接通。
8. GitHub：59209a3e已非强制同步开发分支，独立远端SHA相同；main/旧Tag未改。随后未提交的原型和DSL不能称已同步。
9. DSL：开发源已接muse.view/1；Memory+view68、Task23、摘要9、特殊文件拒绝3均在真实reference VM通过；可见行动链DSL三尺寸各9项通过。原失败保留，未宣称完整Host/全链通过。
10. 人工缺项：真实Agent consent及Mail原生审阅，准备具体入口后集中提出；当前先继续隔离实现。

## 单元A：发布布局与便携测试

- 默认publication-layout只检查真实根bundle；--migration显式核对旧别名和可选原字节参考。
- 合法后缀对齐锁定Hub95e4831，允许AGENT.md和skills文本；拒绝原生文件、包内symlink、逃逸资源。
- python3 -m unittest discover -s scripts/tests -p test_release_layout.py -v：9/9，exit0；合成布局含有效PNG，仅校验器测试。
- python3 scripts/check_release_layout.py --migration --out build/runtime-closure-20261011/baseline-layout.json：layout PASS/exit0；原rehearsal签名仍是正式publisher准备的阻塞。
- python3 -B -m unittest discover -s official_muse/semifinal/stability_integration -p test_check_host_log.py -v：10/10，exit0，明确合成。
- 显式读取旧compact refusal与源码timeout目录：PASS_PRESERVED_FAILURE_CHECK/exit0；不是新实机通过。缺产物NOT_TESTED/exit2保留。

## 现场保护与下一步

基线Commit15cc57187358b2ab09c089c5232ef74d4c30d53c；分支codex/muse-pivot-20261010。完整逐文件摘要在ignored build/runtime-closure-20261011/baseline.json；根main.splash摘要90351cba、472628字节（770540是六文件包总量，不是单个源码长度）。不修改旧安装、活动Host、生产数据或既有未提交工作。

下一优先级：完整Shell与真实注册/Relay/consent → 薄Calendar/Mail适配与共享DSL → 同候选冻结、实机验收及20次。上游旧Issue不重复新建或再发组件进度评论。

## 01:08接续：真实构建与新阻塞

- 官方锁定内核b0759a57719fd35b3a2da1c5d969bc67538ed516已取得真实Git对象，release实际编译中；尚无已核验二进制/receipt。首次offline缺wreq失败保存，不称完整Shell已运行。
- 隔离full-shell保留官方Mail/connected_review、OAuth、Model、Kernel、Relay与系统apps。Native原型使用独立muse-native-prototype和新资料目录，已应用3个隔离patch，只授予明确声明的calendar.events查询；不借用muse-goals或os.calendar身份。生成/应用通过，未构建或调用。
- Git传输失败后，从官方OctosCode固定版本归档恢复574个源blob，逐个Git SHA1核对一致；仅精确源路径覆盖，原锁文件留存。Rinx固定版本正在下载，完整Cargo图尚未解析，不称仅缺一项依赖。
- 真实Memory/Task参考VM发现fs.sha256不存在；原错误和fixture缺文件失败全部保留。为新jailed fs准备最小摘要方法，复用官方Rust digest，不增Cargo依赖、不覆盖整个新FS。
- 修订摘要补丁实际应用两目标，full-shell复用open_storage_file/read_storage_bytes，reference先拒绝特殊文件再open。真正提取生产helper与官方digest编译后，abc/1MiB边界和字节/mtime不变通过；FIFO/目录/symlink分别限3秒实际拒绝通过。仅组件证据，未证明VM注册/完整Shell，仍保留TOCTOU边界。
- 共享DSL候选source SHA2253e9f00e8a0a57b713c316db2c40d26e5c937beef54703833a52cdee6cb7fa，compact SHA493e9f4b76fbdbdfef89039911164de6c72ded0f5fc5773987c82bb8e5f96a0d；619382→493020字节。官方Tokenizer实跑104622 Token/97762指令，边界与指令相等、parse_errors=0；映射PASS_STATIC_MAPPING_ONLY。不是准入或业务通过。
- 真实新组件测试：candidate映射11/11、Calendar投影7/7。Mail/Memory边界26项为源码与已有证据审计；本轮未重复外发、调用付费模型或执行日历写入。
- 用户已允许磁盘不足自动清可重建缓存/核验重复产物；01:01可用9.0GiB，不清活动构建、源码、模型、用户资料、稳定包或唯一失败证据。

完整证据在build/runtime-closure-*，当前总体仍PARTIAL。07:00冻结、08:00停止保持。

## 02:07 接续：已取得真实内核与完整依赖图

- 官方锁定Kernel实际release编译exit0（47分15秒），版本octos 2.0.3-rc.13 / b0759a5；官方stage工具exit0，binary/receipt SHA `9c3d4b947a9f90f19acfabad0f90cc891525751d418cb333e6e1d83220c4fb0a`。尚未取得完整Shell运行或Agent工具调用证明。
- 固定Rinx、Cadcraft及11个craft依赖完整源逐blob核对；OctosCode574源blob为明确标注的子集。保留所有Git/archive失败、原锁文件和来源记录，路径覆盖没有删官方依赖。metadata-r10实际成功1710包/41成员，唯一canonical Hub；新Cargo.lock SHA `c87d9f2941e211ef0ab987604fe994b067e044c71aa05d9194ddaa32f00beb05`。
- 有效输入指纹r2 SHA `9f15ae944208f8a6f9dcffb98e5a625dd5b95350c265cb9a3c8f79b14f4a0a54`。框架唯一已知变化为审阅过的jailed FS摘要API；native原型仅独立ID只读events grant，不改身份/可信Person。完整Desktop以app-hub,octos-core,app-muse-native-prototype、offline/locked/release、2 jobs实际编译，共享target只有中央使用。
- 摘要兼容提案不增加Cargo依赖，实际新reference78ab9efc建成；真实VM成功范围与合成截图见共享DSL证据。旧task-focus fixture仍假定同步dispatch，与生产原有50ms拆分不兼容；保留out-of-bounds失败，ZC-03准备最小异步fixture修复，未删除检查或改生产预算。
- 实际自动清理无进程占用的debug incremental，净释放2,818,244,608字节，receipt `build/runtime-closure-20261011/storage-cleanup-r1.json`。未删源码、模型、稳定Host、用户资料或唯一失败证据；02:00磁盘可用7.6GiB，后续编译继续监测。
- 本段没有真实外发、Calendar写入或新增付费模型调用；原生可信Person缺失继续HUMAN_REQUIRED。正式Relay、根包晋级、T18和最终20次尚未完成。
