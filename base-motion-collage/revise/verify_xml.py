#!/usr/bin/env python3
"""ตรวจ XML ซีเควนซ์ Draft2: อ่านได้ · ไฟล์ที่อ้างมีจริง · ภาพเฟรมแรก/กลาง/ท้ายของทุกชิ้นบน V1 ตรงกับ base.mkv (ภาพของ MP4 ก่อนทับกราฟิก)
base.mkv อ่านด้วยเลขเฟรม (select) ไม่ใช้ -ss เพราะไฟล์ที่ต่อด้วย concat กระโดดหาเวลาไม่แม่น
ใช้: python3 -I work/verify_xml.py"""
import json, os, subprocess, xml.etree.ElementTree as ET
from urllib.parse import unquote
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
C = json.load(open(f'{HERE}/clip.json', encoding='utf-8')); T = os.path.basename(C['out'])[:-4]
X = os.path.join(os.path.dirname(os.path.dirname(C['xml'])), 'C5395-draft2', T, f'{T}.xml')
r = ET.parse(X).getroot()
paths = {f.get('id'): unquote(f.find('pathurl').text.replace('file://localhost', '')) for f in r.iter('file') if f.find('pathurl') is not None}
miss = [p for p in paths.values() if not os.path.exists(p)]
print('ไฟล์ที่อ้าง', len(paths), '· หาไม่เจอ', miss or 0)
LUT = f'{P}/assets/BASE-dark-moody.cube'; SZ = 54 * 96
def grab(args, vf):
    return subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', *args, '-frames:v', '1', '-vf', vf + ',scale=54:96,format=gray', '-f', 'rawvideo', '-'], capture_output=True).stdout
def by_index(path, idxs):                                      # อ่านตามเลขเฟรม (แม่นกว่า -ss สำหรับ collage / ไฟล์ concat)
    sel = '+'.join(f'eq(n\\,{n})' for n in sorted(idxs))
    raw = subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', path, '-vf', f"select='{sel}',scale=54:96,format=gray",
                          '-vsync', '0', '-f', 'rawvideo', '-'], capture_output=True).stdout
    return {n: raw[j * SZ:(j + 1) * SZ] for j, n in enumerate(sorted(idxs))}
checks = []                                                    # (เฟรมไทม์ไลน์, ไฟล์, เฟรมในไฟล์ต้นทาง)
for c in r.find('.//video').findall('track')[0].findall('clipitem'):
    fid = c.find('file').get('id'); st, en, i = int(c.find('start').text), int(c.find('end').text), int(c.find('in').text)
    for k in sorted({0, (en - st) // 2, en - st - 1}): checks.append((st + k, fid, i + k))
col = by_index(C['collage'], {s for _, f, s in checks if f == 'f-col'})
src = {s: grab(['-ss', f'{(s + 0.5) * 1001 / 30000:.4f}', '-i', C['src']], f'scale=1080:1920,lut3d={LUT}') for _, f, s in checks if f == 'f-src'}
checks = [(n, f, col[s] if f == 'f-col' else src[s]) for n, f, s in checks]
base = by_index(f'{HERE}/base.mkv', {n for n, _, _ in checks})
worst = 0
for n, fid, a in sorted(checks):
    b = base[n]
    d = sum(abs(x - y) for x, y in zip(a, b)) / SZ; worst = max(worst, d)
    if d > 10: print(f'  ⚠️ เฟรม {n} ({fid}) ต่าง {d:.1f}')
print(f'ตรวจ {len(checks)} เฟรม ·', 'ตรงทุกเฟรม ✅' if worst <= 10 else f'⚠️ ไม่ตรง (สูงสุด {worst:.1f})')
