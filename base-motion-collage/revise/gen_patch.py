#!/usr/bin/env python3
"""แผ่นแปะแก้ป้ายในการ์ด B-roll (เมื่อไม่มีไฟล์ gen.py ของการ์ดเดิม) — ทำป้ายใหม่ด้วย CSS เดียวกับ base-motion-collage
(strip + ขอบกระดาษฉีก + Noto Sans + เงาแข็ง) เข้ามาแบบ slap ทึบตั้งแต่เฟรมแรก (กันป้ายเดิมโผล่จาง ๆ) แล้วค้าง
ใช้: python3 -I work/gen_patch.py <ลำดับ> <ความยาววินาที>  → gfx_patch/p<ลำดับ>/ (compose.py เรียกเอง)
วัด cx, cy, rot จากเฟรมที่ป้ายเดิมนิ่งแล้ว · at = เฟรมแรกที่ป้ายเดิมโผล่ (Draft1)"""
import json, os, random, shutil, sys
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
SK = os.path.expanduser('~/.claude/skills/base-motion-collage/template')
n, DUR = int(sys.argv[1]), float(sys.argv[2])
p = json.load(open(f'{HERE}/edl.json', encoding='utf-8'))['patches'][n]
FILL = {'s-paper': ('#faf7f0', '#0d1b2a'), 's-cream': ('#efe6d6', '#0d1b2a'), 's-ember': ('#ff3608', '#fff'), 's-navy': ('#0d1b2a', '#fff')}
FONT = {'big': "900 110px/1.05 'Noto'; letter-spacing: -3px", 'mid': "900 72px/1.1 'Noto'; letter-spacing: -1px", 'sml': "700 40px/1.2 'Noto'; letter-spacing: 1px"}
bg, fg = FILL[p.get('kind', 's-cream')]; font = FONT[p.get('cls', 'mid')]

def edge(seed, fill, top):            # ก๊อปจาก base-motion-collage/template/gen.py
    R = random.Random(seed); xs = range(0, 101, 4); ys = [R.uniform(1, 9) for _ in xs]
    poly = ('0,10 ' + ' '.join(f'{x},{y:.1f}' for x, y in zip(xs, ys)) + ' 100,10') if top else \
           ('0,0 ' + ' '.join(f'{x},{10 - y:.1f}' for x, y in zip(xs, ys)) + ' 100,0')
    return (f'<svg class="edge" style="{"top" if top else "bottom"}:-9px" viewBox="0 0 100 10" preserveAspectRatio="none">'
            f'<polygon points="{poly}" fill="{fill}"/></svg>')

d = f'{P}/gfx_patch/p{n}'; os.makedirs(f'{d}/fonts', exist_ok=True)
for f in ('NotoSans-Black.ttf', 'NotoSans-Bold.ttf'): shutil.copy(f'{SK}/fonts/{f}', f'{d}/fonts/')
for f in ('package.json', 'hyperframes.json'): shutil.copy(f'{SK}/{f}', d)
s = sum(map(ord, p['text'])) * 7
open(f'{d}/index.html', 'w', encoding='utf-8').write(f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=1080, height=1920" />
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    @font-face {{ font-family: 'Noto'; font-weight: 900; src: url('fonts/NotoSans-Black.ttf'); }}
    @font-face {{ font-family: 'Noto'; font-weight: 700; src: url('fonts/NotoSans-Bold.ttf'); }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{ width: 1080px; height: 1920px; background: transparent; overflow: hidden; }}
    #root {{ position: relative; width: 1080px; height: 1920px; }}
    .hold {{ position: absolute; left: {p['cx']}px; top: {p['cy']}px; width: 0; height: 0; }}
    .shadow {{ position: absolute; transform: translate(-50%, -50%) rotate({p['rot']}deg); filter: drop-shadow(5px 8px 0 rgba(13,27,42,.32)); }}
    .anim {{ transform-origin: 50% 50%; }}
    .strip {{ position: relative; white-space: nowrap; padding: 14px 34px 20px; background: {bg}; color: {fg}; font: {font}; }}
    .edge {{ position: absolute; left: 0; width: 100%; height: 10px; display: block; }}
  </style>
</head>
<body>
  <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1920">
    <div class="hold clip" id="hold" data-start="0" data-duration="{DUR}" data-track-index="0">
      <div class="shadow"><div class="anim" id="anim"><div class="strip">{edge(s, bg, True)}{p['text']}{edge(s + 1, bg, False)}</div></div></div>
    </div>
  </div>
  <script>
    window.__timelines = window.__timelines || {{}};
    const tl = gsap.timeline({{ paused: true }});
    tl.fromTo('#anim', {{ scale: 1.3 }}, {{ scale: 1, duration: 0.23, ease: 'back.out(2.2)' }}, 0);
    window.__timelines["main"] = tl;
  </script>
</body>
</html>
''')
print(f'✅ gfx_patch/p{n}')
