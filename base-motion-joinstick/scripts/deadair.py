#!/usr/bin/env python3
"""เดดแอร์จากเสียงจริง → เพิ่มลง work/cuts.json "cut_times" (ลบของรอบก่อนที่ขึ้นต้น "เดดแอร์" ก่อน)
ใช้ (จากโฟลเดอร์โปรเจกต์ มี work/rough.py): python deadair.py  แล้ว rough.py build อีกรอบ (สคริปต์ build ให้เองหนึ่งรอบก่อนคำนวณ)
ค่าที่ผู้ใช้ผ่าน (C2676): เงียบ < −32 dB นาน ≥ 0.15 วิ ในช่วงที่เก็บ → เหลือ 0.12 วิ (0.06 หัว/ท้าย)
Lot 2 SJAI (25 พ.ย. 2026 ฟีดแบ็ค Lot 1 "ตัดฉับ ๆ หายใจไม่ทัน"): เหลือ 0.24 วิ (0.12 หัว/ท้าย) · ยังต่ำกว่าเกณฑ์เดดแอร์ 0.3 วิของ check_final
ห้ามใช้ช่องว่างเวลาตัวอักษรของ Scribe แทน (ไม่ใช่ความเงียบจริง เคยตัดคำทิ้ง)"""
import json, re, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
TH, D, LEAVE = -32, 0.15, 0.12
C = json.load(open('work/cuts.json', encoding='utf-8'))
# ลบเดดแอร์รอบก่อน แล้ว build ใหม่ก่อนคำนวณ — ไม่งั้น keep.json ยังมีรูจากรอบเก่า ช่วงเงียบที่รอบเก่าตัดจะไม่ถูกเพิ่มกลับ (C2675 Draft 5 เหลือเงียบ 0.54 วิ)
C['cut_times'] = [c for c in C.get('cut_times', []) if not c[2].startswith('เดดแอร์')]
json.dump(C, open('work/cuts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
subprocess.run([sys.executable, 'work/rough.py', 'build', '--no-preview'], check=True, stdout=subprocess.DEVNULL)
K = json.load(open('work/keep.json', encoding='utf-8'))
log = subprocess.run([shutil.which('ffmpeg'), '-nostdin', '-i', 'work/audio.mp3', '-af', f'silencedetect=noise={TH}dB:d={D}', '-f', 'null', '-'],
                     capture_output=True, text=True).stderr
st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]; en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
# ห้ามตัดทับคำ: คำที่พูดเบา (< −32 dB) silencedetect นับเป็นเงียบ (C2680 "การจัดข้อมูล" → "จัด" หาย) → หักช่วงตัวอักษร Scribe ออกก่อน
W = [w for w in json.load(open('work/scribe.json', encoding='utf-8'))['words'] if w['type'] == 'word']
CHR = sorted((w['start'], min(w['end'], w['start'] + 0.12)) for w in W)   # เวลาจบของ Scribe ลากเข้าช่วงเงียบ → นับแค่ 0.12 วิแรกของตัวอักษร
def free(lo, hi):   # ช่วงย่อยใน [lo, hi] ที่ไม่มีตัวอักษรเลย
    out, cur = [], lo
    for cs, ce in CHR:
        if ce <= cur or cs >= hi: continue
        if cs > cur: out.append((cur, cs))
        cur = max(cur, ce)
    if cur < hi: out.append((cur, hi))
    return out
n = 0
for a, b in zip(st, en):
    for s, e in K:
        for lo, hi in free(max(a, s), min(b, e)):
            if hi - lo > max(D, 2 * LEAVE + 0.04): C['cut_times'].append([round(lo + LEAVE, 2), round(hi - LEAVE, 2), f'เดดแอร์ {hi - lo:.2f} วิ ({TH} dB)']); n += 1
json.dump(C, open('work/cuts.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'เดดแอร์ {n} จุด → work/cuts.json · รัน rough.py build อีกรอบ')
