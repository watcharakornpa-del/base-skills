# พลังงานเสียงทีละ 20 ms (dB) ช่วง [t0, t0+dur] ของ work/audio.mp3 — ใช้หาขอบคำจริงตอนตัดคำซ้ำ
import sys,struct,math,subprocess,shutil
t0,dur=float(sys.argv[1]),float(sys.argv[2])
d=subprocess.run([shutil.which('ffmpeg'),'-nostdin','-v','error','-ss',str(t0),'-t',str(dur),'-i','work/audio.mp3','-ac','1','-ar','8000','-f','s16le','-'],capture_output=True).stdout
n=len(d)//2; s=struct.unpack('<%dh'%n,d); w=160
print(' '.join(f'{t0+i/8000:.2f}:{int(20*math.log10(math.sqrt(sum(x*x for x in s[i:i+w])/w)/32768+1e-9))}' for i in range(0,n-w,w)))
