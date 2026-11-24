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
      (`synth:<tên>` = file đã render ở audio/sfx/<tên>.wav); t của beat/SFX tính từ đầu shot, phải nằm trong shot
  E7  shot có ≥2 nhân vật: MỖI nhân vật có ≥1 hành vi tường minh (beat set/move/look/react) — người nói cũng vậy.
      Người nghe/người nói tự động (quay mắt, gật) do generator thêm, không thay được beat tường minh (R11.1).
  E9  beat (và macro đã bung) chỉ nhắc nhân vật/đạo cụ có mặt trong shot; thư viện macro hợp lệ
  E8  beat theo từ (`word`) phải trỏ tới từ có thật trong line; `move.to` phải là anchor L/C/R; react.preset ∈ {nod, flinch}.
  Line dài tách nhiều shot: mỗi shot khai `span: [từ, đến]` (giây, tính từ đầu line đầu tiên của shot).
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timing_lib import beat_time  # noqa: E402
from behaviors import check_library, expand_shot, load_library  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SFX_TOLERANCE = 0.15
EPS = 0.05
BEAT_LEAD = 0.6  # beat được phép đi trước thoại tối đa chừng này (anticipation)
SIZES = {"wide", "medium", "close", "macro", "ots"}


def check_sfx_src(src: str, repo: Path, proj: Path) -> str | None:
    """None nếu hợp lệ, ngược lại là thông điệp lỗi. Phải trỏ tới FILE âm thanh có thật."""
    if not src:
        return "SFX cue thiếu `src`"
    if src.startswith("synth:"):
        name = src[len("synth:"):].strip()
        if not name or "/" in name or "\\" in name:
            return f"recipe synth không hợp lệ: {src}"
        wav = proj / "audio" / "sfx" / f"{name}.wav"
        if not wav.is_file():
            return f"recipe '{name}' chưa render ra {wav.as_posix()}"
        return None
    for base in (repo, proj):
        if (base / src).is_file():
            return None
    return f"file SFX không tồn tại: {src}"


def load(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"LỖI: thiếu {path} — chưa tới bước này của workflow (C2 shotlist / C3 voice) hay sai đường dẫn --project?")
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

    only = {x.strip() for x in args.scenes.split(",") if x.strip()} if args.scenes else None
    if args.scenes is not None and not only:
        print("✗ --scenes rỗng", file=sys.stderr)
        return 1
    manifest_ids = {sc["id"] for sc in manifest["scenes"]}
    if only and only - manifest_ids:
        print(f"✗ --scenes có scene không có trong manifest: {', '.join(sorted(only - manifest_ids))}", file=sys.stderr)
        return 1
    lines: dict[str, dict] = {}
    for sc in manifest["scenes"]:
        if only and sc["id"] not in only:
            continue
        for ln in sc["lines"]:
            lines[ln["id"]] = ln
    if not lines:
        print("✗ không có line nào để kiểm (manifest rỗng hoặc scene không có line)", file=sys.stderr)
        return 1
    roles = {c["id"]: c.get("role", "character") for c in script.get("characters", [])}
    script_ids = {ln["id"] for sc in script.get("scenes", []) if not only or sc.get("id") in only for ln in sc.get("lines", [])}
    missing_in_manifest = sorted(script_ids - set(lines))
    if missing_in_manifest:
        print(f"✗ script.json có {len(missing_in_manifest)} line không có trong manifest.json (chạy lại build_voiceover.py): "
              f"{', '.join(missing_in_manifest[:8])}{' …' if len(missing_in_manifest) > 8 else ''}", file=sys.stderr)
        return 1

    chars = {c["id"]: c for c in bible.get("characters", [])}
    locs = {l["id"]: l for l in bible.get("locations", [])}
    props = {p["id"]: p for p in bible.get("props", [])}
    emotions = set(bible.get("emotion_vocab", []))
    if not emotions and any(c.get("emotion") for sh in shotlist.get("shots", []) for c in sh.get("characters", [])):
        print("✗ shotlist dùng emotion nhưng bible.emotion_vocab trống/thiếu — khai từ vựng cảm xúc trước", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    errors += [f"library/behaviors: {e}" for e in check_library(load_library())]

    shots = shotlist.get("shots", [])
    covering: dict[str, list[dict]] = {lid: [] for lid in lines}
    durations: list[float] = []
    sfx_total = 0
    beats_total = 0
    shot_win: dict[str, tuple[float, float]] = {}  # cửa sổ tuyệt đối (giây trên timeline thoại) của từng shot
    line_ivals: dict[str, list[tuple[float, float, str]]] = {lid: [] for lid in lines}
    acted: set[str] = set()

    # line nào được >1 shot chia sẻ thì mỗi shot phải khai span
    shared: dict[str, int] = {}
    for shot in shots:
        for lid in set(shot.get("line_ids", [])):
            if lid in lines:
                shared[lid] = shared.get(lid, 0) + 1

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
        span = shot.get("span")
        if span is not None:
            if not (isinstance(span, list) and len(span) == 2 and all(isinstance(x, (int, float)) for x in span)):
                errors.append(f"{sid}: span phải là [từ, đến] bằng giây")
                span = None
            elif not (0 <= span[0] < span[1] <= (end - start) + 1e-6):
                errors.append(f"{sid}: span {span} nằm ngoài khoảng {end - start:.2f}s của line")
                span = None
        if span is not None:
            dur = float(span[1]) - float(span[0])
        else:
            if any(shared[l] > 1 for l in lids):
                errors.append(f"{sid}: line dùng chung với shot khác nhưng thiếu `span` — không tính được thời lượng riêng của shot")
            dur = end - start
        durations.append(dur)
        abs0 = start + (float(span[0]) if span is not None else 0.0)
        abs1 = start + (float(span[1]) if span is not None else (end - start))
        shot_win[sid] = (abs0, abs1)
        for l in lids:
            lo, hi = max(abs0, lines[l]["start"]), min(abs1, lines[l]["start"] + lines[l]["duration"])
            if hi > lo:
                line_ivals[l].append((lo, hi, sid))
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
            if not states:
                errors.append(f"{sid}: bối cảnh {loc} chưa khai light_states trong bible")
            elif not light:
                errors.append(f"{sid}: thiếu `light` (phải thuộc light_states của {loc})")
            elif light not in states:
                errors.append(f"{sid}: ánh sáng '{light}' không thuộc light_states của {loc}")
        if shot.get("size") not in SIZES:
            errors.append(f"{sid}: size '{shot.get('size')}' không hợp lệ ({'/'.join(sorted(SIZES))})")
        for c in shot.get("characters", []):
            if c.get("id") not in chars:
                errors.append(f"{sid}: nhân vật '{c.get('id')}' không có trong bible")
            if c.get("emotion") not in emotions:
                errors.append(f"{sid}: cảm xúc '{c.get('emotion')}' ngoài emotion_vocab")
        for p in shot.get("props", []):
            pid = p.get("id")
            if pid not in props:
                errors.append(f"{sid}: đạo cụ '{pid}' không có trong bible")
                continue
            st = p.get("state")
            declared = props[pid].get("states")
            if not declared:
                errors.append(f"{sid}: đạo cụ {pid} chưa khai `states` trong bible")
            elif st not in declared:
                errors.append(f"{sid}: đạo cụ {pid} trạng thái '{st}' không có trong bible")
            allowed = props[pid].get("locations")
            if allowed and loc not in allowed:
                warnings.append(f"{sid}: đạo cụ {pid} xuất hiện ở {loc}, bible chỉ cho {allowed}")

        # --- bung macro hành vi (library/behaviors) → beat thường, để mọi gate dưới đây thấy đúng cái generator dựng
        try:
            shot = expand_shot(shot, lines, abs0)
        except (ValueError, KeyError) as exc:
            errors.append(f"{sid}: macro không hợp lệ — {exc}")
        # --- E9: beat (kể cả đã bung từ macro) chỉ được nhắc nhân vật/đạo cụ có mặt trong shot
        cids = {c.get("id") for c in (shot.get("characters") or [])}
        pkeys = {(p.get("key") or p.get("id")) for p in (shot.get("props") or [])}
        for b in shot.get("beats", []):
            tag = f" (macro {b['from_macro']})" if b.get("from_macro") else ""
            refs = [k for k in (b.get("set") or {}) if k != "light" and not k.startswith("prop:")]
            for k in ("move", "look", "react"):
                if isinstance(b.get(k), dict):
                    refs.append(b[k].get("char"))
            if isinstance(b.get("look"), dict):
                refs.append(b["look"].get("target"))
            if isinstance(b.get("hand_over"), dict):
                refs += [b["hand_over"].get("from"), b["hand_over"].get("to")]
                if b["hand_over"].get("prop") not in pkeys:
                    errors.append(f"{sid}: beat{tag} hand_over prop '{b['hand_over'].get('prop')}' không có trong shot (E9)")
            for r in refs:
                if r not in cids:
                    errors.append(f"{sid}: beat{tag} nhắc nhân vật '{r}' không có trong shot (E9)")
        # --- beats & sfx
        beats = shot.get("beats", [])
        beats_total += len(beats)
        sfx = shot.get("sfx", [])
        sfx_total += len(sfx)
        for b in beats:
            if b.get("line_id") not in lids:
                errors.append(f"{sid}: beat tham chiếu line '{b.get('line_id')}' ngoài shot")
            has_do = bool(str(b.get("do", "")).strip())
            if not has_do:
                errors.append(f"{sid}: beat của {b.get('line_id')} thiếu mô tả hành động `do`")
            try:
                t = beat_time(b, lines, abs0)
            except (ValueError, KeyError) as exc:
                errors.append(f"{sid}: beat không hợp lệ — {exc}")
                continue
            if "word" in b:
                ln_w = lines.get(b.get("line_id"))
                if ln_w is not None and not (0 <= int(b["word"]) < len(str(ln_w["text"]).split())):
                    errors.append(f"{sid}: beat word={b['word']} ngoài số từ của {b.get('line_id')}")
            if isinstance(b.get("react"), dict) and b["react"].get("preset", "nod") not in ("nod", "flinch"):
                errors.append(f"{sid}: react.preset '{b['react'].get('preset')}' không hỗ trợ (nod|flinch)")
            if b.get("move") and not isinstance(b["move"], dict):
                errors.append(f"{sid}: move phải là object {{char,to,dur}}")
            t_ok = -EPS <= t <= dur + EPS
            if not t_ok:
                errors.append(f"{sid}: beat t={t} nằm ngoài shot (0–{dur:.2f}s)")
            bl = lines.get(b.get("line_id"))
            if t_ok and bl is not None:
                at = abs0 + t
                if bl["start"] - BEAT_LEAD - EPS <= at <= bl["start"] + bl["duration"] + EPS:
                    if has_do:
                        acted.add(b["line_id"])
                else:
                    errors.append(f"{sid}: beat '{str(b.get('do', ''))[:30]}' rơi ở {at:.2f}s, ngoài cửa sổ thoại của {b['line_id']} "
                                  f"({bl['start']:.2f}–{bl['start'] + bl['duration']:.2f}s, cho phép sớm {BEAT_LEAD}s)")
            if isinstance(b.get("hand_over"), dict) and not b.get("physical"):
                errors.append(f"{sid}: beat hand_over phải có physical=true (R6.1/R11.5)")
            if b.get("physical"):
                if not any(abs(float(s.get("t", 0.0)) - t) <= SFX_TOLERANCE for s in sfx):
                    errors.append(f"{sid}: beat vật lý '{b.get('do', '')[:40]}' (t={t}) chưa có SFX trong ±{SFX_TOLERANCE}s")
        shot_chars = shot.get("characters", []) or []
        if len(shot_chars) >= 2:
            explicit = set()
            for b in beats:
                explicit |= set((b.get("set") or {}).keys()) & {c.get("id") for c in shot_chars}
                for k in ("move", "look", "react"):
                    if isinstance(b.get(k), dict):
                        explicit.add(b[k].get("char"))
                if isinstance(b.get("hand_over"), dict):  # chuyển tay: cả người cho lẫn người nhận đều có hành vi
                    explicit |= {b["hand_over"].get("from"), b["hand_over"].get("to")}
            for c in shot_chars:
                if c.get("id") not in explicit:
                    errors.append(f"{sid}: shot nhiều người nhưng {c.get('id')} không có hành vi tường minh (beat set/move/look/react) — "
                                  f"thêm beat cho nhân vật này (E7/R11.1)")
        for s in sfx:
            st_ = float(s.get("t", 0.0))
            if not (-EPS <= st_ <= dur + EPS):
                errors.append(f"{sid}: SFX '{s.get('cue', '')}' t={st_} nằm ngoài shot (0–{dur:.2f}s)")
            err = check_sfx_src(str(s.get("src", "")).strip(), args.repo, proj)
            if err:
                errors.append(f"{sid}: {err}")

    # --- E1/E2/E4 theo từng line
    for lid, ln in lines.items():
        cov = covering[lid]
        if not cov:
            errors.append(f"{lid}: không có shot")
            continue
        if lid not in acted:
            errors.append(f"{lid}: có shot nhưng không có beat diễn hợp lệ (có `do`, t trong shot, rơi trong cửa sổ thoại)")
        # các shot chia sẻ line phải phủ kín line, không hở, không chồng
        if len(line_ivals[lid]) > 0 and (shared.get(lid, 0) > 1 or any(sh.get("span") for sh in cov)):
            iv = sorted(line_ivals[lid])
            cur = ln["start"]
            end_l = ln["start"] + ln["duration"]
            for lo, hi, sid_ in iv:
                if lo > cur + EPS:
                    errors.append(f"{lid}: hở {cur - ln['start']:.2f}–{lo - ln['start']:.2f}s không shot nào phủ (trước {sid_})")
                elif lo < cur - EPS:
                    errors.append(f"{lid}: shot {sid_} chồng lên shot trước {cur - lo:.2f}s")
                cur = max(cur, hi)
            if cur < end_l - EPS:
                errors.append(f"{lid}: hở {cur - ln['start']:.2f}–{ln['duration']:.2f}s cuối line không shot nào phủ")
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
