"""สร้าง LUT โทนเข้ม (.cube 33³) ใช้ได้ทั้ง ffmpeg lut3d และ Lumetri ใน Premiere (Creative › Look)
เข้ม = ลดแสงกลาง ~0.6 stop · กดไฮไลต์ (ท้องฟ้าหน้าต่าง) · คอนทราสต์ S-curve · ลดความอิ่มสี 15% · อุ่นเล็กน้อย"""
import os, sys
N = 33; out = sys.argv[1]
def tone(x):
    x = x ** 1.35                                   # ลดแสงกลาง
    x = x / (1 + 0.55 * x) * 1.55                   # กดไฮไลต์ (roll-off) ให้ขาวสุด ≈ 1.0
    s = x * x * (3 - 2 * x)                         # S-curve
    return min(1, max(0, 0.70 * x + 0.30 * s))
lines = ['TITLE "BASE dark moody v1"', f'LUT_3D_SIZE {N}', 'DOMAIN_MIN 0 0 0', 'DOMAIN_MAX 1 1 1']
for b in range(N):
    for g in range(N):
        for r in range(N):
            R, G, B = (tone(v / (N - 1)) for v in (r, g, b))
            Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
            R, G, B = (Y + 0.85 * (c - Y) for c in (R, G, B))      # ลดอิ่มสี
            R, B = R * 1.02, B * 0.97                              # อุ่นนิด
            lines.append(' '.join(f'{min(1, max(0, c)):.6f}' for c in (R, G, B)))
open(out, 'w').write('\n'.join(lines) + '\n')
print('✅', out)
