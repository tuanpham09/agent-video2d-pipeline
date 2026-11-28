#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""behavior_sheet.py — sheet duyệt bằng mắt cho hành vi mẫu (R2.7, R10.4): mỗi macro một thẻ, hai nhân vật thật của project,
hàng "trước" (idle/calm) và hàng "sau" (trạng thái cuối do macro đặt). Macro chuyển động (react, move, hand_over) có nhãn
mô tả vì ảnh tĩnh không thể hiện chuyển động — xem snapshot của shot để duyệt phần động.

  python behavior_sheet.py --project projects/<slug> [--out library/sheets/behaviors.png] [--a host --b me]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_rig as BR  # noqa: E402
from behaviors import REPO, _sub, load_library, resolve_args  # noqa: E402

EXAMPLE = {"char": None, "target": None, "from": None, "to": None, "prop": "mam_tre", "side": None, "dur": None}


def final_states(macro: dict, args: dict, a: str, b: str) -> tuple[dict, list[str]]:
    """Trạng thái cuối theo nhân vật + danh sách nhãn mô tả phần chuyển động."""
    st: dict[str, dict] = {a: {}, b: {}}
    tags: list[str] = []
    pos = {a: 0, b: 1}  # a đứng bên trái, b bên phải
    for step in macro["steps"]:
        for cid, vals in (_sub(step.get("set", {}), args)).items():
            st.setdefault(cid, {}).update(vals)
        if "look" in step:
            lk = _sub(step["look"], args)
            st[lk["char"]]["gaze"] = "right" if pos[lk["target"]] > pos[lk["char"]] else "left"
        if "react" in step:
            r = _sub(step["react"], args)
            tags.append(f"động: {r['preset']} ({r['char']})")
        if "move" in step:
            mv = _sub(step["move"], args)
            tags.append(f"động: đi tới {mv['to']} ({mv['char']})")
        if "hand_over" in step:
            h = _sub(step["hand_over"], args)
            side = "l" if pos[h["to"]] > pos[h["from"]] else "r"
            st[h["from"]]["pose"] = f"reach-{side}"
            tags.append(f"động: {h['from']} trao {h['prop']} → {h['to']}")
    return st, tags


def build(project: Path, a: str, b: str) -> str:
    bible = json.loads((project / "script" / "bible.json").read_text(encoding="utf-8-sig"))
    style = bible.get("style", {})
    palette = BR.load_palette(REPO / "library", style.get("palette_ref") or ["base"], style.get("palette", {}))
    cat = REPO / "library" / "rigs" / "archetypes.json"
    catalog = json.loads(cat.read_text(encoding="utf-8")) if cat.exists() else {}
    chars = {c["id"]: c for c in BR.resolve_extends(bible.get("characters", []))}
    rigs = {i: BR.Rig(chars[i], palette, catalog) for i in (a, b)}
    cards = []
    for name, m in load_library().items():
        args = {}
        for k, default in m["params"].items():
            if default is not None:
                args[k] = default
        for k, v in {"char": a, "target": b, "from": a, "to": b}.items():
            if k in m["params"]:
                args[k] = v
        if "prop" in m["params"]:
            args["prop"] = "mam_tre"
        args = resolve_args(name, m, args)
        after, tags = final_states(m, args, a, b)
        flags = (["vật lý + SFX"] if m.get("physical") else []) + tags

        full = any("pose" in v for v in after.values()) or any("động: đi" in t or "trao" in t for t in tags)

        def row(states):  # đổi biểu cảm/ánh nhìn → cận đầu cho thấy rõ; đổi tư thế/di chuyển → toàn thân
            return "".join(
                f'<div class="f {"full" if full else "head"}">{rigs[i].svg(states.get(i, {}), None if full else rigs[i].crop())}</div>'
                for i in (a, b))

        cards.append(
            f'<section><h3>{name}</h3><p>{BR.esc(m["desc"])}</p>'
            f'<div class="pair"><div><small>trước</small><div class="r">{row({})}</div></div>'
            f'<div><small>sau</small><div class="r">{row(after)}</div></div></div>'
            f'<div class="tags">{"".join(f"<span>{BR.esc(t)}</span>" for t in flags) or "<span>tĩnh</span>"}'
            f'<span>{BR.esc(_sub(m["do"], args))}</span></div></section>'
        )
    return f"""<!doctype html><html lang="vi"><meta charset="utf-8">
<style>:root{{color-scheme:dark}}
body{{margin:0;padding:24px 28px 32px;background:#2a2018;color:#eadfce;font:14px/1.4 system-ui,sans-serif;width:1500px}}
h1{{font-size:20px;margin:0 0 4px}} .meta{{opacity:.75;margin-bottom:16px}}
.g{{display:grid;grid-template-columns:repeat(2,730px);gap:14px}}
section{{background:#3a2d22;border-radius:10px;padding:10px 12px}}
h3{{margin:0;font-size:15px}} p{{margin:2px 0 6px;opacity:.8;font-size:12px}}
.pair{{display:flex;gap:10px}} small{{opacity:.6;font-size:11px}}
.r{{display:flex;gap:2px}} .f.full svg{{width:170px;height:196px;display:block}} .f.head svg{{width:170px;height:auto;display:block}}
.tags{{margin-top:6px;display:flex;flex-wrap:wrap;gap:4px}} .tags span{{background:#4b3a2c;border-radius:6px;padding:1px 7px;font-size:11px}}
</style><h1>Hành vi mẫu — {len(cards)} macro</h1>
<div class="meta">Nhân vật minh hoạ: {BR.esc(a)} (trái) và {BR.esc(b)} (phải) từ {BR.esc(project.name)}. Ảnh tĩnh = trạng thái cuối; phần "động" xem ở snapshot shot.</div>
<div class="g">{"".join(cards)}</div></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=REPO / "library" / "sheets" / "behaviors.png")
    ap.add_argument("--a", default="host")
    ap.add_argument("--b", default="me")
    args = ap.parse_args()
    html = build(args.project, args.a, args.b)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    h = args.out.with_suffix(".html")
    h.write_text(html, encoding="utf-8")
    BR.render_png(h, args.out, 1556)
    h.unlink()
    print(f"ok: {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
