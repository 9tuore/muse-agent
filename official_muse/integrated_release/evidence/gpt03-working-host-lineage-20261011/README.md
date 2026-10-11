# 工作 Host 血缘与独立重签候选

当前范围：静态真实字节/系统签名验证，以及不启动 Host 的 Foundation fixture。Root 的真实启动已显示413 direct shell执行完整签名inner Host仍黑，不能把本目录当作可见性或业务成功证据。

## 最小候选

原文件：`/Users/mima0000/WorkBuddy/2026-09-28-21-35-00/muse-blackfix/artifacts-rc3/octosense`，SHA `ec83a4f9682f75602b88f7d4cf17d3c8711e7b5034298d848735bafce685594d`。

已生成候选：`/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松/build/gpt03-standalone-sign-20261011/octosense`，SHA `4623caae99142bfd5a2826a86038e17d6860b611b337614bdf0cf5334e5f9a3c`，CDHash `f5ec312ce76f4572a788b97f741a1324add40664`。没有执行这个候选。

对位于 `.app` 外的独立复制件执行以下实际已验证命令；不要覆盖原件，不加 `--preserve-metadata` 或 `--deep`：

```sh
/usr/bin/codesign --force --sign - --identifier org.xinghai.muse.paired-host /absolute/path/to/owned-standalone-copy/octosense
/usr/bin/codesign --verify --strict --verbose=4 /absolute/path/to/owned-standalone-copy/octosense
```

本机 `man codesign` 说明 `--force` 替换旧签名，`--identifier` 设置签名标识；不传 `--preserve-metadata` 时旧签名不影响新签名过程。实际原件严格验签exit1：invalid Info.plist；候选exit0：valid on disk / satisfies its Designated Requirement。原CodeDirectory特殊槽1是inner Info SHA `c09b516a…`，槽3是资源封印hash；候选槽1全零，槽3不存在，槽2保持。详细命令、输出与16个section字节不变证据在 `standalone-sign.json`。

最小真实验证方向是让Root用原WorkBuddy外层Shell及其原状态/资源方式执行这份独立候选，保持Kernel `56761a9f…`。此次更换会改变Host SHA/CDHash，因此不能继续称执行的是原ec83字节；动态SecCode、Keychain授权和可见正文尚未验证。

## 已证实血缘

`ec83…` 是 `build/muse-integrated-history-r1/octosense` 的签名版本，unsigned SHA `30d4d35646591b5aca1d39f912338427362e7c7c478892aab7635ef2d32c5836`。UUID `19aa3b8e-6602-38ef-a004-d6acb3097b13`、16个文件section完全相同。去掉LC_CODE_SIGNATURE、签名blob、8字节零对齐，归一__LINKEDIT大小与load command计数后，整个unsigned文件字节相同，归一SHA `26528fbaff8ea3d11be4a43e7f4a32a6d1974c8a66b93d26ea09de243b9a07e7`。

实际准备源码路径是中央 `build/runtime-closure-full-shell-r1/sdk` 与 `/hub`；target是 `build/official-hub-rc2-target`。完整绝对路径、source checkpoint、patch SHA、锁SHA、命令和helper环境规则见 `lineage.json`。Release/offline/locked、`app-hub,octos-core,app-muse-native-prototype`、packaged资源与remap由History receipt支持。当前packager设置MAKEPAD=apple_bundle、MAKEPAD_PACKAGE_DIR=.、deployment11.0、strip debuginfo以及路径重映射；历史完整继承环境没有记录。

原source identity checkpoint `b8fe503e…` 只是Root仓库提交；SDK/Hub是无独立.git的准备副本。当前记录17源码中10匹配、7漂移；当前target unsigned `aec5…` 不是工作构建，rc2 `f5eb…`也不同。因此不能把当前共享目录或当前rustc cache当作工作Host的完整冻结源码/历史环境。

完整签名inner app静态deep/strict再次PASS。Info SHA、209个资源文件清单（208资源+Kernel receipt）、Kernel与receipt SHA均已保存。`bundle-path-probe.json` 的Foundation fixture证明unsigned外层Shell直接exec嵌套inner时NSBundle.mainBundle指向inner；它不能证明实际Host的安全服务或黑屏原因。
