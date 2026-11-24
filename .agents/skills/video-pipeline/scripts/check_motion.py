#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate chuyển động của composition đã sinh (motion_plan.json).

Đọc:
  video/motion_plan.json   (build_video.py xuất cạnh HTML; ops đã tính sẵn)
  script/shotlist.json     (tuỳ chọn, để đối chiếu beat vật lý)

Kiểm:
  M1  plan có shots, mỗi shot có duration > 0 và frame hợp lệ
  M2  op nằm trong shot: at ≥ 0, at + dur ≤ duration (+0.12 cho mouth), không `repeat` vô hạn
  M3  selector của op thuộc đúng shot (không rò sang shot khác)
  M4  mỗi nhân vật không "đứng chết" quá --max-gap giây (mặc định 0.6 s)
  M5  mỗi beat vật lý có gesture thật: op bắt đầu đúng t, nhắm đúng rig, kéo dài ≥ 0.12 s
  M6  path đi lại: 0 ≤ t0 < t1 ≤ duration; số footstep = số nửa chu kỳ; gait=float thì 0 footstep
  M7  mật độ gesture (cảnh báo nếu < 4 cử chỉ / 10 s) và đa dạng cỡ cảnh (< 3 cỡ = cảnh báo)

Dùng:
  python .agents/skills/video-pipeline/scripts/check_motion.py --project projects/<slug>
  python ... --project projects/<slug> --plan video/demo/motion_plan.json
  python ... --project projects/<slug> --max-gap 0.6 --json
Mã thoát: 0 = qua gate, 1 = có lỗi.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EPS = 0.05
END_TOLERANCE = 0.12
GESTURE_MIN_DUR = 0.12
GESTURE_DENSITY = 4.0  # số cử chỉ / 10 giây


def load(path: Path) -> dict:
    if not path.is_file():
        sys.exit(f"LỖI: thiếu {path} — chạy build_video.py trước khi gate chuyển động")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def op_interval(item: dict) -> tuple[float, float]:
    at = float(item.get("at", 0.0))
    return at, at + max(0.0, float(item.get("dur", 0.0)))


def coverage_gaps(ops: list[dict], duration: float) -> list[tuple[float, float]]:
    """Khoảng trống (giây) giữa các op đã hợp nhất, tính cả đầu và cuối shot."""
    spans = sorted(op_interval(item) for item in ops if float(item.get("dur", 0.0)) > 0)
    gaps: list[tuple[float, float]] = []
    cursor = 0.0
    for start, end in spans:
        if start > cursor + EPS:
            gaps.append((round(cursor, 4), round(start, 4)))
        cursor = max(cursor, end)
    if duration > cursor + EPS:
        gaps.append((round(cursor, 4), round(duration, 4)))
    return gaps


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate chuyển động từ motion_plan.json.")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--plan", type=Path, help="mặc định <project>/video/motion_plan.json")
    ap.add_argument("--shotlist", type=Path, help="tuỳ chọn: đối chiếu beat vật lý với shotlist")
    ap.add_argument("--max-gap", type=float, default=0.6)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    project = args.project
    plan_path = args.plan or (project / "video" / "motion_plan.json")
    if not plan_path.is_absolute():
        plan_path = project / plan_path
    plan = load(plan_path)
    shots = plan.get("shots") or []
    errors: list[str] = []
    warnings: list[str] = []
    if not shots:
        sys.exit(f"LỖI: {plan_path} không có shots")

    if args.shotlist:
        shotlist_path = args.shotlist if args.shotlist.is_absolute() else project / args.shotlist
        source = load(shotlist_path)
        source_shots = source.get("shots") or []
        if len(source_shots) != len(shots):
            errors.append(f"shotlist có {len(source_shots)} shot nhưng plan có {len(shots)} — plan đã cũ, build lại")
        source_beats = sum(1 for shot in source_shots for beat in shot.get("beats", []) if beat.get("physical"))
        plan_beats = sum(len(shot.get("physical_beats") or []) for shot in shots)
        if source_beats != plan_beats:
            errors.append(f"shotlist có {source_beats} beat vật lý nhưng plan có {plan_beats} — build lại")

    gesture_total = 0
    sizes: set[str] = set()
    max_gap_seen = 0.0
    footstep_total = 0
    for shot in shots:
        sid = str(shot.get("shot") or "?")
        duration = float(shot.get("duration", 0.0))
        if duration <= EPS:
            errors.append(f"{sid}: duration ≤ 0")
            continue
        frame = shot.get("frame") or {}
        if float(frame.get("scale", 0) or 0) <= 0:
            errors.append(f"{sid}: frame.scale phải > 0")
        sizes.add(str(frame.get("size") or "?"))
        prefix = f"#{sid}"
        chars = shot.get("characters") or []
        if not chars:
            errors.append(f"{sid}: không có nhân vật nào trong motion plan")

        # M2/M3: op hợp lệ và thuộc shot
        for ch in chars:
            for item in ch.get("ops") or []:
                sel = str(item.get("sel") or "")
                at, end = op_interval(item)
                if not sel.startswith(prefix):
                    errors.append(f"{sid}: op '{sel}' không thuộc shot này (phải bắt đầu bằng '{prefix}')")
                if "repeat" in item:
                    errors.append(f"{sid}: op '{sel}' có `repeat` — không cho phép lặp vô hạn trong plan")
                if at < -EPS:
                    errors.append(f"{sid}: op '{sel}' bắt đầu ở {at:.2f}s < 0")
                if end > duration + END_TOLERANCE:
                    errors.append(f"{sid}: op '{sel}' kết thúc ở {end:.2f}s, vượt shot {duration:.2f}s")
                if float(item.get("dur", 0.0)) <= 0:
                    errors.append(f"{sid}: op '{sel}' có dur ≤ 0")

            # M4: không đứng chết
            gaps = coverage_gaps(ch.get("ops") or [], duration)
            for start, end in gaps:
                span = end - start
                max_gap_seen = max(max_gap_seen, span)
                if span > args.max_gap + EPS:
                    errors.append(
                        f"{sid}: {ch.get('id')} đứng yên {span:.2f}s ({start:.2f}–{end:.2f}), "
                        f"quá --max-gap {args.max_gap:.2f}s"
                    )

        # M5: beat vật lý phải có gesture thật
        by_id = {str(ch.get("id")): ch for ch in chars}
        for beat in shot.get("physical_beats") or []:
            t = float(beat.get("t", 0.0))
            name = str(beat.get("gesture") or "")
            target = str(beat.get("target") or "")
            if not name:
                errors.append(f"{sid}: beat vật lý t={t:.2f}s thiếu gesture trong plan")
                continue
            ch = by_id.get(target)
            if ch is None:
                errors.append(f"{sid}: gesture '{name}' nhắm '{target}' nhưng nhân vật không có trong shot")
                continue
            rig_prefix = f"{prefix}-rig-{ch.get('index')}"
            hit = any(
                str(item.get("sel", "")).startswith(rig_prefix)
                and abs(float(item.get("at", -9)) - t) <= 0.03
                and float(item.get("dur", 0.0)) >= GESTURE_MIN_DUR
                for item in ch.get("ops") or []
            )
            if not hit:
                errors.append(f"{sid}: beat vật lý t={t:.2f}s khai gesture '{name}' nhưng không có op tương ứng")

        # M6: path + footstep
        for ch in chars:
            path = ch.get("path")
            if not path:
                continue
            t0, t1 = float(path.get("t0", 0.0)), float(path.get("t1", 0.0))
            if not (0.0 <= t0 < t1 <= duration + EPS):
                errors.append(f"{sid}: path {ch.get('id')} cần 0 ≤ t0 < t1 ≤ {duration:.2f}s (đang {t0}–{t1})")
            period = float(ch.get("walk_period") or 1.0)
            steps = [float(v) for v in (ch.get("footsteps") or [])]
            footstep_total += len(steps)
            if str(ch.get("gait") or "walk") == "float":
                if steps:
                    errors.append(f"{sid}: {ch.get('id')} gait=float nhưng có {len(steps)} footstep")
            else:
                expected = math.ceil((t1 - t0) / (period / 2) - 1e-9) if t1 > t0 else 0
                if len(steps) != expected:
                    errors.append(
                        f"{sid}: {ch.get('id')} có {len(steps)} footstep, cần {expected} "
                        f"({t1 - t0:.2f}s / nửa chu kỳ {period / 2:.2f}s)"
                    )
                for t in steps:
                    if not (t0 - EPS <= t <= t1 + EPS):
                        errors.append(f"{sid}: footstep {ch.get('id')} t={t:.2f} ngoài path {t0:.2f}–{t1:.2f}")

        gesture_total += len(shot.get("gestures") or [])

    total = float(plan.get("duration", 0.0) or 0.0)
    density = (gesture_total / total * 10.0) if total > 0 else 0.0
    if density < GESTURE_DENSITY:
        warnings.append(f"mật độ gesture {density:.1f}/10s < {GESTURE_DENSITY:.0f}/10s")
    if len(sizes) < 3:
        warnings.append(f"chỉ có {len(sizes)} cỡ cảnh ({', '.join(sorted(sizes))}) — cần ≥ 3 cỡ để hình không đơn điệu")

    report = {
        "status": "ok" if not errors else "error",
        "plan": str(plan_path),
        "shots": len(shots),
        "duration": round(total, 4),
        "gestures": gesture_total,
        "gesture_density_10s": round(density, 2),
        "footsteps": footstep_total,
        "sizes": sorted(sizes),
        "max_static_gap_s": round(max_gap_seen, 3),
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"plan     : {len(shots)} shot, {total:.2f}s | cỡ {', '.join(sorted(sizes))}")
        print(f"chuyển động: {gesture_total} gesture ({density:.1f}/10s), {footstep_total} footstep, "
              f"gap tĩnh lớn nhất {max_gap_seen:.2f}s")
        for warning in warnings:
            print(f"  ! {warning}")
        for error in errors:
            print(f"  LỖI: {error}")
        print("OK" if not errors else f"FAIL: {len(errors)} lỗi")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
