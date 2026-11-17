#!/usr/bin/env python3
"""plan.py + Scribe + ซับทีม → work/edl.json (ชิ้นตัด · ปก · Super · ซับ) + renders/<ชื่อ>.srt
ซับตั้งต้นจากซับทีมของ Draft1 (คำสะกดที่ทีมแก้แล้ว) → ตัด อ่ะ/น่ะ/คำถามคือ → FIX → REWRITE → ย้ายเวลาเข้าไทม์ไลน์ใหม่
ไม่มีซับใต้ปก / B-roll / Super · เตือนบรรทัดยาวเกินจอ และคำอังกฤษที่โดนแยกบรรทัด
ใช้: python3 -I work/edl.py"""
import json, os, re, sys
try: import PIL                                   # ต้องมี Pillow ไว้วัดความกว้างซับ — python3 ของระบบ Mac ไม่มี → สลับไป .venv
except ImportError:
    V = os.path.expanduser('~/Desktop/BASE/.venv/bin/python')
    if os.path.exists(V) and sys.executable != V: os.execv(V, [V, '-I', *sys.argv])
    sys.exit('❌ ไม่มี Pillow (pip install Pillow) — วัดความกว้างซับไม่ได้')
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
sys.path.insert(0, HERE); import plan
FPS = 30
C = json.load(open(f'{HERE}/clip.json', encoding='utf-8'))
BR = json.load(open(f'{HERE}/broll.json'))
END = max(m['end'] for m in json.load(open(f'{HERE}/xmlmap.json'))) / FPS
norm = lambda s: re.sub(r'[\s,.!?“”"\'‘’]', '', s)

W = [w for w in json.load(open(f'{HERE}/scribe.json', encoding='utf-8'))['words'] if w['type'] == 'word']
CH = []
for w in W:
    t = norm(w['text']); n = len(t)
    for i, c in enumerate(t):
        CH.append((c, w['start'] + (w['end'] - w['start']) * i / n, w['start'] + (w['end'] - w['start']) * (i + 1) / n))
STREAM = ''.join(c for c, _, _ in CH)

def find(s, after=0):
    """วลี (ตามที่พูดจริง) ที่เริ่มหลังวินาที after → (เริ่ม, จบ)"""
    k = norm(s); i = 0
    while True:
        i = STREAM.find(k, i)
        if i < 0: sys.exit(f'❌ หาไม่เจอหลัง {after}: {s}')
        if CH[i][1] >= after - 0.05: return CH[i][1], CH[i + len(k) - 1][2]
        i += 1

q = lambda t: round(round(t * FPS) / FPS, 4)
# ระดับเสียง Draft1 ทุก 10 ms -> เลื่อนจุดตัดให้ตกช่องเงียบจริง (pad คงที่ -0.06/+0.10 ไม่พอ: เวลาเริ่มคำจาก Scribe ช้ากว่าเสียงจริง ~0.1 วิ
# -> "HR" ตอนเริ่ม / หางคำ "พอ ๆ กัน" ขาด · ทีมจับได้ C5395 Draft2)
import subprocess, shutil, numpy as np
_b = subprocess.run([shutil.which('ffmpeg') or 'ffmpeg', '-nostdin', '-v', 'error', '-i', C['draft1'], '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
_x = np.frombuffer(_b, np.int16).astype(np.float32) / 32768; _x = _x[:len(_x) // 160 * 160].reshape(-1, 160)
ENV = 20 * np.log10(np.sqrt((_x ** 2).mean(1)) + 1e-9); QUIET = max(-57.0, float(np.percentile(ENV, 5)) + 12)
def loud(a, b):
    i, j = max(0, int(a * 100)), max(int(a * 100) + 1, int(b * 100)); return j <= len(ENV) and float(ENV[i:j].max()) >= QUIET
def snap_in(a, mx=.3):                             # มีเสียงก่อนจุดเริ่ม -> ถอยจนเงียบ (ไม่เกิน mx)
    t = a
    while t > a - mx and loud(t - .04, t): t -= .01
    return max(0, t - .02) if t > a - mx else a
def snap_out(b, mx=.3):                            # มีเสียงหลังจุดจบ -> ยืดจนเงียบ
    t = b
    while t < b + mx and loud(t, t + .04): t += .01
    return t + .02 if t < b + mx else b
SEGS = []; at = 0
for i, (p0, a0, p1, a1) in enumerate(plan.KEEP):
    a = 0.0 if p0 is None else snap_in(max(0, find(p0, a0)[0] - 0.06))
    b = END if p1 is None else min(END, snap_out(find(p1, a1)[1] + 0.10))
    s = dict(id=chr(65 + i), a=q(a), b=q(b), at=round(at, 4)); SEGS.append(s); at += s['b'] - s['a']
TOTAL = round(at, 4)

def tl(x, seg):
    return round(seg['at'] + min(max(x, seg['a']), seg['b']) - seg['a'], 3)
def seg_of(a, b):
    """ชิ้นที่ช่วง [a,b] ของ Draft1 อยู่มากที่สุด → (ชิ้น, สัดส่วนที่อยู่)"""
    best = max(SEGS, key=lambda s: min(b, s['b']) - max(a, s['a']))
    return best, max(0, min(b, best['b']) - max(a, best['a'])) / max(b - a, 0.01)
def in_broll(a, b):
    return any(min(b, y) - max(a, x) > 0.15 * (b - a) for x, y in BR)

COVER = dict(t1=plan.COVER[0], t2=plan.COVER[1], at=0.0, dur=round(min(SEGS[0]['b'] - SEGS[0]['a'], plan.COVER_MAX), 3))
SUPERS = []
for text, p0, a0, p1, a1 in plan.SUPERS:
    a = find(p0, a0)[0] - 0.05; b = find(p1, a1)[0] - 0.05; s, _ = seg_of(a, b)
    SUPERS.append(dict(text=text, at=tl(a, s), dur=round(b - a, 3), d1=[round(a, 2), round(b, 2)]))

# ===== ซับ =====
def ts(s):
    h, m, r = s.strip().replace(',', '.').split(':'); return int(h) * 3600 + int(m) * 60 + float(r)
caps = []
for blk in open(C['srt'], encoding='utf-8-sig').read().replace('\r', '').strip().split('\n\n'):
    ln = blk.split('\n'); s_, e_ = ln[1].split(' --> ')
    caps.append([ts(s_), ts(e_), ' '.join(ln[2:]).strip(), None])
for a, b, lines in plan.REWRITE:                  # เขียนใหม่ทั้งช่วง (เวลาจาก Scribe)
    caps = [c for c in caps if not (a - 0.05 <= c[0] < b)]
    cur = a
    for txt, say in lines:
        x, y = find(say, cur); caps.append([x - 0.02, y, txt, say]); cur = y
caps.sort(key=lambda c: c[0])
clean = []
for i, (a, b, txt, say) in enumerate(caps):
    txt = re.sub(r'คำถามคือ\s*', '', txt)
    txt = re.sub(r'\s*(อ่ะ|น่ะ)', '', txt)                     # ตัด อ่ะ น่ะ ทุกที่ในซับ (รีฟ) — เสียงคงไว้
    for o, n in plan.FIX: txt = txt.replace(o, n)
    txt = re.sub(r'\s*ๆ\s*', ' ๆ ', txt); txt = re.sub(r'\s+', ' ', txt).strip()
    if not txt: continue
    if i + 1 < len(caps) and caps[i + 1][0] - b < 0.6: b = caps[i + 1][0] - 0.02   # ต่อเนื่องถึงบรรทัดถัดไป
    clean.append((a, b, txt))
out = []
hide = [(0, COVER['dur'])] + [(s['at'], s['at'] + s['dur']) for s in SUPERS]
for a, b, txt in clean:
    s, frac = seg_of(a, b)
    if frac < 0.5 or in_broll(max(a, s['a']), min(b, s['b'])): continue
    x, y = tl(a, s), tl(b, s)
    for h0, h1 in hide:                            # ไม่ทับปก/Super
        if x < h1 and y > h0:
            if x >= h0: x = h1 + 0.03
            else: y = h0 - 0.05
    if y - x >= 0.3: out.append(dict(text=txt, at=round(x, 3), end=round(y, 3)))

def srt_time(x):
    ms = round(x * 1000); return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'
with open(f"{P}/renders/{C['name']}.srt", 'w', encoding='utf-8') as f:
    for i, c in enumerate(out, 1): f.write(f"{i}\n{srt_time(c['at'])} --> {srt_time(c['end'])}\n{c['text']}\n\n")
json.dump(dict(fps=FPS, total=TOTAL, segs=SEGS, broll=BR, cover=COVER, supers=SUPERS, caps=out, patches=plan.PATCHES),
          open(f'{HERE}/edl.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# ===== รายงาน + คำเตือน =====
for s in SEGS: print(f"{s['id']} Draft1 {s['a']:6.2f}–{s['b']:6.2f} → ใหม่ {s['at']:6.2f}")
print(f"ยาวรวม {TOTAL:.2f} วิ · ปก 0–{COVER['dur']} · B-roll ใน Draft1 {BR}")
for s in SUPERS: print(f"Super {s['text']} {s['at']} +{s['dur']}")
try:
    from PIL import ImageFont
    F = ImageFont.truetype(os.path.expanduser('~/Library/Fonts/IBMPlexSansThai-SemiBold.ttf'), 60)
except Exception: F = None
for i, c in enumerate(out):
    warn = ''
    if F and F.getlength(c['text']) > 870: warn += ' ⚠️ยาวเกินจอ (เกิน ~920px)'
    if i + 1 < len(out) and re.search(r'[A-Za-z]$', c['text']) and re.match(r'[A-Za-z]', out[i + 1]['text']) and out[i + 1]['at'] - c['end'] < 0.1:
        warn += ' ⚠️คำอังกฤษอาจโดนแยกบรรทัด'
    print(f"{c['at']:6.2f}–{c['end']:6.2f} {c['text']}{warn}")
