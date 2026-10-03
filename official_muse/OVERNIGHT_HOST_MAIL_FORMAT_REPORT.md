# 夜间 Host 邮件格式转换核对

2026-10-03（Asia/Shanghai），结果 **PASS（纯函数格式 fixture）**。原始 RFC822/MIME 输入调用真实 `network::decode` 后接真实 `normalize`，新增5项测试通过；没有构造预先转换的 `body` JSON替代转换链。没有真实联网、登录、账号读取或发信。这不是官方邮箱 full-chain 验收。

## 冻结边界

总控正在用的新Host为 `mail-host-033/OctoSense Muse 0.3.3 UI-candidate.app`，本机候选可执行文件 SHA256 在测试后仍为 `f5989ea3b5a80a357eda4fde5a64684f4adc7e0c0b441f46b8c706845dd5f215`。冻结 Host lib仍为 `bebdedd540046c1d8839433e47aad2f233a59707568dd3d21edcc9dfad8948b5`，network仍为 `90a6f5a4f76eb286077284e81446c0e2d9aa8f6184e28e91c5402d381a8e5ef4`。

实际测试副本在 `app/build/ui-memory-20261003/host-mail-format-tests/OctoSense`，从冻结副本用APFS clone复制，只在该第二副本添加 `#[cfg(test)] mod overnight_mail_formats` 和测试模块。网络实现、HTML实现、Calendar、Cargo清单和锁文件均与冻结副本SHA相同；没有修改冻结源码、main、任何Release逻辑或重建/覆盖.app。仅复用原target的debug编译缓存。

## 真实实现与已有覆盖

路径均相对上述OctoSense源码根：

| 边界 | 实现 | 原有纯函数测试覆盖 |
| --- | --- | --- |
| 空发件人 | `apps/mail/host-service/src/network.rs:371`，解析From后没有地址时sender为“未知发件人”，address为空；没有display name但有地址时sender使用地址 | 原有格式测试未断言这些分支 |
| 空主题 | `network.rs:419`，trim后为空使用`(No subject)` | 原有格式测试未覆盖空/缺失Subject |
| plain优先 | `collect_parts`收集plain/html；`decode`仅在plain.trim为空时从HTML提取text节点 | `network::tests::mime_decodes_encoded_subject_and_multipart_body`使用真实原始multipart MIME；Base64 plain正文被选中，UTF-8 encoded subject为`Hello 世界`，HTML仍保留，id稳定 |
| HTML-only UTF-8 | `decode`先按MIME charset/transfer encoding读取HTML，无plain则用scraper text节点作body；`lib.rs:357 normalize`再安全重建HTML并替换fallback正文和preview | `html::tests::mail_html_is_rebuilt_from_safe_tags`纯函数测试HTML重建，但不经MIME；`tests::an_app_signs_in_on_the_hosts_sheet_and_reads_and_sends_without_the_password`用fake transport与预设HTML/body JSON检查normalize后的body，仍不是原始HTML-only MIME UTF-8转换测试 |

上述3个既有测试在7f1a239交付的邮箱服务日志中实际通过（11通过/0失败/2原测试跳过），证据为 `ui_memory/host-login/mail-service-tests.log`。本次没有把这3项重复记入新增5项结果。锁定解析依赖为mailparse 0.16.1、scraper 0.24.0，核对来自Cargo.lock。

真实POP3 fetch在network内调用decode；IMAP `imap.rs:197/203`调用同一decode。Host sync在 `lib.rs:554`把每条fetched message经过normalize再保存。HTML decoder fallback直接取所有text节点，可能含style；normalize会重建安全HTML并删除该fallback的style文本。normalize保留非空独立plain正文，但判断也包括body恰好等于HTML fallback的情况，不能从这些测试推断任意MIME结构都绝对保留原plain排版。

## 新增测试与实际结果

测试源码、仅测试patch、复现安装脚本、执行日志和JSON在 `ui_memory/host-mail-format/`。

| 完整测试名 | 原始输入与断言 | 结果 |
| --- | --- | --- |
| `overnight_mail_formats::empty_or_missing_sender_and_subject_use_host_fallbacks` | 两种RFC822输入：缺失From/Subject、显式空From/空白Subject；UTF-8 plain正文真实解码，断言未知发件人、空address、无主题fallback和原正文 | PASS |
| `overnight_mail_formats::sender_without_display_name_uses_parsed_address` | 原始From仅邮箱地址，断言sender/address取解析后的地址 | PASS |
| `overnight_mail_formats::alternative_plain_body_wins_in_either_part_order` | quoted-printable UTF-8 plain与不同HTML内容的multipart，分别交换part顺序；decode与normalize均断言plain获选 | PASS |
| `overnight_mail_formats::html_only_utf8_base64_decodes_then_normalizes_to_readable_body` | 将含中文、entity、两段正文和style sentinel的HTML编码成Base64 MIME输入；decode确实还原HTML并产生fallback，normalize产生中文段落正文/preview且清除style sentinel | PASS |
| `overnight_mail_formats::whitespace_plain_part_falls_back_to_html_utf8` | 原始multipart的plain仅空白，HTML为中文；断言真实回退后的可读正文 | PASS |

执行命令（在第二源码副本根目录）:

```sh
CARGO_TARGET_DIR='/Users/mima0000/.codex/worktrees/muse-ui-global-memory/Agent APP黑客松/official_muse/app/build/ui-memory-20261003/mail-host-033/target' cargo test --locked --offline -p octosense-mail-service --lib overnight_mail_formats -- --test-threads=1
```

实际结果：`5 passed; 0 failed; 0 ignored; 13 filtered out`，编译完成10.43秒。筛选只执行这些纯函数测试，既有真实网络、Keychain和fake Host service测试未执行；编译的既有dead-code/manifest警告保留在日志，没有本次测试失败。没有运行Release构建。

## 简短交接

分支 `codex/muse-ui-global-memory`，开工现场HEAD `b3c8cbf`，本报告与测试文件独立本地提交、未push。总控负责CURRENT_STATE及最终验收收口，main和Host.app冻结保持。新增测试仅交付为test-only patch，未并入冻结Release。真实邮箱接收、账号鉴权、特殊字符集或更复杂MIME结构不在此次已验证范围；无需等待总控或用户操作，本聊天此项工作完成。
