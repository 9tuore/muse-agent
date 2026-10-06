#!/usr/bin/env python3
"""Narrate actual, redacted rc10 window screenshots; never generate UI evidence."""
import argparse,hashlib,json,subprocess,wave
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
PRIVATE=HERE.parent/'.local-state'
FF=ROOT/'official_muse/rc/submission-ready-20261006-r1/media/.local-state/ffmpeg'
OCR=PRIVATE/'email-boxes-objc'
FONT='/System/Library/Fonts/PingFang.ttc'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):subprocess.run(list(map(str,args)),check=True,stdout=subprocess.DEVNULL)
def prepare(spec):
 out=HERE/'rc10-public';out.mkdir(exist_ok=True);tmp=PRIVATE/'rc10-video-work';tmp.mkdir(exist_ok=True)
 records=[];parts=[];srt=[];at=0
 for n,stage in enumerate(spec):
  raw=PRIVATE/stage['file'];assert raw.is_file(),raw
  if stage.get('cover'):
   canvas=Image.open(raw).convert('RGB').resize((1280,720),Image.Resampling.LANCZOS)
  else:
   im=Image.open(raw).convert('RGB');boxes=json.loads(subprocess.check_output([str(OCR),str(raw)]))[str(raw)]
   draw=ImageDraw.Draw(im)
   for x,y,w,h in boxes:
    rect=(int(x*im.width)-4,int(y*im.height)-4,int((x+w)*im.width)+4,int((y+h)*im.height)+4)
    draw.rectangle(rect,fill='#272a2e')
   meta=json.loads((PRIVATE/stage['meta']).read_text());rect=meta['rects'][stage.get('area','central_main')];sx=im.width/1400;sy=im.height/815
   x,y,w,h=rect;crop=im.crop((round(x*sx),round(y*sy),round((x+w)*sx),round((y+h)*sy)))
   crop.thumbnail((1160,530),Image.Resampling.LANCZOS);canvas=Image.new('RGB',(1280,720),'#15191e');canvas.paste(crop,((1280-crop.width)//2,105+(530-crop.height)//2))
   d=ImageDraw.Draw(canvas);d.text((48,28),stage['title'],font=ImageFont.truetype(FONT,34),fill='#edf3f5');d.text((48,78),'Muse rc9 → 0.3.27-rc10 · 实机截图回放 · 等待已压缩',font=ImageFont.truetype(FONT,18),fill='#9fb2b9');d.text((48,655),stage['caption'],font=ImageFont.truetype(FONT,22),fill='#a8dfdb')
  image=out/f'{n:02d}.png';canvas.save(image)
  text=tmp/f'{n:02d}.txt';text.write_text(stage['voice']);audio=tmp/f'{n:02d}.aiff';run(['/usr/bin/say','-v','Tingting','-r','180','-f',text,'-o',audio])
  wav=tmp/f'{n:02d}.wav';run([FF,'-hide_banner','-loglevel','error','-y','-i',audio,'-ar','24000',wav])
  with wave.open(str(wav)) as stream:spoken=stream.getnframes()/stream.getframerate()
  duration=max(stage.get('seconds',12),spoken+1)
  part=tmp/f'{n:02d}.mp4';run([FF,'-hide_banner','-loglevel','error','-y','-loop','1','-i',image,'-i',audio,'-r','10','-t',str(duration),'-af','apad','-c:v','libx264','-preset','veryfast','-crf','24','-pix_fmt','yuv420p','-c:a','aac','-b:a','96k',part]);parts.append(part)
  def stamp(t):return f'{int(t//3600):02d}:{int(t//60)%60:02d}:{int(t)%60:02d},{int((t%1)*1000):03d}'
  srt.append(f'{n+1}\n{stamp(at)} --> {stamp(at+duration)}\n{stage["voice"]}\n');at+=duration
  records.append({'stage':stage['title'],'actual_source_sha256':digest(raw),'public_image':image.name,'public_sha256':digest(image),'duration':duration,'kind':'USER_COVER' if stage.get('cover') else 'REAL_VISIBLE_MAKEPAD_SCREENSHOT','email_regions_masked':0 if stage.get('cover') else len(boxes)})
 playlist=tmp/'parts.txt';playlist.write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n" for p in parts));video=out/'Muse-Mail-Calendar-rc10.zh-CN.mp4';run([FF,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',playlist,'-c','copy','-movflags','+faststart',video]);run([FF,'-hide_banner','-loglevel','error','-i',video,'-f','null','-'])
 (out/'Muse-Mail-Calendar-rc10.zh-CN.srt').write_text('\n'.join(srt));(out/'RC9_PROVENANCE.json').write_text(json.dumps({'kind':'NARRATED_ACTUAL_TEST_SCREENSHOTS','continuous_recording':False,'voice':'macOS Tingting','duration_seconds':at,'video_sha256':digest(video),'full_decode_exit':0,'stages':records},ensure_ascii=False,indent=2)+'\n');print(video,video.stat().st_size)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('spec',type=Path);a=p.parse_args();prepare(json.loads(a.spec.read_text()))
