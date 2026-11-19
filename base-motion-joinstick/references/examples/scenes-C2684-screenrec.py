# ===== C2684 · คลิป 8 · Prompt 6 องค์ประกอบ ตอน 2: ให้ตัวอย่าง · วางทางคิด · ขีดเส้นผ่าน · insert = กล้อง − 30.05
OFF = 30.05
TH = at('เดี๋ยวเรามาดูอีกสามสูตร')
hook(TH, [
    (0.1, '<span class="en">Prompt</span>', 'hk-xl', 610),
    (0.4, '<span class="en">6</span> องค์ประกอบ', 'hk-em', 770),
    (0.8, 'ตอน 2: ให้ตัวอย่าง', 'hk-s', 980),
    (1.1, 'วางทางคิด · ขีดเส้นผ่าน', 'hk-s', 1060),
])
# โต๊ะ: 3 สูตรแรกอยู่แล้ว → งานยากต้องวางของเพิ่ม (ตัวอย่าง · ทางคิด · เกณฑ์ผ่าน)
a, b = at('สมมุติเราเอาConcept') - 0.1, at('ไปสูตรที่สี่') - 0.1
D = [('d1', 110, 560, 'NO. 1–3', 'สามสูตรแรก', 'doc', -3, ''), ('d2', 570, 560, 'NO. 4', 'ตัวอย่าง', 'doc', 3, 'hot'),
     ('d3', 110, 750, 'NO. 5', 'ทางคิด', 'chat', 2, 'hot'), ('d4', 570, 750, 'NO. 6', 'เกณฑ์ผ่าน', 'check', -2, 'hot')]
broll(a, b, hd('CONTEXT', 'งานยาก ต้องวางของเพิ่ม<span class="red">บนโต๊ะ</span>')
      + '<div class="card desk" id="dk" style="height:500px"><div class="lbl">ON THE DESK</div></div>'
      + ''.join(item(i, x, y, l, n, ic, rt, c) for i, x, y, l, n, ic, rt, c in D))
pop('dk', a + 0.3, None); drop('d1', a + 0.6, 'click', -3)
t = at('เราต้องใส่บางอย่างเพิ่ม'); drop('d2', t, 'click', 3); drop('d3', t + 0.5, 'click', 2); drop('d4', t + 1.0, 'click', -2)

t = at('โครงสร้างที่สี่')
sup(t, at('ผมเปิดให้ดูเลย') - 0.1, [(chip('k1', '<span class="th"><span class="en">Reference Point</span> · ให้ตัวอย่าง</span>', 'NO. 4 / 6', hot=True), 110)], [('k1', t)])
a, b = at('ผมเปิดให้ดูเลย') - 0.05, at('งานแบบไหนครับที่เรา') - 0.1
screenroll(a, b, OFF, 'NO. 4', '<span class="en">Reference Point</span>',
           [('p1', 'ตัวอย่างโพสต์ที่ชอบ', at('ตัวอย่างโพสต์ที่ผมชอบ'), False), ('p2', 'ไม่อยากได้แบบตะโกน', at('ไม่อยากได้สไตล์'), True)])

t = at('สูตรที่ห้าครับ')
sup(t, at('คือบอกขั้นตอน') - 0.1, [(chip('k2', '<span class="th"><span class="en">Thinking Path</span> · วางทางคิด</span>', 'NO. 5 / 6', hot=True), 110)], [('k2', t)])
a, b = at('เช่นขั้นแรก') - 0.1, at('นี่ดูครับแบบที่หนึ่ง') - 0.1
TP = [('w1', 'chat', 'คิด <span class="red">3 มุม</span> ที่คนทำงานสนใจ', at('ขั้นแรกนะครับ')), ('w2', 'check', 'เลือกมุมที่ตรงที่สุด', at('ขั้นที่สอง')),
      ('w3', 'doc', 'ค่อยเขียนลง <span class="en">Detail</span>', at('ขั้นที่สาม'))]
broll(a, b, hd('THINKING PATH', 'ไกด์<span class="red">ขั้นตอน</span>ให้ AI') + ''.join(step(i, 470 + 170 * k, k + 1, ic, tx) for k, (i, ic, tx, _) in enumerate(TP)))
for i, _, _, t in TP: pop(i, t, 'click')
a, b = at('นี่ดูครับแบบที่หนึ่ง') - 0.05, at('มันเหมาะกับงานบางงาน') - 0.1
screenroll(a, b, OFF, 'NO. 5', '<span class="en">Thinking Path</span>',
           [('p3', 'ขั้น 1: คิด 3 มุม', a + 0.3, False), ('p4', 'ขั้น 2: เราเลือก', at('สมมุติเราบอกว่าเราเลือก'), False), ('p5', 'ขั้น 3: <span class="en">Final Copy</span>', at('เขาก็จะเขียนแบบFinal'), True)])
t = at('และเราอยากจะHuman')
sup(t, at('เพราะว่าเรารู้') - 0.1, [(chip('k3', '<span class="en">Human in the Loop</span>', hot=True), 110)], [('k3', at('HumanintheLoop') - 0.2)])

t = at('โครงสร้างที่หก')
sup(t, at('ขีดเส้นผ่านคืออะไร') - 0.1, [(chip('k4', '<span class="th"><span class="en">Success Criteria</span> · ขีดเส้นผ่าน</span>', 'NO. 6 / 6', hot=True), 110)], [('k4', t)])
a, b = at('ขีดเส้นผ่านคืออะไร') - 0.05, at('ตัวอย่างเมื่อกี้ของผม') - 0.1
SC = [('c1', 'check', 'ถูกไหม?', at('ถูกไหม')), ('c2', 'check', 'ครบไหม?', at('ครบไหม')), ('c3', 'check', 'ปลอดภัยไหม?', at('ปลอดภัยไหม'))]
broll(a, b, hd('SUCCESS CRITERIA', 'ขีด<span class="red">เส้นผ่าน</span>ให้ชัด')
      + ''.join(step(i, 420 + 150 * k, k + 1, ic, tx) for k, (i, ic, tx, _) in enumerate(SC))
      + '<div class="fin" id="fn"></div>' + step('c4', 940, '!', None, 'ตัวเลขต้องมาจากไฟล์เท่านั้น · <span class="red">ห้ามเดา</span>', hot=True))
tw(f"tl.fromTo('#fn',{{scaleX:0}},{{scaleX:1,duration:0.5,ease:'power2.out'}},{r(a + 0.4)});"); fx(a + 0.4, 'pen', 0.4)
for i, _, _, t in SC: pop(i, t, 'click')
pop('c4', at('ตัวเลขต้องมาจากไฟล์'), 'thump')
a, b = at('ตัวอย่างเมื่อกี้ของผม') - 0.05, at('Noteไว้นิดนึง') - 0.1
screenroll(a, b, OFF, 'NO. 6', '<span class="en">Success Criteria</span>',
           [('p6', 'ไม่เกิน 80 คำ', at('ผ่านถ้าไม่เกินแปดสิบคำ'), False), ('p7', 'มีชื่อเมนู + ราคา', at('ต้องมีชื่อเมนู'), False), ('p8', 'ไม่อ้างสรรพคุณสุขภาพ', at('ไม่อ้างสรรพคุณ'), True)])
t = at('Noteไว้นิดนึง')
sup(t, at('ผมอยากให้ทุกคนลองดูด้วยตัวเอง') - 0.1, [(chip('k5', '<span class="th">AI รุ่นใหม่ อาจไม่ต้องไกด์ทางคิดแล้ว</span>', 'NOTE'), 110)], [('k5', t)])
t = at('สรุปครับสามสูตร')
sup(t, at('เวลาเราpromptรอบหน้า') - 0.1, [(''.join(pill(i, x, on=True) for i, x in [('r1', 'ให้ตัวอย่าง'), ('r2', 'วางทางคิด'), ('r3', 'ขีดเส้นผ่าน')]), 110)],
    [('r1', at('ตัวอย่างวางทางคิด')), ('r2', at('วางทางคิดแล้ว')), ('r3', at('ขีดเส้นผ่านนะครับ'))])
RE = at('เวลาเราpromptรอบหน้า')
tryit(RE - 0.1, [('t1', 'doc', 'โยน<span class="red">ตัวอย่าง</span>ให้ดูได้ไหม?', at('ลองโยนตัวอย่าง')),
                 ('t2', 'chat', 'ไกด์<span class="red">วิธีคิด</span>ไหม?', at('ไกด์วิธีคิดไหม')),
                 ('t3', 'check', 'ขีดเส้น <span class="en">Success Criteria</span>', at('แล้วขีดเส้น'))])
