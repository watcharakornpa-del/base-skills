#!/usr/bin/env python3
"""ทำชิ้นกระดาษตัดสำหรับ collage: ภาพดิบ → PNG พื้นใส + ขอบกระดาษขาว (+ขาวดำ/สีทับ)
ใช้ (รันจากโฟลเดอร์โปรเจกต์):
  python work/cutout.py assets/raw/tv.jpg assets/cut/tv.png --mode subject --bw
  python work/cutout.py assets/raw/city.jpg assets/cut/city.png --mode torn --tint navy
โหมด
  subject = ลบพื้นหลังด้วย `hyperframes remove-background` (โมเดลบนเครื่อง ไม่ส่งภาพออกไปไหน) แล้วตัดขอบขาวรอบตัว
  torn    = ไม่ลบพื้น · ตัดเป็นแผ่นสี่เหลี่ยมขอบฉีกขาด ๆ (ภาพฉาก/ตึก/ท้องฟ้า)
  white   = ภาพประกอบ/สติกเกอร์พื้นขาว · ลบสีขาวที่ต่อกับขอบ
  keep    = ภาพมีพื้นใสอยู่แล้ว (PNG) · แค่เติมขอบขาว
ตัวเลือก --bw ขาวดำคอนทราสต์สูง · --tint ember|navy ย้อมสองสี (duotone) · --border px ขอบขาว (0 = ไม่มี) · --max px ด้านยาวสุด"""
import argparse, os, random, subprocess, sys, tempfile
from PIL import Image, ImageFilter, ImageOps, ImageEnhance, ImageDraw, ImageChops
sys.stdout.reconfigure(encoding='utf-8')
CI = {'ember': ((40, 8, 0), (255, 54, 8)), 'navy': ((13, 27, 42), (237, 230, 220))}   # (เงา, สว่าง)

ap = argparse.ArgumentParser()
ap.add_argument('src'); ap.add_argument('dst')
ap.add_argument('--mode', choices=['subject', 'white', 'torn', 'keep'], default='subject')
ap.add_argument('--bw', action='store_true'); ap.add_argument('--tint', choices=list(CI))
ap.add_argument('--border', type=int, default=12); ap.add_argument('--max', type=int, default=1100)
ap.add_argument('--seed', type=int, default=7)
a = ap.parse_args(); random.seed(a.seed)

src = a.src
if a.mode == 'subject':
    tmp = os.path.join(tempfile.mkdtemp(), 'cut.png')
    r = subprocess.run(f'npx --yes hyperframes@0.8.147 remove-background "{src}" -o "{tmp}"', shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode or not os.path.exists(tmp): sys.exit('❌ remove-background ล้ม: ' + (r.stderr or r.stdout)[-400:])
    src = tmp
im = Image.open(src).convert('RGBA')
im.thumbnail((a.max, a.max), Image.LANCZOS)

if a.mode == 'white':     # ภาพประกอบพื้นขาว/ลายตาราง: ลบสีอ่อนที่ต่อกับขอบภาพ (โมเดลลบพื้นมักตัดภาพวาดพลาด)
    w, h = im.size; rgb0 = im.convert('RGB'); seen = Image.new('L', im.size, 0); px = rgb0.load(); sp = seen.load()
    stack = [(x, y) for x in range(w) for y in (0, h - 1)] + [(x, y) for y in range(h) for x in (0, w - 1)]
    while stack:
        x, y = stack.pop()
        if sp[x, y] or min(px[x, y]) < 225 or max(px[x, y]) - min(px[x, y]) > 18: continue
        sp[x, y] = 255
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and not sp[nx, ny]: stack.append((nx, ny))
    im.putalpha(ImageChops.subtract(im.getchannel('A'), seen.filter(ImageFilter.MaxFilter(3))))
if a.mode == 'subject':   # ตัดเศษพื้นที่โมเดลเหลือไว้ + เก็บเฉพาะก้อนใหญ่
    al = im.getchannel('A').point(lambda v: 255 if v > 128 else 0)
    im.putalpha(al.filter(ImageFilter.MedianFilter(5)))
if a.mode == 'torn':      # ขอบฉีก: สุ่มจุดรอบสี่เหลี่ยมให้หยัก
    w, h = im.size; pad = 6; pts = []
    def edge(x0, y0, x1, y1, n):
        for i in range(n):
            t = i / n; j = random.uniform(-9, 9)
            x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
            pts.append((x + (j if x0 == x1 else 0), y + (j if y0 == y1 else 0)))
    n = max(20, w // 18)
    edge(pad, pad, w - pad, pad, n); edge(w - pad, pad, w - pad, h - pad, max(20, h // 18))
    edge(w - pad, h - pad, pad, h - pad, n); edge(pad, h - pad, pad, pad, max(20, h // 18))
    m = Image.new('L', im.size, 0); ImageDraw.Draw(m).polygon(pts, fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel('A'), m))

rgb = im.convert('RGB'); alpha = im.getchannel('A')
if a.bw or a.tint:
    g = ImageOps.autocontrast(ImageOps.grayscale(rgb), cutoff=2)
    g = ImageEnhance.Contrast(g).enhance(1.35)
    rgb = ImageOps.colorize(g, *CI[a.tint]) if a.tint else g.convert('RGB')
out = Image.merge('RGBA', (*rgb.split(), alpha))

if a.border > 0:          # ขอบกระดาษขาว = ขยาย alpha ออก แล้ววางขาวไว้ข้างหลัง
    b = a.border; W, H = out.size
    canvas = Image.new('RGBA', (W + 2 * b, H + 2 * b), (0, 0, 0, 0))
    big = Image.new('L', canvas.size, 0); big.paste(alpha, (b, b))
    grown = big.filter(ImageFilter.MaxFilter(b * 2 + 1 if b * 2 + 1 <= 61 else 61))
    grown = grown.filter(ImageFilter.GaussianBlur(1.2)).point(lambda v: 255 if v > 90 else 0)
    paper = Image.new('RGBA', canvas.size, (250, 247, 240, 255)); paper.putalpha(grown)
    canvas = Image.alpha_composite(canvas, paper)
    layer = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); layer.paste(out, (b, b), out)
    out = Image.alpha_composite(canvas, layer)

bbox = out.getchannel('A').getbbox()
if bbox: out = out.crop(bbox)
os.makedirs(os.path.dirname(os.path.abspath(a.dst)), exist_ok=True)
out.save(a.dst, optimize=True)
print('✅', a.dst, out.size)
