#!/usr/bin/env python3
"""pm-timeline — คลิป BASE "Checklist การวาง Timeline" แบบแผงกราฟิกบน + คนพูดล่าง
ทุกจังหวะผูกกับเวลาคำจริง (ElevenLabs Scribe → work/align.py) · รัน: python3 gen.py"""
import json, os, re, subprocess, sys, shutil
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, 'work'); from align import at, captions

TOTAL = 156.2
SHRINK = 8.2          # แผงเต็มจอจนจบประโยค "เป็นไปไม่ได้จริง" (และพ้นการ์ดชื่อเรื่องในต้นฉบับที่ทับหน้าถึง ~4.5 วิ)
P = 800               # ความสูงแผงหลังหด
js = []
def tw(s): js.append(s)
def r(x): return round(x, 3)

# ---------- เวลาเปิดฉาก (จากคำพูดจริง) ----------
S = {
 1: at('อย่างแรกเลย'), 2: at('ข้อที่สอง'), 3: at('สิ่งที่สามครับ'), 4: at('สิ่งที่สี่'),
 5: at('อย่างที่ห้า'), 6: at('ข้อสุดท้าย'), 7: at('ถ้าเราทำได้ทั้งหก'),
}
S[0] = 0.0
order = [0, 1, 2, 3, 4, 5, 6, 7]

def enter(sid, t):
    tw(f"tl.fromTo('#s{sid}',{{opacity:0,y:70}},{{opacity:1,y:0,duration:0.45,ease:'power3.out'}},{r(t)});")
def leave(sid, t):
    tw(f"tl.to('#s{sid}',{{opacity:0,y:-60,duration:0.3,ease:'power2.in'}},{r(t-0.3)});")
def pop(sel, t, d=0.4, frm='y:30,opacity:0', to='y:0,opacity:1', ease='power3.out'):
    tw(f"tl.fromTo('{sel}',{{{frm}}},{{{to},duration:{d},ease:'{ease}'}},{r(t)});")
def grow(sel, t, w, d=0.6, ease='power2.out'):
    tw(f"tl.fromTo('{sel}',{{width:0}},{{width:{w},duration:{d},ease:'{ease}'}},{r(t)});")
def draw(sel, t, d=0.5, ease='power2.inOut'):
    tw(f"tl.fromTo('{sel}',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{d},ease:'{ease}'}},{r(t)});")

CHECK = lambda w=80: f'<svg width="{w}" height="{w}" viewBox="0 0 80 80"><path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M10 44 L32 64 L72 10" fill="none" stroke="#ED4734" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/></svg>'

html = []
# ---------- 0 · intro ----------
html.append(f'''
    <div id="intro-full">
      <div class="k" id="i-k">ปัญหาที่ <b>Project Manager</b> เจอเหมือนกันหมด</div>
      <div class="big b1" id="i-b1">UNDER</div>
      <div class="big b2" id="i-b2">ESTIMATE</div>
      <div class="rule" id="i-rule"></div>
      <div class="q" id="i-q">timeline ที่ตั้งไว้<br><em>เป็นไปไม่ได้จริง</em></div>
    </div>
    <div class="scene" id="s0">
      <div class="kick">WHY TIMELINES FAIL</div>
      <div class="ttl">ลืมเผื่อ <span style="color:var(--red)">6</span> อย่าง</div>
      <div class="row" style="top:250px">แผนที่ตั้ง</div>
      <div class="bar" id="s0-plan" style="top:236px;background:var(--ink)"></div>
      <div class="row" style="top:350px">เกิดขึ้นจริง</div>
      <div class="bar redhatch" id="s0-real" style="top:336px"></div>
      <div class="flag" id="s0-flag"><i>DEADLINE</i></div>
      <div class="six">{''.join(f'<div id="s0-b{i}">0{i}</div>' for i in range(1,7))}</div>
    </div>''')
t_ul = at('Underestimate')
pop('#i-k', at('ProjectManager') - 0.2)
pop('#i-b1', t_ul, 0.45, 'x:-80,opacity:0', 'x:0,opacity:1', 'power4.out')
pop('#i-b2', r(t_ul + 0.35), 0.45, 'x:80,opacity:0', 'x:0,opacity:1', 'power4.out')
tw(f"tl.fromTo('#i-rule',{{scaleX:0}},{{scaleX:1,duration:0.5,ease:'power2.inOut'}},{r(t_ul+0.6)});")
pop('#i-q', at('timelineที่ตั้งไว้'), 0.4)
pop('#i-q em', at('เป็นไปไม่ได้จริง'), 0.35, 'opacity:0,x:-20', 'opacity:1,x:0')
tw(f"tl.to('#i-b1,#i-b2',{{x:12,duration:0.06,yoyo:true,repeat:5,ease:'none'}},{r(at('เป็นไปไม่ได้จริง')+0.2)});")
tw(f"tl.to('#intro-full',{{opacity:0,y:-120,duration:0.4,ease:'power2.in'}},{r(SHRINK-0.35)});")
tw(f"tl.to('#panel',{{height:{P},duration:0.55,ease:'power3.inOut'}},{SHRINK});")
tw("tl.set('#capbox',{y:1540},0);")
tw(f"tl.to('#capbox',{{y:{P-46},duration:0.55,ease:'power3.inOut'}},{SHRINK});")
enter(0, SHRINK + 0.25)
grow('#s0-plan', SHRINK + 0.5, 420, 0.4)
t = at('ลืมเผื่อ')
grow('#s0-real', SHRINK + 0.8, 740, 1.0, 'power1.inOut')
tw(f"tl.to('#s0-flag',{{rotation:-7,duration:0.12,yoyo:true,repeat:3,ease:'sine.inOut',transformOrigin:'50% 100%'}},{r(t+0.9)});")
t6 = at('หกอย่าง')
for i in range(1, 7):
    pop(f'#s0-b{i}', r(t6 + 0.09 * (i - 1)), 0.3, 'y:40,opacity:0', 'y:0,opacity:1', 'back.out(2)')
leave(0, S[1])

def head(sid, kick, title, sub, num):
    return f'''
      <div class="num">{num}</div>
      <div class="kick">{kick.replace('เผื่อข้อ', '<span class="th">เผื่อข้อ</span>')}</div>
      <div class="ttl">{title}<small>{sub}</small></div>'''

# ---------- 1 · Resource ----------
html.append(f'''
    <div class="scene" id="s1">{head(1,'เผื่อข้อ 01 — RESOURCE','Resource','เวลาของ Core Team ที่ใส่ได้จริง','01')}
      <svg class="person" width="170" height="200" viewBox="0 0 170 200"><circle cx="85" cy="52" r="42" fill="#211F20"/><path d="M8 196 C8 128 40 104 85 104 C130 104 162 128 162 196 Z" fill="#211F20"/></svg>
      <div class="lbl" style="left:64px;top:480px;font-size:26px">Core Team</div>
      <div class="lbl" id="s1-cap" style="left:270px;top:250px;font-size:26px;color:#5d5a5b">เวลาทั้งหมดของเขา 100%</div>
      <div class="bar" id="s1-bar">
        <div class="blk hatch" id="s1-a" style="left:0;width:250px;border-right:4px solid #211F20">งาน A</div>
        <div class="blk hatch" id="s1-b" style="left:250px;width:226px;border-right:4px solid #211F20">งาน B</div>
        <div class="blk" id="s1-r" style="left:476px;width:260px;background:var(--red);color:#fff">งานนี้</div>
      </div>
      <div class="lbl" id="s1-other" style="left:270px;top:440px;color:#5d5a5b">↑ งานอื่นที่ถืออยู่</div>
      <div class="lbl" id="s1-ok" style="left:650px;top:520px;color:var(--red)">เผื่อตามที่ใส่ได้จริง</div>
      <svg id="s1-ul" style="position:absolute;left:640px;top:568px" width="380" height="24"><path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M4 14 C90 4 200 22 376 8" fill="none" stroke="#ED4734" stroke-width="8" stroke-linecap="round"/></svg>
    </div>''')
enter(1, S[1])
pop('#s1 .person', at('CoreTeam'), 0.4, 'scale:0.6,opacity:0', 'scale:1,opacity:1', 'back.out(1.8)')
pop('#s1-bar', at('CoreTeam'), 0.4); pop('#s1-cap', at('CoreTeam') + 0.15, 0.3)
t = at('ไม่ได้ถืองานเดียว')
grow('#s1-a', t, 250, 0.45); grow('#s1-b', t + 0.35, 226, 0.45)
t = at('เผื่อResource'); grow('#s1-r', t, 260, 0.5)
t = at('MakeSense'); pop('#s1-ok', t, 0.35); draw('#s1-ul path', t + 0.2, 0.5)
t = at('งานอื่น', after=S[1] + 10); pop('#s1-other', t, 0.35)
tw(f"tl.to('#s1-a,#s1-b',{{y:-10,duration:0.18,yoyo:true,repeat:1,ease:'power1.out'}},{r(t+0.1)});")
leave(1, S[2])

# ---------- 2 · Learning Curve ----------
html.append(f'''
    <div class="scene" id="s2">{head(2,'เผื่อข้อ 02 — LEARNING CURVE','Learning Curve','งานใหม่ คนทำต้องใช้เวลาเรียนรู้','02')}
      <svg class="chart" width="952" height="330" viewBox="0 0 952 330">
        <rect id="s2-zone" x="44" y="40" width="380" height="244" fill="#e4e0d9"/>
        <text id="s2-zt" x="60" y="80" font-family="Plex Thai" font-weight="700" font-size="28" fill="#5d5a5b">ช่วงเรียนรู้</text>
        <path d="M44 20 V284 H930" fill="none" stroke="#211F20" stroke-width="5"/>
        <text x="60" y="20" font-family="Plex Thai" font-weight="600" font-size="24" fill="#211F20">ความเก่ง ↑</text>
        <text x="850" y="320" font-family="Plex Thai" font-weight="600" font-size="24" fill="#211F20">เวลา →</text>
        <path id="s2-curve" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M44 270 C260 268 330 250 430 160 S 640 40 920 34" fill="none" stroke="#ED4734" stroke-width="10" stroke-linecap="round"/>
      </svg>
      <div class="blk task" id="s2-plan" style="width:470px;background:var(--ink);color:#fff">เวลาที่คิดไว้</div>
      <div class="blk task redhatch" id="s2-ext" style="left:534px;width:0;color:#211F20">+ เวลาเรียนรู้</div>
    </div>''')
enter(2, S[2])
t = at('LearningCurve', after=S[2]); draw('#s2-curve', t, 1.4)
t = at('เรียนรู้', after=S[2]); pop('#s2-zone,#s2-zt', t, 0.4, 'opacity:0', 'opacity:1')
t = at('LearningCurve', after=S[2] + 8); pop('#s2-plan', t, 0.35, 'x:-40,opacity:0', 'x:0,opacity:1')
t = at('ยืดออกไป'); grow('#s2-ext', t, 420, 0.9, 'power1.inOut')
leave(2, S[3])

# ---------- 3 · Approval ----------
ppl = ''.join(f'<svg id="s3-p{i}" style="position:absolute;left:{i*92}px;top:{40 if i==1 else 120}px" width="110" height="140" viewBox="0 0 110 140"><circle cx="55" cy="36" r="30" fill="{"#ED4734" if i==1 else "#a09e9f"}"/><path d="M6 138 C6 90 28 74 55 74 C82 74 104 90 104 138 Z" fill="{"#ED4734" if i==1 else "#a09e9f"}"/></svg>' for i in range(3))
html.append(f'''
    <div class="scene" id="s3">{head(3,'เผื่อข้อ 03 — APPROVAL','รอ Stakeholder อนุมัติ','ทุก Project มีคนที่ต้องเซ็นผ่าน','03')}
      <div class="ppl" style="top:300px">{ppl}<div class="lbl" id="s3-key" style="left:40px;top:-10px;font:700 22px Poppins,'Plex Thai';letter-spacing:3px;color:var(--red)">KEY PERSON</div></div>
      <div class="doc" id="s3-doc">
        <h4>APPROVAL FORM</h4><h5>ขออนุมัติ Timeline</h5>
        <div class="fld" id="s3-f1">ใคร?<span></span>{CHECK(56)}</div>
        <div class="fld" id="s3-f2">เมื่อไหร่?<span></span>{CHECK(56)}</div>
        <div class="fld" id="s3-f3">ใช้กี่วัน?<span></span>{CHECK(56)}</div>
      </div>
      <div class="chip" id="s3-chip">กำลังตรวจสอบ …</div>
      <div class="stamp" id="s3-stamp">APPROVED</div>
    </div>''')
enter(3, S[3])
pop('#s3-doc', at('Approval') , 0.5, 'y:80,opacity:0,rotation:4', 'y:0,opacity:1,rotation:-1.5')
t = at('คนสำคัญ')
for i in range(3): pop(f'#s3-p{i}', r(t - 0.6 + 0.12 * i), 0.35, 'y:30,opacity:0', 'y:0,opacity:1', 'back.out(1.8)')
pop('#s3-key', t, 0.3)
t = at('ตรวจสอบ'); pop('#s3-chip', t, 0.3)
tw(f"tl.to('#s3-chip',{{opacity:0,duration:0.2}},{r(at('คนๆนั้น'))});")
for k, ph in enumerate(['คือใคร', 'เมื่อไหร่', 'ใช้เวลาเท่าไหร่']):
    draw(f'#s3-f{k+1} svg path', at(ph, after=S[3] + 5), 0.35)
t = at('อย่าลืมเผื่อสิ่งนี้')
tw(f"tl.fromTo('#s3-stamp',{{scale:2.4,opacity:0}},{{scale:1,opacity:1,duration:0.22,ease:'power4.in'}},{r(t)});")
tw(f"tl.to('#s3-doc',{{x:6,duration:0.05,yoyo:true,repeat:3}},{r(t+0.22)});")
leave(3, S[4])

# ---------- 4 · Waiting ----------
days = ''.join(f'<b id="s4-d{i}"><span class="th">รอ</span> · DAY {i:02d}</b>' for i in range(1, 8))
html.append(f'''
    <div class="scene" id="s4">{head(4,'เผื่อข้อ 04 — WAITING TIME','เวลาในการรอ','ปัจจัยที่เราควบคุมไม่ได้','04')}
      <div class="box vendor" id="s4-v">VENDOR</div>
      <div class="road" id="s4-road"></div>
      <div class="box us">ทีมเรา</div>
      <div class="day">{days}</div>
      <div class="parcel" id="s4-p"></div>
      <div class="lbl" id="s4-nc" style="left:330px;top:470px;padding:4px 18px;border:4px solid #5d5a5b;color:#5d5a5b;transform:rotate(-3deg)">ควบคุมไม่ได้</div>
      <div class="strip">
        <div class="blk" id="s4-t1" style="left:0;top:0;width:320px;height:90px;background:var(--ink);color:#fff">งาน</div>
        <div class="blk hatch" id="s4-w" style="left:320px;top:0;width:0;height:90px;font-family:Poppins;letter-spacing:3px">WAITING</div>
        <div class="blk" id="s4-t2" style="left:320px;top:0;width:320px;height:90px;background:var(--ink);color:#fff;border-left:4px solid var(--paper)">งาน</div>
      </div>
    </div>''')
enter(4, S[4])
t = at('Vendor'); pop('#s4-v', t, 0.35, 'scale:0.7,opacity:0', 'scale:1,opacity:1', 'back.out(2)')
tw(f"tl.fromTo('#s4-road',{{scaleX:0}},{{scaleX:1,transformOrigin:'left center',duration:0.5,ease:'power2.out'}},{S[4]+0.5});")
tw(f"tl.fromTo('#s4-p',{{opacity:0,scale:0.5}},{{opacity:1,scale:1,duration:0.3,ease:'back.out(2)'}},{r(at('มาส่งของ'))});")
# พัสดุขยับทีละนิด หยุดเป็นช่วง ๆ = ความรู้สึก "รอ"
t0 = at('มาส่งของ'); tend = at('Waitingtime')
steps = 6; span = (tend - t0) / steps
for k in range(steps):
    tw(f"tl.to('#s4-p',{{x:{(k+1)*52},duration:0.35,ease:'power2.inOut'}},{r(t0 + 0.4 + k*span)});")
dstart = at('เวลาในการรอ'); dspan = (tend + 1.5 - dstart) / 7
for i in range(1, 8):
    tw(f"tl.set('#s4-d{i}',{{opacity:1}},{r(dstart + (i-1)*dspan)});")
    if i < 7: tw(f"tl.set('#s4-d{i}',{{opacity:0}},{r(dstart + i*dspan)});")
pop('#s4-nc', at('ควบคุมไม่ได้'), 0.3, 'scale:1.6,opacity:0', 'scale:1,opacity:1', 'power4.in')
pop('#s4-t1,#s4-t2', S[4] + 0.8, 0.35)
t = at('Waitingtime')
tw(f"tl.to('#s4-w',{{width:280,duration:0.6,ease:'power2.inOut'}},{r(t)});")
tw(f"tl.to('#s4-t2',{{x:280,duration:0.6,ease:'power2.inOut'}},{r(t)});")
leave(4, S[5])

# ---------- 5 · Planning Fallacy ----------
cards = [(64, 'A', 150, 250), (396, 'B', 120, 230), (728, 'C', 160, 240)]
ch = ''.join(f'''<div class="card" id="s5-c{i}" style="left:{x}px"><div class="tab">PROJECT {n}</div>
      <p>แผน</p><div class="mb" style="width:{p}px;background:var(--ink)"></div>
      <p>ใช้จริง</p><div class="mb s5-real" style="width:{a}px;background:var(--red)"></div>
      <p style="font:700 18px Poppins;letter-spacing:3px;color:var(--grey);margin-top:34px">RECORD</p></div>''' for i, (x, n, p, a) in enumerate(cards))
html.append(f'''
    <div class="scene" id="s5">{head(5,'เผื่อข้อ 05 — PLANNING FALLACY','Planning Fallacy','คนเราประเมินเวลาเร็วเกินจริงเสมอ','05')}
      <div id="s5-a">
        <div class="row" style="top:286px">ที่คิดไว้</div><div class="bar" id="s5-th" style="top:270px;width:0;background:var(--ink)"></div>
        <div class="row" style="top:396px">ใช้จริง</div><div class="bar redhatch" id="s5-re" style="top:380px;width:0"></div>
        <svg id="s5-br" style="position:absolute;left:600px;top:476px" width="420" height="60"><path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M4 4 V24 H410 V4 M207 24 V50" fill="none" stroke="#211F20" stroke-width="5"/></svg>
        <div class="lbl" id="s5-gap" style="left:600px;top:540px;font-size:26px;color:var(--red)">ส่วนที่ไม่ได้เผื่อ</div>
      </div>
      <div id="s5-b" data-layout-allow-occlusion>{ch}<div class="xc" id="s5-xc"><i>CROSS CHECK</i></div><div class="fact" id="s5-fact">FACT <b>BASE</b></div></div>
    </div>''')
enter(5, S[5])
t = at('ประเมินเวลาเร็ว'); grow('#s5-th', t, 300, 0.4)
t = at('เราทำได้จริง', after=S[5]); grow('#s5-re', t, 726, 1.1, 'power1.inOut')
draw('#s5-br path', t + 1.0, 0.4); pop('#s5-gap', t + 1.2, 0.3)
t = at('ย้อนกลับไปดู')
tw(f"tl.to('#s5-a',{{opacity:0,y:-40,duration:0.3,ease:'power2.in'}},{r(t-0.1)});")
for i in range(3): pop(f'#s5-c{i}', r(at('Projectก่อนหน้า') + 0.15 * i), 0.4, 'y:120,opacity:0,rotation:6', 'y:0,opacity:1,rotation:0', 'back.out(1.4)')
tw(f"tl.fromTo('#s5 .s5-real',{{scaleX:0,transformOrigin:'left center'}},{{scaleX:1,duration:0.6,stagger:0.12,ease:'power2.out'}},{r(at('เวลาจริง', after=S[5]))});")
pop('#s5-xc', at('CrossCheck'), 0.3, 'scale:1.05,opacity:0', 'scale:1,opacity:1')
t = at('ข้อเท็จจริง')
tw(f"tl.to('#s5-xc',{{opacity:0,duration:0.25}},{r(t-0.2)});")
tw(f"tl.to('#s5-c0,#s5-c1,#s5-c2',{{opacity:0.3,duration:0.2}},{r(t)});")
tw(f"tl.fromTo('#s5-fact',{{scale:2.2,opacity:0}},{{scale:1,opacity:1,duration:0.22,ease:'power4.in'}},{r(t)});")
leave(5, S[6])

# ---------- 6 · Slack Time ----------
G = [('t1', 64, 200, 'งาน 1', 0), ('b1', 264, 90, 'เผื่อ', 1), ('t2', 354, 200, 'งาน 2', 0),
     ('b2', 554, 90, 'เผื่อ', 1), ('t3', 644, 200, 'งาน 3', 0), ('b3', 844, 90, 'เผื่อ', 1)]
gh = ''.join(f'<div class="blk g {"hatch" if b else ""}" id="s6-{k}" style="left:{x}px;width:{w}px;{"" if b else "background:var(--ink);color:#fff;"}border:4px solid #211F20;font-size:{24 if b else 30}px">{lab}</div>' for k, x, w, lab, b in G)
X = lambda k, x: f'<svg class="x" id="s6-x{k}" style="left:{x}px" width="110" height="150" viewBox="0 0 110 150"><path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M10 20 L100 130" fill="none" stroke="#ED4734" stroke-width="12" stroke-linecap="round"/><path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="M100 20 L10 130" fill="none" stroke="#ED4734" stroke-width="12" stroke-linecap="round"/></svg>'
html.append(f'''
    <div class="scene" id="s6">{head(6,'เผื่อข้อ 06 — SLACK TIME','Buffer ไว้ท้ายสุด','ไม่ใช่แทรกไว้ระหว่างงาน','06')}
      <div class="axis"></div>{gh}{X(1,254)}{X(2,544)}
      <div class="note" id="s6-n1" style="left:64px;top:300px;color:var(--red)">✗ แทรกระหว่างงาน</div>
      <div class="note" id="s6-n2" style="left:64px;top:560px">มีเท่าไหร่ ก็ใช้จนหมด</div>
      <div class="note" id="s6-n3" style="left:640px;top:300px;color:var(--red)">✓ รวมไว้ท้ายสุด</div>
    </div>''')
enter(6, S[6])
t = at('BufferTime')
for i, (k, *_r) in enumerate(G): pop(f'#s6-{k}', r(t - 1.2 + 0.12 * i), 0.3, 'y:40,opacity:0', 'y:0,opacity:1', 'back.out(1.6)')
t = at('ระหว่างงาน', after=S[6])
for k in (1, 2): draw(f'#s6-x{k} path', r(t + 0.15 * k), 0.25)
pop('#s6-n1', t, 0.3)
t = at('ใช้เวลาให้มันจนหมด')
tw(f"tl.to('#s6-x1,#s6-x2,#s6-n1',{{opacity:0,duration:0.25}},{r(t-0.1)});")
tw(f"tl.to('#s6-t1,#s6-t2',{{width:290,backgroundColor:'#7a2a20',duration:0.7,ease:'power2.inOut'}},{r(t)});")
tw(f"tl.to('#s6-b1,#s6-b2',{{opacity:0,duration:0.3}},{r(t+0.5)});")
pop('#s6-n2', t + 0.3, 0.3)
t = at('แล้วค่อยเอาเวลาเผื่อทั้งหมด')
tw(f"tl.to('#s6-n2',{{opacity:0,duration:0.2}},{r(t-0.1)});")
tw(f"tl.to('#s6-t1',{{width:200,backgroundColor:'#211F20',duration:0.5,ease:'power2.inOut'}},{r(t)});")
tw(f"tl.to('#s6-t2',{{x:-90,width:200,backgroundColor:'#211F20',duration:0.5,ease:'power2.inOut'}},{r(t+0.1)});")
tw(f"tl.to('#s6-t3',{{x:-180,duration:0.5,ease:'power2.inOut'}},{r(t+0.2)});")
tw(f"tl.to('#s6-b3',{{x:-180,width:352,borderColor:'#ED4734',color:'#ED4734',duration:0.6,ease:'power2.inOut'}},{r(t+0.4)});")
tw(f"tl.set('#s6-b3',{{innerHTML:'BUFFER รวม'}},{r(t+0.7)});")
pop('#s6-n3', at('ตอนท้ายครับ'), 0.3)
leave(6, S[7])

# ---------- 7 · Recap ----------
items = ['Resource', 'Learning Curve', 'Approval', 'Waiting Time', 'Planning Fallacy', 'Slack Time']
ih = ''.join(f'<div class="it" id="s7-i{i}" style="left:{64 + (i % 2) * 490}px;top:{232 + (i // 2) * 116}px"><div class="cb">{CHECK(92)}</div><span class="n">0{i+1}</span>{name}</div>' for i, name in enumerate(items))
html.append(f'''
    <div class="scene" id="s7">
      <div class="kick">TAKE AWAY</div>
      <div class="ttl">ก่อน Final Timeline<small>เช็คให้ครบ 6 ข้อนี้</small></div>
      {ih}
      <div class="band" id="s7-band">REALISTIC <b>TIMELINE</b></div>
    </div>''')
enter(7, S[7])
for i in range(6): pop(f'#s7-i{i}', r(S[7] + 0.2 + 0.08 * i), 0.3, 'x:-30,opacity:0', 'x:0,opacity:1')
t = at('หกเรื่องนี้')
for i in range(6): draw(f'#s7-i{i} .cb path', r(t - 1.6 + 0.32 * i), 0.3)
t = at('Realistictimeline')
tw(f"tl.to('#s7-band',{{clipPath:'inset(0 0% 0 0)',duration:0.6,ease:'power3.inOut'}},{r(t)});")
tw(f"tl.to('#s7-i0,#s7-i1,#s7-i2,#s7-i3,#s7-i4,#s7-i5',{{y:-8,duration:0.2,stagger:0.05,yoyo:true,repeat:1}},{r(at('รวมหกข้อนี้'))});")

# ---------- ตัวนับบนหัว ----------
cnt = ['00 / 06'] + [f'<b>0{i}</b> / 06' for i in range(1, 7)] + ['<b>✓</b> 06 / 06']
html_cnt = ''.join(f'<span id="c{i}">{c}</span>' for i, c in enumerate(cnt))
for i in range(8):
    st = SHRINK if i == 0 else S[i]
    tw(f"tl.fromTo('#c{i}',{{y:24,opacity:0}},{{y:0,opacity:1,duration:0.3,ease:'power2.out'}},{r(st)});")
    if i < 7: tw(f"tl.to('#c{i}',{{y:-24,opacity:0,duration:0.25,ease:'power2.in'}},{r(S[i+1]-0.05)});")

# ---------- "ตัด" ซูมหน้าสลับตอนเปลี่ยนฉาก ----------
for i in range(1, 8):
    tw(f"tl.set('#vbox',{{scale:{1.08 if i % 2 else 1.0}}},{r(S[i])});")

# ---------- ซับ ----------
caps = captions(); ch = []
for i, c in enumerate(caps):
    txt = re.sub(r'\*(.+?)\*', r'<b>\1</b>', c['text'])
    ch.append(f'<div class="cap" id="k{i}">{txt}</div>')
    st = c['start']; nxt = caps[i + 1]['start'] if i + 1 < len(caps) else TOTAL
    end = nxt if nxt - c['end'] < 0.6 else c['end'] + 0.25
    tw(f"tl.fromTo('#k{i}',{{opacity:1,clipPath:'inset(0 100% 0 0)'}},{{clipPath:'inset(0 0% 0 0)',duration:0.14,ease:'power2.out'}},{r(st)});")
    tw(f"tl.set('#k{i}',{{opacity:0}},{r(end)});")

tw(f"tl.to('#fade',{{opacity:1,duration:0.5}},{r(TOTAL-0.5)});")

# ---------- เสียงเอฟเฟกต์ (ผูกเวลาเดียวกับภาพ) ----------
SFX = []   # (วินาที, ไฟล์, ความดัง)
def fx(t, kind, vol=None):
    v = {'swoosh': 0.30, 'click': 0.45, 'thump': 0.75, 'pen': 0.30}[kind] if vol is None else vol
    SFX.append((r(max(0, t)), kind, v))
fx(t_ul, 'thump'); fx(t_ul + 0.35, 'thump'); fx(SHRINK, 'swoosh')
for i in range(6): fx(t6 + 0.09 * i, 'click', 0.3)
for i in range(1, 8): fx(S[i] - 0.05, 'swoosh')
fx(at('CoreTeam'), 'click'); t = at('ไม่ได้ถืองานเดียว'); fx(t, 'click'); fx(t + 0.35, 'click')
fx(at('เผื่อResource'), 'click'); fx(at('MakeSense') + 0.2, 'pen', 0.25)
fx(at('LearningCurve', after=S[2]), 'pen', 0.22); fx(at('ยืดออกไป'), 'swoosh', 0.18)
fx(at('Approval'), 'click')
for ph in ['คือใคร', 'เมื่อไหร่', 'ใช้เวลาเท่าไหร่']: fx(at(ph, after=S[3] + 5), 'pen', 0.28)
fx(at('อย่าลืมเผื่อสิ่งนี้'), 'thump')
fx(at('Vendor'), 'click'); fx(at('ควบคุมไม่ได้'), 'thump', 0.4)
for i in range(1, 8): fx(dstart + (i - 1) * dspan, 'click', 0.12)
fx(at('Waitingtime'), 'swoosh', 0.2)
for i in range(3): fx(at('Projectก่อนหน้า') + 0.15 * i, 'click', 0.35)
fx(at('CrossCheck'), 'pen', 0.25); fx(at('ข้อเท็จจริง'), 'thump')
t = at('BufferTime')
for i in range(6): fx(t - 1.2 + 0.12 * i, 'click', 0.28)
t = at('ระหว่างงาน', after=S[6]); fx(t + 0.15, 'pen', 0.3); fx(t + 0.3, 'pen', 0.3)
fx(at('ใช้เวลาให้มันจนหมด'), 'swoosh', 0.18); fx(at('แล้วค่อยเอาเวลาเผื่อทั้งหมด'), 'swoosh', 0.22)
t = at('หกเรื่องนี้')
for i in range(6): fx(t - 1.6 + 0.32 * i, 'pen', 0.22)
fx(at('Realistictimeline'), 'swoosh', 0.3)

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
  <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
    <div id="vbox"><video id="talk" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-media-start="0" muted playsinline src="assets/talk.mp4"></video></div>
    <div id="panel" data-layout-allow-overflow data-layout-allow-occlusion>
      <div class="hdr"><img src="assets/base-logo.png" alt="BASE Playhouse"><div class="tag">PM CHECKLIST</div><div class="cnt">{html_cnt}</div></div>
{''.join(html)}
    </div>
    <div id="capbox" data-layout-allow-overflow>{''.join(ch)}</div>
    <audio id="voice" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="1" data-volume="1" src="assets/mix.wav"></audio>
    <div id="fade"></div>
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
if not os.path.exists('assets/voice.wav'):
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', 'assets/talk.mp4', '-vn', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', '-y', 'assets/voice.wav'], check=True)
if not os.path.exists('assets/base-logo.png'):
    subprocess.run(['cp', os.path.expanduser('~/.claude/skills/base-slides/assets/BASE_Logo_4_SH_BPH-CW.png'), 'assets/base-logo.png'], check=True)
# ---------- มิกซ์: เสียงพูด + SFX (ไม่มีเพลง) ----------

FILES = {'swoosh': 'assets/sfx/swoosh.mp3', 'click': 'assets/sfx/click.mp3', 'thump': 'assets/sfx/thump.wav', 'pen': 'assets/sfx/pen.wav'}
cmd = [FF, '-nostdin', '-v', 'error', '-i', 'assets/voice.wav']   # ไม่มีเพลง
fl = ['[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v]']
labels = ['[v]']
for k, (tm, kind, vol) in enumerate(SFX, 1):
    cmd += ['-i', FILES[kind]]; ms = int(tm * 1000)
    fl.append(f'[{k}:a]volume={vol},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{k}]'); labels.append(f'[s{k}]')
fl.append(''.join(labels) + f'amix=inputs={len(labels)}:normalize=0:duration=first,atrim=0:{TOTAL},alimiter=limit=0.89[out]')
cmd += ['-filter_complex', ';'.join(fl), '-map', '[out]', '-ar', '48000', '-ac', '2', '-y', 'assets/mix.wav']
subprocess.run(cmd, check=True)
print('sfx', len(SFX))
json.dump({'scenes': S, 'total': TOTAL}, open('work/timeline.json', 'w'), indent=1)
print('scenes', {k: S[k] for k in sorted(S)}, '· captions', len(caps), '· tweens', len(js))
