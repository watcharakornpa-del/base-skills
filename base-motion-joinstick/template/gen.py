#!/usr/bin/env python3
"""base-motion-joinstick — คลิป Micro Learning สำหรับแอป JOINSTICK
โครง (จาก base-motion-collage v3): Text Hook → คนพูดเต็มจอ + ซับ + Super ชิปบนหัว + การ์ดระดับล่างจอ → B-roll หน้าจอแบบแอป + หน้าในวงกลม
หน้าตา = ภาษา UI ของแอป JOINSTICK (พื้นดำ การ์ด #131313 แดงไฟ #EA3A1F ทอง Stage · Poppins + IBM Plex Sans Thai) — วาดใหม่ ไม่ใช้ภาพจอจริง
รัน: python gen.py → index.html + assets/mix.wav แล้ว render
คลิปนี้: C2673 · Extrinsic Motivation 4 ระดับ (Ryan & Deci)"""
import json, math, os, re, shutil, subprocess, sys
from xml.sax.saxutils import escape
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, 'work'); from align import at
# at('วลี') = เวลา "หลังตัด" · ถ้าใช้ after= ต้องเป็นเวลาหลังตัดด้วย ห้ามเอาเวลาจาก phrases.txt (ไฟล์ดิบ) มาใส่ — เคยพลาดทั้งคลิป
#   คำซ้ำ: ใช้วลีที่ยาวพอให้ไม่ซ้ำ (เช่น at('Doข้อที่สอง')) หรือ after=at('วลีก่อนหน้า')

# ===== ตั้งค่าต่อคลิป =====
TOTAL = 200.76
FACE_CROP = '1000:1000:90:280'    # crop หน้าคนพูดสำหรับวงกลม B-roll (ตัดกว้าง เผื่อคนพูดขยับ)
SUBS = 'work/subs.srt'

js = []; html = []; SFX = []; HIDE_SUBS = []
def tw(s): js.append(s)
def r(x): return round(x, 3)
def fx(t, kind, vol=None):
    v = {'swoosh': 0.30, 'click': 0.45, 'thump': 0.70, 'pen': 0.30}[kind] if vol is None else vol
    SFX.append((r(max(0, t)), kind, v))

# ---------- ชิ้นส่วน UI ----------
FLAME = ('<path fill="{c}" d="M20 2C24 12 36 18 36 32C36 42 29 48 20 48C11 48 4 42 4 32C4 24 10 20 12 12C15 18 17 20 19 20C19 13 18 8 20 2Z"/>'
         '<path fill="#FFB199" d="M20 26C23 31 27 33 27 38C27 43 24 45 20 45C16 45 13 43 13 38C13 34 17 32 20 26Z"/>')
def flame(w=34, col='#EA3A1F'):
    return f'<svg class="flame" style="width:{w}px;height:{round(w * 1.24)}px" viewBox="0 0 40 50">{FLAME.format(c=col)}</svg>'
def gauge(id, x, y, w, val0=0, big=True):
    """เกจครึ่งวงแบบหน้า Home (Hype) · ขีด 20–100 · big = มีตัวเลขกลาง (#id_num) · ส่วนโค้งแดง #id_arc"""
    R, cx, cy = 300, 350, 360
    ticks = ''.join(f'<text class="tk" x="{cx - (R + 50) * math.cos(math.pi * v / 100):.0f}" y="{cy - (R + 50) * math.sin(math.pi * v / 100) + 9:.0f}" '
                    f'text-anchor="middle">{v}</text>' for v in (20, 40, 60, 80, 100))
    if big: mid = f'<g transform="translate({cx - 54} {cy - 300}) scale(2.7)">{FLAME.format(c="#EA3A1F")}</g><text class="num" id="{id}_num" x="{cx}" y="{cy}" text-anchor="middle">{val0}</text>'
    else: mid = f'<g transform="translate({cx - 75} {cy - 200}) scale(3.75)">{FLAME.format(c="#EA3A1F")}</g>'
    arc = f'M{cx - R} {cy} A{R} {R} 0 0 1 {cx + R} {cy}'
    return (f'<svg class="gauge" id="{id}" style="left:{x}px;top:{y}px;width:{w}px" viewBox="-40 -30 780 420">'
            f'<path d="{arc}" fill="none" stroke="#2c2c2e" stroke-width="34" stroke-linecap="round"/>'
            f'<path id="{id}_arc" pathLength="100" stroke-dasharray="100" stroke-dashoffset="{100 - val0}" d="{arc}" '
            f'fill="none" stroke="#EA3A1F" stroke-width="34" stroke-linecap="round"/>{ticks}{mid}</svg>')
# หลอดพลัง · กราฟแท่ง · เช็กลิสต์ · การ์ด DO/DON'T (เพิ่มจาก COM-01 C5398/C5399 · ตัวอย่างใช้งานใน references/examples/)
def track(n, tot=4): return '<div class="track">' + ''.join(f'<i class="{"f" if k < n else ""}"></i>' for k in range(tot)) + '</div>'
def meter(id, y, lbl, name, th, low=False):
    return (f'<div class="card mtr{" low" if low else ""}" id="{id}" style="top:{y}px"><div class="lbl">{lbl}</div>'
            f'<div class="nm">{name}<small>{th}</small></div><div class="pc" id="{id}_pc">0</div><div class="tr"><div class="fl" id="{id}_fl"></div></div></div>')
def mfill(id, t, v0, v1, d=0.8):
    tw(f"tl.fromTo('#{id}_fl',{{scaleX:{v0 / 100}}},{{scaleX:{v1 / 100},duration:{d},ease:'power2.out',immediateRender:false}},{r(t)});")
    tw(f"tl.fromTo('#{id}_pc',{{textContent:{v0}}},{{textContent:{v1},duration:{d},ease:'power2.out',snap:{{textContent:1}},immediateRender:false}},{r(t)});")
def mset0(*ids):
    for id in ids: tw(f"tl.set('#{id}_fl',{{scaleX:0}},0);")
def bar(id, x, h, v, c, goal=False):
    return f'<div class="bar{" goal" if goal else ""}" id="{id}" style="left:{x}px;height:{h}px"><div class="v">{v}</div><div class="c">{c}</div></div>'
def grow(id, t, s='click'):
    tw(f"tl.fromTo('#{id}',{{opacity:0,scaleY:0}},{{opacity:1,scaleY:1,duration:0.5,ease:'power3.out'}},{r(t)});")
    if s: fx(t, s)
CHK = '<svg width="26" height="26" viewBox="0 0 24 24"><path d="M5 12.5L10 17L19 7" fill="none" stroke="#000" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CRS = '<svg width="24" height="24" viewBox="0 0 24 24"><path d="M6 6L18 18M18 6L6 18" fill="none" stroke="#fff" stroke-width="3.4" stroke-linecap="round"/></svg>'
def lvcard(id, a, b, lbl, name, desc, n, tot, cls=''):
    html.append(f'<div class="lv {cls}" id="{id}"><div class="lbl">{lbl}</div>{track(n, tot)}<div class="ttl-en th">{name}</div><div class="sub-t th">{desc}</div></div>')
    slide(id, a, dy=120); tw(f"tl.to('#{id}',{{opacity:0,y:60,duration:0.2,ease:'power2.in'}},{r(b - 0.2)});")
    HIDE_SUBS.append((a, b))   # ผู้ใช้สั่ง: กล่องข้อความที่อนิเมทขึ้นมา (การ์ดล่างจอด้วย) ไม่ต้องมีซับ

# ---------- ท่าขยับ ----------
def pop(id, t, s='click', d=0.28, dy=40):
    tw(f"tl.fromTo('#{id}',{{opacity:0,y:{dy},scale:0.94}},{{opacity:1,y:0,scale:1,duration:{d},ease:'back.out(1.8)'}},{r(t)});")
    if s: fx(t, s)
def slide(id, t, dx=0, dy=0, s='swoosh', d=0.4):
    tw(f"tl.fromTo('#{id}',{{opacity:0,x:{dx},y:{dy}}},{{opacity:1,x:0,y:0,duration:{d},ease:'power3.out'}},{r(t)});")
    if s: fx(t, s)
def bump(id, t, k=1.08, s=True):
    tw(f"tl.to('#{id}',{{scale:{k},duration:0.12,yoyo:true,repeat:1,ease:'power2.out'}},{r(t)});")
    if s: fx(t, 'click', 0.3)
def out(id, t, d=0.2):
    tw(f"tl.to('#{id}',{{opacity:0,y:-20,duration:{d},ease:'power2.in'}},{r(t)});")
def fill(id, t, val, d=0.8):
    tw(f"tl.to('#{id}_arc',{{strokeDashoffset:{100 - val},duration:{d},ease:'power2.out'}},{r(t)});")
def count(id, t, v0, v1, d):
    # ease ต้องเท่ากับ fill() — เดิม power1.in vs power2.out ตัวเลขช้ากว่าหลอด (หลอด 70 ตัวเลขยัง 20) · ผู้ใช้ติ C2673 Draft1
    tw(f"tl.fromTo('#{id}_num',{{textContent:{v0}}},{{textContent:{v1},duration:{d},ease:'power2.out',snap:{{textContent:1}}}},{r(t)});")

# ===== 1 · Text Hook: แบบชื่อคลิปในหน้าเล่น Micro Learning (ป้ายแดง → คำขาวใหญ่ → คำแดง) =====
def hook(t_end, words):
    body = ''.join(f'<div class="hk {c}" id="hw{i}" style="top:{y}px">{w}</div>' for i, (t, w, c, y) in enumerate(words))
    html.append(f'<div id="hook"><div class="dim"></div>{body}</div>')
    for i, (t, w, c, y) in enumerate(words):
        big = c in ('hk-xl', 'hk-em')
        tw(f"tl.fromTo('#hw{i}',{{opacity:0,scale:{1.4 if big else 0.8},y:{0 if big else 16}}},{{opacity:1,scale:1,y:0,duration:{0.24 if big else 0.18},ease:'{'back.out(2.2)' if big else 'power2.out'}'}},{r(t)});")
        fx(t, 'thump' if big else 'click', 0.55 if big else 0.3)
    tw(f"tl.to('#hook',{{opacity:0,duration:0.2,ease:'power2.in'}},{r(t_end - 0.2)});")
    HIDE_SUBS.append((0, t_end))
TH = at('เป็นสิ่งที่สำคัญ') + 0.3
hook(TH, [   # ปก = ชื่อคลิปจากชีตสคริปต์ (คอลัมน์ "ชื่อคลิป / ช็อต") · ไม่มีป้าย MICRO LEARNING (ผู้ใช้อนุมัติ 18 พ.ย. 2026 · ต้นแบบ C2675)
    (0.1, '<span class="en">Motivation</span>', 'hk-xl', 610),   # คำหลักหน้า ":" บรรทัด 1 ขาว (อังกฤษ/สั้น = hk-xl)
    (0.4, 'แรงจูงใจ 4 ระดับ', 'hk-em', 770),                       # บรรทัด 2 แดง (ไทยใหญ่)
    (0.8, 'ทำไมคนทำงานด้วยใจ', 'hk-s', 980),                       # ส่วนหลัง ":" แบ่ง 1–2 บรรทัดตามวลี ขาว
    (1.1, 'ไม่เท่ากัน', 'hk-s', 1060),
])

# ===== 2 · Super: ชิป/การ์ดดำเหนือหัวคนพูด (y 110–370) · ไม่มีซับช่วงนี้ =====
NS = [0]
def sup(t0, t1, rows, pops):
    """rows = [(html, top)] · pops = [(id, เวลาเด้ง)] (ตัวแรกเสียง thump ที่เหลือ click)"""
    NS[0] += 1
    html.append(f'<div class="super">' + ''.join(f'<div class="row" style="top:{y}px">{h}</div>' for h, y in rows) + '</div>')
    for k, (id, t) in enumerate(pops): pop(id, t, 'thump' if k == 0 else 'click'); out(id, t1 - 0.2)
    HIDE_SUBS.append((t0, t1))
def pill(id, txt, on=False, fl=False): return f'<div class="pill{" on" if on else ""}" id="{id}">{flame(30, "#fff" if on else "#EA3A1F") if fl else ""}{txt}</div>'
def chip(id, ttl, lbl='', hot=False):
    return f'<div class="chip{" hot" if hot else ""}" id="{id}">{f"<div class=lbl>{lbl}</div>" if lbl else ""}<div class="ttl">{ttl}</div></div>'

sup(at('Intrinsic'), at('สิ่งที่เราเคย') - 0.1, [(pill('k1a', 'Intrinsic') + pill('k1b', 'Extrinsic', on=True), 180)],
    [('k1a', at('Intrinsic')), ('k1b', at('Extrinsic'))])
sup(at('ถ้าเรามีแค่'), at('เราจะมีวิธี') - 0.05, [(chip('k2', 'ถ้ามีแค่ <span class="red en">Extrinsic</span> ล่ะ ?', hot=True), 190)], [('k2', at('ถ้าเรามีแค่'))])
sup(at('Ryan'), at('มันแบ่งได้') - 0.4, [(chip('k3', '<span class="en">Ryan &amp; Deci · <span class="red">2000</span></span>', lbl='SELF-DETERMINATION THEORY'), 150)],
    [('k3', at('Ryan'))])
sup(at('แปลว่าหน้าที่'), at('ถ้าเราจะเล่นกับ') - 0.1, [(pill('k4a', 'LEADER', fl=True), 110), (chip('k4b', 'จุดไฟให้ถึง<span class="red">ระดับสูง</span>'), 230)],
    [('k4a', at('แปลว่าหน้าที่') + 0.6), ('k4b', at('เราควรจะต้อง') + 0.4)])
sup(at('Why'), at('Why') + 3.4, [(pill('k5', 'WHY ?', on=True), 200)], [('k5', at('Why'))])
sup(at('Perfectionist'), at('Perfectionist') + 3.6, [(pill('k6', 'Perfectionist', fl=True), 200)], [('k6', at('Perfectionist'))])
sup(at('Take'), at('อย่าใช้แค่') - 0.1, [(pill('k7a', 'TAKEAWAY', on=True), 110), (chip('k7b', 'แตะให้ถึง<span class="red">ระดับ 4</span>'), 230)],
    [('k7a', at('Take')), ('k7b', at('อย่างน้อยแตะ'))])

# ===== 3 · การ์ดระดับ (bottom sheet ล่างจอ ทับโต๊ะ) ค้างตลอดช่วงอธิบายแต่ละระดับ · ไม่มีซับระหว่างการ์ดขึ้น =====
LV = [('Level', 'Introjected', 1, 'External', 'ทำเพราะ<b class="red">รางวัล</b> หรือกลัว<b class="red">โดนลงโทษ</b>'),
      ('Introjected', 'ระดับที่สามคือ', 2, 'Introjected', 'ทำเพราะกลัว<b class="red">รู้สึกผิด</b> หรือกลัว<b class="red">เสียหน้า</b>'),
      ('ระดับที่สามคือ', 'ระดับสุดท้าย', 3, 'Identified', 'ทำเพราะรู้ว่างานนี้<b class="red">สำคัญ</b> · ตอบได้ว่า Why'),
      ('ระดับสุดท้าย', 'หน้าที่ของเราในฐานะหัวหน้าครับคือ', 4, 'Integrated', 'งานนี้<b class="red">เข้ากับตัวตน</b>ของเรา')]
for a_, b_, n, name, desc in LV:
    a, b = at(a_) - 0.1, at(b_) - 0.15
    html.append(f'<div class="lv" id="lv{n}"><div class="lbl">LEVEL {n} / 4</div>{track(n)}<div class="ttl-en">{name}</div><div class="sub-t th">{desc}</div></div>')
    slide(f'lv{n}', a, dy=120); tw(f"tl.to('#lv{n}',{{opacity:0,y:60,duration:0.2,ease:'power2.in'}},{r(b - 0.2)});")
    HIDE_SUBS.append((a, b))   # การ์ดขึ้น = ไม่มีซับ (ผู้ใช้สั่ง C2676)
bump('lv1', at('ต่ำสุด'), 1.04)

# ===== 4 · B-roll: หน้าจอแบบแอป + หน้าคนพูดในวงกลมขอบแดง =====
SEGS = []
def broll(t0, t1, body):
    n = len(SEGS) + 1; L = r(t1 - t0); SEGS.append((n, r(t0), r(t1)))
    html.append(f'''<div class="seg" id="g{n}" data-layout-allow-overflow data-layout-allow-occlusion>{body}
  <div class="face"><video id="cam{n}" class="clip" data-start="{r(t0)}" data-duration="{L}" data-track-index="{n + 2}" data-media-start="0" muted playsinline src="assets/cam{n}.mp4"></video></div>
</div>''')
    tw(f"tl.fromTo('#g{n}',{{opacity:1,y:1920}},{{opacity:1,y:0,duration:0.3,ease:'power3.out'}},{r(t0)});")
    if t1 < TOTAL - 0.1: tw(f"tl.to('#g{n}',{{y:-1920,duration:0.25,ease:'power2.in'}},{r(t1 - 0.25)});")
    fx(t0, 'swoosh', 0.35); HIDE_SUBS.append((t0, t1))
def hd(lbl, ttl): return f'<div class="hd"><div class="lbl">{lbl}</div><div class="ttl">{ttl}</div></div>'

# B1 · 4 ระดับ = เส้นทาง Shift Stage (ล่าง→บน) · นับหนึ่ง–สี่ · ยิ่งสูงยิ่งทำงานได้มาก
a, b = at('มันแบ่งได้') - 0.4, at('แปลว่าหน้าที่') - 0.1
ST = [(4, 'Integrated', 'ตรงกับตัวตน'), (3, 'Identified', 'รู้ว่าสำคัญ'), (2, 'Introjected', 'กลัวเสียหน้า'), (1, 'External', 'รางวัล / โทษ')]
rows = ''
for k, (n, name, d) in enumerate(ST):
    y = 470 + k * 172
    rows += (f'<div class="card st" id="st{n}" style="top:{y}px"><div class="lbl">LEVEL {n}</div><div class="ttl-en">{name}</div><div class="th-d">{d}</div></div>'
             f'<div class="dot" id="dt{n}" style="top:{y + 57}px"></div>')
broll(a, b, hd('EXTRINSIC MOTIVATION', 'แรงจูงใจภายนอกมี <span class="red">4 ระดับ</span>')
      + '<div class="rail" style="top:527px;height:520px"></div><div class="rail-f" id="rf" style="top:527px;height:520px"></div>' + rows
      + '<div class="row" style="top:1180px"><div class="pill on" id="b1p">ยิ่งสูง ยิ่งทรงพลัง</div></div>')
tw("tl.set('#rf',{scaleY:0},0);")
for n, t in zip((1, 2, 3, 4), (at('ตั้งแต่หนึ่ง') + 0.15, at('สอง', after=47.6), at('สาม', after=47.6), at('สี่', after=47.6))):
    slide(f'st{n}', t, dx=200, s='click', d=0.3); tw(f"tl.fromTo('#dt{n}',{{opacity:0}},{{opacity:1,duration:0.1}},{r(t)});")
t = at('ยิ่งเรา'); tw(f"tl.to('#rf',{{scaleY:1,duration:1.6,ease:'power1.inOut'}},{r(t)});"); fx(t, 'pen')
for k, n in enumerate((1, 2, 3, 4)):
    tw(f"tl.to('#st{n}',{{borderColor:'rgba(234,58,31,.7)',duration:0.15}},{r(t + 0.4 * k)});")
    tw(f"tl.to('#st{n} .lbl',{{color:'#EA3A1F',duration:0.15}},{r(t + 0.4 * k)});")
tw(f"tl.to('#dt4',{{backgroundColor:'#ffffff',duration:0.15}},{r(t + 1.5)});"); bump('st4', t + 1.5, 1.04)
pop('b1p', at('แรงจูงใจภายนอกนี้'), 'thump')

# B2 · แชทภารกิจ: หัวหน้าคุยกับน้อง 4 แบบ ไล่ระดับ 1→4 (แถบแดงใต้หัวแชทเต็มขึ้นทีละ 25%)
a, b = at('สมมติ') - 0.1, at('ความทรงพลัง') - 0.05
MS = [(at('ถ้าเราบอกแค่ว่า'), 1, 'ทำนะ ถ้าไม่เสร็จ<b>จะโดนบทลงโทษ</b>', 400),
      (at('แต่ถ้าเราเปลี่ยน') + 0.3, 2, 'ทำนะ ไม่งั้น<b>คนอื่นจะมองเราไม่ดี</b>', 600),
      (at('เพิ่มอีกระดับสาม') + 0.9, 3, 'ทำนะ สิ่งนี้<b>สำคัญมาก</b> ช่วยให้ทีมเดินต่อได้', 800),
      (at('แต่ถ้าคุณสามารถ') + 2.0, 4, 'ทำนะ นี่คือ<b>ตัวตนของเรา</b> ความเป็น Perfectionist ที่มีแค่เราทำได้', 1000)]
msgs = ''.join(f'<div class="msg" id="m{n}" style="top:{y}px"><div class="who"><span class="tag{" l4" if n == 4 else ""}">LEVEL {n}</span>'
               f'{"".join(flame(26) for _ in range(n))}</div><div class="bub th">{txt}</div></div>' for t, n, txt, y in MS)
broll(a, b, '<div class="chat-hd">'   # ไม่ใส่ปุ่ม Back ที่ลอกจากหน้าแอป (ผู้ใช้สั่งเอาออก C2673 Draft1)
      '<div class="nm"><div class="lbl">MISSION · IGNITE</div><div class="ttl">คุยกับน้องในทีม</div></div><div class="bar" id="cbar"></div></div>' + msgs)
tw("tl.set('#cbar',{scaleX:0},0);")
for k, (t, n, txt, y) in enumerate(MS):
    pop(f'm{n}', t, 'click', dy=60)
    tw(f"tl.to('#cbar',{{scaleX:{n / 4},duration:0.5,ease:'power2.out'}},{r(t)});")
    if k: tw(f"tl.to('#m{MS[k - 1][1]} .bub',{{color:'#8e8e93',duration:0.3}},{r(t)});")
bump('m4', at('Perfectionist', after=170), 1.03)

# B3 · เกจพลัง (แบบ Hype): ระดับ 4 = Strong ที่สุด
a, b = at('ความทรงพลัง') - 0.05, at('ดังนั้น', after=180) - 0.05
broll(a, b, hd('POWER OF EXTRINSIC DRIVE', 'ถึงระดับ 4 = <span class="red">แรงที่สุด</span>') + gauge('gp', 90, 520, 900)
      + '<div class="row" style="top:1150px"><div class="pill on" id="b3p"><span class="en">STRONG</span>&nbsp;ที่สุด</div></div>')
fill('gp', a + 0.3, 100, 2.9); count('gp', a + 0.3, 0, 100, 2.9)
bump('gp', at('Strong'), 1.04, False); fx(at('Strong'), 'thump'); pop('b3p', at('Strong') + 0.1, None)

# B4 · ปิดท้าย: ระดับ 1 vs ระดับ 4
a = at('อย่าใช้แค่') - 0.1
broll(a, TOTAL, hd('TAKEAWAY', 'อย่าเล่นแค่<span class="red">ระดับ 1</span>')
      + f'<div class="card cmp" id="c1" style="left:70px"><div class="lbl" style="color:#8e8e93">LEVEL 1</div><div class="ttl-en">External</div><div class="sub-t th">รางวัล / บทลงโทษ</div>{gauge("gg1", 20, 400, 410, 0, False)}</div>'
      + f'<div class="card cmp" id="c4" style="left:560px;border-color:rgba(234,58,31,.7)"><div class="lbl">LEVEL 4</div><div class="ttl-en">Integrated</div><div class="sub-t th">ตรงกับตัวตน</div>{gauge("gg4", 20, 400, 410, 0, False)}</div>')
pop('c1', a + 0.3, 'click', dy=80); fill("gg1", a + 0.6, 22, 0.6)
bump('c1', at('เพราะนั่นคุณ') + 1.4, 1.04)
pop('c4', at('อ่อนแรง') - 0.6, 'thump', dy=80); fill("gg4", at('อ่อนแรง') - 0.3, 100, 0.8)
tw(f"tl.to('#c1',{{opacity:0.4,duration:0.3}},{r(at('อ่อนแรง'))});")

# ===== 5 · ซับ (IBM Plex Sans Thai ขาว เงาฟุ้ง) · ไม่ขึ้นช่วง Hook / Super / B-roll =====
# S3 Transition (ผู้ใช้สั่ง 25 พ.ย. 2026): B-roll/insert เต็มจอ 2 อันห่างกัน < 3 วิ เดิมอันแรกเลื่อนออก อันใหม่เลื่อนเข้า → หน้าคนพูดแว็บตรงกลาง
#   → อันแรกค้าง (ยืดวิดีโอวงกลมหน้า/อัดจอให้เล่นต่อ) อันใหม่เฟดทับ 0.3 วิ แล้วค่อยซ่อนอันแรก · ห่าง ≥ 3 วิ = ตั้งใจให้เห็นคนพูด ใช้ท่าเดิม
def smooth_full(gap=3.0, d=0.3):
    ent, ext = {}, {}
    for i, s in enumerate(js):
        m = re.match(r"tl\.fromTo\('#(g\d+|in\d+\w*)',\{opacity:[01],y:(?:1920|60)\}.*,([\d.]+)\);$", s)
        if m: ent[m.group(1)] = (i, float(m.group(2))); continue
        m = re.match(r"tl\.to\('#(g\d+|in\d+\w*)',\{(?:y:-1920|opacity:0),duration:0\.25,.*,([\d.]+)\);$", s)
        if m: ext[m.group(1)] = (i, r(float(m.group(2)) + 0.25))
    segs = sorted((ent[k][1], ext[k][1] if k in ext else TOTAL, k) for k in ent)
    drop, z, n, end = set(), 21, 0, {}
    for (a0, a1, A), (b0, b1, B) in zip(segs, segs[1:]):
        if A not in ext or not -0.5 < b0 - a1 < gap: z = 21; continue
        e = r(b0 + d); drop.add(ext[A][0]); n += 1; end[A] = e
        js[ent[B][0]] = f"tl.fromTo('#{B}',{{opacity:0,y:0}},{{opacity:1,y:0,duration:{d},ease:'power1.out'}},{r(b0)});"
        tw(f"tl.set('#{B}',{{zIndex:{z}}},{r(b0)});"); tw(f"tl.set('#{A}',{{opacity:0}},{e});"); z += 1
        k = next(i for i, h in enumerate(html) if f'id="{A}"' in h)   # วิดีโอในอันแรก (วงกลมหน้า · อัดจอ) ที่จบตรง a1 → เล่นต่อถึง e
        html[k] = re.sub(r'data-start="([\d.]+)" data-duration="([\d.]+)"', lambda m: m.group(0) if abs(float(m.group(1)) + float(m.group(2)) - a1) > 0.05
                         else f'data-start="{m.group(1)}" data-duration="{r(e - float(m.group(1)))}"', html[k])
        SEGS[:] = [(q, a, e) if f'id="cam{q}"' in html[k] and abs(b - a1) < 0.05 else (q, a, b) for q, a, b in SEGS]
        HIDE_SUBS.append((a1, e))
    js[:] = [s for i, s in enumerate(js) if i not in drop]
    if n: print(f'S3 Transition: B-roll ติดกัน {n} จุด → เฟดทับ ไม่เห็นหน้าคนพูด')
    # ช่วงเต็มจอ (ปก + B-roll/insert) → scripts/facecheck.py ข้ามช่วงนี้ (ตั้งใจทับหน้า) ตรวจ S1 เฉพาะช่วงที่เห็นคนพูด
    hk = [h for h in HIDE_SUBS if h[0] == 0][:1]
    json.dump(hk + [(a0, end.get(A, a1)) for a0, a1, A in segs], open('work/full.json', 'w'))
smooth_full()
FIX = [('ไว้โดยเอ่อ ', 'ไว้โดย '), ('Intrin-Intrinsic', 'Intrinsic'), ('Externalระดับสอง', 'External ระดับสอง'), ('Introjected,', 'Introjected')]
caps = []
def ts(x): h, m, s_ = x.replace(',', '.').split(':'); return int(h) * 3600 + int(m) * 60 + float(s_)
for blk in open(SUBS, encoding='utf-8-sig').read().replace('\r', '').strip().split('\n\n'):
    ln = blk.split('\n'); s_, e_ = ln[1].split(' --> '); txt = ' '.join(ln[2:])
    for a_, b_ in FIX: txt = txt.replace(a_, b_)
    caps.append([ts(s_), ts(e_), re.sub(r'\s*ๆ\s*', ' ๆ ', txt).strip()])
for i in range(len(caps) - 1):           # คำขาดข้ามบรรทัด ("แล้" | "วจะ...") → ย้ายตัวที่หลุดกลับไปบรรทัดก่อน
    if caps[i][2].endswith('แล้') and caps[i + 1][2].startswith('ว'): caps[i][2] += 'ว'; caps[i + 1][2] = caps[i + 1][2][1:]
ch = []
for i, (s_, e_, txt) in enumerate(caps):
    for h0, h1 in HIDE_SUBS:     # Hook / Super / การ์ดล่างจอ / B-roll: ทับเกิน 40% ไม่ขึ้นเลย · ทับนิดเดียว → ตัดหัว/ท้าย (ผู้ใช้: กล่องอนิเมทขึ้น = ไม่มีซับ)
        ov = min(e_, h1) - max(s_, h0)
        if ov > 0.4 * (e_ - s_): s_ = e_; break
        if ov > 0:
            if s_ >= h0: s_ = max(s_, h1)
            else: e_ = min(e_, h0)
    if e_ - s_ < 0.3: continue
    assert len(txt) <= 30, f'ซับยาวเกิน 30 ตัว (ห้ามย่อ ให้แบ่งบรรทัดใน captions.txt): {txt}'
    ch.append(f'<div class="sub" id="sb{i}">{escape(txt)}</div>')
    tw(f"tl.fromTo('#sb{i}',{{opacity:0}},{{opacity:1,duration:0.01}},{r(s_)});"); tw(f"tl.set('#sb{i}',{{opacity:0}},{r(e_)});")
json.dump(sorted(HIDE_SUBS), open('work/hide.json', 'w'))   # ช่วงที่ห้ามมีซับ → scripts/check_final.py ตรวจว่าซับไม่ทับ
tw(f"tl.to('#fade',{{opacity:1,duration:0.5}},{r(TOTAL - 0.5)});")

doc = f'''<!doctype html>
<html lang="th"><head><meta charset="UTF-8" /><meta name="viewport" content="width=1080, height=1920" />
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>
{open('style.css', encoding='utf-8').read()}
</style></head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
    <video id="talk" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-media-start="0" muted playsinline src="assets/talk.mp4"></video>
{chr(10).join(html)}
    <div id="subs">{''.join(ch)}</div>
    <audio id="voice" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-volume="1" src="assets/mix.wav"></audio>
    <div id="fade"></div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join('    ' + l for l in js)}
    window.__timelines["main"] = tl;
  </script>
</body></html>'''
open('index.html', 'w', encoding='utf-8').write(doc)

FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
for n, a, b in SEGS:
    o = f'assets/cam{n}.mp4'; key = f"{a}-{b}-{FACE_CROP}-{os.path.getsize('assets/talk.mp4')}-{os.path.getmtime('assets/talk.mp4')}"; st = o + '.key'
    if os.path.exists(o) and os.path.exists(st) and open(st).read() == key: continue
    subprocess.run([FF, '-nostdin', '-v', 'error', '-ss', str(a), '-t', str(r(b - a)), '-i', 'assets/talk.mp4', '-an', '-vf', f'crop={FACE_CROP},scale=384:384',
                    '-c:v', 'libx264', '-crf', '18', '-g', '30', '-pix_fmt', 'yuv420p', '-y', o], check=True); open(st, 'w').write(key)
# เสียงต้องทำใหม่ทุกครั้งที่คลิปพูดเปลี่ยน (ตัดใหม่) — เดิมเช็คแค่ว่ามีไฟล์ → ใช้เสียงชุดตัดเก่า เสียงไม่ตรงปาก 0.6–1.3 วิ (JOINSTICK C2675)
VKEY = f"{os.path.getsize('assets/talk.mp4')}-{os.path.getmtime('assets/talk.mp4')}-{TOTAL}"
if not (os.path.exists('assets/voice.wav') and os.path.exists('assets/voice.key') and open('assets/voice.key').read() == VKEY):
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', 'assets/talk.mp4', '-vn', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', '-y', 'assets/voice.wav'], check=True)
    open('assets/voice.key', 'w').write(VKEY)   # เขียนหลังทำเสียงสำเร็จเท่านั้น
FILES = {'swoosh': 'assets/sfx/swoosh.mp3', 'click': 'assets/sfx/click.mp3', 'thump': 'assets/sfx/thump.wav', 'pen': 'assets/sfx/pen.wav'}
cmd = [FF, '-nostdin', '-v', 'error', '-i', 'assets/voice.wav']; fl = ['[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v]']; lab = ['[v]']
for k, (tm, kind, vol) in enumerate(SFX, 1):
    cmd += ['-i', FILES[kind]]; ms = int(tm * 1000)
    fl.append(f'[{k}:a]volume={vol},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{k}]'); lab.append(f'[s{k}]')
fl.append(''.join(lab) + f'amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{TOTAL},alimiter=limit=0.8:level=false[out]')
subprocess.run(cmd + ['-filter_complex', ';'.join(fl), '-map', '[out]', '-ar', '48000', '-ac', '2', '-y', 'assets/mix.wav'], check=True)
print('hook 0–', r(TH), '· supers', NS[0], '· levels 4 · B-roll', SEGS, '· subs', len(ch), '· tweens', len(js), '· sfx', len(SFX))
