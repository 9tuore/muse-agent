> R2（2026-10-12）：中央接入NIGHT004_real_kernel_calendar_r2.patch，完整end/location/notes与同稳定request_id重试已纳入；创建和更新六字段、id/request_id与存储event count=1均有断言。实际owner binary七步参数核验PASS（OWNER_FULL_FIELDS_RESULT.json）；R2 apply check/逐字比对/syn解析PASS，未编译未运行Kernel。R1补丁/结果保留。只读reader已在46f3a773交付，路径/权限未变。

# NIGHT-004 ZC01

2026-10-12：中央基线2395a70c/main SHA768e295d。首单元30bc0fdc，L1真实CalendarService九个独立进程完成创建、同ID回读/更新、旧expected与外owner拒绝、删除、不存在和重启持久化；OWNER_RESULT.json和owner-build.log保持原样。

真实Relay/Schema/审批Router组件fixture：RELAY_ATTEMPT2.json/raw relay-attempt2.log记录6通过0失败，nice10/jobs1、22.543秒。包含owner生命周期、错误caller/owner/system、缺consent/签出、owner/caller撤下、审批拒绝/dispatch前撤grant、缺expected拒绝。第一次编译E0282真实失败（133.729秒）与日志保留，修正局部Arc类型后重试。审批sheet手势/consent/catalog为synthetic fixture，不是本人真实同意；此项为L2组件证据，无Kernel。

只读helper read_calendar.py兼容中央runner：argv[1]=CENTRAL/build/night-004/calendar-gui-r1/state/apps/.host，stdin={owner:os.calendar,method:events|get_event,args:{...}}，stdout={fixture_authorization,process_id,result:{ok,data|error}}。root必须已标FIXTURE_ONLY；Rust guard只接受gpt01-night004-*临时根或中央build/night-004内的canonical目录；只开放读方法。READONLY_RESULT.json：两次真实读及Python/Rust两层写拒绝PASS，事件文件SHA不变。重新构建binary SHA见该证据。GUI/root具体接入待中央验证。

状态PARTIAL：真实Kernel+局部模型fixture的签名Muse→Calendar旅程补丁已准备；patch check/逐字比对/现有syn语法解析PASS，本测试未编译未运行，待中央唯一完整Host构建。新增精确filter/命令协议见KERNEL_PATCH_README.md。reader已加shebang/0755，中央runner直接exec协议实测PASS。无共享SDK/main/bundle/target写入、无生产资料、无费用或外部动作。
