# แก้คลิปตามรีฟ (Draft1 → Draft2) — ขั้นตอนเต็ม

ใช้เมื่อทีมส่งรีฟ (PDF/ข้อความ) ติคลิป Draft1 ที่ทำด้วยสกิลนี้ไปแล้ว ทดสอบจริง 9 พ.ย. 2026 กับชุด `tiktok 271069` (C5395) คลิป 1–2
สคริปต์ทั้งหมดอยู่ใน `revise/` · ผลงานตัวอย่าง: `~/Developer/video-use/tt271069-b1-draft2/` (คลิป 1 เขียนมือ) · `tt271069-b2/` (คลิป 2 ใช้ชุดนี้)

## ของที่ต้องมี (ทั้งหมดอยู่ในโฟลเดอร์โปรเจกต์ทีม)
| ไฟล์ | ใช้ทำอะไร |
|---|---|
| `Export/<ชื่อ> Draft1.mp4` | เวลาในรีฟอิงไฟล์นี้ · ถอดเสียงไฟล์นี้ |
| `C5395-collage/<คลิป>-collage.mp4` | ภาพ B-roll เดิม (ไม่มีปก/ซับ) ยาวเท่า Draft1 |
| `C5395-premiere/clipN-roughcut.xml` | จุดตัด → ไฟล์กล้อง 4K ต้นฉบับ (ภาพคนพูดเอาจาก 4K ไม่ใช่จาก collage) |
| `C5395-premiere/<คลิป>-premiere.srt` | ซับทีม (คำสะกดที่ทีมแก้แล้ว) ใช้ตั้งต้น |
| ฟอนต์ใน `~/Library/Fonts` | IBM Plex Sans Thai SemiBold · Anuphan SemiBold · UID Deep sea (ขอทีม) |
| `/Volumes/Extreme SSD/Copied_Tiktok 180526/` | `Gradient Blue copy.png` · `pen writing.wav` · `typewriter.wav` ของ template ทีม |

⚠️ เลขคลิปในชื่อไฟล์ (`c5395-clip1`) **ไม่ตรง**กับเลขในรีฟ → จับคู่จากเนื้อหาซับ + ความยาว Draft1 = collage ทุกครั้ง

## ขั้นตอน
1. อ่านรีฟ (PDF: `swift` + PDFKit ดึงข้อความ ถ้าไม่มี pdftoppm) · จดทีละคลิป: Topic ใหม่ · ตัด/สลับเนื้อหา (timestamp) · Super · แก้ซับ
2. `python3 -I revise/setup.py <ชื่อ> "<Draft1>" "<collage>" "<xml>" "<srt>" "<ไฟล์ส่ง Draft2>"`
   → `~/Developer/video-use/<ชื่อ>/` · ถอดเสียง Draft1 (ElevenLabs) · หาช่วง B-roll เอง (ขอบซ้ายเป็นกระดาษสว่าง) · หาไฟล์ 4K จากชื่อใน XML
   รันหลายคลิปพร้อมกันได้ (`&` แล้ว `wait`)
3. ดู transcript พร้อมเวลา แล้วเขียน `work/plan.py` (ตัวอย่างใน `plan_template.py`): `COVER` · `KEEP` (วลีเริ่ม/จบ ตามเสียงจริง) · `SUPERS` · `FIX` · `REWRITE` · `PATCHES`
4. `python3 -I work/edl.py` → ดูรายงาน: ชิ้นตัด · ความยาว · ซับทุกบรรทัด + ⚠️ ยาวเกินจอ / คำอังกฤษโดนแยกบรรทัด → แก้ plan จนไม่มี ⚠️
   ซับทีมมักฉีกคำ ("คนกลุ่ม / นี้", "ถูก / ไหม", "Fast / Learning") → แก้ด้วย `REWRITE`
5. `python3 -I work/gen_gfx.py && bash work/render_gfx.sh` (ปก + Super เป็น MOV พื้นใส) → `python3 -I work/compose.py` (~1.5 นาที)
6. `python3 -I work/check.py` → **เปิดดูทุกรูป**: `sheet.jpg` (ทุกวินาที) + `caps_*.png` (ซูมซับทุกบรรทัด ดูวรรณยุกต์ทีละคำ) + ซูมปก
7. `python3 -I work/deliver.py` — ก๊อป mp4 + srt ไปที่ไฟล์ส่ง (`clip.json: out`) ห้ามทับ Draft1
8. **Premiere:** `python3 -I work/premiere_xml.py` → `<โปรเจกต์>/C5395-draft2/<ชื่อ>/` (XML + SRT + MOV พื้นใส + LUT) แล้ว `python3 -I work/verify_xml.py` ต้อง "ตรงทุกเฟรม"
   นำเข้าอัตโนมัติ: เปิดโปรเจกต์ใน Premiere + แผง AI Story Cutter → `python3 -I revise/premiere_import.py "<โฟลเดอร์ C5395-draft2>"` (action `importxml` = นำเข้า + ซับเป็น Captions + เซฟ)
   **ก่อนนำเข้า ยืนยันกับผู้ใช้ว่าโปรเจกต์ที่เปิดอยู่ถูกตัว** (Premiere อาจเปิดโปรเจกต์ล่าสุดค้างไว้แทน) · สำรอง .prproj ก่อนเสมอ
   แก้โค้ดแผงแล้วต้องให้ผู้ใช้ปิด-เปิดแผงใหม่ (สั่ง quit Premiere ผ่าน AppleScript บนเครื่องนี้ไม่ทำงาน) · เกรด/style ซับ ยังต้องทำใน Premiere

## กฎ (ผู้ใช้สั่ง/อนุมัติแล้ว 9 พ.ย. 2026)
- **ตัด "คำถามคือ…" ทุกคลิป** · hook ของคนถามตัด/เก็บตามรีฟรายคลิป
- **ซับ**: IBM Plex Sans Thai SemiBold ขนาดคงที่ทั้งคลิป (ass Fontsize 100 = ตัวเท่างานทีมชุด 031026) บรรทัดเดียว **ไม่ย่อ** (Draft1 โดนติว่าซับยืดหด)
  · **เงาฟุ้ง (Drop Shadow) ไม่มีขอบ** (ขอบทำให้ตัวจม) · ตัด อ่ะ / น่ะ ออกจากซับ (เสียงคงไว้)
  · คำอังกฤษหลายคำ (Fast Learning, Critical Thinking Skill) ห้ามแยกบรรทัด · ไม่มีซับใต้ปก / B-roll / Super
- **ฟอนต์ไทยในซับ**: ffmpeg ต้องใช้ฟิลเตอร์ `ass=...:shaping=complex` — ฟิลเตอร์ `subtitles` วางวรรณยุกต์จมในสระบน ("ที่" กลายเป็น "ที") · ผู้ใช้จับได้ → **ต้องซูมเช็คทุกบรรทัดทุกครั้ง**
- **ปก (Topic) = template ทีม Tiktok 180526**: ม่านกรมท่า `Gradient Blue copy.png` + บรรทัด 1 ขาว Anuphan + บรรทัด 2 ส้ม `#FF4F1F` UID Deep sea เขียนออกมา + เส้นใต้ (ครอปจาก `cover font.png`) อยู่ใต้สระล่าง · ปกยาวเท่าชิ้น hook (≤ 3.5 วิ) + เสียงปากกา
- **Super = template ทีม (แบบงานมอเกษตร)**: ม่านกรมท่า + คำขาวกลางจอ พิมพ์ออกมา + typewriter · ขึ้นตรงคำ ~2.5–3 วิ · ซับหายระหว่าง Super
- **เกรดโทนเข้ม**: `assets/BASE-dark-moody.cube` (ลดแสงกลาง กดท้องฟ้า ลดอิ่ม 15%) เฉพาะภาพกล้อง ไม่เกรด B-roll · ใช้ไฟล์เดียวกันใน Lumetri › Creative › Look ได้
- **สะกด**: Judgement (มี e) ทั้งซับ Super และการ์ด
- **แก้ป้ายในการ์ด B-roll โดยไม่มี gen.py เดิม**: `PATCHES` ทำป้ายใหม่ด้วย CSS เดียวกับสกิล (strip + edge + Noto) แปะทับ · วัด cx, cy, มุมเอียงจากเฟรมที่ป้ายนิ่ง · `at` = เฟรมแรกที่ป้ายเดิมโผล่ · แปะทึบตั้งแต่เฟรมแรก (ไม่งั้นป้ายเดิมโผล่จาง ๆ 1–2 เฟรม) · ดูทีละเฟรมช่วงป้ายเข้า
- **เสียง**: loudnorm 2 รอบ (-15 LUFS, พีค ≤ -2 dBTP หลังเข้ารหัสได้ราว -1.8) · ห้าม loudnorm รอบเดียว (ได้แค่ ~-19)
- ห้ามใส่คอมเมนต์ `#` ไว้ใน string ของ `-filter_complex` (ffmpeg error)
- **ตัดชิ้นจากไฟล์ 29.97fps ต้องได้จำนวนเฟรมพอดี** (`trim=end_frame=N` + `setpts=PTS-STARTPTS` + `atrim`) และเริ่มที่ครึ่งเฟรมก่อน (`(เฟรม-0.5)/fps`) — เคยใช้ `-t` แล้วภาพหายทีละเฟรม ภาพนำเสียงสะสม 5 เฟรม (จับได้ตอนเทียบ XML) · ตรวจด้วยเลขเฟรม (`select=eq(n,…)`) อย่าใช้ `-ss` กับไฟล์ที่ต่อด้วย concat
- `python3` ของ Mac ไม่มี Pillow → `edl.py` สลับไป `~/Desktop/BASE/.venv` เอง (ไม่งั้นไม่เตือนซับยาวเกินจอ)

## ยังไม่ได้ทำ (ค้าง)
- ตั้ง style ซับ / ใส่ LUT ใน Premiere ให้อัตโนมัติ (ยังทำมือ)
- กล้องหมุนแนวตั้ง: Scale 50 บน Mac · Draft1 (Windows) ใช้ 88.89 → ถ้าเปิดบน Windows ต้องเช็คใหม่
- ตรวจซับตรงเสียงด้วยการถอดเสียง MP4 ซ้ำ (ตอนนี้วางเวลาจากเสียงจริงทีละคำ แต่ยังไม่ได้ถอดซ้ำ)
