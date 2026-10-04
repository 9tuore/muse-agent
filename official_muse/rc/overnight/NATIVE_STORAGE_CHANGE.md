# 受隔离快照摘要接口

原因：89564字节的真实记忆快照超出`fs.sha256(text)`的65536字节限制；脚本逗号分段摘要方案又触发64ms回调预算。原失败保留，分段实现未进入正式代码。

最小扩展：在已有Makepad storage模块新增`fs.sha256_file(path)`，复用native `target`的根权限、路径限制及symlink检查，只读取普通文件，最多既有`MAX_FILE_BYTES` 1MiB。打开文件后验证metadata，并用`take(MAX_FILE_BYTES+1)`再次限制实际读入字节。输出是文件原始字节的标准SHA256，不是另一种摘要算法。没有网络、第二Runtime或新manifest capability；原文本64KB、执行、heap与存储上限均不提高。

原生Rust `splash_storage::tests` 已实际退出0，新测试覆盖空字节标准摘要、超过64KB的Unicode、1MiB边界、超限、目录与缺失文件。其他三项原隔离测试继续执行。实际VM注册接口、路径越界、symlink拒绝及大记忆遗忘/恢复待新CardHost验证，不以Rust单测代替业务完成。

生产遗忘流程将已清理候选先写入隔离空间并独立读回，再计算原主记录及清理候选的文件摘要，沿用原提交receipt和回退快照次序。摘要失败即停止；重启恢复核对备份字节与摘要，不把“模型说已遗忘”当成持久化完成。

该接口属于明确交付的本地SDK overlay。锁定官方基线commit不改变，overlay与12000文件逐树校验已通过；不能宣称官方上游已接收。
