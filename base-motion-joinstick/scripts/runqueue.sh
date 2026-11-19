#!/bin/zsh
# เรนเดอร์ตามคิวใน renderqueue.txt ทีละบรรทัด (เพิ่มบรรทัดได้ระหว่างรัน) · จบเมื่อคิวว่าง 10 นาที
V=~/Developer/video-use; idle=0   # renderqueue.txt อยู่ที่นี่ (บรรทัดละ  <โฟลเดอร์ใน video-use>|<ชื่อไฟล์ส่ง>)
while [ $idle -lt 40 ]; do
  L=$(head -1 $V/renderqueue.txt 2>/dev/null)
  if [ -z "$L" ]; then sleep 15; idle=$((idle+1)); continue; fi
  idle=0; sed -i '' 1d $V/renderqueue.txt
  echo "▶ $L"; ~/.claude/skills/base-motion-joinstick/scripts/renderclip.sh "$V/${L%%|*}" "${L#*|}" 2>&1 | grep -v "^NEAR" | tail -12
done
