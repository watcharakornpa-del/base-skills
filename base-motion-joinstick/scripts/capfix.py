#!/usr/bin/env python3
"""แก้การแบ่งบรรทัดซับ: capfix.py <captions.txt> <spec>  · spec ทีละบรรทัด "a-b: บรรทัด1 / บรรทัด2 / ..." (เลขบรรทัดเดิม รวม a ถึง b)
ตรวจว่าข้อความรวม (ไม่นับช่องว่าง) เท่าเดิม ห้ามหาย/เกิน"""
import re, sys
P, S = sys.argv[1], sys.argv[2]
L = [l.rstrip('\n') for l in open(P, encoding='utf-8') if l.strip()]
norm = lambda s: re.sub(r'\s', '', s)
reps = []
for ln in open(S, encoding='utf-8'):
    if not ln.strip(): continue
    rng, new = ln.split(':', 1); a, b = (int(x) for x in rng.split('-')) if '-' in rng else (int(rng), int(rng))
    new = [x.strip() for x in new.split('/') if x.strip()]
    assert norm(''.join(L[a-1:b])) == norm(''.join(new)), f'{a}-{b} ข้อความไม่ตรง: {"".join(L[a-1:b])} ≠ {"".join(new)}'
    reps.append((a, b, new))
for a, b, new in sorted(reps, reverse=True): L[a-1:b] = new
def clean(t):
    t = re.sub(r'(\s*)(เนาะ|เนอะ|ป่ะ|อ่ะ)', lambda m: ' ' if m.group(1) else '', t); t = re.sub(r'นะ(?=ครับ|ว่า|$)', '', t); t = re.sub(r'\s*ๆ\s*', ' ๆ ', t)
    return re.sub(r'\s+', ' ', t).strip()
for x in L:
    if len(clean(x)) > 30: print('⚠️ เกิน 30:', x)
open(P, 'w', encoding='utf-8').write('\n'.join(L) + '\n'); print('แก้', len(reps), 'ช่วง →', len(L), 'บรรทัด')
