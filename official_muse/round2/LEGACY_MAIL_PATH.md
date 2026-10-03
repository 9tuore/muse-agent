# 旧 QQ 发送路径边界

C05：当前官方 Muse 使用 `host.request("mail.send", ...)`。账号、授权、SMTP/IMAP 和网络由官方 Mail Host Service 管理；应用仅持有账号 ID。

`app/qqmail_imap_bridge.py` 与独立版 SMTP outbox/queue 为 **LEGACY（仅旧独立版）**。它们不是官方 Muse 的生产路径，官方 bundle 禁止调用或回退到这些发送器。不修改旧安装包、不为死路径新增恢复逻辑。

官方版批准绑定精确草稿、账号及 request_id；调用宿主前保存 durable action 和 attempt。结果未知时显示 UNKNOWN 并要求对账，重启不自动重发。SMTP accepted 不能代替收件端确认，不宣称 exactly-once。

防回退测试：`python3 -m unittest discover -s official_muse/round2/tests -p test_legacy_mail.py -v`。
