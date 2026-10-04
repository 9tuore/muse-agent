# Error category Card fixture

建议源 SHA `977c00ec`；公开提取脚本 SHA `6170fd70`。首次实际 Card 执行：26/26 分类及失败 trace 用例、16/16 中文提示对照用例通过；成功 meta、缺 meta 和原文排除检查也通过。Host 是实际 r2 Card `52768f57`，使用现有 regression_run/runtime_probe。

仅验证实际函数和合成 trace 投影片段；未执行完整 muse_model_request/send_chat、真实模型、产品集成、T17 或 RC_READY。原始运行目录、状态、日志、Root 私有建议源不在公开白名单中。

model_error_code、model_user_error、storage IO 和所需 gm helper 均逐字提取自建议源。旧 UI control 来自33d5d2快照；移除新增 refused/truncated 两行后与旧函数逐字一致。Host callback 开头直到 storage_write 的 trace 代码也逐字提取，但置于明确标注的 fixture projection，request/current 上下文为合成。实际 Card 隔离 fs 写入和读回验证序列化结果。占位详情明确为虚构，未使用真实凭据。

26 个分类用例包含官方10类及 cancelled/memory_conflict、nil/number/bool/array/object、未知/空串/前导空格/大小写/相似前缀/内嵌前缀/缺冒号，以及4096和4097字节。错误类型与超长输入只记录 unknown。失败 trace 只有允许的 metadata 和枚举，没有 raw error/detail。16 个 UI 用例保留14种旧映射，验证 refused/truncated 新中文提示。成功 meta 与无 meta 路径保持一致。

首次准备使用0a661绑定时，Root已更新建议源；SHA检查拒绝，退出1，发生在Card启动前，未生成fixture。ERROR_CATEGORY_PREPARE_FIRST_FAILURE.json保留这一失败。随后Card仅启动一次并全部通过。旧M3 S02和M2.7 D07类别仍为UNKNOWN，T17仍不PASS。

## 公开提取脚本的复现入口

使用全新的可丢弃目录，不覆盖旧证据。将公开脚本作为 main.splash，配上已验证 app/bundle 的 manifest、listing、icon：

```sh
mkdir -p official_muse/rc/memory_model/error-category-public-repro/assets
cp official_muse/rc/memory_model/error_category_functions_r1.splash official_muse/rc/memory_model/error-category-public-repro/main.splash
cp official_muse/app/bundle/manifest.json official_muse/rc/memory_model/error-category-public-repro/manifest.json
cp official_muse/app/bundle/listing.json official_muse/rc/memory_model/error-category-public-repro/listing.json
cp official_muse/app/bundle/assets/icon.svg official_muse/rc/memory_model/error-category-public-repro/assets/icon.svg
python3 official_muse/rc/memory_model/run_contract_probe.py --bundle official_muse/rc/memory_model/error-category-public-repro --out error-category-public-run --probes error_category_fixture_r1 --minimal-bundle-copy --host <verified-actual-CardHost-executable>
```

要求8510空闲。相同运行绑定使用Host SHA `52768f5750b51574c892f7d51dbf33422511c0a615bd2027687e34874e0c6837`。本轮未执行上述公开复现命令；新Host/manifest的运行必须保留自己的实测结果。读取26+16个真实用例数量，通用runner的6个汇总布尔检查不是6个用例。run_contract_probe.py及两个底层runner是已存在、未修改的公开依赖。

prepare_error_category_fixture.py用于原始私有建议源与旧control的绑定，需要本机保留33d5d2快照；它不是公开复现入口。error_category_functions_r1.splash已含所有必要函数、投影片段和fixture stub，可独立用于上述现有runner。

Root清理schema Cargo target后，目录外manifest/lock/src/306报告的SHA仍匹配。此fixture不依赖Rust target，也不调用Cargo。仅按ERROR_CATEGORY_PUBLIC_ALLOWLIST.json逐文件处理，不递归暂存原始目录。
