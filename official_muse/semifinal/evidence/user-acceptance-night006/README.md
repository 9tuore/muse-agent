# ZC-05 独立用户验收 · NIGHT-006

当前仅完成准备，未获得最终候选或 GUI 所有权；没有执行 GUI 测试，没有 PASS。

`acceptance-matrix.json` 是本轮唯一用例与结果索引。它基于当前可读源的实际界面入口整理，不沿用旧版本通过结论。`MUSE_USER_ACCEPTANCE_MATRIX.md` 为同一矩阵的可读视图。冻结时重新核对实际导航、按钮和候选身份；移除或不可达功能保留明确范围说明。

顺序：P0 邮件连续写信、正文/编辑器布局、Calendar 查询/创建/改期/删除/邮件按钮联动、聊天与存储恢复；随后 P1 记忆、行动链和设置；最后非关键诊断入口。每项三轮分别为正常操作、修改/取消/切页、重启/重复操作。每轮使用新的合成测试标识，实际持久化结果另行只读核对。模型、账号或输运为 fixture 时，只能记录 `SIMULATION_PASS`；未完成本人操作的原生授权为 `HUMAN_REQUIRED`。

`ua_driver.py` 提供真实 Makepad Remote 输入及原生窗口截图。它不启动 Host、不修改应用存储、不调用业务内部函数，也不自动判定 PASS。总控需交付 `handoff.json`，明确 GUI 所有权、冻结文件、准确进程/窗口与隔离数据目录。禁止多个操作者同时使用同一窗口。输入操作单次投递；超时后先观察，不重复点击发送、创建、删除等动作。截图捕获后仍须通过 `view_image` 实际查看，再写结果。

```sh
python3 ua_driver.py --help
python3 ua_driver.py validate-matrix acceptance-matrix.json
python3 ua_driver.py --handoff handoff.json --case UA-MAIL-10 --round 1 observe
python3 ua_driver.py --handoff handoff.json --case UA-MAIL-10 --round 1 capture editor
```

每次尝试写入独立目录 `round-01/UA-MAIL-10/attempt-01/`，包含冻结身份、操作日志、脱敏观察、原生截图和手工观察结果。`record` 要求截图、逐图视觉观察、明确预期/实际结果及必要读回；不会因脚本退出成功而记产品 PASS。`manifest` 生成 SHA-256 完整性清单。旧失败永不覆写。候选 SHA 改变后用新轮次目录，不能拼旧通过记录。

正式三轮报告在实际执行后由同一矩阵生成；全部证据齐全且适用功能三轮确实全部通过，才能写 `FULL_3_ROUND_PASS`。当前为 `PARTIAL_3_ROUND_ACCEPTANCE`。

准备验证：Python 语法检查及 9 项离线 driver 检查通过，包括 90/270 唯一性、边界裁剪、邮箱/密钥字样脱敏、单次点击和可信原生按钮拒绝。原始记录在本工作区 `build/user-acceptance-night006/driver-check.json`；这些不是 Muse 产品功能测试。
