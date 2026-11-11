#!/usr/bin/env python3
"""ส่งใบงานให้ panel AIStoryCutter ใน Premiere แล้วรอผล

ใช้คู่กับ client/js/basemotionwatch.js — วางไฟล์ .json ไว้ในคิว panel
เห็นภายใน 3 วิ แล้วเขียนไฟล์ .done กลับมาบอกผล

  premiere_bridge.py export <sequence> <out.mp4>
  premiere_bridge.py insert <overlay.mov> <sequence> [--video 1] [--audio 1]
                            [--at 0] [--replace]

ชื่อซีเควนซ์เว้นเป็น "" ได้ = ใช้ซีเควนซ์ที่เปิดอยู่
ออก 0 = สำเร็จ · ออก 1 = พัง (พิมพ์เหตุผลออก stderr)
"""
import argparse, json, os, subprocess, sys, time, uuid

QUEUE = os.path.expanduser("~/AIStoryCutter/base-motion-queue")
PRESET = ("/Applications/Adobe Media Encoder 2026/Adobe Media Encoder 2026.app"
          "/Contents/MediaIO/systempresets/4E49434B_48323634"
          "/00 - Match Source - High bitrate.epr")

# panel ตอบกลับเร็ว (แค่รับงาน) แต่ Premiere อาจยังไม่เปิด จึงรอได้นาน
ACK_TIMEOUT = 300
# AME เรนเดอร์จริงใช้เวลาตามความยาวคลิป
RENDER_TIMEOUT = 3600
# ไฟล์ต้องหยุดโตเท่านี้ถึงนับว่าเรนเดอร์จบ
STABLE_SECONDS = 6


def submit(job: dict) -> str:
    """วางใบงานลงคิวแล้วคืน path ของไฟล์ .done ที่ panel จะเขียนกลับ"""
    os.makedirs(QUEUE, exist_ok=True)
    job_id = f"{int(time.time())}-{uuid.uuid4().hex[:8]}"
    done = os.path.join(QUEUE, f"{job_id}.done")
    job["done"] = done
    # เขียนไฟล์ .tmp ก่อนแล้วค่อย rename: panel poll ทุก 3 วิ ถ้าเขียนตรง ๆ
    # มันอาจอ่านไฟล์ที่ยังเขียนไม่จบแล้ว JSON.parse พังแล้วทิ้งใบงานทันที
    tmp = os.path.join(QUEUE, f"{job_id}.json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(job, fh, ensure_ascii=False)
    os.replace(tmp, os.path.join(QUEUE, f"{job_id}.json"))
    return done


def wait_ack(done: str, timeout: int) -> str:
    """รอ panel ตอบกลับ — ข้อความขึ้นต้น OK คือรับงานแล้ว"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if os.path.exists(done):
            with open(done, encoding="utf-8") as fh:
                return fh.read().strip()
        time.sleep(1)
    raise TimeoutError(
        f"panel ไม่ตอบใน {timeout} วิ — Premiere เปิดอยู่ไหม "
        "และเปิดแผง AI Story Cutter แล้วหรือยัง (Window › Extensions)"
    )


def wait_render(path: str, timeout: int) -> None:
    """รอจน AME เขียนไฟล์เสร็จ — โตแล้วหยุดโตนิ่ง ๆ ถึงนับว่าจบ

    ack จาก panel บอกแค่ว่า "ส่งเข้าคิว AME แล้ว" ไม่ได้แปลว่าเรนเดอร์เสร็จ
    ถ้าหยิบไฟล์ไปใช้ตอนเขียนยังไม่จบ ffprobe จะอ่านความยาวผิด แล้วซับเลื่อนทั้งคลิป
    """
    deadline = time.time() + timeout
    last_size, stable_since = -1, None
    while time.time() < deadline:
        size = os.path.getsize(path) if os.path.exists(path) else -1
        if size > 0 and size == last_size:
            if stable_since is None:
                stable_since = time.time()
            elif time.time() - stable_since >= STABLE_SECONDS:
                return
        else:
            stable_since = None
        last_size = size
        time.sleep(2)
    raise TimeoutError(f"AME เรนเดอร์ไม่เสร็จใน {timeout} วิ — เช็คคิวใน Media Encoder")


def _main_binaries() -> list:
    """เฉพาะ process ที่เป็น "ตัวแอปจริง" — .../<ชื่อ>.app/Contents/MacOS/<ชื่อ>

    Premiere ลากลูกน้องมาเพียบใต้ bundle เดียวกัน (crashpad_handler ·
    dynamiclinkmanager · TeamProjectsLocalHub · CEPHtmlEngine อีกหลายตัว)
    และพวกนี้ค้างต่ออีกพักหลังตัวหลักปิดไปแล้ว การเช็คแค่ว่าเจอ
    ".app/Contents/MacOS/" จึงรายงานว่า "ยังเปิดอยู่" ตลอดกาล
    """
    out = subprocess.run(["ps", "-A", "-o", "comm"], capture_output=True, text=True).stdout
    names = []
    for line in out.splitlines():
        line = line.strip()
        head, sep, exe = line.partition(".app/Contents/MacOS/")
        if not sep or "/" in exe:        # "/" ใน exe = ลูกน้องที่ซ้อน .app อีกชั้น
            continue
        app = head.split("/")[-1]
        if exe == app:                   # ชื่อไฟล์ต้องตรงกับชื่อ .app ถึงจะเป็นตัวหลัก
            names.append(app)
    return names


def premiere_app() -> str:
    """ชื่อแอป Premiere ที่กำลังรันอยู่ — เครื่องนี้มีหลายเวอร์ชัน เดาไม่ได้"""
    for app in _main_binaries():
        if app.startswith("Adobe Premiere Pro"):
            return app
    raise RuntimeError("หา Premiere ที่เปิดอยู่ไม่เจอ — เปิดโปรแกรมก่อน")


def premiere_running(app_name: str) -> bool:
    return app_name in _main_binaries()


def restart(skip_save: bool = False, timeout_quit: int = 120, timeout_up: int = 300) -> int:
    """เซฟ → ปิดแบบสุภาพ → เปิดใหม่ → รอจนสะพานตอบอีกครั้ง

    ไม่ใช้ force quit (kill) เด็ดขาด: ถ้ามีหน้าต่างค้างขวางอยู่ การบังคับปิด
    = งานที่ยังไม่เซฟหาย ยอมหมดเวลาแล้วให้คนไปดูเองดีกว่า
    """
    app_name = premiere_app()
    print(f"… เจอ {app_name}")

    if skip_save:
        # ไก่กับไข่: ครั้งแรกสุด baseMotionSave ยังไม่ถูกโหลดใน Premiere ที่เปิดค้างอยู่
        # จึงเซฟผ่านสะพานไม่ได้ ต้องให้คนกด Cmd+S เองก่อนแล้วค่อยสั่งด้วยธงนี้
        print("… ข้ามการเซฟตามที่สั่ง (ถือว่ากด Cmd+S มาแล้ว)")
    else:
        res = wait_ack(submit({"action": "save"}), ACK_TIMEOUT)
        if not res.startswith("OK"):
            print(f"เซฟไม่สำเร็จ ยกเลิกการรีสตาร์ท: {res}", file=sys.stderr)
            return 1
        print(f"… {res}")

    # "ignoring application responses" = ยิงคำสั่งแล้วไม่รอ reply
    # Premiere รับ quit ไปทำจริง แต่ไม่ส่งคำตอบกลับ ถ้ารอจะได้ -1712 AppleEvent
    # timed out ทั้งที่คำสั่งถึงแล้ว — เราเฝ้า process เองอยู่แล้ว ไม่ต้องการ reply
    q = subprocess.run(
        ["osascript", "-e",
         f'ignoring application responses\ntell application "{app_name}" to quit\nend ignoring'],
        capture_output=True, text=True)
    if q.returncode != 0:
        err = (q.stderr or "").strip()
        hint = ""
        if "-1743" in err or "Not authorized" in err or "not allowed" in err:
            hint = ("\n→ macOS ไม่อนุญาตให้สั่งคุม Premiere: ไปที่ System Settings › Privacy & Security "
                    "› Automation แล้วเปิดสิทธิ์ให้แอปที่รันคำสั่งนี้ (Terminal / Claude) ควบคุม Premiere")
        print(f"สั่งปิด Premiere ไม่สำเร็จ: {err or 'osascript ล้มเหลว'}{hint}", file=sys.stderr)
        return 1
    deadline = time.time() + timeout_quit
    while time.time() < deadline:
        if not premiere_running(app_name):
            break
        time.sleep(2)
    else:
        print(f"Premiere ไม่ยอมปิดใน {timeout_quit} วิ — น่าจะมีหน้าต่างค้างขออะไรอยู่ "
              "ไปดูที่หน้าจอแล้วลองใหม่ (ไม่บังคับปิดให้ เดี๋ยวงานหาย)", file=sys.stderr)
        return 1
    print("… ปิดแล้ว กำลังเปิดใหม่")

    subprocess.run(["open", "-a", app_name], check=True)
    # เปิดโปรแกรมติดไม่ได้แปลว่าพร้อม — ต้องรอจนแผงโหลดและตอบใบงานได้
    deadline = time.time() + timeout_up
    while time.time() < deadline:
        done = submit({"action": "ping"})
        try:
            res = wait_ack(done, 20)
        except TimeoutError:
            continue
        if res.startswith("OK"):
            print(f"✅ Premiere พร้อมแล้ว ({res})")
            return 0
    print(f"เปิดแล้วแต่สะพานไม่ตอบใน {timeout_up} วิ — เช็คว่าโปรเจกต์เปิดคืนมาไหม "
          "และแผง AI Story Cutter เปิดอยู่หรือเปล่า", file=sys.stderr)
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="action", required=True)

    pe = sub.add_parser("export", help="สั่ง Premiere export ซีเควนซ์ที่เปิดอยู่")
    pe.add_argument("sequence", help='ชื่อซีเควนซ์ ("" = ที่เปิดอยู่)')
    pe.add_argument("out", help="ไฟล์ปลายทาง .mp4")
    pe.add_argument("--preset", default=PRESET)
    pe.add_argument("--no-captions", action="store_true",
                    help="ไม่เบิร์นแทร็กซับลงภาพ — ใช้กับไฟล์ส่งงานจริงที่ขึ้นซับเป็น CC แยกแทร็ก")

    pi = sub.add_parser("insert", help="วางกราฟิกกลับเข้า timeline")
    pi.add_argument("mov", help="ไฟล์ overlay .mov")
    pi.add_argument("sequence", help='ชื่อซีเควนซ์ ("" = ที่เปิดอยู่)')
    pi.add_argument("--video", type=int, default=1, help="แทร็กวิดีโอ 0=V1 1=V2")
    pi.add_argument("--audio", type=int, default=1, help="แทร็กเสียง 0=A1 1=A2")
    pi.add_argument("--at", type=float, default=0.0, help="วินาทีที่วาง")
    pi.add_argument("--replace", action="store_true", help="ทับของเดิมบนแทร็กนั้น")

    pf = sub.add_parser("frame", help="เลื่อนหน้าคนพูดลงให้พ้นแผงกราฟิก")
    pf.add_argument("sequence", help='ชื่อซีเควนซ์ ("" = ที่เปิดอยู่)')
    pf.add_argument("--video", type=int, default=0, help="แทร็กวิดีโอของคนพูด 0=V1")
    pf.add_argument("--dy", type=float, default=600, help="เลื่อนลงกี่ px (แผงสูง 800)")

    sub.add_parser("save", help="เซฟโปรเจกต์ที่เปิดอยู่")
    pr = sub.add_parser("restart", help="เซฟ → ปิด → เปิด Premiere ใหม่ (ให้โค้ดใหม่มีผล)")
    pr.add_argument("--skip-save", action="store_true",
                    help="ข้ามการเซฟผ่านสะพาน (ใช้ครั้งแรกสุดที่โค้ดใหม่ยังไม่โหลด — ต้องกด Cmd+S เองก่อน)")

    a = ap.parse_args()

    if a.action == "restart":
        return restart(skip_save=a.skip_save)

    if a.action == "save":
        res = wait_ack(submit({"action": "save"}), ACK_TIMEOUT)
        if not res.startswith("OK"):
            print(f"เซฟไม่สำเร็จ: {res}", file=sys.stderr)
            return 1
        print(f"✅ {res}")
        return 0

    if a.action == "frame":
        done = submit({"action": "frame", "sequence": a.sequence,
                       "video": a.video, "dy": a.dy})
        res = wait_ack(done, ACK_TIMEOUT)
        if not res.startswith("OK"):
            print(f"เลื่อนไม่สำเร็จ: {res}", file=sys.stderr)
            return 1
        print(f"✅ {res}")
        return 0

    if a.action == "export":
        out = os.path.abspath(a.out)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        if not os.path.exists(a.preset):
            print(f"ไม่พบ preset: {a.preset}", file=sys.stderr)
            return 1
        # ไฟล์เก่าค้างอยู่จะทำให้ wait_render คิดว่าเสร็จแล้วตั้งแต่วินาทีแรก
        if os.path.exists(out):
            os.remove(out)
        done = submit({"action": "export", "sequence": a.sequence,
                       "out": out, "preset": a.preset,
                       "captions": not a.no_captions})
        res = wait_ack(done, ACK_TIMEOUT)
        if not res.startswith("OK"):
            print(f"Premiere ปฏิเสธงาน export: {res}", file=sys.stderr)
            return 1
        print(f"… ส่งเข้าคิว Media Encoder แล้ว กำลังรอไฟล์ {out}")
        wait_render(out, RENDER_TIMEOUT)
        print(f"✅ export เสร็จ: {out}")
        return 0

    mov = os.path.abspath(a.mov)
    if not os.path.exists(mov):
        print(f"ไม่พบไฟล์ overlay: {mov}", file=sys.stderr)
        return 1
    done = submit({"action": "insert", "mov": mov, "sequence": a.sequence,
                   "video": a.video, "audio": a.audio, "at": a.at,
                   "replace": bool(a.replace)})
    res = wait_ack(done, ACK_TIMEOUT)
    if not res.startswith("OK"):
        print(f"วางกราฟิกไม่สำเร็จ: {res}", file=sys.stderr)
        return 1
    print(f"✅ {res}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except TimeoutError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
