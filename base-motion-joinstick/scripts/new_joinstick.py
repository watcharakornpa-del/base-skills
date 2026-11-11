#!/usr/bin/env python3
"""base-motion-joinstick ขั้น 1 — ตั้งโปรเจกต์จากไฟล์ดิบ + ถอดเสียง + ตารางวลี (สำหรับเลือกช่วงตัด)
ใช้: python new_joinstick.py <ชื่อโปรเจกต์> "<ไฟล์ดิบ.MP4>"
โปรเจกต์อยู่ที่ $BASE_MOTION_HOME (ค่าเริ่มต้น ~/Developer/video-use) · ไฟล์ดิบไม่ถูกก๊อปหรือแก้ (อ่านอย่างเดียว)
คีย์ ElevenLabs อ่านจาก ~/.elevenlabs/api_key โดย transcribe.py (ไม่พิมพ์คีย์ออกจอ)"""
import os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
if len(sys.argv) < 3 or not os.path.isfile(sys.argv[2]): sys.exit('ใช้: new_joinstick.py <ชื่อ> "<ไฟล์ดิบ.MP4>"')
name, src = sys.argv[1], os.path.abspath(sys.argv[2])
K = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(os.environ.get('BASE_MOTION_HOME', os.path.expanduser('~/Developer/video-use')), name)
if os.path.exists(P): sys.exit(f'❌ มีโปรเจกต์ชื่อนี้แล้ว: {P}')
for d in ('work', 'renders', 'assets'): os.makedirs(os.path.join(P, d))
S = os.path.join(K, 'scripts')
for f in ('rough.py', 'transcribe.py', 'hlg2sdr_lut.py'): shutil.copy(os.path.join(S, f), os.path.join(P, 'work'))
shutil.copytree(os.path.join(S, 'fonts'), os.path.join(P, 'work', 'fonts'))
os.chdir(P); py = sys.executable
# กล้องทีมถ่าย HLG แต่ ffmpeg บน Mac (conda-forge) ไม่มี zscale → rough.py แปลงสีด้วย LUT นี้แทน
subprocess.run([py, 'work/hlg2sdr_lut.py', 'assets/hlg2sdr.cube'], check=True)
subprocess.run([py, 'work/transcribe.py', src], check=True)
subprocess.run([py, 'work/rough.py', 'table'], check=True, stdout=subprocess.DEVNULL)
print('✅', P, '· อ่าน work/phrases.txt แล้วเขียน work/cuts.json')
