#!/usr/bin/env python3
import sys; sys.stdout.reconfigure(encoding="utf-8")
"""จับเวลาซับ: captions.txt (แบ่งวลีเอง · *คำเน้น*) → caps.json ตามเวลาตัวอักษรจาก ElevenLabs Scribe
และมีฟังก์ชัน at(วลี) ให้ gen.py หาเวลาเริ่มของวลีในคลิป"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
W = [w for w in json.load(open(f'{HERE}/scribe.json', encoding='utf-8'))['words'] if w['type'] == 'word']
norm = lambda s: re.sub(r'[\s*]', '', s).lower()   # ไม่สนตัวเล็ก/ใหญ่: Scribe ถอดรอบละแบบ (Mindset / mindset)
# ตัวอักษรทีละตัว → (start, end) ของ token ที่มันอยู่
CH = []
for w in W:
    for c in norm(w['text']):
        CH.append((c, w['start'], w['end']))
STREAM = ''.join(c for c, _, _ in CH)

def at(phrase, nth=1, after=0.0):
    """เวลาเริ่มของวลี (ครั้งที่ nth ที่อยู่หลังวินาที after)"""
    p = norm(phrase); i = -1; k = 0
    while True:
        i = STREAM.find(p, i + 1)
        if i < 0: raise ValueError(f'ไม่เจอวลี: {phrase}')
        if CH[i][1] >= after:
            k += 1
            if k == nth: return round(CH[i][1], 3)

def captions():
    lines = [l.strip() for l in open(f'{HERE}/captions.txt', encoding='utf-8') if l.strip()]
    out = []; pos = 0
    for l in lines:
        n = len(norm(l))
        seg = STREAM[pos:pos + n]
        assert seg == norm(l), f'ข้อความไม่ตรงที่ "{l}" → เจอ "{seg}"'
        out.append({'text': l, 'start': round(CH[pos][1], 3), 'end': round(CH[pos + n - 1][2], 3)})
        pos += n
    assert pos == len(STREAM), f'ซับไม่ครบ เหลือ "{STREAM[pos:pos+40]}"'
    return out

def captions_fuzzy():
    """เหมือน captions() แต่ทนคำที่ Scribe สะกดต่างรอบละแบบ (บรีฟ/brief · อ่ะ หาย/มา) — ข้อความที่แสดงใช้ของ captions.txt
    เทียบตัวอักษรด้วย difflib แล้วเอาเวลาจากตัวที่จับคู่ได้ใกล้สุด · รายงานบรรทัดที่จับคู่ได้น้อย (< 70%)"""
    import difflib
    lines = [l.strip() for l in open(f'{HERE}/captions.txt', encoding='utf-8') if l.strip()]
    A = ''.join(norm(l) for l in lines)
    sm = difflib.SequenceMatcher(None, A, STREAM, autojunk=False)
    amap = [None] * len(A)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n): amap[i + k] = j + k
    out = []; pos = 0; weak = []
    for l in lines:
        n = len(norm(l)); idx = [amap[p] for p in range(pos, pos + n) if amap[p] is not None]
        if len(idx) < 0.7 * n: weak.append(l)
        if not idx:
            raise AssertionError(f'จับคู่ไม่ได้เลย: {l}')
        out.append({'text': l, 'start': round(CH[idx[0]][1], 3), 'end': round(CH[idx[-1]][2], 3)})
        pos += n
    unmatched = len(STREAM) - sum(n for _, _, n in sm.get_matching_blocks())
    return out, weak, unmatched

if __name__ == '__main__':
    import sys
    if '--fuzzy' in sys.argv:
        c, weak, um = captions_fuzzy(); print('จับคู่อ่อน:', weak, '· ตัวอักษรในเสียงที่ไม่มีในซับ:', um)
    else:
        c = captions()
    json.dump(c, open(f'{HERE}/caps.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(len(c), 'บรรทัด · สั้นสุด', min(x['end'] - x['start'] for x in c), 'วิ')
