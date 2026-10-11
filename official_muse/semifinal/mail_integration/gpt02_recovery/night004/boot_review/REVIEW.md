# R4大库启动：Memory/activity审查及GPT03恢复补丁评审

2026-10-12，只读Root现场及GPT03提案；本聊天Kernel/VM/GUI/Cargo调用0，中央源码/状态0写入。基线Main SHA `8227bbb38637aeba28cfe67e5d120a704bfcaf579910610b6b64a6d414acde0d`。

## 现场与Memory/activity边界

Root R4 state及apps/.host均有实际FIXTURE_ONLY标记。读取时memory.json为114559 bytes，64 claims/128 sources/0 forget，claim history总数0，scope及memory_type/conversation_id/history默认字段均已齐全；activity.json 64项/10177 bytes。goals.json 83100 bytes，32 goals/32 runs/128 actions，状态为8 unknown/120 in_flight，backup为7 unknown/121 in_flight。

Root host.log实际报script time budget exceeded。R4已签名bundle的6779行是core_commit_goals内backup write之后的独立readback比较；与逐个action恢复已经成功8次一致。这次已经进入后续goals阶段，没有证据证明memory/activity先停止。

真实GUI启动顺序为chat→activity→core_boot_memory→gm_boot及分批typed/index校验→goals→calendar→restore。core_memory_valid只查原生容器形状，typed验证由gm_boot负责，不能将前者true当全库有效。gm_boot的大库index每次8项，typed每次2项；scope cache包含完整scope及legacy，time cache按完整文本键，不可绕过或替换。gm_validate_indexed_part每次仍遍历全部128/64外层项，gm_finish_boot仍有全库copy/scope迁移/commit，core_boot_activity仍有64项序列化及字段split；这些是潜在同步成本，本次没有更早预算失败证据，故不增加推测性Memory/activity补丁。

## 已评审的GPT03最小提案

文件：GPT03 `official_muse/semifinal/gpt03_night004_boot_recovery/main-8227-boot-recovery.patch`，实际SHA `fb9920983255377d71a9d58f4bb4ecf25a5d8d1c28ca19760a410c874cfedfb7`。本聊天只在自有scratch进行git apply --check及apply，未写Root Main。提案完整源SHA `caa99c570744d36a5e3b3d890fe56baf6337f506b8e37353e5d79bca9e3e7cce`；仅core_boot_goals改变，579个其他函数逐字一致，静态审查10/10见static-review.json。

**语义可接受。** 原primary/backup选择及core_goals_valid保留，首个in_flight才从core_last_goals复制独立revised；只将这些动作变unknown，保留已有unknown及其他终态、ID/request/payload/scope/时间字段。循环中不commit，收集完后只调用一次原core_commit_goals；没有pending就0恢复commit。不改Goal/Run状态，不推断失败/成功，不发Host请求、不重试、不新增完成回执。

原commit必须先保存整个旧accepted snapshot并独立回读backup，再写/回读全部新primary，全部确认后才发布新内存及core_last_goals。backup或primary普通失败继续原core_restore_goals并返回false；不提前发布revised。profile/权限/Secret路径无变化。新快照备份是恢复前全部状态，避免128次循环造成backup只剩最后一次中间态。

## 关键验证要求

- 0、1、128 pending及已部分恢复的8 unknown/120 in_flight：只有pending状态改变；所有非status字段、Goal/Run、selected_id和其他终态保持，0 pending不写盘，其余只有一次commit。
- backup写失败及backup回读失败：不得尝试primary写入，失败返回，内存回到原accepted snapshot；不得把未独立回读的backup称为有效。
- primary写失败与primary回读失败：失败返回、内存仍旧；backup为整个旧accepted snapshot。回读失败可能发生在实际primary写入之后，必须记录真实磁盘结果，不能声称primary必然未改。
- 成功后再启动：128 unknown保持，0再次恢复写入、0外部重发，原ID/回执/权限绑定保留。主坏/备有效和双坏仍沿原选择与拒绝路径。
- Root真实R5 GUI确认启动后续阶段完成，budget error不再出现。GPT03 debug VM的50M指令及IPC耗时只验证功能与操作数，不能证明production 64ms回调预算已满足；单次83KB commit仍是同步成本。

本评审不替代GPT03的VM失败注入结果或Root实际GUI结果；不启动这些测试，不生成第二份竞争补丁。旧R4失败报告/原文件及大库字节保留。
