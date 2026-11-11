#!/usr/bin/env python3
"""clip4-journal — ทดลองสไตล์ใหม่ให้คลิป TikTok ชุด 031026 (คลิปที่ 4: รับ Feedback / เสื้อ Jacket)

โครง + จังหวะ เลียนแบบคลิป 2 ของทีม ("หัวหน้ามือใหม่ Draft1"):
  ปก 3.5 วิ → คนพูดเต็มจอ → ช่วง B-roll ~4–5 วิ = พื้นกระดาษขยำ + การ์ดมุมมน + หน้าคนพูดในวงกลมทับขอบล่าง
ภาพในการ์ด เปลี่ยนจากคอลลาจภาพนิ่ง เป็นเส้นหมึกวาดสด + ระบายมาร์กเกอร์ (MinuteEarth + visual journal ของพี่แม็ค)
ข้อความทั้งหมดใช้ Anuphan

รัน: python3 gen.py  (สร้าง index.html + assets/mix.wav ใหม่ทุกครั้ง — ห้ามแก้ index.html ตรง ๆ)
เวลาทุกจุดมาจาก at('วลีที่พูด') ใน work/scribe.json — ห้ามเดาตัวเลข"""
import json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, 'work'); from align import at

# ไฟล์ export จาก AI PR ยาว 82 วิ แต่หลัง 68.5 วิเป็นจอดำล้วน (คำสุดท้ายจบ 68.42)
# และคลิป 4 บนไทม์ไลน์ 0310 ก็ยาว 68.53 วิ — ตัดจบตรงนี้
TOTAL = 68.5
# สี CI ของ BASE ทดลอง 2 แบบ: navy = การ์ดกรมท่า · ember = การ์ดส้มแดง (ดู style.css)
THEME = os.environ.get('THEME', 'navy')

js = []; html = []; SFX = []
def tw(s): js.append(s)
def r(x): return round(x, 3)
def fx(t, kind, vol=None):
    v = {'swoosh': 0.30, 'click': 0.45, 'thump': 0.65, 'pen': 0.32}[kind] if vol is None else vol
    SFX.append((r(max(0, t)), kind, v))
def draw(sel, t, d=0.5, ease='power1.inOut', ghost=True):
    tw(f"tl.fromTo('{sel}',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{d},ease:'{ease}'}},{r(t)});")
    if ghost and sel.startswith('#') and ' ' not in sel and ',' not in sel:
        # เส้นซ้ำบาง ๆ วาดตามหลังเล็กน้อย — คนจริงลากทับเส้นเดิมไม่ตรงเป๊ะเสมอ
        tw(f"tl.fromTo('{sel}-g',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{r(d*1.15)},ease:'{ease}'}},{r(t + 0.1)});")
def pop(sel, t, d=0.35, frm='y:24,opacity:0', to='y:0,opacity:1', ease='back.out(1.6)'):
    tw(f"tl.fromTo('{sel}',{{{frm}}},{{{to},duration:{d},ease:'{ease}'}},{r(t)});")
def swipe(sel, t, d=0.35):
    """ระบายมาร์กเกอร์ — ปาดจากซ้ายไปขวาเหมือนลากปากกาเมจิก"""
    tw(f"tl.fromTo('{sel}',{{scaleX:0,opacity:.9,transformOrigin:'0% 50%'}},{{scaleX:1,opacity:.9,duration:{d},ease:'power2.out'}},{r(t)});")
def splat(sel, t):
    """รอยเปื้อน/ตราประทับ กระแทกลงมา + เสียงตึ้บ"""
    tw(f"tl.fromTo('{sel}',{{scale:2.2,opacity:0,transformOrigin:'50% 50%'}},{{scale:1,opacity:.9,duration:0.2,ease:'power4.in'}},{r(t)});")
    fx(t, 'thump', 0.5)
def shake(sel, t, n=5, dx=9):
    tw(f"tl.to('{sel}',{{x:{dx},duration:0.06,yoyo:true,repeat:{n},ease:'none'}},{r(t)});")

INK = 'pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"'
CLS = {'red': 'acc', 'grn': 'ok'}       # สีจริงของ acc/ok ขึ้นกับธีม (style.css)
def ink(i, d, cls=''):
    c = ' '.join(CLS.get(x, x) for x in cls.split())
    return (f'<path class="ink {c}" id="{i}" {INK} d="{d}"/>'
            f'<path class="ink {c} ghost" id="{i}-g" {INK} d="{d}"/>')
def guide(i, d):
    """เส้นร่างจาง ๆ ก่อนวาดจริง — แบบพิมพ์เขียวต้องมีเส้นช่วยเสมอ"""
    return f'<path class="ink guide" id="{i}" {INK} d="{d}"/>'
def mk(i, d, color):
    return f'<path class="mk {color}" id="{i}" d="{d}" style="opacity:0"/>'
JACKET = 'M110 34 L165 70 L220 34 L292 74 L268 168 L236 156 L236 348 L94 348 L94 156 L62 168 L38 74 Z'
JK_MID = 'M165 70 L165 348'
JK_COLLAR = 'M110 34 L165 148 L220 34'
TEAR = 'M100 300 l16 -14 l12 16 l16 -14 l12 16 l16 -14'

# ============================== ปก 0–3.5 วิ ==============================
html.append('''
    <div id="cover">
      <div id="cv-black"></div>
      <img id="cv-grad" src="assets/cover-gradient.png" alt="">
      <div id="cv-t1">โดนฟีดแบ็ก</div>
      <div id="cv-t2">ทำไมถึงเจ็บจี๊ด ?</div>
      <img id="cv-ul" src="assets/cover-swash.png" alt="">
    </div>''')
# ชื่อเรื่องต้องเห็นตั้งแต่เฟรมแรก — TikTok ใช้เฟรมแรกเป็นภาพปก
pop('#cv-t2', 0.3, 0.4, 'y:30,opacity:0', 'y:0,opacity:1', 'power3.out'); fx(0.3, 'click', 0.35)
# เส้นใต้ = ภาพจาก cover font.png ของทีม เลยใช้วิธีปาดเผยแทนการวาดเส้น
tw(f"tl.fromTo('#cv-ul',{{opacity:1,clipPath:'inset(0 100% 0 0)'}},{{opacity:1,clipPath:'inset(0 0% 0 0)',duration:0.45,ease:'power2.out'}},{r(0.6)});")
fx(0.0, 'swoosh', 0.22)
tw(f"tl.to('#cover',{{opacity:0,duration:0.25,ease:'power1.in'}},{r(3.45)});")

# ============================== ชั้น B-roll ที่ใช้ร่วมกัน ==============================
html.append('''
    <svg id="paperbg" width="1080" height="1920" viewBox="0 0 1080 1920">
      <filter id="crumple" x="0" y="0" width="100%" height="100%">
        <feTurbulence type="fractalNoise" baseFrequency="0.0065 0.009" numOctaves="4" seed="11" result="n"/>
        <feDiffuseLighting in="n" lighting-color="#f1efea" surfaceScale="2.4" result="lit"><feDistantLight azimuth="230" elevation="56"/></feDiffuseLighting>
      </filter>
      <rect width="1080" height="1920" filter="url(#crumple)"/>
    </svg>''')
tw("tl.set('#cam',{opacity:0,scale:0.5,transformOrigin:'50% 50%'},0);")

BROLL = []
def broll(n, t0, t1, last=False):
    """เปิด/ปิดช่วง B-roll — พื้นกระดาษ + การ์ดของช่วงนี้ + วงกลมหน้าคนพูด"""
    BROLL.append((t0, TOTAL if last else t1))
    tw(f"tl.to('#paperbg',{{opacity:1,duration:0.14}},{r(t0)});")
    tw(f"tl.fromTo('#b{n}',{{opacity:0,y:80,scale:0.94,transformOrigin:'50% 50%'}},{{opacity:1,y:0,scale:1,duration:0.42,ease:'back.out(1.4)'}},{r(t0)});")
    tw(f"tl.to('#cam',{{opacity:1,scale:1,duration:0.42,ease:'back.out(1.8)'}},{r(t0 + 0.12)});")
    fx(t0, 'swoosh')
    if last:
        return                                   # ช่วงสุดท้ายค้างไว้จนจบคลิป
    tw(f"tl.to('#b{n}',{{opacity:0,y:-50,duration:0.22,ease:'power2.in'}},{r(t1 - 0.22)});")
    tw(f"tl.to('#cam',{{opacity:0,scale:0.6,duration:0.22,ease:'power2.in'}},{r(t1 - 0.22)});")
    tw(f"tl.to('#paperbg',{{opacity:0,duration:0.18}},{r(t1 - 0.18)});")

# ---------- B1 · เราผูกตัวตนไว้กับผลงาน ----------
BL = 'M55 360 C 48 195, 380 180, 392 352 C 404 525, 70 548, 55 360 Z'
BR = 'M498 356 C 492 190, 828 188, 836 360 C 844 532, 506 540, 498 356 Z'
html.append(f'''
    <div class="card" id="b1"><div class="stage">
      <svg class="dd" width="890" height="820" viewBox="0 0 890 820">
        {mk('b1-m1', BL, 'y')}{ink('b1-o1', BL)}
        {mk('b1-m2', BR, 't')}{ink('b1-o2', BR)}
        {ink('b1-r1', 'M392 330 C 420 290, 432 380, 445 330 S 475 290, 498 336', 'red')}
        {ink('b1-r2', 'M394 380 C 420 420, 432 330, 445 378 S 475 420, 498 380', 'red')}
        {ink('b1-z1', 'M196 92 l28 36 l-24 8 l30 44', 'red')}
        {ink('b1-z2', 'M636 88 l28 36 l-24 8 l30 44', 'red')}
      </svg>
      <div class="lab xl" id="b1-l1" style="left:103px;top:482px;width:240px">ตัวตน<small>IDENTITY</small></div>
      <div class="lab xl" id="b1-l2" style="left:547px;top:482px;width:240px">ผลงาน<small>BEHAVIOR</small></div>
      </div>
    </div>''')
t0 = at('เรามักจะเอาผลลัพธ์ของพฤติกรรม') + 1.7      # 9.56 · เข้าช่วงพอดีตอนพูดคำว่า "พฤติกรรม"
broll(1, t0, at('ทำให้เราจิตตก') + 0.65)
draw('#b1-o1', t0 + 0.3, 0.6); fx(t0 + 0.3, 'pen')
swipe('#b1-m1', t0 + 0.8)
pop('#b1-l1', t0 + 0.9, 0.3)
draw('#b1-o2', t0 + 1.1, 0.6); fx(t0 + 1.1, 'pen')
swipe('#b1-m2', t0 + 1.6)
pop('#b1-l2', t0 + 1.7, 0.3)
t = at('Identityของเรากับพฤติกรรม')               # เชือกมัดตรงคำว่า Identity
draw('#b1-r1', t, 0.45); draw('#b1-r2', t + 0.15, 0.45); fx(t, 'pen')
t = at('ทำให้เราจิตตก')                          # มัดอยู่ด้วยกัน = สะเทือนพร้อมกัน
shake('#b1-o1,#b1-o1-g,#b1-m1,#b1-o2,#b1-o2-g,#b1-m2,#b1-l1,#b1-l2', t)
draw('#b1-z1', t, 0.25, 'none'); draw('#b1-z2', t + 0.08, 0.25, 'none'); fx(t, 'thump', 0.45)

# ---------- B2 · แค่เสื้อเปื้อน แต่เราเจ็บ ----------
STAIN1 = 'M120 210 c18 -26 52 -12 46 12 c20 6 6 40 -18 30 c-14 22 -46 4 -36 -16 c-22 -8 -8 -36 8 -26 z'
STAIN2 = 'M205 252 c12 -18 36 -8 32 8 c14 4 4 28 -12 20 c-10 16 -32 2 -24 -12 c-16 -6 -6 -24 4 -16 z'
html.append(f'''
    <div class="card" id="b2"><div class="stage">
      <svg class="dd" width="890" height="820" viewBox="0 0 890 820">
        <g transform="translate(20,60) scale(1.38)">
          {mk('b2-mk', JACKET, 't')}{ink('b2-j1', JACKET)}{ink('b2-j2', JK_MID)}{ink('b2-j3', JK_COLLAR)}
          {mk('b2-s1', STAIN1, 'b')}{mk('b2-s2', STAIN2, 'b')}
          {ink('b2-tear', TEAR, 'red')}
        </g>
        {guide('b2-dt', 'M72 62 L72 100 M423 62 L423 100')}
        {ink('b2-dm', 'M78 82 L417 82 M78 82 l16 -9 M78 82 l16 9 M417 82 l-16 -9 M417 82 l-16 9', 'red thin')}
        {ink('b2-a1', 'M500 168 C 430 178, 320 250, 238 340 M238 340 l30 -6 M238 340 l4 -30', 'red')}
        {ink('b2-a2', 'M500 440 C 430 448, 360 452, 300 456 M300 456 l26 -14 M300 456 l26 14', 'red')}
        <g id="b2-fig">
          {ink('b2-f1', 'M690 470 m-36 0 a36 36 0 1 0 72 0 a36 36 0 1 0 -72 0')}
          {ink('b2-f2', 'M690 506 L690 610 M646 548 L734 548 M690 610 L658 690 M690 610 L722 690')}
        </g>
        {ink('b2-dn', 'M800 450 L800 660 M800 660 l-18 -24 M800 660 l18 -24', 'red')}
      </svg>
      <div class="dim" id="b2-dl" style="left:97px;top:196px;width:300px">แค่เสื้อ 1 ตัว</div>
      <div class="lab red xl" id="b2-l1" style="left:515px;top:300px;width:240px;text-align:left">เปื้อน!</div>
      <div class="lab red xl" id="b2-l2" style="left:515px;top:574px;width:240px;text-align:left">ขาด!</div>
      <div class="lab" id="b2-l3" style="left:560px;top:880px;width:300px">ตัวเราด้อยค่า</div>
      </div>
    </div>''')
t0 = at('มันเปื้อนนะมันขาดนะ') - 0.3
broll(2, t0, at('ตัวเราอ่ะด้อยค่าลงไปเลย') + 2.9)
# เสื้อเป็นภาพที่พูดถึงมาตั้งแต่ 15 วิ — วาดเร็ว ๆ ให้มีอยู่ก่อนรอยเปื้อนกระแทก
draw('#b2-j1', t0 + 0.05, 0.4); draw('#b2-j2', t0 + 0.25, 0.2); draw('#b2-j3', t0 + 0.3, 0.2)
swipe('#b2-mk', t0 + 0.35, 0.3)
draw('#b2-dt', t0 + 0.5, 0.25, ghost=False); draw('#b2-dm', t0 + 0.6, 0.35); pop('#b2-dl', t0 + 0.75, 0.3)
t = at('มันเปื้อนนะมันขาดนะ')
splat('#b2-s1', t + 0.05); splat('#b2-s2', t + 0.22)
draw('#b2-a1', t + 0.1, 0.3); pop('#b2-l1', t + 0.25, 0.25)
t = at('มันขาดนะ')
draw('#b2-tear', t, 0.35); fx(t, 'pen')
draw('#b2-a2', t + 0.1, 0.3); pop('#b2-l2', t + 0.25, 0.25)
t = at('ตัวเราอ่ะด้อยค่าลงไปเลย')
draw('#b2-f1', t - 0.6, 0.3); draw('#b2-f2', t - 0.35, 0.35)
# คำติพูดถึง "เสื้อ" แต่คนที่หดลงคือ "ตัวเรา" — ภาพต้องเล่าความผิดฝาผิดตัวนี้
tw(f"tl.to('#b2-fig',{{scale:0.5,svgOrigin:'690 690',duration:0.7,ease:'power3.in'}},{r(t + 0.1)});")
draw('#b2-dn', t + 0.1, 0.5); fx(t + 0.1, 'swoosh', 0.2)
pop('#b2-l3', t + 0.7, 0.3)

# ---------- B3 · คำติ ไม่ใช่ตัวเรา ----------
html.append(f'''
    <div class="card" id="b3"><div class="stage">
            <div class="big" id="b3-w1" style="top:250px">FEEDBACK</div>
      <svg class="dd" width="890" height="820" viewBox="0 0 890 820">
        {ink('b3-box', 'M166 70 C 330 64, 560 66, 726 70 L722 206 C 560 210, 330 208, 162 204 Z', 'red')}
        {ink('b3-e1', 'M385 296 L505 296')}{ink('b3-e2', 'M385 336 L505 336')}
        {ink('b3-x', 'M480 252 L410 380', 'red')}
      </svg>
      <div class="big" id="b3-w2" style="top:560px">ตัวเรา</div>
      <div class="mkbar t" id="b3-ul" style="left:300px;top:688px;width:290px;height:16px;opacity:0"></div>
      <div class="sub" id="b3-ws" style="top:716px">SELF WORTH</div>
      </div>
    </div>''')
t0 = at('Feedbackนั้นไม่ใช่ตัวตนของเรา') - 0.26
broll(3, t0, at('มันไม่ใช่SelfWorth') + 3.0)
t = at('Feedbackนั้นไม่ใช่ตัวตนของเรา')
draw('#b3-box', t + 0.1, 0.55); fx(t + 0.1, 'pen', 0.25); pop('#b3-w1', t, 0.35); fx(t, 'click')
draw('#b3-e1', t + 0.6, 0.22); draw('#b3-e2', t + 0.75, 0.22); fx(t + 0.6, 'pen', 0.25)
pop('#b3-w2', t + 0.95, 0.35); swipe('#b3-ul', t + 1.15, 0.3); pop('#b3-ws', t + 1.2, 0.3)
t = at('มันไม่ใช่SelfWorth')                     # ขีด = เป็น ≠ ตรงคำว่า "ไม่ใช่"
draw('#b3-x', t, 0.3, 'power2.out'); fx(t, 'thump', 0.5)

# ---------- B4 · ซ่อมที่เสื้อ ไม่ใช่ที่ตัวเรา ----------
STITCH = 'M96 318 l10 -26 M120 318 l10 -26 M144 318 l10 -26 M168 318 l10 -26 M192 318 l10 -26'
CHECK = 'M0 44 L22 64 L62 10'
STAR = lambda x, y, s: (f'M{x} {y-s} L{x+s*.22} {y-s*.22} L{x+s} {y} L{x+s*.22} {y+s*.22} '
                        f'L{x} {y+s} L{x-s*.22} {y+s*.22} L{x-s} {y} L{x-s*.22} {y-s*.22} Z')
html.append(f'''
    <div class="card" id="b4"><div class="stage">
      <svg class="dd" width="890" height="820" viewBox="0 0 890 820">
        {ink('b4-tb', 'M80 652 L810 652')}
        <g transform="translate(150,180) scale(1.3)">
          {mk('b4-mk', JACKET, 't')}{ink('b4-j1', JACKET)}{ink('b4-j2', JK_MID)}{ink('b4-j3', JK_COLLAR)}
          {ink('b4-tear', TEAR, 'red')}
          {ink('b4-st', STITCH, 'thin')}
        </g>
        {ink('b4-nd', 'M610 520 L428 592 M610 520 m-8 -4 a10 6 -22 1 0 15 7 a10 6 -22 1 0 -15 -7', 'thin')}
        {ink('b4-th', 'M610 520 C 670 470, 730 520, 790 460', 'thin')}
        <g transform="translate(670,100) scale(1.6)">{ink('b4-ck', CHECK, 'grn')}</g>
        {mk('b4-s1', STAR(110, 200, 34), 'y')}{ink('b4-s1o', STAR(110, 200, 34), 'thin')}
        {mk('b4-s2', STAR(590, 200, 26), 'y')}{ink('b4-s2o', STAR(590, 200, 26), 'thin')}
        {mk('b4-s3', STAR(100, 560, 22), 'y')}{ink('b4-s3o', STAR(100, 560, 22), 'thin')}
      </svg>
      <div class="lab grn" id="b4-l1" style="left:610px;top:420px;width:260px">แก้ที่เสื้อ</div>
      </div>
    </div>''')
t0 = at('แล้วแก้ที่พฤติกรรมนั้น') - 0.26
broll(4, t0, at('เลือกสวมJacketตัวใหม่') + 0.85)
draw('#b4-tb', t0 + 0.05, 0.3)
draw('#b4-j1', t0 + 0.1, 0.4); draw('#b4-j2', t0 + 0.3, 0.2); draw('#b4-j3', t0 + 0.35, 0.2)
swipe('#b4-mk', t0 + 0.35, 0.3); draw('#b4-tear', t0 + 0.4, 0.2)
t = at('แล้วแก้ที่พฤติกรรมนั้น')
draw('#b4-nd', t + 0.2, 0.3); draw('#b4-th', t + 0.35, 0.3)
draw('#b4-st', t + 0.5, 1.1, 'none'); fx(t + 0.5, 'pen'); fx(t + 1.0, 'pen', 0.25)
t = at('แก้ที่Jacketตัวนั้น')
draw('#b4-ck', t, 0.35, 'power2.out'); fx(t, 'pen'); pop('#b4-l1', t + 0.2, 0.3)
t = at('เลือกสวมJacketตัวใหม่')
for i, dt in [(1, 0), (2, 0.12), (3, 0.24)]:
    tw(f"tl.fromTo('#b4-s{i},#b4-s{i}o,#b4-s{i}o-g',{{scale:0,opacity:0,transformOrigin:'50% 50%'}},{{scale:1,opacity:1,strokeDashoffset:0,duration:0.3,ease:'back.out(2.4)'}},{r(t - 0.6 + dt)});")
fx(t - 0.6, 'click', 0.35)

# ---------- B5 · Separate Self Worth (ค้างถึงจบคลิป) ----------
DASH = ' '.join(f'M445 {y} L445 {y + 36}' for y in range(30, 590, 62))   # จบเหนือแถบดำสรุป ไม่ให้ทะลุแถบ
HEART = 'M220 250 C 220 190, 130 180, 120 245 C 110 315, 210 355, 220 410 C 230 355, 330 315, 320 245 C 310 180, 220 190, 220 250 Z'
html.append(f'''
    <div class="card" id="b5"><div class="stage">
      <svg class="dd" width="890" height="820" viewBox="0 0 890 820">
        {ink('b5-dl', DASH, 'red')}
        {mk('b5-hm', HEART, 'c')}{ink('b5-h', HEART)}
        <g transform="translate(555,140) scale(0.78)">{mk('b5-jm', JACKET, 't')}{ink('b5-j1', JACKET)}{ink('b5-j2', JK_COLLAR)}</g>
      </svg>
      <div class="lab" id="b5-l1" style="left:40px;top:620px;width:360px">คุณค่าในตัวเรา<small>SELF WORTH</small></div>
      <div class="lab" id="b5-l2" style="left:500px;top:620px;width:340px">สิ่งที่เราทำ<small>BEHAVIOR</small></div>
      </div>
    </div>''')
t0 = at('ต้องSeparateSelfWorth') - 0.26
broll(5, t0, TOTAL, last=True)
t = at('ต้องSeparateSelfWorth')
draw('#b5-dl', t + 0.1, 0.6, 'none'); fx(t + 0.1, 'pen')
draw('#b5-h', t + 0.45, 0.55); swipe('#b5-hm', t + 0.9, 0.3); pop('#b5-l1', t + 0.95, 0.3)
draw('#b5-j1', t + 0.85, 0.45); draw('#b5-j2', t + 1.15, 0.2); swipe('#b5-jm', t + 1.25, 0.3); pop('#b5-l2', t + 1.3, 0.3)
fx(t + 0.85, 'pen', 0.25)
t = at('แยกคุณค่าของตัวเรา')

# ============================== ซับ ==============================
# ขึ้นเฉพาะตอนคนพูดเต็มจอ — ช่วงปกกับช่วง B-roll ไม่ขึ้น (สั่งจากผู้ใช้)
COVER_END = 3.5
subs = [x for x in json.load(open('work/subs.json', encoding='utf-8')) if 'start' in x]
# คำพิมพ์ผิดใน 04.SRT ต้นฉบับของทีม — แก้ตามเสียงจริงใน work/scribe.json (ไม่ได้เดา)
TYPO = {'ที่เราสวมทำไว้': 'ที่เราสวมทับไว้', 'เราถึงจะจำต้อง': 'เราถึงจะต้อง'}
for x in subs:
    for a_, b_ in TYPO.items(): x['text'] = x['text'].replace(a_, b_)
hide = [(0, COVER_END)] + BROLL
def visible(a, b):
    """ตัดช่วงที่ทับปก/B-roll ออก เหลือช่วงที่ซับขึ้นได้จริง"""
    spans = [(a, b)]
    for h0, h1 in hide:
        nxt = []
        for x0, x1 in spans:
            if x1 <= h0 or x0 >= h1: nxt.append((x0, x1)); continue
            if x0 < h0: nxt.append((x0, h0))
            if x1 > h1: nxt.append((h1, x1))
        spans = nxt
    # สั้นกว่าครึ่งวินาที = ขึ้นแวบแล้วการ์ดเด้งทับทันที ดูเหมือนกะพริบ ไม่ขึ้นเลยดีกว่า
    return [(x0, x1) for x0, x1 in spans if x1 - x0 >= 0.5]
sub_html = []
for k, x in enumerate(subs):
    nxt = subs[k + 1]['start'] if k + 1 < len(subs) else TOTAL
    end = nxt if nxt - x['end'] < 0.6 else x['end'] + 0.3      # ค้างจนบรรทัดถัดไป ถ้าช่องว่างสั้น จะได้ไม่กะพริบ
    spans = visible(x['start'], end)
    if not spans: continue
    sub_html.append(f'<div class="sb" id="sb{k}">{x["text"]}</div>')
    for a, b in spans:
        tw(f"tl.set('#sb{k}',{{opacity:1}},{r(a)});")
        tw(f"tl.set('#sb{k}',{{opacity:0}},{r(b)});")
html.append(f'''
    <div id="subs">{''.join(sub_html)}</div>''')

# ============================== ประกอบ HTML ==============================
doc = f'''<!doctype html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
{open('style.css').read()}
  </style>
</head>
<body>
  <div id="root" class="theme-{THEME}" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
    <svg width="0" height="0" style="position:absolute">
      <filter id="rough" filterUnits="userSpaceOnUse" x="-400" y="-400" width="1800" height="1800"><feTurbulence type="fractalNoise" baseFrequency="0.022" numOctaves="2" seed="4" result="t"/>
        <feDisplacementMap in="SourceGraphic" in2="t" scale="4" xChannelSelector="R" yChannelSelector="G"/></filter>
      <filter id="rough2" filterUnits="userSpaceOnUse" x="-400" y="-400" width="1800" height="1800"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="19" result="t"/>
        <feDisplacementMap in="SourceGraphic" in2="t" scale="7" xChannelSelector="G" yChannelSelector="R"/></filter>
      <pattern id="hatchW" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><line x1="0" y1="0" x2="0" y2="16" stroke="#FFFFFF" stroke-width="3" opacity=".8"/></pattern>
      <pattern id="hatchA" width="14" height="14" patternUnits="userSpaceOnUse" patternTransform="rotate(-38)"><line x1="0" y1="0" x2="0" y2="14" style="stroke:var(--hatchA)" stroke-width="3" opacity=".85"/></pattern>
      <pattern id="xhatch" width="9" height="9" patternUnits="userSpaceOnUse" patternTransform="rotate(30)"><path d="M0 0 L0 9 M0 0 L9 0" stroke="#FFFFFF" stroke-width="2.6" opacity=".9"/></pattern>
    </svg>
    <video id="talk" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-media-start="0" muted playsinline src="assets/talk.mp4"></video>
{''.join(html)}
    <div id="cam"><video id="camv" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="3" data-media-start="0" muted playsinline src="assets/cam.mp4"></video></div>
    <audio id="voice" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-volume="1" src="assets/mix.wav"></audio>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join('    ' + l for l in js)}
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
'''
open('index.html', 'w').write(doc)

# ===== มิกซ์: เสียงพูด + SFX (ไม่มีเพลง) =====
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
if not os.path.exists('assets/voice.wav'):
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', 'assets/talk.mp4', '-t', str(TOTAL), '-vn',
                    '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', '-y', 'assets/voice.wav'], check=True)
FILES = {'swoosh': 'assets/sfx/swoosh.mp3', 'click': 'assets/sfx/click.mp3', 'thump': 'assets/sfx/thump.wav', 'pen': 'assets/sfx/pen.wav'}
cmd = [FF, '-nostdin', '-v', 'error', '-i', 'assets/voice.wav']
fl = ["[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v]"]; labels = ['[v]']
for k, (tm, kind, vol) in enumerate(SFX, 1):
    cmd += ['-i', FILES[kind]]; ms = int(tm * 1000)
    fl.append(f'[{k}:a]volume={vol},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{k}]'); labels.append(f'[s{k}]')
fl.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{TOTAL},alimiter=limit=0.85[out]')
cmd += ['-filter_complex', ';'.join(fl), '-map', '[out]', '-ar', '48000', '-ac', '2', '-y', 'assets/mix.wav']
subprocess.run(cmd, check=True)
print('theme', THEME, '· tweens', len(js), '· sfx', len(SFX), '· total', TOTAL)
