#!/usr/bin/env python3
"""base-motion-collage — B-roll collage (MP Ci) แทรกเฉพาะตอนยกตัวอย่าง/เปรียบเทียบ · ที่เหลือเป็นคลิปเดิม (หน้าคนพูด + ซับของทีม)
รัน: python gen.py → index.html (= "ม้วน B-roll" ต่อกันเฉพาะช่วงที่ขึ้นภาพ) + work/segs.json + work/sfx.json
แล้ว render ม้วนนี้ (สั้นกว่าทั้งคลิปมาก) → python work/compose.py วางทับ assets/talk.mp4 ตามเวลาจริง
ต้นแบบในไฟล์นี้ = คลิป "Gen Z vs Gen Y" (Tiktok 031026 คลิป 3) · คลิปใหม่: แก้ "ตั้งค่าต่อคลิป" + เขียน "ช่วง B-roll" ใหม่"""
import json, os, random, shutil, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, 'work'); from align import at

# ===== ตั้งค่าต่อคลิป =====
TOTAL = 65.4                     # ความยาวคลิป (วินาที)
FACE_CROP = '1000:1000:80:150'   # crop หน้าคนพูดสำหรับวงกลม (w:h:x:y บนเฟรม 1080×1920) · ตัดกว้างให้หัวกิน ~ครึ่งวง เหลือที่เหนือหัว (คนพูดขยับแล้วไม่ตกขอบ)
COVER = None                     # คลิปยังไม่มีปก → ('บรรทัดใหญ่', 'บรรทัดรองสีส้ม') · มีปกเบิร์นมาแล้ว → None

js = []; html = []; SFX = []; ROT = {}; SEGS = []; USED = {}
OFF = 0.0; T0 = 0.0              # ช่วงที่กำลังเขียน: OFF = เวลาบนม้วน · T0 = เวลาบนคลิปจริง
def rt(t): return round(OFF + (t - T0), 3)          # เวลาคลิปจริง → เวลาบนม้วน
def tw(s): js.append(s)
def fx(t, kind, vol=None):                           # t = เวลาคลิปจริง
    v = {'swoosh': 0.30, 'click': 0.45, 'thump': 0.70, 'pen': 0.30}[kind] if vol is None else vol
    SFX.append((round(max(0, t), 3), kind, v))

# ---------- ชิ้นส่วน (พิกัดบนเฟรม 1080×1920 · การ์ดอยู่ x 95–985 · y 250–1500 · วงกลมหน้า y 1270–1700) ----------
FILL = {'s-paper': '#faf7f0', 's-navy': '#0d1b2a', 's-ember': '#ff3608', 's-cream': '#efe6d6'}
def edge(seed, fill, top):
    """ขอบกระดาษฉีก = SVG หยักแปะบน/ล่างแถบ (ห้ามใช้ clip-path: เยอะ ๆ HyperFrames จับภาพเป็นจอดำ)"""
    R = random.Random(seed); xs = range(0, 101, 4); ys = [R.uniform(1, 9) for _ in xs]
    poly = ('0,10 ' + ' '.join(f'{x},{y:.1f}' for x, y in zip(xs, ys)) + ' 100,10') if top else \
           ('0,0 ' + ' '.join(f'{x},{10 - y:.1f}' for x, y in zip(xs, ys)) + ' 100,0')
    return (f'<svg class="edge" style="{"top" if top else "bottom"}:-9px" viewBox="0 0 100 10" preserveAspectRatio="none">'
            f'<polygon points="{poly}" fill="{fill}"/></svg>')
def strip(id, text, x, y, kind='s-paper', cls='mid', rot=0, z=6):
    """แถบกระดาษฉีกมีข้อความ · kind = s-paper/s-navy/s-ember/s-cream · cls = big/mid/sml/thb/thm/ths (ไทยเติม ' th')"""
    ROT[id] = rot; s = sum(map(ord, id)) * 7
    return (f'<div class="shadow" id="{id}" style="left:{x}px;top:{y}px;z-index:{z}">'
            f'<div class="strip {kind} {cls}">{edge(s, FILL[kind], True)}{text}{edge(s + 1, FILL[kind], False)}</div></div>')
def piece(id, src, x, y, w, rot=0, z=4):
    """ภาพกระดาษตัด assets/cut/*.png · ใช้ไฟล์ซ้ำได้ (ก๊อปเป็นชื่อใหม่ให้เอง · ห้ามต่อท้าย ?n= ตอนเรนเดอร์ภาพไม่ขึ้น)"""
    ROT[id] = rot; USED[src] = USED.get(src, 0) + 1
    if USED[src] > 1:
        b, e = os.path.splitext(src); dup = f'{b}-{USED[src]}{e}'; shutil.copy(f'assets/cut/{src}', f'assets/cut/{dup}'); src = dup
    return f'<img class="pc" id="{id}" src="assets/cut/{src}" style="left:{x}px;top:{y}px;width:{w}px;z-index:{z}">'
def tape(id, x, y, rot=0):
    ROT[id] = rot; return f'<div class="tape" id="{id}" style="left:{x}px;top:{y}px;z-index:9"></div>'
def line(id, x, y, w, h, d, color='#ffffff', sw=9, z=8):
    """เส้นชอล์ก/หมึก SVG (ลูกศร ดาว ขีดฆ่า วงล้อม) · วาดด้วย draw()"""
    return (f'<svg class="ink" id="{id}" style="left:{x}px;top:{y}px;z-index:{z}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')
# ลายเส้นสำเร็จรูป (ขนาดกล่อง 200×200 · ขยายด้วย w/h)
ARROW_R = 'M10 100 C60 90 120 95 180 100 M150 70 L185 100 L150 130'
ARROW_DN = 'M100 10 C95 60 105 120 100 180 M70 150 L100 185 L130 150'
BURST = 'M100 20 L110 80 M150 40 L125 88 M180 100 L122 104 M150 160 L120 118 M50 160 L80 118 M20 100 L78 104 M50 40 L88 88'
STAR = 'M100 30 L112 88 L170 100 L112 112 L100 170 L88 112 L30 100 L88 88 Z'
CROSS = 'M30 30 L170 170 M170 30 L30 170'

# ---------- ท่าขยับ (เวลา = คลิปจริง · แปลงเป็นเวลาบนม้วนให้เอง) ----------
def slap(id, t, s='click', d=0.26):
    rot = ROT.get(id, 0)
    tw(f"tl.fromTo('#{id}',{{opacity:0,scale:1.35,rotation:{rot + 9}}},{{opacity:1,scale:1,rotation:{rot},duration:{d},ease:'back.out(2.2)'}},{rt(t)});")
    if s: fx(t, s)
def slide(id, t, dx=0, dy=0, s='swoosh', d=0.45):
    rot = ROT.get(id, 0)
    tw(f"tl.fromTo('#{id}',{{opacity:0,x:{dx},y:{dy},rotation:{rot - 8}}},{{opacity:1,x:0,y:0,rotation:{rot},duration:{d},ease:'power3.out'}},{rt(t)});")
    if s: fx(t, s)
def drop(id, t, s='thump'):
    rot = ROT.get(id, 0)
    tw(f"tl.fromTo('#{id}',{{opacity:0,y:-1100,rotation:{rot - 14}}},{{opacity:1,y:0,rotation:{rot},duration:0.5,ease:'bounce.out'}},{rt(t)});")
    if s: fx(t + 0.32, s)
def bump(id, t, k=1.12):
    tw(f"tl.to('#{id}',{{scale:{k},duration:0.12,yoyo:true,repeat:1,ease:'power2.out'}},{rt(t)});"); fx(t, 'click', 0.3)
def shake(id, t, n=6, a=14):
    """ค่าตายตัว (ไม่ใช้ +=) · เรียกหลังท่าเข้าจบเท่านั้น"""
    tw(f"tl.fromTo('#{id}',{{x:{-a}}},{{x:{a},duration:0.04,yoyo:true,repeat:{n},ease:'none',immediateRender:false}},{rt(t)});")
    tw(f"tl.set('#{id}',{{x:0}},{round(rt(t) + 0.04 * (n + 1) + 0.01, 3)});")
def away(id, t, dy=900, rot=25, d=0.5):
    tw(f"tl.to('#{id}',{{y:{dy},rotation:{rot},opacity:0,duration:{d},ease:'power2.in'}},{rt(t)});"); fx(t, 'swoosh', 0.25)
def dim(id, t, o=0.3): tw(f"tl.to('#{id}',{{opacity:{o},duration:0.25}},{rt(t)});")
def draw(id, t, d=0.4, s='pen'):
    tw(f"tl.fromTo('#{id} path',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{d},ease:'power2.inOut'}},{rt(t)});")
    if s: fx(t, s)
def boil(ids, t0, t1, step=0.25):
    """สั่นแบบ stop-motion ±0.8° ทุก 0.25 วิ ให้ภาพที่ค้างดูมีชีวิต"""
    for k, id in enumerate(ids):
        rot = ROT.get(id, 0); t = t0 + 0.6 + k * 0.07; i = 0
        while t < t1 - 0.25:
            tw(f"tl.set('#{id}',{{rotation:{rot + (0.8 if i % 2 else -0.8)}}},{rt(t)});"); t += step; i += 1

def broll(t0, t1, card, body):
    """เปิดช่วง B-roll t0–t1 (เวลาคลิปจริง · ใช้ at() เสมอ) · card = 'navy' หรือ 'ember' (สลับกันทีละช่วง)
    ภายในเรียก slap/slide/... ด้วยเวลาคลิปจริงได้เลย · ช่วงละ 3–7 วิ · เข้า 0.3 วิ ออก 0.25 วิ"""
    global OFF, T0
    OFF = round(sum(b - a for _, a, b in SEGS), 3); T0 = t0; n = len(SEGS) + 1; L = round(t1 - t0, 3)
    SEGS.append((n, round(t0, 3), round(t1, 3)))
    html.append(f'''<div class="seg" id="g{n}" data-layout-allow-overflow data-layout-allow-occlusion>
  <div class="card {card}" id="cd{n}"><div class="grain"></div></div>
  {body}
  <div class="face" id="fc{n}"><video id="cam{n}" class="clip" data-start="{OFF}" data-duration="{L}" data-track-index="{n + 1}" data-media-start="0" muted playsinline src="assets/cam{n}.mp4"></video></div>
</div>''')
    tw(f"tl.fromTo('#g{n}',{{opacity:1,y:1920}},{{opacity:1,y:0,duration:0.3,ease:'power3.out'}},{OFF});")
    tw(f"tl.to('#g{n}',{{y:-1920,duration:0.25,ease:'power2.in'}},{round(OFF + L - 0.25, 3)});")
    fx(t0, 'swoosh', 0.35)
    return n

# ===== B-roll ตัวเลข: เส้นกราฟวาดตัวเอง + ตัวเลขใหญ่นับตามปลายเส้น (ใช้ตอนคนพูดอ้างสถิติ/การเติบโต) =====
# ต้นแบบอนุมัติ 10 พ.ย. 2026 (F:\AI\test-animation-skills\collage-stat) · ไอเดียจากสกิล /graph ทำใหม่ในภาษาภาพ collage
STAT_INK = {'navy':  dict(line='#ffffff', tip='#ff3608', burst='#ff3608', grid='rgba(255,255,255,.16)', base='rgba(255,255,255,.55)', yr='rgba(255,255,255,.6)', lab='s-paper'),
            'ember': dict(line='#0d1b2a', tip='#0d1b2a', burst='#0d1b2a', grid='rgba(13,27,42,.22)',  base='rgba(13,27,42,.6)',    yr='rgba(13,27,42,.75)',  lab='s-paper')}
def stat(id, t0, t1, card, label, values, ticks=None, t_land=None, prefix='', suffix='', decimals=0, final=None, extra=''):
    """ช่วง B-roll ตัวเลข (เรียก broll() ให้เอง) · ตัวเลขต้องมาจากที่คนพูดอ้าง/มีที่มา — ห้ามแต่ง
    id = คำนำหน้า id (เช่น 's1') · label = หัวข้อสั้น (ไทย/อังกฤษ) · values = ค่าทุกจุด เก่า→ใหม่ (≥ 2 ค่า, ≥ 0)
    ticks = ป้ายใต้แกน (ปี/เดือน) ≤ 8 · t_land = เวลาที่เส้นแตะปลาย (ใส่ at('คำที่พูดตัวเลข')) ค่าเริ่ม = t0+3.5
    final = เลขที่นับไปจบ (ให้ values เป็นหน่วยย่อได้ เช่น values เป็นพัน final เป็นเต็ม) · extra = ชิ้น collage เพิ่ม"""
    k = STAT_INK[card]; V = [float(v) for v in values]; vmax = max(V) or 1; last = V[-1] or 1
    FIN = float(final) if final is not None else V[-1]; SC = FIN / last
    X0, X1, Y0, Y1 = 70, 800, 900, 600                      # พิกัดในการ์ด 890×1250 (วงกลมหน้าเริ่ม y 1020 ในการ์ด)
    px = lambda i: X0 + i * (X1 - X0) / (len(V) - 1); py = lambda v: Y0 - v / vmax * (Y0 - Y1)
    P = [(px(i), py(v)) for i, v in enumerate(V)]; d = f'M{P[0][0]:.1f},{P[0][1]:.1f}'
    for i in range(len(P) - 1):                              # Catmull-Rom → เส้นโค้งเนียนผ่านทุกจุด
        p0, p1, p2, p3 = P[max(0, i - 1)], P[i], P[i + 1], P[min(len(P) - 1, i + 2)]; c = 0.5 / 3
        d += (f' C{p1[0] + (p2[0] - p0[0]) * c:.1f},{p1[1] + (p2[1] - p0[1]) * c:.1f}'
              f' {p2[0] - (p3[0] - p1[0]) * c:.1f},{p2[1] - (p3[1] - p1[1]) * c:.1f} {p2[0]:.1f},{p2[1]:.1f}')
    fmt = lambda x: f'{prefix}{x:,.{decimals}f}{suffix}'
    em = sum(.56 if ch.isdigit() else .24 if ch in ',.' else .25 if ch == ' ' else .62 for ch in fmt(FIN))
    size = int(min(230, 760 / max(1, em)))                  # เลขยาว → หดเอง ไม่ล้นการ์ด
    bx = (770, 440) if 150 + size * em + 20 <= 770 else (P[-1][0] + 95 - 100, P[-1][1] + 250 - 100)   # เส้นระเบิด: ข้างเลข · เลขยาวไม่มีที่ → ที่ปลายเส้น
    tk = ''.join(f'<text class="st-yr" x="{px(i):.0f}" y="955" text-anchor="middle" opacity="0" fill="{k["yr"]}">{t}</text>'
                 for i, t in enumerate((ticks or [])[:len(V)]))
    th = ' th' if any('\u0e00' <= ch <= '\u0e7f' for ch in label) else ''
    body = (strip(f'{id}l', label, 140, 300, k['lab'], ('thm' if th else 'mid') + th, -3, z=8)
        + f'<div class="st-num" id="{id}n" style="font-size:{size}px;z-index:7">{fmt(0)}</div>'
        + f'<svg class="st-chart" width="890" height="1250" viewBox="0 0 890 1250" style="z-index:5">'
          f'<line id="{id}g0" stroke="{k["grid"]}" stroke-width="3" stroke-dasharray="10 14" x1="{X0}" y1="{Y1}" x2="{X0}" y2="{Y1}"/>'
          f'<line id="{id}g1" stroke="{k["grid"]}" stroke-width="3" stroke-dasharray="10 14" x1="{X0}" y1="{(Y0 + Y1) / 2}" x2="{X0}" y2="{(Y0 + Y1) / 2}"/>'
          f'<line id="{id}g2" stroke="{k["base"]}" stroke-width="5" x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y0}"/>{tk}'
          f'<path id="{id}p" d="{d}" opacity="0" fill="none" stroke="{k["line"]}" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>'
          f'<circle id="{id}h" r="17" fill="none" stroke="{k["tip"]}" stroke-width="6" opacity="0"/>'
          f'<circle id="{id}t" r="17" fill="{k["tip"]}" stroke="#ffffff" stroke-width="6" opacity="0"/></svg>'
        + line(f'{id}b', *bx, 200, 200, BURST, k['burst'], 9) + extra)
    ROT[f'{id}n'] = -2
    broll(t0, t1, card, body)
    T = globals().get('rt') or r                             # broll-only = เวลาบนม้วน · คลิปเต็ม = เวลาจริง
    tl_ = t_land if t_land is not None else t0 + 3.5
    tl_ = min(tl_, t1 - 1.0); td = t0 + 0.9; dur = round(max(0.8, tl_ - td), 3)
    slap(f'{id}l', t0 + 0.35); slap(f'{id}n', t0 + 0.55)
    for j in range(3): tw(f"tl.to('#{id}g{j}',{{attr:{{x2:{X1 + 20}}},duration:.45,ease:'power3.out'}},{T(t0 + 0.6 + j * 0.06)});")
    tw(f"document.querySelectorAll('#g{len(SEGS)} .st-yr').forEach((el,i)=>tl.to(el,{{opacity:1,duration:.25}},{T(t0 + 0.75)}+i*.04));")
    js_ = '''(()=>{const ln=document.getElementById('@p'),tp=document.getElementById('@t'),hl=document.getElementById('@h'),nm=document.getElementById('@n');
      const L=ln.getTotalLength();ln.setAttribute('stroke-dasharray',L);ln.setAttribute('stroke-dashoffset',L);const st={p:0};
      const f=x=>PRE+x.toLocaleString('en-US',{minimumFractionDigits:DEC,maximumFractionDigits:DEC})+SUF;
      function dr(){const q=st.p*L;ln.setAttribute('stroke-dashoffset',L-q);const pt=ln.getPointAtLength(Math.max(.01,q));
        for(const c of [tp,hl]){c.setAttribute('cx',pt.x);c.setAttribute('cy',pt.y);}
        const v=st.p>=1?FIN:st.p<=0?0:Math.round((Y0-pt.y)/(Y0-Y1)*VMAX*SC*10**DEC)/10**DEC;nm.textContent=f(v);}
      dr();tl.to(['#@t','#@p'],{opacity:1,duration:.12},TD);tl.to(st,{p:1,duration:DUR,ease:'power1.inOut',onUpdate:dr},TD);})();'''
    for a_, b_ in (('@', id), ('PRE', json.dumps(prefix)), ('SUF', json.dumps(suffix)), ('DEC', str(decimals)), ('FIN', repr(FIN)),
                   ('VMAX', repr(vmax)), ('SC', repr(SC)), ('Y0', str(Y0)), ('Y1', str(Y1)), ('TD', str(T(td))), ('DUR', str(dur))):
        js_ = js_.replace(a_, b_)
    tw(js_); fx(td, 'pen', 0.3)
    tw(f"tl.fromTo('#{id}h',{{opacity:.9,attr:{{r:17}}}},{{opacity:0,attr:{{r:70}},duration:.6,ease:'power2.out',immediateRender:false}},{T(tl_)});")
    bump(f'{id}n', tl_); fx(tl_, 'thump'); draw(f'{id}b', tl_ + 0.05, 0.3)
    boil([f'{id}l'], t0, t1); boil([f'{id}n'], tl_, t1)

# ===== ช่วง B-roll (ขึ้นเฉพาะตอนยกตัวอย่าง / เปรียบเทียบเป็นภาพ) =====
# 1 · ตัวอย่างเครื่องมือ: Gen Y อยากให้ใช้คอม vs Gen Z ใช้ iPad
a, b = at('คนนึงอยาก') - 0.1, at('แล้วก็หาว่า')
broll(a, b, 'navy',
    piece('a1', 'pc.png', 150, 450, 360, -6) + tape('a2', 260, 435, -18)
    + piece('a3', 'ipad.png', 550, 700, 420, 8) + tape('a4', 750, 685, 22)
    + strip('a5', 'VS', 420, 620, 's-ember', 'big', -8, z=9)
    + strip('a6', 'GEN Y', 150, 330, 's-paper', 'mid', -4) + strip('a7', 'Microsoft Word', 150, 930, 's-cream', 'sml', 3)
    + strip('a8', 'GEN Z', 620, 1130, 's-paper', 'mid', 5)
    + line('a9', 640, 400, 300, 260, BURST) + line('a10', 180, 1060, 220, 180, STAR, '#ff3608', 8))
slide('a1', a + 0.25, dx=-600); tw(f"tl.fromTo('#a2',{{opacity:0}},{{opacity:1,duration:0.01}},{rt(a + 0.6)});")
slap('a6', at('ให้ใช้')); slap('a7', at('MicrosoftWord'))
slap('a5', at('แต่GenZ'), 'thump'); slide('a3', at('แต่GenZ') + 0.3, dx=620); tw(f"tl.fromTo('#a4',{{opacity:0}},{{opacity:1,duration:0.01}},{rt(at('แต่GenZ') + 0.7)});")
slap('a8', at('ปัจจุบันนี้')); draw('a9', at('iPad') - 0.1, 0.35); bump('a3', at('iPad')); draw('a10', at('ใช้กันแต่เครื่องมือ'), 0.4)
boil(['a1', 'a3', 'a5'], a, b)

# 2 · เปรียบ: วางความรู้ที่คุ้นเคยลง (หนังสือเก่าร่วงออก) → หยิบของใหม่ (หลอดไฟหล่นลงมา)
a, b = at('เราต้องหยุดที่'), at('เราต้องเปลี่ยน')
broll(a, b, 'ember',
    piece('b1', 'books.png', 150, 470, 780, -4) + tape('b2', 420, 450, -6)
    + strip('b3', 'ความรู้ที่คุ้นเคย', 170, 900, 's-paper', 'thm th', -5)
    + strip('b4', 'UNLEARN', 380, 1040, 's-navy', 'big', 6, z=8)
    + piece('b5', 'bulb.png', 400, 250, 300, 0, z=5)
    + strip('b6', 'RELEARN', 190, 930, 's-paper', 'big', -4, z=9) + strip('b7', 'ของใหม่', 600, 1100, 's-navy', 'thm th', 5, z=9)
    + line('b8', 180, 1180, 220, 200, STAR, '#0d1b2a', 8))
slide('b1', a + 0.25, dx=-800); tw(f"tl.fromTo('#b2',{{opacity:0}},{{opacity:1,duration:0.01}},{rt(a + 0.6)});")
slap('b3', at('ที่เราคุ้นเคย')); slap('b4', at('Unlearn', 2) - 0.1, 'thump')
for i, id in enumerate(('b1', 'b2', 'b3', 'b4')): away(id, at('ของเดิม', 2) + 0.15 + i * 0.05, 1300, (-18, 30, -25, 20)[i])
drop('b5', at('Relearn') - 0.2); slap('b6', at('Relearn') + 0.1, 'thump'); slap('b7', at('ของใหม่')); draw('b8', at('กลับขึ้นมา'))
boil(['b1', 'b4'], a, at('ของเดิม', 2)); boil(['b5', 'b6', 'b7'], at('Relearn'), b)

# 3 · ตัวอย่างสองฝั่ง: Gen Z → iPad สู่ Professional · Gen Y → คอมสู่ iPad
a, b = at('ทั้งGenZ'), at('ถูกไหม')
broll(a, b, 'navy',
    strip('c1', 'GEN Z', 130, 320, 's-ember', 'mid', -5) + piece('c2', 'ipad.png', 140, 450, 280, -6)
    + line('c3', 420, 520, 160, 120, ARROW_R, '#ffffff', 10)
    + piece('c4', 'suit.png', 590, 380, 230, 4) + piece('c5', 'tower.png', 760, 410, 200, -3, z=3)
    + strip('c6', 'PROFESSIONAL', 560, 710, 's-paper', 'sml', -3, z=7)
    + strip('c7', 'GEN Y', 130, 850, 's-paper', 'mid', 4) + piece('c8', 'pc.png', 160, 960, 220, 5)
    + line('c9', 420, 1030, 160, 120, ARROW_R, '#ffffff', 10)
    + piece('c10', 'ipad.png', 600, 900, 320, 7))
slap('c1', a); slide('c2', a + 0.3, dx=-400, s=None); draw('c3', at('Unlearn', 3), 0.3)
slide('c4', at('Professional'), dy=-500); slide('c5', at('Corporate'), dx=500, s=None); slap('c6', at('Professional') + 0.25)
slap('c7', at('GenYก็ต้อง')); slide('c8', at('GenYก็ต้อง') + 0.3, dx=-400, s=None); draw('c9', at('Unlearn', 4) + 0.3, 0.3)
slide('c10', at('iPadมันทำ'), dx=500)
boil(['c2', 'c4', 'c8', 'c10'], a, b)

# 4 · เปรียบ: โลกเปลี่ยนเร็ว (นาฬิกาสั่น + เส้นความเร็ว) → ค้างถึงจบ
a, b = at('ที่การเปลี่ยน') - 0.1, TOTAL
broll(a, b, 'ember',
    piece('d1', 'clock.png', 170, 420, 740, -5)
    + line('d2', 110, 340, 280, 280, BURST, '#ffffff', 10) + line('d3', 700, 900, 280, 280, BURST, '#0d1b2a', 10)
    + strip('d4', 'โลกเปลี่ยน<span class="em">เร็ว</span>', 240, 300, 's-navy', 'thb th', -3, z=8)
    + strip('d5', 'สกิลที่ขาดไป', 260, 1000, 's-paper', 'thb th', 3, z=8))
slide('d1', a + 0.25, dx=-700); slap('d4', at('เปลี่ยนแปลง') + 0.2, 'thump')
draw('d2', at('เร็วมาก'), 0.3); draw('d3', at('เร็วมาก') + 0.15, 0.3, None); shake('d1', at('เร็วมาก') + 0.3, 10, 10)
slap('d5', at('ขาดไป') - 0.15, 'thump')
boil(['d1', 'd4', 'd5'], a, b)

# ===== ปก (เฉพาะคลิปที่ยังไม่มีปกเบิร์นมา) =====
if COVER:
    pass   # TODO: ทำเป็นช่วงแรกของม้วน (วิดีโอเต็มจอ + .dark + .t1/.t2) — ยังไม่ได้ทดสอบ

# ===== เขียนม้วน =====
REEL = round(sum(b - a for _, a, b in SEGS), 3)
tw('tl.set([' + ','.join(f"'#{k}'" for k, v in ROT.items() if v) + '],{rotation:(i,el)=>ROTS[el.id]},0);')
doc = f'''<!doctype html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
{open('style.css', encoding='utf-8').read()}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{REEL}" data-width="1080" data-height="1920">
{chr(10).join(html)}
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const ROTS = {json.dumps(ROT)};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join('    ' + l for l in js)}
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
'''
open('index.html', 'w', encoding='utf-8').write(doc)

# วิดีโอหน้าคนพูดในวงกลม: ตัดเฉพาะช่วงของแต่ละ B-roll (ไฟล์แยก · ห้ามใช้ไฟล์เดียวหลาย <video>)
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
for n, a, b in SEGS:
    out = f'assets/cam{n}.mp4'; key = f'{a}-{b}-{FACE_CROP}'; stamp = out + '.key'
    if os.path.exists(out) and os.path.exists(stamp) and open(stamp).read() == key: continue
    subprocess.run([FF, '-nostdin', '-v', 'error', '-ss', str(a), '-t', str(round(b - a, 3)), '-i', 'assets/talk.mp4', '-an',
                    '-vf', f'crop={FACE_CROP},scale=410:410', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-y', out], check=True)
    open(stamp, 'w').write(key)
json.dump({'segs': SEGS, 'total': TOTAL, 'reel': REEL}, open('work/segs.json', 'w', encoding='utf-8'), indent=1)
json.dump(SFX, open('work/sfx.json', 'w', encoding='utf-8'))
print('B-roll', [(n, a, b, round(b - a, 1)) for n, a, b in SEGS], f'· ม้วนยาว {REEL} วิ จากคลิป {TOTAL} วิ · tweens', len(js), '· sfx', len(SFX))
