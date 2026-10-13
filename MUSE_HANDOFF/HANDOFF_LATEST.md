# Handoff

## Task
单人修复邮箱、对话、日历；基线05930a71，已部署rc11/1b5d0990。

## Result
PARTIAL。用户确认邮箱正常；原生发送回执accepted。rc12待构建部署后GUI复核。

## Changed
Main恢复授权邮箱选择、简化对话输入；SDK patch仅随包本地模型传递JSON schema并限制普通回复长度。版本rc12。保留rc11可运行包。

## Tests
Mail Splash VM fixture42/42；本地模型wire单测3/3；真实SMTP accepted，未独立匹配收件ID。rc12打包5/6，另一项被运行宿主互斥阻止，待停宿主再跑。证据build/recovery-20261013；原生私有GUI图在旧总控worktree同目录，失败保留。

## Commit
本地提交，未推送。

## Remaining
真实新包聊天、邮箱重启回归；Calendar AI调用未通过。当前干净资料仅Qwen0.5B，无MiniMax配置，不能把模型文字当执行。原生Calendar输入自动化未成功，未写事件。

## Important Boundaries
用户要求清理已完成：3缓存、23旧app；源码、账户、日志、截图及回退保留。fixture与真实结果分开，当前未完成三轮全功能验收。
