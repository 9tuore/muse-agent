# Handoff

## Task
GPT-03，基线841ce042。按最新授权，仅自有打包/脚本：外层CF shell直接exec工作Host，撤销NSWorkspace二跳。

## Result
PARTIAL：代码与合成fixture完成；原可见App未替换，新候选真实GUI由Root独占。
外层Info使用原WorkBuddy完整字节（identifier/版本3/Launcher）；rc5与model/state放launcher.json。只一个Native action，无Muse/Hub附加action。Source shell按Contents定位资源，保留HOME、目录与日志；Git/发布脚本正常运行经open调用同一CF shell，诊断走只读分支。

## Changed
package复用完整已签pair并强制双SHA保持；记录脚本/Info SHA，源码与成品脚本相同断言。原profile全部字节保留。编译helper改成校验/后台guardian，不启动Host；持锁、管理Qwen，跟踪原父PID，shell同PID exec Host后退出清理。无嵌套Launcher.app/NSWorkspace/NSAlert。

## Tests
2026-10-11 Launcher24/24，20.093s；package4/4，4.953s。真实clang/ad-hoc签名+stub/合成health，含argc/env/resources、PID连续、重复拒绝、正常/SIGTERM退出、模型清理/锁释放。首轮22/23的旧路由更新断言已改为原route保持，日志保留。build/gpt03-direct-shell-20261011。原Info cmp、shell语法、AST、diff通过。

## Commit
本文件所属本地提交，未push；接续48745406/841ce042。

## Remaining
Root按README新目录生成正式候选并单独验收此入口，不再A/B。Qwen服务就绪不代表Native路由/推理；guardian不改端点，需本人Models配置。原可见app继续使用，本轮未运行真实model/Host/GUI/Cargo。

## Important Boundaries
旧23/4与112fixture不代表此前wrapper runtime成功；Root实际黑屏记录保留。不改shared SDK/root main、installed main/userstorage、凭据、catalog floor或本人批准。
