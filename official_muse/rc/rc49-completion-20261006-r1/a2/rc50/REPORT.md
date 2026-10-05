# rc50 工作源码：矮窗与快捷入口回归

本次指定的两尺寸交互回归 **PASS**。此前 990×380 历史区挤压导致首尾操作无法完成的问题，在这份工作源码上已修复。**T19 整体仍不能标全通过**：初始完整标题数分别为 1 和 3；若原“四条同时可见”适用于这两个视口，仍未满足。

| 实际尺寸 | 历史区高度：rc49 → 当前 | 导航区高度 | 初始完整标题数 | 首尾选择/删除预览取消 | 快捷导航 |
|---|---|---|---|---|---|
| 990×380 | 40 → 161 | 84 | 1 | PASS | 邮箱、日历、记忆、更多→操作记录 PASS |
| 990×539 | 188 → 285 | 119 | 3 | PASS | 邮箱、日历、记忆、更多→操作记录 PASS |

两个窗口的 `/s` 实际尺寸等于请求尺寸，PNG 分别为 1980×760 和 1980×1078（DPI 2）。各案例保留16条完整标题和历史内容，未确认删除。展开、左栏折叠、两栏折叠和恢复后，输入回读及空消息按钮校验均通过；长正文滚动前后 RGB 像素变化。截图人工复核标题两行省略、删除按钮独立和输入区域可见。

快捷入口采用真实 Remote 滚动及点击，按钮完全位于 shortcuts 矩形内；点击邮箱/日历/记忆后分别核对 `page_title`，点击更多后继续滚动进入操作记录，再返回对话。990×380 下日历/记忆/更多/操作记录分别需2/3/4/5次35点滚动；990×539下为1/2/3/4次。只调用被 fixture 拦截的 mail.accounts、calendar.status；模型调用、邮件发送、系统日历写入均为0。

## 源码与可复现性

- 本次读取 `official_muse/app/source/main.splash`，SHA256 **0e705f33c36c77e32c335c1489a7ebe047a2e6476a473a4678cbffb767ca480f**；先保存本目录 working-main.splash 快照，两个尺寸使用同一份字节，避免 Root 并行编辑造成混合结果。来源/读取时 HEAD 见 SOURCE_BINDING.json。
- 快照含 Root 修改的 `clamp(80px,22cqh,205px)`。本任务未写产品源码；只读取 app/bundle 元数据、资源，在案例副本去签名、stamp并注入合成场景和服务拦截。
- 官方 packaged card-host SHA256 `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`，端口8517，各案例全新隔离状态目录。自建进程已退出；未控制8493或主profile。
- 参数化脚本保存在本目录 `t19_visible.py`，支持 `--source/--out/--navigation`。两次实测使用同一脚本逻辑在父目录执行；归档时移入本目录，仅调整 ROOT 的目录层级，父目录 rc49 脚本恢复原字节，旧哈希证据保持有效。

复现：`python3 official_muse/rc/rc49-completion-20261006-r1/a2/rc50/t19_visible.py 990x380 --source official_muse/rc/rc49-completion-20261006-r1/a2/rc50/working-main.splash --out <新的空目录> --navigation`；第二尺寸替换为990x539。profile、源码快照、bundle及runtime日志只留本地；Git收报告、脚本、快照JSON和合成截图。

范围是 **WORKING_SOURCE / FIXTURE_VISIBLE_CARD_HOST**，不是 Root 最终rc50 Shell。未重测宽/窄窗口；此补丁会改变它们的导航高度，因此rc49宽/窄结果仅保留为历史参考，不直接转为rc50通过。未重包或重做视频；未覆盖默认owner修复、真实Mail→Goal或cold fresh模型链。
