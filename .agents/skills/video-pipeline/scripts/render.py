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
  python .agents/skills/video-pipeline/scripts/render.py --project projects/<slug> --shots SH002
  python .agents/skills/video-pipeline/scripts/render.py --project projects/<slug> --shots SH002,SH005

Mặc định: nháp -> --quality draft + 15 fps, ra output/draft-<YYYYMMDD-HHMMSS>.mp4.
--delivery -> --quality delivery, fps gốc của composition, ra output/final.mp4.
--shots <id,...> -> render RIÊNG từng shot (compositions/<id>.html, qua cờ -c của
hyperframes), mỗi shot 1 file. Draft: output/draft-<id>-<stamp>.mp4, chỉ để xem
chuyển động của shot vừa sửa. Delivery (Opt round 3 mục 1): --shots + --delivery
ra đường dẫn ỔN ĐỊNH output/shots/<id>.mp4 để concat_shots.py nối lại thành video
hoàn chỉnh — render 1 shot KHÔNG kèm track giọng (compositions chỉ chứa hình +
GSAP); đồng bộ giọng vẫn phải render đủ hoặc nối bằng concat_shots.py.
Mọi cờ sau `--` được chuyển thẳng cho `hyperframes render` (vd --fps 30 sẽ
thắng fps mặc định của bản nháp). Phiên bản HyperFrames đã ghim
(HYPERFRAMES_VERSION = 0.9.82, Opt round 3 mục 0) — xem ghi chú ở đầu file.
Mã thoát = mã thoát của hyperframes (với --shots: 1 nếu shot nào fail).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Opt round 3, mục 0: GHIM phiên bản HyperFrames — `npx hyperframes` không ghim
# từng tự cài 0.9.82 trong lúc kiểm chứng, trong khi package.json ghim 0.9.81 và
# AGENTS.md ghi 0.9.66. Mọi số đo vòng 3 chạy trên phiên bản này; muốn đo phiên
# bản khác thì dùng cờ --hyperframes-version (ghi rõ version vào báo cáo).
HYPERFRAMES_VERSION = "0.9.82"


def hf_cmd(version: str = HYPERFRAMES_VERSION) -> list[str]:
    """Lệnh gọi HyperFrames đã ghim phiên bản (tránh npx trôi nổi)."""
    return ["npx", "--yes", f"hyperframes@{version}"]


def render_shots(proj: Path, video_dir: Path, shots_arg: str, extra: list[str],
                 hf_version: str = HYPERFRAMES_VERSION, delivery: bool = False,
                 workers: str | None = None) -> int:
    """Render riêng từng shot qua `hyperframes render -c`.

    Mỗi shot = compositions/<id>.html (do build_video.py sinh). Render 1 shot chỉ
    chứa hình + GSAP, không kèm track giọng — chỉ dùng để xem chuyển động.
    Draft (mặc định): 15fps, ra output/draft-<id>-<stamp>.mp4 để xem thử.
    Delivery (--delivery, Opt round 3 mục 1): chất lượng đầy đủ, ra đường dẫn
    ỔN ĐỊNH output/shots/<id>.mp4 để concat_shots.py nối lại — không timestamp
    để lần render sau ghi đè đúng file cần nối.
    """
    ids = [s.strip() for s in shots_arg.split(",") if s.strip()]
    if not ids:
        print("LỖI: --shots rỗng", file=sys.stderr)
        return 1
    missing = [s for s in ids if not (video_dir / "compositions" / f"{s}.html").is_file()]
    if missing:
        print(f"LỖI: không có composition: {', '.join(missing)} (chạy build_video.py trước)", file=sys.stderr)
        return 1
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    outdir = proj / "output"
    outdir.mkdir(parents=True, exist_ok=True)
    if delivery:
        (outdir / "shots").mkdir(parents=True, exist_ok=True)
    t_all = time.time()
    failed: list[str] = []
    for sid in ids:
        # hyperframes chạy với cwd=<video_dir> nên -o phải là đường dẫn tuyệt đối
        if delivery:
            out = (outdir / "shots" / f"{sid}.mp4").resolve()
        else:
            out = (outdir / f"draft-{sid}-{stamp}.mp4").resolve()
        cmd = hf_cmd(hf_version) + ["render", "-c", f"compositions/{sid}.html",
               "--quality", "delivery" if delivery else "draft", "-o", str(out)]
        if workers:
            cmd += ["--workers", workers]
        if not delivery and not any(a == "--fps" or a.startswith("--fps=") for a in extra):
            cmd += ["--fps", "15"]
        cmd += extra
        print(f"render shot {sid} ({'delivery' if delivery else 'draft'}): {' '.join(cmd)}  [cwd={video_dir}]")
        t0 = time.time()
        r = subprocess.run(cmd, cwd=video_dir)
        dt = time.time() - t0
        if r.returncode == 0:
            print(f"  {sid}: xong trong {dt:.1f}s -> {out}")
        else:
            print(f"  {sid}: FAIL sau {dt:.1f}s (mã {r.returncode})", file=sys.stderr)
            failed.append(sid)
    print(f"tổng {len(ids)} shot trong {time.time() - t_all:.1f}s"
          + (f" — FAIL: {', '.join(failed)}" if failed else ""))
    return 1 if failed else 0


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
    ap.add_argument("--shots", help="chỉ render các shot này (id cách nhau dấu phẩy), mỗi shot 1 file riêng — xem chuyển động, không kèm track giọng")
    ap.add_argument("--hyperframes-version", default=HYPERFRAMES_VERSION,
                    help=f"phiên bản HyperFrames đã ghim (mặc định {HYPERFRAMES_VERSION}); chỉ đổi khi đo so sánh phiên bản")
    ap.add_argument("--workers", default=None,
                    help="số worker render song song của HyperFrames (số hoặc 'auto'; mặc định để HyperFrames tự chọn). "
                         "Mỗi worker là 1 tiến trình Chrome (~256MB RAM). Opt round 3 mục 3: đo trên VM chỉ ~1,5 CPU — "
                         "low-memory mode (RAM ≤8GB) có thể ghim về 1 worker bất kể cờ này; đo thật rồi hãy tin.")
    args = ap.parse_args(argv)

    proj = args.project
    video_dir = args.video_dir or (proj / "video")
    if not video_dir.is_dir():
        print(f"LỖI: không có thư mục video {video_dir}", file=sys.stderr)
        return 1
    if args.shots and args.out:
        print("LỖI: --shots xung đột với --out (mỗi shot ra 1 file riêng)", file=sys.stderr)
        return 1
    if args.shots:
        return render_shots(proj, video_dir, args.shots, extra, args.hyperframes_version, args.delivery, args.workers)
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

    cmd = hf_cmd(args.hyperframes_version) + ["render", "--quality", quality, "-o", str(out)]
    if args.workers:
        cmd += ["--workers", args.workers]
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
