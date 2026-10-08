# rc16 本地复现包

成品：仓库 `build/7h-delivery-r1/Muse.app`。构建脚本仅生成新的隔离副本，已有输出目录存在时拒绝覆盖。

已执行构建、原生启动器编译、严格深度验签、单条本地目录签名核验及 `muse-launcher --check`。源码为 rc16 / dd2ce025，Host 为 276b2b68，与桌面最终候选载荷相同。完整六文件身份见上级 `source-component-r1/bundle-promotion.json`。

包含既有 Qwen2.5-0.5B Instruct Q4_0 与 llama.cpp；沿用现有启动器和官方 model.complete，无第二套 Agent Runtime。空模型配置可由既有启动器自动配置本地基础模型。启动器环境变量改为 `MUSE_7H_STATE` / `MUSE_7H_REMOTE`，默认资料目录为 `~/Library/Application Support/Muse Seven Hour 20261008`。

不携带账号凭据或生产资料。首次邮箱使用必须在该新目录通过原生窗口登录；官方凭据仓库按规范资料路径隔离，复制邮件缓存不能复制登录。新的外层应用 ID 为 `org.xinghai.muse.7h.rc16`，日历权限需要系统正常确认。

该复现包尚未在全新收件 Mac 进行窗口、模型及真实外部全链验收。最终桌面冷启动 10+5 测试使用相同 Host/业务载荷、外层测试身份 rc14，不冒充该新 rc16 外层身份已重新完成全矩阵。成品为本地 ad hoc 开发签名，未公证、未发布、未获上游 Calendar 扩展接受。

成品目录约 547 MB，未生成本轮 ZIP；不把目录大小当作压缩包大小。构建记录与资源检查分别为本目录 `DELIVERY.json`、`launcher-check.txt`、`verify.txt`。
