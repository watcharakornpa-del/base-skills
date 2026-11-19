#!/bin/zsh
# ประกอบฉาก + ซับ คลิป AI Productivity · ใช้: buildclip.sh <โปรเจกต์> [--recaps]
# work/scenes_clip.py (ฉากของคลิปนี้) + template/scene_common.py · FACE_CROP=... ตั้งได้ (ค่าเริ่ม ห้องโปสเตอร์ AI Productivity) → work/scenes.py → splice → ซับ (autocaps ถ้ายังไม่มี captions.txt) → gen → lint
export PATH=$HOME/.local/bin:$PATH; PY=${JS_PY:-$(ls ~/.venvs/joinstick/bin/python ~/Desktop/BASE/.venv/bin/python ~/Developer/video-use/tiktok031026-clip6/.venv/bin/python 2>/dev/null | head -1)}; K=~/.claude/skills/base-motion-joinstick/scripts; V=~/Developer/video-use; S=~/.claude/skills/base-motion-joinstick
cd "$1" || exit 1
T=$(ffprobe -v error -show_entries format=duration -of csv=p=0 gfx/assets/talk.mp4)
cat $S/template/scene_common.py work/scenes_clip.py > work/scenes.py
grep -q 'C2678 · 7 Values' gfx/style.css || cat $S/template/extra_screenrec.css >> gfx/style.css
[ -f work/extra_clip.css ] && { python3 -c "import sys;p='gfx/style.css';s=open(p).read().split('/* EXTRA_CLIP')[0];open(p,'w').write(s+'/* EXTRA_CLIP */\n'+open('work/extra_clip.css').read())"; }
FIX=$(cat work/fix.json 2>/dev/null || echo '[]')
$PY $K/splice.py gfx work/scenes.py $T "${FACE_CROP:-1000:1000:40:280}" "$FIX" | tail -1
cd gfx/work; cp $K/caps2srt.py caps2srt.py
[ -f captions.txt ] || $PY $K/autocaps.py . | tail -1
python3 align.py --fuzzy 2>&1 | tail -2; cd ..; python3 work/caps2srt.py || exit 1
$PY gen.py 2>&1 | tail -2; npx --yes hyperframes@0.8.147 lint 2>&1 | tail -1
python3 $K/cicheck.py . || { echo '⛔ แก้ CI ก่อนเรนเดอร์'; exit 1; }
python3 - <<'PY'
import json,re
H=json.load(open('work/hide.json')); s=open('work/subs.srt',encoding='utf-8').read().strip().split('\n\n')
def sec(x): h,m,r=x.split(':'); return int(h)*3600+int(m)*60+float(r.replace(',','.'))
vis=0
for b in s:
    L=b.split('\n'); a,e=[sec(x) for x in L[1].split(' --> ')]
    ov=max([max(0,min(e,h1)-max(a,h0)) for h0,h1 in H]+[0])
    if ov/(e-a)<=0.4: vis+=1; print(f'{L[0]:>4}|{a:7.2f} {L[2]}')
    elif ov<e-a-0.05 and ov>0: print(f'{L[0]:>4}|~ทับ {a:.2f} {L[2]}')
print('ซับที่ขึ้นจริง',vis,'/',len(s))
PY
