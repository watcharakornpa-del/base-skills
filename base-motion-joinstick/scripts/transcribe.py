#!/usr/bin/env python3
"""ถอดเสียงไฟล์ดิบด้วย ElevenLabs Scribe (เวลาระดับคำ/พยางค์ + เสียงที่ไม่ใช่คำ) → work/scribe.json
ใช้ (จากโฟลเดอร์โปรเจกต์): python work/transcribe.py "<ไฟล์ดิบ>"   · คีย์ ~/.elevenlabs/api_key (ไม่พิมพ์คีย์ออกจอ)"""
import json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
src = sys.argv[1]; FF = shutil.which('ffmpeg')
key = os.environ.get('ELEVENLABS_API_KEY') or open(os.path.expanduser('~/.elevenlabs/api_key'), encoding='utf-8').read().strip()
os.makedirs('work', exist_ok=True)
subprocess.run([FF, '-nostdin', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'libmp3lame', '-b:a', '64k', 'work/audio.mp3'], check=True)
code = subprocess.run(['curl', '-s', '-X', 'POST', 'https://api.elevenlabs.io/v1/speech-to-text', '-H', f'xi-api-key: {key}',
    '-F', 'model_id=scribe_v1', '-F', 'language_code=tha', '-F', 'timestamps_granularity=word', '-F', 'tag_audio_events=true',
    '-F', 'file=@work/audio.mp3', '-o', 'work/scribe.json', '-w', '%{http_code}'], capture_output=True, text=True).stdout
if code != '200': sys.exit(f'❌ Scribe HTTP {code}: ' + open('work/scribe.json', encoding='utf-8').read()[:300])
d = json.load(open('work/scribe.json', encoding='utf-8'))
open('work/transcript.txt', 'w', encoding='utf-8').write(d['text'])
json.dump({'src': os.path.abspath(src)}, open('work/source.json', 'w', encoding='utf-8'))
print('✅ ถอดเสียงแล้ว', len(d['words']), 'token ·', d['text'][:80], '…')
