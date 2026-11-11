"""ปก + Super แบบ template ทีม (Tiktok 180526 / มอเกษตร) → โปรเจกต์ HyperFrames แยกตัวละโฟลเดอร์ใน gfx/
ปก: ม่านกรมท่า Gradient Blue copy.png + บรรทัด 1 ขาว Anuphan + บรรทัด 2 ส้ม UID Deep sea เขียนออกมา + เส้นใต้จาก cover font.png
Super: ม่านกรมท่า + คำขาวกลางจอ พิมพ์ออกมาซ้ายไปขวา (คู่กับเสียง typewriter)
ใช้: python3 -I work/gen_gfx.py  แล้วเรนเดอร์ทีละโฟลเดอร์ (ดู render_gfx.sh)"""
import json, os, shutil
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
TEAM = '/Volumes/Extreme SSD/Copied_Tiktok 180526'
FONTS = os.path.expanduser('~/Library/Fonts')
E = json.load(open(f'{HERE}/edl.json', encoding='utf-8'))
ORANGE = '#FF4F1F'   # สีจาก cover font.png ของทีม

def project(name, dur, body, js):
    d = f'{P}/gfx/{name}'; os.makedirs(f'{d}/assets', exist_ok=True)
    for src, dst in [(f'{TEAM}/Gradient Blue copy.png', 'veil.png'), (f'{P}/assets/underline.png', 'underline.png'),
                     (f'{FONTS}/Anuphan-SemiBold.ttf', 'Anuphan-SemiBold.ttf'), (f'{FONTS}/UID Deep sea.ttf', 'UIDDeepSea.ttf')]:
        if not os.path.exists(f'{d}/assets/{dst}'): shutil.copy(src, f'{d}/assets/{dst}')
    shutil.copy(os.path.expanduser('~/.claude/skills/base-motion-collage/template/package.json'), d)
    shutil.copy(os.path.expanduser('~/.claude/skills/base-motion-collage/template/hyperframes.json'), d)
    html = f'''<!doctype html>
<html lang="th">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: 'Anuphan'; src: url('assets/Anuphan-SemiBold.ttf'); font-weight: 600; }}
    @font-face {{ font-family: 'UIDDeepSea'; src: url('assets/UIDDeepSea.ttf'); }}
    html, body {{ margin: 0; width: 1080px; height: 1920px; background: transparent; overflow: hidden; }}
    #root {{ position: relative; width: 1080px; height: 1920px; }}
    .veil {{ position: absolute; inset: 0; width: 1080px; height: 1920px; }}
    .t {{ position: absolute; left: 0; width: 1080px; text-align: center; white-space: nowrap; }}
    .t1 {{ top: 812px; font: 600 112px/1.25 'Anuphan'; color: #fff; text-shadow: 0 4px 18px rgba(0,0,0,.35); }}
    .t2 {{ top: 940px; font: 150px/1.2 'UIDDeepSea'; color: {ORANGE}; }}
    .ul {{ position: absolute; left: 0; top: 1092px; width: 1080px; }}   /* ต่ำกว่าสระล่าง (ู ุ) */
    .sup {{ top: 890px; font: 600 118px/1.25 'Anuphan'; color: #fff; text-shadow: 0 4px 18px rgba(0,0,0,.35); }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="1080" data-height="1920">
{body}
  </div>
  <script>
    // ข้อความยาวเกินจอ → ย่อฟอนต์ให้พอดี 1000px (ไม่ล้นขอบ)
    document.querySelectorAll('.t').forEach(el => {{ const r = document.createRange(); r.selectNodeContents(el); const w = r.getBoundingClientRect().width; if (w > 1000) el.style.fontSize = (parseFloat(getComputedStyle(el).fontSize) * 1000 / w) + 'px'; }});
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
{js}
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
'''
    open(f'{d}/index.html', 'w', encoding='utf-8').write(html)
    return d

wipe = lambda sel, at, d: f"    tl.fromTo('{sel}',{{clipPath:'inset(-20% 100% -20% -2%)'}},{{clipPath:'inset(-20% -2% -20% -2%)',duration:{d},ease:'none'}},{at});"

c = E['cover']; D = c['dur']
project('cover', D, f'''    <img class="veil clip" id="veil" src="assets/veil.png" data-start="0" data-duration="{D}" data-track-index="0" />
    <div class="t t1 clip" id="t1" data-start="0" data-duration="{D}" data-track-index="1">{c['t1']}</div>
    <div class="t t2 clip" id="t2" data-start="0" data-duration="{D}" data-track-index="2">{c['t2']}</div>
    <img class="ul clip" id="ul" src="assets/underline.png" data-start="0" data-duration="{D}" data-track-index="3" />''',
    '\n'.join([f"    tl.fromTo('#t1',{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35,ease:'power2.out'}},0.05);",
               wipe('#t2', 0.3, 0.7), wipe('#ul', 0.85, 0.4),
               f"    tl.to(['#veil','#t1','#t2','#ul'],{{opacity:0,duration:0.2,ease:'power1.in'}},{round(D - 0.2, 3)});"]))

for i, s in enumerate(E['supers'], 1):
    D = s['dur']; n = len(s['text'])
    project(f'super{i}', D, f'''    <img class="veil clip" id="veil" src="assets/veil.png" data-start="0" data-duration="{D}" data-track-index="0" />
    <div class="t sup clip" id="s" data-start="0" data-duration="{D}" data-track-index="1">{s['text']}</div>''',
        '\n'.join([f"    tl.fromTo('#veil',{{opacity:0}},{{opacity:1,duration:0.2}},0);",
                   wipe('#s', 0.1, round(min(0.6, 0.04 * n), 2)),
                   f"    tl.to(['#veil','#s'],{{opacity:0,duration:0.2,ease:'power1.in'}},{round(D - 0.2, 3)});"]))
print('✅ gfx/cover + super1–' + str(len(E['supers'])))
