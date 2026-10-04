# Muse 仓库瘦身报告 · 2026-10-04

## 范围与结果

原公开main基线be552c1e。整套vendor的12000个条目不再作为重复基础源码跟踪；五个官方commit锁定，76个可读差异文件与4个内部链接完整保留，21个原快照排除项按锁恢复。完整原vendor已移到本机隔离备份，Git历史不重写，旧Tag不动。

38张历史公开截图（103481088字节，约98.7MiB）归档到固定历史提交和逐文件哈希验证的本机原件；索引EVIDENCE_ARCHIVE.json。当前新截图、README展示图、AppHub listing截图、全部测试/日志/JSON失败记录保留。不移除唯一失败证据。

README收敛为四部分；移除旧导出器和10个未使用import。开发主入口累计删除9个无引用函数、隐藏/重复/不可达UI；该清理以可应用补丁交付，公开稳定0.3.22签名payload字节不变。

## 实际验证

- 官方Git树与保留blob SHA1逐个核对，58个差异原文从官方blob读取并验哈希；没有读取任何竞争作品。
- 隔离恢复五个SDK，内容、执行模式、4个相对链接全树哈希与原12000条目完全一致。
- Cargo锁定离线metadata：OctoSense18个工作区包、AppHub8个包通过，锁文件未变。
- 还原后的Hub实际构建通过（45.81秒）；使用已有开发公钥check原0.3.22签名bundle，PASS。
- 还原后的Calendar宿主实际锁定离线编译检查通过（2分08秒），没有调用系统Calendar或写入事件。
- 主入口清理121项合成card-host断言通过，旧selection_suite前后同错保留；三页可见截图和初次字体未完成绘制记录保留。
- 源码导出按新SOURCE_MANIFEST允许清单进行逐文件读回，最终结果另见SOURCE_EXPORT_VERIFICATION.json。

官方大codeload下载超时记录保留；验证使用官方Git对象归档及经Git树逐文件核对的基础档案，并应用完整差异。完整Shell本轮没有重新编译或执行业务整链；不把源码等价、编译或Gate当作真实动作完成。本地Calendar/准入扩展仍未被声明为官方上游接纳。

## 下载与开发

```sh
python3 scripts/bootstrap_sdk.py
python3 scripts/bootstrap_sdk.py --verify
```

首次需下载锁定官方SDK及Cargo依赖，下载速度取决于网络；可使用精确归档缓存--archive-dir。已有依赖发生变化时立即拒绝覆盖。源码包/HEAD精简，开发时恢复完整依赖；全部历史clone仍包含旧大对象，未通过强推或历史重写缩小。

## 产品状态与保护

原0.3.22安装和签名bundle未更新；整体PARTIAL，日历hard_windows为空、同候选真实全链、第二模型及正式材料仍未完成。旧独立安装版与生产数据不改；没有新模型调用、邮件发送、系统日历写入、成功Tag或正式AppHub提交。
