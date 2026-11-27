#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chạy các gate song song (Opt round 2, mục 2).

Các gate Python (check_rules / check_shots / check_sync, mỗi cái <2s) chạy cùng
lúc với hyperframes lint + check (~31s, chủ yếu khởi động Chrome) thay vì nối
tiếp nhau. Đo thật (vòng 2, demo #3): Chrome ấm tiết kiệm chỉ ~1,7s so với nối
tiếp — giá trị chính là 1 lệnh duy nhất + báo cáo gộp, KHÔNG phải ~30s như ước
tính ban đầu (số đó đo lúc Chrome lạnh). Phiên bản HyperFrames đã ghim
(HYPERFRAMES_VERSION = 0.9.82, Opt round 3 mục 0) để số đo so sánh được.

Dùng (từ gốc repo):
  python .agents/skills/video-pipeline/scripts/gates.py --project projects/<slug>
  python .agents/skills/video-pipeline/scripts/gates.py --project projects/<slug> --phase demo --scenes S01
  python .agents/skills/video-pipeline/scripts/gates.py --project projects/<slug> --skip-hyperframes

Mỗi gate chạy trong worker riêng; kết quả gộp thành bảng, mã thoát 1 nếu gate
nào fail (kèm đuôi output để thấy lỗi). lint + check chạy nối tiếp nhau trong
cùng 1 worker vì cả hai đều dùng Chrome.

--auto-skip (Opt round 3, backlog): bỏ bước hyperframes khi diff chỉ chạm file
.py/.md — tiết kiệm ~38s mỗi lần gate lạnh (Chrome khởi động ~38s), ~7s khi
Chrome ấm. Cờ này KHÔNG mặc định bật, chỉ dùng khi lặp sửa script Python và
chạy gates nhiều lần mà không rebuild. An toàn vì 2 lớp chắn:
  1. git status --porcelain (bỏ qua projects/ — thư mục demo không commit bao
     giờ) chỉ còn file .py/.md, và
  2. không file nào trong <project>/video/ mới hơn lần sửa .py/.md gần nhất
     (rebuild sau khi sửa script sẽ viết lại index.html/compositions → mtime
     mới hơn → vẫn chạy hyperframes, không bỏ lọt lần lint đầu sau rebuild).
Nghi ngờ chỗ nào thì vẫn chạy hyperframes như thường.
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

# Opt round 3, mục 0: ghim phiên bản HyperFrames (xem render.py — cùng lý do).
HYPERFRAMES_VERSION = "0.9.82"


def hf_cmd(version: str = HYPERFRAMES_VERSION) -> list[str]:
    """Lệnh gọi HyperFrames đã ghim phiên bản (tránh npx trôi nổi)."""
    return ["npx", "--yes", f"hyperframes@{version}"]


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


def gate_script(proj: Path, scenes: str | None, phase: str) -> tuple[str, int, str]:
    """Logic & liền mạch kịch bản (check_script_logic.py). Demo: cảnh thiếu setting chỉ cảnh báo; full/final: --strict."""
    cmd = [sys.executable, str(SCRIPTS / "check_script_logic.py"), "--project", str(proj)]
    if scenes:
        cmd += ["--scenes", scenes]
    if phase in ("full", "final"):
        cmd.append("--strict")
    code, out = run(cmd, cwd=REPO)
    return "check_script_logic", code, out


def gate_sync(proj: Path) -> tuple[str, int, str]:
    code, out = run([sys.executable, str(SCRIPTS / "check_sync.py"),
                     "--project", str(proj)], cwd=REPO)
    return "check_sync", code, out


def only_py_md_changed(repo: Path) -> tuple[bool, str]:
    """(True, lý do) nếu diff chỉ chạm file .py/.md — đủ điều kiện bỏ hyperframes.

    Bỏ qua thư mục projects/ (demo không commit bao giờ, luôn bẩn). Khi nghi
    ngờ (không phải git repo, git lỗi, có file khác .py/.md) trả False để vẫn
    chạy hyperframes như thường.
    """
    r = subprocess.run(["git", "status", "--porcelain"], cwd=repo,
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, "không đọc được git status"
    changed: list[str] = []
    for line in r.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if " -> " in path:  # rename: lấy đường dẫn mới
            path = path.split(" -> ", 1)[1]
        path = path.strip('"')
        if path.startswith("projects/"):
            continue
        changed.append(path)
    if not changed:
        return True, "cây git sạch (không đổi gì ngoài projects/)"
    others = [p for p in changed if not p.endswith((".py", ".md"))]
    if others:
        return False, f"có file khác .py/.md đổi: {', '.join(others[:3])}"
    return True, f"chỉ {len(changed)} file .py/.md đổi"


def video_newer_than_code(proj: Path, repo: Path) -> bool:
    """True nếu file nào đó trong <project>/video/ mới hơn mọi file .py/.md
    trong repo — tức project vừa được rebuild sau lần sửa script gần nhất,
    lần lint đầu sau rebuild KHÔNG được bỏ."""
    video = proj / "video"
    if not video.is_dir():
        return False
    # Chỉ xét code sinh ra video/ (scripts + docs của skill), không quét cả repo.
    newest_code = 0.0
    for pat in (".agents/**/*.py", ".agents/**/*.md", "*.md"):
        for p in repo.glob(pat):
            try:
                newest_code = max(newest_code, p.stat().st_mtime)
            except OSError:
                pass
    for p in video.rglob("*"):
        if p.is_file():
            try:
                if p.stat().st_mtime > newest_code:
                    return True
            except OSError:
                pass
    return False


def gate_hyperframes(proj: Path, hf_version: str = HYPERFRAMES_VERSION) -> tuple[str, int, str]:
    video = proj / "video"
    if not video.is_dir():
        return "hyperframes", 1, f"thiếu thư mục video {video} — chưa dựng (build_video.py)"
    code1, out1 = run(hf_cmd(hf_version) + ["lint"], cwd=video)
    if code1 != 0:
        return "hyperframes", code1, "[lint]\n" + out1
    code2, out2 = run(hf_cmd(hf_version) + ["check", "--json"], cwd=video)
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
    ap.add_argument("--auto-skip", action="store_true",
                    help="tự bỏ hyperframes khi diff chỉ chạm .py/.md và video/ không mới hơn code "
                         "(lặp sửa script; chạy gates đầy đủ 1 lần ngay sau mỗi rebuild)")
    ap.add_argument("--hyperframes-version", default=HYPERFRAMES_VERSION,
                    help=f"phiên bản HyperFrames đã ghim (mặc định {HYPERFRAMES_VERSION})")
    ap.add_argument("--repo", type=Path, default=REPO,
                    help="gốc repo (mặc định từ vị trí script; chỉ dùng để test --auto-skip)")
    args = ap.parse_args()

    proj = args.project
    jobs = [
        lambda: gate_rules(proj, args.phase),
        lambda: gate_shots(proj, args.scenes),
        lambda: gate_script(proj, args.scenes, args.phase),
        lambda: gate_sync(proj),
    ]
    hf_skipped = ""
    if not args.skip_hyperframes:
        if args.auto_skip:
            ok_skip, why = only_py_md_changed(args.repo)
            if ok_skip and not video_newer_than_code(proj, args.repo):
                hf_skipped = f"bỏ hyperframes (--auto-skip: {why}; video/ không mới hơn code)"
            elif ok_skip:
                print("! --auto-skip: video/ mới hơn code (vừa rebuild?) — vẫn chạy hyperframes",
                      file=sys.stderr)
                jobs.append(lambda: gate_hyperframes(proj, args.hyperframes_version))
            else:
                print(f"! --auto-skip: {why} — vẫn chạy hyperframes", file=sys.stderr)
                jobs.append(lambda: gate_hyperframes(proj, args.hyperframes_version))
        else:
            jobs.append(lambda: gate_hyperframes(proj, args.hyperframes_version))

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
    for name in ("check_rules", "check_shots", "check_script_logic", "check_sync", "hyperframes"):
        if name not in results:
            continue
        code, out, _ = results[name]
        mark = "OK  " if code == 0 else "FAIL"
        print(f"  [{mark}] {name} (mã {code})")
        if code != 0:
            failed.append(name)
            print("    " + tail(out).replace("\n", "\n    "))
    if hf_skipped:
        print(f"  [SKIP] hyperframes — {hf_skipped}")
    if failed:
        print(f"FAIL ({len(failed)} gate): {', '.join(failed)}")
        return 1
    print("OK — tất cả gate đều qua")
    return 0


if __name__ == "__main__":
    sys.exit(main())
