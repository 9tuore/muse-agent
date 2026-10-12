# SPRINT-005 ZC01 当前状态

2026-10-12；基线own codex/gpt01-calendar-history/ea4d6e52，中央8da96cf；正式Main已核仍caa99c57。13:11:25开始，19:11:25高风险冻结，20:11:25截止。仅本namespace/自有fixture测试；Root独占GUI与生产、Main/Host/Bundle。本站没有GUI操作、真实模型/Calendar/Mail调用、生产profile/Secret/Keychain读取、Tag/发布/push、跨聊天消息或子代理。

**结论PARTIAL / 源码与接口交接READY。** 模型和三轮GUI仍未验证。完整入口为DELIVERY.md，不重复旧NIGHT004测试结论。

- Models首提交62f28817：正式Host1eb1887b包含7系统pack，AI providers脚本c6680953/21763bytes与SDK相同且有llm.test。裸文本marker不存在不是缺包。ai-providers/models搜索无结果可由连字符规范化/缺别名/当前子树解释；Root核AI providers/providers/ai及合法Settings/OpenProviders入口。未假定菜单实际可见。
- 严格探针：已有os.ai-providers Test按指定provider固定ping，无tools/history；Muse model.complete固定合成nonce JSON已备，wire源码无工具执行器/私人上下文。后者可回退/重试，不证明指定MiniMax-M3或Agent full-chain。Root可挂接已有授权UI，本站未改Main。
- 资源：formal与zc05-preflight-r1的211个host-runtime文件名称/大小/hash逐一同，无symlink，model_resource_audit.json。Root报告originalR5同state单Host重启正文恢复；首用Deny亦已持久化，根因未隔离。未做GPU/布局改动。
- profile_unresolved：Kernel真实Git b0759a57；在session/open active profile检查、cwd/sandbox前抛错。Main open传{}，agent.profile read-only是工具预设，family/model配置不是Kernel profile存在证明。合法peer/session/register/declaration/owner链定位见DELIVERY；缺实际失败method/data/profile绑定，不改生产注册。
- 官方：组织方实际render-source写10/12决赛用10/9冻结版、Native参评、Apache2公开可运行源码和复现材料、无需先上架。当前AppHub需GitHub-attested及独立review/admin发布；legacy本机签名仅rehearsal。未确认Muse实际冻结版/后修例外或catalog approval。
- vanilla差异：固定SDK4ccf8e06/当前f0754134/RC6 Calendar tools均无get_event，配对源码新增。10相关文件4异6同；32 framework patch hash全符合lock。只是选定源码审计；PREPARED_NOT_BUILT不是formal Host完整编译receipt，需Root绑定正式binary→Rust closure。
- Calendar：read_calendar_store.py仅中央build/sprint005/zc05-*/state、双marker+spec、nonce标题及ID白名单，拒生产/symlink/混入/损坏/缺失/写操作。13/13 fixture tests PASS，日志calendar_reader_tests.log；service_api_called=false，未读Root状态或GUI创建的数据。Root/ZC05按example准备spec后可用events发现ID、绑定后精确读改期/冲突/删除/重启。旧helper现场binary缺失，旧证据保留。

未完成：合法真实provider Test/固定probe、profile错误实际绑定、ZC05三轮GUI、formal Host完整源码receipt及比赛冻结版关系。Local commits only，Root统一收口。
