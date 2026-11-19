#!/bin/zsh
# ตัดใหม่ → talk.mp4 → ถอดเสียงไฟล์ตัด (ใช้ทุกครั้งที่ cuts.json เปลี่ยน) · ใช้: recut.sh <โปรเจกต์> <insert.mp4>
export PATH=$HOME/.local/bin:$PATH; PY=${JS_PY:-$(ls ~/.venvs/joinstick/bin/python ~/Desktop/BASE/.venv/bin/python ~/Developer/video-use/tiktok031026-clip6/.venv/bin/python 2>/dev/null | head -1)}; K=~/.claude/skills/base-motion-joinstick/scripts
cd "$1" || exit 1
$PY work/rough.py full > work/rough_log.txt 2>&1 || { echo "❌ full $1"; exit 1; }
if [ -d gfx ]; then cp renders/cut_1080.mp4 gfx/assets/talk.mp4; else $PY $K/setup_gfx.py . | tail -1; fi
[ -f gfx/assets/screen.mp4 ] || ffmpeg -nostdin -v error -i "$2" -an -c:v libx264 -preset fast -crf 18 -g 15 -keyint_min 15 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 -movflags +faststart -y gfx/assets/screen.mp4
$PY $K/retranscribe.py gfx/assets/talk.mp4 gfx/work/scribe.json
echo "✅ $(basename $1) talk $(ffprobe -v error -show_entries format=duration -of csv=p=0 gfx/assets/talk.mp4)"
