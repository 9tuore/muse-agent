# Handoff

## Task
GPT-03；基线 48745406。只同步自有 Launcher/package/README 到 rc5，Root负责应用准备与publisher helper。

## Result
PASS（版本与fixture）；成品/真实Hub更新待中央。
Launcher所需artifact、main比较、check文案；package版本、CFBundleVersion=5、main SHA路径均已同步。WorkBuddy pair、资源与Qwen原输入保留，原state只作路径引用。已安装main不同则打开App Hub，正常安装/权限批准后才打开Muse。

## Changed
仅自有三单元及fixture/本交接；未修改Root的prepare_bundle.py、muse_local_catalog.rs、共享SDK或已安装文件。

## Tests
2026-10-11 Launcher 23/23，20.157s；package 4/4，5.859s。新增旧安装main不重写、转Hub更新检查；rc5包版本与原pair字节检查通过。签名stub/合成资源，不是正式Hub实装；无Cargo/GUI/真实模型调用。日志build/gpt03-rc5-package-20261011。

## Commit
本文件所属本地提交，未push；依赖工作pair补丁48745406。

## Remaining
Root helper已升rc5，但观察到Catalog::new仍固定1；当前rc4镜像sequence=1。合法更新须sequence高于设备已验序列（本基线至少2），不能同序不同内容。Root同步序列并验签后，设置MUSE_RC5_MIRROR，按README生成新候选。

## Important Boundaries
不直接写installed main/userstorage，不改floor/cache/本人批准；Kernel新产物另行冻结配套输入。本轮不声称最终GUI或model.complete实调通过。
