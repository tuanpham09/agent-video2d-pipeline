#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""detect_issues.py — QC mắt máy sau render (Opt round 3, mục 2).

Chạy ffmpeg blackdetect + freezedetect + silencedetect trên video đã render,
ánh xạ khoảng bị cờ vào shot (qua manifest + shotlist), rồi báo cáo.

Vấn đề nó bắt: bug nhịp 2 Thần Trùng (đen toàn bộ do <div id="fade"> che
stage) mà hyperframes check KHÔNG bắt được — chỉ QC frame bằng mắt mới thấy.
Detector này là "mắt máy" thay cho mắt người ở vòng đầu.

Ngưỡng mặc định ĐÃ ĐO trên file thật (vòng 3):
  - blackdetect d=2.0 pic_th=0.98: demo #3 final sạch (SH003 macro tối có chủ
    ý KHÔNG bị cờ — nó tối chứ không đen thuần); Thần Trùng full 34 phút:
    xem DETECTOR_BASELINE.md (đo ở vòng 3).
  - freezedetect n=0.001 d=2.0, silencedetect n=-50dB d=2.0: demo #3 sạch.
  - Khoảng lặng bình thường giữa các line ≤0,35s (luật timing) nên d=2.0 không
    cờ nhầm; shot tĩnh có lip-sync/GSAP vẫn đổi pixel nên không bị freeze.
Loại trừ shot tối có chủ ý: shotlist khai `"dark_ok": true` ở shot đó, hoặc
cờ --allow-dark SH003. Khoảng được loại trừ vẫn liệt kê, không tính là lỗi.

Vòng này detector chỉ REPORT (exit 0), không fail build — ngưỡng còn cần
theo dõi trên nhiều video. Cờ --fail-on-issue để dùng sau khi ngưỡng ổn.

Ví dụ:
  python detect_issues.py --project projects/demo-30s-than-trung
  python detect_issues.py --project projects/demo-30s-than-trung --video projects/demo-30s-than-trung/output/final.mp4 --json
  python detect_issues.py --video ~/workspace/than-trung-video/full-video/than-trung-full.mp4
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Ngưỡng mặc định — đã đo trên file thật (xem docstring). Đổi ngưỡng thì ghi
# lý do + số đo vào DETECTOR_BASELINE.md, đừng đổi lặng.
BLACK_D = 2.0
BLACK_PIC_TH = 0.98
BLACK_PIX_TH = 0.10
FREEZE_D = 2.0
FREEZE_NOISE = 0.001
SILENCE_D = 2.0
SILENCE_DB = -50

# Định dạng log thật của ffmpeg (đo 23/11, vòng 3):
#   black:  "black_start:10 black_end:13.033333 black_duration:3.033333" (1 dòng, KHÔNG có khoảng trắng sau dấu hai chấm)
#   freeze: "freeze_start: ..." rồi "freeze_end: ... | freeze_duration: ..." (2 dòng, có thể kèm tiền tố lavfi.freezedetect.)
#   silence:"silence_start: 9.754771" rồi "silence_end: 13.013333 | silence_duration: 3.258563" (2 dòng)
# → parse start/end/duration riêng rồi ghép theo thứ tự, đừng giả định 1 dòng.
def _num(pat: str):
    return re.compile(pat + r":\s*([\d.]+)")


RE_START = {
    "black": _num(r"black_start"),
    "freeze": _num(r"(?:lavfi\.freezedetect\.)?freeze_start"),
    "silence": _num(r"(?:lavfi\.silencedetect\.)?silence_start"),
}
RE_END = {
    "black": _num(r"black_end"),
    "freeze": _num(r"(?:lavfi\.freezedetect\.)?freeze_end"),
    "silence": _num(r"(?:lavfi\.silencedetect\.)?silence_end"),
}
RE_DUR = {
    "black": _num(r"black_duration"),
    "freeze": _num(r"(?:lavfi\.freezedetect\.)?freeze_duration"),
    "silence": _num(r"(?:lavfi\.silencedetect\.)?silence_duration"),
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def shot_windows(proj: Path) -> tuple[dict[str, tuple[float, float]], set[str]]:
    """Cửa sổ tuyệt đối của từng shot + tập shot dark_ok (tính như check_shots)."""
    manifest = load_json(proj / "audio" / "manifest.json")
    shotlist = load_json(proj / "script" / "shotlist.json")
    lines: dict[str, dict] = {}
    for sc in manifest["scenes"]:
        for ln in sc["lines"]:
            lines[ln["id"]] = ln
    windows: dict[str, tuple[float, float]] = {}
    dark_ok: set[str] = set()
    for shot in shotlist.get("shots", []):
        sid = shot.get("id", "?")
        lids = [lid for lid in shot.get("line_ids", []) if lid in lines]
        if not lids:
            continue
        start = min(lines[l]["start"] for l in lids)
        end = max(lines[l]["start"] + lines[l]["duration"] for l in lids)
        span = shot.get("span")
        if isinstance(span, list) and len(span) == 2:
            windows[sid] = (start + float(span[0]), start + float(span[1]))
        else:
            windows[sid] = (start, end)
        if shot.get("dark_ok"):
            dark_ok.add(sid)
    return windows, dark_ok


def find_video(proj: Path | None, explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.is_file():
            print(f"✗ video không tồn tại: {p}", file=sys.stderr)
            sys.exit(2)
        return p
    assert proj is not None
    for cand in (proj / "output" / "final.mp4", proj / "video" / "final.mp4",
                 proj / "output" / "draft.mp4", proj / "video" / "draft.mp4"):
        if cand.is_file():
            return cand
    out = proj / "output"
    if out.is_dir():
        mp4s = sorted(out.glob("*.mp4"))
        if mp4s:
            return mp4s[0]
    print(f"✗ không tìm thấy video trong {proj} (dùng --video để chỉ file)", file=sys.stderr)
    sys.exit(2)


def has_audio(video: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream=index", "-of", "csv=p=0",
                        str(video)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def video_duration(video: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(video)], capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                        "-show_entries", "stream=index", "-of", "csv=p=0",
                        str(video)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def run_ffmpeg(video: Path, audio: bool, args) -> str:
    vf = (f"blackdetect=d={args.black_d}:pic_th={args.pic_th}:pix_th={args.pix_th},"
          f"freezedetect=n={args.freeze_noise}:d={args.freeze_d}")
    cmd = ["ffmpeg", "-v", "info", "-i", str(video), "-vf", vf, "-an", "-f", "null", "-"]
    if audio:
        cmd = ["ffmpeg", "-v", "info", "-i", str(video), "-vf", vf,
               "-af", f"silencedetect=n={args.silence_db}dB:d={args.silence_d}",
               "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"✗ ffmpeg lỗi (exit {r.returncode}):\n{r.stderr[-800:]}", file=sys.stderr)
        sys.exit(2)
    return r.stderr


def map_shots(start: float, end: float, windows: dict[str, tuple[float, float]]) -> list[str]:
    """Các shot mà khoảng [start, end] chạm vào (sắp xếp theo thời gian)."""
    hits = [(w[0], sid) for sid, w in windows.items() if start < w[1] and end > w[0]]
    return [sid for _, sid in sorted(hits)]


def main() -> int:
    ap = argparse.ArgumentParser(description="QC mắt máy: black/freeze/silence trên video đã render.")
    ap.add_argument("--project", type=Path, help="project (để map shot + tìm video mặc định)")
    ap.add_argument("--video", help="file video cụ thể (mặc định: output/final.mp4 của project)")
    ap.add_argument("--black-d", type=float, default=BLACK_D, help=f"đen tối thiểu bao lâu mới cờ (mặc định {BLACK_D}s)")
    ap.add_argument("--pic-th", type=float, default=BLACK_PIC_TH)
    ap.add_argument("--pix-th", type=float, default=BLACK_PIX_TH)
    ap.add_argument("--freeze-d", type=float, default=FREEZE_D)
    ap.add_argument("--freeze-noise", type=float, default=FREEZE_NOISE)
    ap.add_argument("--silence-d", type=float, default=SILENCE_D)
    ap.add_argument("--silence-db", type=float, default=SILENCE_DB)
    ap.add_argument("--allow-dark", action="append", default=[],
                    help="shot tối có chủ ý, được miễn cờ đen (dùng lại được nhiều lần); shotlist cũng nhận \"dark_ok\": true")
    ap.add_argument("--json", action="store_true", help="in kết quả dạng JSON")
    ap.add_argument("--fail-on-issue", action="store_true",
                    help="exit 1 nếu còn lỗi (mặc định chỉ báo cáo, exit 0)")
    args = ap.parse_args()

    if not args.project and not args.video:
        ap.error("cần --project hoặc --video")
    video = find_video(args.project, args.video)

    windows: dict[str, tuple[float, float]] = {}
    dark_ok: set[str] = set()
    if args.project:
        try:
            windows, dark_ok = shot_windows(args.project)
        except (OSError, ValueError, KeyError) as exc:
            print(f"! không map được shot (thiếu manifest/shotlist): {exc} — vẫn chạy detector, không gắn shot",
                  file=sys.stderr)
    dark_ok |= set(args.allow_dark)

    audio = has_audio(video)
    dur_total = video_duration(video)
    log = run_ffmpeg(video, audio, args)

    issues: list[dict] = []
    for kind, label in (("black", "đen"), ("freeze", "đứng hình"), ("silence", "câm")):
        starts = [float(x) for x in RE_START[kind].findall(log)]
        ends = [float(x) for x in RE_END[kind].findall(log)]
        durs = [float(x) for x in RE_DUR[kind].findall(log)]
        if not (len(starts) == len(ends) == len(durs)):
            print(f"! {kind}: log ffmpeg lệch start/end/duration ({len(starts)}/{len(ends)}/{len(durs)}) — bỏ qua loại này",
                  file=sys.stderr)
            continue
        for start, end, dur in zip(starts, ends, durs):
            shots = map_shots(start, end, windows)
            allowed = kind == "black" and any(s in dark_ok for s in shots)
            # Đuôi câm cuối video (giọng hết trước khi hình hết) là bình thường —
            # Thần Trùng full có 2,78s câm ở 2037,95–2040,73s (cuối video 2040,73s).
            tail = kind == "silence" and dur_total > 0 and end >= dur_total - 0.5
            issues.append({
                "type": kind, "label": label, "start": round(start, 2),
                "end": round(end, 2), "duration": round(dur, 2),
                "shots": shots, "allowed": allowed or tail,
                "note": "đuôi video" if tail else "",
            })
    real = [i for i in issues if not i["allowed"]]
    allowed_list = [i for i in issues if i["allowed"]]

    if args.json:
        print(json.dumps({"video": str(video), "duration_checked": True,
                          "issues": issues, "real_issues": len(real),
                          "allowed": len(allowed_list), "has_audio": audio},
                         ensure_ascii=False, indent=2))
    else:
        print(f"video: {video}" + ("" if audio else " (không có track audio — bỏ qua silencedetect)"))
        if not issues:
            print("✓ sạch: không có khoảng đen/đứng hình/câm nào ≥ ngưỡng")
        else:
            for i in issues:
                tag = "cho phép (dark_ok)" if i["allowed"] and i["type"] == "black" else \
                      "cho phép (đuôi video)" if i["allowed"] else "LỖI"
                shots = ", ".join(i["shots"]) or "không gắn được shot"
                print(f"[{tag}] {i['label']} {i['start']:.2f}–{i['end']:.2f}s ({i['duration']:.2f}s) — shot: {shots}")
            print(f"tổng: {len(real)} lỗi, {len(allowed_list)} khoảng được miễn (dark_ok/đuôi video)")
    return 1 if (args.fail_on_issue and real) else 0


if __name__ == "__main__":
    sys.exit(main())
