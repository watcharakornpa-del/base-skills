#!/bin/zsh
# base-motion — ตั้งโปรเจกต์ใหม่ + ถอดเสียงด้วย ElevenLabs Scribe (เวลาระดับตัวอักษร)
# ใช้: new_project.sh <ชื่อโปรเจกต์> <คลิปพูด.mp4> [--overlay]
#   --overlay = คลิปที่ตัดเสร็จจาก Premiere → ทำชั้นกราฟิกพื้นใส (MOV) ไปวางทับบน V2
# โปรเจกต์อยู่ที่ $BASE_MOTION_HOME (ค่าเริ่มต้น ~/Developer/video-use)
# คีย์ ElevenLabs: env ELEVENLABS_API_KEY หรือไฟล์ ~/.elevenlabs/api_key
set -e
NAME="$1"; SRC="$2"; MODE="$3"
[[ -z "$NAME" || ! -f "$SRC" ]] && { echo "ใช้: new_project.sh <ชื่อ> <คลิป.mp4>"; exit 1; }
K="${0:A:h:h}"; P="${BASE_MOTION_HOME:-$HOME/Developer/video-use}/$NAME"
FF="${FFMPEG:-$(command -v ffmpeg)}"; FP="$(dirname "$FF")/ffprobe"
[[ -x "$FF" ]] || { echo "❌ ไม่เจอ ffmpeg — รัน setup.sh ก่อน"; exit 1; }
KEY="${ELEVENLABS_API_KEY:-$(cat ~/.elevenlabs/api_key 2>/dev/null)}"
[[ -z "$KEY" ]] && { echo "❌ ไม่เจอคีย์ ElevenLabs — ใส่ใน ~/.elevenlabs/api_key (รัน setup.sh)"; exit 1; }
[[ -e "$P" ]] && { echo "❌ มีโปรเจกต์ชื่อนี้แล้ว: $P"; exit 1; }
mkdir -p "$P"/{assets/sfx,fonts,work}
cp $K/template/{package.json,CLAUDE.md,AGENTS.md,hyperframes.json,style.css,gen.py} "$P/"
sed -i '' "s/base-motion-project/$NAME/" "$P/package.json"
[[ "$MODE" == --overlay ]] && sed -i '' 's/^OVERLAY = False /OVERLAY = True  /' "$P/gen.py"
echo "{\"id\":\"$NAME\",\"name\":\"$NAME\"}" > "$P/meta.json"
cp $K/scripts/align.py "$P/work/"; cp $K/assets/sfx/* "$P/assets/sfx/"
cp $K/assets/fonts/*.ttf "$P/fonts/"
cp $K/assets/base-logo.png "$P/assets/base-logo.png"
cp "$SRC" "$P/assets/talk.mp4"
# ถอดเสียง: ElevenLabs Scribe (แม่นกว่า whisper-th มาก · whisper หลุดช่วงยาว/หลอนท้ายคลิป)
"$FF" -v error -y -i "$P/assets/talk.mp4" -vn -ac 1 -ar 16000 -c:a libmp3lame -b:a 64k "$P/work/audio.mp3"
code=$(curl -s -X POST https://api.elevenlabs.io/v1/speech-to-text -H "xi-api-key: $KEY" \
  -F model_id=scribe_v1 -F language_code=tha -F timestamps_granularity=word -F file=@"$P/work/audio.mp3" \
  -o "$P/work/scribe.json" -w '%{http_code}')
[[ "$code" != 200 ]] && { echo "❌ Scribe HTTP $code"; cat "$P/work/scribe.json"; exit 1; }
"$FP" -v error -show_entries format=duration:stream=width,height,r_frame_rate -of compact "$P/assets/talk.mp4"
python3 -I -c "import json,sys;print(json.load(open(sys.argv[1]))['text'])" "$P/work/scribe.json" > "$P/work/transcript.txt"
echo "✅ $P · ข้อความถอดเสียง: $P/work/transcript.txt"
