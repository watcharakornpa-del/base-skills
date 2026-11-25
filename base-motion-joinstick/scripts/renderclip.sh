#!/bin/zsh
# เรนเดอร์ → finalize → check_final → พรีวิว 720p · ใช้: renderclip.sh <โปรเจกต์> <ชื่อไฟล์ส่ง ไม่มี .mp4>
export PATH=$HOME/.local/bin:$PATH; PY=${JS_PY:-$(ls ~/.venvs/joinstick/bin/python ~/Desktop/BASE/.venv/bin/python ~/Developer/video-use/tiktok031026-clip6/.venv/bin/python 2>/dev/null | head -1)}; K=~/.claude/skills/base-motion-joinstick/scripts
cd "$1/gfx" || exit 1
python3 $K/cicheck.py . || { echo "⛔ CI ไม่ผ่าน ไม่เรนเดอร์ $1"; exit 1; }
npx --yes hyperframes@0.8.147 render -q draft --workers 1 -o renders/draft.mp4 > work/render_log.txt 2>&1 || { echo "❌ render $1"; tail -5 work/render_log.txt; exit 1; }
echo "HDR: $(grep -o '"effectiveHdr":"[a-z]*"' work/render_log.txt | head -1)"
cd ..; OUT="renders/$2.mp4"
$PY $K/finalize.py gfx/renders/draft.mp4 "$OUT" 2>&1 | tail -1
cp gfx/work/subs.srt "renders/$2_subs.srt"
$PY $K/check_final.py "$OUT" 2>&1 | grep -v "^NEAR" > work/check_final.txt; cat work/check_final.txt
$PY $K/facecheck.py "$OUT" 2>&1 | tee -a work/check_final.txt   # S1 กราฟิกห้ามทับหัวคนพูด (ผู้ใช้สั่ง 25 พ.ย. 2026)
ffmpeg -nostdin -v error -i "$OUT" -vf scale=720:1280 -c:v libx264 -preset fast -b:v 650k -maxrate 800k -bufsize 1500k -c:a aac -b:a 80k -movflags +faststart -y "renders/$2_preview.mp4"
# ปกซูม (ครึ่งบนจอ ช่วงคำใหญ่) ไว้เช็คฟอนต์ไทย/CI ด้วยตา — ผู้ใช้สั่ง: ตรวจ CI ทุกครั้ง
ffmpeg -nostdin -v error -ss 2.2 -i "$OUT" -frames:v 1 -vf "crop=1080:760:0:460" -y "renders/$2_ปก_ซูม.png"
echo "✅ $OUT $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT")"
