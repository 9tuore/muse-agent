# Qwen fast 目录应用单元

2026-10-11。一个实际可应用的产品目录补丁，新增 `local/Qwen2.5-0.5B-Instruct-Q4_0-offline` 的 fast 记录，ctx4096；原有模型、local-default strong、默认选择及排序算法均保留。未应用到共享 SDK，未构建或运行 Host。Launcher/package 的 rc4 同版本同步由中央负责，黑屏与构建/GUI由 WorkBuddy 负责。

| 文件状态 | SHA256 |
| --- | --- |
| 原 model_catalog.json | `65ee8b16156b33705e9937b8c9dc926e27aa247e30c7689f5ce3185313b91bf6` |
| 补丁后 model_catalog.json | `744ae46b6026ddd152b6c86f63f6acb918b05115d239eecbcb06064e271945a9` |
| qwen-fast.patch | `cf881e50ee6b22cd7b83ff673eb421e54f1218eeb0426aebd0cc997801d71a53` |

目标 SDK 相对路径：`apps/ai-providers/config/data/model_catalog.json`。

## 中央应用与核验

在有写入权的独立候选 SDK 上依次运行，替换下面绝对路径；不要同时改活动构建输入。

```sh
python3 official_muse/integrated_release/routing/apply_qwen_fast.py check '/absolute/candidate/sdk/apps/ai-providers/config/data/model_catalog.json'
python3 official_muse/integrated_release/routing/apply_qwen_fast.py apply '/absolute/candidate/sdk/apps/ai-providers/config/data/model_catalog.json'
python3 official_muse/integrated_release/routing/apply_qwen_fast.py verify '/absolute/candidate/sdk/apps/ai-providers/config/data/model_catalog.json'
```

`check` 只读并核验可应用性；`apply` 在精确 baseline 上重现附带 unified diff，经 patched SHA 验证后原子替换，并保留 mode；`verify` 要求精确 patched SHA。重复应用、源漂移、patch/manifest变化、symlink、错误文件名或准备期间改动均拒绝，exit2；不会进行 fuzzy patch。不存在 force 或覆盖漂移模式。脚本不读取/写入 profile，不保存 provider，不访问密钥、不触发联网。原子写入前检测变化不构成跨进程锁，仍须遵守中央串行写入。

脚本同时对相邻 `muse_launcher.m` 做**静态字段**核对：精确 modelID、`--alias`、`--ctx-size 4096`、loopback动态端口、provider的 `/v1` 路由。manifest内 Launcher SHA仅记来源，**不要求整文件SHA相同**；版本号 rc3→rc4 可通过必要字段校验。静态检查不是运行或推理证明。

SDK目录由 `include_str!` 编进 Host，应用后仍需由中央/获构建权者重新构建；修改成品外部资源不会改变路由。

## 设置与业务前提

保留 MiniMax primary；通过官方 Models 加入对应 local fallback，自定义精确模型 ID、OpenAI 协议，端点用 `local-model.json` 的 **`route_base_url`**。`base_url` 是不带 `/v1` 的健康检查根地址，不能替代 provider 路由；端口来自每次实际启动，不能写死默认8080。Launcher332bf仍仅更新已存在的精确本地alias路由，本单元不自动添加provider。

在 MiniMax-M3 strong + 本地Qwen fast这组配置下，已有class排序得到fast→Qwen→MiniMax、strong→MiniMax→Qwen。一般对话应由中央 main.splash 显式请求strong；已明确的字段提取、短摘要可请求fast。0.5B标签表示这类弱任务的路由分类，不是质量验收或通用对话升级。

fast是偏好，**不是禁止云端或收费**。本地网络/HTTP/无文本失败后会尝试后续已配置云provider，仍须沿用用户已有费用授权；此补丁不扩大授权，也不提供货币预算或local-only。结构化输出校验失败两次后按现有实现直接报错；目录分类不修改这一行为。持续Agent/Calendar Relay/Kernel loop不经这条有界调用路径时，仍继承_main。

## 实际验证

```sh
python3 official_muse/integrated_release/routing/test_qwen_fast.py --catalog '/absolute/unmodified/sdk/apps/ai-providers/config/data/model_catalog.json' --result official_muse/integrated_release/routing/TEST_RESULT.json
```

测试只读指定源catalog，所有写入在临时副本。12项离线测试包括真实脚本check/apply/verify子进程、独立git apply --check及实际patch应用、唯一追加与全部旧模型不变、权限保留、漂移/重复/篡改拒绝、写入失败及并发修改保护、symlink/profile路径拒绝、Launcher字段与版本号兼容、现有稳定rank排序。结果见 `TEST_RESULT.json`。排序断言是Python复现已核对Rust逻辑，尚未执行Rust测试、Host构建、GUI、provider保存/Kernel重启、真实Qwen/MiniMax请求或同Host业务全链。
