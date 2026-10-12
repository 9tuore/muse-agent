# ZC-05 独立用户验收准备

当前只完成准备。81 个原子功能、243 个结果格均为 `NOT_TESTED`；没有启动、读取或点击任何运行窗口。

文件边界：根目录两个 `MUSE_USER_ACCEPTANCE_*.md`、`official_muse/semifinal/evidence/user-acceptance-3rounds/` 和本目录。生产源码、bundle、其他 Agent 文件不改。

`cases.json` 保存功能、依据、前置条件、预期和三轮用户步骤。它依据产品说明及 UI 定义，最终 GUI 发现时补齐实际入口。`prepare_acceptance.py` 只生成准备文档与索引，若已有证据则拒绝覆盖；`--validate` 只离线检查 81/243 唯一性、状态及文件 SHA。

`gui-handoff.template.json` 尚未授予 GUI 所有权。总控必须补齐冻结文件与 SHA256、专属 fixture 端口/PID/原生窗口 ID、实际窗口本地 rect、数据归属和服务出口，明确改为 `GUI_OWNERSHIP_GRANTED` 后才能使用 `ua_gui.py`。驱动检查端口实际监听 PID，要求数据根和 `apps/.host/` 双 FIXTURE_ONLY marker，并对完整生产 state 禁止目录清单拒绝相等、ancestor、descendant；只检查路径，不读生产数据。冻结身份包含 main/manifest/host/Kernel/Launcher/launcher.json/catalog 摘要、Git commit、实际 manifest 版本及 Bundle 指纹；给出的插件逐项核 SHA。生产端口 9696 禁用。

`ua_gui.GUIEvidence` 只使用 Makepad 原生 `/snap`、单次 `/click`、`/k`、`/t`、`/m`。`click(key, pane_key, visual_proof)` 和 `type(key, value, pane_key, visual_proof)` 要求当前控件唯一、未禁用、`w` 与对应 pane 相同，完整 rect 位于真实窗口和 pane 内。native capture 生成待检查的 `.visual-template.json`；测试员必须 `view_image` 查看原生图，再填写检查时间、观察及控件完整可见证明。证明绑定截图 SHA 和当前 widget snapshot 摘要，UI 改变后失效。仅反射树没有完整可见证明即 BLOCKED/先滚动，不能点击或认定成功。输入不带 `wait=1`，不业务重试。不得使用 `Remote.click()` 的帧重试，也不得向产品注入内部函数。

每次尝试单独目录：`round-01/UA-MEM-01/attempt-01/`。保存 `identity.json`、`attempt.json`、`snap-*.json`、`ui-actions.jsonl`、未经修改的原生 `.png`、`visual-inspection.json`、需要时的 `independent-readback.json`、`result.json` 和 `attempt-manifest.json`。捕获使用 `screencapture -x -l ID`，每张图必须通过 `view_image` 实际查看后写视觉观察；截图与工具记录均不能自动决定 PASS。

`record_acceptance.py <绝对result.json路径>` 只记录测试员的实际观察，检查每张原生图的视觉观察及所需独立读回，再追加尝试索引。它再次校验尝试身份中的 PID、原生 window、data_dir 双 marker 和完整候选 SHA，三轮候选 key 必须一致；新 PID 重启可接续相同候选，改动 hash 不能混用旧轮次。它保留全部旧尝试，不覆写失败。`FIXTURE_TRANSPORT` 的通过只能为 `SIMULATION_PASS`；GUI 与真实隔离应用存储分别标 `GUI_ONLY`、`LOCAL_REAL_STORAGE`，不可当作真实邮件或日历外部成功。

正式验收的状态：PASS、SIMULATION_PASS、FAIL、BLOCKED、HUMAN_REQUIRED、NOT_IMPLEMENTED。前置条件未交接仍为 NOT_TESTED。受影响修复后需绑定新的统一冻结候选重跑三轮，原失败证据仍保留。

准备检查命令（无 GUI 调用）：

```sh
python3 official_muse/semifinal/sprint005/zc05/prepare_acceptance.py --validate
python3 official_muse/semifinal/sprint005/zc05/check_guards_offline.py
```

尚未执行：GUI、业务动作、模型、收发信、日历、重启。准备脚本语法与索引检查不能作为这些功能的通过证据。

护栏检查为 OFFLINE_GUARD_ONLY，仅用临时合成路径、摘要、rect 验证拒绝行为，没有 GUI 或网络调用，不能记为用户功能 PASS。
