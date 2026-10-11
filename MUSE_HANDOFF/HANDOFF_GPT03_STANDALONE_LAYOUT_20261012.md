# Handoff

## Task
GPT-03；独立worktree基线27cf12e8。验证单.app中standalone Host定位，交付适配中央rc6的own patch。

## Result
PARTIAL。4种signed Foundation fixture路径成功；Resources/host-runtime的mainBundle/resourcePath就是host-runtime，identifier nil，与bare目录行为相同。outer签名前后embedded strict PASS，outer deep/strict PASS。

## Changed
仅own evidence/gpt03-standalone-bundle-layout-20261011与本交接。patch改packager staging/签名路径、Shell exec路径、helper3检查路径；未改中央。

## Tests
实际clang/Foundation/codesign fixture；owned rc6副本patch检查/apply、字节核对、AST、sh -n通过。首次fixture因mkdir未建Resources失败，补parents=True后取得结果，失败记录保留。

## Commit
本地提交见Git，未push。

## Remaining
Root应用patch后真实打包/启动及动态SecCode/Keychain/本人Mail验证。旧layout测试需调整。

## Important Boundaries
208资源namespace与Kernel/receipt必须同置host-runtime；不写Info或内层app。Host在.app外owned临时路径重签，再复制入包。STATE/HOME/args保持。无实际Host/GUI/Secret/Cargo调用，不把fixture当官方整链。
