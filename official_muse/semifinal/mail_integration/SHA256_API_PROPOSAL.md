# 新阻塞：官方RC2 isolate缺摘要方法

真实失败保留：`build/runtime-closure-dsl-vm-r2/run/runtime.log:13` 报 `method sha256 not found on object`，中央Memory VM没有通过，不能用旧Host PASS替代。调用在gm_make_source中的fs.sha256(value)。本专项没有运行新VM。

## 接口事实

实际日志路径指向hub-contract-sdk/makepad；其widgets/src/splash_storage.rs负责isolate的jailed fs，widget_async先移除真实mod.fs再注册该模块。官方platform/script/std/src/fs.rs只见read/read_to_string/write/write_string，且不作为隔离应用的原生文件权限替代。

实际reference版jailed fs与完整Shell SDK的同文件**不是相同字节**，两者都未注册sha256/sha256_file。已查实际脚本/std/host fs入口，没有找到可直接替换的官方脚本摘要方法。不能把Rust hash函数当已存在的OctoScript ABI。

官方Rust `makepad-network::digest::sha256_hash(&[u8])->[u8;32]`存在且已从network公开；widgets到makepad_platform/network重导出已核对。无需新增sha2或改Cargo。仓库sdk-overlays/makepad/widgets/src/splash_storage.rs已有旧配套实现，只提取摘要helper及两注册，不整文件覆盖新FS、不修改现有binary/import API。

这是**配套小型API提案**，非上游原版能力、未被官方接受；保留真实SHA-256及旧来源/墓碑语义，不假hash、不在main里降级到空hash或停掉遗忘验证。

## 最小改动

目标仅所构建Makepad `widgets/src/splash_storage.rs`：加std::io::Read、file_sha256 helper、fs.sha256(text)与fs.sha256_file(path)两个方法。

- text为原UTF-8字节摘要，64字符小写hex；检查已配置root，非字符串/超过65536字节报错。不规范化、更换内容或读取宿主目录。
- file先沿原target→resolve_jailed→verify_no_symlinks；普通文件metadata不得超过原MAX_FILE_BYTES，有限读取MAX_FILE_BYTES+1再次拒超限，真实hash原文件字节。MAX_FILE_BYTES/总jail/entry quota及写入逻辑不改，无网络或新权限。
- 不注册非隔离std.fs，不公开真实root，不借host.request/relay绕jail。两方法是native fs接口，**不是Mail ABI或runtime.list的方法**；runtime.list通过不证明fs摘要存在。

输出 `fs-sha256-reference.patch` 基于reference当前SHA a0f15e96…；`fs-sha256-full_shell.patch` 基于完整SDK当前SHA10abcdcc…。完整具体SHA及提案输出身份见sha256_patch_identity.json。中央完整隔离sdk可能已有别的补丁，须先核对基线/适用hunk；不能跨版本盲套或覆盖整framework。生成器仅写本目录，未apply。

## 最小验证与剩余缺口

已执行：原失败日志与注册源码核对、两个真实Rust摘要实现及重导出存在检查、按各自基线生成diff。**未编译、未运行API、未应用补丁**，patch状态PROPOSED_NOT_APPLIED_NOT_COMPILED。

交付sha256_api_probe.splash为中央候选VM探针（未执行）：空串/abc/中文UTF-8已知向量、64KiB文本边界及超限/非字符串拒绝、文件字节与文本一致、父目录逃逸/不存在拒绝。预期9项，不含真实Mail/模型。中央应以独立jail运行并检查全部bool、无runtime error，避免旧Host代测。

另需原生/隔离反例：无sandbox拒绝；文件1MiB边界、超限/目录拒绝；外部symlink拒绝；hash不改变文件bytes/mtime；quota/entry原测试不退化。旧overlay已有snapshot_digest_preserves_bytes_and_storage_caps Rust范例可复用，但其旧结果不能称RC2新补丁通过。

最终中央重建真实RC2组件/完整Shell，记录framework patch与二进制SHA，再重跑实际Memory更正/遗忘/冲突及新view临界VM。Reference上通过也只能是该VM语义，完整Shell原生Mail仍HUMAN_REQUIRED，不能合并宣称全链。

## P1修订：特殊文件先拒绝（当前补丁取代unsafe-r1）

独立review ROUND2_REVIEW.md指出旧file helper先open再metadata，已有FIFO可能在检查前阻塞UI。此为静态成立的P1，旧版不得应用；未实际FIFO复现，不编造timeout日志。旧两patch/生成器/identity已按`.unsafe-r1`归档，原SHA保留在sha256_patch_revision_history.json。

当前full-shell补丁file_sha256直接调用官方已存在read_storage_bytes；该函数经open_storage_file，在open前symlink_metadata拒绝非普通文件，FD复核后有界读。当前reference补丁在File::open前新增symlink_metadata/is_file拒绝，再保留FD metadata复核、1MiB+1读取及再次上限检查。两个目标仍沿原target/resolve_jailed/verify_no_symlinks，text root/64KiB、quota与真实digest未改，无Cargo依赖变化。此修订不称race-free、不保证并发写入的原子快照；原路径检查/open之间的TOCTOU边界保留。

修订真实执行只含生成及静态检查：reference前置检查顺序/FD复核/限读、full-shell复用官方读、两text上限，以及Python脚本语法均通过。**未应用framework、未Rust编译、未运行FIFO/目录/symlink或VM**。

中央测试交接：将sha256_special_file_tests.rs测试模块追加到对应隔离补丁后的splash_storage.rs，仅在中央指定target串行编译测试binary。随后运行 `python3.12 official_muse/semifinal/mail_integration/run_sha256_special_files.py --test-binary <该测试binary> --sha256 <真实SHA>`；runner先核对binary SHA及精确测试名，再在独占临时fixture建立FIFO/目录/指向合成外部文本的symlink，逐个子进程限3秒（超时kill并记FAIL_TIMEOUT）。无需读生产资料。组件helper拒绝仍不证明VM jail/接口注册；之后中央运行九项VM探针、无root/配额/文件边界与真实Memory恢复。

现补丁SHA：reference `175724609a14816c8f367fef6f83dd065443ad2b872167fca217fb7786d5acb1`；full-shell `e94c06c27326fa1dc0df821bf8a6e1db28c93d9ccbec0c818adb0bf5a61b9371`。适用基线未变，完整身份见sha256_patch_identity.json。
