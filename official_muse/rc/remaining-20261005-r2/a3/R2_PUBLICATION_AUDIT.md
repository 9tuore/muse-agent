# R2 精确增量公开前审查

结论：**本次精确输入范围未发现隐私发布阻塞**。产品原20项仍为PARTIAL；本报告不是完整功能复测或发布成功声明。R1报告未覆盖或改写。

输入 `AUDIT_INPUT_R2.json` SHA-256：`4b2d9cb47c0726efc3cacfc0fafc6dc3e8c3ed880b37b51f66ddf124b6905177`。

范围：`f84e2c1e9bda675f437709d8c5263b504553f81a..dffed0702815cea2255b90da00e9f00edddf9e23` 的4个提交、13个新增历史内容对象（4079593字节），加156项明确SHA文件（A2合成材料140项、Root安全投影16项，479574字节），合计160个不同路径。输入及156项SHA/大小在审查前后均相符，138项嵌套证据manifest引用全部与清单哈希匹配。100个JSON可解析、7个Python可AST解析；未执行这些runner。

## 敏感内容与范围

全部输入为文本。凭据、token、私钥、带认证URL、私人邮箱模式未命中。显式材料只出现7处已授权源码/目录路径，均在合成失败说明中，不作Secret阻塞。合成事件ID、时间、关联ID、存储摘要属于授权测试投影；未发现真实账号、私人邮件正文或凭据。未读取private、未列live/工作树文件、生产数据库或新截图；无媒体全盘检查。

## 宣称核对

- 源信发送是rc28；创建及外部刷新是rc29；本批没有把拟于rc34执行的update写成成功，更没有把跨版本证据拼成同一最终候选整链。两个rc29版本的代码SHA不同，已按commit/源码/payload分别核对。
- 最终提交rc34可读源码SHA为 `b01873c853ea1d08dfbc41f4fa23e19e537d2966412331238b75536f9461e461`，payload为 `f9dff57661d37b5f3f0b403e40ac323dfee075e78c90c38f0b249127bae66b80`，与对应安全投影/fixture报告一致。未以安装或窗口出现替代动作成功。
- 第二GPT只有 `PREPARED_NOT_CALLED`，候选数1/fallback数0；`standard_openai_endpoint=false` 必须保留。该材料不证明官方OpenAI endpoint、真实推理成功或第二强模型已过。A3未读实际profile，没有模型调用。
- 授权提交不涉及Host/SDK预算配置，产品diff没有提高预算上限；分拆回调仍按各轮默认预算执行。26项显式默认预算不变声明均为true，未发现runner新增预算覆盖。此结论不表示总时延不变或任意负载稳定。
- 合成async get/account回复、model.complete入队与真实推理/系统日历/SMTP明确分开；旧source的guard结果保留原SHA，不冒充rc34重跑。原20项整体PARTIAL，未发现READY/full-chain成功升格。

## 失败保留

已审材料保留八次容量ERROR、forget首轮失败、Calendar缺boot/重复点击超时/version构造/缺widget错误，manual rc30累计指令耗尽与缺mail.accounts合成应答、rc31错误绑定、rc32评分耗尽、rc33引用构建耗尽及当时PARTIAL报告；还保留rc28日历写前预算失败、rc29首轮UTC显示格式判断，以及rc34首次安装实际仍为rc31的身份失败。

共识别19项顶层FAIL/ERROR/PARTIAL或失败断言记录，另有嵌套失败摘录。失败后的修正运行另行记载，没有将旧失败改称成功。核对的是授权文件中的失败记录、源代码位置和log哈希，未读取未列原日志/jail来证明所有本地原件存在性。

## 后续边界

R3需另行绑定实际改期回执、最终文档及新的精确SHA；不得追溯升级本批跨版本链或GPT准备记录。现有runner属于依赖保留Host/模板的本地诊断，不是全新checkout可复现安装器。没有source修改、费用调用、GUI操作、stage、commit或push。

逐路径/哈希/模式/版本映射见 R2_PUBLICATION_AUDIT.json、R2_EXPLICIT_SCAN.json、R2_COMMITTED_SCAN.json 和 R2_STATIC_CHECKS.json。
