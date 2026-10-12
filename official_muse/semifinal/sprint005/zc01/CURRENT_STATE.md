# SPRINT-005 ZC01 当前状态

2026-10-12；基线own codex/gpt01-calendar-history/ea4d6e52，中央8da96cf；正式R5仍caa99c57；新Main只读核947c5291，rc8由Root准备。13:11:25开始，19:11:25高风险冻结，20:11:25截止。仅本namespace/自有fixture测试；Root独占GUI与生产、Main/Host/Bundle。本站没有GUI操作、真实模型/Calendar/Mail调用、生产profile/Secret/Keychain读取、Tag/发布/push、跨聊天消息或子代理。

**结论PARTIAL / 源码与接口交接READY。** 模型和三轮GUI仍未验证。完整入口为DELIVERY.md，不重复旧NIGHT004测试结论。

- Models首提交62f28817：正式Host1eb1887b包含7系统pack，AI providers脚本c6680953/21763bytes与SDK相同且有llm.test。裸文本marker不存在不是缺包。ai-providers/models搜索无结果可由连字符规范化/缺别名/当前子树解释；Root核AI providers/providers/ai及合法Settings/OpenProviders入口。未假定菜单实际可见。
- 严格探针：已有os.ai-providers Test按指定provider固定ping，无tools/history；Muse model.complete固定合成nonce JSON已备，wire源码无工具执行器/私人上下文。后者可回退/重试，不证明指定MiniMax-M3或Agent full-chain。Root可挂接已有授权UI，本站未改Main。
- 资源：formal与zc05-preflight-r1的211个host-runtime文件名称/大小/hash逐一同，无symlink，model_resource_audit.json。Root报告originalR5同state单Host重启正文恢复；首用Deny亦已持久化，根因未隔离。未做GPU/布局改动。
- profile_unresolved：Kernel真实Git b0759a57；在session/open active profile检查、cwd/sandbox前抛错。Main open传{}，agent.profile read-only是工具预设，family/model配置不是Kernel profile存在证明。合法peer/session/register/declaration/owner链定位见DELIVERY；缺实际失败method/data/profile绑定，不改生产注册。
- 官方：组织方实际render-source写10/12决赛用10/9冻结版、Native参评、Apache2公开可运行源码和复现材料、无需先上架。当前AppHub需GitHub-attested及独立review/admin发布；legacy本机签名仅rehearsal。未确认Muse实际冻结版/后修例外或catalog approval。
- vanilla差异：固定SDK4ccf8e06/当前f0754134/RC6 Calendar tools均无get_event，配对源码新增。10相关文件4异6同；32 framework patch hash全符合lock。只是选定源码审计；PREPARED_NOT_BUILT不是formal Host完整编译receipt，需Root绑定正式binary→Rust closure。
- Calendar：read_calendar_store.py仅中央build/sprint005/zc05-*/state、双marker+spec、nonce标题及ID白名单，拒生产/symlink/混入/损坏/缺失/写操作。13/13 fixture tests PASS，日志calendar_reader_tests.log；service_api_called=false，未读Root状态或GUI创建的数据。Root/ZC05按example准备spec后可用events发现ID、绑定后精确读改期/冲突/删除/重启。旧helper现场binary缺失，旧证据保留。

未完成：合法真实provider Test/固定probe、profile错误实际绑定、ZC05三轮GUI、formal Host完整源码receipt及比赛冻结版关系。Local commits only，Root统一收口。

## 构建绑定后续收口

Root已接收635ca8d1，并报告providers实际GUI找到、loopback TestConnection产生1次model.request/Connected3ms；不是真实M3。正式1eb Host仅在内存还原签名前字节，SHA精确匹配night004-rc7-preparation实际a9fc8ca3 build receipt（124155120bytes），UUID72569da9…；3/3合成Mach-O测试PASS，证据build_binding_r1/formal-host-binding.json。实际是BINARY_TO_BUILD_RECEIPT_BOUND，完整历史源码/环境freeze尚缺，不能称独立源码重建成功。

已执行current cargo tree offline/locked+精确features，575明确package ID/0未映射；只记录当前manifest SHA和当前环境，未cargo build、未操作Root target。用户经Root确认Oct13截止；主办页复查hash不变仍10/9冻结/10/12答辩，两份依据同时保留，不改用户截止或推断例外。

Root最新要求尽快提交此已确认小单元，不扩大审计、不阻塞冻结。Root新CA fixture Host raw e4e8f5ac/签名cea8ca71属于独立fixture，生产1eb/R5不改；ZC05 Memory实际GUI四项通过为Root提供结果，Goal/Calendar仍进行中。本站无GUI/真实模型/生产/Root target动作；316个本轮开始前已存在的namespace外媒体删除保持原样，没有恢复或提交。

P0 session.open只读小单元：p0_session_open_r1/evidence.json。成功契约open:true正确；请求blocked/turn空且persisted user与settings相同。首用gate立即NO_CONSENT、后Allow仅prepare不replay符合Root现场；原始opened.error未捕获，不能证明具体失败分支。建议明确新只读attempt保留旧FAIL，不自动重放；共享产品未改。

P0 tools wire：p0_tool_offer_r1/evidence.json。OpenAI adapter只因传入tools空而省略，未发现unknown local能力过滤该wire；Kernel将calendar.events映射calendar_events。公开fixture profile为local/OpenAI/sprint005-fixture。等Root新logger offered_tool_names分支定位，不猜字段、不改Root配置、不重编或GUI操作。
