---
name: base-motion-joinstick
description: >
  base-motion-joinstick — ไฟล์ดิบคลิปพูดสอน → คลิป Micro Learning สำหรับแอป JOINSTICK จบในตัว (MP4 1080×1920 พร้อมโพสต์):
  rough cut (ตัดเงียบ/คำเกิน/เทคเสีย) → กราฟิกในภาษา UI ของแอป JOINSTICK (พื้นดำ การ์ด #131313 แดงไฟ #EA3A1F ทอง Stage ·
  Poppins + IBM Plex Sans Thai): Text Hook · ชิปคำสำคัญเหนือหัว · การ์ด LEVEL ล่างจอ · B-roll จอแบบแอป (เส้นทาง Shift Stage
  แชทภารกิจ เกจ Hype การ์ดเทียบ) + หน้าคนพูดในวงกลมขอบแดง · ซับ Plex Thai · SFX. ใช้เมื่อผู้ใช้พูดว่า "/base-motion-joinstick"
  หรือขอคลิป Micro Learning ลงแอป JOINSTICK จากไฟล์ดิบ · ไม่ใช้กับคลิปที่ตัดเสร็จใน Premiere แล้ว (ใช้ base-motion-collage)
  หรือแผงบน+คนพูดล่าง (ใช้ base-motion) · ไม่ใช้ภาพหน้าจอแอปจริงใส่คลิป
---

# base-motion-joinstick — ไฟล์ดิบ → คลิป Micro Learning ในหน้าตาแอป JOINSTICK

> สถานะ 11 พ.ย. 2026: **v1** · ต้นแบบ = คลิป C2673 "Extrinsic Motivation 4 ระดับ" (ไฟล์ดิบ 3:37 → 3:20 · ผู้ใช้อนุมัติแล้ว)
> โค้ดเต็มของต้นแบบ = `template/gen.py` · ชิ้นส่วน/สี/ตำแหน่ง = `references/ui-kit.md` · หน้าตาที่ผ่าน = `references/example-c2673.jpg`
> รวมสามสกิล: base-rough-cut (ตัด) + base-motion-collage v3 (โครง Hook/Super/B-roll) + base-motion (ฟอนต์/SFX)

## ⛔ ถามก่อนเริ่ม
1. **ไฟล์ดิบไหน** · มีหลายเรื่อง/หลายเทคในไฟล์ไหม · ควรจบตรงไหน
2. มีสคริปต์/ชื่อเฉพาะที่ต้องสะกดให้ถูกไหม (ชื่อทฤษฎี ชื่อคน)
3. หน้าตาแอปเปลี่ยนไหม — ถ้ามีภาพหน้าจอชุดใหม่ ให้ดูก่อนแล้วเทียบกับ `ui-kit.md` (ชุดที่ใช้: `JOINSTICK-Screens-2026-11-10`)

## ขั้นตอน (Python = `~/Desktop/BASE/.venv/bin/python` · ffmpeg ต้องอยู่ใน PATH)
```bash
export PATH=~/Desktop/BASE/PrProjCut/.tools/ffmpeg-env/bin:$HOME/.local/bin:$PATH; PY=~/Desktop/BASE/.venv/bin/python
K=~/.claude/skills/base-motion-joinstick
```
1. **ตั้งโปรเจกต์ + ถอดเสียงไฟล์ดิบ** → `$PY $K/scripts/new_joinstick.py <ชื่อ> "<ไฟล์ดิบ>"` (ได้ `work/phrases.txt`)
2. **Rough cut** — อ่าน `work/phrases.txt` ทั้งไฟล์ เขียน `work/cuts.json` (รูปแบบ + กฎเลือกเทค ดู base-rough-cut)
   แล้ว**ส่งรายการที่ตัดให้ผู้ใช้ดู** → `cd <โปรเจกต์> && $PY work/rough.py build && $PY work/rough.py full`
   (4K HLG ~200 วิ ใช้เวลารวม ~15 นาที · รันเบื้องหลัง) · ได้ `renders/cut_1080.mp4` + `renders/roughcut.srt`
3. **ตั้งโปรเจกต์กราฟิก** → `$PY $K/scripts/setup_gfx.py <โปรเจกต์>` (ได้ `gfx/` + ถอดเสียงคลิปที่ตัดแล้ว + พิมพ์ค่า TOTAL)
4. **ดูคลิป** — contact sheet ทุก 8 วิ: หัวคนพูดอยู่ y ไหน (ต้นแบบ 400–850) → ตั้ง `FACE_CROP` (ตัดกว้าง หัวกิน ~ครึ่งวง)
5. **วางฉาก** จาก `gfx/work/transcript.txt` แล้ว**บอกผู้ใช้เป็นตารางก่อนลงมือ** (เวลา · ชนิด · ข้อความ):
   | ชนิด | ใช้เมื่อ | ต้นแบบ |
   |---|---|---|
   | Hook 3–5 วิแรก | ทุกคลิป · คำจากประโยคเปิด | MICRO LEARNING → ทุกคนน่าจะรู้จัก → **Motivation** → แรงจูงใจ |
   | Super ชิปบนหัว | ชื่อแนวคิด/คำถาม/ชื่อทฤษฎี ~1 ครั้งต่อ 15–20 วิ | Intrinsic/Extrinsic · Ryan & Deci 2000 · WHY ? |
   | การ์ดระดับล่างจอ | ช่วงอธิบายยาวทีละหัวข้อ (ค้างทั้งช่วง ซับยังขึ้น) | LEVEL 1–4 External → Integrated |
   | B-roll จอแบบแอป | ลำดับขั้น · ตัวอย่างบทพูด · เทียบ · ตัวเลขพลัง (3–4 ครั้งต่อคลิป) | Shift Stage · แชทภารกิจ · เกจ Hype · การ์ดคู่ |
   เลือกชิ้นส่วนตามตาราง "จับคู่เนื้อหา" ใน `ui-kit.md` · หาเวลาด้วย `at('วลี')` / `at('วลี', after=วินาที)` (คำซ้ำต้องใส่ after)
6. **แก้ `gfx/gen.py`** — "ตั้งค่าต่อคลิป" (TOTAL · FACE_CROP) + เขียน hook/sup/LV/broll ของคลิปใหม่แทนของ C2673 ·
   ซับที่ถอดผิด/คำเกินใส่ใน `FIX` (เช่น "เอ่อ" "Intrin-Intrinsic") · ป้ายที่ตั้งคำเอง**บอกผู้ใช้**ว่าไม่ใช่คำพูดตรง ๆ
7. **ตรวจ** `cd gfx && $PY gen.py && npx --yes hyperframes@0.8.147 lint` → 0 error
8. **ภาพนิ่ง** `npx --yes hyperframes@0.8.147 snapshot --at <เวลาทุกฉาก> --no-end --describe false` → ดู contact sheet
9. **เรนเดอร์** (~15–25 นาทีต่อ 200 วิ · รันเบื้องหลัง · ห้ามถอด `--workers 1`):
   `npx --yes hyperframes@0.8.147 render -q draft --workers 1 -o renders/<ชื่อ>-draft.mp4 > work/render_log.txt 2>&1`
   แล้ว `grep effectiveHdr work/render_log.txt` ต้องเป็น `"sdr"` (ถ้า `hlg` = กราฟิกหายทั้งคลิป → แก้แท็กสี talk.mp4)
10. **ตรวจไฟล์จริงก่อนบอกเสร็จ** — ffprobe (ความยาว · 1080×1920 · มีเสียง) · ดึงเฟรมจาก **MP4** ทุกฉาก + ซูมฟอนต์ไทย ·
    ก๊อปไป `~/Downloads/` · เขียน `NOTES.md` ในโปรเจกต์ (ตารางฉาก · ป้ายที่ตั้งเอง · ไฟล์ส่ง · กับดักที่เจอ)

## หน้าตา (ผู้ใช้อนุมัติแล้ว — เปลี่ยนต้องถามก่อน)
- **วาดใหม่ในภาษา UI แอปเท่านั้น ห้ามใส่ภาพหน้าจอ/อัดจอจริง** — เนื้อหาเชิงทฤษฎีอาจทำให้ฟีเจอร์แอปดูแย่
  (C2673: "รางวัล = แรงจูงใจระดับต่ำสุด" ถ้าใส่จอ Reward/Ranking จริงจะเหมือนแอปใช้แรงจูงใจต่ำ)
- พื้นดำ การ์ด #131313 ขอบขาวจาง มุมมน 30–40 · แดง #EA3A1F · ทอง #F5C542 เฉพาะเรื่อง Stage/ระดับ
- ห้าม: glow · ไล่สี · อนุภาค · น้ำเงิน/ม่วง · อีโมจิ (ไฟใช้ `flame()` SVG) · เพลง (ใส่เฉพาะ SFX: click pop · swoosh เข้า B-roll · thump คำเด่น · pen เส้นไต่)
- ซับ: IBM Plex Sans Thai 600 60px ขาว เงาฟุ้ง ไม่มีขอบ y 1256 · **ไม่ขึ้นช่วง Hook / Super / B-roll** · ไม้ยมก ๆ เว้นวรรคหน้า-หลัง
- B-roll ทุกช่วงมีหน้าคนพูดในวงกลม 400px ขอบแดง 8px ที่ y 1390

## กับดักที่เจอจริง (C2673)
- **ffmpeg บน Mac ไม่มี `zscale`/`libplacebo`** → rough.py ในสกิลนี้แปลง HLG→Rec.709 ด้วย LUT `assets/hlg2sdr.cube`
  (สร้างจาก `hlg2sdr_lut.py` · ขาวอ้างอิง 203 nits = 100% + knee ไฮไลต์ · แบบ hable ของ zscale มืดเกินเมื่อเทียบกัน)
- **แท็กสี HLG ติดค้าง** แม้ใส่ `-color_trc bt709` (ffmpeg 8 ใช้ค่าจากเฟรม) → HyperFrames สลับโหมด HDR แล้ว**ทิ้งชั้นกราฟิกทั้งหมด**
  ได้คลิปที่มีแต่วิดีโอ · แก้แล้ว: `setparams=...bt709` ใน rough.py + setup_gfx.py เข้ารหัส talk.mp4 ใหม่และเช็คแท็ก
- **keyframe ห่าง** (8 วิ) → HyperFrames เตือน seek พลาด · setup_gfx.py ใช้ `-g 30` · gen.py ตัด cam ด้วย `-g 30`
- **id ซ้ำกับของระบบ** (เกจ `g1` = ช่วง B-roll `g1`) → ชิ้นหายเงียบ ๆ · ดูรายการ id ต้องห้ามใน `ui-kit.md`
- rough.py ถอดซับ "แล้" | "วจะ..." ข้ามบรรทัด → gen.py ซ่อมให้ · ถ้าเจอแบบอื่นแก้ใน `FIX`
- `snapshot` ต้อง `--describe false` เสมอ (ไม่งั้นส่งเฟรมงานลูกค้าไป Gemini)
- ห้ามใช้ `rm` กับตัวแปรเปล่า ๆ (`rm -f $S/*`) — ระบบบล็อก · ใช้โฟลเดอร์ใหม่หรือ `"${S:?}"/*`

## ตัวอย่างผลลัพธ์ที่ดี — C2673 (200.8 วิ)
| เวลา | ชนิด | เนื้อหา |
|---|---|---|
| 0–5.1 | Hook | MICRO LEARNING · ทุกคนน่าจะรู้จัก · **Motivation** · แรงจูงใจ |
| 14 / 30 / 42 | Super | Intrinsic·Extrinsic · ถ้ามีแค่ Extrinsic ล่ะ ? · Ryan & Deci 2000 |
| 45–54 | B-roll | Shift Stage 4 ระดับ เด้งตาม "หนึ่ง สอง สาม สี่" + เส้นแดงไต่ + "ยิ่งสูง ยิ่งทรงพลัง" |
| 64–136 | การ์ดล่างจอ | LEVEL 1 External → 2 Introjected → 3 Identified → 4 Integrated (+ WHY ? · Perfectionist) |
| 140–180 | B-roll | แชท "คุยกับน้องในทีม" 4 ข้อความ ระดับ 1→4 |
| 180–184 | B-roll | เกจ Hype 0→100 · STRONG ที่สุด |
| 185–193 / 194–จบ | Super / B-roll | TAKEAWAY แตะให้ถึงระดับ 4 · การ์ดเทียบ Level 1 vs Level 4 |
โปรเจกต์เต็ม: `~/Developer/video-use/joinstick-c2673/` (NOTES.md · gfx/gen.py)

## ข้อจำกัดที่รู้แล้ว
1. ต้องรันโค้ดได้ (Claude Code บนเครื่องที่มี .venv + ffmpeg + node) · ทำผ่านแชทอย่างเดียวไม่ได้
2. ยังไม่ส่งเข้า Premiere — ได้ MP4 จบ · ถ้าต้องการแก้ใน Pr ใช้ `renders/roughcut.xml` + `.srt` จากขั้น 2 แล้ววางกราฟิกเอง
3. ตำแหน่ง Super/การ์ดตั้งตามมุมกล้องโต๊ะ C2673 · มุมอื่นต้องขยับ y เอง
4. ตัดคำซ้ำได้ระดับวลีของ Scribe ("Intrin-Intrinsic" ตัดไม่ได้ · "เอ่อ" กลางวลีเหลือในเสียง แต่ลบจากซับได้)
5. เสียงรวมออกมา ~−16 LUFS (เบากว่าเป้า −14 นิดหน่อย)

## เจ้าของอยากได้ความเห็นเรื่อง
1. ชิ้นส่วนแอปที่เลือกเข้ากับเนื้อหาไหม · มีหน้าจอแอปอื่นที่ควรทำเป็นชิ้นส่วนเพิ่ม (Flash Card · Manager Review · Streak)
2. จำนวน B-roll / ความยาวช่วงแชท (40 วิ) มากไปไหม
3. การ์ดระดับล่างจอค้างนานทับโต๊ะ — อ่านง่ายหรือรก
