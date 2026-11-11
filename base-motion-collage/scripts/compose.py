#!/usr/bin/env python3
"""วางม้วน B-roll ทับคลิปเดิมตามเวลาจริง + มิกซ์ SFX → ไฟล์ส่งงาน
ใช้ (จากโฟลเดอร์โปรเจกต์): python work/compose.py renders/reel.mp4 renders/<ชื่อ>-draft.mp4
อ่าน work/segs.json (ช่วง B-roll · เวลาคลิปจริง) + work/sfx.json จาก gen.py
ภาพนอกช่วง B-roll = assets/talk.mp4 เดิมทุกเฟรม (ปก/ซับ/การตัดของทีมอยู่ครบ)"""
import json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
reel, out = sys.argv[1], sys.argv[2]
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
S = json.load(open('work/segs.json', encoding='utf-8')); SFX = json.load(open('work/sfx.json', encoding='utf-8'))
FILES = {'swoosh': 'assets/sfx/swoosh.mp3', 'click': 'assets/sfx/click.mp3', 'thump': 'assets/sfx/thump.wav', 'pen': 'assets/sfx/pen.wav'}

cmd = [FF, '-nostdin', '-v', 'error', '-i', 'assets/talk.mp4', '-i', reel]
fl = []; off = 0.0; last = '[0:v]'
for i, (n, a, b) in enumerate(S['segs']):
    L = round(b - a, 3)
    fl.append(f'[1:v]trim=start={off}:duration={L},setpts=PTS-STARTPTS+{a}/TB[r{n}]')
    nxt = f'[v{n}]'
    fl.append(f"{last}[r{n}]overlay=eof_action=pass:enable='between(t,{a},{round(b - 0.001, 3)})'{nxt}")
    last = nxt; off = round(off + L, 3)
# เสียง: เสียงเดิม (loudnorm −14) + SFX ตามเวลาจริง
fl.append('[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aformat=sample_rates=48000:channel_layouts=stereo[va]'); labels = ['[va]']
for k, (t, kind, vol) in enumerate(SFX, 2):
    cmd += ['-i', FILES[kind]]; ms = int(t * 1000)
    fl.append(f'[{k}:a]volume={vol},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{k}]'); labels.append(f'[s{k}]')
fl.append(''.join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{S["total"]},alimiter=limit=0.8:level=false[a]")
cmd += ['-filter_complex', ';'.join(fl), '-map', last, '-map', '[a]', '-t', str(S['total']),
        '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-y', out]
subprocess.run(cmd, check=True)
print('✅', out)
