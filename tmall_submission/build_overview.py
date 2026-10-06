#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Narrated product walkthrough; all illustrative segments are labelled.

Uses only the redacted public rc51 clip, the selected cover, and text panels.
No synthetic panel is presented as an application or system screenshot.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import wave

HERE = Path(__file__).resolve().parent
PANELS = [
    (15, 'Muse · 个人智能 Agent', ['会记住你，并帮你把事情办下去。', 'AI 负责理解，本地端负责行动。'],
     '缪斯，是一个会记住你，并帮你把事情办下去的个人智能助手。人工智能负责理解，本地端负责行动。'),
    (22, '一封来信，成为一个可继续的事项', ['来信：下周三下午，项目碰面可以吗？', '相关记忆：项目归属、约定偏好、真实来源', '会话聚焦当前讨论，全局记忆按授权相关检索'],
     '设想一封约时间的邮件。缪斯将来信与授权范围内的项目记忆联系起来，保留来源。换一个聊天，相关记忆仍可检索，不会把整库或别人的项目塞进上下文。'),
    (22, '查询目标日历，先提出可确认安排', ['查询真实目标日历 → 核对冲突', '最多两条经过查询的替代时间', '日期、时区、地点明确后，由用户确认'],
     '接着查询目标日历，核对冲突，提供可确认的安排。需要替代时间时，最多两条，并经过真实查询。用户先核对日期、时区和地点，再决定是否执行。'),
    (18, '确认后执行，再独立读取核对', ['宿主执行 → 系统 Calendar → 独立读回', '模型说“完成”不是系统执行证据', '后续改期关联原事件，不另建第二条'],
     '确认后由本地宿主执行，再独立读取系统结果。后续改期关联原事项并修改原事件。模型说完成了，不能代替真正的系统结果。'),
    (17, '回复由你决定', ['按你的意思起草，或保留手写稿', '草稿可编辑，发送另行确认', '受理与收件到达分别核对'],
     '你可以让人工智能起草，也可以自己写。手写稿不被覆盖。发送仍需单独确认，服务受理与收件到达分别核对。'),
    (14, '不明确，就具体问清楚', ['来信：下周找时间聊一下。', '期待：询问具体日期或时间段', '缺少信息时停止外部写入'],
     '如果邮件只说下周找时间，缪斯应先询问具体日期或时间段，缺少信息时停止外部写入。这段是流程讲解，实际失败状态截图仍待拍摄。'),
]
END = (12, '让记忆推动行动', ['邮件 · 记忆 · 日历 · 执行', '同一套 Muse 核心，基于 OctoSense Agent Runtime', '完整同版本外部闭环实录仍待补齐'],
       '接下来看到的是真实候选的操作节选。内部结果与跨聊天记忆已有实证，完整同版本的邮件日历闭环实录仍待补齐。缪斯，让记忆推动行动。')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stamp(value):
    ms = round(value * 1000)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', type=Path, required=True)
    args = parser.parse_args()
    temp = HERE / '.local-state/overview'
    temp.mkdir(parents=True, exist_ok=False)
    font = '/System/Library/Fonts/PingFang.ttc'
    clips, cues, sources = [], [], []
    cursor = 0

    def ff(*flags):
        result = subprocess.run([str(args.ffmpeg), '-hide_banner', '-loglevel', 'error', '-y',
                                 *map(str, flags)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr[-2000:])

    def panel(index, item):
        nonlocal cursor
        duration, title, lines, narration = item
        txt = temp / f'text-{index}.txt'
        txt.write_text(title + '\n\n' + '\n\n'.join(lines), encoding='utf8')
        label = temp / 'label.txt'
        label.write_text('产品流程讲解 · 示意文字，非系统操作实录', encoding='utf8')
        audio = temp / f'voice-{index}.aiff'
        subprocess.run(['/usr/bin/say', '-v', 'Tingting', '-r', '205', '-f', str(temp / f'narration-{index}.txt'),
                        '-o', str(audio)], check=True)
        wav = temp / f'voice-{index}.wav'
        ff('-i', audio, '-ac', 1, '-ar', 48000, wav)
        with wave.open(str(wav), 'rb') as stream:
            seconds = stream.getnframes() / stream.getframerate()
        assert seconds < duration - 0.2, (index, seconds, duration)
        path = temp / f'clip-{index}.mp4'
        vf = (f'drawtext=fontfile={font}:textfile={txt}:fontsize=42:fontcolor=white:line_spacing=16:x=120:y=180,'
              f'drawtext=fontfile={font}:textfile={label}:fontsize=26:fontcolor=0x9fc7c5:x=120:y=80')
        inputs = ['-f', 'lavfi', '-i', f'color=c=0x181d22:s=1920x1080:r=30:d={duration}']
        if index == 0:
            inputs = ['-loop', 1, '-framerate', 30, '-i', str(HERE / 'assets/cover.png')]
            vf = (f'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x181d22,'
                  f'drawbox=x=0:y=0:w=iw:h=66:color=0x181d22:t=fill,drawtext=fontfile={font}:textfile={label}:fontsize=26:fontcolor=white:x=120:y=18')
        ff(*inputs,
           '-i', wav, '-vf', vf, '-af', f'apad=whole_dur={duration}', '-t', duration,
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 23, '-threads', 2,
           '-c:a', 'aac', '-ar', 48000, '-b:a', '128k', '-pix_fmt', 'yuv420p', path)
        clips.append(path)
        cues.append(dict(start=cursor + 0.1, end=cursor + seconds + 0.1, text=narration))
        sources.append(dict(start=cursor, seconds=duration, kind='LABELLED_FLOW_EXPLANATION', title=title))
        cursor += duration

    for i, item in enumerate(PANELS):
        (temp / f'narration-{i}.txt').write_text(item[3], encoding='utf8')
        panel(i, item)
        print('Encoded explanation', i, flush=True)
    # 42 seconds of the existing public product video, unchanged speed/audio.
    real = HERE / 'demo/Muse-rc51-real-excerpt.zh-CN.mp4'
    label = temp / 'real-label.txt'
    label.write_text('rc51 真实节选 · 内部任务、结果读回与记忆；非邮件日历闭环', encoding='utf8')
    observed = temp / 'real.mp4'
    ff('-ss', 15, '-i', real, '-t', 42,
       '-vf', f'drawbox=x=0:y=0:w=iw:h=64:color=0x181d22:t=fill,drawtext=fontfile={font}:textfile={label}:fontsize=28:fontcolor=white:x=100:y=18',
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 23, '-threads', 2,
       '-c:a', 'aac', '-ar', 48000, '-b:a', '128k', '-pix_fmt', 'yuv420p', observed)
    clips.append(observed)
    sources.append(dict(start=cursor, seconds=42, kind='REAL_RC51_PUBLIC_EXCERPT', source_start=15,
                        source_sha256=sha(real), speed=1.0))
    cursor += 42
    # The closing wording is about the clip already shown.
    closing = (12, END[1], END[2], '刚才是真实候选的操作节选。内部结果与跨聊天记忆已有实证，完整同版本的邮件日历闭环实录仍待补齐。缪斯，让记忆推动行动。')
    (temp / 'narration-end.txt').write_text(closing[3], encoding='utf8')
    panel('end', closing)
    listing = temp / 'clips.ffconcat'
    listing.write_text('ffconcat version 1.0\n' + ''.join(f"file '{p}'\n" for p in clips), encoding='utf8')
    out = HERE / 'demo/Muse-Tmall-Overview.zh-CN.mp4'
    srt = HERE / 'demo/Muse-Tmall-Overview.zh-CN.srt'
    srt.write_text('\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}\n'
                             for i, c in enumerate(cues)), encoding='utf8')
    ff('-f', 'concat', '-safe', 0, '-i', listing, '-i', srt,
       '-map', '0:v:0', '-map', '0:a:0', '-map', '1:0', '-c:v', 'copy', '-c:a', 'copy',
       '-c:s', 'mov_text', '-metadata:s:s:0', 'language=zho', '-movflags', '+faststart', out)
    ff('-i', out, '-f', 'null', '-')
    record = dict(seconds=cursor, width=1920, height=1080, narration='offline Tingting',
                  kind='PRODUCT_EXPLANATION_WITH_REAL_INTERNAL_EXCERPT', full_external_chain=False,
                  panels=sources, full_decode='PASS', visual_review='PENDING',
                  files={out.name:dict(bytes=out.stat().st_size, sha256=sha(out)), srt.name:dict(sha256=sha(srt))})
    (HERE / 'demo/OVERVIEW_PROVENANCE.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    for second in (4, 24, 48, 66, 86, 101, 117, 151, 157):
        ff('-ss', second, '-i', out, '-frames:v', 1, temp / f'review-{second}.png')
    print(json.dumps({'seconds':cursor, 'bytes':out.stat().st_size, 'sha256':sha(out)}), flush=True)


if __name__ == '__main__':
    main()
