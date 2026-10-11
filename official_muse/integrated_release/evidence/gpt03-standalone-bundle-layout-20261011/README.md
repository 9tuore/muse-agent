# Standalone Host 放入单 .app 的最小布局

已执行signed Foundation fixture：外部bare、Resources/host-runtime直接执行、外层unsigned Shell exec、外层signed Shell exec共4种路径。bare的NSBundle.mainBundle/resourcePath均为artifacts目录；其余三种均为host-runtime目录。bundleIdentifier均nil。外层签名前后embedded standalone严格验签PASS，外层deep/strict也PASS。详见probe.json；不是实际Host/GUI/动态SecCode测试。

这证明该路径保持bare目录定位行为，不会选外层Muse.app为Host mainBundle。签名Identifier仍可独立设置org.xinghai.muse.paired-host；NSBundle的nil不是签名失效。

```text
Muse.app/Contents/MacOS/Launcher
Muse.app/Contents/MacOS/muse-launcher
Muse.app/Contents/Resources/host-runtime/octosense
Muse.app/Contents/Resources/host-runtime/octos-kernel
Muse.app/Contents/Resources/host-runtime/octos-kernel.json
Muse.app/Contents/Resources/host-runtime/<208 Host resource files in original namespaces>
```

host-runtime没有Info.plist或内层.app。实际SDK makepad/platform/src/os/apple/apple_resources.rs使用NSBundle.resourcePath加载资源；kernel/src/launch.rs的packaged_candidates首先查Host同目录Kernel，receipt_candidates首先查Kernel同目录receipt。因此208资源及Kernel/receipt都放在这个目录，保留资源namespace相对路径。

standalone-layout-rc6.patch只改当前中央rc6三个文件：package_app.py先按既有方法验证/stage输入，然后迁至上述目录、删除owned临时inner app；Host在output临时目录（.app外）重签并验证后复制入runtime；外层最后签名。Shell仅换exec路径；helper仅换3个存在性检查路径。STATE/HOME/环境/args/版本/mirror/prepare/publisher均不变。paired app分支保留原Kernel字节，但Host重新签名，receipt准确记录输入/输出SHA和reused_signed_pair=false。

patch-check.json保存当前rc6三文件before/after SHA。已在owned临时副本git apply --check、实际apply/字节核对、Python AST、sh -n通过，未改中央。Root若源码已有新漂移，应先核对SHA和apply check。新编译Host通常走既有无paired分支，由Root执行原Cargo资源准备；本任务未运行Cargo。现有旧layout测试需Root调整，未宣称整包或真实启动通过。
