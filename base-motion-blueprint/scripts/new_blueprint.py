#!/usr/bin/env python3
"""base-motion-blueprint — ตั้งโปรเจกต์ + ภาพคนพูดความละเอียดสูง (กันภาพแตกตอนช็อตใกล้) + ถอดเสียง ElevenLabs Scribe
ใช้:
  python new_blueprint.py <ชื่อ> <คลิปที่ตัดแล้ว.mp4> [--rough <โฟลเดอร์ base-rough-cut>] [--srt <ซับ.srt>] [--no-scribe]
  --rough: อ่าน work/source.json (ไฟล์ดิบ) + work/keep.json (ช่วงที่เก็บ) → ตัดช่วงเดียวกันจากไฟล์ดิบเป็น 1620×2880
           (ไม่มี --rough = เกลี่ยสีจากคลิป 1080 · ต้องตั้ง CLOSE ≤ 1.25 ใน gen.py)
  ซับ: ถ้าไม่ใส่ --srt แต่มี --rough จะใช้ renders/roughcut.srt ของ base-rough-cut
โปรเจกต์อยู่ที่ $BASE_MOTION_HOME (ค่าเริ่มต้น ~/Developer/video-use) · คีย์ ElevenLabs: env หรือ ~/.elevenlabs/api_key (ไม่พิมพ์คีย์ออกจอ)"""
import argparse, json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
def die(m): print('❌', m); sys.exit(1)
ap = argparse.ArgumentParser(); ap.add_argument('name'); ap.add_argument('talk')
ap.add_argument('--rough'); ap.add_argument('--srt'); ap.add_argument('--no-scribe', action='store_true')
a = ap.parse_args()
if not os.path.isfile(a.talk): die(f'ไม่เจอคลิป: {a.talk}')
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(os.environ.get('BASE_MOTION_HOME', os.path.expanduser('~/Developer/video-use')), a.name)
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or die('ไม่เจอ ffmpeg')
FP = shutil.which('ffprobe') or die('ไม่เจอ ffprobe')
if os.path.exists(P): die(f'มีโปรเจกต์ชื่อนี้แล้ว: {P}')
GRADE = "curves=all='0/0.03 0.25/0.37 0.5/0.63 0.75/0.84 1/1',colorbalance=rs=0.03:bs=-0.03:rm=0.02:bm=-0.02,eq=saturation=1.06"
TONE = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,'
        'zscale=t=bt709:m=bt709:r=tv,format=yuv420p,')   # HLG/PQ → SDR แบบเดียวกับ base-rough-cut

# ---- ตั้งโฟลเดอร์ (ทำงานบนสำเนาเสมอ ไม่แตะไฟล์ต้นทาง) ----
for d in ('assets/sfx', 'fonts', 'work', 'renders'): os.makedirs(os.path.join(P, d))
T = os.path.join(K, 'template')
for f in ('gen.py', 'style.css', 'hyperframes.json', 'package.json'): shutil.copy(os.path.join(T, f), P)
for f in os.listdir(os.path.join(T, 'fonts')): shutil.copy(os.path.join(T, 'fonts', f), os.path.join(P, 'fonts'))
for f in os.listdir(os.path.join(K, 'assets', 'sfx')): shutil.copy(os.path.join(K, 'assets', 'sfx', f), os.path.join(P, 'assets', 'sfx'))
shutil.copy(os.path.join(K, 'scripts', 'align.py'), os.path.join(P, 'work'))
shutil.copy(a.talk, os.path.join(P, 'assets', 'talk.mp4'))
json.dump({'id': a.name, 'name': a.name}, open(os.path.join(P, 'meta.json'), 'w', encoding='utf-8'))
srt = a.srt or (os.path.join(a.rough, 'renders', 'roughcut.srt') if a.rough else None)
if srt and os.path.exists(srt): shutil.copy(srt, os.path.join(P, 'work', 'subs.srt'))
talk = os.path.join(P, 'assets', 'talk.mp4'); hi = os.path.join(P, 'assets', 'talk_hi.mp4')
dur = float(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', talk], capture_output=True, text=True).stdout)

# ---- ภาพความละเอียดสูงจากไฟล์ดิบ (ช็อตใกล้ 1.5× = พิกเซลจริง) ----
if a.rough:
    src = json.load(open(os.path.join(a.rough, 'work', 'source.json'), encoding='utf-8'))['src']
    keep = [k[:2] for k in json.load(open(os.path.join(a.rough, 'work', 'keep.json'), encoding='utf-8'))]
    # อ่านแบบ json: ไฟล์ดิบที่เก็บแบบหมุน มี side data ทำให้ csv ได้หลายบรรทัด → เคยเช็ก HLG พลาด ภาพออกมาเป็น HDR
    tr = json.loads(subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer', '-of', 'json', src],
                                   capture_output=True, text=True).stdout)['streams'][0].get('color_transfer', '')
    tone = TONE if tr in ('arib-std-b67', 'smpte2084') else ''
    fl = [f'[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]' for i, (s, e) in enumerate(keep)]
    fl.append(''.join(f'[v{i}]' for i in range(len(keep))) + f'concat=n={len(keep)}:v=1:a=0[cv]')
    fl.append(f'[cv]{tone}scale=-2:2880:flags=lanczos,crop=1620:2880,fps=30,{GRADE}[out]')   # ครอปกลางแบบเดียวกับ cut_1080
    print('… ตัดภาพ 1620×2880 จากไฟล์ดิบ (ใช้เวลาสักพัก)')
    subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', src, '-filter_complex', ';'.join(fl), '-map', '[out]',
                    '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p',
                    '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', hi], check=True)
    if json.loads(subprocess.run([FP, '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer', '-of', 'json', hi],
                                 capture_output=True, text=True).stdout)['streams'][0].get('color_transfer') != 'bt709':
        die('ภาพที่ได้ยังไม่ใช่ SDR bt709 — hyperframes จะเรนเดอร์แบบ HDR (ใช้ดิสก์ ~6 GB)')
    d2 = float(subprocess.run([FP, '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', hi], capture_output=True, text=True).stdout)
    if abs(d2 - dur) > 0.2: print(f'⚠ ความยาวภาพจากไฟล์ดิบ {d2:.2f} วิ ≠ คลิป {dur:.2f} วิ — เช็ก keep.json ว่าตรงกับคลิปที่ส่งมา')
else:
    subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', talk, '-an', '-vf', GRADE, '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', hi], check=True)
    print('⚠ ไม่มีไฟล์ดิบ: ภาพ 1080 · ตั้ง CLOSE ≤ 1.25 ใน gen.py ไม่งั้นช็อตใกล้แตก')

# ---- ถอดเสียง ElevenLabs Scribe ----
if not a.no_scribe:
    key = os.environ.get('ELEVENLABS_API_KEY') or ''
    kf = os.path.expanduser('~/.elevenlabs/api_key')
    if not key and os.path.exists(kf): key = open(kf, encoding='utf-8').read().strip()
    if not key: die('ไม่เจอคีย์ ElevenLabs — ใส่ไว้ที่ ~/.elevenlabs/api_key')
    audio = os.path.join(P, 'work', 'audio.mp3'); out = os.path.join(P, 'work', 'scribe.json')
    subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', talk, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'libmp3lame', '-b:a', '64k', audio], check=True)
    code = subprocess.run(['curl', '-s', '-X', 'POST', 'https://api.elevenlabs.io/v1/speech-to-text', '-H', f'xi-api-key: {key}',
                           '-F', 'model_id=scribe_v1', '-F', 'language_code=tha', '-F', 'timestamps_granularity=word',
                           '-F', f'file=@{audio}', '-o', out, '-w', '%{http_code}'], capture_output=True, text=True).stdout
    if code != '200': die(f'Scribe HTTP {code}: {open(out, encoding="utf-8").read()[:300]}')
    open(os.path.join(P, 'work', 'transcript.txt'), 'w', encoding='utf-8').write(json.load(open(out, encoding='utf-8'))['text'])
print(f'✅ {P}\n   TOTAL = {dur:.2f} (ใส่ใน gen.py) · ภาพ: assets/talk_hi.mp4 · ซับ: {"work/subs.srt" if os.path.exists(os.path.join(P, "work", "subs.srt")) else "ไม่มี (ใช้ CAPS ใน gen.py)"}')
