#!/usr/bin/env python3
"""Timestamp-preserving redaction, edit, offline narration and evidence export."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import statistics
import subprocess
from PIL import Image
import build_rc48_demo as base

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs/rc49-final-r1'
SAFE = ROOT / '.local-state/rc49-safe-r1'
PLAN = ROOT / 'rc49-edit-plan.json'
FF = ROOT / '.local-state/ffmpeg'
FONT = '/System/Library/Fonts/PingFang.ttc'
SOURCES = ['live-rc49-r1', 'live-rc48-restart-r1']


def ff(*args, cwd=OUT):
    subprocess.run([str(FF), '-hide_banner', '-loglevel', 'error', '-nostdin', '-n',
                    *map(str, args)], cwd=cwd, check=True)


def write_json(p, data):
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')


def policy(name, i, size, ocr):
    w, h = size
    rectangles = []
    if name == 'live-rc49-r1':
        if 99 <= i <= 122:
            rectangles.append([2150, 240, 630, 1180])
        elif 123 <= i <= 293:
            boxes = ocr[i]['email_like_boxes_normalized_top_left']
            if not boxes:
                raise ValueError('Expected private mail rows missing from OCR inventory')
            bottom = round(max((y+dy)*h for x,y,dx,dy in boxes)) + 16
            left = 2150 if w == 2800 else 2220
            rectangles.append([left, 240, w-left-20, bottom-240])
        if 340 <= i <= 466 or i == 469:
            rectangles.append([520, 1450, 2320, 150])
    return rectangles


def prepare():
    SAFE.mkdir(parents=True, exist_ok=True)
    script_sha = base.sha(Path(__file__))
    marker = SAFE / 'builder.sha256'
    if marker.exists() and marker.read_text().strip() != script_sha:
        raise ValueError('Builder changed; use a fresh safe-frame directory')
    marker.write_text(script_sha+'\n')
    ocr = json.loads((ROOT / '.local-state/rc49-ocr-results.json').read_text())
    jobs, provenance = [], []
    for name in SOURCES:
        src, data, manifest_sha = base.source_data(name)
        target = SAFE / name
        target.mkdir(exist_ok=True)
        rows = []
        for i, frame in enumerate(data['frames']):
            original = src / frame['file']
            with Image.open(original) as im:
                size = im.size
            crop = { (2800,1618):[24,80,2752,1340],
                     (2880,1800):[24,72,2832,1528] }[size]
            masks = policy(name, i, size, ocr)
            jobs.append((original, target / frame['file'], crop, masks))
            rows.append({**frame, 'size':size, 'crop_xywh':crop, 'masks_xywh':masks})
        offsets = [f['monotonic_offset_seconds'] for f in rows]
        gaps = [b-a for a,b in zip(offsets,offsets[1:])]
        provenance.append({'source':name,'manifest_sha256':manifest_sha,
            'elapsed_seconds':data['elapsed_seconds'],'frames':rows,
            'missed_attempts':data['missed_attempts'],
            'median_interval_seconds':statistics.median(gaps),
            'max_interval_seconds':max(gaps),
            'average_capture_fps':len(rows)/data['elapsed_seconds']})

    def normalize(job):
        src, dst, crop, masks = job
        if dst.exists():
            return
        filters = [f'drawbox=x={x}:y={y}:w={w}:h={h}:color=0x17232e:t=fill'
                   for x,y,w,h in masks]
        x,y,w,h = crop
        filters += [f'crop={w}:{h}:{x}:{y}',
            'scale=1840:896:force_original_aspect_ratio=decrease',
            'pad=1920:1080:(ow-iw)/2:88:color=0x0c1420', 'setsar=1']
        ff('-threads',1,'-i',src,'-vf',','.join(filters),'-frames:v',1,
           '-threads',1,'-compression_level',3,dst)
    with ThreadPoolExecutor(max_workers=2) as pool:
        for i, _ in enumerate(pool.map(normalize,jobs)):
            if i % 100 == 0:
                print('Normalized/redacted',i+1,'/',len(jobs),flush=True)
    for source in provenance:
        for row in source['frames']:
            row['redacted_frame_sha256'] = base.sha(SAFE/source['source']/row['file'])
    write_json(OUT/'capture-provenance.json', provenance)


def text_filter(path, x, y, size, color='white'):
    return f'drawtext=fontfile={FONT}:textfile={path}:x={x}:y={y}:fontsize={size}:fontcolor={color}'


def clip(c, number, continuous=False):
    folder = OUT / ('continuous' if continuous else 'clips')
    folder.mkdir(exist_ok=True)
    output = folder / f'{number:02}-{c["id"]}.mp4'
    if output.exists():
        return output
    duration = c['source_end']-c['source_start']
    filters = []
    if c['source'] is None:
        args = ['-loop',1,'-framerate',30,'-i',ROOT/'MUSE_COVER.png']
        filters = ['scale=1920:1080:force_original_aspect_ratio=decrease',
                   'pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x101820']
    else:
        _, data, _ = base.source_data(c['source'])
        fs = data['frames']
        pieces = []
        for i, f in enumerate(fs):
            begin = max(f['monotonic_offset_seconds'], c['source_start'])
            end = min(fs[i+1]['monotonic_offset_seconds'] if i+1<len(fs)
                      else data['elapsed_seconds'],c['source_end'])
            if end>begin:
                pieces += [f"file '{SAFE/c['source']/f['file']}'",f'duration {end-begin:.9f}']
        if not pieces:
            raise ValueError('No captured frames in segment')
        pieces.append(pieces[-2])
        listing = folder/f'{number:02}.ffconcat'
        listing.write_text('ffconcat version 1.0\n'+'\n'.join(pieces)+'\n')
        args = ['-f','concat','-safe',0,'-i',listing]
        title = folder/f'{number:02}-title.txt';title.write_text(c['title'])
        filters.append(text_filter(title,40,24,30,'0x96ded5'))
        version = 'rc49' if c['source']=='live-rc49-r1' else 'rc48 支持证据'
        note = folder/f'{number:02}-note.txt'
        note.write_text(version+' · 低帧率真窗口采集 · '+('连续时间轴 / 隐私遮挡' if continuous else '已剪辑 / 隐私遮挡'))
        filters.append(text_filter(note,1050,34,20,'0xc1ccd6'))
        if c['id'] in ('plan','approve-result') or continuous:
            privacy = folder/f'{number:02}-privacy.txt'
            privacy.write_text('遮挡：历史邮件卡 / 私人标识。邮件与日历外链属于跨版本历史。')
            filters.append(text_filter(privacy,40,61,18,'0xc1ccd6'))
    # Display-time resampling only. The image content is never interpolated.
    filters += ['fps=30','format=yuv420p']
    ff(*args,'-vf',','.join(filters),'-t',duration,'-an','-c:v','libx264',
       '-preset','veryfast','-crf',18,'-threads',2,'-movflags','+faststart',output)
    print('Encoded',output.name,flush=True)
    return output


def narrate(plan):
    base.OUT, base.PLAN = OUT, PLAN
    base.ff = ff
    base.narrate(plan)
    (OUT/'Muse-rc48.zh-CN.srt').rename(OUT/'Muse-rc49.zh-CN.srt')


def render(plan):
    if (OUT/'audio-plan.sha256').read_text().strip()!=base.sha(PLAN):
        raise ValueError('Narration and edit plan differ')
    clips = [clip(c,i) for i,c in enumerate(plan['clips'])]
    listing = OUT/'edit.ffconcat'
    listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{p}'\n" for p in clips))
    video = OUT/'Muse-rc49-demo.zh-CN.mp4'
    style = 'FontName=PingFang SC,FontSize=12,Outline=1,Shadow=0,MarginV=5'
    ff('-f','concat','-safe',0,'-i',listing,'-i',OUT/'narration.m4a',
       '-map','0:v:0','-map','1:a:0','-vf',f"subtitles=Muse-rc49.zh-CN.srt:force_style='{style}'",
       '-t',plan['duration'],'-c:v','libx264','-preset','veryfast','-crf',19,
       '-threads',2,'-c:a','copy','-movflags','+faststart',video)
    ff('-i',video,'-f','null','-')
    for name,t in [('keyshot-01-rc49-verified-result',76),('keyshot-02-rc49-memory-source',106)]:
        ff('-ss',t,'-i',video,'-frames:v',1,OUT/f'{name}.png')
    write_json(OUT/'render-status.json',{'status':'ENCODED_DECODE_PASS_QA_PENDING',
        'video_sha256':base.sha(video),'video_bytes':video.stat().st_size,
        'duration_seconds':plan['duration'],'plan_sha256':base.sha(PLAN)})


def continuous():
    for i,name in enumerate(SOURCES):
        _,d,_ = base.source_data(name)
        c = {'id':name+'-continuous-redacted','source':name,
             'source_start':d['frames'][0]['monotonic_offset_seconds'],
             'source_end':d['elapsed_seconds'],
             'title':('rc49 核心操作' if i==0 else 'rc48 重启与召回支持证据')+'｜连续采集'}
        p=clip(c,i,True)
        ff('-i',p,'-f','null','-')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=['prepare','narrate','render','continuous'])
    a=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    plan=json.loads(PLAN.read_text())
    assert abs(sum(c['source_end']-c['source_start'] for c in plan['clips'])-plan['duration'])<0.001
    if a.phase=='prepare': prepare()
    elif a.phase=='narrate': narrate(plan)
    elif a.phase=='render': render(plan)
    else: continuous()
