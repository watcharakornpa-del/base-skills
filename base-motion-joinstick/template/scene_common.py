# ===== 1 · Text Hook =====
# ชิ้นส่วนกลางของชุด AI Productivity (คลิป 4–12) — ก๊อปจาก C2678 · ใช้คู่กับไฟล์ฉากของแต่ละคลิปที่ต่อท้าย (CFG_* ด้านล่างไฟล์นั้น)
# ปก = ชื่อคลิปจากชีตสคริปต์ (ไม่มี MICRO LEARNING) · ไม่มีซับใต้ Super/การ์ด/B-roll/ปก · screen record ซิงค์กับกล้องด้วย SCR_OFF
import math as _m, json as _j
def hook(t_end, words):
    body = ''.join(f'<div class="hk {c}" id="hw{i}" style="top:{y}px">{w}</div>' for i, (t, w, c, y) in enumerate(words))
    html.append(f'<div id="hook"><div class="dim"></div>{body}</div>')
    for i, (t, w, c, y) in enumerate(words):
        big = c in ('hk-xl', 'hk-em')
        tw(f"tl.fromTo('#hw{i}',{{opacity:0,scale:{1.4 if big else 0.8},y:{0 if big else 16}}},{{opacity:1,scale:1,y:0,duration:{0.24 if big else 0.18},ease:'{'back.out(2.2)' if big else 'power2.out'}'}},{r(t)});")
        fx(t, 'thump' if big else 'click', 0.55 if big else 0.3)
    tw(f"tl.to('#hook',{{opacity:0,duration:0.2,ease:'power2.in'}},{r(t_end - 0.2)});")
    HIDE_SUBS.append((0, t_end))
NS = [0]
def sup(t0, t1, rows, pops):
    assert t1 - t0 > 0.5, f'Super สั้น/กลับด้าน {t0}–{t1} {[i for i, _ in pops]}'
    for _i, _t in pops: assert t0 - 0.35 <= _t < t1, f'pop {_i} {_t} อยู่นอก Super {t0}–{t1}'
    NS[0] += 1
    html.append(f'<div class="super">' + ''.join(f'<div class="row" style="top:{y}px">{h}</div>' for h, y in rows) + '</div>')
    for k, (id, t) in enumerate(pops): pop(id, t, 'thump' if k == 0 else 'click'); out(id, t1 - 0.2)
    HIDE_SUBS.append((t0, t1))
def pill(id, txt, on=False, fl=False): return f'<div class="pill{" on" if on else ""}" id="{id}">{flame(30, "#fff" if on else "#EA3A1F") if fl else ""}{txt}</div>'
def chip(id, ttl, lbl='', hot=False):
    return f'<div class="chip{" hot" if hot else ""}" id="{id}">{f"<div class=lbl>{lbl}</div>" if lbl else ""}<div class="ttl">{ttl}</div></div>'
SEGS = []
def broll(t0, t1, body, under=''):
    assert t1 - t0 > 1.0, f'B-roll สั้น/กลับด้าน {t0}–{t1}'
    n = len(SEGS) + 1; L = r(t1 - t0); SEGS.append((n, r(t0), r(t1)))
    html.append(f'''<div class="seg" id="g{n}" data-layout-allow-overflow data-layout-allow-occlusion>{under}{body}
  <div class="face"><video id="cam{n}" class="clip" data-start="{r(t0)}" data-duration="{L}" data-track-index="{n + 2}" data-media-start="0" muted playsinline src="assets/cam{n}.mp4"></video></div>
</div>''')
    tw(f"tl.fromTo('#g{n}',{{opacity:1,y:1920}},{{opacity:1,y:0,duration:0.3,ease:'power3.out'}},{r(t0)});")
    if t1 < TOTAL - 0.1: tw(f"tl.to('#g{n}',{{y:-1920,duration:0.25,ease:'power2.in'}},{r(t1 - 0.25)});")
    fx(t0, 'swoosh', 0.35); HIDE_SUBS.append((t0, t1))
def hd(lbl, ttl): return f'<div class="hd"><div class="lbl">{lbl}</div><div class="ttl">{ttl}</div></div>'
IC = {
 'search':'<svg class="ic" viewBox="0 0 48 48"><circle cx="20" cy="20" r="14" fill="none" stroke="{c}" stroke-width="3.6"/><path d="M30 30L44 44" stroke="{c}" stroke-width="4" stroke-linecap="round"/></svg>',
 'table': '<svg class="ic" viewBox="0 0 48 48"><rect x="4" y="6" width="40" height="36" rx="5" fill="none" stroke="{c}" stroke-width="3.2"/><path d="M4 18H44M4 30H44M18 6V42" stroke="{c}" stroke-width="3"/></svg>',
 'chat':  '<svg class="ic" viewBox="0 0 48 48"><path d="M6 8H42V34H20L10 42V34H6Z" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/></svg>',
 'doc':   '<svg class="ic" viewBox="0 0 40 48"><path d="M4 2H26L36 12V46H4Z" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/><path d="M26 2V12H36" fill="none" stroke="{c}" stroke-width="3.2" stroke-linejoin="round"/><path d="M11 22H29M11 30H29M11 38H22" stroke="{c}" stroke-width="3" stroke-linecap="round"/></svg>',
 'check': '<svg class="ic" viewBox="0 0 48 48"><circle cx="24" cy="24" r="20" fill="none" stroke="{c}" stroke-width="3.2"/><path d="M14 25L21 32L35 17" fill="none" stroke="{c}" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>',
}
def step(id, y, n, ic, txt, hot=False, cls=''):
    return (f'<div class="stp{" hot" if hot else ""} {cls}" id="{id}" style="top:{y}px"><div class="n">{n}</div>{IC[ic].format(c="#EA3A1F" if hot else "#fff") if ic else ""}'
            f'<div class="tx th">{txt}</div></div>')
# Screen record ซิงค์: ชิ้นจาก keep.json (เวลาไฟล์ดิบ) → ชิ้นเดียวกันใน screen.mp4 (เวลา insert = เวลากล้อง − SCR_OFF) วางที่เวลาเดียวกับ talk.mp4
_KEEP = _j.load(open('../work/keep.json', encoding='utf-8')); _FR = 25.0
_PIECES = []; _t = 0.0
for _s, _e in _KEEP:
    _L = max(_e - _s, (_m.ceil(_e * _FR - 1e-6) - _m.ceil(_s * _FR - 1e-6)) / _FR); _PIECES.append((_t, _L, _s)); _t += _L
SCR_N = [0]
def screen(t0, t1, off):
    out_ = []
    for T, L, s in _PIECES:
        a_, b_ = max(T, t0), min(T + L, t1)
        if b_ - a_ < 0.04 or s - off + (a_ - T) < 0: continue
        SCR_N[0] += 1
        out_.append(f'<video id="sc{SCR_N[0]}" class="clip scr" data-start="{r(a_)}" data-duration="{r(b_ - a_)}" data-track-index="30" '
                    f'data-media-start="{r(s - off + (a_ - T))}" muted playsinline src="assets/screen.mp4"></video>')
    return ''.join(out_)
def screenroll(t0, t1, off, lbl, ttl, pills=(), pills2=()):
    """screen record เต็มจอ + หัว + ชิปเด้งตามคำพูด (pills = [(id, ข้อความ, เวลา, on)]) · pills2 = แถวที่ 2 (แทนที่แถวแรก)"""
    row = lambda ps: '<div class="row scrrow" style="top:220px"><div class="wrap">' + ''.join(pill(i, t, on=o) for i, t, _, o in ps) + '</div></div>' if ps else ''
    broll(t0, t1, '<div class="scrhd">' + hd(lbl, ttl) + '</div>' + row(pills) + row(pills2), under=screen(t0, t1, off))
    for k, (i, _, t, _) in enumerate(pills): pop(i, t, 'click')
    if pills2:
        tt = pills2[0][2]
        for i, *_ in pills: out(i, tt - 0.1)
        for i, _, t, _ in pills2: pop(i, t, 'click')
def tryit(t0, steps):
    """steps = [(id, ไอคอน, ข้อความ, เวลาเด้ง)]"""
    broll(t0, TOTAL, hd('TRY IT', 'ลองกับ<span class="red">งานจริง</span>ของเรา') + ''.join(step(i, 470 + 170 * k, k + 1, ic, tx) for k, (i, ic, tx, _) in enumerate(steps)))
    for i, _, _, t in steps: pop(i, t, 'click')
def screenstages(t0, t1, off, lbl, ttl, stages, y=220):
    """screen record + ชิปหลายชุด: stages = [[(id, ข้อความ, เวลา, on), ...], ...] · ชุดถัดไปขึ้น = ชุดก่อนหน้าหายไป"""
    rows = ''.join(f'<div class="row scrrow sm2" style="top:{y}px"><div class="wrap">' + ''.join(pill(i, t, on=o) for i, t, _, o in st) + '</div></div>' for st in stages)
    broll(t0, t1, '<div class="scrhd">' + hd(lbl, ttl) + '</div>' + rows, under=screen(t0, t1, off))
    for k, st in enumerate(stages):
        for i, _, t, _ in st: pop(i, t, 'click')
        if k + 1 < len(stages):
            for i, *_ in st: out(i, stages[k + 1][0][2] - 0.1)
def drop(id, t, s='click', rot=0):
    tw(f"tl.fromTo('#{id}',{{opacity:0,y:-160,rotation:{rot - 8}}},{{opacity:1,y:0,rotation:{rot},duration:0.38,ease:'back.out(1.6)'}},{r(t)});")
    if s: fx(t, s)
def item(id, x, y, lbl, nm, ic, rot=0, cls=''):
    return (f'<div class="it2 {cls}" id="{id}" style="left:{x}px;top:{y}px;transform:rotate({rot}deg)">'
            f'{IC[ic].format(c="#EA3A1F" if "hot" in cls else "#fff")}<div><div class="lbl">{lbl}</div><div class="nm th">{nm}</div></div></div>')
