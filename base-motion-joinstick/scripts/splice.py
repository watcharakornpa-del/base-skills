#!/usr/bin/env python3
"""ใส่ฉากของคลิปใหม่ลง gfx/gen.py: แทนส่วน "1 · Text Hook" ถึงก่อน "5 · ซับ" ด้วยไฟล์ฉาก + ตั้ง TOTAL / FACE_CROP / FIX
ใช้: python splice.py <gfx dir> <scenes.py> <TOTAL> <FACE_CROP> '<FIX json เช่น [["ศาลตั้งต้น","ฐานตั้งต้น"]]>'
ไฟล์ฉากตัวอย่าง: references/examples/scenes-*.py (เริ่มด้วย "# ===== 1 · Text Hook" · มี hook/sup/broll ครบในไฟล์)
เขียนฉากแยกไฟล์แล้วค่อย splice = แก้ฉากได้โดยไม่แตะส่วนซับ/เสียง และเก็บไว้เป็นตัวอย่างคลิปถัดไป"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
G, scenes, total, crop = sys.argv[1:5]; fix = json.loads(sys.argv[5]) if len(sys.argv) > 5 else []
src = open(f'{G}/gen.py', encoding='utf-8').read()
head, rest = src.split('# ===== 1 · Text Hook', 1)
tail = '# ===== 5 · ซับ' + rest.split('# ===== 5 · ซับ', 1)[1]
head = re.sub(r'^TOTAL = .*$', f'TOTAL = {total}', head, flags=re.M)
head = re.sub(r"^FACE_CROP = '[^']*'", f"FACE_CROP = '{crop}'", head, flags=re.M)
if fix: tail = tail.replace('FIX = [', 'FIX = [' + ''.join(f'({a!r}, {b!r}), ' for a, b in fix), 1)
body = open(scenes, encoding='utf-8').read()
out = head + body.rstrip() + '\n\n' + tail
out = out.replace("print('hook 0–', r(TH), '· supers', NS[0], '· levels 4 · B-roll'", "print('hook 0–', r(TH), '· supers', NS[0], '· B-roll'")
open(f'{G}/gen.py', 'w', encoding='utf-8').write(out)
print('✅', G, '· TOTAL', total, '· FACE_CROP', crop, '· FIX +', len(fix))
