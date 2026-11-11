#!/usr/bin/env python3
"""นำเข้า XML Draft2 + ซับ เข้าโปรเจกต์ที่เปิดอยู่ใน Premiere ผ่านแผง AI Story Cutter (action "importxml") แล้วเซฟ
ต้อง: Premiere เปิดโปรเจกต์ไว้ + แผงเปิดอยู่ · ไม่นำเข้าซ้ำถ้ามีซีเควนซ์ชื่อเดียวกันแล้ว
ใช้: python3 -I premiere_import.py "<โฟลเดอร์ C5395-draft2>" [bin]"""
import os, sys
sys.path.insert(0, os.path.expanduser('~/.claude/skills/base-motion/scripts'))
from premiere_bridge import submit, wait_ack
root = sys.argv[1]; binname = sys.argv[2] if len(sys.argv) > 2 else 'C5395 Draft2'
ok = 0
for d in sorted(os.listdir(root)):
    p = os.path.join(root, d)
    if not os.path.isdir(p): continue
    xml, srt = os.path.join(p, d + '.xml'), os.path.join(p, d + '.srt')
    res = wait_ack(submit({'action': 'importxml', 'xml': xml, 'sequence': 'C5395 ' + d, 'srt': srt if os.path.exists(srt) else '', 'bin': binname}), 300)
    print(('✅ ' if res.startswith('OK') else '❌ ') + res); ok += res.startswith('OK')
print(f'นำเข้าได้ {ok} คลิป')
