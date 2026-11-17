#!/usr/bin/env python3
"""ประกอบ Draft2 → renders/<ชื่อ>.mp4 แล้วก๊อปไปที่ไฟล์ส่ง (clip.json: out)
ภาพ: ช่วงที่ Draft1 เป็นคนพูด = ต้นฉบับ 4K (ตามจุดตัดใน rough cut XML) + LUT โทนเข้ม · ช่วง B-roll = ภาพจาก collage (ไม่เกรด)
ทับ: แผ่นแปะป้าย (ถ้ามี) → ปก → Super → ซับ (IBM Plex Sans Thai ขนาดคงที่ + เงาฟุ้ง ไม่มีขอบ)
เสียง: ต้นฉบับกล้องทั้งคลิป (ช่วง B-roll ด้วย — ห้ามใช้เสียงในไฟล์ collage) + SFX ของ B-roll (sfx.json ของโปรเจกต์ collage)
      + ปากกา/typewriter ทีม · compressor ชั้นเดียวทั้งคลิป · loudnorm 2 รอบ -15 LUFS พีค ≤ -2 dBTP
ใช้: python3 -I work/compose.py"""
import json, os, shutil, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); P = os.path.dirname(HERE)
C = json.load(open(f'{HERE}/clip.json', encoding='utf-8'))
E = json.load(open(f'{HERE}/edl.json', encoding='utf-8'))
M = json.load(open(f'{HERE}/xmlmap.json'))
TEAM = '/Volumes/Extreme SSD/Copied_Tiktok 180526'
LUT = f'{P}/assets/BASE-dark-moody.cube'
FF = shutil.which('ffmpeg'); SRC_FPS = 30000 / 1001
run = lambda a: subprocess.run([FF, '-nostdin', '-v', 'error', '-y', *a], check=True)

def src_pieces(a, b):
    """ช่วง Draft1 [a,b) → ชิ้นในไฟล์ต้นฉบับ [(วินาทีต้นฉบับ, ยาว)]"""
    out = []; fa, fb = round(a * 30), round(b * 30)
    for m in M:
        lo, hi = max(fa, m['start']), min(fb, m['end'])
        if lo >= hi: continue
        k = (m['src_out'] - m['src_in']) / (m['end'] - m['start'])
        out.append(((round(m['src_in'] + (lo - m['start']) * k) - 0.5) / SRC_FPS, (hi - lo) / 30))   # เฟรมเดียวกับ premiere_xml.py (ครึ่งเฟรมก่อน = ได้เฟรมนั้นพอดี)
    return out

def split_broll(a, b):
    """แบ่งช่วง Draft1 เป็น [(a,b,'cam'|'broll')] ตามช่วง B-roll"""
    cut = sorted({a, b} | {x for r in E['broll'] for x in r if a < x < b})
    return [(x, y, 'broll' if any(r[0] <= (x + y) / 2 < r[1] for r in E['broll']) else 'cam') for x, y in zip(cut, cut[1:]) if y - x > 0.01]

os.makedirs(f'{HERE}/pieces', exist_ok=True)
lst = []; n = 0
enc = ['-c:v', 'libx264', '-crf', '12', '-preset', 'fast', '-c:a', 'pcm_s16le', '-ar', '48000', '-ac', '2']
for s in E['segs']:
    for a, b, kind in split_broll(s['a'], s['b']):
        if kind == 'cam':
            for ss, d in src_pieces(a, b):
                n += 1; o = f'{HERE}/pieces/p{n:03}.mkv'
                N = round(d * 30)                    # จำนวนเฟรมต้องพอดี ไม่งั้นภาพหาย 1 เฟรมบางชิ้น → ภาพนำเสียงสะสม (เคยคลาด 5 เฟรม)
                run(['-ss', f'{ss:.4f}', '-i', C['src'], '-t', f'{d + 0.2:.4f}', '-map', '0:v:0', '-map', '0:a:0',
                     '-vf', f'scale=1080:1920:flags=lanczos,fps=30,trim=end_frame={N},setpts=PTS-STARTPTS,lut3d={LUT},format=yuv420p',
                     '-af', f'atrim=end={N / 30:.6f},asetpts=PTS-STARTPTS', *enc, o]); lst.append(o)
        else:
            # ภาพจาก collage · เสียงจากกล้องช่วงเดียวกัน (แผนที่เดียวกับช่วงคนพูด -> ขอบ B-roll เสียงต่อเนื่อง ไม่ซ้ำ/ไม่แหว่ง)
            n += 1; o = f'{HERE}/pieces/p{n:03}.mkv'
            N = round((b - a) * 30); sp = src_pieces(a, b)
            ins_ = ['-ss', f'{(round(a * 30) - 0.5) / 30:.4f}', '-t', f'{b - a + 0.2:.4f}', '-i', C['collage']]
            for ss, d in sp: ins_ += ['-ss', f'{ss:.4f}', '-t', f'{d + 0.1:.4f}', '-i', C['src']]
            fl = [f'[0:v]fps=30,trim=end_frame={N},setpts=PTS-STARTPTS,format=yuv420p[v]']
            fl += [f'[{k}:a:0]atrim=end={d:.6f},asetpts=PTS-STARTPTS[a{k}]' for k, (ss, d) in enumerate(sp, 1)]
            fl.append(''.join(f'[a{k}]' for k in range(1, len(sp) + 1)) + f'concat=n={len(sp)}:v=0:a=1,apad,atrim=end={N / 30:.6f}[a]')
            run([*ins_, '-filter_complex', ';'.join(fl), '-map', '[v]', '-map', '[a]', *enc, o]); lst.append(o)
open(f'{HERE}/pieces/list.txt', 'w').write(''.join(f"file '{x}'\n" for x in lst))
run(['-f', 'concat', '-safe', '0', '-i', f'{HERE}/pieces/list.txt', '-c', 'copy', f'{HERE}/base.mkv'])

# ซับ .ass: ชั้นล่าง = เงาฟุ้ง (Drop Shadow) · ชั้นบน = ตัวขาวไม่มีขอบ (ผู้ใช้สั่ง 9 พ.ย. 2026: ขอบทำให้ตัวจม)
def at(x): return f'{int(x // 3600)}:{int(x // 60 % 60):02}:{x % 60:05.2f}'
ass = ['[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 1080', 'PlayResY: 1920', 'WrapStyle: 2', '', '[V4+ Styles]',
       'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
       'Style: Sub,IBM Plex Sans Thai SemiBold,100,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,2,40,40,540,1',
       'Style: Shd,IBM Plex Sans Thai SemiBold,100,&H50000000,&H50000000,&H50000000,&H00000000,0,0,0,0,100,100,0,0,1,3,0,2,40,40,534,1',
       '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
for c in E['caps']:
    ass += [f"Dialogue: 0,{at(c['at'])},{at(c['end'])},Shd,,0,0,0,,{{\\blur14}}{c['text']}",
            f"Dialogue: 1,{at(c['at'])},{at(c['end'])},Sub,,0,0,0,,{c['text']}"]
open(f'{HERE}/subs.ass', 'w', encoding='utf-8').write('\n'.join(ass) + '\n')

def new_t(x):
    for s in E['segs']:
        if s['a'] <= x <= s['b']: return round(s['at'] + x - s['a'], 3)
    raise SystemExit(f'❌ เวลา {x} ไม่อยู่ในชิ้นที่เก็บ')
seg_end = lambda x: next(round(s['at'] + s['b'] - s['a'], 3) for s in E['segs'] if s['a'] <= x <= s['b'])

ins = ['-i', f'{HERE}/base.mkv']; fv = []; prev = '0:v'; k = 0
def add_overlay(path, t):
    global prev, k, ins
    ins += ['-itsoffset', f'{t:.3f}', '-i', path]; k += 1
    fv.append(f'[{prev}][{k}:v]overlay=eof_action=pass:format=auto[v{k}]'); prev = f'v{k}'
for i, p in enumerate(E['patches']):                     # แผ่นแปะป้าย (ค้างถึงจบชิ้น)
    t0 = new_t(p['at']); t1 = seg_end(p['at'])
    subprocess.run(['python3', '-I', f'{HERE}/gen_patch.py', str(i), f'{t1 - t0:.3f}'], check=True)
    subprocess.run(f'npx --yes hyperframes@0.8.147 render --format mov -f 30 --workers 1 -o "{P}/renders/gfx/patch{i}.mov" > "{HERE}/render_patch{i}.log" 2>&1',
                   shell=True, cwd=f'{P}/gfx_patch/p{i}', check=True)
    add_overlay(f'{P}/renders/gfx/patch{i}.mov', t0)
add_overlay(f'{P}/renders/gfx/cover.mov', E['cover']['at'])
for i, s in enumerate(E['supers'], 1): add_overlay(f'{P}/renders/gfx/super{i}.mov', s['at'])
fonts = os.path.expanduser('~/Library/Fonts')
# ต้องใช้ ass + shaping=complex ไม่งั้นวรรณยุกต์จมในสระบน (เช่น "ที่" กลายเป็น "ที")
fv.append(f"[{prev}]ass='{HERE}/subs.ass':fontsdir='{fonts}':shaping=complex,format=yuv420p[vout]")
ins += ['-i', f'{TEAM}/pen writing.wav', '-i', f'{TEAM}/typewriter.wav']; pen, tw = k + 1, k + 2
fa = [f"[{pen}:a]atrim=0:1.6,afade=t=out:st=1.2:d=0.4,volume=0.45,adelay=300|300[pen]"]; mix = ['[0:a]', '[pen]']
# SFX ของ B-roll: ระดับเทียบเสียงพูดเท่าใน collage (collage พูด -14 LUFS · ที่นี่เสียงกล้องดิบ) -> คูณส่วนต่างความดัง
SFXF = {k_: os.path.expanduser(f'~/.claude/skills/base-motion-collage/assets/sfx/{v_}') for k_, v_ in dict(swoosh='swoosh.mp3', click='click.mp3', thump='thump.wav', pen='pen.wav').items()}
nk = tw
if C.get('sfx'):
    import re as _re
    _r = subprocess.run([FF, '-nostdin', '-hide_banner', '-i', f'{HERE}/base.mkv', '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    rel = 10 ** ((float(_re.findall(r'I:\s+(-?[\d.]+) LUFS', _r)[-1]) + 14) / 20)
    sfx_ins = []
    for t_, kind, vol in json.load(open(C['sfx'], encoding='utf-8')):
        if not any(r[0] - .05 <= t_ < r[1] for r in E['broll']): continue
        try: tn = new_t(t_)
        except SystemExit: continue                              # ช่วงนี้ถูกตัดออกใน Draft2
        sfx_ins += ['-i', SFXF[kind]]; nk += 1; ms = round(tn * 1000)
        fa.append(f"[{nk}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume={vol * rel:.4f},adelay={ms}|{ms}[sx{nk}]"); mix.append(f'[sx{nk}]')
    ins += sfx_ins
else: print('⚠️ ไม่มี sfx.json (clip.json: sfx) — B-roll ไม่มี SFX')
for i, s in enumerate(E['supers'], 1):
    ms = round((s['at'] + 0.1) * 1000)
    fa.append(f"[{tw}:a]atrim=0:0.75,afade=t=out:st=0.55:d=0.2,volume=0.5,adelay={ms}|{ms}[tw{i}]"); mix.append(f'[tw{i}]')
# ดังใกล้ Draft1 (-15 LUFS) · พีคไม่เกิน -2 dBTP — loudnorm 2 รอบ (วัดก่อน แล้วปรับแบบ linear)
LN = 'loudnorm=I=-15:TP=-2.0:LRA=20'
mixf = f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=2"
r = subprocess.run([FF, '-nostdin', '-hide_banner', *ins, '-filter_complex', ';'.join(fa + [f'{mixf},{LN}:print_format=json[m]']),
                    '-map', '[m]', '-f', 'null', '-'], capture_output=True, text=True, check=True).stderr
m = json.loads(r[r.rindex('{'):r.rindex('}') + 1])
LN += f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
fa.append(f"{mixf},{LN},aresample=48000[aout]")
OUT = f"{P}/renders/{C['name']}.mp4"
run([*ins, '-filter_complex', ';'.join(fv + fa), '-map', '[vout]', '-map', '[aout]',
     '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
     '-c:a', 'aac', '-b:a', '256k', '-t', f"{E['total']:.3f}", OUT])
print('✅', OUT)
