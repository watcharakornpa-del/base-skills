# BASE Playhouse — สกิลทีมกราฟิก (FRAME)

สกิล Claude Code ของทีมกราฟิก BASE · วางไว้ที่ `~/.claude/skills/`

| สกิล | ใช้ทำอะไร |
|---|---|
| `base-motion` | คลิปพูดแนวตั้ง → แผงกราฟิกบน + คนพูดล่าง + ซับ (+ โหมด overlay / Premiere) |
| `base-motion-collage` | ใส่ B-roll collage กระดาษตัด สี MP Ci · แก้ Draft1 → Draft2 ตามรีฟ |
| `base-motion-journal` | สไตล์ TikTok: ปก → คนพูด+ซับ → การ์ดวาดเส้น + หน้าในวงกลม |
| `base-motion-blueprint` | Hook เขียนสด + Super ลายมือพู่กัน + ฉากวาดบนกระดาษเขียนแบบ (บรีฟ MAYTWIN) |
| `base-motion-joinstick` | ไฟล์ดิบ → คลิป Micro Learning สำหรับแอป JOINSTICK (ภาษา UI ของแอป) |
| `base-rough-cut` | ไฟล์ดิบ → rough cut XML + ซับ SRT สำหรับ Premiere |
| `mp-sheet-caption` | แปะลิงก์ Drive คลิปที่ส่งแล้ว + แคปชั่น/แฮชแท็ก ลงชีตคอนเทนต์ (แท็บ mp_base) |

## ติดตั้งในเครื่องใหม่ / อัปเดต
**จาก GitHub** (เครื่องต้องล็อกอิน GitHub ที่ได้รับเชิญเข้า repo นี้แล้ว):
```bash
curl -fsSL -H "Authorization: token $(gh auth token)" https://raw.githubusercontent.com/watcharakornpa-del/base-skills/main/install.sh | bash
```
หรือถ้ามีไฟล์ `install.sh` อยู่แล้ว: `bash install.sh` · รันซ้ำ = อัปเดต (git pull)

**จาก SSD** (ไม่ต้องใช้ GitHub):
```bash
bash "/Volumes/Extreme SSD/AI/skills/install.sh" "/Volumes/Extreme SSD/AI/skills"
```
สกิลเดิมในเครื่องจะถูกย้ายไปสำรองที่ `~/Developer/skill-backups/` ไม่ลบทิ้ง · เสร็จแล้วเปิด Claude Code session ใหม่

## ไม่มีใน repo (ตั้งใจ)
- คีย์ ElevenLabs (`~/.elevenlabs/api_key`) — ขอพี่ Mac
- คลิปลูกค้า / ไฟล์เรนเดอร์
