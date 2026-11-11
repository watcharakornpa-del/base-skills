#!/usr/bin/env python3
"""โหมด Premiere: ตัดม้วน B-roll เป็นไฟล์ทีละช่วง (มี SFX ของช่วงนั้นในตัว) แล้วสั่งแผง AI Story Cutter วางลงไทม์ไลน์
ใช้ (จากโฟลเดอร์โปรเจกต์):
  python work/premiere_segs.py cut renders/reel.mp4                 → renders/broll/seg1.mp4 … (H.264 ทึบ ไม่ต้องพื้นใส เพราะการ์ดเต็มจอ)
  python work/premiere_segs.py insert "<ซีเควนซ์>" --offset <วินาทีที่คลิปเริ่มในซีเควนซ์> [--video N] [--audio N]
insert: วิดีโอลงแทร็กที่ยืนยันแล้วว่าว่าง (--video) · ทุกช่วงใช้ replace (ทับเฉพาะช่วงเวลาของคลิปเรา)
        เสียง SFX ลงแทร็กเสียงที่สั่ง (ค่าเริ่มต้น = เพิ่มแทร็กใหม่ต่อท้าย · ห้ามทับเสียงพูด/เพลงของทีม)"""
import argparse, json, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
BRIDGE = os.path.expanduser('~/.claude/skills/base-motion/scripts/premiere_bridge.py')
FILES = {'swoosh': 'assets/sfx/swoosh.mp3', 'click': 'assets/sfx/click.mp3', 'thump': 'assets/sfx/thump.wav', 'pen': 'assets/sfx/pen.wav'}
S = json.load(open('work/segs.json', encoding='utf-8')); SFX = json.load(open('work/sfx.json', encoding='utf-8'))

def cut(reel):
    os.makedirs('renders/broll', exist_ok=True); off = 0.0
    for n, a, b in S['segs']:
        L = round(b - a, 3); out = f'renders/broll/seg{n}.mp4'
        mine = [(t - a, k, v) for t, k, v in SFX if a - 0.01 <= t < b]
        cmd = [FF, '-nostdin', '-v', 'error', '-ss', str(off), '-t', str(L), '-i', reel,
               '-f', 'lavfi', '-t', str(L), '-i', 'anullsrc=r=48000:cl=stereo']
        fl = ['[1:a]aformat=sample_rates=48000:channel_layouts=stereo[z]']; lab = ['[z]']
        for i, (t, k, v) in enumerate(mine, 2):
            cmd += ['-i', FILES[k]]; ms = int(max(0, t) * 1000)
            fl.append(f'[{i}:a]volume={v},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{i}]'); lab.append(f'[s{i}]')
        fl.append(''.join(lab) + f'amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{L},alimiter=limit=0.7:level=false[a]')
        cmd += ['-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[a]', '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p',
                '-c:a', 'aac', '-b:a', '192k', '-y', out]
        subprocess.run(cmd, check=True); off = round(off + L, 3)
        print(f'✅ {out}  ({a}–{b} วิ · {L} วิ · SFX {len(mine)})')

def bridge(*args):
    env = dict(os.environ, PYTHONIOENCODING='utf-8')   # Windows: ไม่งั้นข้อความไทยจากสะพานออกมาเป็นรหัส แล้วเช็คคำไม่เจอ
    r = subprocess.run([sys.executable.replace('pythonw', 'python'), BRIDGE, *args], capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    return r.returncode, (r.stdout + r.stderr).strip()

def insert(seq, offset, video, audio):
    # แทร็กต้องเป็นตัวที่ผู้ใช้ยืนยันแล้วว่าว่างตลอดช่วงคลิปนี้ (ดูจาก .prproj) — ห้ามไล่ลองแทร็ก:
    # แผงนับแทร็กเปล่าว่ามี 1 ชิ้น (Premiere 2026) เลยปฏิเสธทุกแทร็ก และสร้างแทร็กเปล่าเพิ่มทุกครั้งที่ลอง
    segs = S['segs']; v = video
    for n, a, b in segs:
        code, msg = bridge('insert', os.path.abspath(f'renders/broll/seg{n}.mp4'), seq, '--video', str(v), '--audio', str(audio), '--at', str(round(offset + a, 3)), '--replace')
        print(f'seg{n}:', msg)
        if code: sys.exit(1)
    print(f'✅ วาง {len(segs)} ช่วงบน V{v + 1} · SFX บน A{audio + 1}')

ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest='cmd', required=True)
c = sp.add_parser('cut'); c.add_argument('reel')
i = sp.add_parser('insert'); i.add_argument('sequence'); i.add_argument('--offset', type=float, required=True)
i.add_argument('--video', type=int, required=True, help='แทร็กวิดีโอที่ยืนยันว่าว่าง (0=V1 · 4=V5)'); i.add_argument('--audio', type=int, required=True, help='แทร็กเสียงสำหรับ SFX (0=A1) · ใช้เลขที่ยังไม่มี = เพิ่มแทร็กใหม่')
a = ap.parse_args()
cut(a.reel) if a.cmd == 'cut' else insert(a.sequence, a.offset, a.video, a.audio)
