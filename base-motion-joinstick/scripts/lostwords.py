#!/usr/bin/env python3
"""ตรวจคำหาย: ตัวอักษร Scribe (ไฟล์ดิบ) ในวลีที่ "ตั้งใจเก็บ" แต่ไม่อยู่ใน keep.json — ไม่นับที่ตัดตั้งใจ (remove / cut_times ที่ไม่ใช่เดดแอร์)
ใช้ (จากโฟลเดอร์โปรเจกต์ หลัง rough.py build): python lostwords.py   → ต้องได้ "ไม่มีคำหาย" (C2680: เดดแอร์ตัด "จัด" ที่พูดเบา)"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
C = json.load(open('work/cuts.json', encoding='utf-8')); K = json.load(open('work/keep.json', encoding='utf-8'))
W = json.load(open('work/scribe.json', encoding='utf-8'))['words']
# วลีแบบเดียวกับ rough.py (แยกด้วย spacing)
P, cur = [], None
for w in W:
    if w['type'] == 'spacing':
        if cur: P.append(cur); cur = None
        continue
    if w['type'] == 'audio_event':   # rough.py นับเสียงไอ/หัวเราะเป็นวลีของตัวเอง → ลำดับ id ต้องตรงกัน
        if cur: P.append(cur); cur = None
        P.append([]); continue
    if cur is None: cur = []
    cur.append(w)
if cur: P.append(cur)
keep_ids = set(i for a, b in C['segments'] for i in range(a, b + 1)) - set(i for a, b, *_ in C.get('remove', []) for i in range(a, b + 1))
intent = [(a, b) for a, b, why in C.get('cut_times', []) if not why.startswith('เดดแอร์')]
lost = []
for i, ws in enumerate(P):
    if i not in keep_ids: continue
    for w in ws:
        m = w['start'] + min(0.03, (w['end'] - w['start']) / 2)   # จุดเริ่มเสียงของตัวอักษร (เวลาจบของ Scribe ลากยาวเข้าช่วงเงียบได้)
        if any(a <= m <= b for a, b in intent): continue
        if not any(s - 0.02 <= m <= e + 0.02 for s, e in K): lost.append((round(w['start'], 2), w['text'], i))
# รวมตัวอักษรติดกันเป็นคำ
out = []
for t, c, i in lost:
    if out and t - out[-1][2] < 0.3 and out[-1][3] == i: out[-1][1] += c; out[-1][2] = t
    else: out.append([t, c, t, i])
print('ไม่มีคำหาย' if not out else '\n'.join(f'⚠️ หาย {a:.2f}s #{i} "{c}"' for a, c, _, i in out if len(c.strip()) > 0))
