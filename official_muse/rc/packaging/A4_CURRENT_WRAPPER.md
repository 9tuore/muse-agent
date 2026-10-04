# A4 当前入口 · rc9 · 2026-10-05 07:25 +08

本文件是当前打包交接入口。06:20 材料保持原字节：[冻结记录](PUBLIC_MAINTENANCE_FREEZE_RC9_SYNC.json)、[37 项清单](PUBLIC_MAINTENANCE_ALLOWLIST.json)、[当时交接](A4_HANDOFF_CURRENT.md)、[当时薄包方案](THIN_SOURCE_DELIVERY_PLAN.md)。这些历史文件中的“待重测”描述只代表 06:20 时点；本入口不将其改成新版本验收。

## 当前身份和已读证据

应用为 **0.3.26-rc9**，签名应用提交 A = `1c9f3b46e7aac0ee17be385de64c97564651152f`；mirror 为 `official_muse/app/build/ui-memory-20261003/rc9-final-startup-r1/mirror`。可读源码 SHA256 为 `9d01484cb775329530d00f077fb74cfa8469e61ad3117a21360779c4bda13505`，compact payload SHA256 为 `4c970e041bdb8d7726a1ceada2050033445374c3a9e908a873cb36e206d8c5d5`。

A4 当前只读核验：Git/application、Git/source snapshot、mirror 与 pack 的六文件逐字节一致；catalog sequence45/39 entries 的签名核验和 bundle 公钥检查 exit0。当前源码 HEAD 仍为 `862c55e153692647b8699c2c715a0ddf60f1477a`，不是总控声明的最终导出 HEAD。

- [70 次启动摘要](../startup/RC9_STARTUP_70_SUMMARY.json)：30 cold、20 reopen、20 Shell restart 全部通过；摘要文件 SHA256 `cbc7813c17310e639284a72f3e87fe2571d581b29e12cb6febafae9bbeccd70b`。这是实际可见 native Shell 加合成非空数据的逐次检查，未重启电脑，未调用真实模型或 Mail backend。
- [100 次连续应用重开摘要](../startup/RC9_REOPEN_100_SUMMARY.json)：当前已读到 100/100 通过；摘要文件 SHA256 `34dba343eaef4109ea2a18db90c200d0a2f0c7adcda3c7aa28777b57c6e3b95b`。同一 native PID；第1次截图404保留，另行记录第100次最终截图，未重建首次截图。这不代表100次进程冷启动或电脑重启。
- [D05 两模型复测摘要](../startup/RC9_D05_TWO_MODEL_SEMANTIC_REVIEW.json)：受影响的单题由 M3、M2.7 实际 model.complete 后的应用追问通过；M3 class=strong，M2.7 class=unknown。不是完整两模型15题、完整T17或系统Calendar写入，M3提交端404记录也保留。
- 06:39:52 开始的7200秒 r2观察尚未取得终态；约08:00模型复测与约08:40观察收口依总控实际报告，计划时间本身不算通过。原rc9 r1的ENOSPC中断保留：[中断摘要](../startup/RC9_STABILITY_INTERRUPTION_SUMMARY.json)。

A2/A3内部评分70/100、旧20项矩阵5 PASS /14 PARTIAL /1 BLOCKED是总控报告，本入口未重评分。新Host/Calendar T18、接收两台Intel Mac、其macOS版本/电脑重启、正式Hub准入和严格clean仍有缺项。A4未执行GUI、模型、系统权限或账号动作；上述运行结果均来自已读的Root摘要。

## 本轮实际拒绝与快照保全

在当前源码 HEAD `862c55e1`、应用 A 和上述mirror执行 `package_thin_source.py --check-only`：签名静态核验先通过，然后 exit1，明确报 `SOURCE_MANIFEST version is stale`。当前清单仍 version=rc5、product_source_head=b486、files=872；未进入Git archive步骤，未创建ZIP。

06:20:35.053015+08的37项逐文件长度/SHA256再次全部匹配。allowlist SHA256仍为 `326b06f1444782a7a163f15162cbb505a70f600b3908f109400032bb1316fe30`，冻结记录本身SHA256为 `a8e7ec16127abb71a5494cd4294e68e9b164319c219490c7a4b5e883ba10f7e5`。本wrapper是清单外的新增文档；不改历史allowlist，不把它说成06:20的第38项。总控若提交本wrapper，最终SOURCE_MANIFEST必须覆盖它的Git blob。

## 最终 SOURCE_MANIFEST 与导出顺序（交给总控，A4未执行）

导出脚本实际强制检查的三个清单字段如下；任何旧版本、少文件、多文件或SHA不符都会拒绝。

| 字段 | 最终要求 |
| --- | --- |
| `version` | 与 A 的 `official_muse/app/bundle/manifest.json` 完全相等，目前是 `0.3.26-rc9` |
| `product_source_head` | 与 `--application-commit` 完全相等，目前是完整 A |
| `files` | 路径到Git blob内容SHA256的字典；键恰好为最终源码导出commit的全部tracked普通文件，减去 `SOURCE_MANIFEST.json` 自身 |

源文件仅允许Git mode100644/100755；不允许gitlink/symlink、绝对路径/上跳、private/profiles/vendor/target/cargo-home/.local-state路径组件或.gguf。脚本不按工作目录遍历补文件；Git archive的普通成员必须与ls-tree集合/字节/Git blob SHA1/清单SHA256全部相等。tar.umask不作为ZIP权限，ZIP采用冻结Git mode。

1. **先完成所有拟交付的公开改动和报告，再提交它们。** 包括拟纳入的wrapper、最终测试摘要、脚本和HTML模板。保留应用 A 的六文件字节、签名mirror和旧证据。将此提交记录为库存生成提交 **S**。
2. **从S的Git blobs生成清单。** `files`排除清单自身；`regular_file_count=len(files)`、`regular_file_logical_bytes`为这些Git blobs的字节总数。`source_head`和`inventory_generation_head`应记录S，保持现有“清单排除自身；最终export commit另记”的contract。产品源、payload、manifest、dependencies.lock的摘要及验收说明应按当前真实身份更新，不能残留rc5或借用旧Host验收。描述性字段并非脚本全部强制检查，仍须如实生成。
3. **只提交新的SOURCE_MANIFEST，得到最终导出提交F。** 从S到F除SOURCE_MANIFEST外不得再改变任何tracked文件；因此F的其他Git blobs仍与清单相等。不要尝试在清单内写F再提交：会改变F本身。F不等于产品A，也不等于库存S；F记录在导出元数据/最终校验报告中。
4. **总控声明完整F后，先静态检查。** 脚本和HTML从当前工作目录读取，须确认它们与F中的bytes一致。下面命令待总控设定 `muse_export_head` 为完整F后使用；当前未执行：

```sh
set -e
: "${muse_export_head:?Set the coordinator-declared final 40-hex source export commit}"
git diff --exit-code "$muse_export_head" -- official_muse/rc/packaging/package_thin_source.py official_muse/rc/packaging/thin_source_tutorial.html
python3 official_muse/rc/packaging/package_thin_source.py --commit "$muse_export_head" --application-commit 1c9f3b46e7aac0ee17be385de64c97564651152f --mirror official_muse/app/build/ui-memory-20261003/rc9-final-startup-r1/mirror --check-only
```

5. **静态PASS之后重新测容量，仍需总控释放导出。** `--check-only`不检查可用磁盘门槛；对有效清单会生成内存中的Git tar作核验，但不落盘/不写ZIP。薄包预算为F全部源文件逻辑字节（含清单自身）+mirror八文件逻辑字节；实际导出起步要求live free严格大于budget+64MiB+4MiB，每次写文件还要求live free>64MiB+该文件bytes。完整运行包的600MiB门槛不变；历史容量读数不可代替最终检查。
6. **实际导出固定使用同一F、A、mirror。** 获总控释放后才去掉`--check-only`。单ZIP写入，不产生解压stage；旧zip/incomplete.zip不覆盖。全部成员读回长度、SHA256、模式、集合后改名最终ZIP，再算ZIP SHA256并生成`THIN_SOURCE_RESULT_<F前8位>.json`。该后生成报告不回填F；若再做源码改动，需要重新生成库存与导出快照。

现有SOURCE_MANIFEST的 `external_sdk_lock_sha256` 应来自F的dependencies.lock，当前是 `da756dde48232ccc9a3ec642cf206a0872e1731d4f0c0d55b2490de281a810cc`。保留旧runtime provenance：Host938来自b486/SDK lock3f，未含Calendar92b1；不能将源码SDK lock da写成旧Host实际编译输入。

## 用户交付边界

薄包只有签名mirror、冻结源码、离线可点开HTML、身份与文件校验清单；**无Host/Card/Hub二进制、启动器、模型或账号，不是拷过去直接运行的独立包**。目前未创建新的rc9 ZIP，不能宣称已经满足两台接收Mac直接运行。

桌面旧087完整Intel复现包及sha文件保留：`Muse-0.3.26-rc5-Intel复现与源码-0876314b-2026-10-05.zip`，155408912 bytes，SHA256 `127a3ffe0a5343165f659978ec450cecaeeea201467687724e56ec66e521cf17`。该入口仍是rc5，不能冒充rc9验收。A4本轮无归档、编译、删除、模型/UI动作或Git写操作；待总控最终manifest/HEAD及导出释放。
