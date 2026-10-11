# Mail lifecycle account key fix

2026-10-12。最小生产修复仅 lifecycle.rs 两行：accounts=false 使用 None；accounts=true 使用 Some(account)。signed_out 拒绝和 active_account 精确检查保留；mail_claim_allowed 原字节不变，host_dir/admission/Mail grant 检查保留。manifest、生产标记、凭据未改。

补丁还将原两个测试明确设为 accounts=true，保持其按账号暂停断言；新增一个真实 SDK scratch-home 测试覆盖 device 重装恢复、device 暂停、选择改变及原 admission/host-dir 拒绝。该完整 Shell 测试本聊天**未运行**。

实跑独立 Cargo Rust fixture：before 4/6（device 重装误拒绝及 device 暂停漏拒绝），after 6/6，exit101→0。实际提取两 guard 和 Storage::key/sign_out/sign_in/is_signed_out/installed 源码；Storage state/layout、account_hash、active_account、admission/grant 是明确的合成适配器，save_suspended 无磁盘持久化。不能称完整 Shell/Keychain/SMTP/live 通过。13条 dead-code warnings 是 fixture lib 非测试编译警告，输出完整保留。

独立 owned SDK **定向源码副本**在 build/gpt02-mail-lifecycle-key-r1/sdk；仅含此两个文件，不是假称完整可构建 SDK。Cargo before/after 使用各自独立 target，无中央 target 或网络。SHA 与补丁见 identity.json；源码 drift 拒绝。git apply/check 在新临时仓库通过，after 两文件 SHA 匹配，中央 before SHA 未变。最终 patch 为 zero-context，必须先核 identity 的两个 before SHA，再使用 --unidiff-zero。

已执行：prepare.py --sdk <中央已核SDK绝对路径> --out build/gpt02-mail-lifecycle-key-r1；cargo test --offline --manifest-path <独立before/after Cargo.toml> --target-dir <各自独立target>。精确命令及输出在 rust-results.json/before-output.txt/after-output.txt。

中央应用顺序（**本聊天未执行中央应用**）：核对两 before SHA → git apply --check --unidiff-zero <lifecycle-account.patch绝对路径> → git apply --unidiff-zero <同patch> → 核对两 after SHA。中央后续完整 Shell tests / 串行增量 Host / 同候选 live 待完成；保留原 UNKNOWN，不用此 fixture 将现有发送结果改为未发送或重发。
