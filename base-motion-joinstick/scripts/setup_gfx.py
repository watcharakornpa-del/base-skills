#!/usr/bin/env python3
"""base-motion-joinstick ขั้น 3 — ตั้งโปรเจกต์กราฟิก <โปรเจกต์>/gfx จาก renders/cut_1080.mp4 + renders/roughcut.srt
ใช้: python setup_gfx.py <โฟลเดอร์โปรเจกต์>
- talk.mp4: ใช้ cut_1080.mp4 ตรง ๆ ถ้าแท็กสี Rec.709 + keyframe ถี่แล้ว (rough.py full ของสกิลนี้ทำให้) ไม่งั้นเข้ารหัสใหม่
  · ไฟล์ที่ยังติดแท็ก HLG → HyperFrames สลับโหมด HDR แล้วทิ้งชั้นกราฟิกทั้งหมด (เจอจริง C2673) · keyframe ห่าง = seek พลาด
- work/scribe.json: แปลงเวลาคำจากการถอดเสียงไฟล์ดิบ (work/scribe.json) ผ่านช่วงที่เก็บ (work/keep.json) เป็นเวลาหลังตัด
  ไม่ต้องส่งเสียงไปถอดซ้ำ (ประหยัด ~1 นาที + ค่า ElevenLabs) · at() ใน gen.py ใช้ไฟล์นี้
- ก๊อปซับเป็น work/subs.srt"""
import json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
P = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else sys.exit('ใช้: setup_gfx.py <โฟลเดอร์โปรเจกต์>')
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(K, 'template'); G = os.path.join(P, 'gfx')
cut, srt, keep, raw = (os.path.join(P, f) for f in ('renders/cut_1080.mp4', 'renders/roughcut.srt', 'work/keep.json', 'work/scribe.json'))
for f in (cut, srt, keep, raw):
    if not os.path.exists(f): sys.exit(f'❌ ไม่เจอ {f} — รัน rough.py build และ rough.py full ก่อน')
if os.path.exists(G): sys.exit(f'❌ มี {G} แล้ว')
FF, FP = shutil.which('ffmpeg'), shutil.which('ffprobe')
for d in ('assets', 'work', 'renders'): os.makedirs(os.path.join(G, d))
for f in ('gen.py', 'style.css', 'package.json', 'hyperframes.json', 'AGENTS.md', 'CLAUDE.md'): shutil.copy(os.path.join(T, f), G)
shutil.copytree(os.path.join(T, 'fonts'), os.path.join(G, 'fonts')); shutil.copytree(os.path.join(T, 'sfx'), os.path.join(G, 'assets/sfx'))
shutil.copy(os.path.join(K, 'scripts/align.py'), os.path.join(G, 'work')); shutil.copy(os.path.join(K, 'scripts/caps2srt.py'), os.path.join(G, 'work')); shutil.copy(srt, os.path.join(G, 'work/subs.srt'))

probe = lambda f, e: json.loads(subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', e, '-of', 'json', f],
                                               capture_output=True, text=True).stdout)
trc = probe(cut, 'stream=color_transfer')['streams'][0].get('color_transfer')
kf = [float(x['pts_time']) for x in json.loads(subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-read_intervals', '%+10', '-skip_frame', 'nokey',
      '-show_entries', 'frame=pts_time', '-of', 'json', cut], capture_output=True, text=True).stdout)['frames']]
talk = os.path.join(G, 'assets/talk.mp4')
if trc == 'bt709' and len(kf) >= 8:
    shutil.copy(cut, talk); how = 'ก๊อปตรง'
else:
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', cut, '-vf', 'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '17', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
                    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', '-c:a', 'copy', '-y', talk], check=True)
    how = f'เข้ารหัสใหม่ (เดิมแท็ก {trc} · keyframe {len(kf)} ใน 10 วิ)'

# เวลาคำ: ไฟล์ดิบ → หลังตัด (ช่วงที่เก็บต่อกันตามลำดับใน keep.json)
# concat ปัดภาพแต่ละช่วงขึ้นเป็นเฟรมเต็มของไฟล์ดิบ แล้วเลื่อนเสียงช่วงถัดไปตาม → ต้องใช้ความยาวที่ปัดแล้ว (ไม่งั้นเพี้ยนสะสม ~0.1%)
import math
src = json.load(open(os.path.join(P, 'work/source.json'), encoding='utf-8'))['src']
num, den = map(int, probe(src, 'stream=r_frame_rate')['streams'][0]['r_frame_rate'].split('/')); fr = num / den
seglen = lambda s, e: max(e - s, (math.ceil(e * fr - 1e-6) - math.ceil(s * fr - 1e-6)) / fr)
segs = json.load(open(keep, encoding='utf-8')); W = json.load(open(raw, encoding='utf-8'))['words']; out = []; t0 = 0.0
for s, e in segs:
    for w in W:
        if s <= w['start'] < e:
            out.append({**w, 'start': round(t0 + w['start'] - s, 3), 'end': round(t0 + min(w['end'], e) - s, 3)})
    t0 += seglen(s, e)
text = ''.join(w['text'] for w in out)
json.dump({'text': text, 'words': out}, open(os.path.join(G, 'work/scribe.json'), 'w', encoding='utf-8'), ensure_ascii=False)
open(os.path.join(G, 'work/transcript.txt'), 'w', encoding='utf-8').write(text)
dur = float(json.loads(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', talk], capture_output=True, text=True).stdout)['format']['duration'])
print(f'✅ {G} · TOTAL = {dur:.2f} · talk.mp4 {how} · เวลาคำจากไฟล์ดิบ {len(out)} token · แก้ "ตั้งค่าต่อคลิป" + ฉากใน gen.py')
