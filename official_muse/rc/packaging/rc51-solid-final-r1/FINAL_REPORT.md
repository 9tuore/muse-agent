# rc51 完整实包结果

**状态：FAIL_SIZE_LIMIT_CONTENT_VERIFICATION_PASS。**唯一一次实际打包生成完整 ZIP 后，因为超过严格 500,000,000 字节门槛退出。随后对同一个 ZIP 完成独立解压和内容验证；没有重打覆盖失败，不能称符合 500MB。

## 固定输入与产物

| 项目 | 实际结果 |
|---|---|
| 冻结源码 F | a4cf4d9e6cd3ff1067e2821a29d4e5be48d2ad39 |
| 版本 / Gate | 0.3.26-rc51 / gate-rc51-release-r2 |
| compact / Host | ed4874d1 / 1d7d1674，固定输入完整 SHA 在先前预检和本轮验证中核对 |
| 完整源码 | 2180 文件，199506103 逻辑字节，未减范围或删除失败 |
| 源码 tar.xz | 116386480 字节；原源码字节的 58.3373%，缩小 41.663% |
| ZIP | 527708351 字节，超限 27708351 字节；要严格通过至少再减少 27708352 字节 |
| ZIP / 入 ZIP 成员原始字节 | 527708351 / 608510325 = 86.7213%；含压缩源码容器的原始 ZIP 输入，不等于整个项目原文件压缩比 |
| ZIP 成员 | 261；完整源码位于 tar.xz 内，成员变少不表示源码文件丢失 |
| 新外置视频 | Muse-0.3.26-rc51-本轮实录.mp4，2439624 字节，实际新版 rc51 配音实录；没有使用旧 rc49 视频 |

ZIP SHA256：`bbd9da44c1aeece3385f3dac745924c09715fb92d500a27f16a92432cb5496dd`

源码 tar.xz SHA256：`336fcda04efd011d9814a80016ebc9858860240642da42e576ffdcf4105dab90`

视频 SHA256：`5cecf600c6d4a18b0217a0f08f97b76648598a559b1b69cb80b0003375361f21`

视频作为独立文件放桌面；同时它也是冻结 Git 中的文件，所以完整源码 tar 内保留该视频。不能说 ZIP 绝对不含任何视频；外置指可独立观看的交付文件。主 packer 在体积门槛失败后没有生成成功 DELIVERY.json，外置视频随后按已批准输入独立复制并复核。

## 独立验证

在 fresh 本机证据目录下对现有 ZIP 解压，完整恢复源码 tar，已实际通过：

- ZIP 成员允许清单、CRC、逐文件 SHA、大小、Unix mode 和相对 symlink。
- 2180 源码文件的允许清单、SHA、mode 和集合；还原后的整个 stage inventory 完全一致。
- 解压后 `.app` 的 strict deep codesign 验证。
- 解压后 Launcher `--check` 资源验证；没有启动应用界面或模型。
- 解压后本地扩展 Hub verify、check、scan。该检查不是原版 Calendar 准入。

原固定 Host、模型、Gate 和六 bundle 文件与 F 的身份在实际压缩前再次核对。旧 rc49 ZIP 497158213 字节保留，未覆盖。主实际打包一次；盲目重打零次。唯一体积失败和所有已生成文件保留。

## 文件位置

桌面展开文件夹：
`/Users/mima0000/Desktop/Muse-0.3.26-rc51-Intel精简运行与源码-a4cf4d9e-2026-10-06`

超限 ZIP：
`/Users/mima0000/Desktop/Muse-0.3.26-rc51-Intel精简运行与源码-a4cf4d9e-2026-10-06.zip`

新视频：
`/Users/mima0000/Desktop/Muse-0.3.26-rc51-本轮实录.mp4`

桌面另有 `Muse-rc51-打包状态-未达500MB.json` 和 `.failed-size.sha256.txt`，明确区分内容校验通过与体积失败。原始解压副本只在本机 gitignored `.local-state` 保留，不提交包、权重、private 或解压目录。

## 超限构成及最小可选修复

模型 GGUF 在 ZIP 中 329029768 字节；源码 xz 再放 ZIP 后 116415869 字节；其他所有内容合计 82262714 字节。仅这次源码 xz 的再压缩开销为 29389 字节，改成 ZIP_STORED 只能省约 29KB，无法解决 27.7MB 缺口。

下一步由 Root 选择：可以准备可逆的完整运行 payload 与全部源码整体高压封装，使用 macOS 自带 tar 首次展开，继续保留文件字节、mode、symlink、签名和完整清单；或评估更大源码压缩字典。任何方案都要先验证再实际测量，不保证某个 preset 必然小于 500MB。

本轮没有执行这些新方案，没有拆出源码后宣称全项目 ZIP 小于 500MB，没有修改权重、Host、预算、冻结源码内容或运行时。两台接收 Mac 未测；同最终外部业务整链、真实 GPT 通道和原版 Calendar 准入不因包装验证变成 PASS。整个产品仍 PARTIAL。
