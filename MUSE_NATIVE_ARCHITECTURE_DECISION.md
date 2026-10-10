# Muse Native 架构决策 / NIGHT-002

2026-10-11，阶段结论：**保留正式OctoScript版本，隔离验证Rust Native原型；尚不建议正式迁移。** 07:00冻结大改，08:00交付。比赛允许组合路线来自用户本轮明确说明；官方接入边界以下以锁定SDK真实代码为准，不能解释成免权限。

## A / B 比较

| 条件 | A：OctoScript / App Hub | B：Rust Native＋OctoScript / 原Octos Agent |
| --- | --- | --- |
| 正式分发 | 根bundle已有，仍需正式publisher与Gate | Native模块随受审Shell编译；不是普通Hub包放exe/dylib |
| Calendar合法准入 | 商店outbound tool ceiling、共享owner与#182/#427尚受阻 | reviewed native registry可明确声明跨app grant；consent、shareable、owner executor和双方准入仍必需 |
| 创建/原ID修改/删/精确读回 | 配套Calendar组件提案有历史证据；正式Muse Relay未验收 | Native迁移不会自动解决原版get缺失和update/delete owner-only；目前原型仅events只读 |
| Mail | 现有compose/review_send/status受控协议保留 | 完整Shell同一MailService与前台native审阅；不能用Agent或聊天批准代替可信本人动作 |
| Memory / 行动链 | 保留真实存储/授权检索/只读状态投影 | 保留OctoScript业务；原型不复制数据库、不建立第二Runtime |
| Intel构建 | 旧配套Host仍有效 | 完整Desktop r2/r3已实际release编译成功；r3最新真实Calendar owner截图可见，早期空白仍保留，正式Relay/本人批准仍缺，尚不能迁入正式候选 |
| 成本/性能 | rc17为旧稳定基线，新源尚未同候选验收 | 仅有短启动时进程采样，非稳态/峰值/基线对照，不能宣称更轻或更准确 |

## 已实际取得的证据

- SDK固定`4ccf8e068399b1da139771a9ed94cef05fa6ae60`，Hub固定`95e4831afca7227b640f075b252c04355bb63865`。
- 独立`muse-native-prototype`真实Rust AppModule已生成，经官方native_apps生成器/生成结果检查及本目录patch零fuzz检查exit0。中央再次git apply-check并应用到ignored完整Shell隔离源码；只有`os.calendar/calendar.events`grant。
- 原AppModule创建由Shell的injection::claim取得OctosAppService；打开自身device context，TurnFrom(App)沿既有Broker/Kernel/ShellToolHost/Relay调用。未伪造Person、未读Calendar私有文件、未执行系统写入。
- owner准备补丁仅加载reviewed registry已有os.* grants对应executor；不加新grant，不改变原consent/shareable/approval。
- 独立review查出同ID Native片段会与现有muse-goals权限和存储碰撞，该旧提案已标废弃保留，禁止登记。正式muse-goals不改名；新home不拷贝旧consent/凭据/生产资料。
- 固定kernel b0759a57719fd35b3a2da1c5d969bc67538ed516实际release编译及官方stage工具成功；binary/receipt SHA9c3d4b947a9f90f19acfabad0f90cc891525751d418cb333e6e1d83220c4fb0a。完整Desktop r2/r3实际编译成功，冻结二进制分别41198bb8/8008ec14；r2独立Native入口和内置Calendar已在新资料目录启动。Shell日志注册官方Kernel/Model/Octos服务是惰性服务注册证据，不是Kernel模型回合或Calendar Relay成功证据。
- Git下载失败与不完整archive保留。574个完整OctosCode源码blob逐一与固定tree metadata核对，路径override只恢复相同源码，不删除依赖；完整源码checkout与原Git对象尚未宣称取得。Rinx/Cadcraft及11个craft固定全源逐blob核验后路径覆盖，metadata-r11成功1710包/41成员，当前lock SHA5b58c5f5。路径源恢复不是Git对象已补齐。
- 原fs.sha256缺方法失败保留，最小提案已实际编译进reference78ab9efc，Memory+view68/Task23/摘要9/特殊文件拒绝3通过；官方原版仍未接受。三尺寸可见行动链DSL通过不能替代完整Host或Native Calendar Relay。

## 未完成的最小运行验证

1. 完整Desktop已构建/隔离启动；04:44原r3在ready-layout后OS/Metal真实截图可见，r6第二轮也可见。早期r2/r3/r5及首轮r6空白保持失败，未证明缓存绕过或诊断修复，也未完成稳定性验收。
2. 独立Native ID的真实本人consent，以及注入服务、own-ID peer、owner声明/executor的冷启动证据。
3. 实际Agent选择calendar.events，并以Relay/工具回执证明读取，不以模型回合结束当成功。
4. 拒绝/撤销consent、无grant与owner-only工具仍拒绝。
5. 经授权唯一合成事件的真实写入/同ID修改/精确读回/重启/删除，仍需独立共享工具契约与原生可信确认。
6. 相同Host/source/bundle身份下Mail、Memory、行动链和最终20次启动。

Native中文、History严格ID与可选结果见证、垂直滚动已编译进r3；纯History解析器5/5通过，不替代实际AppModule History或工具回执。r2 first-use consent未点击Allow，真实服务注入及Agent调用仍HUMAN_REQUIRED。原型只有events只读grant，不能借此执行create/update/delete。

03:52单点诊断结果：r5实际编译成功（89d1bc5d），与r3相同条件/新资料目录均89控件、无Script错误且正文空白；OS与Metal截图一致。r5记录4次相同函数缓存键对应不同生成代码，但绕过未修正文，不能据此称黑屏根因。Metal已恢复47db4d10原字节，r3/r5冻结二进制及失败证据保留。新的原生迁移仍不建议晋级。

## 决策与交付风险

当前只允许继续隔离原型。普通Hub资源后缀不允许原生执行文件；B的正式交付需要配套Shell源码、补丁、锁定依赖、构建和真实运行证据，以及明确维护者/比赛提交路径。不能把本地扩展通过写成官方接受。

本轮仍保留rc17安装、Host276b2b68及纯OctoScript成果，根活动包不晋级。共享DSL与行动链以只读投影接入现有业务，不改变Memory含义或执行权。10月13日前能否形成可复现原生版本，取决于上述构建、合法准入与同候选验收实际完成，当前不能承诺PASS。

证据与最小原型：official_muse/semifinal/calendar_integration/；独立审查：official_muse/semifinal/runtime_review/；当前构建与来源回执：ignored build/runtime-closure-full-shell-r1/、build/runtime-closure-kernel-r1/。

2026-10-11 04:54补证：官方Mail 6项精确组件fixture和signed Hostoffer10项通过；Native可信Person、Store准入、真实Relay与SMTP仍缺。两独立reference进程UNKNOWN核心恢复通过，verified-history前提缺失保持PARTIAL。新的可见Calendar owner烟测不改变本轮保留A、隔离B的决策。
