# 最终9向量VM入口（未执行）

当前状态：中央Rust组件r2已通过；真实RC2 VM接口仍未执行。旧8d131… reference未重建，旧69 Memory/23 Task ERROR必须保留。

## 现有证据核对

已只读核对`build/runtime-closure-sha256-component-r2/identity.json`：compile_exit=0，组件binary SHA `1b3cdc742d528f085a88355231afe2aebee0d86a73104e25bf4343f92f6ef723`；fullSDK storage源SHA4480b0f5…匹配修订方案。special-file-report.json记录FIFO/目录/symlink各exit0、PASS_REJECTED，外层限3秒。组件文件摘要/1MiB结果由中央记录；不是widgets注册、VM jail或完整Shell验收。

## 复用现有runner

使用现有`official_muse/semifinal/tests/run_official_api.py`的`--probe`入口，不增runner框架。它支持显式host/host-cwd/source/out/port，保存host/source/probe/executed SHA、runtime.log，等待fresh `state/muse-goals/probe.json`，检查checks全部true及runtime errors，停止自己的进程。只合成Host transport；此处不调用任何Host服务。

已修本目录`sha256_api_probe.splash`：定义probe_transport、timeout启动函数及runner所需 `{checks,calls,observations}`，输出`probe.json`。旧裸顶层/digest-probe.json版本已保存在sha256_api_probe.before_runner.splash，不能直接给当前runner使用。

中央单一Kernel Cargo结束、重建实际reference后再调度。示意argv（占位项须用中央已验证真实路径，勿沿旧8d131二进制）：

```text
python3.12 official_muse/semifinal/tests/run_official_api.py
  --host <重建后实际RC2 reference binary>
  --host-cwd <中央已验证该binary的运行cwd>
  --source <冻结研究候选main.splash或其已验证compact副本>
  --probe official_muse/semifinal/mail_integration/sha256_api_probe.splash
  --out build/runtime-closure-sha256-vm-r1
  --port <中央选定空闲端口>
```

runner中的90秒report deadline不保护UI被FIFO卡住后的每项测试；特殊文件另需整个runner进程**外层timeout**，见下节。不要在此聊天启动。

9项主向量：empty/abc/中文原UTF-8、文本65536边界、超限拒绝、非字符串拒绝、file字节与文本hash一致、父目录越界拒绝、不存在文件拒绝。file_same_bytes还核对fs.read前后文本一致，fixture文件不删除，允许独立回读。全部checks=true、calls=[]、runtime errors空且SHA是重建版才可记PASS_VM_FS；仍不是Memory69/Task23或Mail原生审批通过。

## 字节/mtime独立观察

主probe写digest-abc.txt及digest-fixture-ready.json，然后延迟3秒执行摘要。中央在启动前安排独立观察者，等待ready marker，在这3秒窗口记录`state/muse-goals/digest-abc.txt`原bytes、stat.st_mtime_ns及size；probe完成后再记录同三项、要求相同。记录必须标before/after时间、host/source SHA及真实路径。错过before窗口或文件已完成摘要则mtime=NOT_TESTED，不能用摘要相同推断没改mtime。此观察不写目标文件，结束后保留报告、仅清理同隔离fixture。

## FIFO/目录/symlink真实VM补验

另复用同runner，换`--probe .../sha256_api_special_probe.splash`和新out。该probe等待fresh jail中的digest-special-ready.json，最多10秒；中央原生fixture准备器见digest-special-waiting.json后，在**该独立jail**创建digest-fifo（os.mkfifo）、digest-directory和digest-symlink（仅指向合成临时外部文本），全部创建成功才写ready marker。不可指向生产/私人文件，不改runtime权限或配额。

中央给整个runner加外层timeout并清理其owned子进程；超时必须FAIL_TIMEOUT、保存log并终止，不能将无report当拒绝成功。probe逐个尝试fs.sha256_file，只有捕获原生错误才记录3项true；fixture未就绪会记录false，不可将未测当拒绝。无jail、文件上限/写配额另沿既有组件/VM反例，原有path-open竞态不称已解决。

这些是待中央执行的VM入口与观察安排。本轮只写probe和文档，未Cargo/GUI/VM、未改shared framework/main或已有evidence。
