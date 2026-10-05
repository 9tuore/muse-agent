# 精简复现包压缩修复

**实现完成，合成验证 PASS；没有创建真实发布包，没有应用启动验收。** 所有权仅既有 package_lean_portable.py 及本目录。模型、Host、启动器和视频配置没有改变，没有删除源码、Git 历史或旧失败。

## 改动

1. 普通文件通过 Python 3.9 公开 `ZipFile.write(..., compresslevel=9)` 写入。旧路径手工 ZipInfo 配合 z.open 没有继承 ZipFile 压缩等级，此处明确设置 9。目录和运行资源 symlink 的 Unix 类型、mode 及原校验规则保留。文件旧时间戳夹到 ZIP 合法年份范围，不改变内容或权限。
2. 可选 `--solid-source`：完整冻结 Git 允许清单，包括源码和历史证据，以 stdlib PAX tar.xz / preset 6 整体压缩。桌面 stage 源码保持展开；ZIP 排除重复的该源码目录，放入同名 `.tar.xz` 及原逐文件允许清单。不缩小源码范围。
3. ZIP 独立解压后校验成员集合、mode、SHA 和相对 symlink，再从 ZIP 中已校验的允许清单恢复 tar 源码。拒绝多余、遗漏、错 mode、错 SHA、非普通源码类型和逃逸路径；重建后的整个 stage inventory 必须完全一致。新 zip-inventory.json 和原完整 package-inventory.json 分开记录。
4. 教程解释：ZIP 解压后应用可直接运行，无需展开源码；阅读或开发源码时 Finder 双击 tar.xz，或用 macOS 内置 `/usr/bin/tar -xJf`。无需额外安装 Python、Rust、Git 或解压软件。既有应用运行路线和模型初始化配置保持原样。

## 实际测试

```sh
python3 official_muse/rc/rc49-completion-20261006-r1/a3/solid-source/test_packaging.py
```

本机 Python 3.9.6，四个合成源码文件含 Unicode 目录/文件、README、历史 FAIL 记录、可执行 sh；另有合成 runtime 文件及相对 symlink。两模式均实际写 ZIP、检验 CRC、完整读回：normal 7491 bytes，solid 6288 bytes。逐文件 SHA、mode、允许清单和整个 inventory 一致；可执行权限 755、symlink 目标不变，stage 展开源码保留。

所有普通文件通过公开 write 的 compresslevel 实参均为 9；1970 文件时间夹至 1980，内容和权限一致。solid 源码另用 macOS 自带 tar 独立展开，inventory 与原目录一致。这里只调用归档命令，没有启动任何 .app。

五个故障拒绝通过：ZIP 错 SHA、ZIP 错 mode、source 允许清单漏文件、tar 路径逃逸、tar 伪造 symlink。结果见 RESULT.json 和独立 run 结果。每次保留新本地目录；后续失败会写独立结果，不能被下一次通过覆盖。当前没有非预期包装测试失败。收口文档曾有一次 stdin 编码写入失败，另记 DOC_WRITE_FAILURE.json，改用文件补丁保存，没有将该失败记成测试通过。

## Root 接手实包验证

在既有完整 packer 调用中增加 `--solid-source`；其余 commit、version、Gate、evidence 和 model 输入按最终冻结候选，使用全新交付路径。`--help` 已实际显示新选项。原 pack 签名、Launcher 资源检查和 500,000,000 字节严格上限继续执行。

Root 需从最终冻结源码实打并独立验证 ZIP、源码、签名、Launcher 和真实启动。本次没有打 497MB 真包，没有替换桌面候选，**不能凭合成体积保证真实包小于 500MB 或声明成品验收成功**。

完整 Git 源码允许清单、原稳定包、唯一失败和历史均保留；未 push。
