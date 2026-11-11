#!/bin/bash
# เรนเดอร์ปก + Super เป็น MOV ProRes 4444 พื้นใส → renders/gfx/<ชื่อ>.mov
set -e; P="$(cd "$(dirname "$0")/.." && pwd)"; mkdir -p "$P/renders/gfx"
for d in "$P"/gfx/*/; do n=$(basename "$d")
  (cd "$d" && npx --yes hyperframes@0.8.147 render --format mov -f 30 --workers 1 -o "$P/renders/gfx/$n.mov" > "$P/work/render_$n.log" 2>&1) && echo "✅ $n" || { echo "❌ $n (ดู work/render_$n.log)"; exit 1; }
done
