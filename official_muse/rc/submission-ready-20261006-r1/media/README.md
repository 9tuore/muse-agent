# Muse 演示媒体制作入口

当前：工具与离线旁白草案已准备，**没有生成真实操作成片**。Root提供的`MUSE_COVER.png`已收到并查看，作为宣传封面使用，不作真实UI证据。所有写入限本目录；不操作8493或其他桌面窗口，不调用付费TTS，不上传视频。

## 已验证与预估

macOS Tingting普通话、本机say输出AIFF成功；18句rc46草案自动配音及按实际句长的SRT已生成，AAC实际2分49.30秒、约2.8MB。音频全量解码/音量测量通过，尚未人工听审。中文PingFang字幕像素已查看；6.92秒纯色“编码校验画面·非产品演示”H.264/AAC样片全解码通过，绝不充当产品操作录像。

PATH/内置bin无ffmpeg，于本目录.local-state提取PyPI imageio-ffmpeg0.6.0 Intel wheel内的ffmpeg7.1，下载24.9MB并核验SHA；实际二进制76.0MB。本地单独使用，不全局安装，也不随Git或交付包分发该二进制。工具来源/哈希/错误记录见TOOLCHAIN_AND_PREP_REPORT.json。AVFoundation与已有项目真实帧编码器可作本机fallback。

预计1600×900、输出30fps、H.264 CRF20且maxrate4M、AAC128k，2–3分钟约40–95MB；155秒/2.5Mbps约51MB。是预计而非成品大小。原连续证据另计，不录用户整桌面。

官方初赛材料要求2–3分钟、两张关键截图、至少一次操作及可核对结果、失败或空状态：[官方赛程](https://github.com/gosimfoundation/hackathon-agenticapp26/blob/main/docs/competition-schedule.md)。Root合规聊天决定本轮材料适用阶段；当前新版本演示不标作10/4初赛冻结版本。

最新旁白按rc46可拍范围调整：应用中心进入、邮件来源与提醒、明确标跨版本的历史、一次性任务计划/批准/模型/存储/读回、Memory及来源DSL、日历只读或空状态、恢复与限制。旧邮件日历链不重复发送，不串成最新候选完整新执行。新音频位于`outputs/narration-draft-rc46-r1/`；旧草案音频保留。所有台词仍为待实录核对的草案。

## Root交付素材

请放到本目录忽略的inputs/，或提供可复制的明确文件路径后再处理。素材接收manifest至少包含：最终候选/commit/payload/Host身份；捕获起止UTC与单调时钟；原始录像或持续帧序列逐文件SHA；宽高、实际采样率、最大帧间隙；操作步骤时间点与结果读回；账号遮挡矩形/时段及可公开范围。

优先真实连续录像。若使用MakepadRemote持续窗口帧采集，按真实时间戳编码并记录实际采样率/中断；输出30fps只代表容器帧率，不伪称采集30fps，不插帧制造动作。明显间断单独分片并标注。不得用几个关键截图轮播替代实际操作。Root负责实际窗口和外部动作；本工具无录屏/控制功能。

至少一段保留输入→确认→动作→可核对结果的连续来源，另保留真实失败或空状态；仅展示空列表可以，不为拍摄故意触发付费失败。版本不同应逐段注明，不拼成同最终从头全链。封面为Root提供的imagegen海报，标作封面，不充当结果截图；两张关键截图必须从真实片段抽取。

## 本机命令

在media目录执行下列命令；从其他目录运行时需使用脚本绝对路径，参数仍全部相对此media目录。输出必须新目录，避免覆盖旧证据。

```sh
python3 media_pipeline.py narrate --script narration.draft.json --out outputs/narration-draft-r2
python3 media_pipeline.py encode --manifest edit-manifest.final.json --out outputs/final-r1
```

第二条需收到真实素材并按edit-manifest.template.json填好冻结来源与精确剪辑决策；脚本拒绝未review的输入。draft旁白状态不能过最终编码门槛。最终旁白必须与真实素材逐句对应，标FINAL_FOOTAGE_MATCHED后重新生成；不能只改草案状态冒充审片。

剪辑不自动拉长画面、不用静帧补够时长。最终已剪素材时长与旁白需匹配，缩减文字或调整自然停顿，保留操作证据。encode检查真实视频时长、source/edited/audio/subtitle SHA，烧录字幕、按output坐标/时段加不透明局部遮挡，H.264/AAC编码、全量解码、抽四帧供进一步人工/代理审片。尚未在真实素材上运行最终encode路径。

## 审片与交付

看整段并抽检每次切镜/遮挡切换：账号名、邮箱地址、私人正文、Key尾码、通知、桌面边缘都不能漏出；只遮账号区域，不遮动作结果。遮挡后片段标“账号信息已局部遮挡”。公开证据用同时间轴遮挡副本；未遮原始素材保持私有，公开manifest绑定原文件哈希与遮挡版哈希，不外发未遮原件。

检查字幕无遮挡按钮与读回结果、中文不缺字、音画指向一致，听审Tingting人名/英文读音与音量/停顿，确认120–180秒、无断尾/黑帧/静帧伪操作。剪辑/加速注明，保留同版本原始连续证据及来源manifest；音轨说明“本机Tingting自动配音”，不用模型自报名称或窗口出现作为动作成功。

交付目标：本地讲解版MP4、SRT、封面PNG、两张真实关键截图、连续证据遮挡版、来源/剪辑/遮挡manifest与SHA。视频、音频、原始帧和依赖全部ignored，不push GitHub。只本地commit --only本目录脚本/字幕/草案/说明。不得宣称20/20、获奖或正式Hub上架。
