#!/usr/bin/env python3
"""NOTES.md คลิป AI Productivity 4–12 · ใช้: mknotes.py <โปรเจกต์> <คลิปที่> <ไฟล์ส่ง ไม่มี .mp4> <ชื่อปก> <insert> <OFF>"""
import json, re, sys, os, glob, subprocess
P, N, OUT, TITLE, INS, OFF = sys.argv[1:7]
cuts = json.load(open(f'{P}/work/cuts.json', encoding='utf-8'))
src = json.load(open(f'{P}/work/source.json', encoding='utf-8')) if os.path.exists(f'{P}/work/source.json') else {}
mp4 = f'{P}/renders/{OUT}.mp4'
dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout.strip()
sc = open(f'{P}/work/scenes_clip.py', encoding='utf-8').read()
hide = json.load(open(f'{P}/gfx/work/hide.json'))
ck = open(f'{P}/work/check_final.txt', encoding='utf-8').read() if os.path.exists(f'{P}/work/check_final.txt') else '(ยังไม่มี)'
labels = re.findall(r"(?:chip|pill|hd|screenroll|screenstages)\([^)]*?'([^']{2,60})'", sc)
name = os.path.basename(P)
md = f"""# {name} — AI Productivity (Skill Booster) คลิป {N}

**ทำเมื่อ:** 18 พ.ย. 2026 · **สถานะ:** Draft 1 รอผู้ใช้ดู · สกิล base-motion-joinstick v3 (กฎห้ามพลาด 13 ข้อ)
**ปก (ชื่อคลิปจากชีต):** {TITLE}
**ต้นทาง:** {src.get('source', 'CLIP/' + name.split('-')[-1].upper() + '.MP4')} + Screen record `Insert footage AI-Lot.1/{INS}` · insert = เวลากล้อง − ({OFF}) วิ (cross-correlation)
**ไฟล์ส่ง:** `renders/{OUT}.mp4` ({float(dur):.1f} วิ) · พรีวิว `renders/{OUT}_preview.mp4` · ซับ `renders/{OUT}_subs.srt`

## ตัด (work/cuts.json)
- เทคสุดท้ายเสมอ · segments {cuts['segments']}
- cut_times {len(cuts.get('cut_times', []))} จุด (คำเกิน/เศษคำหลุด/เดดแอร์) · หมายเหตุ: {' · '.join(cuts.get('notes', [])) if isinstance(cuts.get('notes'), list) else cuts.get('notes', '')}

## ฉาก (work/scenes_clip.py = ฉากของคลิปนี้ · ส่วนกลาง ~/.claude/skills/base-motion-joinstick/template/scene_common.py)
- ช่วงที่มีกราฟิก (ไม่มีซับ): {len(hide)} ช่วง · {', '.join(f'{a:.0f}–{b:.0f}' for a, b in sorted(hide))}
- ป้าย/หัวที่ใช้: {' · '.join(dict.fromkeys(re.sub('<[^>]+>', '', l) for l in labels))}
- **ไม่ใช่คำพูดตรง:** หัว B-roll · ป้าย FIX/NO./MYTH/RECAP/TRY IT · ชิปบนจอ (สรุปจากคำพูด + ชีตสคริปต์)

## ซับ
- captions.txt ร่างด้วย scripts/autocaps.py แล้วแก้บรรทัดที่ขึ้นจริงด้วย capfix.py · align.py --fuzzy ผ่าน · ≤30 ตัว · ไม่ขึ้น เนาะ/เนอะ/นะ/ป่ะ/อ่ะ

## ตรวจ (check_final)
```
{ck.strip()}
```
- ดึงเฟรมจาก MP4 จริงทุกฉากแล้ว

## สร้างใหม่
`$K/buildclip.sh {P}` → `$K/renderclip.sh {P} {OUT}` (K = ~/.claude/skills/base-motion-joinstick/scripts)
"""
open(f'{P}/NOTES.md', 'w', encoding='utf-8').write(md); print('✅', P, 'NOTES.md')
