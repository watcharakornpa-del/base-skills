#!/bin/bash
# ติดตั้ง/อัปเดตสกิลทีมกราฟิก BASE ลง ~/.claude/skills
#
#   จาก GitHub (เครื่องต้องล็อกอิน GitHub ที่มีสิทธิ์เข้า repo):
#     bash install.sh
#   จาก SSD (ไม่ต้องใช้ GitHub):
#     bash "/Volumes/Extreme SSD/AI/skills/install.sh" "/Volumes/Extreme SSD/AI/skills"
#
# สกิลเดิมในเครื่องไม่ถูกลบ — ย้ายไปเก็บที่ ~/Developer/skill-backups/ ก่อน
# (ห้ามเก็บสำรองไว้ใน ~/.claude/skills ชื่อสกิลจะชนกัน)
set -euo pipefail

REPO=https://github.com/watcharakornpa-del/base-skills.git
DEST="$HOME/.claude/skills"
SRC="${1:-}"
STAMP=$(date +%Y%m%d-%H%M%S)
BACKUP="$HOME/Developer/skill-backups/skills-$STAMP"

backup_old() {
  [ -d "$DEST" ] || return 0
  mkdir -p "$(dirname "$BACKUP")"
  mv "$DEST" "$BACKUP"
  echo "📦 สำรองสกิลเดิมไว้ที่ $BACKUP"
}

if [ -z "$SRC" ]; then
  # --- จาก GitHub ---
  if [ -d "$DEST/.git" ] && git -C "$DEST" remote get-url origin 2>/dev/null | grep -q base-skills; then
    echo "🔄 มี repo อยู่แล้ว → git pull"
    git -C "$DEST" pull --ff-only
  else
    backup_old
    mkdir -p "$(dirname "$DEST")"
    if ! git clone "$REPO" "$DEST"; then
      echo
      echo "❌ clone ไม่ได้ — เครื่องนี้ยังไม่ได้ล็อกอิน GitHub หรือบัญชีนี้ยังไม่ได้รับเชิญเข้า repo"
      echo "   ทางเลือก: ติดตั้งจาก SSD แทน (ดูบรรทัดบนสุดของไฟล์นี้)"
      [ -d "$BACKUP" ] && mv "$BACKUP" "$DEST" && echo "   คืนสกิลเดิมกลับที่ $DEST แล้ว"
      exit 1
    fi
  fi
else
  # --- จากโฟลเดอร์ (SSD) ---
  [ -f "$SRC/README.md" ] || { echo "❌ ไม่เจอสกิลใน $SRC"; exit 1; }
  backup_old
  mkdir -p "$DEST"
  rsync -a --exclude '._*' --exclude '.DS_Store' --exclude '__pycache__' --exclude '*.zip' "$SRC/" "$DEST/"
  echo "⚠️  ติดตั้งจากโฟลเดอร์ → ไม่ได้ผูก GitHub · อัปเดตครั้งหน้าให้รันจาก SSD ใหม่อีกรอบ"
fi

chmod +x "$DEST"/*/scripts/*.sh 2>/dev/null || true

echo
echo "✅ สกิลในเครื่อง:"
for d in "$DEST"/*/; do [ -f "$d/SKILL.md" ] && echo "   - $(basename "$d")"; done

echo
echo "🔧 เครื่องมือที่สกิลต้องใช้:"
chk() { if command -v "$1" >/dev/null 2>&1; then echo "   ✅ $1"; else echo "   ❌ $1 — $2"; fi; }
chk ffmpeg  "ต้องมี (ตัด/เรนเดอร์วิดีโอ)"
chk ffprobe "มากับ ffmpeg"
chk node    "ต้องมี v20+ (HyperFrames เรนเดอร์กราฟิก/ซับ)"
chk npx     "มากับ node"
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
  echo "   ✅ python3 ($(python3 -V 2>&1 | cut -d' ' -f2))"
else
  echo "   ❌ python3 3.10+ — python3 ของระบบ Mac เป็น 3.9 ใช้ไม่ได้ (ลงผ่าน uv แล้วใช้ .venv)"
fi
if [ -f "$HOME/.elevenlabs/api_key" ]; then echo "   ✅ คีย์ ElevenLabs"; else echo "   ❌ คีย์ ElevenLabs (~/.elevenlabs/api_key) — ขอพี่ Mac"; fi

echo
echo "เสร็จแล้ว → ปิด Claude Code แล้วเปิด session ใหม่ ถึงจะเห็นสกิล"
