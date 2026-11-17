#!/usr/bin/env python3
"""base-motion-blueprint — คลิปพูดแนวตั้ง → Hook เขียนสด + Super ลายมือพู่กัน + ฉากวาดบนกระดาษเขียนแบบ + ตัดขนาดภาพ
ชั้น: กล้อง (#cam = ภาพคนพูดเต็มจอ เกลี่ยสีแล้ว) → เงากรมท่าด้านบน (ตอนมีตัวหนังสือ) → แผ่นกระดาษเขียนแบบ (ตอนวาด) → ลายมือ → ซับบนสุด
สี: บนภาพจริง (พื้นเข้ม) = ส้ม + ขาว · บนกระดาษ = ส้ม + กรมท่า (บรีฟ MAYTWIN หน้า 15)
ต้นแบบในไฟล์นี้ = คลิป "Gen Z vs Gen Y" 16 วิแรก (ผ่านผู้ใช้ 10 พ.ย. 2026) · คลิปใหม่: แก้ "ตั้งค่าต่อคลิป" + เขียน A/B ใหม่ทั้งหมด
รัน: python gen.py → index.html + assets/mix.wav แล้ว render"""
import math, os, random, re, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, 'work'); from align import at

# ===== ตั้งค่าต่อคลิป =====
TOTAL = 15.95                    # ความยาว (วินาที) — new_blueprint.py พิมพ์ค่าให้
TALK = 'assets/talk.mp4'         # คลิปที่ตัดแล้ว (เอาเสียง)
GRADED = 'assets/talk_hi.mp4'    # ภาพคนพูดเกลี่ยสีแล้ว (1620×2880 ถ้ามีไฟล์ดิบ 4K · ไม่งั้น 1080×1920)
FACE = '50% 40%'                 # จุดศูนย์กลางซูม = หน้าคนพูด (x% y% ของเฟรม) — ดึงเฟรมดูก่อน
SHIFT = 480                      # ตอนแผ่นกระดาษลงมา ภาพคนลงไปอยู่ใต้แผ่น (px)
SUBS = 'work/subs.srt'           # ซับบรรทัดเดียว (จาก base-rough-cut หรือทีม) · None = ใช้ CAPS ด้านล่าง
WIDE, MED, CLOSE = 1.0, 1.25, 1.5   # ขนาดภาพ · ถ้า GRADED เป็น 1080 (ไม่มีไฟล์ดิบ) ให้ CLOSE ≤ 1.25 ไม่งั้นภาพแตก

EMBER, NAVY, WHITE = '#ff3608', '#0d1b2a', '#ffffff'
js, html, SFX = [], [], []
def r(x): return round(x, 3)
def tw(s): js.append(s)
def fx(t, kind, vol=None):
    v = {'swoosh': 0.32, 'click': 0.5, 'thump': 0.6, 'pen': 0.35}[kind] if vol is None else vol
    SFX.append((r(max(0, t)), kind, v))
def wiggle(id, t0, t1, rot=0, a=0.6):
    """ตัวหนังสือสั่นเล็กน้อยแบบลายมือ ~12 fps (ตัวหนังสือเท่านั้น — กล้องห้ามสั่น)"""
    t = t0; i = 0
    while t < t1:
        tw(f"tl.set('#{id}',{{rotation:{rot + (a if i % 2 else -a)}}},{r(t)});"); t += 1 / 12; i += 1

# ---------- ชิ้นส่วน ----------
def word(id, text, x, y, cls, color, rot=0):
    """ตัวหนังสือลายมือพู่กัน (Sriracha + ฟิลเตอร์ #mt) · cls = hk1/hk2 (Hook) · sup (Super) · lab (ป้ายในฉากวาด) · x=0 → กึ่งกลางจอ"""
    tw(f"tl.set('#{id}',{{rotation:{rot},skewX:-4}},0);")
    if x == 0:
        return f'<div class="row" style="top:{y}px"><div class="wo {cls}" id="{id}" style="color:{color}">{text}</div></div>'
    return f'<div class="wo {cls}" id="{id}" style="left:{x}px;top:{y}px;color:{color}">{text}</div>'
def pen(id, x, y, w, h, d, color, sw=6, z=8):
    """เส้นปากกาเทคนิค (บาง คม เส้นเดียว) — ภาพเขียนแบบ: กล่อง ลูกศรตรง เส้นบอกระยะ ไอคอนเส้น"""
    return (f'<svg class="ink" id="{id}" style="left:{x}px;top:{y}px;z-index:{z};opacity:0" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')
def _jit(d, amt, seed):
    R = random.Random(seed)
    return re.sub(r'-?\d+(?:\.\d+)?', lambda m: f'{float(m.group()) + R.uniform(-amt, amt):.1f}', d)
def marker(id, x, y, w, h, d, color, sw=10, passes=3, z=9, jit=None):
    """ปากกาเมจิกวาดมือ (แนว Hand Drawings): ลากซ้ำ 3 รอบ หนา→บาง เหลื่อมนิด + ฟิลเตอร์ #mk ขอบสาก หมึกแห้ง — วงล้อม เส้นใต้ ขีดหยัก"""
    jit = sw * 0.9 if jit is None else jit; s = sum(map(ord, id))
    paths = ''.join(
        f'<path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="{d if k == 0 else _jit(d, jit, s + k)}" fill="none" stroke="{color}" '
        f'stroke-width="{sw * (1, .55, .38)[k]:.1f}" opacity="{(1, .9, .8)[k]}" stroke-linecap="round" stroke-linejoin="round"/>' for k in range(passes))
    return (f'<svg class="ink" id="{id}" style="left:{x}px;top:{y}px;z-index:{z};opacity:0" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<g filter="url(#mk)">{paths}</g></svg>')
def loop2(cx, cy, rx, ry, pad=24):
    """วงล้อมวน ~1.3 รอบ ปลายเลยจุดเริ่ม · คืน (x, y, w, h, d) ให้ marker(id, *loop2(...), สี)"""
    w, h = 2 * (rx + pad), 2 * (ry + pad); c, m = rx + pad, ry + pad; pts = []
    for i in range(61):
        a = -2.2 + i / 60 * 2 * math.pi * 1.3; k = 1 + 0.05 * math.sin(i / 9) + (0.06 if i > 45 else 0)
        pts.append((c + rx * k * math.cos(a), m + ry * k * math.sin(a) - (i / 60) * ry * 0.12))
    return cx - c, cy - m, w, h, 'M' + ' L'.join(f'{px:.1f} {py:.1f}' for px, py in pts)
SCRIB = 'M10 30 C110 20 260 34 {w} 24 M{w2} 38 C200 30 90 44 30 40'   # เส้นใต้ลากไป-กลับ (.format(w=กว้าง, w2=กว้าง-40))
WAVE = 'M10 40 C30 10 45 10 55 35 C65 60 80 60 90 30 C100 5 115 5 125 32 C135 58 150 58 160 30 C170 8 185 8 195 34 C205 56 220 50 240 30'   # ขีดหยัก

# ---------- ท่า (เร็ว คม 6–10 เฟรม · มีเสียงทุกชิ้น) ----------
def write(id, t, d=0.28, s='pen'):
    """ตัวหนังสือถูกเขียน: mask วิ่งซ้าย→ขวา (เผื่อขอบ 20% ไม่งั้นตัวเอียง/ขอบพู่กันโดนตัด — ผู้ใช้ติมาแล้ว)"""
    tw(f"tl.fromTo('#{id}',{{opacity:1,clipPath:'inset(-40% 120% -40% -20%)'}},{{opacity:1,clipPath:'inset(-40% -20% -40% -20%)',duration:{d},ease:'power2.out'}},{r(t)});")
    if s: fx(t, s)
def punch(id, t, s='click'):
    """ขึ้นแล้วกระแทกเข้าที่ 110% → 100% (ขยับตัวหนังสือ/ชิ้นกราฟิก ไม่ใช่กล้อง)"""
    tw(f"tl.fromTo('#{id}',{{scale:1.1}},{{scale:1,duration:0.16,ease:'power4.out'}},{r(t)});")
    if s: fx(t, s)
def draw(id, t, d=0.25, s='pen'):
    tw(f"tl.set('#{id}',{{opacity:1}},{r(t)});")   # ซ่อนจนถึงเวลาวาด (ปลายเส้นมนจะเป็นจุดค้างถ้าไม่ซ่อน)
    tw(f"tl.fromTo('#{id} path',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{d},ease:'power2.out',stagger:0.06}},{r(t)});")
    if s: fx(t, s)
def gone(ids, t, s='swoosh'):
    tw(f"tl.to([{','.join(repr('#' + i) for i in ids)}],{{x:-1200,duration:0.22,ease:'power3.in',stagger:0.02}},{r(t)});")
    if s: fx(t, s)
def shade(t, on=True):
    """เงากรมท่าด้านบน ให้ตัวหนังสือขาว/ส้มอ่านง่ายบนภาพจริง"""
    tw(f"tl.to('#shade',{{opacity:{1 if on else 0},duration:0.15}},{r(t)});")
def cut(t, s, sfx='click', vol=0.3, y=0):
    """ท่ากล้องมีอย่างเดียว: ตัดขนาดภาพทันที (กว้าง/กลาง/ใกล้) + เสียงสั้นตรงเฟรม · ห้ามสั่น ห้ามซูม/ดันกล้องเคลื่อน (ผู้ใช้สั่ง)"""
    tw(f"tl.set('#cam',{{scale:{s},y:{y}}},{r(t)});")
    if sfx: fx(t, sfx, vol)
def sup(id, text, t0, t1, color, under, wave=False):
    """Super: 1 ประเด็น = 1 keyword · สลับ ส้ม → ขาว บนภาพจริง · เส้นใต้สีตรงข้าม"""
    html.append(word(id, text, 0, 300, 'sup', color, -2) + (marker(id + 'u', 400, 540, 260, 70, WAVE, under, 11) if wave
                else marker(id + 'u', 290, 540, 520, 70, SCRIB.format(w=500, w2=460), under, 11)))
    shade(t0 - 0.05); write(id, t0, 0.24); punch(id, t0, 'click'); draw(id + 'u', t0 + 0.3, 0.2)
    wiggle(id, t0 + 0.3, t1 - 0.2, -2)
    gone([id, id + 'u'], t1 - 0.2, None); shade(t1 - 0.05, False)

# ===== A · HOOK (0–3 วิ): ภาพ + ข้อความ + เสียง พร้อมกัน =====  ← ตัวอย่างคลิป Gen Z · แทนด้วยของคลิปนี้
cut(0, CLOSE, 'swoosh', 0.45); cut(0.5, WIDE)   # Visual Hook: เปิดช็อตใกล้ → ตัดกว้าง
shade(0)
html.append(word('h1', '<span class="k1">Gen Z</span> กับ Gen Y', 0, 210, 'hk1', WHITE, -2) + word('h2', 'ใครผิด?', 0, 340, 'hk2', WHITE, -2)
            + marker('h3', *loop2(262, 294, 178, 76), EMBER, 10)                              # keyword #1 = วงส้ม
            + marker('h4', 320, 535, 460, 70, SCRIB.format(w=440, w2=400), WHITE, 11))         # keyword #2 = เส้นใต้
write('h1', 0.3, 0.3); write('h2', 0.9, 0.24)
draw('h3', 1.6, 0.3, 'click'); cut(1.6, MED, None); tw(f"tl.to('#h1 .k1',{{color:'{EMBER}',duration:0.01}},{r(1.6)});")
draw('h4', 2.3, 0.2)
wiggle('h1', 0.6, 3.0, -2); wiggle('h2', 1.15, 3.0, -2)
gone(['h1', 'h2', 'h3', 'h4'], 3.0); shade(3.1, False)
cut(at('เรื่องของการ'), CLOSE)                  # ต้นประโยคใหม่ → ใกล้

# ===== B3 · ANIMATION บนแผ่นกระดาษเขียนแบบ (เปรียบเทียบ = แบ่ง 2 ฝั่ง) =====  ← ตัวอย่าง
a = at('คนนึงอยาก'); b = at('แล้วก็หาว่า')
html.append(
    '<div id="sheet"><div class="paper"></div>'
    + pen('c0', 538, 170, 6, 600, 'M3 0 L3 600', NAVY, 3, 5)
    + word('c1', 'GEN Y', 150, 180, 'lab', NAVY) + word('c2', 'GEN Z', 640, 180, 'lab', EMBER)
    + pen('c3', 110, 330, 380, 300, 'M20 20 H360 V220 H20 Z M150 220 L130 280 M230 220 L250 280 M100 282 H280', NAVY, 6, 6)
    + pen('c4', 175, 375, 150, 130, 'M10 10 H110 L140 40 V125 H10 Z M110 10 V40 H140 M30 60 H110 M30 82 H120 M30 104 H90', NAVY, 4, 7)
    + pen('c5', 110, 660, 380, 50, 'M20 25 H360 M20 8 V42 M360 8 V42 M20 25 L40 15 M20 25 L40 35 M360 25 L340 15 M360 25 L340 35', NAVY, 3, 6)
    + pen('c6', 640, 320, 300, 380, 'M40 20 H260 Q280 20 280 40 V340 Q280 360 260 360 H40 Q20 360 20 340 V40 Q20 20 40 20 Z M140 340 H160', NAVY, 6, 6)
    + pen('c7', 860, 300, 120, 300, 'M90 20 L30 260 L22 290 L44 268 L104 28 Z', NAVY, 4, 7)
    + marker('c8', *loop2(800, 505, 185, 215), EMBER, 10)
    + '</div>')
tw(f"tl.fromTo('#sheet',{{opacity:1,y:-1000}},{{opacity:1,y:0,duration:0.3,ease:'power3.out'}},{r(a - 0.05)});"); fx(a - 0.05, 'swoosh', 0.4)
cut(a - 0.05, WIDE, None, y=SHIFT)              # ภาพคนอยู่ใต้แผ่น (ตัดทันที ไม่เลื่อน)
draw('c0', a + 0.1, 0.25, None); write('c1', a + 0.2, 0.22)
draw('c4', at('Microsoft'), 0.3); punch('c4', at('Microsoft'), None)
draw('c3', at('อยากให้ใช้คอม') + 0.3, 0.3); draw('c5', at('อยากให้ใช้คอม') + 0.6, 0.2, None)
write('c2', at('แต่Gen'), 0.22)
draw('c6', at('iPad'), 0.28); draw('c7', at('iPad') + 0.25, 0.2, None)
draw('c8', at('iPad') + 0.5, 0.3, 'click'); fx(at('iPad') + 0.5, 'thump', 0.4)
tw(f"tl.to('#sheet',{{y:-1050,duration:0.25,ease:'power3.in'}},{r(b - 0.15)});"); fx(b - 0.15, 'swoosh', 0.4)
cut(b + 0.1, MED, None)

# ===== B2 · SUPER + ตัดขนาดภาพตามจังหวะพูด =====  ← ตัวอย่าง
sup('s1', 'หัวโบราณ', at('หัวโบราณ'), at('แล้วกลายเป็น'), EMBER, WHITE, wave=True)
cut(at('หัวโบราณ'), CLOSE, None)                # คำแรง → ใกล้
cut(at('แล้วกลายเป็น'), WIDE)                    # ประโยคใหม่ → กว้าง
cut(at('ดราม่า'), MED, 'thump', 0.45)             # คำหนัก → กลาง + เสียงหนัก
cut(at('แล้วพี่คิด'), CLOSE)                      # คำถามชวนคิด → ใกล้
cut(at('พี่ว่าจริง'), WIDE)                       # คำตอบ → กว้าง
cut(at('มันไม่ได้มี'), MED)
sup('s2', 'ไม่มีใครผิด', at('มีใครผิด'), TOTAL + 0.3, WHITE, EMBER)

# ===== B1 · SUBTITLE: บรรทัดเดียว · แถบกรมท่า Anuphan · ตำแหน่งเดิม · บนสุดเสมอ · ตัด ป่ะ อ่ะ น่ะ ทิ้ง (ผู้ใช้สั่ง) =====
PARTICLE = re.compile(r'(ป่ะ|อ่ะ|น่ะ)')   # ภาษาไทยไม่เว้นวรรค คำลงท้ายมักติดคำถัดไป ("อันนี้ป่ะบน") → ตัดทุกตำแหน่ง
def clean(t): return re.sub(r'\s+', ' ', PARTICLE.sub('', t)).strip()
MAXC = 28   # ตัวที่กินความกว้างจริง (ไม่นับสระบน/ล่าง วรรณยุกต์ ซึ่งไม่กินที่)
THMARK = re.compile('[ัิ-ฺ็-๎]')
def vis(t): return len(THMARK.sub('', t))
def split1(s_, e_, txt):
    """บรรทัดยาวเกิน → แบ่งเป็นซับบรรทัดเดียว 2 ชิ้นต่อกัน (ตัดที่ช่องว่างใกล้กลางที่สุด · เวลาแบ่งตามจำนวนตัวอักษร)"""
    if vis(txt) <= MAXC or ' ' not in txt: return [(s_, e_, txt)]
    sp = [i for i, c in enumerate(txt) if c == ' ']; k = min(sp, key=lambda i: abs(i - len(txt) / 2))
    a, b = txt[:k].strip(), txt[k:].strip(); m = s_ + (e_ - s_) * len(a) / (len(a) + len(b))
    return split1(s_, m, a) + split1(m, e_, b)
def ts(x): h, m, s_ = x.replace(',', '.').split(':'); return int(h) * 3600 + int(m) * 60 + float(s_)
caps = []
if SUBS and os.path.exists(SUBS):
    for blk in open(SUBS, encoding='utf-8-sig').read().replace('\r', '').strip().split('\n\n'):
        ln = blk.split('\n'); s_, e_ = ln[1].split(' --> '); txt = clean(' '.join(ln[2:]))
        if txt: caps += split1(ts(s_), ts(e_), txt)
else:   # ตัวอย่าง: แบ่งเอง (ข้อความ, วลีที่ใช้หาเวลาเริ่ม)
    CAPS = [('เห็นเทรนด์อันนี้บ้างบน Twitter อ่ะ', 'เห็นเทรนด์'), ('ที่ Gen Z กับ Gen Y มันตีกัน', 'ที่Gen'),
            ('เรื่องของการใช้เครื่องมืออ่ะ', 'เรื่องของการ'), ('คนนึงอยากให้ใช้ Microsoft Word', 'คนนึงอยาก'),
            ('อยากให้ใช้คอม', 'อยากให้ใช้คอม'), ('แต่ Gen Z บอกว่าปัจจุบันนี้', 'แต่Gen'), ('เขาไม่ใช้กันแล้ว', 'เขาไม่ใช้'),
            ('เขาใช้กันแต่ iPad', 'เขาใช้กันแต่'), ('ใช้กันแต่เครื่องมือแบบนั้น', 'ใช้กันแต่เครื่อง'), ('แล้วก็หาว่าหัวโบราณ', 'แล้วก็หาว่า'),
            ('แล้วกลายเป็นดราม่าใหญ่โตเลย', 'แล้วกลายเป็น'), ('แล้วพี่คิดว่าเคสนี้ใครผิด', 'แล้วพี่คิด'),
            ('พี่ว่าจริง ๆ', 'พี่ว่าจริง'), ('มันไม่ได้มีใครผิดเลยเว้ย', 'มันไม่ได้มี')]
    T = [max(0, at(p) - 0.05) for _, p in CAPS] + [TOTAL]
    caps = [(T[i], T[i + 1], clean(t)) for i, (t, _) in enumerate(CAPS)]
subs = ''
for i, (s_, e_, txt) in enumerate(caps):
    if vis(txt) > MAXC + 2: print(f'⚠ ซับยาว {vis(txt)} ตัว ไม่มีช่องว่างให้แบ่ง (บรรทัดเดียวเท่านั้น · แบ่งเองใน .srt): {txt}')
    subs += f'<div class="sub" id="sb{i}"><span>{txt}</span></div>'
    tw(f"tl.fromTo('#sb{i}',{{opacity:0}},{{opacity:1,duration:0.01}},{r(s_)});"); tw(f"tl.set('#sb{i}',{{opacity:0}},{r(e_)});")

# ===== เขียนไฟล์ =====
FF = shutil.which('ffmpeg') or 'ffmpeg'
if not os.path.exists(GRADED):   # ไม่มีไฟล์ดิบ: เกลี่ยสีจากคลิป 1080 (ยกเงา สว่างขึ้น อุ่นนิด)
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', TALK, '-an', '-vf',
                    "curves=all='0/0.03 0.25/0.37 0.5/0.63 0.75/0.84 1/1',colorbalance=rs=0.03:bs=-0.03:rm=0.02:bm=-0.02,eq=saturation=1.06",
                    '-c:v', 'libx264', '-crf', '16', '-pix_fmt', 'yuv420p', '-y', GRADED], check=True)
doc = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{open('style.css', encoding='utf-8').read()}
#cam {{ transform-origin: {FACE}; }}
</style></head>
<body>
  <svg width="0" height="0" style="position:absolute"><defs>
    <filter id="mk" filterUnits="userSpaceOnUse" x="-3000" y="-3000" width="8000" height="8000">
      <!-- ปากกาเมจิก: ขอบสาก + หมึกแห้งเป็นช่อง -->
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="4" result="n"/>
      <feDisplacementMap in="SourceGraphic" in2="n" scale="5" xChannelSelector="R" yChannelSelector="G" result="d"/>
      <feTurbulence type="fractalNoise" baseFrequency="1.7" numOctaves="1" seed="9" result="n2"/>
      <feColorMatrix in="n2" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -3 2.3" result="m"/>
      <feComposite in="d" in2="m" operator="in"/>
    </filter>
    <filter id="mt" filterUnits="userSpaceOnUse" x="-3000" y="-3000" width="8000" height="8000">
      <!-- ตัวหนังสือพู่กัน (ผ่านผู้ใช้): เนื้อหมึกทึบหนา → ขอบหยักคม (ห้ามขุยฟุ้ง) → ริ้วหมึกแห้งบาง ๆ ห่าง ๆ → ขอบคม
           ⚠ ริ้วถี่กว่านี้ ตัวไทยขาดจนอ่านไม่ออก (ผู้ใช้ติ "อ่านยาก") -->
      <feMorphology in="SourceGraphic" operator="dilate" radius="2.2" result="b"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.07" numOctaves="2" seed="3" result="n1"/>
      <feDisplacementMap in="b" in2="n1" scale="7" xChannelSelector="R" yChannelSelector="G" result="d"/>
      <feTurbulence type="fractalNoise" baseFrequency="0.006 0.32" numOctaves="2" seed="8" result="s"/>
      <feColorMatrix in="s" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -16 12.4" result="m"/>
      <feComposite in="d" in2="m" operator="in" result="g"/>
      <feComponentTransfer in="g"><feFuncA type="linear" slope="3" intercept="-0.9"/></feComponentTransfer>
    </filter></defs></svg>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
    <div id="stage">
      <div id="cam"><video id="talk" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-media-start="0" muted playsinline src="{GRADED}"></video></div>
      <div id="shade"></div>
      <div class="gfx">{''.join(html)}</div>
    </div>
    <div id="subs">{subs}</div>
    <audio id="voice" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-volume="1" src="assets/mix.wav"></audio>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join('    ' + l for l in js)}
    tl.set({{}}, {{}}, {TOTAL});
    window.__timelines["main"] = tl;
  </script>
</body></html>'''
open('index.html', 'w', encoding='utf-8').write(doc)

# เสียง: เสียงพูด loudnorm −14 + SFX ตรงเฟรม (เบากว่าเสียงพูด) · ไม่มีเพลง · ไม่ตัดเสียงพูด
if not os.path.exists('assets/voice.wav'):
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', TALK, '-vn', '-t', str(TOTAL), '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', '-y', 'assets/voice.wav'], check=True)
FILES = {'swoosh': 'assets/sfx/swoosh.mp3', 'click': 'assets/sfx/click.mp3', 'thump': 'assets/sfx/thump.wav', 'pen': 'assets/sfx/pen.wav'}
cmd = [FF, '-nostdin', '-v', 'error', '-i', 'assets/voice.wav']; fl = ['[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v]']; lab = ['[v]']
for k, (tm, kind, vol) in enumerate(SFX, 1):
    cmd += ['-i', FILES[kind]]; ms = int(tm * 1000)
    fl.append(f'[{k}:a]volume={vol},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{k}]'); lab.append(f'[s{k}]')
fl.append(''.join(lab) + f'amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{TOTAL},alimiter=limit=0.8:level=false[out]')
subprocess.run(cmd + ['-filter_complex', ';'.join(fl), '-map', '[out]', '-ar', '48000', '-ac', '2', '-y', 'assets/mix.wav'], check=True)
print('tweens', len(js), '· sfx', len(SFX), '· subs', len(caps))
