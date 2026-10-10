# Calendar既有只读调试入口冷加载提案

中央在r7 fresh资料中实际观察Calendar owner网格与System“No model provider”窗口，现有调试read在声明预检查停止；0写，正常quit0。ZC01和B真实聊天只读复核认为可提前执行既有Calendar懒加载，仍不得增System grant。

`calendar-system-read-cold-load.patch` 仅在测试入口解析owner==os.calendar时调用已有 `ensure_loaded("card.os.calendar")`，随后仍risk=read、JSON/schema、固定System grant、admission及真实Relay。加载会安装Calendar原有声明/executor/manifest配置，不能称完全无注册副作用；不创建模型、Agent、UI或第二Runtime。不变更identity、审批、商店工具准入或CALENDAR_TOOLS。写工具仍被入口拒绝，get虽read仍NOT_GRANTED。

新增冷加载组件测试在独立子测试进程验证owner登记、Agent未准备、System grants不变、未给Muse跨app grant、四种非read工具被拒绝。r8完整SDK三个针对测试各1/1通过，Desktop release实际构建exit0；编译前后输入摘要一致。冻结二进制SHA baf55d24c3245ca858e68b9776d7f470558d619c65edc4ce288ceb90c8a276b7，124126536字节。真实独立窗口只读诊断8项通过、quit0、无运行错误；events实际空列表、limit=0拒绝、get仍not_granted，四种写工具前置拒绝。公开构建及运行回执见desktop-r8-build-result.json与calendar-r8-system-read-result.json；默认正式路线不改。`prepare_full_shell.py --system-read-review` 才显式带本补丁。该提案和后续实测只证明配套宿主调试路径，不是官方原版接受、Muse Agent、模型决策或原生可信批准证据。
