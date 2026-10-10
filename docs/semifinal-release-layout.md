# Muse 复赛发布布局：B 线

本轮仅迁移实际活动的 rc17 应用包、统一有效入口并准备只读发布前检查。没有修改 readable 业务源码、SDK、A 线状态/报告或用户资料；没有 Host 构建、GUI、外部业务动作、push、tag 或发布。

## 唯一应用包

```text
bundle/                                  实际 rc17 应用包（唯一目录）
  manifest.json                          0.3.27-rc17，本地 rehearsal 签名保持
  listing.json
  main.splash
  assets/icon.svg
  screenshots/01-main.png
  screenshots/02-global-memory.png
official_muse/app/bundle -> ../../bundle  相对兼容别名
official_muse/app/source/main.splash     可读业务源码，保持原位置
scripts/check_release_layout.py          只读布局、资源、Git 属性与可选参考字节检查
.github/workflows/publish-app.yml         workflow_dispatch，只读 preflight 草稿
```

迁移源是旧七小时 worktree 实际活动目录 `official_muse/app/build/ui-memory-20261003/7h-live-route-r1/bundle`，不是 Git 中的 rc16 包，也不是 readable 源码。`main.splash` SHA-256：`90351cba7ec5c493befb6673212bfb1aa9639dbfbc2ce28b83e24b98f3e05bdc`。六文件的集合、长度和 SHA 见 [B 线证据](semifinal-release-layout-evidence.json)。旧 rc16 普通文件保留在原 Git 历史，旧固定验收目录、报告和测试中的 frozen 源路径未重写。

`.gitattributes` 使用官方规则 `bundle/** -text`，阻止 Windows CRLF 转换破坏 stamped/signed 字节。当前候选准备脚本的默认源、官方 smoke 脚本的有效入口和 README 指向根目录；不修改历史冻结测试或旧交付生成器。

## 检查与使用

```sh
python3 scripts/check_release_layout.py
# 可选：对已冻结的迁移源按全文件集合、长度与 SHA 再比较。
python3 scripts/check_release_layout.py --reference /path/to/frozen/bundle
# 发布源预检：现有本地签名仍在，因此这一命令目前预期拒绝。
python3 scripts/check_release_layout.py --for-github-release
```

校验器只读 bundle，可选报告必须在包外。PASS 仅指目录/资源/字节规则，不能替代 `hub check/scan`、签名校验、原生 UI 或业务验收。兼容 symlink 在 Git 中是 120000 模式；Windows 需要启用 Git symlink 支持，正式检查始终使用真实根目录。现有签名不能直接在 standalone card-host 中运行；不要为通过检查自动删除签名或重写当前包。

## 发布流程草稿与尚待审查项

App Hub 官方 pin：`18cd41d91b326db199fbed4129484a9ba1a8c63d`。已只读核对 [PUBLISHING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/18cd41d91b326db199fbed4129484a9ba1a8c63d/docs/PUBLISHING.md#github-publisher-provenance)、[SUBMITTING](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/18cd41d91b326db199fbed4129484a9ba1a8c63d/docs/SUBMITTING.md#6-freeze-and-verify-the-release) 与 [GitHub catalog publishing](https://github.com/OctoSense-org/OctoSense-App-Hub/blob/18cd41d91b326db199fbed4129484a9ba1a8c63d/docs/GITHUB-PUBLISHING.md)。应用 publisher 证明与管理员 catalog 发布是两个流程。

草稿中的 `workflow_dispatch` 只检出所选 commit，运行布局检查并打印未发布状态。仅有 job 级 `contents: read`，没有 Secret、`id-token: write`、`attestations: write`、`contents: write`、自动 push/tag trigger 或发布动作。Checkout 的精确 action pin取自已读取的官方 App Flow `tools/publish-app.template.yml`；模板来源与哈希保存在 B 线证据。2026-10-10 曾因当前 OAuth 凭据的 workflow 权限限制将草稿临时移到文档目录；本人随后明确要求申请该权限并保留工作流，因此原字节恢复到工作流目录。尚未执行 Actions 或正式发布。

正式应用证明要求公开仓库的 **tag-push** 身份，不能用手动 dispatch 签名冒充。待 Root 审查当前业务、最终版本、可编辑包、publisher 延续及截图后，另行授权安装/审查官方 tag workflow；所需写权限也在该步骤明确审查，不在本轮补填。现有 `muse-local-rehearsal` 签名保持原字节，不能自动 strip/sign/restamp；本轮不判断其公共 catalog 身份或迁移资格。

官方正式 native 命令顺序如下，**仅流程说明，本轮未执行**：

```sh
hub publisher-prepare bundle --repository OWNER/REPO \
  --repository-id REPOSITORY_ID --owner-id OWNER_ID \
  --workflow .github/workflows/publish-app.yml \
  --tag vVERSION --commit IMMUTABLE_GIT_SHA \
  --out build/octosense-app-manifest.json
# 官方 tag workflow 使用 actions/attest 对上面的 canonical manifest 生成证明。
hub publisher-attach bundle --attestation build/publisher-attestation.sigstore.json
hub publisher-verify bundle
hub publisher-pack bundle --out build/app.bundle.pack.json
```

这些 placeholder 不能作为实际发布输入；未填仓库/owner numeric IDs，未生成证明或 release pack。正式 workflow 的 trusted toolchain 应由 Root 按已核对官方版本再审查固定，不沿用本机旧 SDK 假称 publisher 命令可用。

最终下载的 pack 还需独立 `publisher-unpack`/`publisher-verify` 与实际 Host 验收；成功 Release 不等于 App Hub 申请、审核或收录。提交 issue、管理员批准和 catalog publication 按官方独立流程执行，本轮均未发生。

## 本轮实际验证

- 六个文件/资源的集合、长度、SHA与实际活动rc17源包全部一致，根目录和别名指向同一目录。
- 真实staged Git checkout启用core.autocrlf=true后，六文件字节仍相同；别名以120000模式签入并正确解析。
- 校验器拒绝字节篡改、缺失listing资源、重复旧目录、经别名向bundle写报告，以及直接对当前sealed源准备GitHub发布。
- Ruby Psych解析workflow YAML，确认仅workflow_dispatch、精确checkout pin、仅contents:read，无发布job；Python编译及shell语法检查通过。没有运行构建/启动脚本或宿主。

完整布尔检查和源包哈希见B线JSON证据。以上是布局/拒绝行为验证，不是官方Gate或业务执行成绩。

## B 线交接

基线 `9b247c892ee61cf3100560453c5b8496e9061fd3`，独立分支 `codex/muse-semifinal-b-layout-20261009`。只做布局与路径/草稿检查，A 线随后 Mail 修改不包含在 rc17 等字节迁移证明中。Root 可审查本地 commit 后 cherry-pick；不要把本轮静态 PASS 作为新的业务或发布通过。
