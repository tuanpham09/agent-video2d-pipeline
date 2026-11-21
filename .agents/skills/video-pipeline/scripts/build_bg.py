#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh thư viện bối cảnh 2D dùng chung: assets/library/bg/<id>.svg + catalog.json + contact sheet.

Mỗi bối cảnh = 1 file SVG tự chứa, viewBox 0 0 1920 1080, 3 lớp để làm parallax:
  <g class="layer far"> <g class="layer mid"> <g class="layer near">
Ánh sáng điều khiển bằng thuộc tính trên <svg data-light="...">, không đổi DOM:
  day | dusk | night | dark | candle_warm | red_flash
(tint nhân màu + trăng/ánh nến bật theo trạng thái; CSS nằm trong file SVG).
Tiêu điểm hành động đặt ở dải giữa x 656..1264 nên cắt dọc 9:16 (viewBox "656 0 608 1080") vẫn đúng cảnh.

Dùng:
  python .agents/skills/video-pipeline/scripts/build_bg.py                 # build tất cả
  python .agents/skills/video-pipeline/scripts/build_bg.py --only nghia_dia,chua
  python .agents/skills/video-pipeline/scripts/build_bg.py --no-sheet       # bỏ contact sheet (cần playwright)
Thêm bối cảnh mới: viết hàm trong bg_lib/ (xem REGISTRY ở cuối file) rồi chạy lại. Clone từ bối cảnh gần nhất cho nhanh.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from bg_lib.core import LIGHTS_EXT, LIGHTS_INT, wrap_svg  # noqa: E402
from bg_lib import REGISTRY  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh thư viện bối cảnh SVG dùng chung.")
    ap.add_argument("--out", type=Path, default=Path("assets/library/bg"))
    ap.add_argument("--only", help="id cách nhau bằng dấu phẩy")
    ap.add_argument("--no-sheet", action="store_true")
    args = ap.parse_args()

    only = {x.strip() for x in args.only.split(",")} if args.only else None
    bad = (only or set()) - set(REGISTRY)
    if bad:
        print(f"LỖI: id không có trong REGISTRY: {sorted(bad)}", file=sys.stderr)
        return 1
    args.out.mkdir(parents=True, exist_ok=True)

    catalog_path = args.out / "catalog.json"
    catalog = {}
    if catalog_path.exists():
        catalog = {b["id"]: b for b in json.loads(catalog_path.read_text(encoding="utf-8"))["backgrounds"]}

    built = []
    for bid, spec in REGISTRY.items():
        if only and bid not in only:
            continue
        layers = spec["draw"]()
        svg = wrap_svg(bid, spec, layers)
        (args.out / f"{bid}.svg").write_text(svg, encoding="utf-8")
        catalog[bid] = {
            "id": bid, "name": spec["name"], "file": f"{bid}.svg", "kind": spec["kind"],
            "layers": ["far", "mid", "near"],
            "light_states": LIGHTS_EXT if spec["kind"] == "exterior" else LIGHTS_INT,
            "tags": spec.get("tags", []), "focus": spec.get("focus", [960, 700]),
        }
        built.append(bid)

    order = [b for b in REGISTRY if b in catalog]
    out = {"viewBox": "0 0 1920 1080", "portrait_crop": "656 0 608 1080",
           "backgrounds": [catalog[b] for b in order]}
    catalog_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.no_sheet and built:
        from bg_lib.sheet import render_sheet
        render_sheet(args.out, [catalog[b] for b in order])
    print(json.dumps({"status": "ok", "built": built, "total_in_catalog": len(order)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
