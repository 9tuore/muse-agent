# UA-PREFLIGHT-001：原生 Shell 可见，但 Muse / App Hub 正文不可见

结论：独立 PRE_FLIGHT 复现正文不可见，阻断普通用户识别和操作应用。正式三轮没有开始，243 格仍 NOT_TESTED。

候选为 sprint005-preflight-r5-no-gauss，实际已签 manifest 版本 0.4.0-rc7。Main SHA256 ef58430fef4b2f707b78a12f4c4bcd2403b8404c092f5cd73239e5d128a9e750；manifest 7b746fb0871e9e40f30819e4f6d851cda9c61d9ccb595468373cf622307f9714。完整Host/Kernel/Launcher/config/catalog/Git/Bundle身份在identity.json，由测试helper实际逐项核对。诊断noGauss启动包不是最终冻结候选，不据本轮判断最终发布包通过或失败。

步骤：

1. 在交接的真实 native window 663（PID 22287，Remote 9799，1400×805）自行捕获并view_image查看01原生图：顶栏可见，应用正文全黑。
2. 依据01图可见OctoSense菜单，以单次真实点击remote (173,14)、w=0打开下拉。02原生图逐图查看后可见主题菜单正常绘制，正文仍黑。
3. 依据02图可见Muse顶栏文字，以单次真实点击remote (298,14)、w=0关闭菜单。03原生图逐图查看后正文仍黑。

预期：新用户可看到Muse/AppHub应用正文及功能入口。实际：仅ShellBar与主题下拉可见，正文没有可见文字或按钮。/snap同时列出AppHub、Muse、新对话、Memory、行动链等控件；这些反射记录不能代替实际可见性，未点击它们。

影响：基础、Memory和行动链真实GUI发现受阻。没有执行账号、模型、邮件、日历、审批、重启、软件或DB修改；生产9696未访问。UI输入只有上述两次非敏感顶栏导航，未选择主题、未申请权限。

独立证据：3张原生PNG全部保留原字节并通过view_image实际查看；3份snap；ui-actions.jsonl中的2次单独/click；visual-inspection.json；身份和开始结束时间；preflight-manifest.json。原图3024×1834，view_image显示2048×1242，记录缩放3024/2048及窗口像素原点(112,76)、2px/remote-unit，仅用于已可见Shell非敏感导航。

此工单记录症状和复现，不推断渲染根因。GUI所有权已回交ZC-00；ZC-05不再访问9799。最终正式冻结另行交接，PRE_FLIGHT证据不能进入三轮矩阵。
