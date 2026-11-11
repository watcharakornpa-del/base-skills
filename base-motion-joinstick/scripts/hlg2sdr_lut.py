"""สร้าง LUT แปลง HLG BT.2020 → SDR Rec.709 (ขาวอ้างอิง 203 nits = 100% · knee ไฮไลต์)
ใช้แทน zscale เพราะ ffmpeg บน Mac เครื่องนี้ (conda-forge) ไม่มี zscale/libplacebo
filter: scale=in_color_matrix=bt2020:in_range=tv,format=rgb48le,lut3d=<cube>,scale=out_color_matrix=bt709:out_range=tv,format=yuv420p"""
import sys, numpy as np
N = 65; out = sys.argv[1]
a, b, c = 0.17883277, 0.28466892, 0.55991073
g = np.linspace(0, 1, N)
B_, G_, R_ = np.meshgrid(g, g, g, indexing='ij')          # .cube: R เร็วสุด
E = np.stack([R_, G_, B_], -1).reshape(-1, 3)
lin = np.where(E <= 0.5, E * E / 3, (np.exp((E - c) / a) + b) / 12)   # HLG inverse OETF → scene linear 0..1
Ys = lin @ np.array([0.2627, 0.6780, 0.0593])
disp = 1000 * np.power(np.maximum(Ys, 1e-9), 0.2)[:, None] * lin       # OOTF Lw=1000 (nits)
x = disp / 203.0                                                        # npl=203 → 1.0 = ขาวอ้างอิง
M = np.array([[1.6605, -0.5876, -0.0728], [-0.1246, 1.1329, -0.0083], [-0.0182, -0.1006, 1.1187]])
x = np.clip(x @ M.T, 0, None)                                           # BT.2020 → BT.709
def hable(v):
    A, B, C, D, Ee, F = .15, .5, .1, .2, .02, .3
    return (v * (A * v + C * B) + D * Ee) / (v * (A * v + B) + D * F) - Ee / F
sig = np.maximum(x.max(1), 1e-6)                                      # ขาวอ้างอิง HLG (203 nits) = 100% SDR · ไฮไลต์เหนือ 0.8 บีบนุ่ม (knee)
k = 0.8
y = np.where(sig <= k, sig, k + (1 - k) * (1 - np.exp(-(sig - k) / (1 - k))))
x = x * (y / sig)[:, None]
x = np.clip(x, 0, 1)
o = np.where(x < 0.018, 4.5 * x, 1.099 * np.power(x, 0.45) - 0.099)    # BT.709 OETF
with open(out, 'w') as f:
    f.write(f'LUT_3D_SIZE {N}\n')
    for r in o: f.write(f'{r[0]:.6f} {r[1]:.6f} {r[2]:.6f}\n')
print('ok', out)
