# ตัวอย่างฉาก: C5399 COM-ML-03 Do & Don't (140.85 วิ) · FIX [["ความมั่นความมั่นใจ","ความมั่นใจ"]] · FACE_CROP 1000:1000:40:520
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
TH = at('แล้วก็วันนี้')
hook(TH, [
    # (ปกแบบเก่า · ปัจจุบันใช้ชื่อคลิปจากสคริปต์ ดู template/gen.py)
    (at('ทุกคนน่าจะเริ่มเอา'), 'ทุกคนน่าจะเริ่มใช้', 'hk-s', 700),
    (at('mindset'), 'Mindset', 'hk-xl', 800),
    (at('สามแกน'), 'ความมั่นใจ 3 แกน', 'hk-em', 980),
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

sup(at('Recap'), at('อย่างแรกเลย') - 0.1, [(pill('k1a', 'RECAP', on=True), 110), (chip('k1b', '<span class="en">DO &amp; <span class="red">DON\'T</span></span>'), 230)],
    [('k1a', at('Recap')), ('k1b', at('Do'))])
sup(at('สามด้านหรือ'), at('สิ่งที่คุณต้องทำ') - 0.1, [(pill('k2a', 'YOU') + pill('k2b', 'COMPANY') + pill('k2c', 'PROPOSAL'), 200)],
    [('k2a', at('สามด้านหรือ')), ('k2b', at('สามด้านหรือ') + 0.3), ('k2c', at('สามด้านหรือ') + 0.6)])
sup(at('Trust'), at('เราจะไม่ไปด้วย') - 0.1, [(chip('k3', '<span class="en">Trust</span> สำคัญ<span class="red">พอ ๆ กับดีล</span>'), 200)], [('k3', at('Trust'))])

# ===== 3 · การ์ด DO / DON'T ล่างจอ (ค้างทั้งช่วงอธิบาย · ซับยังขึ้น) =====
D2 = at('Doข้อที่สอง'); D3 = at('และสุดท้ายนะครับ'); X1 = at("Don'tเลย"); X2 = at('สองเราจะไม่'); X3 = at('และข้อสุดท้าย')
lvcard('lv1', at('สิ่งที่เป็น') - 0.1, D2 - 0.15, 'DO 1 / 3', 'มอง 3 แกนเป็น Dynamic', 'ความมั่นใจคือ<b class="red">หลอดพลัง</b> เติมได้ ลดได้', 1, 3, 'do')
lvcard('lv2', D2 - 0.1, D3 - 0.15, 'DO 2 / 3', 'ประเมิน 3 แกนก่อนเข้าห้อง', 'ดูว่าเรา<b class="red">อ่อนแกนไหน</b>มากที่สุด', 2, 3, 'do')
lvcard('lv3', D3 - 0.1, at('มาดูสิ่งที่ไม่ควร') - 0.15, 'DO 3 / 3', 'ปิดแกนที่อ่อนที่สุดก่อน', 'ให้เวลากับ<b class="red">แกนที่อ่อน</b>มากกว่าแกนที่มีอยู่แล้ว', 3, 3, 'do')
lvcard('lv4', X1 - 0.1, X2 - 0.15, "DON'T 1 / 3", 'มองการโน้มน้าวเป็น Static', 'Pitch ครั้งเดียวจบ ✕ ต้อง<b class="red">เลี้ยงหลอด</b>ตลอด', 1, 3, 'dont')
lvcard('lv5', X2 - 0.1, X3 - 0.15, "DON'T 2 / 3", 'เตรียมแค่ดีลที่ดีที่สุด', 'ลืมเติม<b class="red">ความมั่นใจในตัวเรา</b> + First Impression', 2, 3, 'dont')
lvcard('lv6', X3 - 0.1, at('ถ้าคุณทำได้คุณจะ') - 0.15, "DON'T 3 / 3", 'ไม่ทำการบ้าน', 'ต้องรู้ว่าเขา<b class="red">ชอบ / ไม่ชอบ</b>อะไร', 3, 3, 'dont')

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
M3 = lambda p, low='': (meter(f'{p}1', 430, 'แกน 1', 'YOU', 'ตัวเรา', low == 1) + meter(f'{p}2', 620, 'แกน 2', 'COMPANY', 'ทีม / องค์กร')
                        + meter(f'{p}3', 810, 'แกน 3', 'PROPOSAL', 'ข้อเสนอ'))

# B1 · หลอดพลังขยับขึ้นลง (Dynamic ไม่ใช่ Yes/No)
a, b = at('ลองดูซิว่าเวลาคุณ') - 0.1, at('นี่คือDo') - 0.1
broll(a, b, hd('DYNAMIC CERTAINTY', 'ความมั่นใจคือ<span class="red">หลอดพลัง</span>') + M3('p')
      + '<div class="row" style="top:1040px"><div class="pill on" id="p4">เติมได้ · ลดได้ · ขยับตลอดบทสนทนา</div></div>')
mset0('p1', 'p2', 'p3')
for k, id in enumerate(('p1', 'p2', 'p3')): pop(id, a + 0.3 + 0.15 * k, None)
t = at('เติมได้'); mfill('p1', t, 0, 70); mfill('p2', t + 0.2, 0, 55); mfill('p3', t + 0.4, 0, 80); fx(t, 'pen')
t = at('ลดได้'); mfill('p1', t, 70, 35); mfill('p3', t + 0.2, 80, 60); fx(t, 'click', 0.3)
t = at('มันขยับ'); mfill('p2', t, 55, 85); mfill('p1', t + 0.6, 35, 65); mfill('p3', t + 1.2, 60, 90); mfill('p2', t + 1.8, 85, 60)
pop('p4', at('มันขยับ') + 0.2, 'thump')

# B2 · ประเมินก่อนเข้าห้อง: แกน YOU ต่ำ → เติมแกนนี้ก่อน
a, b = at('ถ้าคุณสามารถประเมิน') - 0.1, at('และสุดท้ายนะครับ') - 0.1
broll(a, b, hd('ASSESS', 'แกนไหน<span class="red">อ่อนที่สุด?</span>') + M3('q', 1)
      + '<div class="row" style="top:1030px"><div class="chip" id="q4"><div class="ttl">“เขาน่าจะไม่ค่อยไว้ใจฉัน”</div></div></div>'
      + '<div class="row" style="top:1210px"><div class="pill on" id="q5">เติมแกนนี้ก่อน</div></div>')
mset0('q1', 'q2', 'q3')
for k, (id, v) in enumerate((('q1', 25), ('q2', 70), ('q3', 80))): pop(id, a + 0.3 + 0.15 * k, None); mfill(id, a + 0.6 + 0.15 * k, 0, v)
pop('q4', at('คุยกับคน'), 'click'); bump('q1', at('ไม่ค่อยเต็ม'), 1.04)
pop('q5', at('คุณจะได้รู้ว่า'), 'thump'); mfill('q1', at('เติมแกนไหน'), 25, 75, 1.0)

# B3 · ปิดท้าย: เช็กลิสต์ DO ✓ / DON'T ✗
a = at('ถ้าคุณทำได้คุณจะ') - 0.1
items_do = ['มอง 3 แกนเป็น Dynamic', 'ประเมิน 3 แกนก่อนเข้าห้อง', 'ปิดแกนที่อ่อนที่สุดก่อน']
items_no = ['มองการโน้มน้าวเป็น Static', 'เตรียมแค่ดีลที่ดีที่สุด', 'ไม่ทำการบ้าน']
ck = lambda id, y, lbl, items, ic, cls: (f'<div class="card ck" id="{id}" style="top:{y}px"><div class="lbl" style="color:{"#fff" if cls == "y" else "#EA3A1F"}">{lbl}</div>'
                                        + ''.join(f'<div class="it" id="{id}{k}"><span class="ic {cls}">{ic}</span>{t}</div>' for k, t in enumerate(items)) + '</div>')
broll(a, TOTAL, hd('RECAP', 'เช็กก่อนเข้าห้อง<span class="red">ทุกครั้ง</span>') + ck('cd', 400, 'DO', items_do, CHK, 'y') + ck('cn', 780, "DON'T", items_no, CRS, 'n'))
pop('cd', a + 0.3, None); pop('cn', a + 0.5, None)
for k in range(3): pop(f'cd{k}', a + 0.6 + 0.3 * k, 'click', dy=20); pop(f'cn{k}', a + 1.6 + 0.3 * k, 'click', dy=20)

