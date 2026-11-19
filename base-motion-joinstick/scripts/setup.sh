#!/bin/zsh
# ติดตั้งสิ่งที่สกิล base-motion-joinstick ต้องใช้ บนเครื่องใหม่ (รันครั้งเดียว · ซ้ำได้ไม่เสียหาย)
# ใช้: zsh ~/.claude/skills/base-motion-joinstick/scripts/setup.sh
VENV=~/.venvs/joinstick; ok=1
say() { print -r -- "$1"; }
for c in ffmpeg ffprobe node npx curl python3; do
  if command -v $c >/dev/null; then say "✅ $c"; else say "❌ ไม่มี $c"; ok=0; fi
done
[ $ok = 1 ] || say "   → ติดตั้งด้วย Homebrew: brew install ffmpeg node   (ไม่มี brew ให้แจ้งพี่ Mac)"
if [ ! -x $VENV/bin/python ]; then python3 -m venv $VENV || { say "❌ สร้าง venv ไม่ได้"; exit 1; }; fi
$VENV/bin/pip install -q --upgrade pip >/dev/null 2>&1
$VENV/bin/pip install -q numpy pythainlp && say "✅ Python venv $VENV (numpy · pythainlp)" || { say "❌ pip install ไม่สำเร็จ"; ok=0; }
# คีย์ ElevenLabs (ถอดเสียง) — ตรวจแค่ว่ามีไฟล์ ไม่อ่าน/ไม่พิมพ์คีย์
if [ -s ~/.elevenlabs/api_key ] || [ -n "$ELEVENLABS_API_KEY" ]; then say "✅ คีย์ ElevenLabs มีแล้ว"
else say "⚠️  ยังไม่มีคีย์ ElevenLabs → ขอคีย์จากพี่ Mac แล้วใส่ไว้ที่ ~/.elevenlabs/api_key (ไฟล์เดียว บรรทัดเดียว · ห้ามส่งในแชท)"; fi
mkdir -p ~/Developer/video-use && say "✅ โฟลเดอร์โปรเจกต์ ~/Developer/video-use"
npx --yes hyperframes@0.8.147 --version >/dev/null 2>&1 && say "✅ HyperFrames 0.8.147 (โหลด Chrome สำหรับเรนเดอร์ครั้งแรกอาจนาน)" || say "⚠️  เรียก HyperFrames ไม่ได้ (ต้องต่อเน็ต + Node ≥ 18)"
[ $ok = 1 ] && say "\nพร้อมใช้ · พิมพ์ /base-motion-joinstick ใน Claude Code" || say "\nยังไม่ครบ ดู ❌ ด้านบน"
