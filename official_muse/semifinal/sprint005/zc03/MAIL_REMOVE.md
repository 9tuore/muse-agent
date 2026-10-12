# 邮箱移除／第二账号定向VM

结果FIXTURE_PASS，最终24个真实Splash VM合成案例，VM337cbba7沿用、无重编。源SHA见evidence/mail-remove/r3/identity.json，归档现场一致性另记archive-identity.json；不将后续Root改动继承为通过。

五个生产函数逐字提取：mail_enabled、mail_host_error、mail_accounts_load、mail_remove_account、mail_add_account，仅host.request改为合成deferred transport；实际取消UI处理体mail_remove_confirm清空/mail_redraw原字节提取。capabilities、redraw和gm_set_accounts为明确fixture，其中后者只记录传入账号ID，不验证全局记忆账号策略。

取消/未确认/错确认/不存在账号、能力缺失、pending/sending/model_pending/calendar_link_pending，以及本账号sending/accepted/unknown草稿均零派发；另一账号accepted不误阻。成功移除仅调用mail.remove_account({account:A})→mail.accounts；回读剩B，当前选A时清空视图/分页/连接/compose，原draft保持。原先选B或等待期间切B保持B选择与列表；等待期间切nil保留回调时视图，不把旧选择当现选择清理。服务拒绝保留选择和账号、显示host错误、清pending；删除成功但账号列表回读失败则报错并调用授权ID清空adapter，不伪称列表成功。

最终添加路径专门从单账号A开始：mail.add_account→mail.accounts后列表A/B及传入授权IDs一致；登录取消保留A、错误可见、无accounts回读；pending或无mail能力阻止add。所有dispatch在callback前pending=true，回调后正确解除。

失败保留：r1实际VM无运行时错误，但4个父断言失败，3个将Splash JSON文本与Python排序文本比较，另1个错要求切nil后继续清空旧列表。按对象值与当前选择保留修正，r2实际24例PASS；r3将原附加账号C例收窄为单A→第二B的明确要求，24例PASS。三轮冻结源、实际命令、原始stdout/stderr、执行父脚本及SHA、每例全部状态齐全，无失败覆盖。

这是控制函数／取消体和异步选择的真实CLI VM验证，transport、账号列表、能力和授权更新均为合成边界。没有GUI、真实邮箱/凭据、宿主移除、vault、业务存储或实际APP添加账号验收，不代表模拟邮箱已被真实清除。Root唯一修改Main；本目录只工具/证据。
