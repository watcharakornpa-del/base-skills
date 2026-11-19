#!/usr/bin/env python3
"""ตรวจ CI ของกราฟิก JOINSTICK ก่อนเรนเดอร์/ก่อนส่ง (ผู้ใช้สั่ง 19 พ.ย. 2026: "เวลาตรวจ เช็ค CI ด้วยทุกครั้ง")
ใช้: python cicheck.py <โปรเจกต์ หรือ โฟลเดอร์ gfx>   → exit 1 ถ้าผิด
1 ฟอนต์: ทุก font / font-family ที่มี Poppins ต้องมี 'Plex Thai' ด้วย (ไม่งั้นคำไทยตกไปฟอนต์ระบบ — ปกคลิป 10–12 พลาดแบบนี้)
         @font-face ได้แค่ Poppins + Plex Thai · ทุกข้อความที่มีอักษรไทยใน index.html ต้องได้ฟอนต์ที่มี Plex Thai
2 สี: ใช้แค่ ดำ · ขาว/เทา · แดง (#EA3A1F โทนแดง) — ห้ามน้ำเงิน ม่วง เหลือง ทอง เขียว
3 ห้ามไล่สี (linear/radial-gradient) · ห้าม glow (เงาสี)"""
import colorsys, os, re, sys
G = sys.argv[1] if len(sys.argv) > 1 else '.'
if os.path.isdir(os.path.join(G, 'gfx')): G = os.path.join(G, 'gfx')
css = open(os.path.join(G, 'style.css'), encoding='utf-8').read()
html = open(os.path.join(G, 'index.html'), encoding='utf-8').read() if os.path.exists(os.path.join(G, 'index.html')) else ''
bad = []
nocomment = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
# 1 ฟอนต์
for fam in re.findall(r"@font-face\s*{[^}]*font-family:\s*['\"]([^'\"]+)", nocomment):
    if fam not in ('Poppins', 'Plex Thai'): bad.append(f'ฟอนต์นอก CI: {fam}')
rules = re.findall(r'([^{}]+){([^{}]*)}', nocomment)
for sel, body in rules:
    if sel.strip().startswith('@font-face'): continue
    for m in re.finditer(r'font(?:-family)?\s*:\s*([^;]+)', body):
        v = m.group(1)
        if ('Poppins' in v or 'sans-serif' in v or 'serif' in v) and 'Plex Thai' not in v:
            bad.append(f'ฟอนต์ไม่มี Plex Thai สำรอง: {sel.strip()[:60]} → {v.strip()[:60]}')
        for fam in re.findall(r"['\"]([^'\"]+)['\"]", v):
            if fam not in ('Poppins', 'Plex Thai'): bad.append(f'ฟอนต์นอก CI: {fam} ที่ {sel.strip()[:40]}')
# ข้อความไทยใน html: ถ้า inline style กำหนด font-family ต้องมี Plex Thai
for st in re.findall(r'style="([^"]*font[^"]*)"', html):
    if 'font' in st and 'Plex Thai' not in st and ('Poppins' in st or 'family' in st): bad.append(f'inline font ไม่มี Plex Thai: {st[:60]}')
# 2 สี
def hue_ok(h):
    h = h.lstrip('#')
    if len(h) in (3, 4): h = ''.join(c * 2 for c in h[:3])
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    hh, ss, vv = colorsys.rgb_to_hsv(r, g, b)
    return ss < 0.25 or vv < 0.12 or hh * 360 <= 15 or hh * 360 >= 345
# สีจาก CSS + attribute ที่เป็นสีใน html เท่านั้น (ไม่นับ id ใน tween เช่น '#fade')
src = ' '.join(body for _, body in rules) + ' ' + ' '.join(re.findall(r'(?:style|fill|stroke|color|stop-color)="([^"]*)"', html))
for h in set(re.findall(r'#[0-9a-fA-F]{3,8}\b', src)):
    if len(h) in (4, 5, 7, 9) and not hue_ok(h[:7] if len(h) >= 7 else h): bad.append(f'สีนอก CI: {h}')
for r, g, b in set(re.findall(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', src)):
    if not hue_ok('#%02x%02x%02x' % (int(r), int(g), int(b))): bad.append(f'สีนอก CI: rgb({r},{g},{b})')
for w in ('gold', 'blue', 'purple', 'violet', 'yellow', 'green', 'cyan', 'magenta', 'orange'):
    if re.search(rf'(?<![\w-]){w}(?![\w-])', nocomment): bad.append(f'สีนอก CI (ชื่อสี): {w}')
# 3 ไล่สี / glow
if re.search(r'(?<!repeating-)(linear|radial|conic)-gradient', src): bad.append('มีไล่สี (gradient)')
for sel, body in rules:   # glow = เงามีสี + เบลอ > 0 (วงแหวนทึบ blur 0 ไม่นับ)
    for sh in re.findall(r'(?:text|box)-shadow\s*:\s*([^;]+)', body):
        for part in re.split(r',(?![^(]*\))', sh):
            nums = [float(x) for x in re.findall(r'(?<![\w#(,.])(-?[\d.]+)(?:px)?(?=\s|$)', re.sub(r'(rgba?|hsla?)\([^)]*\)|#[0-9a-fA-F]+', ' ', part).strip() + ' ')]
            blur = nums[2] if len(nums) >= 3 else 0
            col = re.findall(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', part)
            colored = any(max(map(int, c)) > 60 for c in col) or re.search(r'#(?!000\b|0{6})[0-9a-fA-F]{3,6}', part)
            if colored and blur > 0: bad.append(f'glow: {sel.strip()[:40]} → {part.strip()[:50]}')
bad = list(dict.fromkeys(bad))
if bad:
    print('❌ CI ไม่ผ่าน ' + str(len(bad)) + ' จุด'); [print('  -', b) for b in bad]; sys.exit(1)
print('✅ CI ผ่าน: ฟอนต์ Poppins + Plex Thai ครบทุกจุด · สีดำ/ขาว/แดง · ไม่มีไล่สี/glow')
