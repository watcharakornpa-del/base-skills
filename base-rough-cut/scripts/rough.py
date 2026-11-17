#!/usr/bin/env python3
"""base-rough-cut — ตัดช่วงเงียบ / คำเกิน / เทคเสียจากไฟล์ดิบ แล้วทำ rough cut + ซับให้ Premiere
ใช้ (จากโฟลเดอร์โปรเจกต์ หลัง work/transcribe.py):
  python work/rough.py table            → work/phrases.txt  ตารางวลี (id · เวลา · ช่วงเงียบก่อนหน้า · ข้อความ) ให้ Claude อ่านหาเทคเสีย
                                          + ติดธง F (คำเกินที่น่าตัด) ให้อัตโนมัติ
  (Claude เขียน work/cuts.json แล้วให้ผู้ใช้ดูรายการก่อน)
  python work/rough.py build            → renders/preview.mp4 (ดูเร็ว แนวตั้ง) · renders/roughcut.xml (import เข้า Premiere)
                                          · renders/roughcut.srt (ซับตามเวลาหลังตัด) · work/edit_report.txt
cuts.json: {"remove": [[id_จาก, id_ถึง, "เหตุผล"], ...], "keep_fillers": [id, ...], "start": id_แรก, "end": id_สุดท้าย}
ตั้งค่าหลักอยู่ใน CFG ด้านล่าง (ปรับผ่าน work/cuts.json ช่อง "cfg" ได้)"""
import json, os, re, shutil, subprocess, sys
from xml.sax.saxutils import escape
sys.stdout.reconfigure(encoding='utf-8')
CFG = dict(
    max_gap=0.40,      # เงียบเกินนี้ = ตัดทิ้ง (วินาที)
    pad_in=0.06,       # เผื่อก่อนเริ่มคำ (กันตัดพยัญชนะต้น)
    pad_out=0.14,      # เผื่อหลังจบคำ (กันตัดเสียงท้าย/ลมหายใจครึ่ง ๆ)
    min_keep=0.30,     # ชิ้นที่สั้นกว่านี้หลังตัด = รวมกับชิ้นข้าง ๆ
    snap=True,         # เลื่อนจุดตัดตามระดับเสียงจริงให้ตกช่องเงียบ (เวลาเริ่มคำจาก Scribe ช้ากว่าเสียงจริงได้ ~0.1 วิ)
    snap_max=0.30,     # เลื่อนได้ไกลสุด (วินาที)
    seq_fps=30, width=1080, height=1920,
    cap_chars=28,      # ซับ: ตัวอักษรต่อบรรทัด (ทีมใช้ ~26 · สูงสุด 36)
    cap_max_dur=2.2,   # ซับ: ขึ้นนานสุดต่อบรรทัด
)
# คำเกินที่ตัดได้ (ต้องยืนเดี่ยว ๆ เป็นวลีของตัวเอง) · ห้ามใส่คำลงท้ายที่มีความหมาย เช่น อ่ะ นะ ครับ
FILLERS = {'เอ่อ', 'เออ', 'อ่า', 'อา', 'อืม', 'อือ', 'เอิ่ม', 'อ้า', 'แบบ', 'แบบว่า', 'คือ', 'อ๋อ', 'เอ้อ', 'อะ'}
norm = lambda s: re.sub(r'\s+', '', s)
FF = shutil.which('ffmpeg') or 'ffmpeg'

def phrases():
    W = json.load(open('work/scribe.json', encoding='utf-8'))['words']
    out, cur = [], None
    for w in W:
        if w['type'] == 'spacing':
            if cur: out.append(cur); cur = None
            continue
        if w['type'] == 'audio_event':
            if cur: out.append(cur); cur = None
            out.append({'text': w['text'], 'start': w['start'], 'end': w['end'], 'event': True}); continue
        if cur is None: cur = {'text': '', 'start': w['start'], 'end': w['end'], 'chars': []}
        cur['text'] += w['text']; cur['end'] = w['end']; cur['chars'].append((w['text'], w['start'], w['end']))
    if cur: out.append(cur)
    for i, p in enumerate(out):
        p['id'] = i; p['gap'] = round(p['start'] - (out[i - 1]['end'] if i else 0), 2)
        nxt = out[i + 1]['start'] if i + 1 < len(out) else p['end'] + 1
        p['filler'] = (not p.get('event')) and norm(p['text']) in FILLERS and (p['gap'] > 0.12 or nxt - p['end'] > 0.12)
    return out

def table():
    P = phrases(); L = []
    for p in P:
        flag = 'F' if p['filler'] else ('E' if p.get('event') else ' ')
        L.append(f"{p['id']:4d} {flag} {p['start']:7.2f}–{p['end']:7.2f}  เงียบก่อน {p['gap']:4.2f}  {p['text']}")
    open('work/phrases.txt', 'w', encoding='utf-8').write('\n'.join(L))
    print(f'{len(P)} วลี · ธง F (คำเกิน) {sum(p["filler"] for p in P)} · ดู work/phrases.txt')

def preview_subs(caps, total):
    """ฝังซับลงพรีวิวด้วย HyperFrames (Chrome) — ห้ามใช้ ffmpeg subtitles/drawtext:
    ffmpeg เครื่องนี้วางวรรณยุกต์ไทยซ้อนผิด (นี้ → ้ จมทับ ี) ทุกฟอนต์ · Chrome วางถูก
    สไตล์ = ซับทีมใน Premiere (Anuphan Medium ขาว ไม่มีขอบ เงาบาง ๆ · กลางจอค่อนล่าง)"""
    d = 'work/subprev'; here = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(f'{d}/fonts', exist_ok=True)
    shutil.copy(os.path.join(here, 'fonts', 'Anuphan-Medium.ttf'), f'{d}/fonts/')
    json.dump({'id': 'subprev', 'name': 'subprev'}, open(f'{d}/meta.json', 'w', encoding='utf-8'))
    json.dump({'paths': {'assets': 'assets'}}, open(f'{d}/hyperframes.json', 'w', encoding='utf-8'))
    json.dump({'name': 'subprev', 'private': True, 'type': 'module'}, open(f'{d}/package.json', 'w', encoding='utf-8'))
    T = round(total, 3); divs = []; tl = []
    for i, c in enumerate(caps):
        divs.append(f'<div class="cap" id="c{i}">{escape(c["text"])}</div>')
        tl.append(f"tl.fromTo('#c{i}',{{opacity:0}},{{opacity:1,duration:0.01}},{round(c['start'], 3)});")
        tl.append(f"tl.set('#c{i}',{{opacity:0}},{round(c['end'], 3)});")
    html = f'''<!doctype html><html lang="th"><head><meta charset="UTF-8"><meta name="viewport" content="width=540, height=960">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
<style>@font-face {{ font-family: 'Anuphan'; font-weight: 500; src: url('fonts/Anuphan-Medium.ttf'); }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }} html, body {{ width: 540px; height: 960px; background: #000; overflow: hidden; }}
#root {{ position: relative; width: 540px; height: 960px; overflow: hidden; }} #root video {{ width: 540px; height: 960px; display: block; }}
.cap {{ position: absolute; left: 0; width: 540px; top: 628px; text-align: center; white-space: nowrap; opacity: 0;
  font: 500 32px/1.3 'Anuphan', sans-serif; color: #fff; text-shadow: 0 1px 4px rgba(0,0,0,.55); }}</style></head>
<body><div id="root" data-composition-id="main" data-start="0" data-duration="{T}" data-width="540" data-height="960">
<video id="v" class="clip" data-start="0" data-duration="{T}" data-track-index="1" data-media-start="0" src="assets/cut.mp4"></video>
{''.join(divs)}</div>
<script>window.__timelines = window.__timelines || {{}}; const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tl)}
window.__timelines["main"] = tl;</script></body></html>'''
    open(f'{d}/index.html', 'w', encoding='utf-8').write(html)
    out = os.path.abspath('renders/preview.mp4')
    r = subprocess.run(f'npx --yes hyperframes@0.8.147 render -q draft --workers 1 -o "{out}"', shell=True, cwd=d,
                       capture_output=True, text=True, encoding='utf-8', errors='replace')
    open('work/subprev_log.txt', 'w', encoding='utf-8').write(r.stdout + r.stderr)
    if r.returncode or not os.path.exists(out): sys.exit('❌ เรนเดอร์พรีวิวซับไม่สำเร็จ ดู work/subprev_log.txt')

def snap_cuts(R, src):
    """เลื่อนขอบทุกชิ้นให้ตกช่องเงียบจริง (วัดจากเสียงไฟล์ดิบ ทุก 10 ms)
    เจอจริง C5395 (10 พ.ย.): pad คงที่ 0.06/0.14 ไม่พอ — "เอช" ของคำว่า HR เริ่มก่อน Scribe 0.12 วิ หัวคำขาด ·
    หางคำ "กัน" ยังไม่หายตอนตัด · บางจุด pad_out ล้นเข้าพยางค์แรกของคำถัดไปในเทคที่ทิ้ง (ได้เสียงแว่บ)
    หัวชิ้น: ถ้ามีเสียงก่อนจุดตัด → ถอยไปจนเจอเงียบ ≥40 ms (ไม่เกิน snap_max)
    หางชิ้น: ถ้ามีเสียงหลังจุดตัด → ยืดไปจนเงียบ · ถ้ายืดแล้วไม่เจอ (คนพูดต่อในเทคที่ทิ้ง) → หดกลับไปช่องว่างระหว่างคำก่อนหน้า"""
    try:
        import numpy as np
    except ImportError:
        print('⚠️ ไม่มี numpy — ข้ามการเลื่อนจุดตัดตามเสียง (python -m pip install numpy)'); return []
    b = subprocess.run([FF, '-nostdin', '-v', 'error', '-i', src, '-vn', '-ac', '1', '-ar', '16000', '-f', 's16le', '-'], capture_output=True).stdout
    x = np.frombuffer(b, np.int16).astype(np.float32) / 32768; x = x[:len(x) // 160 * 160].reshape(-1, 160)
    env = 20 * np.log10(np.sqrt((x ** 2).mean(1)) + 1e-9)                 # dB ทุก 10 ms
    floor = float(np.percentile(env, 5)); thr = max(-57.0, floor + 12)  # "เงียบ" = ไม่เกินพื้นห้อง +12 dB
    def loud(a, b, th=None):
        i, j = max(0, int(a * 100)), max(int(a * 100) + 1, int(b * 100))
        return float(env[i:j].max()) >= (th or thr) if j <= len(env) else False
    dip = thr + 9                                                       # ช่องว่างระหว่างคำ (ไม่เงียบสนิท) — ใช้เมื่อพูดต่อเนื่อง
    mx = CFG['snap_max']; log = []
    for k, r in enumerate(R):
        s, e = r[0], r[1]; first, last = r[3][0], r[3][-1]
        if loud(s - .06, s):                                            # หัวคำโดนตัด → ถอยไปช่องเงียบ (ไม่เจอ → ช่องว่างระหว่างคำ)
            for th, lim in ((thr, mx), (dip, .15)):
                t = s
                while t > s - lim and loud(t - .04, t, th): t -= .01
                if t > s - lim: r[0] = max(0, t - .02); break
        if loud(e, e + .06):                                            # หางคำโดนตัด → ยืด หรือหดกลับ
            for th, lim in ((thr, mx), (dip, .15)):
                t = e
                while t < e + lim and loud(t, t + .04, th): t += .01
                if t < e + lim: r[1] = t + .02; break
                t = e
                while t > last['end'] - .02 and loud(t - .04, t, th): t -= .01
                if t > last['end'] - .02: r[1] = t; break
        # ห้ามทับชิ้นก่อนหน้าที่อยู่ติดกันในไฟล์ดิบ
        if k and R[k - 1][0] < s and r[0] < R[k - 1][1]: r[0] = R[k - 1][1]
        if abs(r[0] - s) > .005 or abs(r[1] - e) > .005:
            log.append(f"เลื่อนจุดตัด #{first['id']}–#{last['id']}  หัว {r[0] - s:+.2f}  หาง {r[1] - e:+.2f} วิ")
    return log

def tc(sec, fps):  # วินาที → เฟรม (จำนวนเต็ม)
    return int(round(sec * fps))

def build(keep_only=False):
    C = json.load(open('work/cuts.json', encoding='utf-8')); CFG.update(C.get('cfg', {}))
    P = phrases(); src = json.load(open('work/source.json', encoding='utf-8'))['src']
    # segments = ช่วงวลีที่เก็บ "ตามลำดับที่จะเล่น" (ย้ายเทคแก้ที่ถ่ายท้ายไฟล์มาแทรกกลางได้)
    # ภายในแต่ละช่วง: ตัดคำเกิน (ธง F) + ตัดช่องเงียบที่ยาวเกิน max_gap ให้อัตโนมัติ
    segs = C['segments']; keepf = set(C.get('keep_fillers', [])); also = set()
    for a, b, why in C.get('remove', []): also.update(range(a, b + 1))   # ตัดย่อยภายในช่วงที่เก็บ (คำซ้ำ/พูดติด)
    report = []; R = []
    for a, b in segs:
        prev = None
        for p in P[a:b + 1]:
            if p.get('event') or p['id'] in also: continue
            if p['filler'] and p['id'] not in keepf: report.append(f"ตัดคำเกิน  #{p['id']} {p['start']:.2f} “{p['text']}”"); continue
            s, e = max(0, p['start'] - CFG['pad_in']), p['end'] + CFG['pad_out']
            if prev is not None and p['id'] == prev + 1 and p['start'] - P[prev]['end'] <= CFG['max_gap']:
                R[-1][1] = max(R[-1][1], e); R[-1][3].append(p)          # ต่อเนื่อง ไม่ต้องตัด
            elif prev is not None and s < R[-1][1] and p['id'] > prev:
                R[-1][1] = e; R[-1][3].append(p)                         # ช่องเงียบสั้นกว่า pad รวมกัน
            else:
                R.append([s, e, p['id'], [p]])
            prev = p['id']
    if CFG['snap']: report += snap_cuts(R, src)
    R = [r for r in R if r[1] - r[0] >= CFG['min_keep']] or R
    for a, b, why in C.get('remove', []):
        report.append(f"ตัดในช่วง  #{a}–#{b} {P[a]['start']:.2f}–{P[b]['end']:.2f} · {why} · “{''.join(P[i]['text'] for i in range(a, b + 1))[:60]}”")
    for why in C.get('notes', []): report.append('หมายเหตุ   ' + why)
    raw_len = P[-1]['end']; cut_len = sum(e - s for s, e, *_ in R)
    report.insert(0, f"ไฟล์ดิบ {raw_len:.1f} วิ → หลังตัด {cut_len:.1f} วิ · {len(R)} ชิ้น · ใช้ {len(segs)} ช่วง {segs} · ตัดเงียบเกิน {CFG['max_gap']} วิ")
    open('work/edit_report.txt', 'w', encoding='utf-8').write('\n'.join(report)); print('\n'.join(report[:1]))
    json.dump([[round(s, 3), round(e, 3)] for s, e, *_ in R], open('work/keep.json', 'w', encoding='utf-8'))
    if keep_only: return R          # full() ขอแค่ช่วงที่เก็บ ไม่ต้องทำซับ/XML/พรีวิว

    # ---- ซับตามเวลาหลังตัด: แตกวลียาวด้วยตัดคำไทย (pythainlp) แล้วรวมให้ได้ ~cap_chars ตัวอักษร ----
    def chunks(p):
        if len(norm(p['text'])) <= CFG['cap_chars'] or not p.get('chars'): return [p]
        try:
            from pythainlp.tokenize import word_tokenize
            toks = [t for t in word_tokenize(p['text'], engine='newmm', keep_whitespace=False) if t.strip()]
        except ImportError:
            toks = list(p['text'])   # ไม่มี pythainlp → ตัดตามตัวอักษร (ลง: python -m pip install pythainlp)
        tk = []                      # ห้ามขึ้นบรรทัดใหม่ด้วย ๆ (เคยได้ "ยาก" | "ๆ ด้วย") → ติดกับคำก่อนหน้าเสมอ
        for t in toks:
            if tk and t.lstrip().startswith('ๆ'): tk[-1] += t
            else: tk.append(t)
        toks = tk
        CH = [(c, s_, e_) for t, s_, e_ in p['chars'] for c in t]    # เวลาแยกรายตัวอักษร
        out, cur, i = [], '', 0; cs = None
        n = len(norm(p['text'])); parts = max(2, -(-n // CFG['cap_chars'])); target = n / parts
        for t in toks:
            if cs is None: cs = CH[min(i, len(CH) - 1)][1]
            cur += t; i += len(t)
            if len(cur) >= target and i < len(CH) - 2:
                out.append({'text': cur, 'start': cs, 'end': CH[i - 1][2]}); cur, cs = '', None
        if cur: out.append({'text': cur, 'start': cs if cs is not None else CH[-1][1], 'end': CH[-1][2]})
        return out
    caps = []; t0 = 0.0
    for s, e, _, ps in R:
        for p in [c for q in ps for c in chunks(q)]:
            ns, ne = t0 + (p['start'] - s), t0 + (p['end'] - s)
            last_c = caps[-1] if caps else None
            if last_c and len(norm(last_c['text'] + p['text'])) <= CFG['cap_chars'] and ne - last_c['start'] <= CFG['cap_max_dur'] and ns - last_c['end'] < 0.3:
                last_c['text'] += ' ' + p['text']; last_c['end'] = ne
            else:
                caps.append({'text': p['text'], 'start': ns, 'end': ne})
        t0 += e - s
    merged = []                    # บรรทัดสั้นกุด (เช่น "Case" / "รวดเร็ว") รวมกับบรรทัดก่อนหน้า ถ้ารวมแล้วไม่เกิน 36 ตัว
    for c in caps:
        if merged and len(norm(c['text'])) <= 7 and len(norm(merged[-1]['text'] + c['text'])) <= 36 and c['start'] - merged[-1]['end'] < 0.35:
            merged[-1]['text'] += ' ' + c['text']; merged[-1]['end'] = c['end']
        else: merged.append(c)
    caps = merged
    for c in caps:                 # ไม้ยมก ๆ ต้องเว้นวรรคหน้า-หลังเสมอ (มากๆ → มาก ๆ) · ผู้ใช้สั่ง
        c['text'] = re.sub(r'\s*ๆ\s*', ' ๆ ', c['text']).strip()
    for i, c in enumerate(caps):   # ต่อเวลาให้ติดกันถ้าห่างนิดเดียว (ไม่กะพริบ)
        if i + 1 < len(caps) and caps[i + 1]['start'] - c['end'] < 0.25: c['end'] = caps[i + 1]['start']
    # ซ่อมเวลากลับหัว: บรรทัดถัดไปเริ่มก่อนบรรทัดนี้ (เวลาตัวอักษร Scribe ไม่เรียง) → ลูปบนตั้ง end < start
    # Premiere import SRT หยุดอ่านที่บรรทัดนั้น (เคยได้ซับแค่ 3/52 บรรทัด) และ MOV ซับค้างจอ · เจอจริง C5395 คลิป 4, 7
    for i, c in enumerate(caps):
        if c['end'] > c['start'] + 0.05: continue
        nxt = caps[i + 1]['start'] if i + 1 < len(caps) else c['start'] + 0.8
        if i:                         # แบ่งช่วง (ต้นบรรทัดก่อน … ต้นบรรทัดถัดไป) ตามจำนวนตัวอักษร
            p = caps[i - 1]; a = p['start']; z = max(nxt, a + 0.6)
            mid = round(a + (z - a) * len(p['text']) / (len(p['text']) + len(c['text'])), 3)
            p['end'] = mid; c['start'], c['end'] = mid, z
        else:
            c['end'] = max(nxt, c['start'] + 0.3)
    for i in range(1, len(caps)):     # กันซ้อน: บรรทัดก่อนต้องจบก่อนบรรทัดนี้เริ่ม
        if caps[i - 1]['end'] > caps[i]['start']: caps[i - 1]['end'] = caps[i]['start']
    bad = [c['text'] for c in caps if c['end'] <= c['start']]
    if bad: print('⚠️ ซับเวลาผิด (ต้องแก้มือ):', bad)
    f = lambda t: (lambda ms: f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}")(int(round(t * 1000)))   # ปัดเป็น ms ก่อน (เดิม 5.9996 → 00:00:05,000)
    open('renders/roughcut.srt', 'w', encoding='utf-8').write(
        '\n'.join(f"{i + 1}\n{f(c['start'])} --> {f(c['end'])}\n{c['text']}\n" for i, c in enumerate(caps)))

    # ---- พรีวิวเร็ว (แนวตั้ง crop กลาง · 540×960 · ฝังซับ) ----
    # กล้องถ่าย HLG/PQ (HDR BT.2020) → ต้องแปลงเป็น Rec.709 ก่อน ไม่งั้นเครื่องเล่นทั่วไปโชว์สีทึบเพี้ยน (Premiere แปลงให้เอง)
    col = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer', '-of', 'json', src],
                                    capture_output=True, text=True).stdout)['streams'][0].get('color_transfer', '')
    hdr = col in ('arib-std-b67', 'smpte2084')
    tone = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,'
            'zscale=t=bt709:m=bt709:r=tv,format=yuv420p,') if hdr else ''
    os.makedirs('work/subprev/assets', exist_ok=True)
    cut_video(src, [(s, e) for s, e, *_ in R], f'{tone}scale=-2:960,crop=540:960', 'work/subprev/assets/cut.mp4', ['-preset', 'veryfast', '-crf', '23'])
    if hdr: print('ℹ️ ไฟล์ดิบเป็น HDR (HLG/PQ) — พรีวิวแปลงเป็น Rec.709 แล้ว (ใน Premiere ภาพปกติเพราะ Pr แปลงให้เอง)')
    preview_subs(caps, cut_len)

    # ---- Premiere: FCP7 XML (ซีเควนซ์แนวตั้ง · คลิปดิบตัดเป็นชิ้น · ย่อให้เต็มความสูง) ----
    probe = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', src], capture_output=True, text=True).stdout)
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video'); a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    num, den = map(int, v['r_frame_rate'].split('/')); sfps = num / den; sw, sh = int(v['width']), int(v['height'])
    dur_f = tc(float(probe['format']['duration']), round(sfps)); FPS = CFG['seq_fps']
    scale = round(CFG['height'] / sh * 100, 2)
    url = 'file://localhost/' + src.replace('\\', '/').replace(' ', '%20')
    name = os.path.basename(src); seqname = 'Rough Cut - ' + os.path.splitext(name)[0]
    def rate(fps): return f'<rate><timebase>{int(round(fps))}</timebase><ntsc>{"TRUE" if abs(fps - round(fps)) > 0.01 else "FALSE"}</ntsc></rate>'
    filedef = (f'<file id="file-1"><name>{escape(name)}</name><pathurl>{escape(url)}</pathurl>{rate(sfps)}<duration>{dur_f}</duration>'
               f'<media><video><samplecharacteristics><width>{sw}</width><height>{sh}</height></samplecharacteristics></video>'
               f'<audio><samplecharacteristics><samplerate>{a.get("sample_rate", 48000)}</samplerate><depth>16</depth></samplecharacteristics><channelcount>{a.get("channels", 2)}</channelcount></audio></media></file>')
    vitems, aitems = [[]], [[], []]; pos = 0
    for k, (s, e, *_ ) in enumerate(R, 1):
        # Premiere อ่าน <in>/<out> เป็นเฟรมของ timebase (30) ไม่ใช่ 29.97 ตาม ntsc · ใช้ 29.97 แล้วจุดตัดเลื่อนเร็วขึ้น 0.1% ของเวลาไฟล์ดิบ
        # (C5395 นาทีที่ 12 เพี้ยน 0.7 วิ → หน้าในวงกลม B-roll/ซับไม่ตรงเสียง) · out = in + ความยาวบนไทม์ไลน์ ให้ยาวเท่ากันพอดี
        n = tc(e - s, FPS); i_in = tc(s, round(sfps)); i_out = i_in + n
        fdef = filedef if k == 1 else '<file id="file-1"/>'
        motion = (f'<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype><mediatype>video</mediatype>'
                  f'<parameter><parameterid>scale</parameterid><name>Scale</name><value>{scale}</value></parameter></effect></filter>')
        link = lambda kind, idx, tr: f'<link><linkclipref>{kind}-{k}</linkclipref><mediatype>{"video" if kind == "v" else "audio"}</mediatype><trackindex>{tr}</trackindex><clipindex>{k}</clipindex></link>'
        links = link('v', k, 1) + link('a1', k, 1) + link('a2', k, 2)
        vitems[0].append(f'<clipitem id="v-{k}"><name>{escape(name)}</name>{rate(sfps)}<start>{pos}</start><end>{pos + n}</end><in>{i_in}</in><out>{i_out}</out>{fdef}{motion}{links}</clipitem>')
        for ch in (1, 2):
            aitems[ch - 1].append(f'<clipitem id="a{ch}-{k}"><name>{escape(name)}</name>{rate(sfps)}<start>{pos}</start><end>{pos + n}</end><in>{i_in}</in><out>{i_out}</out><file id="file-1"/>'
                                  f'<sourcetrack><mediatype>audio</mediatype><trackindex>{ch}</trackindex></sourcetrack>{links}</clipitem>')
        pos += n
    xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4"><sequence id="seq-1"><name>{escape(seqname)}</name><duration>{pos}</duration>{rate(FPS)}'
           f'<media><video><format><samplecharacteristics>{rate(FPS)}<width>{CFG["width"]}</width><height>{CFG["height"]}</height><pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>'
           f'<track>{"".join(vitems[0])}</track></video>'
           f'<audio><numOutputChannels>2</numOutputChannels><track>{"".join(aitems[0])}</track><track>{"".join(aitems[1])}</track></audio></media></sequence></xmeml>')
    open('renders/roughcut.xml', 'w', encoding='utf-8').write(xml)
    print(f'✅ renders/preview.mp4 · renders/roughcut.xml ({len(R)} ชิ้น · {pos / FPS:.1f} วิ · scale {scale}%) · renders/roughcut.srt ({len(caps)} บรรทัด) · work/edit_report.txt')

def full():
    """ไฟล์ตัดแล้วความละเอียดเต็ม 1080×1920 (ไม่มีซับ ไม่มีปก) → renders/cut_1080.mp4
    ใช้เป็นต้นทางของ base-motion-collage เมื่อยังไม่ได้ตัดใน Premiere (Text Hook จะได้ไม่ชนปกที่เบิร์นมา)"""
    # คำนวณช่วงที่เก็บใหม่จาก cuts.json ปัจจุบันทุกครั้ง — ห้ามอ่าน keep.json ค้างจาก build ครั้งก่อน
    # (ตัดหลายคลิปจากไฟล์ดิบเดียว แล้วได้ไฟล์ 1080 เป็นคลิปล่าสุดทุกไฟล์ · เจอจริง C5395)
    src = json.load(open('work/source.json', encoding='utf-8'))['src']; R = [[s, e] for s, e, *_ in build(keep_only=True)]
    col = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=color_transfer', '-of', 'json', src],
                                    capture_output=True, text=True).stdout)['streams'][0].get('color_transfer', '')
    tone = ('zscale=t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,'
            if col in ('arib-std-b67', 'smpte2084') else '')
    cut_video(src, R, f"{tone}scale=-2:1920,crop=1080:1920,fps={CFG['seq_fps']}", 'renders/cut_1080.mp4', ['-preset', 'medium', '-crf', '17', '-b:a', '256k'])
    print('✅ renders/cut_1080.mp4')

def cut_video(src, R, vf, out, enc):
    """ต่อช่วง R ตาม "ลำดับในลิสต์" (trim+concat) — ห้ามใช้ select/between: มันเก็บเฟรมตามลำดับไฟล์ดิบ
    เทคแก้ที่ย้ายมาแทรกกลางจะไปโผล่ท้ายคลิป และซับเลื่อนทั้งคลิป (เจอจริงรอบแรก)"""
    fl = []
    for i, (s, e) in enumerate(R):
        fl.append(f'[0:v]trim=start={s:.3f}:end={e:.3f},setpts=PTS-STARTPTS[v{i}]')
        fl.append(f'[0:a]atrim=start={s:.3f}:end={e:.3f},asetpts=PTS-STARTPTS[a{i}]')
    fl.append(''.join(f'[v{i}][a{i}]' for i in range(len(R))) + f'concat=n={len(R)}:v=1:a=1[cv][ca]')
    fl.append(f'[cv]{vf}[ov]')
    subprocess.run([FF, '-nostdin', '-v', 'error', '-i', src, '-filter_complex', ';'.join(fl), '-map', '[ov]', '-map', '[ca]',
                    '-c:v', 'libx264', *enc, '-pix_fmt', 'yuv420p', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709',
                    '-c:a', 'aac', '-y', out], check=True)

{'table': table, 'build': build, 'full': full}[sys.argv[1]]()
