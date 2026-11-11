"""เทียบเวลาซับของทีม (team.srt) เข้ากับคลิปที่ตัดแล้ว

team.srt จับเวลาจากคลิปดิบ 79 วิ แต่คลิปที่ตัดแล้วยาว 68.5 วิ — เวลาใช้ไม่ได้ตรง ๆ
เลยเอา "ข้อความ" ของทีม (สะกดไทยแบบทีม) ไปหาตำแหน่งในเสียงที่ถอดจากคลิปตัดแล้ว
แบบคร่าว ๆ (difflib) เพราะสะกดไม่ตรงกัน เช่น ทีมเขียน ฟีดแบ็ก แต่ถอดเสียงได้ Feedback"""
import difflib, json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
import sys; sys.path.insert(0, HERE)
from align import STREAM, CH, norm
# คำที่ทีมสะกดไทย แต่ถอดเสียงได้อังกฤษ — แปลงก่อนเทียบเท่านั้น ตัวที่โชว์ยังเป็นแบบทีม
SAME = {'ฟีดแบ็ก': 'Feedback', 'แจ็กเกต': 'Jacket', 'คลาสสิก': 'Classic', 'Self-worth': 'SelfWorth', 'สกิล': 'Skill'}
def key(t):
    for a, b in SAME.items(): t = t.replace(a, b)
    return norm(t).replace('-', '')
def load():
    s = open(f'{HERE}/team.srt', encoding='utf-8-sig').read().replace('\r', '')
    return [' '.join(b.split('\n')[2:]).strip() for b in s.strip().split('\n\n') if '-->' in b]
def align():
    out, pos = [], 0
    for line in load():
        k = key(line); n = len(k); best = (0, None)
        for i in range(pos, min(len(STREAM) - 1, pos + 160)):
            for L in (n - 3, n, n + 3):
                seg = STREAM[i:i + max(1, L)]
                r = difflib.SequenceMatcher(None, k, seg).ratio()
                if r > best[0]: best = (r, (i, max(1, L)))
        r, hit = best
        if r < 0.55 or hit is None:
            out.append({'text': line, 'skip': round(r, 2)}); continue
        i, L = hit; j = min(len(CH) - 1, i + L - 1)
        out.append({'text': line, 'start': round(CH[i][1], 3), 'end': round(CH[j][2], 3), 'ratio': round(r, 2)})
        pos = i + L
    return out
if __name__ == '__main__':
    res = align()
    json.dump(res, open(f'{HERE}/subs.json', 'w'), ensure_ascii=False, indent=1)
    ok = [x for x in res if 'start' in x]
    print(f'{len(ok)}/{len(res)} บรรทัดเจอตำแหน่ง')
    for x in res:
        print(f"{x.get('start', '  —  '):>7}  {x.get('ratio', x.get('skip'))}  {x['text']}")
