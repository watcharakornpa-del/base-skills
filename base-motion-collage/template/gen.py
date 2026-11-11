#!/usr/bin/env python3
"""base-motion-collage v3 — คลิปเต็ม: Text Hook (ขึ้นทีละคำ) → คนพูด + ซับทีม + Super คำสำคัญ + B-roll collage เฉพาะจุดที่ภาพช่วยให้เข้าใจ
รัน: python gen.py → index.html + assets/mix.wav  แล้ว render ทั้งคลิป
ต้นแบบในไฟล์นี้ = คลิป "Gen Z vs Gen Y" (ต้นทาง = rough cut จาก base-rough-cut)"""
import json, os, random, re, shutil, subprocess, sys
from xml.sax.saxutils import escape
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
sys.path.insert(0, 'work'); from align import at

# ===== ตั้งค่าต่อคลิป =====
TOTAL = 70.1                      # ความยาว (วินาที)
FACE_CROP = '1000:1000:80:400'    # crop หน้าคนพูดสำหรับวงกลม B-roll (ตัดกว้าง หัวกิน ~ครึ่งวง)
SUBS = 'work/subs.srt'            # ซับ (จาก base-rough-cut หรือของทีม) · None = คลิปมีซับเบิร์นมาแล้ว
SUB_TOP = 1256                    # ตำแหน่งซับ (แบบทีม: กลางจอค่อนล่าง)

js = []; html = []; SFX = []; ROT = {}; USED = {}; HIDE_SUBS = []
def tw(s): js.append(s)
def r(x): return round(x, 3)
def fx(t, kind, vol=None):
    v = {'swoosh': 0.30, 'click': 0.45, 'thump': 0.70, 'pen': 0.30}[kind] if vol is None else vol
    SFX.append((r(max(0, t)), kind, v))

# ---------- ชิ้นส่วน ----------
FILL = {'s-paper': '#faf7f0', 's-navy': '#0d1b2a', 's-ember': '#ff3608', 's-cream': '#efe6d6'}
def edge(seed, fill, top):
    R = random.Random(seed); xs = range(0, 101, 4); ys = [R.uniform(1, 9) for _ in xs]
    poly = ('0,10 ' + ' '.join(f'{x},{y:.1f}' for x, y in zip(xs, ys)) + ' 100,10') if top else \
           ('0,0 ' + ' '.join(f'{x},{10 - y:.1f}' for x, y in zip(xs, ys)) + ' 100,0')
    return (f'<svg class="edge" style="{"top" if top else "bottom"}:-9px" viewBox="0 0 100 10" preserveAspectRatio="none">'
            f'<polygon points="{poly}" fill="{fill}"/></svg>')
def strip(id, text, x, y, kind='s-paper', cls='mid', rot=0, z=6, center=False):
    """แถบกระดาษฉีก · center=True: x = จุดกึ่งกลาง (ข้อความยาวไม่ต้องกะความกว้าง)"""
    ROT[id] = rot; s = sum(map(ord, id)) * 7
    pos = f'left:0;width:1080px;top:{y}px;display:flex;justify-content:center' if center else f'left:{x}px;top:{y}px'
    inner = f'<div class="strip {kind} {cls}">{edge(s, FILL[kind], True)}{text}{edge(s + 1, FILL[kind], False)}</div>'
    if center: return f'<div class="row" style="{pos};z-index:{z}"><div class="shadow rel" id="{id}">{inner}</div></div>'
    return f'<div class="shadow" id="{id}" style="{pos};z-index:{z}">{inner}</div>'
def piece(id, src, x, y, w, rot=0, z=4):
    ROT[id] = rot; USED[src] = USED.get(src, 0) + 1
    if USED[src] > 1:
        b, e = os.path.splitext(src); dup = f'{b}-{USED[src]}{e}'; shutil.copy(f'assets/cut/{src}', f'assets/cut/{dup}'); src = dup
    return f'<img class="pc" id="{id}" src="assets/cut/{src}" style="left:{x}px;top:{y}px;width:{w}px;z-index:{z}">'
def tape(id, x, y, rot=0):
    ROT[id] = rot; return f'<div class="tape" id="{id}" style="left:{x}px;top:{y}px;z-index:9"></div>'
def line(id, x, y, w, h, d, color='#ffffff', sw=9, z=8):
    return (f'<svg class="ink" id="{id}" style="left:{x}px;top:{y}px;z-index:{z}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<path pathLength="1" stroke-dasharray="1" stroke-dashoffset="1" d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"/></svg>')
ARROW_R = 'M10 100 C60 90 120 95 180 100 M150 70 L185 100 L150 130'
BURST = 'M100 20 L110 80 M150 40 L125 88 M180 100 L122 104 M150 160 L120 118 M50 160 L80 118 M20 100 L78 104 M50 40 L88 88'
STAR = 'M100 30 L112 88 L170 100 L112 112 L100 170 L88 112 L30 100 L88 88 Z'

# ---------- ท่าขยับ ----------
def slap(id, t, s='click', d=0.26):
    rot = ROT.get(id, 0)
    tw(f"tl.fromTo('#{id}',{{opacity:0,scale:1.35,rotation:{rot + 9}}},{{opacity:1,scale:1,rotation:{rot},duration:{d},ease:'back.out(2.2)'}},{r(t)});")
    if s: fx(t, s)
def slide(id, t, dx=0, dy=0, s='swoosh', d=0.45):
    rot = ROT.get(id, 0)
    tw(f"tl.fromTo('#{id}',{{opacity:0,x:{dx},y:{dy},rotation:{rot - 8}}},{{opacity:1,x:0,y:0,rotation:{rot},duration:{d},ease:'power3.out'}},{r(t)});")
    if s: fx(t, s)
def bump(id, t, k=1.12):
    tw(f"tl.to('#{id}',{{scale:{k},duration:0.12,yoyo:true,repeat:1,ease:'power2.out'}},{r(t)});"); fx(t, 'click', 0.3)
def shake(id, t, n=6, a=14):
    tw(f"tl.fromTo('#{id}',{{x:{-a}}},{{x:{a},duration:0.04,yoyo:true,repeat:{n},ease:'none',immediateRender:false}},{r(t)});")
    tw(f"tl.set('#{id}',{{x:0}},{r(t + 0.04 * (n + 1) + 0.01)});")
def out(id, t, d=0.18):
    tw(f"tl.to('#{id}',{{opacity:0,scale:0.92,duration:{d},ease:'power2.in'}},{r(t)});")
def draw(id, t, d=0.4, s='pen'):
    tw(f"tl.fromTo('#{id} path',{{strokeDashoffset:1}},{{strokeDashoffset:0,duration:{d},ease:'power2.inOut'}},{r(t)});")
    if s: fx(t, s)
def boil(ids, t0, t1, step=0.25):
    for k, id in enumerate(ids):
        rot = ROT.get(id, 0); t = t0 + 0.6 + k * 0.07; i = 0
        while t < t1 - 0.25:
            tw(f"tl.set('#{id}',{{rotation:{rot + (0.8 if i % 2 else -0.8)}}},{r(t)});"); t += step; i += 1

# ===== 1 · Text Hook: ประโยคเปิดขึ้นทีละคำตามเสียง (สลับเล็ก/ใหญ่ · คำเด่นสี Ember) แล้วค่อยเข้าภาพคนพูด =====
def hook(t_end, words):
    """words = [(เวลา, ข้อความ, คลาส, top)] · คลาส: hk-s (เล็ก) / hk-m / hk-xl (ใหญ่มาก) / hk-em (ใหญ่ สีส้ม เอียง)"""
    body = ''.join(f'<div class="hk {c}" id="hw{i}" style="top:{y}px">{w}</div>' for i, (t, w, c, y) in enumerate(words))
    html.append(f'<div id="hook"><div class="dim"></div>{body}</div>')
    for i, (t, w, c, y) in enumerate(words):
        big = c in ('hk-xl', 'hk-em')
        tw(f"tl.fromTo('#hw{i}',{{opacity:0,scale:{1.6 if big else 0.7},y:{0 if big else 16}}},{{opacity:1,scale:1,y:0,duration:{0.22 if big else 0.16},ease:'{'back.out(2.4)' if big else 'power2.out'}'}},{r(t)});")
        fx(t, 'thump' if big else 'click', 0.55 if big else 0.3)
    tw(f"tl.to('#hook',{{opacity:0,duration:0.2,ease:'power2.in'}},{r(t_end - 0.2)});")
    HIDE_SUBS.append((0, t_end))
TH = at('เรื่องของการใช้')
hook(TH, [
    (at('เห็นเทรนด์'), 'เห็นเทรนด์นี้ยัง?', 'hk-s', 520),
    (at('Twitter') - 0.05, 'บน Twitter', 'hk-s', 600),
    (at('GenC'), 'GEN Z', 'hk-xl', 690),
    (at('กับ'), 'กับ', 'hk-m', 900),
    (at('GenY') + 0.04, 'GEN Y', 'hk-xl', 970),
    (at('มันตีกัน'), 'ตีกัน!', 'hk-em', 1190),
])
shake('hw5', at('มันตีกัน') + 0.25, 6, 10)

# ===== 2 · Super: คำสำคัญที่ไม่ต้อง animate เป็นภาพ — แถบกระดาษเหนือหัวคนพูด แปะแล้วหายไป =====
def sup(n, t0, t1, parts):
    """parts = [(เวลาแปะ, ข้อความ, kind, cls, top, rot)] · วางกลางจอบนพื้นที่ว่างเหนือหัว (y 250–500)"""
    body = ''.join(strip(f'p{n}_{i}', txt, 0, y, kind, cls, rot, z=10, center=True) for i, (t, txt, kind, cls, y, rot) in enumerate(parts))
    html.append(f'<div class="super" id="sp{n}">{body}</div>')
    for i, (t, *_ ) in enumerate(parts): slap(f'p{n}_{i}', t, 'thump' if i == 0 else 'click')
    for i, _ in enumerate(parts): out(f'p{n}_{i}', t1 - 0.18)
    HIDE_SUBS.append((t0, t1))            # ผู้ใช้สั่ง: ตอนขึ้น Super ไม่ต้องมีซับ (ซ้ำกับคำบนจอ)
sup(1, at('ไม่ได้มีใครผิด'), at('เพราะว่าจริง') - 0.1, [(at('ไม่ได้มีใครผิด'), 'ไม่มีใคร<span class="em">ผิด</span>', 's-paper', 'thb th', 300, -3)])
sup(2, at('LearningAgility'), at('จริงๆปัญหา') - 0.2, [(at('LearningAgility'), 'LEARNING AGILITY', 's-navy', 'mid', 290, -2),
                                                       (at('LearningAgility') + 1.4, 'ปรับตัวได้เร็ว', 's-ember', 'ths th', 420, 3)])
sup(3, at('Unlearn'), at('คือหยุดเอา') + 1.6, [(at('Unlearn'), 'UNLEARN', 's-navy', 'big', 280, -3), (at('ของเดิม'), 'ของเดิม', 's-paper', 'thm th', 430, 4)])
sup(4, at('Relearn'), at('เราต้องเปลี่ยน') - 0.1, [(at('Relearn'), 'RELEARN', 's-paper', 'big', 280, 3), (at('ของใหม่'), 'ของใหม่', 's-ember', 'thm th', 430, -4)])
sup(5, at('เปลี่ยนแปลง'), at('เพราะฉะนั้นskill') - 0.1, [(at('เปลี่ยนแปลง'), 'โลกเปลี่ยน<span class="em">เร็ว</span>', 's-paper', 'thb th', 300, -2)])
sup(6, at('ขาดไป') - 0.15, TOTAL, [(at('ขาดไป') - 0.15, 'สกิลที่คนยุคใหม่<span class="em">ขาด</span>', 's-navy', 'thb th', 300, 2)])

# ===== 3 · B-roll collage: เฉพาะจุดที่ภาพทำให้เข้าใจง่ายขึ้น (เปลี่ยนเครื่องมือ คอม/Word ↔ iPad) =====
SEGS = []
def broll(t0, t1, card, body):
    n = len(SEGS) + 1; L = r(t1 - t0); SEGS.append((n, r(t0), r(t1)))
    html.append(f'''<div class="seg" id="g{n}" data-layout-allow-overflow data-layout-allow-occlusion>
  <div class="card {card}"><div class="grain"></div></div>{body}
  <div class="face"><video id="cam{n}" class="clip" data-start="{r(t0)}" data-duration="{L}" data-track-index="{n + 2}" data-media-start="0" muted playsinline src="assets/cam{n}.mp4"></video></div>
</div>''')
    tw(f"tl.fromTo('#g{n}',{{opacity:1,y:1920}},{{opacity:1,y:0,duration:0.3,ease:'power3.out'}},{r(t0)});")
    tw(f"tl.to('#g{n}',{{y:-1920,duration:0.25,ease:'power2.in'}},{r(t1 - 0.25)});")
    fx(t0, 'swoosh', 0.35); HIDE_SUBS.append((t0, t1))

a, b = at('คนนึงอยาก') - 0.1, at('แล้วก็หาว่า')
broll(a, b, 'navy',
    piece('a1', 'pc.png', 150, 450, 360, -6) + tape('a2', 260, 435, -18)
    + piece('a3', 'ipad.png', 550, 700, 420, 8) + tape('a4', 750, 685, 22)
    + strip('a5', 'VS', 420, 620, 's-ember', 'big', -8, z=9)
    + strip('a6', 'GEN Y', 150, 330, 's-paper', 'mid', -4) + strip('a7', 'Microsoft Word', 150, 930, 's-cream', 'sml', 3)
    + strip('a8', 'GEN Z', 620, 1130, 's-paper', 'mid', 5)
    + line('a9', 640, 400, 300, 260, BURST) + line('a10', 180, 1060, 220, 180, STAR, '#ff3608', 8))
slide('a1', a + 0.25, dx=-600); tw(f"tl.fromTo('#a2',{{opacity:0}},{{opacity:1,duration:0.01}},{r(a + 0.6)});")
slap('a6', a + 0.5); slap('a7', at('MicrosoftWord'))
slap('a5', at('แต่GenC'), 'thump'); slide('a3', at('แต่GenC') + 0.3, dx=620); tw(f"tl.fromTo('#a4',{{opacity:0}},{{opacity:1,duration:0.01}},{r(at('แต่GenC') + 0.7)});")
slap('a8', at('ปัจจุบันนี้')); draw('a9', at('iPad') - 0.1, 0.35); bump('a3', at('iPad')); draw('a10', at('iPad') + 0.5, 0.4)
boil(['a1', 'a3', 'a5'], a, b)

a, b = at('ทั้งGenC'), at('ถูกไหม')
broll(a, b, 'ember',
    strip('c1', 'GEN Z', 130, 320, 's-navy', 'mid', -5) + piece('c2', 'ipad.png', 140, 450, 280, -6)
    + line('c3', 420, 520, 160, 120, ARROW_R, '#0d1b2a', 10)
    + piece('c4', 'suit.png', 590, 380, 230, 4) + piece('c5', 'tower.png', 760, 410, 200, -3, z=3)
    + strip('c6', 'PROFESSIONAL', 560, 710, 's-paper', 'sml', -3, z=7)
    + strip('c7', 'GEN Y', 130, 850, 's-paper', 'mid', 4) + piece('c8', 'pc.png', 160, 960, 220, 5)
    + line('c9', 420, 1030, 160, 120, ARROW_R, '#0d1b2a', 10)
    + piece('c10', 'ipad.png', 600, 900, 320, 7))
slap('c1', a); slide('c2', a + 0.3, dx=-400, s=None); draw('c3', at('Unlearn', 3), 0.3)
slide('c4', at('Professional'), dy=-500); slide('c5', at('Corporate'), dx=500, s=None); slap('c6', at('Professional') + 0.25)
slap('c7', at('GenYก็ต้อง')); slide('c8', at('GenYก็ต้อง') + 0.3, dx=-400, s=None); draw('c9', at('Unlearn', 4) + 0.3, 0.3)
slide('c10', at('iPadมันทำ'), dx=500)
boil(['c2', 'c4', 'c8', 'c10'], a, b)

# ===== 4 · ซับ (สไตล์ทีม: Anuphan Medium ขาว) · ไม่ขึ้นช่วง Hook และช่วง B-roll =====
caps = []
if SUBS:
    def ts(x): h, m, s_ = x.replace(',', '.').split(':'); return int(h) * 3600 + int(m) * 60 + float(s_)
    for blk in open(SUBS, encoding='utf-8-sig').read().replace('\r', '').strip().split('\n\n'):
        ln = blk.split('\n'); s_, e_ = ln[1].split(' --> '); caps.append((ts(s_), ts(e_), re.sub(r'\s*ๆ\s*', ' ๆ ', ' '.join(ln[2:])).strip()))   # ไม้ยมก ๆ เว้นวรรคหน้า-หลัง
ch = []
for i, (s_, e_, txt) in enumerate(caps):
    for h0, h1 in HIDE_SUBS:              # ตัดช่วงที่ทับ Hook / B-roll ออก
        if s_ < h1 and e_ > h0:
            if s_ >= h0: s_ = max(s_, h1)
            else: e_ = min(e_, h0)
    if e_ - s_ < 0.3: continue
    ch.append(f'<div class="sub" id="sb{i}">{escape(txt)}</div>')
    tw(f"tl.fromTo('#sb{i}',{{opacity:0}},{{opacity:1,duration:0.01}},{r(s_)});"); tw(f"tl.set('#sb{i}',{{opacity:0}},{r(e_)});")
tw(f"tl.to('#fade',{{opacity:1,duration:0.5}},{r(TOTAL - 0.5)});")
tw('tl.set([' + ','.join(f"'#{k}'" for k, v in ROT.items() if v) + '],{rotation:(i,el)=>ROTS[el.id]},0);')

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
    const ROTS = {json.dumps(ROT)};
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join('    ' + l for l in js)}
    window.__timelines["main"] = tl;
  </script>
</body></html>'''
open('index.html', 'w', encoding='utf-8').write(doc)

FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
for n, a, b in SEGS:
    o = f'assets/cam{n}.mp4'; key = f'{a}-{b}-{FACE_CROP}'; st = o + '.key'
    if os.path.exists(o) and os.path.exists(st) and open(st).read() == key: continue
    subprocess.run([FF, '-nostdin', '-v', 'error', '-ss', str(a), '-t', str(r(b - a)), '-i', 'assets/talk.mp4', '-an', '-vf', f'crop={FACE_CROP},scale=410:410',
                    '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-y', o], check=True); open(st, 'w').write(key)
if not os.path.exists('assets/voice.wav'):
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', 'assets/talk.mp4', '-vn', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', '-ac', '2', '-y', 'assets/voice.wav'], check=True)
FILES = {'swoosh': 'assets/sfx/swoosh.mp3', 'click': 'assets/sfx/click.mp3', 'thump': 'assets/sfx/thump.wav', 'pen': 'assets/sfx/pen.wav'}
cmd = [FF, '-nostdin', '-v', 'error', '-i', 'assets/voice.wav']; fl = ['[0:a]aformat=sample_rates=48000:channel_layouts=stereo[v]']; lab = ['[v]']
for k, (tm, kind, vol) in enumerate(SFX, 1):
    cmd += ['-i', FILES[kind]]; ms = int(tm * 1000)
    fl.append(f'[{k}:a]volume={vol},aformat=sample_rates=48000:channel_layouts=stereo,adelay={ms}|{ms}[s{k}]'); lab.append(f'[s{k}]')
fl.append(''.join(lab) + f'amix=inputs={len(lab)}:normalize=0:duration=first,atrim=0:{TOTAL},alimiter=limit=0.8:level=false[out]')
subprocess.run(cmd + ['-filter_complex', ';'.join(fl), '-map', '[out]', '-ar', '48000', '-ac', '2', '-y', 'assets/mix.wav'], check=True)
print('hook 0–', r(TH), '· supers 6 · B-roll', SEGS, '· subs', len(ch), '· tweens', len(js), '· sfx', len(SFX))
