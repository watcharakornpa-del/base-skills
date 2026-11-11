"""ปรับเสียงไฟล์ที่เรนเดอร์แล้วเป็น ~−14 LUFS · peak ≤ −1 dBFS (loudnorm สองรอบ + limiter · ภาพก๊อปตรง ไม่เข้ารหัสใหม่)
เรนเดอร์จาก HyperFrames ออกมา −16 ถึง −18 LUFS เบากว่าเป้า (C5398/C5399)
ใช้: python finalize.py <in.mp4> <out.mp4>"""
import json, re, subprocess, sys
src, dst = sys.argv[1], sys.argv[2]
FF = __import__('shutil').which('ffmpeg') or 'ffmpeg'
r = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', src, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
m = json.loads(re.findall(r'\{[^{}]*\}', r)[-1])
af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
      f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000,alimiter=limit=0.85:level=false")   # loudnorm ออก 192 kHz → ลดเป็น 48k ก่อน limiter ไม่งั้นพีคเกินหลังแปลง (เคยได้ +0.4)
subprocess.run([FF, '-nostdin', '-v', 'error', '-i', src, '-c:v', 'copy', '-af', af, '-ar', '48000', '-c:a', 'aac', '-b:a', '256k',
                '-movflags', '+faststart', '-y', dst], check=True)
print('ok', dst, 'จาก', m['input_i'], 'LUFS')
