# Boot recovery candidate

只供 Root 合入中央 Main 8227 的单函数 patch：`main-8227-boot-recovery.patch`。Root负责新的签包及实际GUI预算验证。该patch不自动合入生产源码。

原Main SHA `8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`；patch后Main SHA `caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce`。现有VM SHA `f48060d9a6f10d6be1148e93afc1819ce583bc69ec80f24a70d41316d28c5351`。

在当前worktree复验（输出目录须全新）：

```sh
python3 -B official_muse/semifinal/gpt03_night004_boot_recovery/verify.py --out build/gpt03-night004-boot-recovery/checks-r2
```

`--prepared`、`--fixture`、`--runner`可指定现有冻结执行文件、原8白名单导出的fixture目录、缓存VM。只读取fixture中的goals主/备份；新state限制在本worktree build。0/1例在自有jail将不参与测试的动作设unknown，128例完全采用生产API输出原字节。所有fs请求严格只允许目标记录和legacy current.json；任何业务Host调用立即拒绝。

重新提取闭包：

```sh
python3 official_muse/semifinal/gpt03_night004_perf/prepare.py --source build/gpt03-night004-boot-recovery/candidate-main.splash --source-sha caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce --probe official_muse/semifinal/gpt03_night004_boot_recovery/probe.splash --out build/gpt03-night004-boot-recovery/prepared-r2
```

RESULT.md区分真实VM功能结果、fixture失败注入与未测Host64ms；evidence/report.json为最终46项结果。
