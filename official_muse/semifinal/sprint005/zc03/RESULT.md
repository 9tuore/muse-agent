# SPRINT005 ZC03交付结果

当前PARTIAL：Memory最小patch及其实际CLI验证已完成；入口文档patch、离线身份审计、被动观测工具与75秒演示稿完成。新原生黑桌面ROOT_CAUSE_NOT_ESTABLISHED，正式GUI性能/长期业务稳定/演示成片仍NOT_TESTED或NOT_RECORDED，由Root/ZC05控制。

## 实际完成

- Memory：仅gm_validate_indexed_part跳过相反阶段无效循环，batch2/20ms/64ms Host预算/all/correction/所有验证和128动作一次恢复不变。基线caa99、候选947c5291。24函数6global仅目标函数变更；同API生成64/128/空forget，A/B/B/A四实际VM进程384区间，22个边界/损坏结果一致，active坏Source/Claim拒绝、文件不变、零dispatch；归档verifierPASS，不额外计运行。
- CLI Source中位6.509544→5.395151ms、Claim15.450739→11.785216ms；p95 15.121630→11.087673与41.792419→26.478015ms。环境未隔离，baseline最大129.830ms包含RPC/调度，不是Host超64ms证明，也不宣称GUI首屏提速。
- 旧R5真实20证据离线复核：full ready中位21.652428s，Host3.798553s；打开后到完整图文件间隔12.958485s，含采集/轮询而非函数归因。122个20ms串行片段名义2.44s，其余开销尚未绑定。没有跑新20或重复14指标。
- 身份7项PASS：source caa99→stamp readable e6c8adcf→signed ef58430f、manifest7b746fb0，R5实际UI0.4.0-rc7正确。初始Main旧label草稿拒绝，不提Main标签改动。根bundle90351cba/rc17是真实历史保底；root-entry-doc.patch仅建议Root修README入口，独立copy上的git apply --check通过，不写RootREADME/Bundle。
- 工具7项定向测试PASS，其中真实只读proc_pidpath/ps仅针对本测试进程2秒，其他为fixture拒绝分类。最初ps comm截断问题已实际定位并修正，不能把该测试当Host soak。工具有期限/最多721行/单PID exe和出生时间核验，退出/身份丢失保留失败，不读argv/profile、不信号/重启/HTTP。
- 最小非GUI ScriptVM离线构建27.58秒、独立target63MiB、debug=0/incremental=0，driver字节同旧版、SDKscript163源码构建前后一致。新binary337cbba7，不冒充缺失的f480缓存；未构建Host/Kernel/全Shell，无共享target写入。

## 新黑绘制P0

个人查看纯合成r1原图：bar/Consent/AppsMenu可见，桌面壁纸、window chrome和模块正文黑，反射布局不能当像素成功。读取日志已有module/font/Main eval，无[E]/预算错误；分工收窄前176个渲染资源与R5字节完全一致，之后不再调查资源线。

Root Omarchy/NoGauss/supersample对照仍黑，不能把开关当修复。Root退出两个Host再同originalR5/state/flags单Host重启；ZC03实际查看合成图，Ocean/chrome/原型正文可见。Deny也持久化，入口从原型startup改成两模块startup的差异仍存在，尚不能定并行/GPU根因，原型可见不等于完整Muse成功。

按Root指令暂停GPU源码改写，只提供DIAGNOSTIC_PLAN的有界实际pass/texture/clip观测边界；没有SDK patch/Host编译/硬编码pass ID或GUI请求。生产9278原图/profile未读取、未复制、未分享。

## 待Root

接收两个本地提交，唯一决定Main与README patch接入；同资料/方法测新统一候选GUI、处理single-host clone受控对照并预留ZC05三轮。演示前用真实API生成同身份合成记录，没实际核验成功记录就使用UNKNOWN分支。脚本SCRIPT_READY，未录制或发送模型/邮件/日历动作。长期采样未针对Host执行。

本任务未自动push/发布、未申请新权限；19:11:25停止高风险、20:11:25截止，不延期。旧NIGHT004/R5证据和未提交gui_smoke.py保留。
