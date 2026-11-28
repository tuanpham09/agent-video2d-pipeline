#!/usr/bin/env python3
"""Nhập kho bối cảnh sinh bằng code (assets/library/bg/*.svg + catalog.json, do build_bg.py tạo)
vào library/ dùng chung theo chuẩn RULES.md R2.5–R2.7.

Biến đổi (chạy lại được, kết quả xác định):
  • màu:  mọi #hex → var(--pal-bg_<hex6>); các token đó nằm ở library/palettes/scenery-vn.json
          (kế thừa base). Token đặt tên theo giá trị màu: muốn đổi tông cả kho thì sửa giá trị
          trong palette, không đụng SVG. Chưa gom theo ngữ nghĩa (tường/mái/đất…).
  • id nội bộ:  thêm tiền tố <scene>- (cho url(#..), href="#..") để nhúng nhiều asset chung một cảnh không trùng.
  • CSS:  chặn phạm vi bằng svg[data-lib-id="<id>"], .layer.far|mid|near → .layer.layer-far|mid|near.
  • ánh sáng: candle_warm → warm, dusk → dawn; giữ day, night → đủ warm|dark|red_flash|dawn (R4.2).
          Nếu một cảnh thiếu candle_warm/dusk thì gán bí danh theo luật còn lại (hiện chưa cảnh nào cần).
  • index.json: thêm mục kind=location, anchor `stand` L/C/R + `crop_9x16` lấy từ `bg_lib/anchors.py`
          từ bg_lib/anchors.py (đã ghép nhân vật host ở khung 9:16 để chỉnh; anchors_reviewed=true).

Dùng:  python .agents/skills/video-pipeline/scripts/import_bg.py [--src assets/library/bg] [--only id,id]
Sau đó: library.py check && library.py sheet, xem ảnh, rồi commit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import library as L  # noqa: E402
from bg_lib.anchors import ANCHORS  # noqa: E402

HEX3_8 = re.compile(r"(?<!url\()(?<!href=\")#([0-9a-fA-F]{3,8})\b")
RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
LIGHT_RENAME = {"candle_warm": "warm", "dusk": "dawn"}
REQUIRED = ["warm", "dark", "red_flash", "dawn"]
PAL_ID = "scenery-vn"


def norm_hex(h: str) -> str:
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"màu #{h} không phải 3/6 chữ số (alpha hex chưa hỗ trợ)")
    return h.lower()


def scope_css(css: str, lid: str, states: set[str]) -> str:
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    out = []
    for sel_list, body in RULE.findall(css):
        sels = [s.strip() for s in sel_list.split(",") if s.strip()]
        # ngoại cảnh chưa có warm: warm dùng chung luật của dusk (tint + đèn)
        if "candle_warm" not in states:
            sels += [s.replace("'dusk'", "'candle_warm'") for s in sels if "'dusk'" in s]
        new = []
        for s in sels:
            s = re.sub(r"data-light='(\w+)'", lambda m: f"data-light='{LIGHT_RENAME.get(m.group(1), m.group(1))}'", s)
            s = re.sub(r"\.layer\.(far|mid|near)\b", r".layer.layer-\1", s)
            s = f'svg[data-lib-id="{lid}"]' + s[3:] if s.startswith("svg") else f'svg[data-lib-id="{lid}"] {s}'
            new.append(s)
        out.append(f"{','.join(new)}{{{body.strip()}}}")
    if "dusk" not in states:  # nội cảnh chưa có dawn
        out.append(f'svg[data-lib-id="{lid}"][data-light=\'dawn\']{{--t:#ff9a55;--a:.3}}')
    return "\n".join(out)


def convert(scene: dict, text: str, tokens: dict[str, str]) -> str:
    sid = scene["id"]
    # trạng thái thật = trong CSS (khuôn chung có đủ day/dusk/night/dark/candle_warm/red_flash; catalog chỉ liệt kê một phần)
    states = set(re.findall(r"data-light='(\w+)'", text))
    pref = sid.replace("_", "") + "-"

    # 1. id nội bộ + tham chiếu
    ids = set(re.findall(r'\bid="([^"]+)"', text))
    for i in sorted(ids, key=len, reverse=True):
        text = re.sub(rf'\bid="{re.escape(i)}"', f'id="{pref}{i}"', text)
        text = text.replace(f"url(#{i})", f"url(#{pref}{i})")
        text = re.sub(rf'href="#{re.escape(i)}"', f'href="#{pref}{i}"', text)

    # 2. CSS: phạm vi + ánh sáng + lớp
    def style_sub(m: re.Match) -> str:
        return f"<style>\n{scope_css(m.group(1), sid, states)}\n</style>"
    text = re.sub(r"<style>(.*?)</style>", style_sub, text, count=1, flags=re.S)

    # 3. lớp trong DOM
    text = re.sub(r'class="layer (far|mid|near)"', r'class="layer layer-\1"', text)

    # 4. màu → token
    def tok(m: re.Match) -> str:
        h = norm_hex(m.group(1))
        tokens[f"bg_{h}"] = f"#{h}"
        return f"var(--pal-bg_{h})"
    text = HEX3_8.sub(tok, text)
    # var(--t,var(--pal..)) hợp lệ; var(--pal-..) trong thuộc tính trình bày cũng hợp lệ

    # 5. nhãn asset ở thẻ gốc
    text = text.replace("<svg ", f'<svg data-lib-id="{sid}" data-lib-kind="location" ', 1)
    # ánh sáng mặc định ở thẻ gốc giữ nguyên (đã là một trong states; day/night không đổi tên)
    root_light = re.search(r'<svg[^>]*data-light="(\w+)"', text).group(1)
    text = re.sub(r'(<svg[^>]*data-light=")\w+(")', lambda m: f"{m.group(1)}{LIGHT_RENAME.get(root_light, root_light)}{m.group(2)}", text, count=1)
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src", type=Path, default=Path("assets/library/bg"))
    ap.add_argument("--only", help="id cách nhau dấu phẩy")
    args = ap.parse_args()

    cat = json.loads((args.src / "catalog.json").read_text(encoding="utf-8"))
    only = set(args.only.split(",")) if args.only else None
    idx = L.load_index()
    by_id = {e["id"]: e for e in idx["items"]}
    tokens: dict[str, str] = {}
    pal_path = L.LIB / "palettes" / f"{PAL_ID}.json"
    if pal_path.exists():
        tokens.update(json.loads(pal_path.read_text(encoding="utf-8")).get("tokens", {}))

    done = []
    for sc in cat["backgrounds"]:
        if only and sc["id"] not in only:
            continue
        if sc["id"] in by_id and by_id[sc["id"]].get("origin") != "build_bg":
            print(f"BỎ QUA {sc['id']}: trùng id với asset library không phải do import_bg tạo", file=sys.stderr)
            continue
        text = convert(sc, (args.src / sc["file"]).read_text(encoding="utf-8"), tokens)
        dst = L.LIB / "locations" / f"{sc['id']}.svg"
        dst.write_text(text, encoding="utf-8")

        # trạng thái lấy từ CSS thực tế (catalog có thể thiếu: nội cảnh vẫn có luật night của khuôn chung)
        lights = sorted(set(re.findall(r"\[data-light='(\w+)'\]", text)) | set(REQUIRED))
        fy, s_, cx, dx_ = ANCHORS[sc["id"]]
        cx = max(304, min(1616, cx))
        stand = {k: {"x": max(120, min(1800, cx + dx)), "y": fy, "s": s_} for k, dx in (("L", -dx_), ("C", 0), ("R", dx_))}
        entry = {
            "id": sc["id"], "kind": "location", "file": f"locations/{sc['id']}.svg",
            "description": f"{sc['name']} (kho bối cảnh sinh bằng code; {sc['kind']})",
            "size": [1920, 1080], "layers": sc["layers"],
            "light_states": lights, "default_light": LIGHT_RENAME.get(re.search(r'data-light="(\w+)"', text).group(1), "day"),
            "floor_y": fy, "stand": stand, "slots": {}, "crop_9x16": {"center": cx},
            "tags": sorted(set(sc["tags"]) | {sc["kind"], "bg-gen"}), "moods": sc.get("moods", ["normal"]),
            "palettes": ["base", PAL_ID], "origin": "build_bg", "anchors_reviewed": True,
        }
        old = by_id.get(sc["id"])
        digest = L.sha(dst)
        entry["version"] = old["version"] + (0 if old and old.get("sha256") == digest else 1) if old else 1
        entry["sha256"] = digest
        if old:
            idx["items"][idx["items"].index(old)] = entry
        else:
            idx["items"].append(entry)
        done.append(sc["id"])

    pal_path.write_text(json.dumps({
        "id": PAL_ID, "extends": "base",
        "description": "Màu của kho bối cảnh sinh bằng code (import_bg.py). Token đặt tên theo giá trị màu gốc; sửa giá trị để đổi tông.",
        "tokens": dict(sorted(tokens.items())),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    L.save_index(idx)
    print(f"đã nhập {len(done)} bối cảnh, {len(tokens)} token màu → {pal_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
