#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""preview_shot.py — dựng MỘT shot, chụp ảnh ở các mốc beat, ra contact sheet để agent MỞ ẢNH XEM (R10.2).

Làm đúng chuỗi mà agent hay làm tay: build_video --shots <id> → hyperframes snapshot tại mốc beat → contact-sheet.jpg.

Mốc chụp mặc định: đầu shot, mỗi beat (đã giải neo `word`, đã bung macro, cộng `dt`), thêm 0,35 s sau beat vật lý
(để thấy kết quả), và cuối shot. Gộp mốc cách nhau < 0,25 s; tối đa --max-frames (mặc định 10).

Dùng:
  python .agents/skills/video-pipeline/scripts/preview_shot.py --project projects/<slug> --shot SH008
  python ... --project projects/<slug> --shot SH008 --shotlist /đường/dẫn/shotlist_thu.json   # thử biến thể, không sửa project
  python ... --project projects/<slug> --shot SH008 --at 0.5,1.3,2.0                          # tự chọn mốc (giây trong shot)
  python ... --project projects/<slug> --shot SH008 --out /tmp/preview_sh008

Ra: <out>/preview/<shot>_contact.jpg (ảnh ghép; nhiều khung thì _contact_1.jpg, _contact_2.jpg…) + <out>/preview/<shot>_frames/*.png + <out>/preview/<shot>_legend.txt
(mốc ↔ mô tả beat). Lệnh in đường dẫn; agent phải mở ảnh xem rồi mới báo xong (R10.2). Không thay cho gate.
Chưa kiểm: video/âm thanh thật (chỉ khung hình tĩnh, không phát chuyển động).
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HYPERFRAMES = "hyperframes@0.9.82"  # ghim cùng render.py/gates.py
AFTER_PHYSICAL = 0.35
MERGE_GAP = 0.25


def beat_marks(proj: Path, shotlist: Path | None, shot_id: str) -> tuple[float, list[tuple[float, str]]]:
    """(thời lượng shot, [(giây trong shot, nhãn)]) — dùng đúng hàm giải neo của generator."""
    import build_video as bv
    from behaviors import expand_shot
    from timing_lib import beat_time

    ctx = bv.Ctx(proj, shotlist)
    shot = next((s for s in ctx.shotlist["shots"] if s["id"] == shot_id), None)
    if shot is None:
        sys.exit(f"LỖI: không có shot {shot_id} trong shotlist")
    a0, a1 = bv.shot_window(shot, ctx)
    dur = a1 - a0
    shot = expand_shot(shot, ctx.lines, a0)
    marks: list[tuple[float, str]] = [(0.1, "đầu shot")]
    for b in shot.get("beats", []):
        t = beat_time(b, ctx.lines, a0)
        label = (b.get("do") or "beat")[:60]
        marks.append((t, label))
        if b.get("physical"):
            marks.append((t + AFTER_PHYSICAL, f"sau: {label}"))
    marks.append((max(0.1, dur - 0.1), "cuối shot"))
    return dur, marks


def pick(marks: list[tuple[float, str]], dur: float, max_frames: int) -> list[tuple[float, str]]:
    cleaned = sorted((min(max(t, 0.05), max(0.05, dur - 0.05)), lb) for t, lb in marks)
    out: list[tuple[float, str]] = []
    for t, lb in cleaned:
        if out and t - out[-1][0] < MERGE_GAP:
            continue
        out.append((round(t, 2), lb))
    while len(out) > max_frames:  # bỏ bớt mốc "sau:" trước, rồi bỏ đều
        drop = next((i for i, (_, lb) in enumerate(out) if lb.startswith("sau:")), len(out) // 2)
        out.pop(drop)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--shot", required=True, help="id shot, ví dụ SH008")
    ap.add_argument("--shotlist", type=Path, help="shotlist khác (thử biến thể)")
    ap.add_argument("--at", help="mốc tự chọn (giây trong shot), cách nhau dấu phẩy")
    ap.add_argument("--out", type=Path, help="thư mục dựng + ảnh (mặc định: thư mục tạm)")
    ap.add_argument("--max-frames", type=int, default=10)
    args = ap.parse_args()

    proj = args.project.resolve()
    shotlist = args.shotlist.resolve() if args.shotlist else None
    out = (args.out or Path(tempfile.mkdtemp(prefix=f"preview_{args.shot}_"))).resolve()
    out.mkdir(parents=True, exist_ok=True)

    cmd = [sys.executable, str(HERE / "build_video.py"), "--project", str(proj), "--shots", args.shot, "--out", str(out)]
    if shotlist:
        cmd += ["--shotlist", str(shotlist)]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print((r.stdout + r.stderr).strip()[-1500:], file=sys.stderr)
        print(f"✗ build_video lỗi (shot {args.shot}) — sửa shotlist/bible rồi chạy lại", file=sys.stderr)
        return 1

    dur, marks = beat_marks(proj, shotlist, args.shot)
    if args.at:
        times = [(float(x), "tự chọn") for x in args.at.split(",") if x.strip()]
    else:
        times = pick(marks, dur, args.max_frames)

    env = dict(os.environ, TEMP="/tmp", TMP="/tmp") if os.name != "nt" else dict(os.environ)
    snap = subprocess.run(
        ["npx", "-y", HYPERFRAMES, "snapshot", "--at", ",".join(str(t) for t, _ in times)],
        cwd=out, env=env, capture_output=True, text=True, encoding="utf-8")
    text = snap.stdout + snap.stderr
    m = re.search(r"(\S+/snapshots/[0-9a-f-]+)/contact-sheet(?:-\d+)?\.jpg", text)
    if snap.returncode not in (0, 2) or not m:  # mã 2 = chỉ cảnh báo proxy trong môi trường cloud
        print(text.strip()[-1500:], file=sys.stderr)
        print("✗ hyperframes snapshot không ra ảnh", file=sys.stderr)
        return 1
    snap_dir = Path(m.group(1))

    prev = out / "preview"
    frames = prev / f"{args.shot}_frames"
    frames.mkdir(parents=True, exist_ok=True)
    for p in snap_dir.glob("frame-*.png"):
        shutil.copy2(p, frames / p.name)
    sheets = sorted(snap_dir.glob("contact-sheet*.jpg"))  # nhiều khung → hyperframes tách contact-sheet-1.jpg, -2.jpg…
    contacts = []
    for i, sp in enumerate(sheets, 1):
        dst = prev / (f"{args.shot}_contact.jpg" if len(sheets) == 1 else f"{args.shot}_contact_{i}.jpg")
        shutil.copy2(sp, dst)
        contacts.append(dst)
    legend = prev / f"{args.shot}_legend.txt"
    legend.write_text("\n".join(f"{i + 1}. {t:g}s — {lb}" for i, (t, lb) in enumerate(times)) + "\n", encoding="utf-8")

    print(f"shot {args.shot}: dài {dur:.2f}s, chụp {len(times)} khung")
    for i, (t, lb) in enumerate(times):
        print(f"  {i + 1}. {t:g}s — {lb}")
    for c in contacts:
        print(f"ẢNH GHÉP : {c}")
    print(f"KHUNG LẺ : {frames}")
    print("→ MỞ ẢNH GHÉP XEM trước khi báo xong (R10.2); ghi vào báo cáo: 'Ảnh đã XEM: <đường dẫn> — thấy gì, lỗi đã sửa'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
