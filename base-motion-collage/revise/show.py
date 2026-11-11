#!/usr/bin/env python3
"""พิมพ์ transcript พร้อมเวลา (บรรทัดละ ~34 ตัว) + ซับทีมพร้อมเวลา — ไว้เขียน plan.py
ใช้: python3 -I work/show.py"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(f'{HERE}/clip.json', encoding='utf-8'))
W = [w for w in json.load(open(f'{HERE}/scribe.json', encoding='utf-8'))['words'] if w['type'] != 'spacing']
line = []; st = None
print('== เสียงจริง (Scribe)')
for w in W:
    if st is None: st = w['start']
    line.append(w['text'] if w['type'] == 'word' else '[' + w['text'] + ']')
    if len(''.join(line)) > 34: print(f"{st:6.2f} {''.join(line)}"); line = []; st = None
if line: print(f"{st:6.2f} {''.join(line)}")
print('== ซับทีม Draft1 · B-roll', json.load(open(f'{HERE}/broll.json')))
for blk in open(C['srt'], encoding='utf-8-sig').read().replace('\r', '').strip().split('\n\n'):
    l = blk.split('\n'); print(l[1].replace(',', '.').replace('00:0', '')[:24], '|', ' '.join(l[2:]))
