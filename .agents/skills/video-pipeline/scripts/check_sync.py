#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""So khớp timing giữa audio/manifest.json và project HyperFrames.

Kiểm tra:
- data-duration của root composition so với tổng thời lượng manifest.
- Từng <audio id="..."> có data-start / data-duration khớp line trong manifest.
- Cảnh báo khi vừa dùng audio theo scene vừa dùng theo line (double tiếng).

Dùng:
  python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/my-video
  python ... --project projects/my-video --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOLERANCE = 0.05  # giây


def attr(tag: str, name: str) -> str | None:
    m = re.search(rf'\b{name}\s*=\s*"([^"]*)"', tag) or re.search(rf"\b{name}\s*=\s*'([^']*)'", tag)
    return m.group(1) if m else None


def as_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(str(value).strip().rstrip("s"))
    except ValueError:
        return None


def load_manifest(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    if "scenes" not in data:
        raise ValueError("manifest.json thiếu 'scenes' — chạy build_voiceover.py trước.")
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm tra đồng bộ manifest ↔ HyperFrames.")
    ap.add_argument("--project", type=Path, help="thư mục project (có audio/manifest.json và video/index.html)")
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--index", type=Path)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--tolerance", type=float, default=TOLERANCE)
    args = ap.parse_args()

    project = args.project
    manifest_path = args.manifest or (project / "audio" / "manifest.json" if project else None)
    index_path = args.index or (project / "video" / "index.html" if project else None)
    if not manifest_path or not index_path:
        ap.error("cần --project, hoặc cả --manifest và --index")
    if not manifest_path.exists():
        print(f"LỖI: không thấy {manifest_path}", file=sys.stderr)
        return 1
    if not index_path.exists():
        print(f"LỖI: không thấy {index_path}", file=sys.stderr)
        return 1

    manifest = load_manifest(manifest_path)
    html = index_path.read_text(encoding="utf-8", errors="replace")

    errors: list[str] = []
    warnings: list[str] = []
    lines: dict[str, dict] = {}
    scene_ids: set[str] = set()
    for scene in manifest.get("scenes", []):
        scene_ids.add(scene.get("id", ""))
        for line in scene.get("lines", []):
            lines[line["id"]] = line

    total = float(manifest.get("duration") or 0.0)

    # root data-duration
    roots = [t for t in re.findall(r"<[^>]*\bdata-composition-id\b[^>]*>", html)]
    root_durations = [as_float(attr(t, "data-duration")) for t in roots]
    root_durations = [d for d in root_durations if d is not None]
    root_duration = max(root_durations) if root_durations else None
    if root_duration is None:
        warnings.append("không tìm thấy data-duration trên composition root — HyperFrames sẽ dùng mặc định")
    elif root_duration + args.tolerance < total:
        errors.append(
            f"root data-duration={root_duration:.2f}s < manifest={total:.2f}s: video sẽ cắt mất lời"
        )
    elif root_duration > total + 1.0:
        warnings.append(
            f"root data-duration={root_duration:.2f}s dài hơn manifest {root_duration - total:.2f}s (đuôi lặng)"
        )

    # audio clips
    found: dict[str, tuple[float | None, float | None]] = {}
    for tag in re.findall(r"<audio\b[^>]*>", html):
        cid = attr(tag, "id")
        if not cid:
            warnings.append("<audio> không có id nên không được mix — thêm id theo line id")
            continue
        found[cid] = (as_float(attr(tag, "data-start")), as_float(attr(tag, "data-duration")))

    matched = 0
    scene_audio_used = False
    for cid, (start, dur) in found.items():
        if cid in scene_ids:
            scene_audio_used = True
        if cid not in lines:
            if cid in scene_ids:
                continue
            warnings.append(f"<audio id={cid} src=...> không có trong manifest")
            continue
        line = lines[cid]
        matched += 1
        exp_start = float(line.get("start", 0.0))
        exp_dur = float(line.get("duration", 0.0))
        if start is None or dur is None:
            errors.append(f"{cid}: thiếu data-start/data-duration")
            continue
        if abs(start - exp_start) > args.tolerance:
            errors.append(f"{cid}: start {start:.2f} ≠ manifest {exp_start:.2f}")
        if abs(dur - exp_dur) > args.tolerance:
            errors.append(f"{cid}: duration {dur:.2f} ≠ manifest {exp_dur:.2f}")

    missing = [lid for lid in lines if lid not in found]
    if missing:
        errors.append(f"thiếu {len(missing)} audio clip: {', '.join(missing[:6])}{'…' if len(missing) > 6 else ''}")
    if scene_audio_used and matched:
        warnings.append("đang dùng cả audio scene và audio line — kiểm tra double tiếng")

    report = {
        "status": "ok" if not errors else "error",
        "manifest": str(manifest_path),
        "index": str(index_path),
        "manifest_duration": round(total, 2),
        "root_duration": round(root_duration, 2) if root_duration is not None else None,
        "lines": len(lines),
        "audio_clips": len(found),
        "matched": matched,
        "errors": errors,
        "warnings": warnings,
    }

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"manifest : {total:.2f}s, {len(lines)} line")
        print(f"root     : {root_duration:.2f}s" if root_duration is not None else "root     : ?")
        print(f"audio    : {len(found)} clip, {matched} khớp line")
        for w in warnings:
            print(f"  ! {w}")
        for e in errors:
            print(f"  ✗ {e}")
        print("OK" if not errors else f"FAIL ({len(errors)} lỗi)")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
