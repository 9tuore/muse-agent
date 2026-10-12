# Calendar 首用授权提示定向检查

结果：FIXTURE_PASS，25个实际Splash VM合成案例，首轮通过、stderr为空，无VM失败。源码冻结SHA `c09836478cdd5fe58f34634002400ebc517185deb30fe4a29a469705c1ac6bd7`；VM SHA `337cbba7180e913d31d28b3122ce2167484a108b3c1fd2631b99c31815af9d34`，二进制在自有build/sprint005-zc03/vm-target/debug/zc03-sprint005-vm，未重编。

真实提取calendar_agent_session_notice、calendar_agent_submit_bound、calendar_agent_history及3个gm类型谓词；仅host.request改为合成transport端口。save为明确的内存记录adapter，时钟/随机数为常量，redraw为空。binding/工具回执等未走分支为计数拒绝adapter，实际调用0。没有宿主、GUI、真实存储或官方Calendar操作。

16个提示helper边界：exact NO_CONSENT、turned-off、signin、unknown、nil/array、缺is_ok/字符串is_ok/is_ok=true、非字符串error、513字节error、尾空格/小写近似、成功open与malformed data。只有精确且类型匹配的NO_CONSENT返回首用申请提示，其他返回原fallback；原opened记录不变，raw错误不出现在提示中。

9个真实创建函数案例：NO_CONSENT与unknown/turned-off/signin、open=false、malformed data、成功、open回调前user变化、初始busy。拒绝后blocked、空turn_id、仅open调用、两份内存save状态且无turn；成功路径严格open→turn.start→history、turn_completed（仅合成回合，不等于Calendar已核验）；user变化阻止turn；busy时零服务。未注入任何自动重放函数或计时器，改变合成身份后也未新增服务调用。这不等于GUI实际授权或宿主重放行为已测试。

对旧f9冻结源做逐字静态比较：创建/改期/删除三个函数将新session_notice调用还原为各自旧fallback字面量后，与原函数完全相同。因此原守卫、请求顺序和状态分支保持；改期/删除没有重复运行，只做本项静态检查。

证据：evidence/calendar-consent-r1包含冻结源码、executed.splash、executed-parent.py、source/VM/函数SHA、实际父命令与VM命令、全部cases、raw stdout/stderr、逐例结果和归档现场身份。当前源若变化不可沿用本结果。无70行动链复跑，无Cargo、shared target、GUI或业务存储操作。
