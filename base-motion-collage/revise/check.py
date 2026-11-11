#!/usr/bin/env python3
"""ตรวจไฟล์ที่เรนเดอร์จริง: ความยาว/ขนาด/เสียง/พีค + แผ่นภาพเช็คทุกวินาที + ซูมซับทุกบรรทัด (ไว้ดูวรรณยุกต์ทีละคำ)
ใช้: python3 -I work/check.py → work/check/sheet.jpg, work/check/caps_*.png"""
import json, os, re, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
C = json.load(open(f'{HERE}/clip.json', encoding='utf-8')); E = json.load(open(f'{HERE}/edl.json', encoding='utf-8'))
F = f"{P}/renders/{C['name']}.mp4"; D = f'{HERE}/check'; os.makedirs(D, exist_ok=True)
FF = shutil.which('ffmpeg'); run = lambda a: subprocess.run([FF, '-nostdin', '-v', 'error', '-y', *a], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_name,width,height:format=duration', '-of', 'compact', F], capture_output=True, text=True).stdout.strip())
r = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', F, '-af', 'loudnorm=print_format=summary', '-f', 'null', '-'], capture_output=True, text=True).stderr
print(' · '.join(re.findall(r'Input (?:Integrated|True Peak):\s+\S+ \S+', r)))
run(['-i', F, '-vf', "fps=1,scale=120:-1,drawtext=text='%{eif\\:t\\:d}':x=4:y=4:fontsize=22:fontcolor=yellow:box=1:boxcolor=black,tile=13x7", '-frames:v', '1', f'{D}/sheet.jpg'])
files = []
for i, c in enumerate(E['caps'], 1):
    o = f'{D}/c{i:02}.png'; files.append(o)
    run(['-ss', f"{(c['at'] + c['end']) / 2:.2f}", '-i', F, '-frames:v', '1', '-vf', f"crop=1040:150:20:1250,drawtext=text='{i}':x=6:y=6:fontsize=30:fontcolor=yellow:box=1:boxcolor=black", o])
for g in range(0, len(files), 13):
    part = files[g:g + 13]; a = []
    for f in part: a += ['-i', f]
    run([*a, '-filter_complex', f'vstack=inputs={len(part)}' if len(part) > 1 else 'null', f'{D}/caps_{g // 13 + 1}.png'])
print(f'✅ {D}/sheet.jpg + caps_1..{(len(files) + 12) // 13}.png ({len(files)} บรรทัด)')
