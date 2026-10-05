#!/usr/bin/env python3
"""Build an rc48 preview from timestamped captures. Final content QA is pending."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import wave

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs/rc48-preview-r2'
FF = ROOT / '.local-state/ffmpeg'
FONT = '/System/Library/Fonts/PingFang.ttc'
PLAN = ROOT / 'rc48-edit-plan.json'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def ff(*args, cwd=OUT):
    subprocess.run([str(FF), '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
                    *map(str, args)], cwd=cwd, check=True)


def stamp(t):
    ms = round(t * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def captions(cues):
    subs = []
    for c in cues:
        # Short punctuation-bounded captions avoid isolated closing punctuation.
        parts = re.findall(r'[^。；，]+[。；，]?', c['text'])
        cursor = c['start']
        for part in parts:
            end = cursor + c['duration'] * len(part) / len(c['text'])
            subs.append(f'{len(subs)+1}\n{stamp(cursor)} --> {stamp(end)}\n{part}\n\n')
            cursor = end
    return ''.join(subs)


def narrate(plan):
    audio = OUT / 'audio'
    audio.mkdir(parents=True, exist_ok=False)
    pcm = bytearray(round(plan['duration'] * 48000) * 2)
    cues = []
    for i, c in enumerate(plan['cues']):
        txt = audio / f'{i:02}.txt'
        txt.write_text(c['text'].replace('Muse', '缪斯'), encoding='utf-8')
        subprocess.run(['/usr/bin/say', '-v', plan['voice'], '-r', str(plan['rate']),
                        '-f', str(txt), '-o', str(audio / f'{i:02}.aiff')], check=True)
        ff('-i', audio / f'{i:02}.aiff', '-ar', 48000, '-ac', 1,
           '-c:a', 'pcm_s16le', audio / f'{i:02}.wav')
        with wave.open(str(audio / f'{i:02}.wav')) as w:
            count = w.getnframes()
            data = w.readframes(count)
        end = c['start'] + count / 48000
        cues.append({**c, 'end': end, 'duration': count / 48000})
        print(i, round(end, 3), 'limit', c['latest_end'], flush=True)
        if end > c['latest_end']:
            continue  # Keep generated evidence and report all timing issues below.
        start = round(c['start'] * 48000) * 2
        pcm[start:start + len(data)] = data
    (OUT / 'narration-timing.json').write_text(json.dumps(cues, ensure_ascii=False, indent=2)+'\n')
    if any(c['end'] > c['latest_end'] for c in cues):
        raise ValueError('Narration exceeds footage slot; shorten wording, never stretch UI')
    with wave.open(str(audio / 'narration.wav'), 'wb') as w:
        w.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        w.writeframes(pcm)
    ff('-i', audio / 'narration.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
       '-ar', 48000, '-c:a', 'aac', '-b:a', '128k', OUT / 'narration.m4a')
    (OUT / 'Muse-rc48.zh-CN.srt').write_text(captions(cues), encoding='utf-8')
    (OUT / 'audio-plan.sha256').write_text(sha(PLAN)+'\n')


def source_data(name):
    folder = ROOT / 'inputs' / name
    manifest = folder / 'capture.private.json'
    d = json.loads(manifest.read_text())
    if not (folder / 'STOP').exists() or 'elapsed_seconds' not in d:
        raise ValueError('Capture must be stopped before editing')
    for f in d['frames']:
        if not re.fullmatch(r'frame-\d{5}\.png', f['file']):
            raise ValueError('Unexpected frame filename')
        if sha(folder / f['file']) != f['sha256']:
            raise ValueError('Capture frame changed')
    return folder, d, sha(manifest)


def draw_text(text_file, x, y, size=28, color='white'):
    return f'drawtext=fontfile={FONT}:textfile={text_file}:x={x}:y={y}:fontsize={size}:fontcolor={color}'


def clip(plan, c, number):
    folder = OUT / 'clips'
    folder.mkdir(exist_ok=True)
    duration = c['source_end'] - c['source_start']
    output = folder / f'{number:02}-{c["id"]}.mp4'
    if output.exists():
        return output  # Resume only within this fixed reviewed build directory.
    title = folder / f'{number:02}-title.txt'
    title.write_text(c['title'], encoding='utf-8')
    filters = []
    if c['source'] is None:
        args = ['-loop', 1, '-framerate', 30, '-i', ROOT / 'MUSE_COVER.png']
        filters += ['scale=1920:1080:force_original_aspect_ratio=decrease',
                    'pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x101820']
    else:
        source, data, _ = source_data(c['source'])
        fs = data['frames']
        pieces = []
        masks = []
        for i, f in enumerate(fs):
            t = f['monotonic_offset_seconds']
            nxt = fs[i+1]['monotonic_offset_seconds'] if i+1 < len(fs) else data['elapsed_seconds']
            begin, end = max(t, c['source_start']), min(nxt, c['source_end'])
            if end <= begin:
                continue
            pieces += [f"file '{source / f['file']}'", f'duration {end-begin:.9f}']
            # Original-pixel masks, applied before crop/scale. Entire private card.
            rect = None
            if c['source'] == 'live-rc48-r1' and 5 <= i <= 11:
                rect = (1655, 550, 485, 655)
            elif c['source'] == 'live-rc48-r1' and 31 <= i <= 45:
                rect = (40, 435, 2710, 670)
            if rect:
                masks.append((*rect, len(pieces)//2-1))
        if not pieces:
            raise ValueError('No real frames in selected segment')
        pieces.append(pieces[-2])  # End timestamp sentinel, trimmed at exact segment end.
        listing = folder / f'{number:02}.ffconcat'
        listing.write_text('ffconcat version 1.0\n'+'\n'.join(pieces)+'\n')
        args = ['-f', 'concat', '-safe', 0, '-i', listing]
        for x,y,w,h,n in masks:
            filters.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0x17232e:t=fill:enable='eq(n,{n})'")
        filters += ['crop=2752:1340:24:80', 'scale=1840:896',
                    'pad=1920:1080:40:88:color=0x0c1420', 'setsar=1']
        filters.append(draw_text(title, 40, 25, 30, '0x96ded5'))
        disclosure = folder / f'{number:02}-disclosure.txt'
        disclosure.write_text('rc48 实录节选 · 低帧率采集 · 已剪辑 / 隐私遮挡', encoding='utf-8')
        filters.append(draw_text(disclosure, 1160, 34, 20, '0xc1ccd6'))
        if c['id'] in ('open', 'approve'):
            note = folder / f'{number:02}-mask-note.txt'
            note.write_text('旧收信卡已遮挡 · 邮件 / 日历外链为跨版本历史', encoding='utf-8')
            filters.append(draw_text(note, 48, 62, 19, '0xc1ccd6'))
    filters += ['fps=30', 'format=yuv420p']
    ff(*args, '-vf', ','.join(filters), '-t', duration, '-an', '-c:v', 'libx264',
       '-preset', 'veryfast', '-crf', 18, '-threads', 2, '-movflags', '+faststart', output)
    return output


def render(plan):
    if (OUT / 'audio-plan.sha256').read_text().strip() != sha(PLAN):
        raise ValueError('Plan changed after narration')
    clips = [clip(plan, c, i) for i, c in enumerate(plan['clips'])]
    listing = OUT / 'edit.ffconcat'
    listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\n" for p in clips))
    style = 'FontName=PingFang SC,FontSize=12,Outline=1,Shadow=0,MarginV=5'
    ff('-f', 'concat', '-safe', 0, '-i', listing, '-i', OUT / 'narration.m4a',
       '-map', '0:v:0', '-map', '1:a:0', '-vf',
       f"subtitles=Muse-rc48.zh-CN.srt:force_style='{style}'", '-t', plan['duration'],
       '-c:v', 'libx264', '-preset', 'veryfast', '-crf', 19, '-threads', 2,
       '-c:a', 'copy', '-movflags', '+faststart', OUT / 'Muse-rc48-demo.zh-CN.mp4')
    ff('-i', OUT / 'Muse-rc48-demo.zh-CN.mp4', '-f', 'null', '-')
    for name, time in [('keyshot-01-verified-result', 90), ('keyshot-02-cross-chat-memory', 165)]:
        ff('-ss', time, '-i', OUT / 'Muse-rc48-demo.zh-CN.mp4', '-frames:v', 1, OUT / f'{name}.png')
    (OUT / 'render-status.json').write_text(json.dumps({
        'status':'ENCODED_DECODE_PASS_VISUAL_AUDIO_QA_PENDING',
        'plan_sha256':sha(PLAN), 'video_sha256':sha(OUT / 'Muse-rc48-demo.zh-CN.mp4'),
        'video_bytes':(OUT / 'Muse-rc48-demo.zh-CN.mp4').stat().st_size,
        'duration_seconds':plan['duration'],
        'frame_note':'30fps playback repeats captured pixels between actual sample timestamps; no motion interpolation or invented UI frames. All cuts recorded in plan.'}, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['narrate', 'render'])
    a = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    plan = json.loads(PLAN.read_text())
    if a.phase == 'narrate':
        narrate(plan)
    else:
        render(plan)
