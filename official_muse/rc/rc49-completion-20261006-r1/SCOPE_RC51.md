# rc51 界面挂载与可见页面刷新

状态：候选 PARTIAL；这次实现已采纳，不把启动矩阵或原二十项标成全部通过。运行资料使用隔离目录；稳定安装、旧生产和未提交 baseline 保护。

相对 rc50 仅改变 boot、redraw 和 set_page：首次原生控件构建移入 main_mount.on_render，在单独回调挂载一次，再进入既有分段恢复；刷新只构建当前显示的内容，并去掉重复刷新。输入和 ScrollYView 不在普通 redraw 时重新创建。Host 的 64ms 脚本预算未增，未改权限、模型协议、批准或外部动作。三处函数与 19 处关键守卫的逐字对比见 a3/rc51/SOURCE_IMPACT.json。

readable `5c182b67d91182350388b726db64b97dc588be089e9f43951284fa899e0d99f1`；compact `ed4874d1f21464233244410aa5f03d83d74a66ce82a4026a64a8f4539cf778da`；官方 tokenizer 两者 98560 tokens 完全等价。Host `1d7d1674ab7f7d076b301ad033a65ac77f01ea58e414a375930ec87e0372e2d3` 未变。

受影响 UI 覆盖宽、普通、矮和窄窗口，实际载荷和尺寸按 a2/rc51/FINAL_REPORT.md 记载，宽窗使用可读源，后续三窗使用等价 compact；不混成同字节。原 990×380 启动失败保留。Root 实际一次满历史 Shell 六页/输入/16 聊天 256 消息 64 记忆检查通过。最初只挂载不限制刷新时仍触发预算错误；旧进程复用一次为 INVALID，均见 MOUNT_EXPERIMENT_RESULTS.json。

冷启动 r1/r2 失败完整保留：r2 完成 5 次冷，另有退出 RemoteDisconnected、40s 启动超时及旧进程未退出，5 次重开未完成。启动驱动只在已确认关端口后容忍 404/连接中断，quit 等待从 15s 降 5s；总体 40s 不增。最终新矩阵另存 r3，不覆盖原失败。

本地扩展 Gate/check/scan/catalog 仅演练；正式上游 Calendar 准入、发布者登记和独立审核仍未通过。新邮件源为 rc49，日程候选为 rc50，系统事件未获新窄范围批准且未写入；不能拼为 rc51 同最终外部整链。GPT 唯一通道返回 HTTP200 text/html 而非有效模型 API 响应。保持待确认/错误，不造本人收件声明、不重复发送。

## 工具故障记录

首次通过 shell stdin 写入本说明时，Python 返回 Non-UTF-8 SyntaxError，脚本在执行前失败，后续 exact commit 因文件不存在失败。现场 `/usr/bin/python3` 和 Command Line Tools Python 均为 3.9.6；不能据报错声称机器是 Python 2。改用 apply_patch 写入 UTF-8 文档，复制操作使用纯 ASCII 脚本；原失败不计为测试通过。
