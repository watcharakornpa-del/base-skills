# ตัวอย่างฉาก: C5398 COM-ML-02 Quibi (183.7 วิ) · FIX [["ศาลตั้งต้น","ฐานตั้งต้น"],["Dreamworks อืม","Dreamworks"]] · FACE_CROP 1000:1000:40:520
# มุมกล้องหัวต่ำ → style.css ของคลิปนี้ต่อท้าย .lv { top: 1610px; } · ใช้: scripts/splice.py
# ===== 1 · Text Hook =====
def hook(t_end, words):
    body = ''.join(f'<div class="hk {c}" id="hw{i}" style="top:{y}px">{w}</div>' for i, (t, w, c, y) in enumerate(words))
    html.append(f'<div id="hook"><div class="dim"></div>{body}</div>')
    for i, (t, w, c, y) in enumerate(words):
        big = c in ('hk-xl', 'hk-em')
        tw(f"tl.fromTo('#hw{i}',{{opacity:0,scale:{1.4 if big else 0.8},y:{0 if big else 16}}},{{opacity:1,scale:1,y:0,duration:{0.24 if big else 0.18},ease:'{'back.out(2.2)' if big else 'power2.out'}'}},{r(t)});")
        fx(t, 'thump' if big else 'click', 0.55 if big else 0.3)
    tw(f"tl.to('#hook',{{opacity:0,duration:0.2,ease:'power2.in'}},{r(t_end - 0.2)});")
    HIDE_SUBS.append((0, t_end))
TH = at('ลองไปจับ') + 0.8
hook(TH, [
    # (ปกแบบเก่า · ปัจจุบันใช้ชื่อคลิปจากสคริปต์ ดู template/gen.py)
    (at('ทุกคนน่าจะเริ่มเอา'), 'ทุกคนน่าจะเริ่มใช้', 'hk-s', 700),
    (at('Three'), '3 Certainties', 'hk-xl', 800),
    (at('แกนความมั่นใจ'), 'แกนความมั่นใจ', 'hk-em', 980),
])

# ===== 2 · Super =====
NS = [0]
def sup(t0, t1, rows, pops):
    NS[0] += 1
    html.append(f'<div class="super">' + ''.join(f'<div class="row" style="top:{y}px">{h}</div>' for h, y in rows) + '</div>')
    for k, (id, t) in enumerate(pops): pop(id, t, 'thump' if k == 0 else 'click'); out(id, t1 - 0.2)
    HIDE_SUBS.append((t0, t1))
def pill(id, txt, on=False, fl=False): return f'<div class="pill{" on" if on else ""}" id="{id}">{flame(30, "#fff" if on else "#EA3A1F") if fl else ""}{txt}</div>'
def chip(id, ttl, lbl='', hot=False):
    return f'<div class="chip{" hot" if hot else ""}" id="{id}">{f"<div class=lbl>{lbl}</div>" if lbl else ""}<div class="ttl">{ttl}</div></div>'

sup(at('ไม่ได้อยู่แค่'), at('ถ้าเราเข้าใจมัน') - 0.1, [(chip('k1', 'ไม่ได้อยู่แค่ใน<span class="red">ห้องเจรจา</span>'), 200)], [('k1', at('ไม่ได้อยู่แค่'))])
sup(at('Study') - 0.3, at('Founder') - 0.3, [(pill('k2a', 'CASE STUDY', on=True), 110), (chip('k2b', '<span class="en">Quibi</span>', lbl='STARTUP · 2020'), 220)],
    [('k2a', at('Study') - 0.3), ('k2b', at('Quibi'))])
sup(at('Concept'), at('ทั้งสองคนเนี้ย') - 0.1, [(pill('k3a', 'QUICK BITE', on=True), 110), (chip('k3b', 'ซีรีส์สั้น 5 นาที · <span class="en red">Subscription</span>'), 230)],
    [('k3a', at('Quick')), ('k3b', at('ยาวห้านาที'))])
sup(at('ศาลตั้งต้น'), at('เขาระดมทุนมาเสร็จ') - 0.1, [(chip('k4', 'จุดเริ่มต้น<span class="red">ดีมาก</span>', lbl='CREDENTIAL · BRAND'), 190)], [('k4', at('ศาลตั้งต้น'))])
sup(at('ถึงแม้ว่าความมั่นใจ'), at('สิ่งที่จะเป็น') - 0.1, [(chip('k5', '2 แกนสูงแค่ไหน<br>ก็<span class="red">ชดเชยแกนที่ต่ำไม่ได้</span>'), 130)], [('k5', at('ถึงแม้ว่าความมั่นใจ') + 0.3)])
sup(at('Takeaway'), at('คุณจะรู้ว่ามันทดแทน') - 0.1, [(pill('k6a', 'TAKEAWAY', on=True), 110), (chip('k6b', 'ใช้ <span class="en red">3 Certainty</span> ในชีวิตจริง'), 230)],
    [('k6a', at('Takeaway')), ('k6b', at('อย่าลืมว่าเอาสิ่งนี้'))])

# ===== 4 · B-roll =====
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

# B1 · ผู้ก่อตั้ง 2 คน
a, b = at('Founder') - 0.25, at('แล้วก็ตั้งแพลตฟอร์ม')
broll(a, b, hd('FOUNDERS', 'ผู้ก่อตั้ง<span class="red">ระดับตำนาน</span> 2 คน')
      + '<div class="card pc-card" id="f1" style="top:430px"><div class="lbl">FOUNDER</div><div class="ttl-en">Jeffrey Katzenberg</div><div class="sub-t th">อดีตผู้บริหาร Disney · ผู้ร่วมก่อตั้ง DreamWorks</div></div>'
      + '<div class="card pc-card" id="f2" style="top:710px"><div class="lbl">FOUNDER</div><div class="ttl-en">Meg Whitman</div><div class="sub-t th">อดีต CEO ของ eBay และ HP</div></div>'
      + '<div class="row" style="top:1030px"><div class="pill on" id="f3">ชื่อเสียงระดับโลก</div></div>')
slide('f1', at('Jeffrey'), dx=300); slide('f2', at('Meg'), dx=300); pop('f3', at('ตัวใหญ่ทั้งสองคน'), 'thump')

# B2 · ระดมทุน $1.75B + ผู้ลงทุน + คนดัง
a, b = at('เขาระดมทุนได้ถึง') - 0.2, at('ให้กับแพลตฟอร์มนี้ด้วย') + 1.0
broll(a, b, hd('FUNDRAISING', 'ระดมทุน<span class="red">ก่อนเปิดตัว</span>')
      + '<div class="money" id="mn" style="top:400px">$<span id="mn_v">0.00</span><small>B</small></div>'
      + '<div class="cap" id="cp1" style="top:660px">INVESTORS</div><div class="wrap" style="top:710px">' + pill('i1', 'Disney') + pill('i2', 'NBCUniversal') + pill('i3', 'WarnerMedia') + '</div>'
      + '<div class="cap" id="cp2" style="top:900px">CONTENT</div><div class="wrap" style="top:950px">' + pill('s1', 'Steven Spielberg', fl=True) + pill('s2', 'Jennifer Lopez', fl=True) + pill('s3', 'LeBron James', fl=True) + '</div>')
pop('mn', a + 0.3, None)
tw(f"tl.fromTo('#mn_v',{{textContent:0}},{{textContent:1.75,duration:1.6,ease:'power2.out',snap:{{textContent:0.01}},immediateRender:false}},{r(a + 0.3)});")
fx(at('หนึ่งจุดเจ็ดห้า'), 'thump'); bump('mn', at('หนึ่งจุดเจ็ดห้า') + 1.2, 1.05, False)
tw(f"tl.fromTo('#cp1',{{opacity:0}},{{opacity:1,duration:0.2}},{r(at('นักลงทุนระดับ'))});")
for id, p in (('i1', 'Disney'), ('i2', 'NBC'), ('i3', 'Warner')): pop(id, at(p, after=a + 5))
tw(f"tl.fromTo('#cp2',{{opacity:0}},{{opacity:1,duration:0.2}},{r(at('แล้วก็มีคนดัง'))});")
for id, p in (('s1', 'Steven'), ('s2', 'Jennifer'), ('s3', 'LeBron')): pop(id, at(p))

# B3 · จำนวนผู้ใช้: เป้า 7M → 2.6M → 0.5M → ปิดตัว
a, b = at('เขาตั้งเป้า'), at('นิทานเรื่องนี้') - 0.1
broll(a, b, hd('USERS', 'เป้า 7 ล้านคน… <span class="red">ได้จริงเท่าไหร่?</span>')
      + '<div class="wrap" style="top:360px">' + pill('u4', 'ดูบนทีวีไม่ได้') + pill('u5', 'แคปจอแชร์ไม่ได้') + '</div>'
      + '<div class="bars"><div class="base-ln"></div>' + bar('u1', 40, 520, '7M', 'เป้าปีแรก', goal=True) + bar('u2', 370, 193, '2.6M', 'เปิดตัว เม.ย.')
      + bar('u3', 700, 40, '0.5M', '6 เดือนต่อมา') + '</div>'
      + '<div class="row" style="top:1230px"><div class="pill on" id="u6">ปิดตัว · ต.ค. 2020</div></div>')
grow('u1', at('เจ็ดล้านคน')); grow('u2', at('สองจุดหกล้านคน'))
pop('u4', at('ดูบนทีวี')); pop('u5', at('แคปหน้าจอ'))
grow('u3', at('เหลือห้าแสน'), 'thump'); pop('u6', at('เจ๊ง'), 'thump')
tw(f"tl.to(['#u1','#u2','#u3'],{{opacity:0.35,duration:0.3}},{r(at('เจ๊ง'))});")

# B4 · 3 Certainties: เชื่อแค่ 2 ใน 3 แกน
a, b = at('เพราะเขาดันไปเชื่อ') - 0.1, at('นี้เนอะจะเป็นตัวพิสูจน์') - 0.1
broll(a, b, hd('3 CERTAINTIES', 'นักลงทุนเชื่อแค่ <span class="red">2 ใน 3</span> แกน')
      + meter('m1', 430, 'แกน 1', 'YOU', 'ตัวบุคคล') + meter('m2', 620, 'แกน 2', 'COMPANY', 'แบรนด์ / องค์กร')
      + meter('m3', 810, 'แกน 3', 'PROPOSAL', 'ข้อเสนอ', low=True)
      + '<div class="row" style="top:1040px"><div class="pill on" id="m4"><span class="en">Problem–Solution Fit ?</span></div></div>')
mset0('m1', 'm2', 'm3')
pop('m1', a + 0.3, None); mfill('m1', at('เชื่อในตัวบุคคล'), 0, 95)
pop('m2', a + 0.5, None); mfill('m2', at('เชื่อในตัวของแบรนด์'), 0, 95)
pop('m3', at('สิ่งที่เขาลืมดู'), 'thump'); mfill('m3', at('Proposal'), 0, 15)
pop('m4', at('Fit'), 'click')

# B5 · ปิดท้าย: เติมให้เต็มทั้ง 3 แกน
a = at('คุณจะรู้ว่ามันทดแทน') - 0.1
broll(a, TOTAL, hd('TAKEAWAY', 'เติมให้<span class="red">เต็มทั้ง 3 แกน</span>')
      + meter('n1', 430, 'แกน 1', 'YOU', 'ตัวบุคคล') + meter('n2', 620, 'แกน 2', 'COMPANY', 'แบรนด์ / องค์กร') + meter('n3', 810, 'แกน 3', 'PROPOSAL', 'ข้อเสนอ')
      + '<div class="row" style="top:1040px"><div class="pill on" id="n4">ลดความเสี่ยงในการปิด <span class="en">&nbsp;Deal</span></div></div>')
mset0('n1', 'n2', 'n3')
for k, id in enumerate(('n1', 'n2', 'n3')): pop(id, a + 0.3 + 0.15 * k, None)
for k, id in enumerate(('n1', 'n2', 'n3')): mfill(id, at('ให้เต็ม') + 0.25 * k, 0, 100, 0.7)
fx(at('ให้เต็ม'), 'pen'); pop('n4', at('ลดความเสี่ยง'), 'thump')

