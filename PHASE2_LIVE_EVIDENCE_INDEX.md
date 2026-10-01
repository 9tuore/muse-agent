# Muse Phase 2 实机证据索引

最终候选0.2.8，所有after来自真实正确渲染窗口。基目录 `evidence/phase2-live/20261001/`；`candidate.json`记录版本/源哈希/计数，`SHA256.json`记录每个交付证据哈希。before是用户执行包提供的历史真实截图；history-0.2.7是本轮此前版本，不能替代最终8。

| 证据 | 路径（相对基目录） | 实际证明 |
| --- | --- | --- |
| 历史独立/官方参考 | before/ | 历史真实像素参考；未冒称本轮新拍旧版 |
| 中文八页/结果/Host空登录 | after/pages/ | 最终可见UI；没有登录凭据或真实邮件 |
| 三个模型Goal | after/goals/ | 各1Run、model建议、批准、结果SHA与源一致 |
| 指定三轮Chat | after/chat/、chat-repeat-2/、chat-repeat-3/ | 第2次语义失败全部保留；总2/3 |
| 原生消息观察 | after/chat/wire.jsonl | 真实请求转发不改写；仅合成问题明文，其余role/hash/长度 |
| Calendar三动作六图 | after/calendar/ | 真EventKit、批准、独立读回与删除不存在；driver首次失败保留 |
| 五尺寸真实发送 | after/layout/ | 请求/实际尺寸、输入/发送rect、真model成功 |
| 矮窗长文 | after/long/ | 727字8项、Storage/readback；不代表模型长文通过 |
| 最终打包重启 | after/restart/ | 23哈希、Goal21/Run19/Action15/Memory3不变；只增1restore |
| 原Memory更正/遗忘 | history-0.2.7/memory/ | 已更正/固定/墓碑操作；最终8重启保持 |
| provider/格式/渲染历史失败 | failures/、history-0.2.7/ | 历史真实失败证据，未删除或伪装通过 |
| scan七问自审 | local/phase2-028-scan-review.json | 本地人工human-review；不是正式reviewer/上游PASS |

独立UI Agent逐张查看最终五尺寸截图；Core Agent只读核对Goal、wire、Memory和23哈希；Host Agent只读核对包、源码get guard、三份系统收据、六图和重启。独立审计没有重复外部动作，其结论依据总控实机执行证据。

纯源码导出包含源码、补丁、测试和报告；大型截图及配套.app位于桌面实机交付文件夹/ZIP。模式扫描覆盖源码及交付文本，文件名检查排除私钥/配置/数据库。截图由实机查看核对，不把文本模式扫描当作像素或正式安全审计。没有正式签名、发布、push或issue评论。
