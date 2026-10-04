# 官方契约核对与本地扩展边界

于北京时间 2026-10-04 22:03，通过公开 `git ls-remote` 核实 App Hub main 为 `e014fa9c596cdbd95de5cf9fb2a6b4fc2b781d17`，保存了此 commit 的文档字节/SHA。本地 SDK 仍锁 `e8601b80ce104db2e48208094714bdcffdce6b5a`，没有升级。GitHub API 403 限流失败见 `OFFICIAL_FETCH_FAILURE.json`，随后使用无凭据公开 Git/raw 来源成功读取。

bundle 应保持脚本与资源；原生服务随配套 Shell 集成，不能放进脚本 bundle。[官方交付路径](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/e014fa9c596cdbd95de5cf9fb2a6b4fc2b781d17/docs/DEVELOPMENT.md)

核对结果：现行流程仍为固定最终字节后 stamp、真实截图、再次 stamp、Gate/scan、正式身份确认、签名/签后检查，再提交公开固定 commit/tag 的 Issue。首投可 unsigned，已登记 publisher 的更新要求连续签名；Issue 不等于上架。[官方 Publishing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/e014fa9c596cdbd95de5cf9fb2a6b4fc2b781d17/docs/PUBLISHING.md)

本次原版文档的能力闭合集合未列出 `calendar`；当前本地 overlay 明确增加了该能力。由此推断原版准入可能拒绝本应用，**A4 未运行原版 Hub，不能写“已经拒绝”或“官方准入通过”**。本地扩展 check/scan 必须明确命名，不把其 PASS 替代官方原版兼容。须说明 EventKit 扩展版本、平台和可恢复构建，保留 Calendar 功能，不为过 Gate 删除权限声明。[闭合集合与原生交付边界](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/e014fa9c596cdbd95de5cf9fb2a6b4fc2b781d17/docs/PUBLISHING.md)

公开 catalog 同 commit 快照含 signature 字段、entries 为 0，没有 Muse/开发 publisher 记录；这里只读取公开 metadata，没有密码/私钥或其他作品源码。未执行 catalog 密码学验证，因此不是正式身份/continuity 已核准的证据。见 `OFFICIAL_PUBLISHER_LOOKUP.json`；后续需总控用真实目录锚点和正式 publisher 做完整检查。

当前 RC 材料门禁是用户本轮的 **T01–T20 全 PASS**，覆盖旧草稿的 18/20 门槛。本地尺寸合规、overlay 匹配和资料准备都不提升这个判定。

总控执行建议（A4 未执行，变量必须绑定实际最终路径/身份）：

1. 冻结源码/host/Hub，先保存 unsigned 开发副本进行真实截图；截图采集属于同一最终 RC。
2. 把两张最终 PNG 加入 bundle 与 listing，再 stamp。
3. 对实际最终目录运行 `hub check --allow-unsigned`、`hub scan --packet`；完整输出放在 bundle 外。
4. 根据最终 packet 的原始题目逐题填写答案，保留失败/待补，不借用旧 scan。
5. 本人确认真实 privacy URL、publisher id、正式公钥/连续性或 unsigned 首投选择；不读/输出私钥。
6. 若签名，先 stamp 后 sign-manifest，之后做完整 signed check。任何文件变动都重新走对应检查。
7. 全二十项/材料/准入条件齐备且本人最终确认后，由总控提交最终 bundle commit/tag 和 Submission Issue。

文档与命令形状的依据是上述 pinned 官方版本；本轮未声称本机 CLI 构建身份与该版本相同，也未在 A4 执行 stamp/check/scan/sign/publish。
