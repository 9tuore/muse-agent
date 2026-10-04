# 体积整理与提交材料

本目录只提供可审阅的准备工具和草案，不修改产品入口、manifest、listing或生产数据。正式Git和发布收口由总控执行。

- `export_public_source.py`：从已批准公开源码的 `SOURCE_MANIFEST.json` 精确白名单生成 `.tar.gz`，保留许可证、NOTICE、锁文件、vendor、资源、测试及历史失败证据。导出前校验源码，导出后流式回读逐文件SHA256、可执行位和4个内部依赖链接；不读原开发Git历史，不自动构建、启动、Gate、签名或发布。
- `SUBMIT_APPHUB.md`：正式资料草案及尚缺内容，保持整体PARTIAL。
- `prepare_final_delivery.py`：最终候选冻结后，使用`--source-root`、`--bundle`、`--host-app`、`--out`生成流式源码tar.gz和独立速览tar.gz；先用`--plan-only`生成源文件/速览清单与实际payload/Host绑定，不创建大归档。没有SDK新干净构建或全量解压。
- `LAST_HOUR_CONFIRMATION.md`：本人需要一次补齐的4项，以及Root必须自行完成的提交门禁。名称和Support已授权，不重复询问。

本轮输出和完整体积Top20在 `official_muse/app/build/repair-delivery-20261004-115054/thread-delivery/`。公共快照只是0.3.19基线；最终本轮补丁与测试需等总控完成，不能把基线归档当成新版本。

复用命令必须填写实际完整源码HEAD，并使用新的输出目录；工具拒绝覆盖已有输出和向源仓库写入。示例参数结构：

```sh
python3 official_muse/prelim/submit_draft/export_public_source.py \
  --source /absolute/path/to/approved-public-checkout \
  --source-head VERIFIED_FULL_COMMIT_SHA \
  --output /absolute/path/to/new-owned-output
```

`compression_saved_bytes_same_inventory`只比较同一文件清单的原始逻辑字节与压缩归档字节，不表示释放了工作区或Git磁盘空间。已有公开清单中的历史日志不会因通用ignore规则被删去。第三方版权/NOTICE审查边界沿用快照自带的 `THIRD_PARTY_NOTICES.md`，保留文件不代表新增法律审核通过。

## 最终导出接口

`--source-root`指向已有批准公开checkout；`--bundle`是冻结的实际payload目录；`--host-app`是匹配的.app。输出目录必须新建且不在上述三个输入内。最终仍标记PARTIAL，不把归档当作测试或发布通过。

Root增量需显式提供`--change-root`及位于该根目录内的`--root-changes` JSON，不自动将工作区diff、未跟踪文件或private运行目录纳入。结构如下；所有路径相对相应根目录，SHA必须先核对：

```json
{
  "source_head": "ACTUAL_FULL_ROOT_HEAD",
  "files": {
    "archive/relative/path": {
      "source": "relative/path/inside/change-root",
      "sha256": "ACTUAL_SHA256"
    }
  },
  "review_files": ["archive/relative/path"]
}
```

`review_files`可省略，只能选择已批准导出文件。实际bundle替换归档中`official_muse/app/bundle/`子树；若Root覆盖清单在同一路径声明不同SHA，工具拒绝导出。SDK/字体不进速览包，最终媒体只通过本人/Root批准的清单加入，不拿旧图替代final。

路径规则拒绝生产private/profile/state/keys/db、数据库/WAL/私钥/模型权重、文件或父目录symlink和越界/绝对链接。唯一3个已核对的既有上游策略/静态资源路径只在原批准清单且匹配哈希时保留，不能作为Root新增或覆盖的例外。相对SDK链接须仍落在批准源码内部。

`SOURCE_PACKAGE_INVENTORY.json`和`REVIEW_PACKAGE_INVENTORY.json`独立记录选择范围；实际归档成功须有`ARCHIVE_VERIFICATION.json`及回读校验结果。失败残留和缺失验证不能当作完成。原始清单在源码包中保留为`BASELINE_SOURCE_MANIFEST.json`；新的`SOURCE_MANIFEST.json`反映实际文件及Root增量，排除自身哈希。
