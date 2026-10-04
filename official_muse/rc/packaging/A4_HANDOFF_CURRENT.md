# A4 当前交接 · 2026-10-05

旧087桌面Intel开发复现ZIP与sha文件保留，SHA127a3ffe0a5343165f659978ec450cecaeeea201467687724e56ec66e521cf17，155408912 bytes；它是中间候选，不是rc6新包。此前087/92生成stage按总控释放信号已删除，各自旧ZIP的逐文件/链接/权限恢复证明保留。

本地087 ZIP与桌面ZIP实测是同一device/inode的两个硬链接，逐SHA一致、lsof均无占用。按新最小授权仅移除owned本地链接名，桌面唯一内容和sha保全；payload实际可回收量0，不能虚报释放155MB。恢复时可从桌面ZIP建立同盘硬链接。92b本地preview ZIP和0.3.25旧包仍保留。

打包接口已分source snapshot/application/runtime SDK三commit；VERSION由application manifest读取。当前b9cf26b8 rc6公开mirror六文件/Git/pack逐bytes一致，catalog verify和bundle check exit0；Host938/Card527严格签名仍PASS，SDK仍b486/3f。不声称Calendar源码修复已编译进Host。

新包尚未生成：冻结源码导出commit仍待总控声明，磁盘约250MiB，600MiB门禁不改。现有cp -cR已用clonefile；只读硬链接评估未证明比APFS clone产生足够容量。总控新启动失败为preparation wall124.194ms/offset311812，不当作新增产品函数运行，rc6仍PARTIAL；A4无GUI/模型/账号操作。严格clean build仍BLOCKED_CAPACITY。

详证OLD_087_DUPLICATE_ZIP_CHECK.json、OLD_087_DUPLICATE_ZIP_REMOVAL_RESULT.json、PORTABLE_HARDLINK_STAGE_ASSESSMENT.json、RC6_B9CF_STATIC_PACKAGE_INPUTS.json。无Git/产品/SDK修改，无新Rust编译或大复制；唯一失败/源码/SDK/运行数据均保留。

## rc6薄包准备

总控明确产品源暂不再改，finalb9 M3/更正/遗忘/Goal/独立读回/首次Shell重启报告PASS；4:00–6:00持续运行与第二模型观察另由主线负责，A4不代报完成。已准备package_thin_source.py与离线thin_source_tutorial.html：无Host/新runtime/模型，流式单ZIP不生成源码stage；旧087入口仍rc5，rc6接收机运行入口和新Calendar Host明确缺项。

Python3.9.6下AST/CLI help通过，actual b9cf rc6六文件/签名通过后因其SOURCE_MANIFEST仍rc5而正确拒绝，未写ZIP；旧087真实输入check-only已PASS，873文件清单/逐blob/SHA核验，未写ZIP。等待总控冻结最终sourceHEAD及更新清单，先将公开维护清单静态收口，不大复制/编译。方案THIN_SOURCE_DELIVERY_PLAN.md。

公开薄包维护脚本/教程/方案加入明确allowlist（37项），当前只做静态收口。新的rc6 sourceHEAD仍待总控声明。第二模型M2.7 S01/S02成功、M3同题S02服务失败是总控报告，原失败保留，不能把比较判定全PASS。
