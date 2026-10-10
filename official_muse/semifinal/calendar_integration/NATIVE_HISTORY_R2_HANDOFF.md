# History r2 最小修复交接

**提案待中央审查/编译/测试，非live通过。** native-prototype-history-evidence-r2.patch仍从中文label补丁后的基线生成，替代可选r1 History patch，不能叠在r1上。r1 patch、RESULT、SHA、日志均未覆盖；原三提案文件按回执SHA存入native-history-r1-snapshot/。

已读独立B审查的两项P2，只修以下位置：

- history.rs：turn_id/thread_id仅允许缺省/null，或非空、≤256字节且不含空白/控制字符的字符串；两字段均提供时必须一致。类型错误、空串、超限、矛盾均证据不足；仅turn缺省/null才回退thread。未改Host定义、lane、工具或成功判定。
- lib.rs：History接收显式处理Disconnected；context已关闭/缺失时丢receiver并清last_turn，不展示迟到正文；在途提示“停止可取消”。不新增deadline线程、重试、模型调用、存储、权限或Runtime。

保留原3项解析测试，另加2项：null/同ID合法绑定；双ID矛盾和错误类型/空白/控制字符/超长拒绝。**中央本轮消息报告r1三项以release依赖直接rustc运行通过；不是本任务执行，亦非AppModule或live证据。r2五项均未运行。** 中央完整Desktop r2构建exit0也是既有冻结候选，不含本次待审修复。

r2在本目录临时副本零fuzz检查exit0，应用后与专项源码/Cargo字节一致；旧r1补丁/快照SHA确认保留。详见NATIVE_HISTORY_EVIDENCE_R2_RESULT.json与独立check.log。本人无Cargo、GUI、共享SDK写入；真实History/Relay/Person仍未验证。后续由中央处理，当前待命。
