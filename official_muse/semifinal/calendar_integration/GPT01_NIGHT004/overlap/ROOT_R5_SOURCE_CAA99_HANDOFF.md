# R5 source caa99 interval preparation

状态 **PREPARED_NOT_RUN**。本聊天仅prepare/只读字节核对；Root负责R5签名打包与真实三例执行。没有VM/Kernel/GUI/Cargo/签名或Root文件改动，也不把R4报告改为R5 PASS。

Root实际产品commit `0c3aa9b1e0574a550f21b93b6d8942cdd2759f35`，实际Main source SHA `caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce`。现场source字节与该commit内Main逐字相同，三个prepared目录中的frozen-main也逐字相同。原正式preparer只把输出jail指向own build；无提取器或fixture adapters改动。

新目录 `/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-native-overlap-prepared-r8-source-caa99/` 未覆盖旧out。每例338 production functions／184 globals。逐函数原始SHA记录在各case的identity.json；三组function/global maps完全相同，共享完整map也提交到R5_CAA99_FUNCTION_SHA_MANIFEST.json。额外直接核对每个SHA与当前Root原函数，所有非adapter函数在反向归一fixture_transport→host.request后逐字相等。

相较R4/source8227的已准备closure，函数集合和global SHA均不变，只有core_boot_goals原函数SHA变化：

- R4：见manifest内changes_from_r4_selected_closure.core_boot_goals.r4_source_8227。
- R5：见同一字段r5_source_caa99。

这一身份核对不把Root此前报告的R4三例20+20+20 PASS用于R5验收。R5实际三例尚未由本站运行。

| Case | 新prepared绝对路径 | executed SHA256 |
| --- | --- | --- |
| same | `/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-native-overlap-prepared-r8-source-caa99/same/executed.splash` | `c5701f5365cc541731a8b1728edf3d78fe93ded4be149ba940f86754790f4555` |
| contained | `/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-native-overlap-prepared-r8-source-caa99/contained/executed.splash` | `5b1c5ecf079363eefdd344f99bd4388e78f82f7cc2bc1690c2f6f8f986e9f07b` |
| adjacent | `/Users/mima0000/.codex/worktrees/gpt01-calendar-history/Agent APP黑客松/build/gpt01-native-overlap-prepared-r8-source-caa99/adjacent/executed.splash` | `e4b35cca882d5650a75e36d4bf3810ebd4e5569c649bb11568c323f7dcb7cbd2` |

入口及compact local-string出口没有改；contained/adjacent前置官方含端点bounded-match仍为1，Main半开区间adjacent conflicts仍应0。same/contained第一次候选query只读并等待独立选择；adjacent query→settle→第二次候选才创建/精确读回。raw History/owner留原parent日志。

Root执行沿用ROOT_R4_INTERVAL_HANDOFF.md的driver参数，改用上表prepared路径、**explicit source SHA caa99…** 与Root实际新R5 signed Main SHA/config。prepare_root_case必须传 `--source-sha caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce --main-sha256 "$R5_MAIN_SHA" --kernel-config "$R5_KERNEL_CONFIG"`；每例全新F，不复制旧Kernel ledger。R5包身份不可沿用R4 a040…。

记录R5_SOURCE_CAA99_PREP_RESULT.json含prepared/identity绝对路径和SHA，R5_CAA99_FUNCTION_SHA_MANIFEST.json含338逐函数/184逐global SHA及byte-equality断言。没有新增SDK、权限接口或改写旧结果。
