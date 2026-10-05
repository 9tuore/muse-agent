# rc51 UI 最终证据索引与字节身份

四个尺寸各有一组有效可见card-host fixture交互PASS，但使用两份**token等价、字节不同**的输入源码。候选产品仍为 **PARTIAL**，原启动失败不删除；本次只整理文档，未重新运行native测试。

| 实际证据目录（相对本文件） | 请求 → 实际 | 输入源码 | 注入后的实际fixture主文件 | 结果 |
|---|---|---|---|---|
| `visible-1400x760-r1/` | 1400×760 → 1400×760 | readable A：5c182b67… | 29e2f10e… | PASS |
| `visible-990x380-r2/` | 990×380 → 990×380 | compact B：ed4874d1… | b39bfc83… | PASS |
| `visible-990x539-r2/` | 990×539 → 990×539 | compact B：ed4874d1… | b39bfc83… | PASS |
| `visible-412x892-r2/` | 412×892 → 412×813 | compact B：ed4874d1… | b39bfc83… | PASS |

每个目录含report.json、remote-status.json、截图与控件快照。普通和窄窗的真实目录分别为 **visible-990x539-r2**、**visible-412x892-r2**。R2三组另有exit-receipt.json，逐次证明退出后8517释放、输入源仍是B。宽窗来自此前r1，不冒充B的新运行，也不统一改写四组source_sha256。

## 完整SHA与token等价来源

- 输入源A：`5c182b67d91182350388b726db64b97dc588be089e9f43951284fa899e0d99f1`。
- 输入源B：`ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da`。
- 宽窗真正载入的fixture `bundle/main.splash`：`29e2f10e8143f85111d7c2871e4b8b683f66e82c28673405be161ffb4d90c5ec`。
- R2三组真正载入的fixture `bundle/main.splash`：`b39bfc8350a49223c86dd40b362640368cc401f3af153539916525c24d2c3495`。
- 四组card-host：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。

输入源SHA指注入前的源码，不能等同于实际fixture载荷。脚本在副本中注入合成16对话与明确标注的合成结果，并将host.request替换为fixture服务。上述fixture主文件SHA本次从各案例实际保留文件重新计算，没有改写文件。

等价证据来自Root保存的 [RC51_TOKEN_EQUIVALENCE.json](../../RC51_TOKEN_EQUIVALENCE.json)：kind=OFFICIAL_TOKENIZER_SOURCE_COMPARISON；readable_sha256对应A，compact_sha256对应B；raw_result为`tokens_equal=true, original_count=98560, artifact_count=98560`。本次只读核对该文件和匹配SHA，未重新运行tokenizer。该证据仅证明A/B的官方token序列相同，**不证明两者字节相同，不比较注入后的fixture载荷，也不替代UI/Host/全链验收**。文件自身SHA已记录在FINAL_SUMMARY.json。

## UI范围与保留失败

有效组均覆盖首尾标题选择、删除预览取消、16条完整标题保存、输入回读、空发送校验、正文滚动、左栏折叠恢复和快捷页面。桌面窗口覆盖右结果栏折叠重开及切页返回后内容可见；窄窗覆盖“结果”独立页面与返回。结果卡明确标注合成显示样本，不算真实执行回执；未进行外部模型、邮件发送或系统日历写入。

`visible-990x380-r1/`仍为输入源A的真实启动未完成：35秒无seed，Remote w为空，根因未定。后续B的PASS不能消除这次失败，也不能单凭一轮UI成功宣称cold稳定或候选全通过。原REPORT.md、R2_REPORT.md及其证据保持原样，最新身份归属以本文件与FINAL_SUMMARY.json为准。

未操作Root8493、未更改源码/Host/预算/脚本/超时，未push。本次native运行数为0；A4 r3已放行，本任务不再启动窗口。
