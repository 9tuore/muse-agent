# Muse 独立实现与来源

本轮实现依据：用户执行包、当前Muse源码、已有失败证据、锁定官方SDK及其类型/测试。未读取竞争作品源码、Prompt、DSL、截图或私有数据来实现本轮功能。没有把排名目标描述为官方排名。

官方基础通过 `dependencies.lock.json` 固定具体commit，`sdk-overlays/` 保存完整本地差异，`scripts/bootstrap_sdk.py --verify` 逐树校验。来源、许可证、锁文件和本地Calendar/Model/Storage扩展必须随源码交付。

`fs.sha256_file`为本轮必要的受隔离存储接口补丁，不更改文本摘要上限、不提高执行预算、不新增Capability。Calendar是现有EventKit宿主扩展，准入结果只代表配套扩展Host/Hub；正式上游是否接收另行说明。

fixture中的账号、邮件、日程、模型输出与用户动作是测试数据；真实fs、VM、Host协议和Shell运行分别标注测试层。模型文本“完成”不能代替系统事件或投递证明。旧版本证据只在未改变的路径中作为支持，最终候选关键检查重新绑定SHA与commit。

本轮A2曾误进入旧迁移分支并快进至已有开发commit，已记录与纠正，未覆盖未提交工作或push。该协作偏移不隐藏在成功报告中。

最终清洁构建、同候选验收、未完成的人工步骤及模型限制以晨间报告为准；本文件不证明所有门槛已通过。
