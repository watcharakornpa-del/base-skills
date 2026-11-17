#!/usr/bin/env python3
"""ตรวจเสียงคลิปที่จะส่ง เทียบกับไฟล์กล้องต้นฉบับ — หา 3 อย่างที่หูทีมจับได้แต่ตาไม่เห็น (เจอจริง C5395 พ.ย. 2026):
  🔁 คำซ้ำ/คำแหว่งตรงรอยตัด  (ขอบ B-roll เสียงเหลื่อม 0.05–0.2 วิ: "ด-ดังนั้น")
  ✂️ หัว/หางคำโดนตัด          (จุดตัดชิดคำเกิน: "HR" ตอนเริ่ม · "พอ ๆ กัน" ตอนจบ)
  🔉 เสียงตก/ดูดตรงรอยตัด      (ขึ้น/ลงกราฟิกแล้วเสียงตกร่อง · B-roll โดนบีบซ้ำ)
วิธี: ทุก 0.1 วิ หาว่าเสียงในคลิปมาจากวินาทีไหนของไฟล์กล้อง (เทียบคลื่นเสียง) → รู้รอยตัดทุกจุด + ระดับเสียงเทียบต้นฉบับ
ใช้: python audio_check.py <คลิป.mp4> <ไฟล์กล้องต้นฉบับ> [--start <วินาทีในไฟล์กล้องตอนคลิปเริ่ม (ไม่ใส่ = หาเอง)>]
ผล: รายการจุดที่ต้องฟัง (เวลาในคลิป) · exit 1 ถ้ามี 🔁 หรือ ✂️
ต้องมี numpy + scipy"""
import argparse, shutil, subprocess, sys
import numpy as np
from scipy.signal import fftconvolve
sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser(); ap.add_argument('clip'); ap.add_argument('src'); ap.add_argument('--start', type=float)
A = ap.parse_args()
FF = shutil.which('ffmpeg') or 'ffmpeg'; SR = 16000; HOP = .1

def dec(f):
    b = subprocess.run([FF, '-nostdin', '-v', 'error', '-i', f, '-vn', '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    return np.frombuffer(b, np.int16).astype(np.float32) / 32768
X, S = dec(A.clip), dec(A.src)
ENV = 20 * np.log10(np.sqrt((S[:len(S) // 160 * 160].reshape(-1, 160) ** 2).mean(1)) + 1e-9)   # ต้นฉบับ dB ทุก 10 ms
FLOOR = float(np.percentile(ENV, 5)); SPEECH = FLOOR + 25
def senv(a, b):
    i, j = max(0, int(a * 100)), max(int(a * 100) + 1, int(b * 100)); return float(ENV[i:j].max()) if j <= len(ENV) else -99
def lvl(x): return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)

def locate(x, guess=None, span=None):
    """เสียง x อยู่ที่วินาทีไหนของไฟล์กล้อง → (วินาที, ความตรง 0–1)"""
    if guess is None: a0, y = 0, S
    else:
        a0 = max(0, int((guess - span) * SR)); y = S[a0:int((guess + span) * SR) + len(x)]
    x = x[::2].astype(np.float64); y = y[::2].astype(np.float64); n = len(x)
    if len(y) <= n or x.std() < 1e-5: return (guess or 0), 0.0
    x = (x - x.mean()) / x.std(); c = fftconvolve(y, x[::-1], 'valid')
    cs = np.concatenate([[0], np.cumsum(y)]); cs2 = np.concatenate([[0], np.cumsum(y * y)])
    m = (cs[n:] - cs[:-n]) / n; v = (cs2[n:] - cs2[:-n]) / n - m * m
    r = np.where(v > 1e-8, c / (n * np.sqrt(np.maximum(v, 1e-8))), 0); k = int(np.argmax(r))
    return (a0 + k * 2) / SR, float(r[k])

T = len(X) / SR; rows = []; prev = A.start
for t in np.arange(0, T - .2, HOP):
    x = X[int(t * SR):int((t + .2) * SR)]
    if prev is not None:
        r, c = locate(x, prev + HOP, .4)
        if c < .75: r, c = locate(x, prev + HOP, 15)
        if c < .75: r, c = locate(x)
    else: r, c = locate(x)
    rows.append([t, r, c, lvl(X[int(t * SR):int((t + HOP) * SR)]), lvl(S[int(r * SR):int((r + HOP) * SR)])])
    if c >= .75: prev = r
    elif prev is not None: prev += HOP
R = np.array(rows); ok = R[:, 2] >= .75
cons = lambda i, k: abs((R[k, 1] - R[i, 1]) - (R[k, 0] - R[i, 0])) < .02
ok = np.array([ok[i] and ((i > 0 and ok[i - 1] and cons(i - 1, i)) or (i + 1 < len(R) and ok[i + 1] and cons(i, i + 1)))
               for i in range(len(R))])                           # ต้องมีท่อนข้าง ๆ ต่อกันยืนยัน (กันจับคู่ผิดที่ไกล ๆ)
print(f'{A.clip}\n  หาเวลาเจอ {int(ok.sum())}/{len(R)} ท่อน (ที่เหลือเป็นช่วงเงียบ/SFX/เพลง) · ไฟล์กล้อง {R[ok, 1].min():.1f}–{R[ok, 1].max():.1f} วิ')

# รอยตัด = ท่อนติดกันที่เวลาไฟล์กล้องไม่ต่อกัน → หาจุดตัดจริงละเอียด 5 ms (ท่อนละ 0.1 วิ หยาบเกินจะวัดเศษคำ)
def ncc(x, y):
    n = min(len(x), len(y));
    if n < 8: return 0.0
    x, y = x[:n] - x[:n].mean(), y[:n] - y[:n].mean(); return float((x * y).sum() / (np.sqrt((x * x).sum() * (y * y).sum()) + 1e-9))
def refine(tA, rA, tB, rB):
    """จุดในคลิป (tA..tB+0.1) ที่เสียงเปลี่ยนจากแทร็ก A (ต้นฉบับ rA ที่ tA) ไปแทร็ก B → (เวลาคลิป, ต้นฉบับฝั่ง A, ต้นฉบับฝั่ง B)"""
    w = int(.02 * SR); best = (tA + HOP, -9)
    for t in np.arange(tA, tB + HOP, .005):
        sc = 0
        for u in np.arange(t - .06, t + .06, .02):                 # ก่อน t ต้องเหมือน A · หลัง t ต้องเหมือน B
            seg = X[int(u * SR):int(u * SR) + w]
            ra, rb = rA + (u - tA), rB + (u - tB)
            ca = ncc(seg, S[int(ra * SR):int(ra * SR) + w]); cb = ncc(seg, S[int(rb * SR):int(rb * SR) + w])
            sc += (ca - cb) if u < t else (cb - ca)
        if sc > best[1]: best = (t, sc)
    t = best[0]; return t, rA + (t - tA), rB + (t - tB)
bad = 0; cuts = []
last = None
for i in range(len(R)):
    if not ok[i]: continue
    k, last = last, i
    if k is None or R[i, 0] - R[k, 0] > .65: continue          # ข้ามช่วงเงียบ/SFX ยาวไป ไม่นับ
    j = R[i, 1] - R[k, 1] - (R[i, 0] - R[k, 0])
    if abs(j) < .025: continue
    t, r0, r1 = refine(R[k, 0], R[k, 1], R[i, 0], R[i, 1]); cuts.append(t)   # r0 = ต้นฉบับที่ถูกตัดทิ้งเริ่มตรงนี้ · r1 = ต้นฉบับที่เล่นต่อ
    if j < 0:
        d = r0 - r1; seg = X[int((t - d) * SR):int(t * SR)]; ref = S[int(r1 * SR):int(r0 * SR)]
        really = ncc(seg, ref) > .7 and lvl(seg) > SPEECH                # ก่อนรอยตัดเล่นท่อนนี้ไปแล้วจริง (ไม่ใช่แค่เติมช่วงเงียบ)
        if really and senv(r1, r0) > SPEECH + 6:
            print(f'  🔁 {t:6.2f}s  เสียงซ้ำ {(r0 - r1) * 1000:.0f} ms (ต้นฉบับ {r1:.2f}–{r0:.2f} เล่นสองรอบ)'); bad += 1
    elif j < .3:
        if senv(r0, r1) > SPEECH:
            print(f'  ✂️ {t:6.2f}s  เสียงหาย {(r1 - r0) * 1000:.0f} ms กลางคำ (ต้นฉบับ {r0:.2f}–{r1:.2f})'); bad += 1
    else:
        tail, head = senv(r0, r0 + .05) > SPEECH, senv(r1 - .05, r1) > SPEECH
        if tail or head:
            print(f'  ✂️ {t:6.2f}s  {" · ".join(x for x, y in (("หางคำขาด", tail), ("หัวคำขาด", head)) if y)} (ตัดจาก {r0:.2f} ไป {r1:.2f})'); bad += 1
# เศษคำ: เสียงสั้น ๆ (≤ 80 ms) โดด ๆ มีเงียบหน้า-หลัง ใกล้รอยตัด = พยางค์ที่โดนตัดเหลือติดมา ("ด-ดังนั้น")
CE = 20 * np.log10(np.sqrt((X[:len(X) // 160 * 160].reshape(-1, 160) ** 2).mean(1)) + 1e-9)
CF = float(np.percentile(CE, 5)); loud = CE > CF + 22; frag = 0
for c in cuts:
    i0, i1 = max(0, int((c - .3) * 100)), min(len(CE), int((c + .3) * 100)); k = i0
    while k < i1:
        if loud[k]:
            e = k
            while e < len(loud) and loud[e]: e += 1
            near = c - .04 <= e / 100 <= c + .02 or c - .02 <= k / 100 <= c + .04   # ต้องชิดรอยตัด (พยางค์สั้นปกติไม่นับ)
            if near and 2 <= e - k <= 8 and not loud[max(0, k - 4):k].any() and not loud[e:e + 4].any():
                print(f'  ✂️ {k / 100:6.2f}s  เศษคำ {(e - k) * 10} ms โดด ๆ ติดรอยตัด (พยางค์ที่โดนตัดเหลือติดมา)'); frag += 1
            k = e
        k += 1
bad += frag
# ท้ายคลิป: หางเสียงคำสุดท้ายยังไม่หาย
re_ = R[ok][-1, 1] + (T - R[ok][-1, 0])
if senv(re_, re_ + .06) > FLOOR + 17: print(f'  ✂️ {T:6.2f}s  ท้ายคลิป หางเสียงคำสุดท้ายยังไม่หาย (ต้นฉบับหลัง {re_:.2f} ยังมีเสียง)'); bad += 1
if senv(R[0, 1] - .08, R[0, 1]) > SPEECH and ok[0]: print(f'  ✂️   0.00s  หัวคำแรกขาด (เสียงเริ่มก่อน {R[0, 1]:.2f} ในต้นฉบับ)'); bad += 1

# 🔉 ระดับเสียง: gain (คลิป − ต้นฉบับ) เทียบค่ามัธยฐานของท่อนที่ต้นฉบับดังพอ ๆ กัน → ตกเกิน 4 dB ใกล้รอยตัด (±1 วิ)
sp = ok & (R[:, 4] > SPEECH - 3); gain = R[:, 3] - R[:, 4]; ref = np.full(len(R), np.nan)
for b0 in np.arange(SPEECH - 3, SPEECH + 40, 4):
    s_ = sp & (R[:, 4] >= b0) & (R[:, 4] < b0 + 4)
    if s_.sum() > 5: ref[s_] = np.median(gain[s_])
dips = [R[i, 0] for i in range(len(R)) if sp[i] and gain[i] - ref[i] < -4 and any(abs(R[i, 0] - c) < 1 for c in cuts)]
for t in dips: print(f'  🔉 {t:6.2f}s  เสียงเบากว่าปกติ {gain[int(round(t / HOP))] - ref[int(round(t / HOP))]:+.1f} dB (ใกล้รอยตัด)')
print(f'  สรุป: รอยตัด {len(cuts)} จุด · 🔁/✂️ {bad} จุด · 🔉 {len(dips)} ท่อน' + ('  ✅ ไม่เจอคำซ้ำ/คำขาด' if not bad else '  → เปิดฟังทุกจุดข้างบนก่อนส่ง'))
sys.exit(1 if bad else 0)
