#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""So khớp timing giữa audio/manifest.json và project HyperFrames.

Hai layout giọng được chấp nhận (build_video.py chỉ phát 1 track giọng duy nhất,
layout clip-riêng từng line là của generator cũ):
- 1 track giọng duy nhất: <audio id="voice" src="assets/audio/voiceover.wav">
  với data-start=0, data-duration khớp thời lượng các line được phủ, file src
  tồn tại và dài đúng bằng data-duration (nếu là .wav). Layout này KHÔNG cần
  clip riêng từng line.
- clip riêng từng line: mỗi line trong manifest có một <audio id="<line_id>">
  với data-start/data-duration khớp manifest (kiểm nghiêm như cũ).

Phạm vi kiểm: chỉ các line được phủ bởi các shot có trong index.html (cửa sổ
data-start/data-duration của các <div data-composition-src>). Dựng từng phần
(--scenes/--shots/--until) chỉ kiểm các line thuộc phần đó, không đòi root
dài bằng toàn bộ manifest. Không có shot nào trong index thì kiểm toàn bộ.

Kiểm tra:
- data-duration của root composition so với thời lượng các line được phủ.
- <audio id="voice"> (nếu có): src tồn tại, data-start=0, data-duration khớp.
- Từng <audio id="..."> theo line (nếu dùng layout clip-riêng): data-start /
  data-duration khớp line trong manifest; thiếu clip của line được phủ là lỗi.
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
import wave
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


def wav_seconds(path: Path) -> float | None:
    """Thời lượng thật của file .wav (None nếu không đọc được / không phải wav)."""
    try:
        with wave.open(str(path)) as w:
            return w.getnframes() / w.getframerate()
    except Exception:
        return None


def shot_windows(html: str) -> list[tuple[float, float]]:
    """Cửa sổ (start, duration) của các shot — data-start/data-duration trên
    <div data-composition-src>, tính theo timeline (gốc 0 = đầu video dựng)."""
    wins = []
    for tag in re.findall(r"<div\b[^>]*\bdata-composition-src\b[^>]*>", html):
        start = as_float(attr(tag, "data-start"))
        dur = as_float(attr(tag, "data-duration"))
        if start is not None and dur is not None:
            wins.append((start, dur))
    return wins


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

    # audio tags: tách track giọng duy nhất, clip theo line, SFX
    found: dict[str, tuple[float | None, float | None]] = {}
    srcs: dict[str, str | None] = {}
    for tag in re.findall(r"<audio\b[^>]*>", html):
        cid = attr(tag, "id")
        if not cid:
            warnings.append("<audio> không có id nên không được mix — thêm id theo line id")
            continue
        if cid.startswith("sfx-"):
            continue  # SFX của shot, không phải giọng — không kiểm ở gate này
        found[cid] = (as_float(attr(tag, "data-start")), as_float(attr(tag, "data-duration")))
        srcs[cid] = attr(tag, "src")

    voice = found.get("voice")
    voice_src = srcs.get("voice")

    # phạm vi kiểm: các line được phủ bởi shot trong index (t0 = data-media-start của voice)
    t0 = 0.0
    if voice is not None:
        for tag in re.findall(r"<audio\b[^>]*>", html):
            if attr(tag, "id") == "voice":
                t0 = as_float(attr(tag, "data-media-start")) or 0.0
                break
    wins = shot_windows(html)
    covered: set[str] = set()
    if wins:
        for lid, line in lines.items():
            ls = float(line.get("start", 0.0))
            le = ls + float(line.get("duration", 0.0))
            if any(ls < s + d + t0 - 1e-9 and le > s + t0 + 1e-9 for s, d in wins):
                covered.add(lid)
    if not covered:
        covered = set(lines)  # không xác định được phạm vi -> kiểm toàn bộ (như cũ)
    required = max(
        (float(lines[l]["start"]) + float(lines[l]["duration"]) for l in covered),
        default=0.0,
    ) - t0

    # root data-duration
    roots = [t for t in re.findall(r"<[^>]*\bdata-composition-id\b[^>]*>", html)]
    root_durations = [as_float(attr(t, "data-duration")) for t in roots]
    root_durations = [d for d in root_durations if d is not None]
    root_duration = max(root_durations) if root_durations else None
    if root_duration is None:
        warnings.append("không tìm thấy data-duration trên composition root — HyperFrames sẽ dùng mặc định")
    elif root_duration + args.tolerance < required:
        errors.append(
            f"root data-duration={root_duration:.2f}s < {required:.2f}s (các line được phủ): video sẽ cắt mất lời"
        )
    elif root_duration > required + 1.0:
        warnings.append(
            f"root data-duration={root_duration:.2f}s dài hơn phần được phủ {root_duration - required:.2f}s (đuôi lặng)"
        )

    # layout 1 track giọng duy nhất: không cần clip riêng từng line
    if voice is not None:
        v_start, v_dur = voice
        if not voice_src:
            errors.append('track giọng <audio id="voice"> thiếu src')
        else:
            v_path = (index_path.parent / voice_src) if not Path(voice_src).is_absolute() else Path(voice_src)
            if not v_path.is_file():
                errors.append(f"track giọng trỏ tới file không tồn tại: {voice_src}")
            elif v_path.suffix.lower() == ".wav" and v_dur is not None:
                real = wav_seconds(v_path)
                if real is not None and abs(real - v_dur) > args.tolerance:
                    errors.append(
                        f"track giọng: file {voice_src} dài {real:.2f}s ≠ data-duration {v_dur:.2f}s (file giọng cũ/không khớp)"
                    )
        if v_start is None or v_dur is None:
            errors.append('track giọng <audio id="voice"> thiếu data-start/data-duration')
        else:
            if abs(v_start) > args.tolerance:
                errors.append(f"track giọng: data-start {v_start:.2f} ≠ 0 (giọng sẽ lệch khỏi timeline)")
            if v_dur + args.tolerance < required:
                errors.append(
                    f"track giọng: data-duration={v_dur:.2f}s < {required:.2f}s (các line được phủ): video sẽ cắt mất lời"
                )
            elif v_dur > required + 1.0:
                warnings.append(
                    f"track giọng: data-duration={v_dur:.2f}s dài hơn phần được phủ {v_dur - required:.2f}s (đuôi lặng)"
                )

    # audio clips (per-line): kiểm nghiêm khi dùng layout clip-riêng;
    # khi có track giọng duy nhất thì clip line (nếu có) chỉ được kiểm khớp, không bắt buộc
    matched = 0
    scene_audio_used = False
    for cid, (start, dur) in found.items():
        if cid == "voice":
            continue
        if cid in scene_ids:
            scene_audio_used = True
            continue
        if cid not in lines:
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

    if voice is None:
        missing = [lid for lid in covered if lid not in found]
        if missing:
            errors.append(f"thiếu {len(missing)} audio clip: {', '.join(missing[:6])}{'…' if len(missing) > 6 else ''}")
        if scene_audio_used and matched:
            warnings.append("đang dùng cả audio scene và audio line — kiểm tra double tiếng")
    else:
        if matched:
            warnings.append("đang dùng cả track giọng duy nhất và clip riêng từng line — kiểm tra double tiếng")
        if scene_audio_used:
            warnings.append("đang dùng cả track giọng duy nhất và audio scene — kiểm tra double tiếng")

    report = {
        "status": "ok" if not errors else "error",
        "manifest": str(manifest_path),
        "index": str(index_path),
        "manifest_duration": round(total, 2),
        "covered_duration": round(required, 2),
        "covered_lines": len(covered),
        "layout": "voice" if voice is not None else "per-line",
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
        print(f"manifest : {total:.2f}s, {len(lines)} line (phủ {len(covered)} line, {required:.2f}s)")
        print(f"root     : {root_duration:.2f}s" if root_duration is not None else "root     : ?")
        if voice is not None:
            print(f"audio    : track giọng duy nhất (voice), {voice[1]:.2f}s" if voice[1] is not None else "audio    : track giọng duy nhất (voice)")
        else:
            print(f"audio    : {len(found)} clip, {matched} khớp line")
        for w in warnings:
            print(f"  ! {w}")
        for e in errors:
            print(f"  ✗ {e}")
        print("OK" if not errors else f"FAIL ({len(errors)} lỗi)")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
