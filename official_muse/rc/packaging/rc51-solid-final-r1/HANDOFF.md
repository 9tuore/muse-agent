# 实包交接

结果 FAIL_SIZE_LIMIT_CONTENT_VERIFICATION_PASS，详见 FINAL_REPORT.md、SIZE_FAILURE_VERIFICATION.json 和 PACK_FAILURE.json。最终 frozen F=a4cf4d9e；唯一 packer 调用超 500MB，随后只验证同 ZIP，没有重新打包。

桌面新展开目录、超限 ZIP、实际 rc51 视频和明确状态文件保留，旧49未动。完整 2180 源码逐文件/集合/mode/SHA 及运行 symlink/CRC/验签/launcher/Hub 已独立验证。没有 native GUI、模型、邮箱、Calendar 调用，没有两 Mac 实测。

不要把此次 ZIP 发为小于500MB成功包，不要删除唯一失败。Root 可选择可逆整体高压封装等最小方案，在新证据目录再验证；当前没有执行该方案，不修改权重或宿主。只提交安全报告，生成包、权重、private 和解压副本均不提交。
