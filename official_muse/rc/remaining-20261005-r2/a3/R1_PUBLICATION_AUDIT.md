# R1 精确增量公开前审查

结论：**本次精确输入范围未发现隐私发布阻塞**；整体产品状态继续 PARTIAL。本审查不是产品重测或成功发布授权。

输入 `AUDIT_INPUT_R1.json` SHA-256：`782d83dab9a41dc72d80d5cc373964b8275006225dd9f089a2514082e93a6a55`。

范围：`39e2b20d992bea5e856fe93bc97702650a37c487..f84e2c1e9bda675f437709d8c5263b504553f81a`，2个提交、15个新增内容对象，加清单46个明确SHA文件（其中1个与提交范围重合，共60个路径）。46项共139963字节，审查前后SHA和大小全部相符，输入清单哈希也未变。没有读取 SAFE_STAGE_LIST、private、真实账号/邮件/配置、清单外工作树文件或未提交rc29。

## 敏感内容

提交对象和46文件全部为文本。凭据/token/私钥/带认证URL/私人邮箱启发式检查未命中；46文件所有所查模式均为0。提交内容仅命中已授权的源码/构建绝对目录路径，不作为Secret阻塞。manifest中的公开签名不是签名私钥。合成探针明确构造 synthetic/合成事实并拒绝外部服务；native四项为状态、合成关联ID、摘要与错误安全投影，没有真实收件人、邮件正文、账号或凭据。没有新媒体需要本轮像素检查。

## 证据真实性边界

两处SDK改动是现有测试函数的模块路径与中文搜索词修正，没有runtime/Host诊断接口；已对比冻结Git diff及生产区字节。依赖锁的两处overlay SHA与实际blob相符。可读源5e931846、payload4ce3a734和SDK锁f487df0c均重新计算匹配报告。

A4材料明确默认dev、无过滤558 PASS；保留release首轮552/6失败及修正临时目录后554/4失败。空target Host build明确复用SDK/cargo源码缓存，不冒充严格fresh checkout，也未替换运行Host。A3只审查命令、结果投影及日志哈希，没有读取未列原日志或重复运行测试。

A2保留八次容量ERROR和对应诊断摘录、forget首轮两个guard_activity_unchanged失败、独立r2修正时序结果。容量/forget仅是合成fixture中的真实产品函数窄范围验证，不升格为原生UI、任意负载、正式full-chain。失败摘要和哈希已核对；未列原始日志/jail实际存在性未重新访问验证。

native旧R1收件是用户声明记录，不是Host自动投递证明；新邮件仍accepted且recipient_arrival=UNVERIFIED；rc28日历FAIL_PRE_HOST_CALLBACK_BUDGET保留。未将安装、窗口出现或卡片出现当作动作成功。

## 需要在最终增量中保持的边界

rc28提交报告仍保留当时的安装待验/default suite进行中措辞，后续A4报告和本清单native投影给出较晚结果；最终入口宜按后续证据更新，保留历史记录。容量报告留待forget的当时缺口由独立forget附录补足，只限附录范围。runner明确依赖本地历史模板和CardHost，不宣称全新checkout可独立复现。

本结论仅绑定上述输入哈希、提交对象与46文件哈希；新增Calendar名单、截图、报告或rc29提交须另给精确冻结增量。没有stage、commit、push、模型调用或生产资料访问。逐文件哈希、模式统计和边界见 R1_PUBLICATION_AUDIT.json。
