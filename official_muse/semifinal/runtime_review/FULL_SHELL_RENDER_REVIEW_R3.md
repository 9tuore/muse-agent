# Full Shell render review — R3：现有诊断的实际范围

**结论：根因 UNKNOWN；下一步选冻结 r5 的短时 remote trace 采集，不再改 cache、不需 Cargo。** 本轮只读；唯一写入此报告。未启动宿主、调用 remote、操作 GUI/consent、编译或改源码，未触碰 stable503。

已读取 diagnostic-result.json、两轮 launch/capture/snapshot/log 和 frame-0 原像素。r3 PID27508/Host8008ec14、r5 PID28073/Host89d1bc5d；两者均89widgets、未发现 ScriptError/script error 文本。保守正文 ROI[420,322,1959,1129]均仅RGB(16,19,21)。r5 shell.log确有4条“VM-local function hash matched different generated code”，cached_shader为0/27；这是实际缓存候选证据，但绕过后 Calendar 仍空，不能称其是正文故障根因。当前 Metal 文件SHA已实测恢复47db4d10503ee4ed70860529f914df8b740c16f2bc04f768fcb9fb69314f5a04。

## 可直接取得什么

| 现有入口 | 确实输出的数据 | 不提供/不能推断的内容 |
| --- | --- | --- |
| `/trace?topics=gpu.drawcalls,gpu.hole,gpu.upload,remote.grab` | runtime开启四个现有topic；`/trace`回读规范化spec | 不修改shader源码/业务，但会改变日志配置 |
| gpu.drawcalls | repaint、pass ID、根draw_list ID、draw_calls_done | 每pass汇总，含递归child；不列每个widget/实例/PSO/clip。计数在实际drawIndexed编码处递增，不证明像素可见/command buffer已完成 |
| gpu.hole | 第一个阻挡呈现的未驻留item：list debug ID/index、item、shader debug ID、wanted/bytes、retained/pub_id、pending/dirty/zero_ink、backing、collector/分配状态 | 只检查已具os_shader_id且slots>0的对象；只报第一个符合条件项、按变化/1秒节流。无行不能排除shader/PSO/geometry/clip问题；不是全部skip原因 |
| gpu.upload | frame、bytes、instances_uploaded、pending、starved、allocation_refusals等 | 仅有upload/pending时输出，主要上传预算证据；不能定位所有shader/几何 |
| remote.grab | capture request IDs、window ID、repaint、尺寸 | 可把/gseq截图绑定到paint日志，不是控件内容证据 |
| `/log?n=1` 与 `/log?since=N` | 远程日志seq及后续日志；平台log handler确实转入remote ring | stdout的println! debug dump不保证出现在/log；保留shell.log |
| `/tweak/state`（保持tweak关闭、不选择控件） | f=repaint_id、shaders总数，读取不触发frame | 数量不是成功PSO数量；不含完整draw-list/geometry/clip状态 |

代码依据：metal.rs:144、364–371、418–474、1408–1421、1502–1515、1817–1825；编码计数1038；remote.rs:1798–1825、2029–2042；log.rs:45–52、259。gpu.drawcalls只在本进程首次200次启用日志时输出，计数不能通过/trace重置；应在截图之前才启用，不要从启动就消耗上限。MAKEPAD_TRACE读取存在于Cx::init_log，但本次优先runtime/trace，避免启动噪声。

## 建议中央只执行这一轮

沿用已验证的 `build/runtime-closure-render-compare-r1/run_calendar_readonly.py` 启动方式、冻结 r5、fresh home、launch-calendar，使用新证据目录和本轮owned port。该脚本有真实/s PID核对与/quit清理；保持无输入、无Allow、无模型/Relay。无需重新构建或改Rust。

在既有脚本 snapshot之后、gseq之前加入/执行以下采集调用，回执全保存：

1. `/s` 核对owned PID与w0；`/trace`保存旧topic，`/log?n=1`保存日志游标N；`/tweak/state`保存f0。不要开启tweak。
2. `/trace?topics=gpu.drawcalls,gpu.hole,gpu.upload,remote.grab`，确认返回topics确为此spec。
3. 一次 `/gseq?w=0&n=3&every_ms=500`，保存JSON与原PNG；随后 `/log?since=N`、`/tweak/state`、`/snap?w=0`。必要时只做一次额外/g以等待异步日志进入ring，不无限轮询。
4. shell.log为完整备份，按remote.grab repaint与gpu.drawcalls/gpu.upload关联。恢复旧topics（spec需URL编码）后沿用既有/quit和owned进程退出确认。所有请求针对这次新启动的owned port，不能使用stable503。

判读：有gpu.hole→首先定位它给出的list/item与上传collector，不能把它直接认作Calendar；没有hole且draw_calls_done>0→只证明该pass编码了一些绘制（可能只有bar），正文仍UNKNOWN；grab相关pass为0→该paint没有编码draw，优先记录pass/list关联，仍不能区分clip与未提交child。若受200条上限或remote日志截断影响，保留失败/缺失，不作阴性结论。

## PSO、geometry、clip的真实获取限制

现有remote/snap、/d、/shader/consts、/tweak/state都没有直接列出完整PSO/geometry/clip实际状态的入口。检查过tweaker op分支；theme只读/数量也不能替代这些数据。不要编造 `/draw`、`/passes` 或 PSO查询API。

已有 `View::set_debug_dump`（view.rs:357–384）可以标记draw-list，但只对已有draw_list的View有效，MpModuleView不是该View；现有remote没有直接调用它的已验证route。Metal dump打印6帧的named实例/动态uniform，包括mapping存在的rect_pos/size/draw_clip等（metal.rs:1073–1115），发生在PSO与geometry的跳过检查之后；它不输出所有未通过项、不显示完整pass/list camera/clip或PSO状态，也不能宣称直接采集齐全。

`shader.bench`只记录源长度、blend和编译时间，且打印在pipeline成功/失败判定之前，无唯一shader id/成功状态，不应拿它当PSO查询。`debug_draw`也有现成打印代码，但需要shader flag；用/tweak/apply开启会改变live shader/布局并可能触发编译，不能当作不扰动对照。

因此本轮先用上述现有trace取得上传/编码边界。如果结果仍不能区分具体正文draw，下一步才是中央明确选择一个受限、可回退的诊断插桩，输出每item的skip理由/PSO状态/geometry布局/clip实值；本报告没有提出新cache改动，也没有声称已有接口能采集这些全部字段。
