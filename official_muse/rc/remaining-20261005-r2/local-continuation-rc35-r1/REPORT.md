# GitHub撤回与本地续测

## 状态

**PARTIAL；新版停止公开。** 当前本地产品 `522ad4954d5cb8a5f094d5b637a81f20c69baf81` / **0.3.26-rc36**，8493真实Shell已回到Chat。

## GitHub

按本人明确要求，用目标SHA和精确force-with-lease把 `9tuore/muse-agent/main` 从 `bce33551` 恢复到本轮同步前的 `39e2b20d992bea5e856fe93bc97702650a37c487` / rc27。GitHub API和后续ls-remote分别读回相同SHA。没有回滚本地代码、移旧Tag或删除历史测试。后续只做本地提交，旧自动push指令被覆盖。

恢复的是主分支指向，不能承诺清除已经公开过的对象URL、缓存或他人副本。记录：PUBLICATION_HOLD.json。

## 真实续测

| 项目 | 实际结果 | 范围 |
| --- | --- | --- |
| rc35重启后原问题 | 真实model.complete成功；strong、attempts1、已知用量，回答正确区分“打算导出”与执行证据 | 本轮一次未复现旧失败；不是根因修复证明 |
| 模型用量 | ledger46→47；input764/output43，累计63942 tokens | 官方token账本，不是人民币账单 |
| 日历刷新 | 选择工作，刷新后真实calendar.list回调显示范围加载完成 | 只读，不代表写入或delete/get |
| 日期打开 | 以实际日期Button准确定位后打开表单 | 旧Remote.find('6')错误匹配星期Label的id=6；原失败保留 |
| rc36表单返回 | 返回按钮移至固定标题；表单滚动1200后矩形不变、可点击；返回后表单和返回按钮隐藏 | 真实Shell UI；goals/actions和模型ledger不变，无系统写操作 |
| AppHub安装 | 权限页真正“安装”按钮点击一次；六bundle文件SHA与候选一致；七资料文件及ledger保持 | 本机已授权候选更新；不是正式上架 |

原始driver失败保留：R1误读不存在actions.json，R2在滚动顶部查找不到原内嵌返回控件。AppHub前两次Update只进入权限页，尚未安装；RC36_INSTALL记录后续实际确认安装，未把初期观察覆盖掉。CALENDAR_READ_FORM_R1的空字段和false日期标签不得计为PASS。

## 最小修改和候选身份

- 可读源码 `f9b3a4d51afbf8f408fdc32909aa14e5a97b125cddf764d7968c89a65e76df7d`；compact载荷 `827ba8d75ac290bbeac13ae47f43bd312982fd881fc850cb7bdf0c6c54f314a4`。
- 官方tokenizer两份源码均 **96668 tokens**，序列相等。
- 业务守卫、Host、SDK、模型、邮件发送、日历批准与读回均未修改；manifest能力/预算/存储/网络与rc35相同。
- 运行Host仍 `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3`。
- 本地stamp/sign/check/scan/catalog verify通过，使用原本地演练发布者。Gate检查先于产品commit，其catalog元数据Git基线仍bce33551；源码SHA与最终522ad495已独立核对，不冒充正式源码登记。
- 原预算、旧独立安装、稳定0.3.25、生产资料和未提交baseline保留。baseline SHA仍 `2830708d92b842d84eec1b7ec83d29e31b36bc599c9be5ea59a124a5aad97c90`。

## 证据与缺项

POST_RESTART_QUERY_R2、RC36_INSTALL、RC36_CALENDAR_RETURN及PUBLICATION_HOLD为本轮安全投影。正确渲染的真实窗口截图已查看，含真实账号信息，`*.private.png`仅本机保留，未入Git或GitHub。

原二十项没有重新全跑或升格。第二strong provider失败、早期model前失败根因、同最终完整外链、真实替代时间、真账号2h、OS/双Mac等仍未闭环。rc36的UI节点PASS不代表这些门槛完成；Muse删除导航没有在本轮验证。558 Shell全套及旧业务证据仍按各自身份记录，不改成rc36全量结果。
