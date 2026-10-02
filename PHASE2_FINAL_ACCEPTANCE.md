# Muse Phase 2 最终候选验收

日期：2026-10-01 至 2026-10-02（Asia/Shanghai）。状态：**PARTIAL**。

Muse 固定为 **0.2.9**；产品源码提交 `17e63c5`，测试提交 `4729e7a`。报告/索引为后续本地提交，最终文档 HEAD 以 `git rev-parse HEAD` 为准。GitHub 创建和上传暂停，未 push，未评论主办方 issue。

最终主源 SHA-256：`eb0e32778c03ea4cc7e331a63ad9aee7bd36bdf5c541e1ec61d99502199b1489`。bundle BLAKE3：`77e8960d261ffa542b25aba4ec7c66f74b959ee1534053d69e0912b1aac9c5d8`。中途来源字符处理修复后，已重新签名、经 Gate 安装并重跑最终 Chat/Goal/Memory/UI/Restart；旧 0.2.7/0.2.8 证据不计本轮 PASS。

## Definition of Done

| 项目 | 0.2.9 状态 | 证据与边界 |
|---|---|---|
| 1. 同一候选 | PASS | 源码、签名和安装副本一致 |
| 2. Chat 上下文 | TRANSPORT_PASS | 真实 wire 的 role/history SHA 匹配；最后 user 一次，时间顺序正确 |
| 3. Chat 语义或能力限制 | SEMANTIC_LIMITED | A代号回忆、C会话隔离、D重启通过；B回答3147而不是4；未硬编码 |
| 4. Multi Goal | PASS | 3个模型Goal、1个679字符长文Goal；4个独立完成Run |
| 5. model.complete | PASS | 真实Chat和Goal建议，实际停服错误与恢复 |
| 6. Memory字段/来源 | PASS_CORE / PARTIAL | 精确产物hash、更正、固定、墓碑、独立验证器通过；Mail/Calendar来源待实机联动 |
| 7. Activity | PASS_SCOPE | 各Goal创建/批准/写入/读回/记忆各一次，真实模型、错误与重启事件 |
| 8. Calendar CRUD/readback | NOT_RUN | 当前permission=not_determined；等待本人完整访问及创建确认 |
| 9. Mail真实收件 | NOT_RUN | accounts为空，官方Host登录sheet已打开，等待本人登录 |
| 10. Mail真实确认发送 | NOT_RUN | 未发送；不以fixture accepted代替 |
| 11. 收件端确认 | NOT_RUN | 必须本人确认，accepted不等于delivery |
| 12. Mail→Calendar同Goal | NOT_RUN | 连接逻辑存在，最终真实邮件/系统事件/结果/来源链未完成 |
| 13. 两个approval独立 | PASS_LOCAL / LIVE_NOT_RUN | 精确动作/revision核心契约通过；真实双确认待联动 |
| 14. 重启不重复外部动作 | PASS_INTERNAL / EXTERNAL_NOT_RUN | 7文件SHA一致、内部数量不变；外部action为0，不能声称真实邮件/日历防重发已验 |
| 15. 响应式 | PASS_AVAILABLE_DESKTOP | 五次尺寸请求均真发送、切四页、长文滚动、返回输入；高窄被桌面限制为818 |
| 16. Goal/storage/restore | PASS_SCOPE | 批准绑定Goal/revision/result path，真实写入与读回；模型建议先生成再批准存储 |
| 17. hub check | PASS_LOCAL_EXTENSION | 注册真实本地公钥后签名Gate通过；原版仍拒calendar |
| 18. hub scan | COMPLETE / human-review | 最终源七问完整，非上游正式接受 |
| 19. Secret/旧版保护 | PASS_SCOPE | 44份候选源模式扫描无疑似Secret；旧0.3.1严格验签及主程序SHA不变；未读改生产DB |

## 人工节点与下一步

本人完成日历完整访问和官方邮箱登录后，继续此候选：唯一 `MUSE-CALENDAR-FINAL-<timestamp>` 的 create/get/update/get/delete/get，实际邮件读取，邮件→候选日程→本人创建确认→系统事件独立读回→结果与来源记忆→可编辑回复→本人单独发送确认→收件端确认，再重启验证外部动作不重复。不能自动批准创建或发送，不自动重发。

当前账号登录中停止窗口抓取、控件检查；Secret只进官方Host/Keychain。未新增Capability/Provider/Phase 3，不改旧安装包、生产数据或核心架构。

## 仍存在的产品差异

模型/预算明确只读，由OctoSense管理；官方Mail登录sheet英文。旧raw MemoryStore和完整图谱未导入。卡片字体、间距、原生控件仍与独立版有差异；同分钟会话标题可能重复，数据ID隔离已验。UI时间显示使用宿主UTC，与本地时间有8小时差异；日历候选明确使用带偏移的时间和Asia/Shanghai。

[测试报告](PHASE2_FINAL_TEST_REPORT.md) · [证据索引](PHASE2_FINAL_EVIDENCE_INDEX.md) · [Memory对照](MEMORY_PARITY_MATRIX.md)
