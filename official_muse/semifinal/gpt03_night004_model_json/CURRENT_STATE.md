# GPT03 NIGHT-004 无效原始模型 JSON

2026-10-12 04:14（Asia/Shanghai）：机制组件PASS，3场景54项。实际已编译SDK ModelService dispatch接受原Main payload与fixture provider bytes，两种原始坏JSON经SDK重试一次真实返回invalid_output；c892 Main原callback回复error/原请求finished，实际存储无候选/Goal/Run/Action/完成Memory，Calendar/Mail/transport均0。合法JSON对照实际经SDK解析。

仅自有stdio wrapper由rustc链接已有SDK rlibs，未Cargo/SDK修改/Kernel/GUI/包重建；Main203函数＋88global逐字提取。源/库及raw bytes/Err/Ok/SHA保留evidence，原14e0384的107项证据未改。重现见README；短交接见HANDOFF_LATEST。

Calendar overlap归GPT01，本单元不重复。官方真实模型/网络/完整包全链不在本机制验收。Root接收复验后可关闭上一单元该JSON机制缺口。
