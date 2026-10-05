# rc13 邮件缺地址追问：实际 CardHost fixture 验收

**FIXTURE_PASS：13组、262项布尔检查通过，含5次独立第二进程恢复。**

实际CardHost运行当前生产函数、默认预算与隔离文件存储。Host/model响应是合成fixture，不是实际M3、QQ邮件收发、系统Calendar、最终Shell或T18通过。A2没有修改产品/SDK/Git、使用GUI或读取private profile/凭据。

## 冻结身份

- rc12 readable：`191e17086435de00c88951be2e445d9dc6e30a4819ac5bada60c6e54001292c7`
- rc12 compact：`149c36279f4a2c08634705dab88af9b5de143143d9561c3f869ff40f38c1fffe`
- rc13 readable：`53c8c0d9a0ebf2c1ec979b9e6c1a11100e6f190af94b978fe23486cb55ebe6ae`
- rc13 tested compact：`754962b96f60fe2022f6f40923e478e2aa4d72f5e6a5304bc29d4bdc8007dc90`
- CardHost：`52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`
- 实际Card：`official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host`。
- 默认Card路径已不存在；使用Root明确允许的现存5276，import前设置MUSE_CARD_HOST。
- 逐字节核对rc12→rc13完整readable：仅增加`prior.state != waiting_user`早退及版本文字；其余相同。
- compact使用既有项目工具，本轮未重新做tokenizer等价验证，不把变换当AST证明或上游认证。

## 实际覆盖

| 组 | 真实Card fixture检查 | 第二进程 |
|---|---|---|
| flow | 空to→waiting_user；recipient action/need与原请求持久化；纯地址补充→Mail schema→唯一完整候选→成功保存 | 候选恢复，无模型重放 |
| waiting_restore | 先保存缺地址等待状态 | 等待状态字节保持；补纯地址→完整候选 |
| scope | 不同project/owner不合并、不进入旧历史 | — |
| refs | missing和expired Memory refs不合并、不进入历史 | — |
| forgot | 实际gm_save/gm_forget后，旧原话不得重新合并 | — |
| invalid_address | 11种多地址/分隔符/空格/换行/多@/缺本地部分/无域点/域点开头/尖括号/制表拒绝 | — |
| topic | 新知识/日历/Goal/取消/普通话题不误合并；最新普通回复后补地址安全早退；Mail等待不用于Calendar补时 | — |
| bounds | 合并2400字节允许，2401不合并 | — |
| metadata | 12种非法元数据拒绝，普通error不入模型历史 | 损坏主/备份拒绝且字节保持，无模型重放 |
| cancel | 取消无新模型请求；随后地址进入普通对话，无Mail候选 | — |
| plain_metadata_guard | success无action、普通waiting无action、Mail waiting无need、error、cancelled五种均返回原地址，不读缺属性 | — |
| calendar_flow | 沿用旧Calendar完整缺时间→补时间候选标准 | 候选恢复，无模型重放 |
| calendar_malformed_meta | **旧标准保持**：把Calendar action改成Mail但无recipient need仍拒绝 | 坏存储拒绝并保留，无模型重放 |

所有组均核对无系统服务请求、无Goal Run或外部Action。除明确注入坏存储的组外，保存状态schema有效。候选未外部执行。

## 保留的失败与归属

1. **rc12真实产品缺陷**：`evidence-r1/topic/first/runtime.log`。最近assistant是普通success，没有clarification_action；helper允许success上下文后直接读缺属性而trap。A2报告后，Root只增加waiting_user状态早退并递增rc13；A2没有改生产源码。
2. **新fixture错误断言**：`evidence-r1/flow`与`waiting_restore`把模型最后用户content期望为纯地址；真实muse_model_request会追加固定相关资料说明。修正为已核对的地址前缀检查，同时保留原请求历史、地址、Mail schema及完整主题/正文候选检查；合成模型input可独立查。旧Calendar标准没改。
3. **fixture集中回调预算失败**：`evidence-r1/invalid_address/first/runtime.log`，11地址检查一回调触发默认script time budget。改为各自timeout；没有提高预算、删变体或缩短输入，原日志保留。
4. `evidence-r2`仅同rc12冻结源的flow/waiting_restore/invalid_address三组修正验证。最终完整13组是`evidence-rc13-r1`，不把rc12结果改标签为rc13。

## 证据与复现

- 最终摘要：`evidence-rc13-r1/summary.json`，SHA `283b968ab68799c80f23cb2b3c4f2ef253f84449e2ab5cf3d2820238831b7789`。
- 各组实际first/report.json、runtime.log、隔离state及probe源码保留。
- 五组restart-report.json/restart-runtime.log/restart-bundle与相同隔离state保留。
- `PUBLIC_RESULT.json`记录逐文件长度/SHA、原失败与范围，不含生产资料。
- 既有regression_run只替换复制源码的Host transport、redraw/set_page/calendar_enabled/mail_redraw与root widgets；生产send_chat/history/schema/存储真实执行。无实际模型推理或系统动作。

在仓库根目录，以**全新自有输出目录**复现：

```sh
PYTHONDONTWRITEBYTECODE=1 python3 official_muse/rc/core_chain/morning-mail-clarification-r1/run.py \
  --source official_muse/rc/core_chain/morning-mail-clarification-r1/evidence-rc13-r1/readable-bundle/main.splash \
  --expected-source-sha256 53c8c0d9a0ebf2c1ec979b9e6c1a11100e6f190af94b978fe23486cb55ebe6ae \
  --host 'official_muse/rc/packaging/.local-state/chunk-delta-r2/Muse Chunk RC Card Host.app/Contents/MacOS/card-host' \
  --out official_muse/rc/core_chain/morning-mail-clarification-r1/NEW-OWNED-EVIDENCE
```

port8509必须空闲；遇他人实例停止，不接管。只结束自己创建的Card进程，不据此宣告UI_PARITY/READY或升级T17/T18。

下一步由Root在实际rc13 Shell/M3验证缺地址→补地址和零自动发信，再继续本人精确授权的真实Mail/Calendar链。A2不读取其private raw。
