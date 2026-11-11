#!/bin/zsh
# base-motion-journal — ตั้งโปรเจกต์สไตล์ TikTok (ปก → คนพูดเต็มจอ+ซับ → B-roll การ์ดวาดเส้น + หน้าในวงกลม)
# ใช้: new_journal.sh <ชื่อโปรเจกต์> <คลิปที่ตัดแล้ว.mp4> [ซับของทีม.srt]
# ถอดเสียงด้วยสคริปต์ของ base-motion (ต้องติดตั้ง base-motion ไว้ก่อน) แล้ววางโครงของสไตล์นี้ทับ
set -e
NAME="$1"; SRC="$2"; SRT="$3"
[[ -z "$NAME" || ! -f "$SRC" ]] && { echo "ใช้: new_journal.sh <ชื่อ> <คลิป.mp4> [ซับ.srt]"; exit 1; }
K="${0:A:h:h}"; BM="$HOME/.claude/skills/base-motion"
[[ -x "$BM/scripts/new_project.sh" ]] || { echo "❌ ต้องติดตั้งสกิล base-motion ก่อน (ใช้สคริปต์ถอดเสียงของมัน)"; exit 1; }
"$BM/scripts/new_project.sh" "$NAME" "$SRC"
P="${BASE_MOTION_HOME:-$HOME/Developer/video-use}/$NAME"
cp "$K/template/gen.py" "$K/template/style.css" "$P/"
cp "$K/template/fonts/"*.ttf "$P/fonts/"
cp "$K/template/assets/"*.png "$P/assets/"
cp "$K/template/work/srt_align.py" "$P/work/"
[[ -n "$SRT" && -f "$SRT" ]] && cp "$SRT" "$P/work/team.srt"
echo "✅ วางโครง journal แล้ว · gen.py ยังเป็นเนื้อหาคลิป 4 (Feedback) — ต้องเขียนฉากใหม่ตามคลิปนี้"
