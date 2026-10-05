#!/usr/bin/env python3
"""Offline rc51 edit. Private inputs read only; no app/driver/network access.
Uses the previously installed Pillow, ffmpeg and macOS Tingting toolchain.
Run phases: prepare, narrate, render, qa. Intermediate data stays gitignored.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
MEDIA = ROOT.parent
RC = MEDIA.parent
OLD = RC.parent / 'submission-ready-20261006-r1/media'
FF = OLD / '.local-state/ffmpeg'
TMP = ROOT / '.local-state'
FONT = '/System/Library/Fonts/PingFang.ttc'
W, H = 1920, 1080
BG, FG, MUTED, ACCENT = '#0b1522', '#eff5fa', '#a9bdce', '#86e4d5'
VIDEO = ROOT / 'Muse-rc51-demo.zh-CN.mp4'

# Each live segment preserves source monotonic offsets, including capture gaps.
CLIPS = [
 dict(id='cover',duration=6,title='Muse',note='rc51 开发候选 · 真实窗口实录',lines=['从计划，到可追溯的结果','内部存储 / 独立读回 / 跨聊天召回']),
 dict(id='v1-plan',duration=10,source='live-rc51-r1',start=382,end=392,central=True,title='01  真实对话形成首版计划',note='v1 · 原始时间节选 / 连续 10 秒',lines=['M3 真实聊天 → 首版计划','两条资料，等待用户批准','首版批准瞬间未在本片录像中']),
 dict(id='v1-result',duration=8,still='task-done.private.png',title='02  用户批准后的结果',note='v1 · 批准后截屏 / 非连续录像',lines=['内部存储 → 独立读回','两条资料已完成','手写输入仍保留']),
 dict(id='v2-update',duration=8,source='live-rc51-r2',start=0.001,end=8.001,title='03  显式更新为第二版',note='v2 · 原始时间节选 / 连续 8 秒',lines=['同一目标，版本更新','真实 Goal 模型建议','新计划重新等待批准']),
 dict(id='v2-approve',duration=22,source='live-rc51-r2',start=222,end=244,title='04  第二版批准 → 保存 → 读回',note='v2 · 连续 22 秒 / 未变速 / 保留采集间隙',lines=['真实窗口，原始时间轴','抓帧间隙约 2.18 秒','结果已核验：整理 2 条资料']),
 dict(id='before-restart',duration=5,source_still='live-rc51-r2',frame='frame-00232.png',title='05  Shell 重启前后对照',note='重启前截屏 · 非连续重启录像',lines=['证据：本轮重启核对报告','7 个受保护文件保持一致','8 提醒 / 9 Goal / 13 Run / 17 Action']),
 dict(id='after-restart',duration=5,still='restart-restored.private.png',title='05  Shell 重启前后对照',note='重启后截屏 · 此帧界面尚为空',lines=['文件与记录数来自独立核对','不能仅凭这张空界面证明恢复','后续召回见下一段']),
 dict(id='cross-chat',duration=20,still='cross-chat.private.png',central=True,title='06  另一已有聊天召回结果',note='重启后 · 真实截屏 / 非连续录像',lines=['两条说明 + 两个真实结果来源','“未核事实”指用户资料摘录','保存动作已独立读回核对']),
 dict(id='limits',duration=12,title='rc51 · 验收仍为 PARTIAL',note='开发候选 · 本机证据范围',lines=['冷启动 7/10 · 重开 5/5','GPT 缺有效 API','本轮未新增邮件或日历写入']),
]
# Short utterances have measured, independent subtitle timings; no word guesses.
CUES = [
 (0.4,5.8,'这是缪斯开发候选，真实窗口实录。'),
 (6.3,11.1,'真实模型对话，形成首版计划。'),
 (11.3,15.8,'两条资料，等待用户批准。'),
 (16.3,23.8,'批准后的截图显示完成。保存并读回，手写输入保留。'),
 (24.3,31.8,'随后，明确更新同一目标到第二版，重新等待批准。'),
 (32.3,38.3,'这一段保留二十二秒原始时间，没有变速。'),
 (38.5,45.0,'请求真实模型建议后，用户批准计划。'),
 (45.2,53.7,'结果已核验：两条资料保存成功，并完成独立读回。'),
 (54.2,63.8,'接着是重启前后截图。独立核对显示，七个文件和记录数保持不变。'),
 (64.3,72.6,'在另一已有聊天中，正确召回两条说明，以及两个真实结果来源。'),
 (72.8,83.7,'未核事实，是用户资料摘录的标签。保存动作已完成读回核对。'),
 (84.3,90.2,'整体验收仍为部分通过。冷启动七成，重开五次通过。'),
 (90.4,95.8,'未新增邮件或日历写入。GPT 缺有效接口。'),
]

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def ff(*args):
    subprocess.run([str(FF),'-hide_banner','-loglevel','error','-nostdin','-n',*map(str,args)],cwd=ROOT,check=True)

def text(draw,xy,value,size=30,fill=FG):
    draw.text(xy,value,font=ImageFont.truetype(FONT,size),fill=fill)

def logo(im,x,y,s):
    # Exact geometry of the existing official bundle/assets/icon.svg.
    d=ImageDraw.Draw(im);k=s/64
    q=lambda a:x+a*k;v=lambda a:y+a*k
    d.rounded_rectangle((q(4),v(4),q(60),v(60)),radius=15*k,fill='#183C87')
    pts=[(q(a),v(b)) for a,b in [(14,42),(14,22),(24,33),(32,21),(40,33),(50,22),(50,42)]]
    d.line(pts,fill='white',width=round(5*k),joint='curve')
    for a,b in pts:d.ellipse((a-2.5*k,b-2.5*k,a+2.5*k,b+2.5*k),fill='white')
    d.ellipse((q(43),v(13),q(49),v(19)),fill='#80D8FF')

def card(c,src=None,mask=None):
    im=Image.new('RGB',(W,H),BG);d=ImageDraw.Draw(im)
    if src is None:
        logo(im,96,116,170);text(d,(300,132),'Muse',112)
        text(d,(104,350),c['note'],34,ACCENT)
        text(d,(104,446),c['title'] if c['id']=='limits' else c['lines'][0],64)
        for i,line in enumerate(c['lines'] if c['id']=='limits' else c['lines'][1:]):text(d,(108,580+i*70),line,38,MUTED)
        text(d,(108,906),'计划 · 用户批准 · 内部存储 · 独立读回 · 来源追溯',28,ACCENT)
        text(d,(108,967),'非正式上架版本  /  不宣称官方全链通过',26,MUTED)
        return im
    original=Image.open(src).convert('RGB');assert original.size==(2800,1626)
    if mask:
        dr=ImageDraw.Draw(original)
        for x,y,w,h in mask:dr.rectangle((x,y,x+w-1,y+h-1),fill='#172638')
    # Remove entire left history list and all desktop/chrome. Keep real UI pixels.
    crop=(600,268,1648 if c.get('central') else 2148,1224)
    snap=original.crop(crop);snap.thumbnail((1370,840),Image.Resampling.LANCZOS)
    im.paste(snap,(50+(1370-snap.width)//2,124))
    text(d,(50,25),c['title'],38)
    text(d,(50,79),c['note'],24,ACCENT)
    d.line((1460,136,1460,940),fill='#294253',width=2)
    for i,line in enumerate(c['lines']):
        # Each sidebar line is reviewed as short editorial context, outside UI.
        text(d,(1490,206+i*128),line[:14],28,FG if i==0 else MUTED)
        if len(line)>14:text(d,(1490,249+i*128),line[14:],28,MUTED)
    text(d,(1490,820),'rc51 开发候选',25,ACCENT)
    text(d,(1490,870),'裁剪 / 隐私遮挡',23,MUTED)
    return im

def masks(c,index=None):
    if c.get('central'):return []
    if c['id']=='v1-result':return [[1660,365,488,278]]
    if c['id']=='after-restart':return [[1660,365,488,848]]
    # Entire historical email rows, including the upper-right address entry.
    if c['id']=='v2-update' and index is not None and index<=1:return []
    return [[1660,365,488,195 if c['id']=='before-restart' or (index is not None and index>=163) else 90]]

def source(name):
    folder=MEDIA/'.local-state'/name;p=folder/'capture.private.json';data=json.loads(p.read_text())
    # Recorder has a verified 420s auto-stop; STOP is optional in its actual code.
    assert data['elapsed_seconds']>=420 and data['kind']=='REAL_VISIBLE_MAKEPAD_WINDOW_FRAMES'
    return folder,data,sha(p)

def prepare():
    TMP.mkdir(exist_ok=True)
    safe=TMP/'safe';safe.mkdir(exist_ok=False)
    sources={n:source(n) for n in ['live-rc51-r1','live-rc51-r2']}
    rows=[];cursor=0
    for ci,c in enumerate(CLIPS):
        selected=[]
        if 'source' in c:
            folder,data,msha=sources[c['source']];fs=data['frames']
            for i,f in enumerate(fs):
                end=fs[i+1]['monotonic_offset_seconds'] if i+1<len(fs) else data['elapsed_seconds']
                a=max(c['start'],f['monotonic_offset_seconds']);b=min(c['end'],end)
                if b>a:selected.append((folder/f['file'],b-a,i,f))
        elif 'source_still' in c:
            folder,data,msha=sources[c['source_still']];i=next(i for i,f in enumerate(data['frames']) if f['file']==c['frame'])
            f=data['frames'][i];selected=[(folder/f['file'],c['duration'],i,f)]
        elif 'still' in c:selected=[(MEDIA/c['still'],c['duration'],None,None)]
        else:selected=[(None,c['duration'],None,None)]
        pieces=[];frames=[]
        for j,(p,duration,i,f) in enumerate(selected):
            h=sha(p) if p else None
            if f:assert h==f['sha256']
            rect=masks(c,i);output=safe/f'{ci:02}-{j:03}.png';card(c,p,rect).save(output,compress_level=3)
            pieces.extend([f"file '{output}'",f'duration {duration:.9f}'])
            frames.append(dict(input=str(p.relative_to(MEDIA)) if p else None,input_sha256=h,
                index=i,source_offset_seconds=f['monotonic_offset_seconds'] if f else None,
                displayed_seconds=duration,masks_xywh=rect,crop_xyxy=([600,268,1648 if c.get('central') else 2148,1224] if p else None),
                safe_file=str(output.relative_to(ROOT)),safe_sha256=sha(output)))
        pieces.append(pieces[-2]);(TMP/f'{ci:02}.ffconcat').write_text('ffconcat version 1.0\n'+'\n'.join(pieces)+'\n')
        rows.append(dict(**c,timeline_start=cursor,timeline_end=cursor+c['duration'],frames=frames));cursor+=c['duration']
        print('prepared',c['id'],len(frames),flush=True)
    assert cursor==96
    write(ROOT/'edit-provenance.json',dict(duration_seconds=96,clips=rows,sources={n:dict(manifest_sha256=s[2],elapsed_seconds=s[1]['elapsed_seconds'],frame_count=len(s[1]['frames']),missed_attempts=s[1]['missed_attempts']) for n,s in sources.items()},
        frame_rate_note='Recorded offsets are request-start timestamps. 30fps output repeats captured pixels; no interpolation. Gaps retain last observed image. Not native 30fps capture.',
        original_audio=False,stills_are_not_continuous=True))
    card(CLIPS[0]).save(ROOT/'Muse-rc51-cover.png')
    # Editable native-vector cover, using existing official icon geometry.
    icon=(RC.parent.parent/'app/bundle/assets/icon.svg').read_text()
    assert 'M14 42V22L24 33L32 21L40 33L50 22V42' in icon
    body=icon[icon.index('>')+1:icon.rindex('</svg>')]
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080"><rect width="1920" height="1080" fill="{BG}"/><g transform="translate(96 116) scale(2.65625)">{body}</g><g font-family="PingFang SC,sans-serif" fill="{FG}"><text x="300" y="244" font-size="112">Muse</text><text x="104" y="397" font-size="34" fill="{ACCENT}">rc51 开发候选 · 真实窗口实录</text><text x="104" y="510" font-size="64">从计划，到可追溯的结果</text><text x="108" y="622" font-size="38" fill="{MUTED}">内部存储 / 独立读回 / 跨聊天召回</text><text x="108" y="946" font-size="28" fill="{ACCENT}">计划 · 用户批准 · 内部存储 · 独立读回 · 来源追溯</text><text x="108" y="1004" font-size="26" fill="{MUTED}">非正式上架版本 / 不宣称官方全链通过</text></g></svg>'
    (ROOT/'Muse-rc51-cover.svg').write_text(svg)
    write(ROOT/'edit-plan.json',dict(duration=96,voice='Tingting',rate=205,clips=CLIPS,cues=[dict(start=a,latest_end=b,text=t) for a,b,t in CUES]))

def stamp(t):
    m=round(t*1000);return f'{m//3600000:02}:{m//60000%60:02}:{m//1000%60:02},{m%1000:03}'

def narrate():
    folder=TMP/'audio';folder.mkdir(exist_ok=False);pcm=bytearray(96*48000*2);timings=[]
    for i,(start,limit,words) in enumerate(CUES):
        p=folder/f'{i:02}.txt';p.write_text(words)
        subprocess.run(['/usr/bin/say','-v','Tingting','-r','205','-f',str(p),'-o',str(folder/f'{i:02}.aiff')],check=True)
        ff('-i',folder/f'{i:02}.aiff','-ar',48000,'-ac',1,'-c:a','pcm_s16le',folder/f'{i:02}.wav')
        with wave.open(str(folder/f'{i:02}.wav')) as w:count=w.getnframes();data=w.readframes(count)
        end=start+count/48000;timings.append(dict(start=start,end=end,latest_end=limit,text=words))
        print('voice',i,round(end,3),'limit',limit,flush=True)
        if end<=limit:pcm[round(start*48000)*2:round(start*48000)*2+len(data)]=data
    write(ROOT/'narration-timing.json',timings)
    assert all(c['end']<=c['latest_end'] for c in timings),'Shorten narration; never stretch live footage'
    with wave.open(str(folder/'narration.wav'),'wb') as w:w.setparams((1,2,48000,0,'NONE','not compressed'));w.writeframes(pcm)
    ff('-i',folder/'narration.wav','-af','loudnorm=I=-16:TP=-1.5:LRA=11','-ar',48000,'-c:a','aac','-b:a','128k',ROOT/'Muse-rc51-narration.m4a')
    subtitles(timings)

def subtitles(timings):
    subs=[]
    for i,c in enumerate(timings):
        t=c['text'];split=len(t)
        if len(t)>27:
            boundaries=[m.end() for m in re.finditer('[。；，]',t) if m.end()<len(t)]
            split=min(boundaries,key=lambda n:abs(n-len(t)/2)) if boundaries else math.ceil(len(t)/2)
        # Whole utterance on screen for its measured duration; no fabricated word alignment.
        subs.append(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+t[:split]+ ('\n'+t[split:] if split<len(t) else '')+'\n\n')
    (ROOT/'Muse-rc51.zh-CN.srt').write_text(''.join(subs).rstrip()+'\n')

def render():
    folder=TMP/'clips';folder.mkdir(exist_ok=True)
    for i,c in enumerate(CLIPS):
        p=folder/f'{i:02}.mp4'
        if not p.exists():ff('-f','concat','-safe',0,'-i',TMP/f'{i:02}.ffconcat','-vf','fps=30,format=yuv420p','-t',c['duration'],'-an','-c:v','libx264','-preset','veryfast','-crf',19,'-threads',2,p)
        print('encoded',c['id'],flush=True)
    listing=TMP/'edit.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{folder/f'{i:02}.mp4'}'\n" for i in range(len(CLIPS))))
    style='FontName=PingFang SC,FontSize=12,Outline=1,Shadow=0,MarginV=8'
    ff('-f','concat','-safe',0,'-i',listing,'-i',ROOT/'Muse-rc51-narration.m4a','-map','0:v:0','-map','1:a:0','-vf',f"subtitles=Muse-rc51.zh-CN.srt:force_style='{style}'",'-t',96,'-c:v','libx264','-preset','veryfast','-crf',19,'-threads',2,'-c:a','copy','-movflags','+faststart',VIDEO)

def qa():
    ff('-i',VIDEO,'-f','null','-')
    times=[1,9,18,26,34,42,49,56,61,67,77,88,93]
    folder=ROOT/'keyframes';folder.mkdir(exist_ok=True)
    for t in times:
        p=folder/f'{t:02}s.png'
        if not p.exists():ff('-ss',t,'-i',VIDEO,'-frames:v',1,p)
    result=subprocess.run([str(FF),'-hide_banner','-i',str(VIDEO),'-af','volumedetect','-vn','-f','null','-'],capture_output=True,text=True,check=True)
    # Store only technical stream/audio output, never source pixels or private text.
    clean_log=result.stderr.replace(str(ROOT)+'/', '')
    (ROOT/'decode-audio-qa.txt').write_text('\n'.join(line.rstrip() for line in clean_log.splitlines()).rstrip()+'\n')
    write(ROOT/'render-status.json',dict(duration_seconds=96,bytes=VIDEO.stat().st_size,sha256=sha(VIDEO),full_decode='PASS',keyframe_seconds=times,visual_qa='PENDING',audio_listening='NOT_PERFORMED',audio_measurement='decode-audio-qa.txt'))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('phase',choices=['prepare','narrate','render','qa']);a=p.parse_args()
    globals()[a.phase]()
