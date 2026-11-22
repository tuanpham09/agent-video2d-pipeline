#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chạy các gate song song (Opt round 2, mục 2).

Các gate Python (check_rules / check_shots / check_sync, mỗi cái <2s) chạy cùng
lúc với hyperframes lint + check (~31s, chủ yếu khởi động Chrome) thay vì nối
tiếp nhau. Tiết kiệm ~30s mỗi lần chạy gate (đo thật ở demo #3).

Dùng (từ gốc repo):
  python .agents/skills/video-pipeline/scripts/gates.py --project projects/<slug>
  python .agents/skills/video-pipeline/scripts/gates.py --project projects/<slug> --phase demo --scenes S01
  python .agents/skills/video-pipeline/scripts/gates.py --project projects/<slug> --skip-hyperframes

Mỗi gate chạy trong worker riêng; kết quả gộp thành bảng, mã thoát 1 nếu gate
nào fail (kèm đuôi output để thấy lỗi). lint + check chạy nối tiếp nhau trong
cùng 1 worker vì cả hai đều dùng Chrome.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO = SCRIPTS.parents[3]


def run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout + r.stderr).strip()


def gate_rules(proj: Path, phase: str) -> tuple[str, int, str]:
    code, out = run([sys.executable, str(SCRIPTS / "check_rules.py"),
                     "--project", str(proj), "--phase", phase], cwd=REPO)
    return "check_rules", code, out


def gate_shots(proj: Path, scenes: str | None) -> tuple[str, int, str]:
    cmd = [sys.executable, str(SCRIPTS / "check_shots.py"), "--project", str(proj)]
    if scenes:
        cmd += ["--scenes", scenes]
    code, out = run(cmd, cwd=REPO)
    return "check_shots", code, out


def gate_sync(proj: Path) -> tuple[str, int, str]:
    code, out = run([sys.executable, str(SCRIPTS / "check_sync.py"),
                     "--project", str(proj)], cwd=REPO)
    return "check_sync", code, out


def gate_hyperframes(proj: Path) -> tuple[str, int, str]:
    video = proj / "video"
    if not video.is_dir():
        return "hyperframes", 1, f"thiếu thư mục video {video} — chưa dựng (build_video.py)"
    code1, out1 = run(["npx", "hyperframes", "lint"], cwd=video)
    if code1 != 0:
        return "hyperframes", code1, "[lint]\n" + out1
    code2, out2 = run(["npx", "hyperframes", "check", "--json"], cwd=video)
    return "hyperframes", code2, "[lint]\n" + out1 + "\n[check]\n" + out2


def tail(text: str, lines: int = 12) -> str:
    rows = [ln for ln in text.splitlines() if ln.strip()]
    return "\n".join(rows[-lines:]) if rows else "(không có output)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Chạy các gate song song (rules/shots/sync + hyperframes).")
    ap.add_argument("--project", type=Path, required=True, help="thư mục project, vd projects/<slug>")
    ap.add_argument("--phase", default="demo", choices=["demo", "full", "final"],
                    help="phase cho check_rules (mặc định demo)")
    ap.add_argument("--scenes", help="chỉ kiểm các scene này (check_shots --scenes)")
    ap.add_argument("--skip-hyperframes", action="store_true",
                    help="bỏ qua lint/check (chỉ chạy 3 gate Python)")
    args = ap.parse_args()

    proj = args.project
    jobs = [
        lambda: gate_rules(proj, args.phase),
        lambda: gate_shots(proj, args.scenes),
        lambda: gate_sync(proj),
    ]
    if not args.skip_hyperframes:
        jobs.append(lambda: gate_hyperframes(proj))

    t0 = time.time()
    results: dict[str, tuple[int, str, float]] = {}
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futs = {pool.submit(j): j for j in jobs}
        for fut in as_completed(futs):
            t1 = time.time()
            name, code, out = fut.result()
            results[name] = (code, out, t1 - t0)
    total = time.time() - t0

    print(f"gates ({len(jobs)} gate song song): {total:.1f}s")
    failed: list[str] = []
    for name in ("check_rules", "check_shots", "check_sync", "hyperframes"):
        if name not in results:
            continue
        code, out, _ = results[name]
        mark = "OK  " if code == 0 else "FAIL"
        print(f"  [{mark}] {name} (mã {code})")
        if code != 0:
            failed.append(name)
            print("    " + tail(out).replace("\n", "\n    "))
    if failed:
        print(f"FAIL ({len(failed)} gate): {', '.join(failed)}")
        return 1
    print("OK — tất cả gate đều qua")
    return 0


if __name__ == "__main__":
    sys.exit(main())
