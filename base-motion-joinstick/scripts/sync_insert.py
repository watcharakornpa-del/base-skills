#!/usr/bin/env python3
"""หาออฟเซ็ตของ screen record เทียบกล้อง: เวลา insert = เวลากล้อง − OFF (cross-correlation envelope เสียง 100 Hz)
ใช้: python sync_insert.py <โปรเจกต์> <insert.mp4>  → พิมพ์ OFF + ความมั่นใจ 3 ช่วง"""
import subprocess, shutil, sys, numpy as np
P, F = sys.argv[1], sys.argv[2]; FF = shutil.which('ffmpeg')
pcm = lambda f: np.frombuffer(subprocess.run([FF, '-nostdin', '-v', 'error', '-i', f, '-vn', '-ac', '1', '-ar', '2000', '-f', 's16le', '-'], capture_output=True).stdout, np.int16).astype(float)
env = lambda x: np.abs(x[:len(x) // 20 * 20]).reshape(-1, 20).mean(1)
a, b = env(pcm(f'{P}/work/audio.mp3')), env(pcm(F)); a = (a - a.mean()) / a.std(); b = (b - b.mean()) / b.std()
c = np.correlate(np.pad(a, (len(b), len(b))), b, 'valid'); k = int(np.argmax(c)) - len(b)
print(f'OFF = {k / 100:.2f}  (insert t=0 ↔ กล้อง t={k / 100:.2f}) · peak {c.max() / len(b):.2f}')
for t in (len(b) // 400, len(b) // 200, len(b) * 3 // 400):
    w = b[t * 100:(t + 20) * 100]; cc = np.correlate(a, w, 'valid'); kk = int(np.argmax(cc)); print(f'  insert {t}s → กล้อง {kk / 100:.2f} · off {kk / 100 - t:.2f} · {cc.max() / len(w):.2f}')
