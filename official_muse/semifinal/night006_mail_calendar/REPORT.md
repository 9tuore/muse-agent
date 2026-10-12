# Mail / Calendar 关联修复交接

待集成补丁：`linkage.patch`。源基线为中央未提交快照 `faf1e253…`，修后源 `d9c3c194…`；**只应用补丁，不覆盖整份 main.splash**。没有改动中央工作区、没有操作 GUI、没有发真实邮件。

修复：邮件的“添加到日历”先保存独立事项与来源；当前回合的真实结构 add/get 回执逐字段相符后才接入行动链。日历查询不再挤掉原日程的改期、删除、确认邮件入口，32条归档滚动后仍可取回。编辑输入立即取消旧候选；对已有日程说“改到12点”，结构化提取新时间后复用同ID改期。正文尚未读到时给出清楚提示，关联写入失败不显示普通成功。

发现并修复了两处集成缺陷：新候选必须补齐通用空字段，否则实际 Chat schema 在重启时拒绝；完整产物从JSON恢复后会改变键顺序，完结步骤改为完整结构比较，并避免完成重试重写同一Run产物字节。篡改字段、跨账号、跨事项及缺回执仍拒绝。

## 定向验证

- `final-linkage`：40/40 FIXTURE_PASS。
- `final-history`：9/9 FIXTURE_PASS，实际 history callback 与独立保存读回。
- `final-create`：原创建回执23/23 PASS；`final-scope`：原事项归属11/11 PASS。
- `full-store-r5`：15/15 PASS，完整生产 Goal/Chat/Calendar 存储、重启恢复及同ID改期；实际模型包装流程由合成 Host 回复驱动。
- `final-completion-serial`：33/33 FIXTURE_PASS，56.51秒。并行版本撞60秒测试脚本上限的原记录保留；改为串行120秒上限，所有断言未变。

以上六组共131项均对应同一修后源 SHA `d9c3c19456fd211df894912954e5bd089bc723c85cb1b64e377a8dca2e94dd2e`。

基线39项中25项 FAIL、初次完整存储 schema FAIL、完结重试 FAIL 与只读根因诊断均保留在 evidence 和 build/night006-mail-calendar。所有 PASS 都是实际 Splash VM；Host、模型、时钟、文件系统边界合成，**不代表 GUI、真实 SMTP、真实 Calendar owner 或三轮验收已通过**。

正式三轮仍由 ZC-05 针对中央签名候选执行。集成后需优先 GUI 检查：邮件按钮→创建→查询→原事件改期/删除→重启→行动链与确认邮件是否还可用。
