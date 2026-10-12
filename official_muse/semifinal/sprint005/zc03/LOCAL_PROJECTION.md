# UA-PREFLIGHT-003 本地读回投影

结果：`FIXTURE_PASS`，实际既有Splash VM执行70个合成案例。冻结Main SHA `f9e94877a4f1eb4f4f9d442b16adc01a4c74af815e3611ef8aaecfcba318e891`；归档时Root现场仍同SHA。VM SHA `337cbba7180e913d31d28b3122ce2167484a108b3c1fd2631b99c31815af9d34`，未重编。

22个生产函数与23个生产global从冻结源逐字提取，包括ac_local_run_readback/ac_projection/ac_current_goal/ac_goal_allowed及gm类型/账号谓词，执行身份与原文保存在evidence/local-projection/r4。直接判定是内部helper，不自行做scope保护；跨项目/owner/account/chat否定例检验的是父选择器和实际投影隐藏。

匹配completed Goal/Run、当前版本、同path、storage.write单步spec，以及同Goal/Run、起止时间内readback才显示本地已核验。正向包含起止边界。planned/failed/unknown/accepted/running、错Goal/Run/版本/path、缺时间/错类型/越界时间、缺或坏spec、Mail/Calendar spec、mail_source都未错误取得本地读回标记。检查会话/归属/账号撤销、不可读状态、最近64记录边界、4个Run/读回和12节点截断；每例业务记录前后JSON相等。

官方Calendar投影设为返回false的明确fixture边界；无关Memory/邮件依赖为计数拒绝边界且实际调用数0。Mail/Calendar spec检查只证明本地storage分支不会泛化verified，不是官方服务验收。全部运行无Host、GUI、存储读写、计时器、网络或业务执行。

失败历史保留：r1实际61例PASS；r2父脚本把解析器误按冻结副本路径解析，VM未启动，工具异常已转录到receipt（没有原始stderr文件）；修正为自有仓库解析器后r3实际70例，仅测试默认的读回节点数量预期错。12节点中原计划1＋回执2＋动作4占7，余5容纳2组执行/读回＋1执行，因此修正该fixture为2读回；r3原始stdout/stderr/report保留。r4实际70例PASS、stderr空，三轮已执行父脚本均按原runner SHA复核归档。

复现（自有worktree；输出目录须不存在）：

```sh
python3 -B official_muse/semifinal/sprint005/zc03/run_local_projection_probe.py --source official_muse/semifinal/sprint005/zc03/evidence/local-projection/r4/frozen-main.splash --vm build/sprint005-zc03/vm-target/debug/zc03-sprint005-vm --out build/sprint005-zc03/local-projection-new
```

以上为复现入口，尚未执行新目录命令。实际父命令、VM命令、stdout、stderr、cases和每例完整view在各轮目录。Root后续源码变化必须重新冻结，不将此次纯VM成绩当GUI或真实存储PASS。

已执行父脚本以executed-parent.json的source字符串保存，解码后SHA与各轮identity一致；这是保留原字节（含原尾空格）的存储格式。当前复现runner仅去除行尾空格，未重跑；r4冻结执行脚本另有原SHA。
