# rc51 实包只读预检

状态：PREFLIGHT_PASS，等待 Root 的最终 FULL_SHA 和 A2 新 rc51 视频完整路径。没有压缩，没有启动应用，没有模型、邮件或 Calendar 调用。

观察点为分支 codex/muse-rc-finalization、HEAD 9bf91927283d038ef4981afd6ab94c86cfbbb18c；不是最终冻结提交。

- Git 源码允许清单：2114 普通文件，191833344 字节；路径、类型和私有排除规则通过。
- Gate：gate-rc51-release-r2，候选 e2a71195，版本 0.3.26-rc51，compact ed4874d1；该观察 HEAD 的六 bundle 文件与 Gate、pack 逐字节一致。
- 实际 Host SHA 1d7、Hub SHA 24db 与固定输入匹配。Host 目录逻辑大小 117790489 字节；model 文件允许清单逐项大小和 SHA 匹配，366262112 字节。
- 可用磁盘 4092506112 字节，既有 2GiB gate 通过；粗估峰值 2435438578 字节，仅用于预检，不承诺并发期间容量或最终压缩比。
- 最终证据目录 official_muse/rc/packaging/rc51-solid-final-r1 尚未创建，留给 packer 单次创建。目标 Desktop，旧 rc49 ZIP 497158213 字节仍在。

RC51_COMMAND_TEMPLATE.json 提供完整 argv；两占位字段必须由 Root 明确给出后才替换执行，不使用 HEAD 或旧视频猜代。已有 packager 选项 --solid-source 和严格小于 500000000 字节门槛继续执行；只运行一次完整打包。

最终包自检会独立解压 ZIP、还原源码 tar、核对集合/SHA/mode/symlink，再执行 codesign、launcher --check、Hub verify/check/scan。这里只准备命令，未把这些写成已经通过。两台接收 Mac 尚未实测；新包未验证前保留旧 rc49。
