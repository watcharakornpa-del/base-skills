#!/usr/bin/env python3
"""base-motion-collage — ตั้งโปรเจกต์ใหม่ + ถอดเสียงด้วย ElevenLabs Scribe (ใช้ได้ทั้ง Windows และ Mac)
ใช้: python new_collage.py <ชื่อโปรเจกต์> <คลิปพูด.mp4> [ซับทีม.srt]
โปรเจกต์อยู่ที่ $BASE_MOTION_HOME (ค่าเริ่มต้น ~/Developer/video-use)
คีย์ ElevenLabs: env ELEVENLABS_API_KEY หรือไฟล์ ~/.elevenlabs/api_key (สคริปต์ไม่พิมพ์คีย์ออกจอ)"""
import json, os, shutil, subprocess, sys

def die(msg): print('❌', msg); sys.exit(1)
sys.stdout.reconfigure(encoding='utf-8')
if len(sys.argv) < 3 or not os.path.isfile(sys.argv[2]): die('ใช้: new_collage.py <ชื่อ> <คลิป.mp4> [ซับ.srt]')
name, src = sys.argv[1], sys.argv[2]; srt = sys.argv[3] if len(sys.argv) > 3 else None
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))           # โฟลเดอร์สกิล
P = os.path.join(os.environ.get('BASE_MOTION_HOME', os.path.expanduser('~/Developer/video-use')), name)
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or die('ไม่เจอ ffmpeg')
FP = shutil.which('ffprobe') or die('ไม่เจอ ffprobe')
key = os.environ.get('ELEVENLABS_API_KEY')
if not key:
    kf = os.path.expanduser('~/.elevenlabs/api_key')
    key = open(kf, encoding='utf-8').read().strip() if os.path.exists(kf) else ''
if not key: die('ไม่เจอคีย์ ElevenLabs — ใส่ไว้ที่ ~/.elevenlabs/api_key')
if os.path.exists(P): die(f'มีโปรเจกต์ชื่อนี้แล้ว: {P}')

for d in ('assets/sfx', 'assets/cut', 'assets/raw', 'fonts', 'work', 'renders'): os.makedirs(os.path.join(P, d))
T = os.path.join(K, 'template')
for f in ('package.json', 'hyperframes.json', 'AGENTS.md', 'CLAUDE.md', 'style.css', 'gen.py'):
    shutil.copy(os.path.join(T, f), P)
pj = os.path.join(P, 'package.json'); s = open(pj, encoding='utf-8').read().replace('base-motion-project', name)
open(pj, 'w', encoding='utf-8').write(s)
json.dump({'id': name, 'name': name}, open(os.path.join(P, 'meta.json'), 'w', encoding='utf-8'))
for f in os.listdir(os.path.join(T, 'fonts')): shutil.copy(os.path.join(T, 'fonts', f), os.path.join(P, 'fonts'))
for f in os.listdir(os.path.join(K, 'assets', 'sfx')): shutil.copy(os.path.join(K, 'assets', 'sfx', f), os.path.join(P, 'assets', 'sfx'))
for f in ('align.py', 'cutout.py', 'srt_check.py', 'compose.py', 'premiere_segs.py'): shutil.copy(os.path.join(K, 'scripts', f), os.path.join(P, 'work'))
for f in ('grain.png', 'crumple.png'): shutil.copy(os.path.join(K, 'assets', f), os.path.join(P, 'assets'))
shutil.copy(src, os.path.join(P, 'assets', 'talk.mp4'))
if srt: shutil.copy(srt, os.path.join(P, 'work', 'team.srt'))

# ถอดเสียง: ElevenLabs Scribe (แม่นกว่า whisper ภาษาไทยมาก)
audio = os.path.join(P, 'work', 'audio.mp3')
subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', os.path.join(P, 'assets', 'talk.mp4'), '-vn', '-ac', '1', '-ar', '16000',
                '-c:a', 'libmp3lame', '-b:a', '64k', audio], check=True)
out = os.path.join(P, 'work', 'scribe.json')
code = subprocess.run(['curl', '-s', '-X', 'POST', 'https://api.elevenlabs.io/v1/speech-to-text', '-H', f'xi-api-key: {key}',
                       '-F', 'model_id=scribe_v1', '-F', 'language_code=tha', '-F', 'timestamps_granularity=word',
                       '-F', f'file=@{audio}', '-o', out, '-w', '%{http_code}'], capture_output=True, text=True).stdout
if code != '200': die(f'Scribe HTTP {code}: {open(out, encoding="utf-8").read()[:300]}')
info = subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration:stream=width,height,r_frame_rate', '-of', 'compact',
                       os.path.join(P, 'assets', 'talk.mp4')], capture_output=True, text=True).stdout
print(info.strip())
txt = json.load(open(out, encoding='utf-8'))['text']
open(os.path.join(P, 'work', 'transcript.txt'), 'w', encoding='utf-8').write(txt)
print('✅', P, '· ข้อความถอดเสียง: work/transcript.txt')
