# ===== 1 · Text Hook =====
# ฉาก: C2676 AI Productivity Clip 2 · AI ไปเอาข้อมูลจากไหน: ค้นเว็บ · Memory · MCP
# Insert ตามชีต LD: ไอคอนแหล่งข้อมูลเติมบนโต๊ะตามจังหวะพูด · Super ค้นเว็บไซต์ · บอกให้ AI อ้างอิงแหล่งข้อมูล · Memory
#   · Model Context Protocol (MCP) · Connector, Plug-in · AI ตรงกลาง + แอปรอบ ๆ ต่อท่อเข้ามา
# (USB-C ในชีต: ผู้พูดสั่งตัดทิ้ง "ไม่เอาประโยคเมื่อกี้" → ใช้ภาพ "ท่อ" ตามที่พูดแทน)
def hook(t_end, words):
    body = ''.join(f'<div class="hk {c}" id="hw{i}" style="top:{y}px">{w}</div>' for i, (t, w, c, y) in enumerate(words))
    html.append(f'<div id="hook"><div class="dim"></div>{body}</div>')
    for i, (t, w, c, y) in enumerate(words):
        big = c in ('hk-xl', 'hk-em')
        tw(f"tl.fromTo('#hw{i}',{{opacity:0,scale:{1.4 if big else 0.8},y:{0 if big else 16}}},{{opacity:1,scale:1,y:0,duration:{0.24 if big else 0.18},ease:'{'back.out(2.2)' if big else 'power2.out'}'}},{r(t)});")
        fx(t, 'thump' if big else 'click', 0.55 if big else 0.3)
    tw(f"tl.to('#hook',{{opacity:0,duration:0.2,ease:'power2.in'}},{r(t_end - 0.2)});")
    HIDE_SUBS.append((0, t_end))
TH = at('หรือContext')
hook(TH, [
    # (ปกแบบเก่า · ปัจจุบันใช้ชื่อคลิปจากสคริปต์ ดู template/gen.py)
    (0.3, 'คลิปที่แล้ว', 'hk-s', 700),
    (at('AI'), 'AI', 'hk-xl', 800),
    (at('ตอบจากสิ่งที่'), 'ตอบจาก', 'hk-s', 960),
    (at('บนโต๊ะ'), 'ของบนโต๊ะ', 'hk-em', 1040),
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

t = at('การค้นหาเว็บไซต์')
sup(t, at('AIตัวใหม่') - 0.1, [(chip('k1', '<span class="th">ค้นเว็บไซต์</span>', 'SOURCE 3', hot=True), 110)], [('k1', t)])
t = at('ใช้เมื่อไหร่ครับ')
sup(t, at('เพราะสิ่งนี้') - 0.1, [(pill('k2a', 'ค้นเว็บ ใช้เมื่อไหร่?', on=True), 110),
    (pill('k2b', 'ข้อมูลล่าสุด') + pill('k2c', 'ข่าว') + pill('k2d', '<span class="en">Trend</span>') + pill('k2e', 'ราคา'), 240)],
    [('k2a', t), ('k2b', at('เวลาที่ต้องการข้อมูลล่าสุด')), ('k2c', at('ข่าวTrend')), ('k2d', at('Trend')), ('k2e', at('ราคา'))])
t = at('อ้างอิงแหล่งข้อมูลมา')
sup(t, at('ต่อมาเป็นเรื่อง') - 0.1, [(pill('k3a', 'TIP', on=True), 110), (chip('k3b', '<span class="th">บอกให้ AI <span class="red">อ้างอิงแหล่งข้อมูล</span></span>'), 230)],
    [('k3a', t), ('k3b', t + 0.25)])
t = at('ต่อมาเป็นเรื่อง')
sup(t, at('ยุคประมาณ') - 0.1, [(chip('k4a', '<span class="en">Memory</span>', 'SOURCE 4', hot=True), 110), (pill('k4b', 'ความทรงจำของ AI'), 290)],
    [('k4a', at('Memory', after=t)), ('k4b', at('Memory', after=t) + 0.3)])
t = at('Model')
sup(t, at('ถ้าตอนนี้อยู่ใน') - 0.1, [(chip('k5a', '<span class="en">Model Context Protocol</span>', 'SOURCE 5 · MCP', hot=True), 110), (pill('k5b', 'มาตรฐานเปิด'), 290)],
    [('k5a', t), ('k5b', at('มาตรฐานเปิด'))])
t = at('Connector')
sup(t, at('ทั้งหมดนี้มันคือ') - 0.1, [(chip('k6a', '<span class="en">Connector</span>', 'COPILOT · CLAUDE · GEMINI')
    + chip('k6b', '<span class="en">Plugin</span>', 'GPT'), 110)], [('k6a', t), ('k6b', at('Plugin'))])

# ===== 3 · การ์ดล่างจอ (ค้างทั้งช่วง · ซับยังขึ้น) =====
lvcard('lv1', at('แต่ต้องบอกไว้เลย') - 0.1, at('ไปลองดูกันได้ครับ') + 1.0, 'MEMORY', 'ไม่ได้จำทุกอย่าง', 'ดู · แก้ · ลบได้ใน<b class="red">หน้าตั้งค่า</b>', 1, 1)
lvcard('lv2', at('แต่มีข้อควรระวัง') - 0.1, at('สรุปครับ') - 0.15, 'CAUTION', 'ยิ่งเชื่อมเยอะ ยิ่งต้องระวัง', 'ใช้เฉพาะตัวที่<b class="red">ฝ่าย IT อนุญาต</b>', 1, 1, 'dont')
R1, R2, R3, R4, R5, RE = (at('สรุปครับ'), at('แต่ถ้ามันเป็นข้อมูลที่เราต้องการ'), at('แต่ถ้ามันเป็นข้อมูลล่าสุด'),
                          at('และถ้ามันเป็นข้อมูลที่เราเคยคุย'), at('สุดท้ายครับ'), at('ลองดูนะครับทุกคน'))
for k, (a, b, name, desc) in enumerate([
        (R1, R2, 'ความรู้ทั่วไป', 'ถาม AI <b class="red">ตรง ๆ</b> ได้เลย'),
        (R2, R3, 'ข้อมูลจากไฟล์เฉพาะ', '<b class="red">แนบไฟล์</b>ลงไป'),
        (R3, R4, 'ข้อมูลล่าสุด', 'สั่งให้<b class="red">ค้นเว็บ</b>'),
        (R4, R5, 'เรื่องที่เคยคุยแล้ว', 'เช็กว่ามีระบบ <b class="red">Memory</b>'),
        (R5, RE, 'ข้อมูลในระบบงาน', 'ต่อ <b class="red">MCP / Connector</b>')]):
    lvcard(f'lr{k + 1}', a - 0.1, b - 0.15, f'RECAP {k + 1} / 5', name, desc, k + 1, 5)

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
def draw(id, t, d=0.4, s='pen'):
    tw(f"tl.fromTo('#{id}',{{strokeDashoffset:100}},{{strokeDashoffset:0,duration:{d},ease:'power2.out',immediateRender:false}},{r(t)});")
    tw(f"tl.set('#{id}',{{strokeDashoffset:100}},0);")
    if s: fx(t, s)
def ln(id, x1, y1, x2, y2, on=False):
    return f'<line id="{id}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" pathLength="100" stroke-dasharray="100" stroke-dashoffset="100" stroke="{"#EA3A1F" if on else "#3a3a3c"}" stroke-width="{12 if on else 6}" stroke-linecap="round"/>'
def drop(id, t, s='click', rot=0):
    tw(f"tl.fromTo('#{id}',{{opacity:0,y:-160,rotation:{rot - 8}}},{{opacity:1,y:0,rotation:{rot},duration:0.38,ease:'back.out(1.6)'}},{r(t)});")
    if s: fx(t, s)
# ไอคอนวาดเส้นเอง (ไม่ใช้โลโก้/อีโมจิ) · {c} = สีเส้น
IC = {
 'book':  '<svg class="ic" viewBox="0 0 48 48"><path d="M24 10C19 6 11 6 4 8V40C11 38 19 38 24 42C29 38 37 38 44 40V8C37 6 29 6 24 10Z" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/><path d="M24 10V42" stroke="{c}" stroke-width="3.2"/></svg>',
 'doc':   '<svg class="ic" viewBox="0 0 40 48"><path d="M4 2H26L36 12V46H4Z" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/><path d="M26 2V12H36" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/><path d="M11 22H29M11 30H29M11 38H22" stroke="{c}" stroke-width="3" stroke-linecap="round"/></svg>',
 'globe': '<svg class="ic" viewBox="0 0 48 48"><circle cx="24" cy="24" r="20" fill="none" stroke="{c}" stroke-width="3.2"/><ellipse cx="24" cy="24" rx="9" ry="20" fill="none" stroke="{c}" stroke-width="3"/><path d="M4 24H44M8 13H40M8 35H40" stroke="{c}" stroke-width="3"/></svg>',
 'brain': '<svg class="ic" viewBox="0 0 48 48"><path d="M22 6C16 4 10 8 10 13C5 14 3 20 6 24C3 28 5 35 10 36C11 42 18 45 22 42Z" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/><path d="M26 6C32 4 38 8 38 13C43 14 45 20 42 24C45 28 43 35 38 36C37 42 30 45 26 42Z" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/><path d="M24 6V42" stroke="{c}" stroke-width="3"/></svg>',
 'apps':  '<svg class="ic" viewBox="0 0 48 48"><rect x="4" y="4" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="3.2"/><rect x="28" y="4" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="3.2"/><rect x="4" y="28" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="3.2"/><rect x="28" y="28" width="16" height="16" rx="4" fill="none" stroke="{c}" stroke-width="3.2"/></svg>',
 'search':'<svg class="ic" viewBox="0 0 48 48"><circle cx="20" cy="20" r="14" fill="none" stroke="{c}" stroke-width="3.6"/><path d="M30 30L44 44" stroke="{c}" stroke-width="4" stroke-linecap="round"/></svg>',
 'cut':   '<svg class="ic" viewBox="0 0 48 48"><circle cx="11" cy="37" r="7" fill="none" stroke="{c}" stroke-width="3.2"/><circle cx="37" cy="37" r="7" fill="none" stroke="{c}" stroke-width="3.2"/><path d="M16 32L38 4M32 32L10 4" stroke="{c}" stroke-width="3.2" stroke-linecap="round"/></svg>',
 'chat':  '<svg class="ic" viewBox="0 0 48 48"><path d="M6 8H42V34H20L10 42V34H6Z" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/></svg>',
}
def item(id, x, y, lbl, nm, ic, rot=0, cls=''):
    return (f'<div class="it2 {cls}" id="{id}" style="left:{x}px;top:{y}px;transform:rotate({rot}deg)">'
            f'{IC[ic].format(c="#EA3A1F" if "hot" in cls else "#fff")}<div><div class="lbl">{lbl}</div><div class="nm th">{nm}</div></div></div>')
def step(id, y, n, ic, txt, hot=False):
    return (f'<div class="stp{" hot" if hot else ""}" id="{id}" style="top:{y}px"><div class="n">{n}</div>{IC[ic].format(c="#EA3A1F" if hot else "#fff")}'
            f'<div class="tx th">{txt}</div></div>')

# B1 · 5 แหล่งที่ AI หยิบข้อมูลมาวางบนโต๊ะ (2 แหล่งที่คุยไปแล้ว = ขาว · 3 แหล่งวันนี้ = ขอบแดง)
a, b = at('ผมรวบรวมมา') - 0.1, at('ไปข้อที่สาม') - 0.1
S5 = [('s1', 110, 560, 'SOURCE 1', 'สิ่งที่เรียนมา', 'book', -3, ''), ('s2', 570, 560, 'SOURCE 2', 'ไฟล์ที่แนบ', 'doc', 3, ''),
      ('s3', 110, 750, 'SOURCE 3', 'เว็บไซต์', 'globe', 2, 'hot'), ('s4', 570, 750, 'SOURCE 4', 'ความทรงจำ', 'brain', -2, 'hot'),
      ('s5', 340, 930, 'SOURCE 5', 'แอปที่เชื่อมไว้', 'apps', 1, 'hot')]
broll(a, b, hd('5 SOURCES', 'AI หยิบข้อมูลมาวาง<span class="red">บนโต๊ะ</span>')
      + '<div class="card desk" id="dk" style="height:640px"><div class="lbl">ON THE DESK</div></div>'
      + ''.join(item(i, x, y, l, n, ic, rt, c) for i, x, y, l, n, ic, rt, c in S5)
      + '<div class="row" style="top:1150px"><div class="wrap">' + pill('a1', '<span class="en">OneDrive</span>') + pill('a2', '<span class="en">SharePoint</span>')
      + pill('a3', '<span class="en">Canva</span>') + '</div></div>')
pop('dk', a + 0.3, None)
for (i, *_x, rt, _c), ph in zip(S5, ['สิ่งที่เขาเรียนรู้', 'สองครับไฟล์', 'เว็บไซต์ครับ', 'Memory', 'ห้าครับการที่เรา']):
    drop(i, at(ph), 'click', rt)
pop('a1', at('OneDrive'), 'click'); pop('a2', at('SharePoint'), None); pop('a3', at('Canva'), None)

# B2 · ค้นเว็บทำงานยังไง: ขอข่าวล่าสุด → รู้ว่าต้องใช้ข้อมูลปัจจุบัน → เรียกเครื่องมือค้นหา → เปิดเว็บที่เกี่ยวข้อง → ตัดข้อความส่งให้ AI สรุป
a, b = at('เวลาเราต้องการข้อมูลที่มัน') - 0.1, at('ใช้เมื่อไหร่ครับ') - 0.1
ST = [('w1', 430, 'chat', 'ขอ<span class="red">ข่าวล่าสุด</span>'), ('w2', 580, 'search', 'รู้ว่าต้องใช้ข้อมูลปัจจุบัน'),
      ('w3', 730, 'search', 'เรียก<span class="red">เครื่องมือค้นหา</span>'), ('w4', 880, 'globe', 'เปิดเว็บที่เกี่ยวข้อง'),
      ('w5', 1030, 'cut', 'ตัดข้อความ ส่งให้ AI <span class="red">สรุป</span>')]
broll(a, b, hd('WEB SEARCH', 'AI <span class="red">ค้นเว็บ</span>ยังไง')
      + ''.join(step(i, y, k + 1, ic, tx, k == 4) for k, (i, y, ic, tx) in enumerate(ST)))
for (i, *_x), ph, s in zip(ST, ['อยากจะให้คุณไปหาข่าว', 'Detect', 'เรียกเครื่องมือค้นหา', 'เปิดเว็บอันไหน', 'ตัดข้อความ'], ['click', 'click', 'click', 'click', 'thump']):
    pop(i, at(ph), s)

# B3 · Memory: บอกความชอบ → เก็บลง Memory → แชทใหม่โต๊ะว่าง แต่ AI หยิบ Memory มาวางคู่ให้เอง
a, b = at('เมื่อไหร่ที่เราคุยกับ') - 0.1, at('แต่ต้องบอกไว้เลย') - 0.1
broll(a, b, hd('MEMORY', 'AI <span class="red">จำ</span>ความชอบของเรา')
      + '<div class="card chatc" id="m0"><div class="lbl">CHAT</div>'
      + '<div class="ub th" id="m1">ชอบไปเที่ยวญี่ปุ่น</div><div class="ub th" id="m2">ชอบ <span class="en">Report</span> ยาว ๆ เป็นทางการ</div>'
      + '<div class="ub th" id="m5">ช่วยวางแผนทริปให้หน่อย</div></div>'
      + '<div class="card memc" id="m3"><div class="lbl">' + IC['brain'].format(c='#EA3A1F') + 'MEMORY</div>'
      + '<div class="mi th" id="m3a">ชอบญี่ปุ่น</div><div class="mi th" id="m3b"><span class="en">Report</span> ยาว · ทางการ</div></div>'
      + '<div class="row" style="top:1215px"><div class="pill on" id="m6"><span class="th">ใส่ให้เอง โดยเราไม่รู้ตัว</span></div></div>')
pop('m0', a + 0.3, None)
pop('m1', at('เราบอกว่าเราชอบไปเที่ยว'), 'click'); pop('m2', at('เราบอกว่าเราชอบ', nth=2), 'click')
t = at('ไปเก็บไว้ใน'); pop('m3', t, 'thump'); pop('m3a', t + 0.3, None); pop('m3b', t + 0.5, None)
t = at('ครั้งหน้าถ้าเราเปิดแชทใหม่'); out('m1', t); out('m2', t)
pop('m5', at('ช่วยวางแผนทริป'), 'click')
t = at('ไปหยิบ'); bump('m3', t, 1.06)
pop('m6', at('โดยที่เราอาจจะไม่รู้ตัว'), 'thump')

# B4 · MCP = ท่อ: AI ตรงกลาง ต่อท่อไปแอปรอบ ๆ (ชื่อแอปพิมพ์ด้วย Poppins แทนโลโก้) + เมนูที่แอปอนุญาต
a, b = at('ผมชอบเปรียบเทียบ') - 0.1, at('แต่มีข้อควรระวัง') - 0.1
AP = [('p1', 230, 470, 'Canva', True), ('p2', 850, 470, 'Google Drive', False), ('p3', 230, 980, 'OneDrive', False), ('p4', 850, 980, 'SharePoint', False)]
svg = '<svg class="tree" viewBox="0 0 1080 1920">' + ''.join(ln(f'q{k}', 540, 790, x, y + 60, on) for k, (_i, x, y, _n, on) in enumerate(AP)) + '</svg>'
broll(a, b, hd('MCP · CONNECTOR', 'ต่อ<span class="red">ท่อ</span>ให้ AI เข้าแอป') + svg
      + '<div class="hub" id="hb"><span class="en">AI</span></div>'
      + ''.join(f'<div class="nd{" hot" if on else ""}" id="{i}" style="left:{x - 150}px;top:{y}px"><span class="en">{n}</span></div>' for i, x, y, n, on in AP)
      + '<div class="row" style="top:1150px"><div class="wrap">' + pill('u1', 'ดูสไลด์') + pill('u2', 'ทำสไลด์') + pill('u3', 'เรียบเรียงเนื้อหา')
      + pill('u4', 'สร้างภาพ') + '</div></div>')
pop('hb', a + 0.3, None)
for k, (i, *_x) in enumerate(AP): pop(i, a + 0.45 + 0.12 * k, None)
t = at('เป็นเหมือนท่อ')
for k in range(4): draw(f'q{k}', t + 0.15 * k, s='pen' if k == 0 else None)
bump('p1', at('Canvaอนุญาต'), 1.1)
for i, ph in [('u1', 'ดูสไลด์'), ('u2', 'ทำสไลด์'), ('u3', 'เรียบเรียงเนื้อหา'), ('u4', 'สร้างภาพ')]: pop(i, at(ph, after=at('ดูสไลด์') - 0.05), 'click')

# B5 · ลองเอง 3 ขั้น
a = at('ลองดูนะครับทุกคน') - 0.1
broll(a, TOTAL, hd('TRY IT', 'ลองกับ<span class="red">งานจริง</span>ของเรา')
      + step('t1', 470, 1, 'chat', 'นึกงานจริง 1 ชิ้น ที่อยากให้ AI ช่วย')
      + step('t2', 640, 2, 'apps', 'ต้องใช้ข้อมูลจาก<span class="red">แหล่งไหน</span>ใน 5 แหล่ง')
      + step('t3', 810, 3, 'doc', 'พิมพ์ <span class="en">Prompt</span> ให้ตรงแหล่ง')
      + '<div class="row" style="top:1000px"><div class="pill on" id="t4"><span class="th">ผลลัพธ์ตรงใจไหม?</span></div></div>')
pop('t1', at('ผมแนะนำว่า'), 'click'); pop('t2', at('หลังจากนั้นตั้งคำถาม'), 'click'); pop('t3', at('Prompt', after=at('หลังจากนั้นตั้งคำถาม')), 'click')
pop('t4', at('แล้วลองดูสิว่าผลลัพธ์'), 'thump')
