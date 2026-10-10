# Muse Phone 关机后续跑结果

2026-10-10，状态：**HOME_EMULATOR_UI_PASS / 手机业务全链未通过 / DEVICE_NOT_TESTED**。

## 修复与真实证据

旧 rc16 配套 r7 APK 在全新 API35 模拟器实际崩溃：缺少 `makepad/octosense_shell/resources/themes/mobile-presets.json`。原因是官方 Makepad 打包器的依赖目录解析按空格拆分，漏掉带空格的工作区资源。最新官方源码同一函数仍有该行为。

单函数补丁实际 Rust/文件系统变体：原版4FAIL/2PASS，修补6PASS。锁定官方打包器构建通过、Cargo.lock不变。第一次完整构建因10.5GB资源守护停止；第二次因重建工具缺少原 Phone Java 兼容层失败，均保留。对齐保留基线中已有的三份 Java 文件后第三次构建 exit0。

- APK：`build/phone-home-assets-r3/home-assets-fixed.apk`，246,145,986字节，SHA256 `a7bac6c066c2cbac2d679ae8278e814d837baeb77a3afa4ea115df26f4673634`。
- 主题资源3630字节已包含，SHA256 `8f57abbba088f82113ab242151c3756910b3649050176c84e04bd0f65167aecb`。
- 全部 native库与原 r7逐字节一致，签名验证exit0；并未重写 Phone 业务或更新正式 Desktop。
- API35全新模拟器安装成功，实际Home两次冷启动及一次force-stop恢复通过；首次拒绝定位、重启后取消权限询问，无正向授权。
- 截图：[启动](research/phone-resume/evidence/home-native.png)、[重启](research/phone-resume/evidence/home-restart-native.png)。实际查看过渲染，没有把过渡黑屏计为通过。
- 原始检查：[运行范围](research/phone-resume/evidence/home-emulator-report.json)、[APK身份](research/phone-resume/evidence/apk-identity.json)、[验签](research/phone-resume/evidence/apksigner.txt)。

## 来源与未覆盖范围

SDK基线7f962547、framework基线bf318136带有此前本地配套改动，不是新Desktop rc.2原版。仅新增资源目录解析修补；Java补丁文件记录既有兼容层的来源。旧APK、原SDK/Phone源码、原始ELF和实体设备不改。

Kernel进程未在首个进程快照中观察到；Bridge、手机Muse、真实Agent、邮件、日历及设备兼容在本次续跑未验证。实体手机仍为DEVICE_NOT_TESTED。不能把本页两次Home启动计入桌面rc18最终20次。

官方反馈：[OctoSense #458](https://github.com/OctoSense-org/OctoSense/issues/458)，补充[实际构建和UI证据](https://github.com/OctoSense-org/OctoSense/issues/458#issuecomment-6095819625)。尚未被官方接受。10.5GB组合上限未提高；只清可重建编译缓存、已核验派生副本和本轮无账号鲜AVD缓存。资源停止、Java错误、首次错误的库文件名检查及黑屏过渡证据均保留。

## 截止停止

本轮owned模拟器PID99877已在17:00前发SIGTERM并结束；包装守护返回exit0，但模拟器子进程记录exit-6，停止时的日志保留。此退出结果不能写成自然无错误退出；运行期两次Home证据与停止结果分开记录。夜间心跳muse-07-00已删除。新增真实邮件0、日历写入0、付费调用0。
