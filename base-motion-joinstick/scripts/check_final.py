#!/usr/bin/env python3
"""เช็คลิสต์ก่อนบอก "เสร็จ" — ตรวจจากไฟล์ส่งจริง (ผู้ใช้จับพลาดได้ทุกข้อนี้ใน C2675/C2676)
ใช้ (จากโฟลเดอร์โปรเจกต์): python check_final.py <ไฟล์ส่ง.mp4>
1 ffprobe 1080×1920 · ภาพ = เสียง   2 loudness   3 voice.wav ใหม่กว่า talk.mp4 (เสียงค้างจากตัดเก่า = ไม่ตรงปาก)
4 ซิงค์: cross-correlation เสียงไฟล์ส่ง vs talk.mp4 6 จุด ≤ 40 ms   5 เดดแอร์ที่เหลือ   6 ซับไม่ทับ Super/การ์ด/B-roll (gfx/work/hide.json)
7 ถอดเสียงไฟล์ส่งใหม่ → repeats.py (ADJ ต้องว่าง ยกเว้นภาษาปกติ · NEAR อ่านทีละจุด)
ยังต้องทำเอง: ดึงเฟรมจาก MP4 ทุกฉาก + ซูมฟอนต์ไทย · อ่าน transcript ทั้งเรื่องดูเนื้อหาสับสน"""
import json, os, re, shutil, subprocess, sys, numpy as np
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
F = sys.argv[1]; FF, FP = shutil.which('ffmpeg'), shutil.which('ffprobe'); here = os.path.dirname(os.path.abspath(__file__)); bad = []
st = json.loads(subprocess.run([FP, '-v', 'error', '-show_entries', 'stream=codec_type,width,height,duration', '-of', 'json', F], capture_output=True, text=True).stdout)['streams']
v = next(x for x in st if x['codec_type'] == 'video'); a = next((x for x in st if x['codec_type'] == 'audio'), None)
print(f"1 ภาพ {v['width']}×{v['height']} {float(v['duration']):.2f}s · เสียง {float(a['duration']):.2f}s" if a else '1 ❌ ไม่มีเสียง')
if not a or (v['width'], v['height']) != (1080, 1920) or abs(float(v['duration']) - float(a['duration'])) > 0.1: bad.append('1')
lg = subprocess.run([FF, '-nostdin', '-i', F, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print('2', ' · '.join(re.findall(r'(I:\s+-?[\d.]+ LUFS|Peak:\s+-?[\d.]+ dBFS)', lg)[-2:]))
T, V = 'gfx/assets/talk.mp4', 'gfx/assets/voice.wav'
ok = os.path.exists(V) and os.path.getmtime(V) >= os.path.getmtime(T); print('3 voice.wav', 'ใหม่กว่า talk.mp4 ✓' if ok else '❌ เก่ากว่า talk.mp4 — เสียงค้างจากชุดตัดเก่า'); ok or bad.append('3')
pcm = lambda f, t: np.frombuffer(subprocess.run([FF, '-nostdin', '-v', 'error', '-ss', str(t), '-t', '4', '-i', f, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout, np.int16).astype(float)
dur = float(v['duration']); lags = []
for t in np.linspace(5, dur - 10, 6):
    x, y = pcm(F, t), pcm(T, t)[4000:12000]; c = np.correlate(x, y, 'valid'); lags.append(round((int(np.argmax(c)) - 4000) / 8, 1))
print('4 ซิงค์ (ms):', lags); max(map(abs, lags)) <= 40 or bad.append('4')
sl = re.findall(r'silence_duration: ([\d.]+)', subprocess.run([FF, '-nostdin', '-i', F, '-af', 'silencedetect=noise=-35dB:d=0.15', '-f', 'null', '-'], capture_output=True, text=True).stderr)
print(f'5 เงียบ ≥ 0.15 วิ: {len(sl)} จุด (≥ 0.3 วิ: {sum(float(x) >= 0.3 for x in sl)})'); sum(float(x) >= 0.3 for x in sl) and bad.append('5')
if os.path.exists('gfx/work/hide.json') and os.path.exists('gfx/index.html'):
    h = open('gfx/index.html', encoding='utf-8').read(); H = json.load(open('gfx/work/hide.json'))
    on = {k: float(t) for k, t in re.findall(r"tl\.fromTo\('#sb(\d+)',\{opacity:0\},\{opacity:1,duration:0\.01\},([\d.]+)\)", h)}
    off = {k: float(t) for k, t in re.findall(r"tl\.set\('#sb(\d+)',\{opacity:0\},([\d.]+)\)", h)}
    ov = [k for k in on for x, y in H if on[k] < y - 0.01 and off.get(k, 0) > x + 0.01]
    txt = [s for s in re.findall(r'id="sb\d+">([^<]*)<', h) if re.search('อ่ะ|เนาะ|เนอะ|ป่ะ', s) or len(s) > 30]
    print(f'6 ซับ {len(on)} บรรทัด · ทับกราฟิก {len(ov)} · คำต้องห้าม/ยาวเกิน {txt}'); (ov or txt) and bad.append('6')
os.makedirs('work', exist_ok=True); out = os.path.abspath('work/final_scribe.json')
subprocess.run([sys.executable, os.path.join(here, 'retranscribe.py'), F, out], check=True)
ci = subprocess.run([sys.executable, os.path.join(here, 'cicheck.py'), '.'], capture_output=True, text=True) if os.path.exists('gfx/style.css') else None
print('8 CI', ci.stdout.strip() if ci else '(ไม่มี gfx/)'); ci and ci.returncode and bad.append('8 CI')
print('7'); subprocess.run([sys.executable, os.path.join(here, 'repeats.py'), out])
print('\n❌ ไม่ผ่าน: ' + ', '.join(bad) if bad else '\n✅ ผ่านข้อ 1–6 + 8 CI · ข้อ 7 อ่านผลเอง · ยังต้องดึงเฟรมจาก MP4 ทุกฉาก + ซูมปก/ฟอนต์ไทย + อ่าน transcript ทั้งเรื่อง')
