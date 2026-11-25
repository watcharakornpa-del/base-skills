# caps.json → subs.srt · ผู้ใช้สั่ง: ไม่ขึ้นคำ เนาะ เนอะ นะ ป่ะ อ่ะ · S2 (25 พ.ย. 2026): + น่ะ เนี่ย เฮ้ย เอ่อ เออ · เนี้ย → นี้ · บรรทัด ≤ 30 ตัว (ห้ามย่อ)
import json,re,sys
c=json.load(open('work/caps.json'))
def clean(t):
    t=re.sub(r'เนี้ย', 'นี้', t); t=re.sub(r'(\s*)(เนาะ|เนอะ|ป่ะ|อ่ะ|น่ะ|เนี่ย|เฮ้ย|เอ่อ|เออ(?!ร))', lambda m: ' ' if m.group(1) else '', t); t=re.sub(r'นะ(?=ครับ|ว่า|$)', '', t)
    return re.sub(r'\s+',' ',t).strip()
def f(t): return f"{int(t//3600):02d}:{int(t%3600//60):02d}:{t%60:06.3f}".replace('.',',')
out=[]
for i,x in enumerate(c):
    s,e=x['start'],x['end']
    if i+1<len(c): n=c[i+1]['start']; e = n if n-e<0.5 else e+0.2
    t=clean(x['text']); assert len(t)<=30, t
    out.append(f"{i+1}\n{f(s)} --> {f(e)}\n{t}\n")
open('work/subs.srt','w',encoding='utf-8').write('\n'.join(out)); print(len(out),'บรรทัด')
