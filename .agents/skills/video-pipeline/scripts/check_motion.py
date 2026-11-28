#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate chuyển động của video đã dựng (motion_plan.json, version 2).

`build_video.py` xuất `motion_plan.json` cạnh `index.html` (mặc định `projects/<slug>/video_demo/`). Plan chỉ ghi các thao tác
TƯỜNG MINH lấy từ beat đã bung macro: move/reach/hand_over có độ dài; set/look/react là sự kiện tức thời (dur 0). Hơi thở, chớp mắt,
quay mắt và gật tự động do generator thêm KHÔNG nằm trong plan (nên không dùng để đo "đứng yên").

Kiểm:
  M1  plan version 2, có shot; mỗi shot duration > 0 và có cỡ cảnh (size)
  M2  thao tác nằm trong shot: at ≥ 0 và at + dur ≤ duration + 0.12 (bắt lỗi move/reach/hand_over bị CẮT ở cuối shot)
  M3  thao tác thuộc nhân vật có mặt trong shot; shot ≥ 2 nhân vật thì mỗi người ≥ 1 thao tác (khớp R11.1 / E7)
  M5  beat vật lý có hành động thật: beat nhắm một nhân vật phải có thao tác của người đó tại t (±0.03 s);
      beat đổi state đạo cụ (prop) thì tính là hợp lệ (E6 lo SFX)
  M6  đường đi (move): 0 ≤ t0 < t1 ≤ duration + 0.12
  M7  cảnh báo: mật độ thao tác tường minh < 3 / 10 s; < 3 cỡ cảnh khác nhau

Không kiểm (chưa có dữ liệu): footstep âm thanh (generator chưa tự thêm SFX bước chân), mượt chuyển động giữa khung hình.

Dùng:
  python .agents/skills/video-pipeline/scripts/check_motion.py --project projects/<slug>
  python ... --project projects/<slug> --plan projects/<slug>/video_demo/motion_plan.json [--json]
Mã thoát: 0 = qua gate, 1 = có lỗi.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

EPS = 0.05
END_TOLERANCE = 0.12
MATCH_TOL = 0.03
DENSITY_MIN = 3.0  # thao tác tường minh / 10 giây


def load(path: Path) -> dict:
    if not path.is_file():
        sys.exit(f"LỖI: thiếu {path} — chạy build_video.py trước khi gate chuyển động")
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate chuyển động từ motion_plan.json (version 2).")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--plan", type=Path, help="mặc định <project>/video_demo/motion_plan.json")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    plan_path = args.plan or (args.project / "video_demo" / "motion_plan.json")
    plan = load(plan_path)
    errors: list[str] = []
    warnings: list[str] = []
    if plan.get("version") != 2:
        sys.exit(f"LỖI: {plan_path} không phải motion plan version 2 (do build_video.py mới xuất) — dựng lại video")
    shots = plan.get("shots") or []
    if not shots:
        sys.exit(f"LỖI: {plan_path} không có shots")

    ops_total, sizes = 0, set()
    for shot in shots:
        sid = str(shot.get("shot") or "?")
        duration = float(shot.get("duration", 0.0))
        if duration <= EPS:
            errors.append(f"{sid}: duration ≤ 0")
            continue
        if not shot.get("size"):
            errors.append(f"{sid}: thiếu size (cỡ cảnh)")
        sizes.add(str(shot.get("size") or "?"))
        chars = shot.get("characters") or []
        by_id = {str(c.get("id")): c for c in chars}

        for c in chars:
            cid = c.get("id")
            for op in c.get("ops") or []:
                at, d = float(op.get("at", 0.0)), float(op.get("dur", 0.0))
                ops_total += 1
                if at < -EPS:
                    errors.append(f"{sid}: {cid} {op.get('kind')} bắt đầu ở {at:.2f}s < 0")
                if at + d > duration + END_TOLERANCE:
                    errors.append(f"{sid}: {cid} {op.get('kind')} {at:.2f}→{at + d:.2f}s vượt hết shot ({duration:.2f}s) — bị cắt; rút dur/hold hoặc đặt sớm hơn")
            path = c.get("path")
            if path:
                t0, t1 = float(path.get("t0", 0.0)), float(path.get("t1", 0.0))
                if not (-EPS <= t0 < t1 <= duration + END_TOLERANCE):
                    errors.append(f"{sid}: đường đi của {cid} cần 0 ≤ t0 < t1 ≤ {duration:.2f}s (đang {t0}–{t1})")
        if len(chars) >= 2:
            for c in chars:
                if not (c.get("ops") or []):
                    errors.append(f"{sid}: {c.get('id')} không có thao tác tường minh nào dù shot có ≥ 2 nhân vật (R11.1)")

        for pb in shot.get("physical_beats") or []:
            t, tgt = float(pb.get("t", 0.0)), pb.get("target")
            if tgt:
                ch = by_id.get(str(tgt))
                if ch is None:
                    errors.append(f"{sid}: beat vật lý t={t:.2f}s nhắm '{tgt}' nhưng nhân vật không có trong shot")
                elif not any(abs(float(o.get("at", -9)) - t) <= MATCH_TOL for o in ch.get("ops") or []):
                    errors.append(f"{sid}: beat vật lý t={t:.2f}s ('{pb.get('do', '')[:30]}') không có thao tác của {tgt} tại thời điểm đó")
            elif not pb.get("prop"):
                errors.append(f"{sid}: beat vật lý t={t:.2f}s ('{pb.get('do', '')[:30]}') không gắn nhân vật hay đạo cụ nào — không ai thấy gì")

    total = float(plan.get("duration", 0.0) or 0.0)
    density = (ops_total / total * 10.0) if total > 0 else 0.0
    if density < DENSITY_MIN:
        warnings.append(f"mật độ thao tác tường minh {density:.1f}/10s < {DENSITY_MIN:.0f}/10s (chưa tính hơi thở/chớp/gật tự động)")
    if len(sizes) < 3:
        warnings.append(f"chỉ có {len(sizes)} cỡ cảnh ({', '.join(sorted(sizes))}) — cần ≥ 3 cỡ để hình không đơn điệu")

    report = {"status": "ok" if not errors else "error", "plan": str(plan_path), "shots": len(shots),
              "duration": round(total, 3), "ops": ops_total, "ops_density_10s": round(density, 2),
              "sizes": sorted(sizes), "errors": errors, "warnings": warnings}
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"plan     : {len(shots)} shot, {total:.2f}s | cỡ {', '.join(sorted(sizes))}")
        print(f"chuyển động: {ops_total} thao tác tường minh ({density:.1f}/10s)")
        for w in warnings:
            print(f"  ! {w}")
        for e in errors:
            print(f"  LỖI: {e}")
        print("OK" if not errors else f"FAIL: {len(errors)} lỗi")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
