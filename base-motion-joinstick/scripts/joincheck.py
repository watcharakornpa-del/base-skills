#!/usr/bin/env python3
"""สแกนทุกจุดต่อหาเศษคำที่หลุด (C2676: ตัดประโยคทิ้งแล้วยังได้ยิน "ส…" ของคำว่าสอง 40 ms)
ใช้ (จากโฟลเดอร์โปรเจกต์ หลัง rough.py build): python joincheck.py
แจ้งเมื่อ ท้ายชิ้นดัง (> −30 dB) ทั้งที่ 0.2 วิก่อนหน้ามีช่วงเงียบ หรือหัวชิ้นดังแล้วตามด้วยเงียบ → เปิด energy.py ดูแล้วย้ายจุดตัดไปช่วงเงียบจริง
บางจุดเป็นคำที่ตั้งใจเก็บ (เปิด|เว็บ · เอา|แปล) — ดูข้อความประกอบก่อนแก้"""
import json, math, shutil, struct, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
K = json.load(open('work/keep.json', encoding='utf-8'))
d = subprocess.run([shutil.which('ffmpeg'), '-nostdin', '-v', 'error', '-i', 'work/audio.mp3', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True).stdout
n = len(d) // 2; s = struct.unpack('<%dh' % n, d)
def db(t0, t1):
    seg = s[int(t0 * 8000):int(t1 * 8000)] or (0,)
    return 20 * math.log10(math.sqrt(sum(x * x for x in seg) / len(seg)) / 32768 + 1e-9)
W = [w for w in json.load(open('work/scribe.json', encoding='utf-8'))['words'] if w['type'] == 'word']
near = lambda t: ''.join(w['text'] for w in W if t - 0.6 <= w['start'] <= t + 0.6)
sus = 0
for i, (st, e) in enumerate(K):
    if i + 1 < len(K) and K[i + 1][0] - e > 0.3 and db(e - 0.04, e) > -30 and min(db(e - 0.2 + k * 0.02, e - 0.18 + k * 0.02) for k in range(7)) < -35:
        sus += 1; print(f'ท้ายชิ้น {e:.2f}s ดังหลังช่วงเงียบ · "{near(e)}"')
    if i and st - K[i - 1][1] > 0.3 and db(st, st + 0.04) > -30 and min(db(st + 0.06 + k * 0.02, st + 0.08 + k * 0.02) for k in range(7)) < -35:
        sus += 1; print(f'หัวชิ้น {st:.2f}s ดังแล้วเงียบ · "{near(st)}"')
print(f'{len(K)} ชิ้น · น่าสงสัย {sus} จุด')
