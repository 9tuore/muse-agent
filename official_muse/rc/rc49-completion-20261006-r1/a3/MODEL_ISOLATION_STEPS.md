# 第二模型：最小单provider真实核验

用户已向Root确认第二通道是GPT/OpenAI，并授权继续真实调用，不再询问模型名称。较早金额上限被用户后续“随便用”覆盖；旧未知费用/失败证据保留，**不修改Host每天/每分钟/Token预算**，也不将失败未知usage写成零费用。

## 现有接口及限制（已读源码）

- 当前`model.complete`由Shell的`ai_host::start`注册；CardHost仅pump已注册表，不初始化该模型服务。CardHost fixture不能冒充真实模型调用。本次用同一Host1d7的独立Shell，Remote端口8515。
- `official_muse/ui_memory/prepare_candidate.py --authorized-model-only`仍硬限制特定M3官方路线、零fallback，不适合当前两个自定义候选，也不能用它准备GPT并假称已支持。
- `official_muse/rc/startup/run_chat_no_action.py`支持`--candidate --port --out --full-frozen-corpus`或`--case-ids`、`--resume-report`、`--continue-on-model-error`。但其candidate/model_metadata带完整base_url并输出私有报告；不可原样导出到公开a3材料。Root如复用只能置于private，用安全投影另出报告。
- `official_muse/phase2/tests/remote.py`真实接口已确认：`Remote.find/set_text/request('/click')/shot`；`Remote.wait_for`未处理端口尚未监听的URLError，因此本次驱动先做有界启动轮询。发送用一次raw click，不因超时重发。
- 服务meta有class/requested/attempts/usage/budget，不含真实返回model字段。因此本次在**测试副本配置**插入正文观察器（响应头/重定向不等价）记录请求model、响应model/usage/状态；请求/响应正文不改，响应头及重定向处理限制见下，身份声明不是密码学证明，也不推导整个语义题集通过。

## 本次可复现的具体入口

`python3 official_muse/rc/rc49-completion-20261006-r1/a3/run_gpt_once.py`

入口已经执行过，固定fresh目录存在时会拒绝重跑，保护一次提交和原失败。继续实验必须由Root明确创建新的独立记录，不删旧目录或反复点击以凑成功。

1. 只读指定现有隔离profile，不搜索别处Key。选择其唯一`openai/gpt-4o`配置复制到全新private目录，`fallbacks=[]`；原profile不写。
2. 使用同最终Gate49-r2六文件及其catalog；仅复制模型预算，不复制邮件账号、系统日历状态、其他联系人或生产数据库。提醒禁用，应用库为空合成数据。
3. 8516为正文观察端口：转发原授权GPT route，headers/凭据只在内存及TLS请求中使用；不写env值、URL、Key后缀或完整HTTP错误。观察记录只含模型名、状态、允许的usage、请求次数。
4. 前两次直接`--test-action launch-hub:muse-goals`未完成UI启动、没有发模型请求；第三次使用`--test-action launch-apphub`，等待Hub、5秒稳定后点击“打开”；环境`OCTOSENSE_HOME/OCTOSENSE_APP_DATA/OCTOS_APP_CORE_DIR/OCTOSENSE_HUB/OCTOSENSE_HUB_ANCHOR/MAKEPAD_REMOTE/MAKEPAD_APP_CONFIG`都指向本次隔离目录/8515，8493不动。
5. 等真实输入框可用后，只点一次“发送”，安全合成题2+3，不创建Goal、不操作邮件/日历。Host可按既有规则做格式修复，同provider实际请求次数另记，绝不加入MiniMax fallback。
6. 记录requested_model、response_model（若服务返回）、HTTP状态、failure_category、Host的is_ok/known_usage/meta和实际UI终态。配置标签≠response模型，response模型≠全部语义正确。无返回model则明确未暴露。
7. 关自己Shell/观察器，核对原profile摘要不变；自己的private日志/截图保留但不导出。公开JSON只含已允许投影字段。

## 后续T17完整题集

一次基本问答是连通/模型观察，**不是T17 PASS**。Root先确认独立通道成功及预算，两个fresh model-only profile各一个provider、fallback空、相同冻结安全题及原失败/未见变体；分别记录API尝试、usage、semantic PASS/FAIL与本地动作步骤。不得因弱通道失败直接降低标准，也不得要求弱通道每题都PASS来扩大原定义；最终生产通道必须过关键动作，另一通道差异照实交付。

既有冻结题来源：`official_muse/prelim/tests/semantic_expectations.json`、`official_muse/rc/startup/frozen_original_chat_inputs.json`；真实两模型历史复核`official_muse/rc/memory_model/RC10_FROZEN28_SEMANTIC_REVIEW.json`，保持rc10原身份。测试驱动由Root适配安全输出即可，不改产品预算/题目/原断言。

## 实际结果与协议证据边界

r1端口启动异常、r2冷编译71.085ms超时，均0次UI发送/0次API。r3正常Hub路径启动后一次发送、一条`gpt-4o`请求、HTTP200、fallback空；Host `error_code=provider`、`is_ok=false`、`known_usage=false`，真实日志含非JSON响应错误，UI为error。未成功回答5，也未核验实际响应模型，T17仍未通过。

响应正文/头只在内存使用，进程退出后已丢弃，故Content-Type、Content-Encoding、字节数/SHA、HTML/SSE/gzip/JSON/plainerror形态、登录页重定向均NOT_OBSERVED。不能重新从配置推断这些字段，不再自动网络重试。

观察器转发正文，但强制Content-Type为application/json、未保留Content-Encoding，且urllib可能跟随重定向，原Host禁止重定向。因此此项不能作为协议完全等价的直连结果，也不能唯一归因于错误路由。请求API尾路径为`/chat/completions`，不是`/responses`：由当前OpenAI `wire.prepare`和未改尾路径转发共同确认。

已读Host `complete/wire.rs`：非流式请求`stream=false`，解析直接`serde_json::from_slice`，取`choices[0].message.content`及usage。当前ureq依赖声明default-features=false/features=tls；若实际上游返回SSE或压缩字节，此解析入口不能直接处理它们，但本次没有保存形态证据，不能据此宣称原因或改Host。

## 后续单次授权 r4（已执行，不重复）

`run_gpt_protocol_once.py`与独立r4使用http.client原HTTP语义，端到端重复headers保留、无redirect、无解压；原始response仅mode0600/gitignore私有保存。代码保留原r3工具和限制，不把旧结果洗掉。r4真实返回text/html/1166字节/HTTP200，HTML=true/JSON=false，Host provider失败/UI error。请求suffix不重复；需要核验已有通道API base/路径，不猜地址，不兼容HTML当模型结果。结果见GPT_ONCE_RESULT_R4.json；至此2条分别授权API、没有再发送。
