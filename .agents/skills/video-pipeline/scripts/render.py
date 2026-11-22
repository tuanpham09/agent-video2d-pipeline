#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Render HyperFrames: mặc định draft (nháp, nhanh), delivery chỉ 1 lần cuối.

Quy tắc (Fix 4): xem chuyển động thì render nháp — nhanh hơn rõ rệt mà vẫn đủ
xem motion/timing. Chỉ khi đã chốt preview mới render delivery, đúng 1 lần cuối.
Không render delivery cho bản xem thử.
Nháp nhanh nhờ 2 thứ: --quality draft (encode nhẹ) và 15 fps (Chrome chụp ít
frame hơn một nửa; thời lượng và tiếng vẫn khớp vì composition tính theo giây).
Đo thật trên demo 15s (VM 1,5 CPU): draft 15fps ~72s, delivery 30fps ~135s.

Dùng (từ gốc repo):
  python .agents/skills/video-pipeline/scripts/render.py --project projects/<slug>
  python .agents/skills/video-pipeline/scripts/render.py --project projects/<slug> --delivery
  python .agents/skills/video-pipeline/scripts/render.py --project projects/<slug> --out output/xem-thu.mp4 -- --fps 30

Mặc định: nháp -> --quality draft + 15 fps, ra output/draft-<YYYYMMDD-HHMMSS>.mp4.
--delivery -> --quality delivery, fps gốc của composition, ra output/final.mp4.
Mọi cờ sau `--` được chuyển thẳng cho `npx hyperframes render` (vd --fps 30 sẽ
thắng fps mặc định của bản nháp).
Mã thoát = mã thoát của hyperframes.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path


def main() -> int:
    argv = sys.argv[1:]
    extra: list[str] = []
    if "--" in argv:
        cut = argv.index("--")
        extra = argv[cut + 1:]
        argv = argv[:cut]

    ap = argparse.ArgumentParser(description="Render HyperFrames (mặc định draft, --delivery chỉ 1 lần cuối).")
    ap.add_argument("--project", type=Path, required=True, help="thư mục project, vd projects/<slug>")
    ap.add_argument("--delivery", action="store_true", help="render delivery (chất lượng đầy đủ), ra output/final.mp4")
    ap.add_argument("--out", type=Path, help="đường dẫn file ra (mặc định theo chế độ)")
    ap.add_argument("--video-dir", type=Path, help="thư mục project HyperFrames (mặc định <project>/video)")
    args = ap.parse_args(argv)

    proj = args.project
    video_dir = args.video_dir or (proj / "video")
    if not video_dir.is_dir():
        print(f"LỖI: không có thư mục video {video_dir}", file=sys.stderr)
        return 1
    quality = "delivery" if args.delivery else "draft"
    if args.out:
        out = args.out if args.out.is_absolute() else proj / args.out
    elif args.delivery:
        out = proj / "output" / "final.mp4"
    else:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        out = proj / "output" / f"draft-{stamp}.mp4"
    # hyperframes chạy với cwd=<video_dir> nên -o phải là đường dẫn tuyệt đối
    out = out.resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = ["npx", "hyperframes", "render", "--quality", quality, "-o", str(out)]
    if not args.delivery and not any(a == "--fps" or a.startswith("--fps=") for a in extra):
        cmd += ["--fps", "15"]  # nháp: ít frame hơn một nửa -> nhanh ~2 lần, vẫn đủ xem chuyển động
    cmd += extra
    print(f"render ({quality}): {' '.join(cmd)}  [cwd={video_dir}]")
    t0 = time.time()
    r = subprocess.run(cmd, cwd=video_dir)
    dt = time.time() - t0
    if r.returncode == 0:
        print(f"xong trong {dt:.1f}s -> {out}")
    else:
        print(f"FAIL sau {dt:.1f}s (mã {r.returncode})", file=sys.stderr)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
