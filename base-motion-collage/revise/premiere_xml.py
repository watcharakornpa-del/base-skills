#!/usr/bin/env python3
"""ซีเควนซ์ Draft2 สำหรับ Premiere (FCP7 XML แบบเดียวกับ clipN-roughcut.xml) → File › Import ได้ซีเควนซ์ทันที
จุดตัดชุดเดียวกับ compose.py (MP4) · ก๊อปกราฟิก + ซับ + LUT ลง SSD ข้างโปรเจกต์ (ทีมเปิดจากเครื่องไหนก็เจอไฟล์)
แทร็ก: V1 กล้อง 4K (Scale 50 บน Mac) / B-roll collage · V2 แผ่นแปะป้าย · V3 ปก · V4 Super
       A1–A2 เสียงพูด (ช่วง B-roll = เสียง collage ที่มี SFX เดิม) · A3 ปากกา + typewriter
ไม่อยู่ใน XML (ต้องทำใน Premiere): ซับ = Import .srt แล้วลากลงซีเควนซ์ (CC) · เกรด = Adjustment Layer + Lumetri › Creative › Look = .cube
ใช้: python3 -I work/premiere_xml.py → <โฟลเดอร์โปรเจกต์ทีม>/C5395-draft2/<ชื่อคลิป>/"""
import json, os, shutil, subprocess
from urllib.parse import quote
from xml.sax.saxutils import escape
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
C = json.load(open(f'{HERE}/clip.json', encoding='utf-8')); E = json.load(open(f'{HERE}/edl.json', encoding='utf-8'))
M = json.load(open(f'{HERE}/xmlmap.json'))
TEAM = '/Volumes/Extreme SSD/Copied_Tiktok 180526'
TITLE = os.path.basename(C['out'])[:-4]                      # "<ชื่อคลิป> Draft2"
OUT = os.path.join(os.path.dirname(os.path.dirname(C['xml'])), 'C5395-draft2', TITLE); os.makedirs(OUT, exist_ok=True)
FPS = 30
CAM_SCALE = 50   # Premiere บน Mac หมุนไฟล์แนวตั้งให้เอง → 50 = เต็มเฟรม (88.89 ของ Draft1 มาจากเครื่อง Windows จะซูมเกิน)
fr = lambda t: int(round(t * FPS))

def dur_frames(path):
    d = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True).stdout
    return fr(float(d))

# ===== ไฟล์ทั้งหมด (ของที่อยู่ใน Mac ก๊อปลง SSD ก่อน) =====
G = {'cover': f'{P}/renders/gfx/cover.mov'}
for i in range(1, len(E['supers']) + 1): G[f'super{i}'] = f'{P}/renders/gfx/super{i}.mov'
for i in range(len(E.get('patches', []))): G[f'patch{i}'] = f'{P}/renders/gfx/patch{i}.mov'
for k, v in G.items(): shutil.copy(v, f'{OUT}/{k}.mov'); G[k] = f'{OUT}/{k}.mov'
srt = f"{P}/renders/{C['name']}.srt"; shutil.copy(srt, f'{OUT}/{TITLE}.srt')
shutil.copy(f'{P}/assets/BASE-dark-moody.cube', f'{OUT}/BASE-dark-moody.cube')

files = {}                                                  # id → (path, ntsc, frames, w, h, has_video, has_audio)
def file_def(fid, path, ntsc, frames, w=1080, h=1920, video=True, audio=True):
    files[fid] = (path, ntsc, frames, w, h, video, audio)
file_def('f-src', C['src'], True, 24480, 3840, 2160)
file_def('f-col', C['collage'], False, dur_frames(C['collage']))
for k, v in G.items(): file_def(f'f-{k}', v, False, dur_frames(v), audio=False)
file_def('f-pen', f'{TEAM}/pen writing.wav', False, dur_frames(f'{TEAM}/pen writing.wav'), video=False)
file_def('f-tw', f'{TEAM}/typewriter.wav', False, dur_frames(f'{TEAM}/typewriter.wav'), video=False)
seen = set()
def fileref(fid):
    if fid in seen: return f'<file id="{fid}"/>'
    seen.add(fid); path, ntsc, frames, w, h, v, a = files[fid]
    url = 'file://localhost' + quote(path)
    med = (f'<video><samplecharacteristics><width>{w}</width><height>{h}</height></samplecharacteristics></video>' if v else '') + \
          ('<audio><samplecharacteristics><samplerate>48000</samplerate><depth>16</depth></samplecharacteristics><channelcount>2</channelcount></audio>' if a else '')
    return (f'<file id="{fid}"><name>{escape(os.path.basename(path))}</name><pathurl>{url}</pathurl>'
            f'<rate><timebase>30</timebase><ntsc>{"TRUE" if ntsc else "FALSE"}</ntsc></rate><duration>{frames}</duration><media>{med}</media></file>')

# ===== ชิ้นบน V1/A1/A2 (เหมือน compose.py) =====
def src_frames(a, b):
    out = []; fa, fb = round(a * 30), round(b * 30)
    for m in M:
        lo, hi = max(fa, m['start']), min(fb, m['end'])
        if lo >= hi: continue
        k = (m['src_out'] - m['src_in']) / (m['end'] - m['start'])
        out.append((round(m['src_in'] + (lo - m['start']) * k), hi - lo))
    return out
def split_broll(a, b):
    cut = sorted({a, b} | {x for r in E['broll'] for x in r if a < x < b})
    return [(x, y, 'broll' if any(r[0] <= (x + y) / 2 < r[1] for r in E['broll']) else 'cam') for x, y in zip(cut, cut[1:]) if y - x > 0.01]
pieces = []; t = 0                                          # (fid, start, end, in, out, scale)
for s in E['segs']:
    for a, b, kind in split_broll(s['a'], s['b']):
        if kind == 'cam':
            for sin, n in src_frames(a, b): pieces.append(('f-src', t, t + n, sin, sin + n, CAM_SCALE)); t += n
        else:
            n = round((b - a) * 30); pieces.append(('f-col', t, t + n, fr(a), fr(a) + n, 100)); t += n
TOTAL = t

def clip(cid, fid, st, en, i, o, name, scale=None, links='', srctrack=None):
    ntsc = 'TRUE' if files[fid][1] else 'FALSE'
    f = (f'<filter><effect><name>Basic Motion</name><effectid>basic</effectid><effectcategory>motion</effectcategory><effecttype>motion</effecttype>'
         f'<mediatype>video</mediatype><parameter><parameterid>scale</parameterid><name>Scale</name><value>{scale}</value></parameter></effect></filter>') if scale else ''
    st_ = f'<sourcetrack><mediatype>audio</mediatype><trackindex>{srctrack}</trackindex></sourcetrack>' if srctrack else ''
    return (f'<clipitem id="{cid}"><name>{escape(name)}</name><rate><timebase>30</timebase><ntsc>{ntsc}</ntsc></rate>'
            f'<start>{st}</start><end>{en}</end><in>{i}</in><out>{o}</out>{fileref(fid)}{st_}{f}{links}</clipitem>')
def link3(n):
    return ''.join(f'<link><linkclipref>{r}-{n}</linkclipref><mediatype>{mt}</mediatype><trackindex>{ti}</trackindex><clipindex>{n}</clipindex></link>'
                   for r, mt, ti in (('v', 'video', 1), ('a1', 'audio', 1), ('a2', 'audio', 2)))
name = lambda fid: os.path.basename(files[fid][0])
V1 = ''.join(clip(f'v-{n}', fid, st, en, i, o, name(fid), sc, link3(n)) for n, (fid, st, en, i, o, sc) in enumerate(pieces, 1))
A1 = ''.join(clip(f'a1-{n}', fid, st, en, i, o, name(fid), None, link3(n), 1) for n, (fid, st, en, i, o, sc) in enumerate(pieces, 1))
A2 = ''.join(clip(f'a2-{n}', fid, st, en, i, o, name(fid), None, link3(n), 2) for n, (fid, st, en, i, o, sc) in enumerate(pieces, 1))

def gfx(cid, key, at):
    fid = f'f-{key}'; n = files[fid][2]; st = fr(at)
    return clip(cid, fid, st, min(st + n, TOTAL), 0, min(n, TOTAL - st), name(fid))
def new_t(x):
    s = next(s for s in E['segs'] if s['a'] <= x <= s['b']); return s['at'] + x - s['a']
V2 = ''.join(gfx(f'p-{i}', f'patch{i}', new_t(p['at'])) for i, p in enumerate(E.get('patches', [])))
V3 = gfx('cv-1', 'cover', E['cover']['at'])
V4 = ''.join(gfx(f'sp-{i}', f'super{i}', s['at']) for i, s in enumerate(E['supers'], 1))
sfx = [('f-pen', 0.3, 1.6)] + [('f-tw', s['at'] + 0.1, 0.75) for s in E['supers']]
A3 = ''.join(clip(f'sfx-{n}', fid, fr(t0), fr(t0) + fr(d), 0, fr(d), name(fid), None, '', 1) for n, (fid, t0, d) in enumerate(sfx, 1))

trk = lambda body: f'<track>{body}</track>'
seq = (f'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4"><sequence id="seq-1"><name>{escape("C5395 " + TITLE)}</name>'
       f'<duration>{TOTAL}</duration><rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate><media><video><format><samplecharacteristics>'
       f'<rate><timebase>30</timebase><ntsc>FALSE</ntsc></rate><width>1080</width><height>1920</height><pixelaspectratio>square</pixelaspectratio>'
       f'</samplecharacteristics></format>{trk(V1)}{trk(V2)}{trk(V3)}{trk(V4)}</video><audio>{trk(A1)}{trk(A2)}{trk(A3)}</audio></media></sequence></xmeml>')
x = f'{OUT}/{TITLE}.xml'; open(x, 'w', encoding='utf-8').write(seq)
print(f'✅ {x}\n   {TOTAL} เฟรม = {TOTAL / 30:.2f} วิ (MP4 {E["total"]:.2f}) · V1 {len(pieces)} ชิ้น · Super {len(E["supers"])} · แผ่นแปะ {len(E.get("patches", []))}')
