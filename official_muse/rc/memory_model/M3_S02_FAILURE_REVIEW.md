# Official MiniMax-M3 S02 failure: UNKNOWN

只读现有合成候选与安全记录，未执行模型、GUI、Git、SDK或产品修改；只写A3独立摘要。未读凭据字段、production profile、snap或截图；日志只提取白名单code标记，不输出原始错误detail。Root报告未修改。

结论：**UNKNOWN**。不能从现有记录判定为rate/provider/invalid_output/refused/truncated，也不能因为M2.7随后成功就归因于M3的格式、限流或服务问题。

## Verified observations

运行绑定commit b9cf26b8、应用payload f5cd33b7、Host938ba58a；实际候选bundle和Host executable SHA均匹配记录。候选属于AUTHORIZED_MODEL_ONLY_SYNTHETIC。S01成功返回13；S02同会话追问状态error，提示“这次没有整理成功。请重试，或手动填写。”，proposals前后为空，single_input=true。S02ledger从calls35/tokens34188到calls36/tokens35349，即+1call/+1161tokens。

保存的model-last-response trace query_sha256与S02原话SHA一致，is_ok=false、known_usage=false，无meta。trace源码位于main.splash:7088附近，Host回包后先保存trace；仅成功且meta含usage/budget/attempts时更新known_usage。失败路径不保存r.error的稳定前缀。known_usage=false因此不代表没花tokens，也不能表明具体失败类别。

实际安全log中MODEL_FINAL_FAILURE、MODEL_FORMAT_ERROR、MODEL_RETRY均0，严格的“model: muse-goals refused (白名单code)”也无匹配；无[E]/scriptbudget标记。一个普通model:字符串和一个budget:字符串均不能当成错误类别证据。run_chat_no_action.py保存远程/log，launch_candidate.py经open启动应用，没有捕获该Host进程stdout/stderr；这解释现有安全日志不足以取到官方eprintln类别，但不证明其他外部日志绝对不存在。

## Verified code paths

chat_model_config默认普通对话schema要求reply:string、maxLength1200、禁止额外字段；S02是普通数值追问，从该源码路由不会选Mail/Calendar/Goal动作。send_chat用class fast，将config.schema交给muse_model_request；后者按有效历史和本轮query构造交替messages，Host回包失败传给model_user_error。没有保存实际S02请求payload/Host错误code，因此源码路径核对不能替代该次请求数据证明。

model_user_error把invalid_output映射成通用文案；nil和所有未识别前缀也使用同文案。官方Code枚举还含refused/truncated，Muse当前未单独映射，因此它们也可能落入相同通用提示。**这是不可区分集合，不是对S02的类别判定。**

官方host-service/src/complete/mod.rs当前SHA1ccf4531与CHUNK_DELTA_BUILD_RESULTS的build input完全一致，该记录的签后HostSHA也与此次938ba58a一致，故本次Host源码路径有实际构建绑定。Refusal Display将稳定code以“code: message”传给应用；ModelService::call还有现有MODEL_FINAL_FAILURE app/code stderr标记。complete先admit，收到可解析reply后charge，随后才检查refused/truncated和schema；格式失败可重试，后续也可遇预算/传输失败。+1161tokens只证明ledger确有增加，不能唯一指认某个失败路径或次数。

Root报告相同应用/Host换M2.7后S01/S02/S03/S04/S05/H01成功；A3未另读那些实测资料，只注明Controller来源。该对照有用，但不补回已丢失的M3错误code。

## Smallest proposed observability boundary

无需改SDK：在muse_model_request既有Host callback的现有trace里增加**拟议字段**host_error_code。当r.is_ok=false且r.error为字符串时，只提取冒号前前缀，严格与官方白名单capability/no_provider/rate/budget/bad_request/invalid_output/refused/truncated/too_large/provider匹配；无匹配或无字符串保存unknown。绝不保存原始错误后缀、detail、prompt、回答、凭据、provider/model配置或route。保留现有query SHA/session/time，足够关联本次请求。失败缺meta时known_usage继续false，不猜attempts/tokenusage。

若要保留多轮证据，Root现有驱动每次响应后在下一请求覆盖前快照这个安全trace即可；可选只捕获现有Host MODEL_FINAL_FAILURE app/code行，不收集带detail的另一路日志。以上均为建议，A3未实施、未重试、未执行额外测试。

结构化结果和证据SHA见M3_S02_FAILURE_REVIEW.json。未改Calendar公开摘要或既有Root报告。
