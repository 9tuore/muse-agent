#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create a product presentation from published, redacted rc51 evidence.

Original evidence and verdicts remain separate. This edit contains selected
actual task footage and observed results, without an acceptance-status claim.
No application, account, model API or system calendar is accessed.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import wave

ROOT = Path(__file__).resolve().parent
FF = ROOT.parents[2] / 'submission-ready-20261006-r1/media/.local-state/ffmpeg'
TMP = ROOT / '.local-state/product-demo-v2'
SRC = ROOT / 'Muse-rc51-demo.zh-CN.mp4'
COVER = ROOT / 'Muse-rc51-cover-v2.png'
OUT = ROOT / 'Muse-rc51-product-demo.zh-CN.mp4'
FONT = '/System/Library/Fonts/PingFang.ttc'
DURATION = 74
CLIPS = [
    (None, 5, 'Muse · 让记忆推动行动'),
    (6, 10, '真实对话，形成计划'),
    (16, 8, '结果保存，独立读回'),
    (24, 8, '同一事项，继续讨论'),
    (32, 22, '确认计划，执行并核对结果'),
    (64, 14, '跨对话检索，保留真实来源'),
    (None, 7, 'Muse · 星海队'),
]
CUES = [
    (0.35, 4.8, '缪斯，让记忆推动行动。'),
    (5.35, 14.8, '从自然语言开始，真实模型生成计划。用户看清内容，再确认执行。'),
    (15.3, 22.8, '任务完成后，结果卡呈现内容，并通过独立读回核对保存。'),
    (23.3, 30.8, '讨论可以继续，计划也能更新。同一事项保留版本和上下文。'),
    (31.35, 39.4, '执行前再次确认，让每一步行动有明确的依据。'),
    (40.0, 52.8, '这里展示真实窗口中的保存和读回过程。结果与来源同时保留，方便之后继续使用。'),
    (53.35, 66.8, '切换到另一段对话，缪斯仍能找到相关全局记忆，并给出来源。新对话延续同一用户的知识。'),
    (67.35, 73.8, '邮件、日历、全局记忆。缪斯，星海队。'),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ff(*args):
    subprocess.run([str(FF), '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
                    *map(str, args)], cwd=ROOT, check=True)


def stamp(t):
    m = round(t * 1000)
    return f'{m // 3600000:02}:{m // 60000 % 60:02}:{m // 1000 % 60:02},{m % 1000:03}'


def main():
    assert sha(SRC) == '5cecf600c6d4a18b0217a0f08f97b76648598a559b1b69cb80b0003375361f21'
    assert sha(COVER) == 'c6eefaa390670165be5557c2c890b14e057d4088c0a3c73eb8c88b3d0d6c4a6f'
    TMP.mkdir(parents=True, exist_ok=False)
    pcm = bytearray(DURATION * 48000 * 2)
    timings = []
    for i, (start, limit, words) in enumerate(CUES):
        text = TMP / f'voice-{i}.txt'
        text.write_text(words, encoding='utf-8')
        aiff, wav = TMP / f'voice-{i}.aiff', TMP / f'voice-{i}.wav'
        subprocess.run(['/usr/bin/say', '-v', 'Tingting', '-r', '205', '-f', str(text), '-o', str(aiff)], check=True)
        ff('-i', aiff, '-ar', 48000, '-ac', 1, '-c:a', 'pcm_s16le', wav)
        with wave.open(str(wav)) as w:
            assert w.getnchannels() == 1 and w.getsampwidth() == 2 and w.getframerate() == 48000
            frames = w.getnframes()
            raw = w.readframes(frames)
        end = start + frames / 48000
        assert end <= limit, f'Cue {i} exceeds real time allocation'
        a = round(start * 48000) * 2
        pcm[a:a + len(raw)] = raw
        timings.append(dict(start=start, end=end, text=words))
    voice = TMP / 'narration.wav'
    with wave.open(str(voice), 'wb') as w:
        w.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        w.writeframes(pcm)
    srt = ROOT / 'Muse-rc51-product-demo.zh-CN.srt'
    srt.write_text('\n'.join(f'{i + 1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}\n'
                             for i, c in enumerate(timings)), encoding='utf-8')
    clips = []
    cursor = 0
    provenance = []
    for i, (source_start, duration, title) in enumerate(CLIPS):
        path = TMP / f'clip-{i}.mp4'
        title_path = TMP / f'title-{i}.txt'
        title_path.write_text(title, encoding='utf-8')
        if source_start is None:
            args = ['-loop', 1, '-framerate', 30, '-i', COVER]
            vf = 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x15191d'
        else:
            args = ['-ss', source_start, '-i', SRC]
            vf = ('crop=1380:840:50:124,scale=1600:974,pad=1920:1080:160:70:color=0x15191d,'
                  f'drawtext=fontfile={FONT}:textfile={title_path}:fontcolor=white:fontsize=34:x=160:y=20')
        ff(*args, '-vf', vf + ',fps=30,format=yuv420p', '-t', duration, '-an',
           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 19, '-threads', 2, path)
        clips.append(path)
        provenance.append(dict(start=cursor, duration=duration, source_start=source_start,
                               input='Muse-rc51-cover-v2.png' if source_start is None else 'Muse-rc51-demo.zh-CN.mp4',
                               real_capture_time_preserved=source_start is not None,
                               crop_xywh=None if source_start is None else [50, 124, 1380, 840], title=title))
        cursor += duration
        print('Encoded', i, duration, flush=True)
    assert cursor == DURATION
    listing = TMP / 'clips.ffconcat'
    listing.write_text('ffconcat version 1.0\n' + ''.join(f"file '{p}'\n" for p in clips))
    style = 'FontName=PingFang SC,FontSize=12,Outline=1,Shadow=0,MarginV=8'
    ff('-f', 'concat', '-safe', 0, '-i', listing, '-i', voice, '-map', '0:v:0', '-map', '1:a:0',
       '-vf', f"subtitles={srt.name}:force_style='{style}'", '-t', DURATION,
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 19, '-threads', 2,
       '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', 48000, '-c:a', 'aac', '-b:a', '128k',
       '-movflags', '+faststart', OUT)
    ff('-i', OUT, '-f', 'null', '-')
    for second in (1, 8, 19, 27, 43, 60, 70):
        ff('-ss', second, '-i', OUT, '-frames:v', 1, TMP / f'review-{second}.png')
    record = dict(kind='PRODUCT_PRESENTATION_SELECTED_REAL_EVIDENCE', duration_seconds=DURATION,
                  source_sha256=sha(SRC), cover_sha256=sha(COVER), narration='offline Tingting',
                  clips=provenance, cues=timings, files={OUT.name: dict(bytes=OUT.stat().st_size, sha256=sha(OUT)),
                                                     srt.name: dict(bytes=srt.stat().st_size, sha256=sha(srt))},
                  full_decode='PASS', visual_review='PENDING', original_test_evidence_preserved=True,
                  acceptance_verdict='See original test report; this video makes no all-gates-pass claim',
                  external_actions_performed=False)
    (ROOT / 'product-demo-provenance.json').write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
