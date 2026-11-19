#!/usr/bin/env python3
"""ถอดเสียงไฟล์ที่ตัดแล้ว / ไฟล์ส่ง ด้วย Scribe ในโฟลเดอร์ชั่วคราว (ไม่ทับ work/ ของไฟล์ดิบ)
ใช้: python retranscribe.py <ไฟล์.mp4> <ปลายทาง scribe.json>
- หลัง rough.py full: python retranscribe.py gfx/assets/talk.mp4 gfx/work/scribe.json  ← เวลาซับ/at() ตรงเสียงที่ได้ยินจริง
  (แปลงเวลาจากไฟล์ดิบผ่าน keep.json เพี้ยนตรงจุดตัดคำ · C2676)
- ก่อนส่ง: check_final.py เรียกให้เอง"""
import json, os, shutil, subprocess, sys, tempfile
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
here = os.path.dirname(os.path.abspath(__file__)); tmp = tempfile.mkdtemp(prefix='retx-')
subprocess.run([sys.executable, os.path.join(here, 'transcribe.py'), src], cwd=tmp, check=True, stdout=subprocess.DEVNULL)
shutil.copy(os.path.join(tmp, 'work', 'scribe.json'), out)
d = json.load(open(out, encoding='utf-8'))
open(os.path.splitext(out)[0].replace('scribe', 'transcript') + '.txt', 'w', encoding='utf-8').write(
    ''.join(w['text'] for w in d['words'] if w['type'] != 'audio_event'))
shutil.rmtree(tmp, ignore_errors=True)
print('✅', out, '·', sum(w['type'] == 'word' for w in d['words']), 'token')
