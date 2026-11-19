# ติดตั้งสกิล base-motion-joinstick (ส่งต่อในทีม BASE)

ทำคลิป Micro Learning ลงแอป JOINSTICK จากไฟล์ดิบ: ตัดคำ/เดดแอร์ → กราฟิก UI แอป → ซับไทย → MP4 พร้อมส่ง

## 1 · วางไฟล์
แตก zip แล้ววางโฟลเดอร์ `base-motion-joinstick` ไว้ที่
```
~/.claude/skills/base-motion-joinstick/
```
(ในโฟลเดอร์ต้องเห็น `SKILL.md` ทันที ไม่ซ้อนโฟลเดอร์สองชั้น)

## 2 · ติดตั้งเครื่องมือ (ครั้งเดียว)
```bash
zsh ~/.claude/skills/base-motion-joinstick/scripts/setup.sh
```
ตรวจ ffmpeg · Node · curl · สร้าง Python venv (`numpy` `pythainlp`) · เช็คคีย์ ElevenLabs
- ไม่มี ffmpeg/Node → `brew install ffmpeg node` (ไม่มี Homebrew แจ้งพี่ Mac)
- **คีย์ ElevenLabs** (ใช้ถอดเสียง) ขอจากพี่ Mac → ใส่ไฟล์ `~/.elevenlabs/api_key` · **ห้ามส่งคีย์ในแชท/ห้ามใส่ในโฟลเดอร์งาน**

## 3 · ใช้งาน
เปิด Claude Code แล้วพิมพ์ `/base-motion-joinstick` + บอกไฟล์ดิบ / สคริปต์
- โปรเจกต์จะอยู่ที่ `~/Developer/video-use/<ชื่อ>/` · ไฟล์ส่งอยู่ใน `renders/`
- หลายคลิป + screen record → ดูหัวข้อ "⚡ โหมดหลายคลิป" ใน SKILL.md

## ข้อควรรู้
- หน้าตา/CI (ดำ · แดง #EA3A1F · ขาว · Poppins + IBM Plex Sans Thai) ผู้ใช้/พี่ Mac อนุมัติแล้ว — จะเปลี่ยนต้องถามก่อน
- ตรวจ CI อัตโนมัติด้วย `scripts/cicheck.py` (อยู่ใน buildclip/renderclip/check_final แล้ว) + ซูมดูปกทุกครั้ง
- `references/` มีภาพตัวอย่างจากงาน JOINSTICK — ใช้ภายในทีมเท่านั้น ห้ามโพสต์ออกนอก
- เวอร์ชัน: v4 (19 พ.ย. 2026) · ผู้ดูแล: พี่ Mac
