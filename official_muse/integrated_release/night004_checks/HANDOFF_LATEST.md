# Handoff

## Task

GPT05：将已有冷启动、动态身份、原生窗口和Mail计数工具移入独立Git源码目录。基线codex/muse-pivot-20261010，HEAD 961d05ec9755abb3436aa2c6c38914427ae20f5d。

## Result

PASS，仅源码交接与准备检查；正式20次和业务验收未完成。

## Changed

本目录七个源码工具、gitignore、迁移SHA记录、准备结果及说明。只修仓库ROOT和同目录probe路径；C源字节保留，binary不入Git。

## Tests

2026-10-12：两个clang轻量C编译exit0，py_compile及四个help exit0，路径导入检查PASS；中央明确rc7包/双marker隔离state执行prepare-only一次exit0。命令与退出见local-evidence，摘要PREPARATION.json。原Mail自造样本16项PASS沿用证据，迁移后未重跑。

## Commit

本单元未提交/未推送，由中央统一提交。

## Remaining

中央最终source freeze、真实Mail/Calendar计数基线、正式冷启动、native图片复核及T18。

## Important Boundaries

迁移无Host/GUI/动态PID/Mail资料/Secret操作，无Cargo。已有单次rc7实测不是20PASS；零计数/签名/窗口不能替代业务成功。
