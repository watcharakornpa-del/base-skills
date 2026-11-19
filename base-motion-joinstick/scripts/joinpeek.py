#!/usr/bin/env python3
# ดูพลังงานเสียง ±0.5 วิ รอบจุดที่ joincheck แจ้ง (ใช้จากโฟลเดอร์โปรเจกต์): python joinpeek.py 53.92 63.44 ...
import json,subprocess,shutil,struct,math,sys
K=json.load(open('work/keep.json')); W=[w for w in json.load(open('work/scribe.json'))['words'] if w['type']=='word']
d=subprocess.run([shutil.which('ffmpeg'),'-nostdin','-v','error','-i','work/audio.mp3','-ac','1','-ar','8000','-f','s16le','-'],capture_output=True).stdout
n=len(d)//2; s=struct.unpack('<%dh'%n,d)
def mp(t0,t1):
    o=''
    for i in range(int(t0*8000),int(t1*8000),160):
        seg=s[i:i+160]; db=20*math.log10(math.sqrt(sum(x*x for x in seg)/len(seg))/32768+1e-9); o+='_' if db<-35 else ('.' if db<-25 else '#')
    return o
for t in map(float,sys.argv[1:]):
    pk=[k for k in K if abs(k[0]-t)<0.01 or abs(k[1]-t)<0.01]
    print(f'== {t} piece {pk}  {mp(t-0.5,t)}|{mp(t,t+0.5)}')
    print('   ', ''.join(f"{w['text']}{w['start']:.2f} " for w in W if t-0.6<=w['start']<=t+0.6))
