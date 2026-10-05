# Root 本轮保留的失败

- visual-990-r1：引用了不存在的裸 card-host 路径；未启动窗口。
- visual-990-r2：快捷区改为 on_render 后未显式 render，启动时没有导航；已补 render。其原日志保留。
- visual-990-r3：源目录仅含 main.splash，缺 manifest；没有启动，修正完整 bundle 准备。
- visual-990-final：旧夹具用 chat_body 定位，实际当前为 chat_list；更新驱动，不修改产品掩盖。
- visual-990-final-r2：驱动把屏幕外的次级导航当作未展开，误点击更多收起；改为先滚动寻找，再打开。
- visual-990-final-r3：日期 2026-10-05 15:00 已过去，产品正确拒绝，因此没有确认卡；新纯 UI fixture 使用 2030 年未来时间，原失败不删。
- 第二模型 r1/r2：AI设置被Muse覆盖，首次点坐标未形成测试；后一次误展开目录导致找不到按钮。保留原意图。r3通过实际官方测试按钮观察“已连接 · 630 毫秒”。截图第一次404后仅重试截图，没有重复模型测试。

范围判断：可见 fixture 截图不证明外部邮件/日历动作。--keep 子进程在命令结束后未保持运行，后续连接失败保留；界面附加动作改为同一驱动生命周期中执行。

- visual-short-final：驱动从已保留的底部滚动位置只向下找新插入表单，无法定位位于上方的标题。重置外层到顶后找控件。
- visual-short-final-r2：回复后输入框位于屏幕外，驱动即时 find 错误；补真实外层滚动后 r3 通过全部相关操作。
- r19/r5：静态审查提出单点日期和无关任选风险，实际 helper 保留“菜单任选”扩大整日 FAIL。版本递增 rc20，只缩紧相邻时间许可词，原失败不删。
- token工具初次构建发现两个缓存依赖变体，未猜选；分别构建并核对两种 tokenizer，均等价。
- App Hub 安装实际成功但详情停在底部，驱动找不到“打开”；真实滚到顶部后打开，安装源哈希相符。

- rc20/rc21 GPT首选三次真实调用：前两次invalid_output，rc21新增固定分类后新变式确认为invalid_json；未知usage保持false，未重放。同一真实官方模型窗口已恢复MiniMax M3首选。
- Shell菜单模型设置入口的首次缺包推断撤回：实际Cmd+Space→KeyA/KeyI可见并打开设置；六份编译pack字节相同，不需要重建。
- rc22首次删除预览，只有前缀及截短ID也通过，真实隔离反例FAIL保留。rc22-r2仅用完整标题token谓词统一预览及最终确认，最终窄域结果待独立复核。

- rc22实际Calendar update：首次snapshot绑定变化，0点击；重新观察后单次update成功，但驱动误按changes.start/end核对合并事件回执。原FAIL保留，独立get逐字段通过，没有重放update。
- rc22日期选择：Remote.find("6")误匹配widget ID6而非日期文本，仅发生只读选择；改为Button精确文本与可见矩形，正确日期显示保留截图。
- rc22实际完整ID预览、确认、单次删除、独立get明确不存在成功。首次partial按钮和scroll区域定位失败均在外部dispatch前，原记录保留。
- rc23普通短答46+27实际73通过；原长问无工具回执的视频笔记，在GPT首选及M3首选均invalid_json，单次app dispatch，无额外重发。显式用户JSON格式控制通过，仅作诊断，不替换原输入。
- 模型settings菜单不在/snap widget树；通过真实窗口截图和官方菜单进入设置，M3首选已恢复。response不返回provider ID，attempts=2不能单独证明独立GPT成功。

## rc25 界面修复的保留失败

- 默认 CardHost 路径已被清理，首次视觉脚本启动 FileNotFoundError；之后指定现存 QQ 配套 CardHost，没有伪造执行。
- 视觉脚本传入“对话”页触发 first_screen 标题映射 KeyError；三页新目录重新运行，旧截图/runtime保留。
- 原生16聊天第一次把整个 sessions JSON要求逐字节不变，实际 chat_save 对选中聊天更新 updated_at，断言失败；检查实际函数后仅排除这个已知时间戳，所有其他字段严格比较，并在新目录重新运行。原两个删除预览截图及失败报告保留。
- 更新重启后原生 Shell尺寸从1440×900变为1400×809，旧菜单坐标误打开官方Mail应用；没有登录/发送/修改账号，关闭后按当前真实截图进入模型设置。第一次首选切换断言失败，0聊天提交，截图留在私人目录。
- GPT-4o精确连接测试成功，但一次普通聊天仍attempts=2、usage.estimated=true；正确回答不证明独立GPT通道，T17仍不升级，M3首选恢复。
- SDK首次verify发现本地忽略的vendor中两处Mail文件仍为QQ改动前源码；已有overlay与冻结构建SDK一致。两处原文件已备份到私人证据目录后对齐已提交overlay，新的完整SDKverify通过12000文件；没有把首次失败删除。


## rc25→rc27 最小修复与测试留痕

- 原实际Chat状态问题后接“请解释”被误路由calendar_candidate，GPT首选请求2次尝试/估算用量，持久回复追问日期；无系统写入。原问题与路由失败在A2 `rc25-baseline-r1/v2`保留；不以连接成功或错误动作模型响应升级T17。
- A2原en-dash准备句被旧格式检查拒绝，不能只把setup改“到”算修好。rc26-r2只补字符后缺右钟“15:00–”2FAIL保留且未安装；rc27限定新分支完整双时钟，同原失败＋变体拒绝通过。新34/5与旧状态52/10不相加冒充全套。
- Root第一次全源逆向检查误要求旧regex全文件只出现一次，其他函数也使用该literal导致AssertionError；改为精确函数前缀后验证全部余字节相同，原失败未用于产品结论。
- Root首次rc26本地发布前状态检查误列sources.json/calendar-goals.json，缺文件立即停止，零publish/安装；改用已经观察的六文件列表并保存前后SHA，未创建这些不存在的文件。
- Root先后请求不存在的nav_mail/page_scroll widget，前者零点击、后者在只读账号请求后停止；使用实际可见中文按钮和mail_list_body后继续，不能把失败标成功。
- 新Host最初日历not_determined，已请求本人允许；最新真实只读检查为完整访问。账号metadata和缓存提醒可见，当前没有新收信同步完成证据；不拿cache替代service回执。
- 原完整Shell单测因launcher已有super::menu命名空间错误BLOCKED，日志留包装目录；8项窄几何PASS和新Host增量构建/严格验签不替代完整clean/全suite。
- 导出完成前返回对话页时，驱动把观察到的非唯一widget ID“-”传给find，匹配了另一控件，随后goal_input缺失断言失败。没有模型/邮件/日历提交；改用唯一可见中文文本“对话”后正确返回，输入框278/644/703/32与发送按钮986/644/56/36可见。保留此工具定位失败，不解释为产品回归。
