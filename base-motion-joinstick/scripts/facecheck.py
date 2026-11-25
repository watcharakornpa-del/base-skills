#!/usr/bin/env python3
"""S1 (ผู้ใช้สั่ง 25 พ.ย. 2026): ห้าม Super / การ์ด / ซับ / กราฟิก ทับหน้าหรือหัวคนพูด
เทียบไฟล์ส่งกับ gfx/assets/talk.mp4 ทุก 0.5 วิ ในกรอบหัว → ตรงไหนพิกเซลต่างกันเยอะ = มีกราฟิกทับหัว
ข้ามช่วงเต็มจอ (ปก + B-roll/insert จาก gfx/work/full.json) เพราะตั้งใจทับ และมีหน้าในวงกลมแล้ว
กรอบหัว: HEAD_BOX = 'x0:y0:x1:y1' ใน gfx/gen.py (ตั้งจาก contact sheet ขั้น 4) · ไม่มี → ประมาณจาก FACE_CROP (หัวกิน ~ครึ่งวง)
ใช้ (จากโฟลเดอร์โปรเจกต์): python facecheck.py <ไฟล์ส่ง.mp4>  · ไม่ผ่าน = exit 1 + บอกเวลา → ขยับ Super/การ์ดออกจากหัว"""
import json, re, shutil, subprocess, sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
FF = shutil.which('ffmpeg') or 'ffmpeg'
OUT = sys.argv[1]; STEP = 0.5; TH, AREA = 45, 0.03     # ต่าง > 45 (0–255) เกิน 3% ของกรอบหัว = ทับ (ต่ำกว่านี้คือ noise จากการบีบอัด)
src = open('gfx/gen.py', encoding='utf-8').read()
m = re.search(r"^HEAD_BOX = '(\d+):(\d+):(\d+):(\d+)'", src, re.M)
if m: x0, y0, x1, y1 = map(int, m.groups())
else:
    w, h, x, y = map(int, re.search(r"^FACE_CROP = '(\d+):(\d+):(\d+):(\d+)'", src, re.M).groups())
    x0, y0, x1, y1 = x + w * 22 // 100, y + h * 8 // 100, x + w * 78 // 100, y + h * 70 // 100
W, H = (x1 - x0) // 4 * 2, (y1 - y0) // 4 * 2   # ย่อครึ่ง (เลขคู่) ให้เร็ว
FULL = json.load(open('gfx/work/full.json'))
def frames(f):
    raw = subprocess.run([FF, '-nostdin', '-v', 'error', '-i', f, '-vf', f'fps={1 / STEP},scale=1080:1920,crop={x1 - x0}:{y1 - y0}:{x0}:{y0},scale={W}:{H},format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.int16)
a, b = frames(OUT), frames('gfx/assets/talk.mp4')
bad = []
for i in range(min(len(a), len(b))):
    t = i * STEP
    if any(s - 0.4 <= t <= e + 0.4 for s, e in FULL) or t > len(b) * STEP - 1.0: continue   # ท้ายคลิปเฟดดำ 0.5 วิ
    p = float((np.abs(a[i] - b[i]) > TH).mean())
    if p > AREA: bad.append((t, p))
print(f'S1 กรอบหัว x{x0}–{x1} y{y0}–{y1} ({"HEAD_BOX" if m else "ประมาณจาก FACE_CROP"}) · ตรวจ {min(len(a), len(b))} เฟรม')
if not bad: print('✅ S1 ไม่มีกราฟิกทับหัวคนพูด'); sys.exit(0)
runs = []                     # รวมเวลาที่ติดกันเป็นช่วง
for t, p in bad:
    if runs and t - runs[-1][1] <= STEP + 0.01: runs[-1][1] = t; runs[-1][2] = max(runs[-1][2], p)
    else: runs.append([t, t, p])
for s, e, p in runs: print(f'⛔ S1 ทับหัว {s:.1f}–{e + STEP:.1f} วิ (สูงสุด {p:.0%} ของกรอบหัว)')
sys.exit(1)
