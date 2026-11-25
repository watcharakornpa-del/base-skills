#!/usr/bin/env python3
"""ร่าง captions.txt จาก gfx/work/scribe.json — ตัดวลีตามจังหวะหยุดพูด + ไวยากรณ์ไทย (pythainlp newmm)
กฎ: บรรทัด ≤ 30 ตัวหลังลบ เนาะ/เนอะ/ป่ะ/อ่ะ/นะ · ตัดหลัง ครับ/เนาะ/ช่วงหยุด · ก่อนคำเชื่อม · ไม่ตัดกลางคำ
ใช้: python autocaps.py <gfx/work>  → เขียน captions.txt (ต้องอ่านทวนเองก่อนใช้)"""
import json, re, sys
from pythainlp.tokenize import word_tokenize
D = sys.argv[1]
W = json.load(open(f'{D}/scribe.json', encoding='utf-8'))['words']
# สตรีมตัวอักษร + เวลา (เว้นวรรคของ Scribe เก็บไว้เป็นช่องว่าง)
txt, T = '', []
for w in W:
    s = w['text'] if w['type'] != 'spacing' else ' '
    if w['type'] == 'audio_event': continue
    for c in s: txt += c; T.append((w['start'], w['end']))
toks = word_tokenize(txt, engine='newmm', keep_whitespace=True)
# รวม token: ช่องว่างติดท้ายคำก่อนหน้า · อังกฤษ/ตัวเลขติดกันรวมกัน
units, pos = [], 0
for t in toks:
    a = pos; pos += len(t)
    if t.isspace() and units: units[-1][1] = pos; continue
    units.append([a, pos])
def clean(s):
    s = re.sub(r'เนี้ย', 'นี้', s); s = re.sub(r'(\s*)(เนาะ|เนอะ|ป่ะ|อ่ะ|น่ะ|เนี่ย|เฮ้ย|เอ่อ|เออ(?!ร))', lambda m: ' ' if m.group(1) else '', s); s = re.sub(r'นะ(?=ครับ|ว่า|$)', '', s)
    s = re.sub(r'\s*ๆ\s*', ' ๆ ', s)
    return re.sub(r'\s+', ' ', s).strip()
CONJ = ('ว่า', 'แล้ว', 'และ', 'หรือ', 'เพราะ', 'ที่', 'ก็', 'แต่', 'ถ้า', 'เพื่อ', 'คือ', 'โดย', 'ให้', 'เช่น', 'ซึ่ง', 'จะ', 'เวลา', 'อย่าง', 'จาก', 'ใน', 'กับ', 'ของ', 'เป็น')
END = ('ครับ', 'เนาะ', 'เนอะ', 'นะ', 'ค่ะ', 'ป่ะ', 'อ่ะ')
def gap(i):  # เวลาเงียบหลัง unit i
    if i + 1 >= len(units): return 9
    e = T[units[i][1] - 1][1]; s = T[units[i + 1][0]][0]; return s - e
def bcost(i):  # ค่าตัดหลัง unit i
    if i + 1 >= len(units): return 0
    w = txt[units[i][0]:units[i][1]].strip(); nx = txt[units[i + 1][0]:units[i + 1][1]].strip()
    g = gap(i); c = 6.0
    if w.endswith(END): c = 0.0
    elif g >= 0.25: c = 0.3
    elif txt[units[i][1] - 1] == ' ': c = 1.5
    elif nx.startswith(CONJ): c = 2.5
    if re.match(r'[A-Za-z0-9]', nx) and re.search(r'[A-Za-z0-9]$', w) and txt[units[i][1]-1] != ' ': c += 20
    if nx.startswith('ๆ') or (w.endswith('ตัว') and nx.startswith('อย่าง')): c += 50
    if nx in END or nx.startswith(('ครับ', 'นะครับ', 'เนาะ')): c += 30  # ห้ามขึ้นบรรทัดด้วยคำลงท้าย
    return c
N = len(units); INF = 1e9
best = [INF] * (N + 1); prv = [0] * (N + 1); best[0] = 0
for j in range(1, N + 1):
    for i in range(max(0, j - 25), j):
        line = clean(txt[units[i][0]:units[j - 1][1]])
        L = len(line)
        if L > 30: continue
        pen = (8 - L) * 0.8 if L < 8 else 0
        pen += abs(L - 20) * 0.04
        c = best[i] + bcost(j - 1) + pen + 1.0
        if c < best[j]: best[j], prv[j] = c, i
out, j = [], N
while j > 0:
    i = prv[j]; out.append(txt[units[i][0]:units[j - 1][1]].strip()); j = i
out.reverse()
out = [o for o in out if clean(o)]
open(f'{D}/captions.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print(len(out), 'บรรทัด · ยาวสุด', max(len(clean(o)) for o in out))
