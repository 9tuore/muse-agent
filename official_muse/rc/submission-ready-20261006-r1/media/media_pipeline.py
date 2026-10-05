#!/usr/bin/env python3
"""Offline narration/subtitles and final encode. No capture, app control or upload.

All arguments are paths relative to this media directory. Use fresh output
directories. encode requires an already edited real recording and its reviewed
provenance; it never manufactures application frames or lengthens footage.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import wave

ROOT = Path(__file__).resolve().parent
FFMPEG = ROOT / '.local-state/ffmpeg'


def path(value):
    p = (ROOT / value).resolve()
    if not p.is_relative_to(ROOT):
        raise ValueError('Path must stay inside the owned media directory')
    return p


def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def run(args, cwd=None):
    subprocess.run([str(x) for x in args], cwd=cwd, check=True,
                   stdout=subprocess.DEVNULL)


def ff(*args, cwd=None):
    if not FFMPEG.is_file():
        raise FileNotFoundError('Verified local ffmpeg is missing; see README')
    run([FFMPEG, '-hide_banner', '-loglevel', 'error', '-nostdin', '-n', *args], cwd)


def stamp(seconds):
    ms = round(seconds * 1000)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'


def duration_of(video):
    # ffmpeg -i without an output intentionally exits nonzero after inspection.
    result = subprocess.run([str(FFMPEG), '-hide_banner', '-nostdin', '-i', str(video)],
                            capture_output=True, text=True)
    match = re.search(r'Duration: (\d+):(\d+):([\d.]+)', result.stderr)
    if not match:
        raise ValueError('Cannot establish media duration')
    return int(match[1]) * 3600 + int(match[2]) * 60 + float(match[3])


def wrapped(text, width=25):
    # Chinese captions, capped by character count; inspect rendered line breaks.
    return '\n'.join(text[i:i + width] for i in range(0, len(text), width))


def narrate(args):
    source = path(args.script)
    spec = json.loads(source.read_text())
    out = path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    gap = round(float(spec.get('gap_seconds', .25)) * 48000)
    if not 0 <= gap <= 48000:
        raise ValueError('Gap must be between zero and one second')
    cues, chapters = [], []
    cursor = 0
    with wave.open(str(out / 'narration.wav'), 'wb') as combined:
        combined.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        for chapter in spec['chapters']:
            chapter_start = cursor / 48000
            for segment in chapter['segments']:
                i = len(cues)
                text_file = out / f'{i:02}.txt'
                text_file.write_text(segment['spoken'])
                aiff, pcm = out / f'{i:02}.aiff', out / f'{i:02}.wav'
                run(['/usr/bin/say', '-v', spec['voice'], '-r', str(spec['rate']),
                     '-f', text_file, '-o', aiff])
                ff('-i', aiff, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', pcm)
                with wave.open(str(pcm), 'rb') as audio:
                    count = audio.getnframes()
                    combined.writeframes(audio.readframes(count))
                cues.append({'chapter': chapter['id'], 'text': segment['subtitle'],
                             'start': cursor / 48000, 'end': (cursor + count) / 48000})
                cursor += count
                combined.writeframes(b'\0\0' * gap)
                cursor += gap
            chapters.append({'id': chapter['id'], 'title': chapter['title'],
                             'start': chapter_start, 'end': cursor / 48000})
    srt = ''.join(f'{i + 1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'
                  f'{wrapped(c["text"])}\n\n' for i, c in enumerate(cues))
    (out / 'subtitles.srt').write_text(srt)
    ff('-i', out / 'narration.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
       '-ar', '48000', '-c:a', 'aac', '-b:a', '128k', out / 'narration.m4a')
    result = {'status': spec['status'], 'script_sha256': sha(source),
              'voice': spec['voice'], 'rate': spec['rate'], 'paid_calls': 0,
              'duration_seconds': cursor / 48000, 'chapters': chapters, 'cues': cues,
              'narration_sha256': sha(out / 'narration.m4a'),
              'subtitles_sha256': sha(out / 'subtitles.srt')}
    (out / 'timing.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'out': str(out.relative_to(ROOT)), 'duration_seconds': cursor / 48000}))


def encode(args):
    manifest_path = path(args.manifest)
    spec = json.loads(manifest_path.read_text())
    # This gate is a required review record, not automatic proof of provenance.
    if spec.get('review_status') != 'APPROVED_REAL_CAPTURE_EDIT':
        raise ValueError('Final capture/provenance review is required')
    if not spec.get('source_recordings') or not spec.get('edit_decisions'):
        raise ValueError('Original recordings and exact edit decisions required')
    for source in spec['source_recordings']:
        if sha(path(source['path'])) != source['sha256']:
            raise ValueError('Original recording hash changed')
    video = path(spec['edited_video'])
    if sha(video) != spec['edited_video_sha256']:
        raise ValueError('Edited video hash changed')
    duration = float(spec['duration_seconds'])
    if not 120 <= duration <= 180:
        raise ValueError('Final duration must be 120–180 seconds')
    if abs(duration_of(video) - duration) > .1:
        raise ValueError('Actual edited-video duration differs from manifest')
    narration = path(spec['narration_directory'])
    timing = json.loads((narration / 'timing.json').read_text())
    if timing['status'] != 'FINAL_FOOTAGE_MATCHED' or abs(timing['duration_seconds'] - duration) > .05:
        raise ValueError('Final narration must match the edited timeline without freeze/stretch')
    if sha(narration / 'narration.m4a') != timing['narration_sha256']:
        raise ValueError('Narration changed')
    if sha(narration / 'subtitles.srt') != timing['subtitles_sha256']:
        raise ValueError('Subtitles changed')
    out = path(args.out)
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(narration / 'subtitles.srt', out / 'subtitles.srt')
    filters = ['scale=1600:900:force_original_aspect_ratio=decrease',
               'pad=1600:900:(ow-iw)/2:(oh-ih)/2:color=0x0d1424', 'setsar=1']
    for mask in spec.get('masks', []):
        x, y, w, h = [int(mask[k]) for k in ('x', 'y', 'w', 'h')]
        start, end = float(mask['start']), float(mask['end'])
        if not (0 <= x < x + w <= 1600 and 0 <= y < y + h <= 900 and 0 <= start < end <= duration):
            raise ValueError('Invalid mask in normalized 1600x900 coordinates')
        filters.append(f"drawbox=x={x}:y={y}:w={w}:h={h}:color=0x111827:t=fill:enable='between(t,{start},{end})'")
    style = 'FontName=PingFang SC,FontSize=22,Outline=1,Shadow=0,MarginV=22'
    filters += [f"subtitles=subtitles.srt:force_style='{style}'", 'fps=30', 'format=yuv420p']
    ff('-i', video, '-i', narration / 'narration.m4a', '-map', '0:v:0', '-map', '1:a:0',
       '-vf', ','.join(filters), '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
       '-maxrate', '4M', '-bufsize', '8M', '-threads', '2', '-c:a', 'aac', '-b:a', '128k',
       '-movflags', '+faststart', out / 'muse-demo.mp4', cwd=out)
    # Full decode is mandatory. Pixel/audio/factual QA remains human/agent work.
    ff('-i', out / 'muse-demo.mp4', '-f', 'null', '-')
    actual_duration = duration_of(out / 'muse-demo.mp4')
    if not 120 <= actual_duration <= 180 or abs(actual_duration - duration) > .1:
        raise ValueError('Encoded duration is outside the frozen timeline')
    for i, seconds in enumerate((0, duration / 3, duration * 2 / 3, max(0, duration - 1))):
        ff('-ss', str(seconds), '-i', out / 'muse-demo.mp4', '-frames:v', '1', out / f'qa-{i}.png')
    result = {'status': 'ENCODED_FULL_DECODE_PASS_VISUAL_AUDIO_QA_PENDING',
              'input_manifest_sha256': sha(manifest_path), 'video_sha256': sha(out / 'muse-demo.mp4'),
              'bytes': (out / 'muse-demo.mp4').stat().st_size,
              'actual_duration_seconds': actual_duration,
              'frame_rate_note': '30fps output; original capture cadence remains in provenance',
              'original_audio_used': False, 'automated_claim': 'Encoding/decode only, not action success'}
    (out / 'encode-result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    n = sub.add_parser('narrate')
    n.add_argument('--script', required=True)
    n.add_argument('--out', required=True)
    n.set_defaults(func=narrate)
    e = sub.add_parser('encode')
    e.add_argument('--manifest', required=True)
    e.add_argument('--out', required=True)
    e.set_defaults(func=encode)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
