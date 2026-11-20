#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate đồng bộ thoại ↔ shot ↔ bible ↔ SFX.

Đọc:
  audio/manifest.json      (thời lượng thật của từng line)
  script/script.json       (vai trò nhân vật: narrator hay nhân vật)
  script/bible.json        (nhân vật, bối cảnh, đạo cụ, từ vựng cảm xúc)
  script/shotlist.json     (shot cho từng line, beat diễn, SFX cue)

Kiểm:
  E1  mọi line có shot phủ
  E2  mọi line có ≥1 beat diễn riêng (kể cả line rất ngắn)
  E3  shot không dài quá --max-shot (mặc định 6.0 s)
  E4  nhân vật nói phải xuất hiện trong shot, mouth=true
  E5  location / nhân vật / đạo cụ / trạng thái đạo cụ / cảm xúc / ánh sáng phải có trong bible
  E6  beat physical=true phải có SFX cue trong ±0.15 s; file SFX phải tồn tại
  W   cỡ cảnh lặp, đạo cụ lùi trạng thái, shot quá ngắn, nhịp shot trung bình chậm

Dùng:
  python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/<slug>
  python ... --project projects/<slug> --scenes S01,S02   # chỉ bản demo
Mã thoát: 0 = qua gate, 1 = có lỗi.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SFX_TOLERANCE = 0.15
SIZES = {"wide", "medium", "close", "macro", "ots"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    ap = argparse.ArgumentParser(description="Kiểm thoại ↔ shot ↔ bible ↔ SFX.")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path("."), help="gốc repo, để tìm file SFX/rig tương đối")
    ap.add_argument("--scenes", help="chỉ kiểm các scene này, ví dụ S01,S02 (dùng cho bản demo)")
    ap.add_argument("--max-shot", type=float, default=6.0)
    ap.add_argument("--min-shot", type=float, default=1.0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    proj = args.project
    manifest = load(proj / "audio" / "manifest.json")
    script = load(proj / "script" / "script.json")
    bible = load(proj / "script" / "bible.json")
    shotlist = load(proj / "script" / "shotlist.json")

    only = set(args.scenes.split(",")) if args.scenes else None
    lines: dict[str, dict] = {}
    for sc in manifest["scenes"]:
        if only and sc["id"] not in only:
            continue
        for ln in sc["lines"]:
            lines[ln["id"]] = ln
    roles = {c["id"]: c.get("role", "character") for c in script.get("characters", [])}

    chars = {c["id"]: c for c in bible.get("characters", [])}
    locs = {l["id"]: l for l in bible.get("locations", [])}
    props = {p["id"]: p for p in bible.get("props", [])}
    emotions = set(bible.get("emotion_vocab", []))

    errors: list[str] = []
    warnings: list[str] = []

    shots = shotlist.get("shots", [])
    covering: dict[str, list[dict]] = {lid: [] for lid in lines}
    durations: list[float] = []
    sfx_total = 0
    beats_total = 0

    for shot in shots:
        sid = shot.get("id", "?")
        lids = [lid for lid in shot.get("line_ids", []) if lid in lines]
        if not lids:
            if only is None:
                warnings.append(f"{sid}: không gắn line nào trong manifest")
            continue
        for lid in lids:
            covering[lid].append(shot)
        start = min(lines[l]["start"] for l in lids)
        end = max(lines[l]["start"] + lines[l]["duration"] for l in lids)
        dur = end - start
        durations.append(dur)
        if dur > args.max_shot:
            errors.append(f"{sid}: dài {dur:.1f}s > {args.max_shot:.1f}s ({', '.join(lids)}) — tách shot/đổi góc")
        elif dur < args.min_shot:
            warnings.append(f"{sid}: chỉ {dur:.1f}s — gộp với shot kế hoặc kéo dài khoảng nghỉ")

        # --- bible refs
        loc = shot.get("location")
        if loc not in locs:
            errors.append(f"{sid}: location '{loc}' không có trong bible")
        else:
            light = shot.get("light")
            states = locs[loc].get("light_states")
            if light and states and light not in states:
                errors.append(f"{sid}: ánh sáng '{light}' không thuộc light_states của {loc}")
        if shot.get("size") not in SIZES:
            errors.append(f"{sid}: size '{shot.get('size')}' không hợp lệ ({'/'.join(sorted(SIZES))})")
        for c in shot.get("characters", []):
            if c.get("id") not in chars:
                errors.append(f"{sid}: nhân vật '{c.get('id')}' không có trong bible")
            if emotions and c.get("emotion") not in emotions:
                errors.append(f"{sid}: cảm xúc '{c.get('emotion')}' ngoài emotion_vocab")
        for p in shot.get("props", []):
            pid = p.get("id")
            if pid not in props:
                errors.append(f"{sid}: đạo cụ '{pid}' không có trong bible")
                continue
            st = p.get("state")
            if props[pid].get("states") and st not in props[pid]["states"]:
                errors.append(f"{sid}: đạo cụ {pid} trạng thái '{st}' không có trong bible")
            allowed = props[pid].get("locations")
            if allowed and loc not in allowed:
                warnings.append(f"{sid}: đạo cụ {pid} xuất hiện ở {loc}, bible chỉ cho {allowed}")

        # --- beats & sfx
        beats = shot.get("beats", [])
        beats_total += len(beats)
        sfx = shot.get("sfx", [])
        sfx_total += len(sfx)
        for b in beats:
            if b.get("line_id") not in lids:
                errors.append(f"{sid}: beat tham chiếu line '{b.get('line_id')}' ngoài shot")
            if b.get("physical"):
                t = float(b.get("t", 0.0))
                if not any(abs(float(s.get("t", 0.0)) - t) <= SFX_TOLERANCE for s in sfx):
                    errors.append(f"{sid}: beat vật lý '{b.get('do', '')[:40]}' (t={t}) chưa có SFX trong ±{SFX_TOLERANCE}s")
        for s in sfx:
            src = s.get("src", "")
            if src.startswith("synth:"):
                continue
            if not (args.repo / src).exists() and not (proj / src).exists():
                errors.append(f"{sid}: file SFX không tồn tại: {src}")

    # --- E1/E2/E4 theo từng line
    for lid, ln in lines.items():
        cov = covering[lid]
        if not cov:
            errors.append(f"{lid}: không có shot")
            continue
        if not any(b.get("line_id") == lid for s in cov for b in s.get("beats", [])):
            errors.append(f"{lid}: có shot nhưng không có beat diễn riêng")
        spk = ln.get("speaker")
        if roles.get(spk, "character") != "narrator":
            ok = any(
                c.get("id") == spk and c.get("mouth") for s in cov for c in s.get("characters", [])
            )
            if not ok:
                errors.append(f"{lid}: {spk} nói nhưng không có shot nào cho {spk} mouth=true")

    # --- cảnh báo nhịp & lặp
    sizes = [s.get("size") for s in shots]
    for i in range(2, len(shots)):
        a, b, c = shots[i - 2], shots[i - 1], shots[i]
        if (a.get("size"), a.get("camera")) == (b.get("size"), b.get("camera")) == (c.get("size"), c.get("camera")):
            warnings.append(f"{a.get('id')}→{c.get('id')}: 3 shot liền cùng cỡ cảnh + camera")
    if sizes and max(sizes.count(s) for s in set(sizes)) / len(sizes) > 0.5:
        warnings.append("hơn 50% shot cùng một cỡ cảnh")
    last: dict[str, int] = {}
    for shot in shots:
        for p in shot.get("props", []):
            pid = p.get("id")
            order = props.get(pid, {}).get("states") or []
            if p.get("state") in order:
                idx = order.index(p["state"])
                if idx < last.get(pid, -1) and not p.get("reset"):
                    warnings.append(f"{shot.get('id')}: đạo cụ {pid} lùi trạng thái → '{p['state']}' (thêm reset:true nếu cố ý)")
                last[pid] = idx
    avg = sum(durations) / len(durations) if durations else 0.0
    if avg > 5.0:
        warnings.append(f"shot trung bình {avg:.1f}s: nhịp chậm hơn chuẩn 3–5 s")

    report = {
        "status": "ok" if not errors else "error",
        "lines": len(lines),
        "lines_with_shot": sum(1 for v in covering.values() if v),
        "shots": len(shots),
        "avg_shot_s": round(avg, 2),
        "beats": beats_total,
        "sfx_cues": sfx_total,
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"line     : {report['lines_with_shot']}/{report['lines']} có shot | {len(shots)} shot, TB {avg:.1f}s")
        print(f"diễn/sfx : {beats_total} beat, {sfx_total} SFX cue")
        for w in warnings[:15]:
            print(f"  ! {w}")
        for e in errors[:30]:
            print(f"  ✗ {e}")
        if len(errors) > 30:
            print(f"  … và {len(errors) - 30} lỗi nữa (dùng --json)")
        print("OK" if not errors else f"FAIL ({len(errors)} lỗi)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
