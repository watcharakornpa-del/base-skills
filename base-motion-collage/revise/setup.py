#!/usr/bin/env python3
"""ตั้งโปรเจกต์ "แก้คลิปตามรีฟ" (Draft1 → Draft2) ของ base-motion-collage
ใช้: python3 -I setup.py <ชื่อโปรเจกต์> "<Draft1.mp4>" "<collage.mp4>" "<roughcut.xml>" "<ซับทีม .srt>" "<ไฟล์ส่ง Draft2.mp4>"
ทำให้: ~/Developer/video-use/<ชื่อ>/work/ (ก๊อปสคริปต์ชุดนี้) · ถอดเสียง Draft1 (ElevenLabs) · แผนที่ rough cut → ต้นฉบับ 4K
· หาช่วง B-roll ใน Draft1 อัตโนมัติ · plan.py ตั้งต้นให้แก้"""
import json, os, re, shutil, subprocess, sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote
KIT = os.path.dirname(os.path.abspath(__file__))
name, draft1, collage, xmlp, srt, out = sys.argv[1:7]
P = os.path.expanduser(f'~/Developer/video-use/{name}'); W = f'{P}/work'
os.makedirs(W, exist_ok=True); os.makedirs(f'{P}/assets', exist_ok=True); os.makedirs(f'{P}/renders/gfx', exist_ok=True)
for f in os.listdir(KIT):
    if f.endswith(('.py', '.sh')) and f not in ('setup.py', 'plan_template.py'): shutil.copy(f'{KIT}/{f}', W)
for f in ('underline.png', 'BASE-dark-moody.cube'): shutil.copy(f'{KIT}/assets/{f}', f'{P}/assets/')
if not os.path.exists(f'{W}/plan.py'): shutil.copy(f'{KIT}/plan_template.py', f'{W}/plan.py')
FF = shutil.which('ffmpeg')

# ไฟล์ต้นฉบับ 4K: เอาจาก pathurl ใน XML (เครื่อง Windows) แล้วหาไฟล์ชื่อเดียวกันในโฟลเดอร์โปรเจกต์
x = ET.parse(xmlp).getroot()
url = unquote(x.find('.//file/pathurl').text); base = os.path.basename(url.replace('\\', '/'))
root = os.path.dirname(os.path.dirname(xmlp))
src = next((os.path.join(d, base) for d, _, fs in os.walk(root) if base in fs), None)
if not src: sys.exit(f'❌ หาไฟล์ต้นฉบับ {base} ไม่เจอใน {root}')
M = [dict(start=int(c.find('start').text), end=int(c.find('end').text), src_in=int(c.find('in').text), src_out=int(c.find('out').text))
     for c in x.find('./sequence/media/video/track').findall('clipitem')]
json.dump(M, open(f'{W}/xmlmap.json', 'w'), indent=1)
json.dump(dict(name=name, draft1=draft1, collage=collage, xml=xmlp, srt=srt, src=src, out=out), open(f'{W}/clip.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ช่วง B-roll: ขอบซ้ายของ collage เป็นกระดาษขยำสว่าง (ภาพกล้องตรงนั้นมืด)
r = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', collage, '-vf', 'crop=50:1400:0:250,signalstats,metadata=print:key=lavfi.signalstats.YAVG',
                    '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
ys = [float(v) for v in re.findall(r'YAVG=([\d.]+)', r)]
br = []; on = None
for i, y in enumerate(ys + [0]):
    t = round(i / 30, 3)
    if y > 170 and on is None: on = t
    if y <= 170 and on is not None:
        if t - on > 0.5: br.append([on, t])
        on = None
m = []                                           # รวมช่วงที่ห่างกันไม่ถึง 0.3 วิ (กันภาพกล้องแว้บ 1 เฟรม)
for r in br:
    if m and r[0] - m[-1][1] < 0.3: m[-1][1] = r[1]
    else: m.append(r)
br = m
json.dump(br, open(f'{W}/broll.json', 'w'), indent=1)

# ถอดเสียง Draft1 (เวลาตรงกับ timestamp ในรีฟ)
if not os.path.exists(f'{W}/scribe.json'):
    subprocess.run(['python3', '-I', os.path.expanduser('~/.claude/skills/base-rough-cut/scripts/transcribe.py'), draft1], cwd=P, check=True)
print(f'✅ {P}\n   ต้นฉบับ: {src}\n   B-roll ใน Draft1: {br}\n   ต่อไป: แก้ work/plan.py ตามรีฟ → python3 -I work/edl.py')
