#!/usr/bin/env python3
"""หาคำ/ประโยคซ้ำใน scribe.json (ถอดเสียงไฟล์ที่ตัดแล้ว) — ใช้ก่อนส่งทุกครั้ง
ใช้: python repeats.py <scribe.json>
- ADJ  = ซ้ำติดกัน (ถาม ถาม · เปิด เปิดเว็บ) → ต้องตัด เก็บครั้งหลัง (ยกเว้นภาษาปกติ เช่น "แต่ แต่ละ" · "พยายาม")
- NEAR = ข้อความ ≥ 7 ตัวซ้ำภายใน 80 ตัวอักษร → อ่านทีละจุด: พูดสะดุด / พูดทวน / แก้คำ = ตัด · ลิสต์ / ตัวอย่าง / สรุป = เก็บ
Scribe มักรวมคำซ้ำเป็นคำเดียว ("ถาม ถามคำถาม" → "ถามคำถาม") → ADJ ว่างไม่ได้แปลว่าไม่มีซ้ำ ต้องถอดเสียงไฟล์ตัดแล้วซ้ำ + ฟังจุดที่ตัดคำ"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
W = [w for w in json.load(open(sys.argv[1], encoding='utf-8'))['words'] if w['type'] == 'word']
CH = [(c, w['start']) for w in W for c in w['text'].lower() if c.strip()]
S = ''.join(c for c, _ in CH)
print('ADJ :', [(round(CH[m.start()][1], 1), S[max(0, m.start() - 10):m.end() + 10]) for m in re.finditer(r'(.{2,12})\1', S)])
seen = []
for L in (12, 7):
    for i in range(len(S) - L):
        j = S.find(S[i:i + L], i + L, i + L + 80)
        if j > 0 and not any(abs(i - a) < 20 for a in seen):
            seen.append(i); print(f'NEAR {CH[i][1]:7.2f}s  [{S[i:i + L]}]  … {S[max(0, i - 8):j + L + 8]}')
