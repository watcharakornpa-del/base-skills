#!/usr/bin/env python3
"""ก๊อป renders/<ชื่อ>.mp4 + .srt ไปที่ไฟล์ส่ง (clip.json: out) · ไม่ยอมเขียนทับไฟล์ที่ชื่อมี Draft1
ใช้: python3 -I work/deliver.py"""
import json, os, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
C = json.load(open(f'{HERE}/clip.json', encoding='utf-8')); out = C['out']
if 'Draft1' in os.path.basename(out): raise SystemExit('❌ ห้ามเขียนทับ Draft1')
shutil.copy(f"{P}/renders/{C['name']}.mp4", out); shutil.copy(f"{P}/renders/{C['name']}.srt", out[:-4] + '.srt')
print('✅', out); print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', out], capture_output=True, text=True).stdout.strip(), 'วิ')
