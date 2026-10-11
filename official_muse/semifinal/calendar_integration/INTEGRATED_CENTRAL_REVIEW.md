# 中央 cold-launch / local catalog 窄静态复核

2026-10-11。状态 **STATIC_REVIEW_ONLY / NOT_COMPILED / NOT_LIVE**。只读复核两项中央新增实现及必要的现有 API/launcher 上下文；本聊天唯一新增文件为本报告，没有改共享SDK、旧history.rs、中央工具，也没有执行Cargo、GUI、模型、日历、外发或Git。未读取任何实际工作私钥、证书文件、用户配置或Secret；仅查看工具如何调用这些输入。

结论：在稳定、冻结的Bundle输入和指定本地配套Host下，未发现这两项变更绕过Gate、publisher签名、原catalog/floor、owner身份或native consent的路径；未发现可由当前API签名确定的Rust类型错误。cold-launch已补上先前“绕过正式Backend直接冷开Card”缺口。存在两个小的产物核对缺口，另有必须保留的本地准入/运行时条件；以下不等于编译或正式验收通过。

## 1. 冷开补丁：静态链成立

补丁目标 `sdk/crates/shell/src/apps.rs::module_open`，仅 `module.id()=="card"` 且解析得到 `manifest_id=="muse-goals"` 时，调用现有 `pub(crate) script_apps::admitted_bundle(&str) -> Result<(PathBuf,PathBuf),String>`。在同一crate内可见；`?;`可以合法丢弃成功的tuple，并向原Result传播String错误；guard与script_apps的cfg完全一致。

原链：`launch_module_as → module_open → admitted_bundle → check_script_app_id → data_root_if_set → admission::installed_bundle → CatalogChannel::from_environment/read_cache → accept_catalog → check_verified_catalog_floor → configure_muse_calendar_offers → Store::may_run`，成功后才继续schema.validate和module_host.create。mobile_app亦走module_open。没有改成system_app、没有写consent或切developer grants_all；未准入、digest/manifest/withdrawal/floor错误会在Card挂载前返回。CardAppView稍后仍使用prepare_launch，保持原启动snapshot校验，不因这里返回路径就直接执行可变jail源码。

前置条件：runtime_host::init已设置apps root，system_card_apps/register_host_services已显式启用宿主ceiling；若调用顺序未满足，错误仍是fail-closed。已读现有启动器，它设置隔离OCTOSENSE_APP_DATA；cold patch本身不伪造root、不安装bundle、不补造catalog。须中央实际确认第一次已安装冷开；本报告没有跑窗口。

## 2. local catalog：签名与权限边界保持

`muse_local_catalog.rs`先限制初读manifest的ID/version为muse-goals/0.4.0-rc3；使用固定publisher与公开验证key构造PublisherKeys。只在局部HostLimits.default上添加events/get_event/add_event/notify，原check_bundle、entry_for、pack_dir、unpack、verify_catalog实现均未改。没有扩大update/remove，也没有给os.*或其他ID使用system limits。

签名链不仅依赖 `check_bundle`：原entry_for在report.passed后再次核对manifest、ID、version、digest与GateReport；有signature时要求key_id与固定publisher一致并用固定public key验签；无signature但指定非空publisher_key时明确拒绝。因而即使默认Gate对unsigned只产生warning，此工具也不能输出unsigned entry。固定public hex实际64字符/32字节，未发现格式长度错误。Catalog先由working key签名，再以所传anchor验证working certificate与catalog签名；任何失败均在create_dir(output)前返回。没有打印私钥内容。

类型核对：check_bundle四参数、entry_for七参数、packet/pack_dir/unpack参数、HubKey::from_bytes(&[u8;32])、Catalog::new(u64,&str,Vec<Entry>)、verify_catalog均与本地定义匹配；GateReport.digest为public String，json/render/passed可用；Packet/Pack/Catalog都有Serialize。hex/serde_json为Hub实际依赖。独立rustc构建仍需中央正确提供各--extern和edition，未执行编译，不能担保链接或borrow checker最终结果。

## 3. 两项最小收据修正建议（非已发现权限绕过）

**[P2] 冻结输入之外，最初ID/version检查没有绑定到最终GateReport。** 工具18–20行读一次manifest，30行check_bundle重新读，33行entry_for又读。如果同一工作Bundle在首次读取与Gate之间被中央其他准备步骤替换为同publisher签名的别的ID/version，report+entry_for可以彼此一致，但不再是最初检查的muse-goals/rc3。局部four ceiling会在该工具中被用于这个新ID，违反“仅本候选”限制。最小修正是在report.passed后、packet前再检查 `report.app_id == "muse-goals" && report.version == "0.4.0-rc3"`；失败退出。稳定被冻结输入下未复现该情况，不能称实际越权。

**[P2] 48行的“packed bundle differs from admitted bytes”只比digest，漏比较打包后的manifest。** 原 `app-contract/src/bundle.rs::digest_dir`跳过manifest.json。entry_for之后、pack_dir之前如果manifest被替换而其他内容不变，unpack后的digest仍相同，工具可以保存一个catalog entry与pack manifest不一致的镜像并打印ADMITTED。正常Store.install_staged会在same_manifest检查拒绝它，故没有安装权限绕过，但本地产物成功收据不充分。最小修正：unpack后解析artifact/manifest.json，把serde_json::to_value(parsed_manifest)与serde_json::to_value(catalog.entries[0].manifest)逐字段比较，再确认digest；失败保留output并退出。不要删除旧失败、重签变造的包或跳过Store检查。

这两项仅需改中央该发布工具，不要求停当前Host编译；本聊天遵守只写报告，不实改。初读manifest是std::fs::read_to_string而不是Gate内部bounded reader，但这是中央给定可信冻结输入，并非新增网络入口；不扩大成与请求无关的文件安全重构。

## 4. 本地配套运行条件与声明限制

- 工具仅生成legacy Ed25519 catalog.json，没有GitHub-v2证明，`packet`只生成审阅材料，不运行scan、不代表审阅通过。固定local publisher/anchor也不是官方anchor。结果只能称**指定配套Host的本地结构准入**，不能称官方公开Hub接受、公开发布、完整两阶段准入或Muse动作成功。
- 已读中央launcher源码：明确清理继承设置、指定任务本地anchor、`OCTOSENSE_HUB_CATALOG=legacy`、developer mode=0与隔离apps root，因此不是遗漏了channel入口。若该root已有catalog-v2.json，原CatalogChannel仍拒绝downgrade；不要删v2 floor绕过。工具anchor参数必须与launcher所固定的公开anchor对应，否则运行时自然验签拒绝；本报告未读取anchor文件核实对应关系。
- `Catalog::new(1,...)`与previous=None只适用于这次fresh mirror/fresh发布历史，不能用它覆盖已有同anchor序列/withdrawal历史或重复发布既有版本。Host原cache/file-lock/floor应保留；新输出目录不能替代已有root的序列检查。SOURCE_COMMIT目前只校验40位hex格式，是来源标签，没有验证仓库归属，不得宣称GitHub provenance证明。
- 本地结构准入不强制Bundle申请Agent及这四项tool；agent:null/缺少octos.session.* capability可能结构Gate通过但无法提供Muse Agent UI。中央须核本次实际rc3manifest的agent.tools、profile、instructions和contained四服务capabilities；有offer不等于runtime grant、实际模型选择、result或History通过。
- 保留本人nativeconsent；muse-native-prototype的同意不迁移到muse-goals。AppSaysPerson/lane=person不等于本人操作。此冷开调用只准入，无同意设置。
- update/remove不在Host/local四工具集合内；即使staged tools.json先前提案shareable:true，也不代表Muse本次有权。错误和撤销必须经原Broker/Relay实际返回记录，不手写call冒充owner。

最终建议：cold patch可保持进入中央Host编译；local工具在最终生成镜像前补上述两个产物绑定检查，维持既有原Gate/签名/identity/consent。当前无法由本次静态复核确认新Host编译、冷开窗口、模型首轮Result/History或本机Calendar四工具动作。

## 本次只读核对的字节

- `official_muse/integrated_release/muse-cold-launch.patch` SHA256 `7993b2152285fb7dd614b29899281e83ae6ae42f34ad613f9cb68488c041a413`
- `official_muse/integrated_release/muse_local_catalog.rs` SHA256 `406e981092021768bff7c36fda56eab9af44443f13d0cd878fce83b99d357fb2`
- `build/runtime-closure-full-shell-r1/sdk/crates/shell/src/apps.rs` SHA256 `a523dcaebee3ab84c7308a8f08327701926d75f7e07705e4535984574158090b`
