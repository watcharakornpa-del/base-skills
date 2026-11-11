#!/usr/bin/env python3
"""base-motion-joinstick ขั้น 3 — ตั้งโปรเจกต์กราฟิก <โปรเจกต์>/gfx จาก renders/cut_1080.mp4 + renders/roughcut.srt
ใช้: python setup_gfx.py <โฟลเดอร์โปรเจกต์>
- เข้ารหัส talk.mp4 ใหม่: แท็กสี Rec.709 (setparams) + keyframe ทุก 30 เฟรม
  · ถ้าไฟล์ยังติดแท็ก HLG จากไฟล์ดิบ HyperFrames จะสลับเป็นโหมด HDR แล้วทิ้งชั้นกราฟิกทั้งหมด (เจอจริง C2673)
  · keyframe ห่าง = วิดีโอค้าง/seek พลาดตอนเรนเดอร์
- ถอดเสียงคลิปที่ตัดแล้วอีกรอบ (work/scribe.json ให้ at() ใช้หาเวลา) · ก๊อปซับเป็น work/subs.srt"""
import json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
P = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else sys.exit('ใช้: setup_gfx.py <โฟลเดอร์โปรเจกต์>')
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); T = os.path.join(K, 'template'); G = os.path.join(P, 'gfx')
cut, srt = os.path.join(P, 'renders/cut_1080.mp4'), os.path.join(P, 'renders/roughcut.srt')
for f in (cut, srt):
    if not os.path.exists(f): sys.exit(f'❌ ไม่เจอ {f} — รัน rough.py build และ rough.py full ก่อน')
if os.path.exists(G): sys.exit(f'❌ มี {G} แล้ว')
FF, FP = shutil.which('ffmpeg'), shutil.which('ffprobe')
for d in ('assets', 'work', 'renders'): os.makedirs(os.path.join(G, d))
for f in ('gen.py', 'style.css', 'package.json', 'hyperframes.json', 'AGENTS.md', 'CLAUDE.md'): shutil.copy(os.path.join(T, f), G)
shutil.copytree(os.path.join(T, 'fonts'), os.path.join(G, 'fonts')); shutil.copytree(os.path.join(T, 'sfx'), os.path.join(G, 'assets/sfx'))
shutil.copy(os.path.join(K, 'scripts/align.py'), os.path.join(G, 'work')); shutil.copy(srt, os.path.join(G, 'work/subs.srt'))
subprocess.run([FF, '-nostdin', '-v', 'error', '-i', cut, '-vf', 'setparams=color_primaries=bt709:color_trc=bt709:colorspace=bt709',
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-g', '30', '-keyint_min', '30', '-pix_fmt', 'yuv420p',
                '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-movflags', '+faststart', '-c:a', 'copy',
                '-y', os.path.join(G, 'assets/talk.mp4')], check=True)
os.chdir(G)
subprocess.run([sys.executable, os.path.join(K, 'scripts/transcribe.py'), 'assets/talk.mp4'], check=True)
info = json.loads(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration:stream=color_transfer', '-of', 'json', 'assets/talk.mp4'],
                                 capture_output=True, text=True).stdout)
trc = info['streams'][0].get('color_transfer')
if trc != 'bt709': sys.exit(f'❌ talk.mp4 ยังติดแท็กสี {trc} — HyperFrames จะทิ้งกราฟิก')
print(f'✅ {G} · TOTAL = {float(info["format"]["duration"]):.2f} · แท็กสี {trc} · แก้ "ตั้งค่าต่อคลิป" + ฉากใน gen.py')
