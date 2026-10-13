# Muse 原生桌面交付

Muse 将对话、全局记忆、邮件与内置日历组织为持续事务。每个事项保留信息来源、当前计划和实际执行结果；新时间更新原日程，并让旧回复草稿失效。

本候选包含 Intel x86_64 的 Muse.app、OctoSense 桌面宿主及内置日历 Relay。宿主基线为 `desktop-v0.1.0-rc.6`，准确源码、依赖和补丁由 `dependencies.lock.json` 固定。根 `bundle/` 是唯一应用源码入口。它需要配套宿主提供 `calendar_bridge` 与相应 Calendar 工具；普通 App Hub 的默认工具集合尚不具备这一组合。

## 使用

将完整交付目录放在可写位置，双击 Muse.app。新机器在应用旁创建独立的 `Muse Data`，包内不包含开发机器的资料路径或账号。首次安装在 App Hub 正常确认后打开 Muse；邮箱和云端模型由使用者配置。无云端配置时可使用随包提供的 Qwen 基础离线模型。

日历例句：`明天下午三点开项目评审会，地点线上会议`。点“处理日程”后查看保存结果。需要改期时在同一事项输入 `改到明天下午四点`；删除使用“删除这项日程”。从邮件正文点击“添加到日历”可携带该邮件的安排，随后可按保存后的时间起草确认邮件。

## 从固定源码重建

需要 Intel macOS、Xcode Command Line Tools、Rust/Cargo、Python 3 和公开依赖下载能力。先准备包含 llama.cpp Intel 运行库、Qwen GGUF 与许可证的公共模型目录；模型来源与准确版本见应用的 `local-model/licenses/NOTICE.txt`。

```sh
python3 scripts/bootstrap_sdk.py --use-cargo-cache
python3 scripts/rebuild_muse.py --work build/rebuild-001 --model-source /absolute/path/local-model
```

入口恢复固定 SDK，构建 Host、固定 revision 的 Kernel 和 Hub，生成构建专用本地目录密钥，进行准入检查、打包及签名。私钥留在忽略的 `build/` 中，应用只携带公开验证材料。重建无需原开发者私钥，不读取用户资料。每次使用新的 `--work` 路径。

有匹配二进制与许可证清单时，可显式传入 `--host`、`--kernel`、`--hub`、`--publisher`、`--licenses`；此模式会记录输入，不能称为所有组件从零编译。Kernel 仍由官方 staging helper 核对固定 revision。

## 发布边界

`release-native.yml` 在匹配版本的 tag 上校验根 Bundle、导出固定源码和 Bundle、生成 GitHub 来源证明与待审阅 Release。正式二进制、视频和验收结果应与该 tag 对应后加入 Release。最终视频、文案和便携应用通过同一版本 Release 分发，使用前可对照资产校验清单。

`publish-app.yml` 保留官方 App Hub 的证明、验证与打包流程，只有仓库变量 `MUSE_APP_HUB_RELEASE=true` 才运行。启用前必须通过公开宿主工具检查；不能用配套宿主的本地准入替代 App Hub 管理员审核。赛事原生扩展交付与商店上架是分别验收的流程。

实际通过项目、失败记录与候选身份以 `CURRENT_STATE.md` 和 `验收证据/` 为准。
