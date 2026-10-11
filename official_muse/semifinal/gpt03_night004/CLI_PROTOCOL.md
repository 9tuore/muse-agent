# NIGHT-004 无窗口 Splash VM 协议

真实runner：`/Users/mima0000/.codex/worktrees/gpt03-launcher-preflight/Agent APP黑客松/build/gpt03-night004/target/debug/gpt03-night004-vm`。它使用官方makepad-script 1.0.0的ScriptVm/ScriptVmBase，与仓库官方execution_limits/fn_ref_callback测试相同的初始化和native method注册；没有Makepad窗口、Host或Kernel进程。仅小型独立target构建，SDK只读。

普通执行：`gpt03-night004-vm prepared.splash`。输出最终Splash字符串（probe返回JSON），VM错误写stderr且exit1；指令上限5000万。主源prep用run.py保留生产前缀和行动链函数，只替换列明的存储/绘制边界，把host.request映射到fixture_transport。每个函数SHA写入report；不能把Mock权限、回执或输运当官方整链PASS。

同候选L3桥接执行：`gpt03-night004-vm prepared.splash --rpc`。仅Mock transport调用以下native桥接，生产业务函数仍相同：

```text
runner stdout: MUSE_VM_REQUEST {"method":"octos.session.open","payload":{}}
parent stdin:  {"is_ok":true,"data":{"open":true}}
...
runner stdout: MUSE_VM_RESULT {"checks":{...}}
```

请求/响应均一行JSON，最大1MiB；父driver在收到REQUEST后向runner stdin写一行并flush。父driver负责调用ZC01 CalendarService/Relay和ZC02 Mail/MockTransport helper，留下各自真实日志。runner本身不伪造批准、Kernel或Mail回执。错误/超时必须返回明确的Mock边界错误；迟到/UNKNOWN用原请求记录验证，不能自动补派。

```splash
fn fixture_transport(method,payload,callback){
    let reply = mod.fixture.rpc({method: method payload: payload}.to_json()).parse_json()
    callback(reply)
}
```

可将上面的adapter替换run.py HEADER中的queued fixture_transport。常规回归保留队列，可精确安排账号/版本/事务切换。`mod.fixture.sha256(text)`使用真实sha2 0.10.9，供Mock fs.sha256边界核对canonical摘要。

协议已实际往返验证：fixture.ping请求逐字等于预期JSON，父响应is_ok=true，VM返回rpc_ok=true；日志在build/gpt03-night004/rpc-smoke-r2.log。第一次ping用了Splash保留名称scope作裸literal key，生成错误JSON，已改为字符串索引并核对完整请求，旧日志保留。

安全回归命令：

```sh
python3 official_muse/semifinal/gpt03_night004/run.py --source /absolute/frozen/main.splash --runner /absolute/gpt03-night004-vm --out build/owned-new-result
```

runner源码与Cargo.lock在vm/；重建使用独立CARGO_TARGET_DIR并执行`cargo build --offline --locked --manifest-path official_muse/semifinal/gpt03_night004/vm/Cargo.toml`。Cargo.toml指向现场已核对的SDK Makepad源码路径，不是新增SDK副本或完整Host构建。当前具体函数身份、前后失败和Source SHA见evidence/。

native update仍是下一单元：当前adapter只有create，legacy update不属于正式cap。完整同ID链需要独立update journal，原创建证明不可改写成新add证明；严格get旧→update完整替换→get新，三条同Kernel/摘要/调用顺序，准备/UNKNOWN期间旧Mail和delete失效，verified后新draft绑定新快照。单独调用Rust update helper不能记L3应用链通过。
