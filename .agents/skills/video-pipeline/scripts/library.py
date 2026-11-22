#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quản lý library/ dùng chung: rig (archetype/outfit), đạo cụ, bối cảnh, palette.

Luật (RULES.md R2): tra thư viện TRƯỚC khi vẽ mới; dùng lại bằng `use` (có khoá phiên bản);
asset mới phải đạt chuẩn rồi `promote` vào library trước khi đóng gói project.

Lệnh:
  list   [--kind prop|location|archetype|outfit|palette] [--tag TAG]
  show   <id>
  check                         kiểm toàn bộ library (màu, trạng thái, parts, sha, id trùng)
  reindex                       cập nhật sha256, tự tăng version khi nội dung đổi
  use    --project SLUG <id>... chép asset vào projects/SLUG/assets/{props,bg}, ghi LIBRARY.lock.json
  lock-check --project SLUG     so lock với library (asset đã bị sửa sau khi chốt?)
  sheet                         render library/sheets/{props,locations}.png để duyệt bằng mắt
  promote --project SLUG --kind prop|location --id ID --file PATH --states a,b --tags x,y --desc "..."
                                đưa asset mới của project vào library (chạy check trước)

Asset trong library: KHÔNG hex/rgb/tên màu, chỉ var(--pal-<token>); không <text>; không <script>.
Trạng thái đạo cụ: data-state; ánh sáng bối cảnh: data-light. Gốc toạ độ prop = giữa-đáy.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[4]
LIB = REPO / "library"
KIND_DIR = {"prop": "props", "location": "locations"}
PROJECT_DIR = {"prop": "props", "location": "bg"}
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
FUNC_COLOR = re.compile(r"\b(?:rgb|rgba|hsl|hsla)\s*\(", re.I)
VAR_TOKEN = re.compile(r"var\(--pal-([A-Za-z0-9_]+)\)")
COLOR_ATTRS = ("fill", "stroke", "stop-color", "flood-color", "color")
OK_COLOR = re.compile(r"^(none|currentColor|transparent|inherit|url\(.*\)|var\(--pal-[A-Za-z0-9_]+\))$")


# ---- dữ liệu --------------------------------------------------------------

def load_index(lib: Path | None = None) -> dict:
    lib = lib or LIB
    return json.loads((lib / "index.json").read_text(encoding="utf-8"))


def save_index(idx: dict, lib: Path | None = None) -> None:
    lib = lib or LIB
    (lib / "index.json").write_text(json.dumps(idx, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_palette(library: Path, refs: list[str], overrides: dict | None = None) -> dict:
    """Gộp palette theo chuỗi extends rồi áp ghi đè của project."""

    def resolve(pid: str, seen: tuple = ()) -> dict:
        if pid in seen:
            raise SystemExit(f"LỖI: palette vòng lặp extends: {pid}")
        f = library / "palettes" / f"{pid}.json"
        if not f.exists():
            raise SystemExit(f"LỖI: không có palette '{pid}' ({f})")
        d = json.loads(f.read_text(encoding="utf-8"))
        base = resolve(d["extends"], seen + (pid,)) if d.get("extends") else {}
        return {**base, **d.get("tokens", {})}

    out: dict = {}
    for r in refs:
        out.update(resolve(r))
    out.update(overrides or {})
    return out


def palette_style(tokens: dict, lib_id: str) -> str:
    body = ";".join(f"--pal-{k}:{v}" for k, v in sorted(tokens.items()))
    return f'<style data-palette="1">svg[data-lib-id="{lib_id}"]{{{body}}}</style>'


def inject_palette(svg_text: str, tokens: dict, lib_id: str) -> str:
    svg_text = re.sub(r'<style data-palette="1">.*?</style>', "", svg_text, flags=re.S)
    m = re.search(r"<svg\b[^>]*>", svg_text)
    return svg_text[: m.end()] + palette_style(tokens, lib_id) + svg_text[m.end():]


def strip_palette(svg_text: str) -> str:
    return re.sub(r'<style data-palette="1">.*?</style>', "", svg_text, flags=re.S)


# ---- kiểm asset -----------------------------------------------------------

def check_asset(entry: dict, lib: Path | None = None, base_tokens: dict | None = None) -> tuple[list[str], list[str]]:
    lib = lib or LIB
    errs: list[str] = []
    warns: list[str] = []
    eid = entry["id"]
    path = lib / entry["file"]
    if not path.exists():
        return [f"{eid}: thiếu file {entry['file']}"], warns
    text = path.read_text(encoding="utf-8")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        return [f"{eid}: SVG không parse được: {e}"], warns

    if root.get("data-lib-id") != eid:
        errs.append(f"{eid}: <svg data-lib-id> = {root.get('data-lib-id')!r}, phải bằng id")
    if root.get("data-lib-kind") != entry["kind"]:
        errs.append(f"{eid}: <svg data-lib-kind> sai (cần {entry['kind']})")
    vb = [float(x) for x in (root.get("viewBox") or "").split()]
    if len(vb) != 4 or vb[2:] != [float(x) for x in entry["size"]]:
        warns.append(f"{eid}: viewBox {vb} không khớp size {entry['size']} trong index")

    # màu: chỉ token
    if HEX.search(text) or FUNC_COLOR.search(text):
        errs.append(f"{eid}: có màu viết cứng (hex/rgb/hsl). Chỉ dùng var(--pal-<token>) — R2.5")
    for el in root.iter():
        for a in COLOR_ATTRS:
            v = el.get(a)
            if v is not None and not OK_COLOR.match(v.strip()):
                errs.append(f"{eid}: <{el.tag.split('}')[-1]} {a}={v!r}> không phải token màu")
                break
    for css in re.findall(r"<style[^>]*>(.*?)</style>", text, re.S):  # HyperFrames scoper bỏ cả khối <style> khi gặp ">"
        if ">" in css:
            errs.append(f"{eid}: CSS trong asset có combinator '>' — scoper của HyperFrames sẽ bỏ cả khối <style>; dùng selector hậu duệ (khoảng trắng)")
            break
    if "<text" in text or "<script" in text:
        errs.append(f"{eid}: không dùng <text> (phụ thuộc font) hoặc <script> trong asset")
    if re.search(r"<image\b|href=\"https?:", text):
        errs.append(f"{eid}: không nhúng ảnh/URL ngoài")

    # token tồn tại
    tokens = base_tokens if base_tokens is not None else load_palette(lib, entry.get("palettes", ["base"]))
    used = set(VAR_TOKEN.findall(text))
    unknown = sorted(t for t in used if t not in tokens)
    if unknown:
        errs.append(f"{eid}: token không có trong palette {entry.get('palettes')}: {unknown}")

    # trạng thái
    if entry["kind"] == "prop":
        attr, declared, default = "data-state", set(entry.get("states", [])), entry.get("default_state")
    else:
        attr, declared, default = "data-light", set(entry.get("light_states", [])), entry.get("default_light")
    in_css = set(re.findall(rf"\[{attr}='([^']+)'\]", text))
    in_dom = {el.get(attr) for el in root.iter() if el.get(attr)}
    if default not in in_dom:
        errs.append(f"{eid}: {attr} mặc định trong SVG ≠ {default!r} (thấy {sorted(in_dom)})")
    if declared and (in_css | {default}) != declared:
        errs.append(f"{eid}: trạng thái trong CSS {sorted(in_css | {default})} ≠ index {sorted(declared)}")

    classes = set()
    for el in root.iter():
        classes.update((el.get("class") or "").split())
    for part in entry.get("parts", {}):
        if part not in classes:
            errs.append(f"{eid}: part '{part}' không có class tương ứng trong SVG")
    if entry["kind"] == "location":
        for layer in entry.get("layers", []):
            if f"layer-{layer}" not in classes:
                errs.append(f"{eid}: thiếu lớp layer-{layer} (R4.2: 3 lớp xa/giữa/gần)")
        for name, s in {**entry.get("stand", {}), **entry.get("slots", {})}.items():
            if not (0 <= s["x"] <= entry["size"][0] and 0 <= s["y"] <= entry["size"][1]):
                errs.append(f"{eid}: anchor '{name}' nằm ngoài khung {entry['size']}")
    if entry["kind"] == "prop":
        for name, s in entry.get("slots", {}).items():
            if not (0 <= s["x"] <= entry["size"][0] and 0 <= s["y"] <= entry["size"][1]):
                errs.append(f"{eid}: slot '{name}' nằm ngoài khung {entry['size']}")

    if entry.get("sha256") and entry["sha256"] != sha(path):
        warns.append(f"{eid}: nội dung đã đổi so với index (sha) — chạy `library.py reindex`")
    return errs, warns


def ids_in(path: Path) -> list[str]:
    return re.findall(r'\bid="([^"]+)"', path.read_text(encoding="utf-8"))


def run_check() -> tuple[list[str], list[str], int]:
    """Kiểm toàn bộ library. Trả (lỗi, cảnh báo, số asset)."""
    idx = load_index()
    errs: list[str] = []
    warns: list[str] = []
    seen_ids: dict[str, str] = {}
    base_cache: dict[tuple, dict] = {}
    listed = set()
    for e in idx["items"]:
        listed.add(e["file"])
        key = tuple(e.get("palettes", ["base"]))
        if key not in base_cache:
            base_cache[key] = load_palette(LIB, list(key))
        er, wr = check_asset(e, LIB, base_cache[key])
        errs += er
        warns += wr
        if (LIB / e["file"]).exists():
            for i in ids_in(LIB / e["file"]):
                if i in seen_ids and seen_ids[i] != e["id"]:
                    errs.append(f"id SVG '{i}' trùng giữa {seen_ids[i]} và {e['id']} (lồng chung một cảnh sẽ vỡ) — thêm tiền tố")
                seen_ids[i] = e["id"]
    for sub in KIND_DIR.values():
        for f in sorted((LIB / sub).glob("*.svg")):
            if f"{sub}/{f.name}" not in listed:
                errs.append(f"{sub}/{f.name} không có trong index.json")
    arch = LIB / "rigs" / "archetypes.json"
    if arch.exists():
        base = load_palette(LIB, ["base", "folk-horror-vn"])
        cat = json.loads(arch.read_text(encoding="utf-8"))
        for table in ("archetypes", "outfits"):
            for name, v in cat.get(table, {}).items():
                for k, val in v["params"].items():
                    if isinstance(val, str) and k in ("robe", "sleeve", "pants", "sash", "skin", "hair_color", "brow_color") and val not in base:
                        errs.append(f"rigs/archetypes.json {table}.{name}.{k}: token '{val}' không có trong palette")
    return errs, warns, len(idx["items"])


def cmd_check(args) -> int:
    errs, warns, n = run_check()
    for w in warns:
        print("CẢNH BÁO:", w)
    for e in errs:
        print("LỖI:", e)
    print(f"library: {n} asset, {len(errs)} lỗi, {len(warns)} cảnh báo")
    return 1 if errs else 0


# ---- reindex / list / show --------------------------------------------------

def cmd_reindex(args) -> int:
    idx = load_index()
    changed = []
    for e in idx["items"]:
        p = LIB / e["file"]
        if not p.exists():
            print(f"LỖI: thiếu {e['file']}", file=sys.stderr)
            return 1
        new = sha(p)
        if e.get("sha256") != new:
            e["version"] = e.get("version", 0) + 1
            e["sha256"] = new
            changed.append(f"{e['id']} → v{e['version']}")
    save_index(idx)
    print("đã đổi: " + (", ".join(changed) if changed else "không có"))
    return 0


def cmd_list(args) -> int:
    idx = load_index()
    rows = []
    for e in idx["items"]:
        if args.kind and e["kind"] != args.kind:
            continue
        if args.tag and args.tag not in e.get("tags", []):
            continue
        st = e.get("states") or e.get("light_states") or []
        rows.append((e["kind"], e["id"], f"v{e.get('version', '?')}", ",".join(st), ",".join(e.get("tags", [])), e["description"]))
    cat = json.loads((LIB / "rigs" / "archetypes.json").read_text(encoding="utf-8"))
    if args.kind in (None, "archetype"):
        for k, v in cat["archetypes"].items():
            if not args.tag or args.tag == "rig":
                rows.append(("archetype", k, "", "", "rig", v["description"]))
    if args.kind in (None, "outfit"):
        for k, v in cat["outfits"].items():
            if not args.tag or args.tag == "rig":
                rows.append(("outfit", k, "", "", "rig", v["description"]))
    if args.kind in (None, "palette"):
        for f in sorted((LIB / "palettes").glob("*.json")):
            d = json.loads(f.read_text(encoding="utf-8"))
            rows.append(("palette", d["id"], "", "", "", d["description"][:90]))
    if args.json:
        print(json.dumps([dict(zip(("kind", "id", "ver", "states", "tags", "desc"), r)) for r in rows], ensure_ascii=False, indent=2))
        return 0
    for r in rows:
        print(f"{r[0]:<9} {r[1]:<18} {r[2]:<4} [{r[3]}] #{r[4]}\n          {r[5]}")
    print(f"-- {len(rows)} mục")
    return 0


def cmd_show(args) -> int:
    idx = load_index()
    for e in idx["items"]:
        if e["id"] == args.id:
            print(json.dumps(e, ensure_ascii=False, indent=2))
            print("file:", LIB / e["file"])
            return 0
    cat = json.loads((LIB / "rigs" / "archetypes.json").read_text(encoding="utf-8"))
    for table in ("archetypes", "outfits"):
        if args.id in cat[table]:
            print(json.dumps({table: {args.id: cat[table][args.id]}}, ensure_ascii=False, indent=2))
            return 0
    print(f"Không có '{args.id}' trong library", file=sys.stderr)
    return 1


# ---- use / lock ------------------------------------------------------------

def project_palette(proj: Path) -> tuple[list[str], dict]:
    b = proj / "script" / "bible.json"
    style = json.loads(b.read_text(encoding="utf-8-sig")).get("style", {}) if b.exists() else {}
    refs = style.get("palette_ref") or ["base"]
    return refs, load_palette(LIB, refs, style.get("palette", {}))


def cmd_use(args) -> int:
    proj = Path(args.root) / args.project
    if not proj.exists():
        print(f"LỖI: không có {proj}", file=sys.stderr)
        return 1
    idx = {e["id"]: e for e in load_index()["items"]}
    refs, tokens = project_palette(proj)
    lock_path = proj / "assets" / "LIBRARY.lock.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {"items": {}}
    rc = 0
    for iid in args.ids:
        e = idx.get(iid)
        if not e:
            print(f"LỖI: '{iid}' không có trong library (list để xem). Muốn tạo mới: làm đúng chuẩn rồi promote.", file=sys.stderr)
            rc = 1
            continue
        errs, _ = check_asset(e)
        if errs:
            print("LỖI: asset library không đạt chuẩn:\n  " + "\n  ".join(errs), file=sys.stderr)
            rc = 1
            continue
        dest_dir = proj / "assets" / PROJECT_DIR[e["kind"]]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / Path(e["file"]).name
        dest.write_text(inject_palette((LIB / e["file"]).read_text(encoding="utf-8"), tokens, e["id"]), encoding="utf-8")
        lock["items"][iid] = {"kind": e["kind"], "version": e.get("version"), "sha256": e.get("sha256") or sha(LIB / e["file"]),
                              "file": str(dest.relative_to(proj))}
        print(f"đã chép {iid} v{e.get('version')} → {dest.relative_to(proj)}")
    lock["palette_ref"] = refs
    lock["palette_sha"] = hashlib.sha256(json.dumps(tokens, sort_keys=True).encode()).hexdigest()
    lock_path.write_text(json.dumps(lock, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return rc


def lock_drift(proj: Path) -> list[str]:
    """Danh sách lệch giữa LIBRARY.lock.json và library hiện tại (rỗng = khớp)."""
    lp = proj / "assets" / "LIBRARY.lock.json"
    if not lp.exists():
        return []
    lock = json.loads(lp.read_text(encoding="utf-8"))
    idx = {e["id"]: e for e in load_index()["items"]}
    out = []
    for iid, v in lock.get("items", {}).items():
        e = idx.get(iid)
        if not e:
            out.append(f"{iid}: đã bị xoá khỏi library")
        elif e.get("sha256") != v.get("sha256"):
            out.append(f"{iid}: library v{e.get('version')} khác bản project dùng v{v.get('version')} (chạy `use` lại nếu muốn nâng cấp)")
    return out


def cmd_lock_check(args) -> int:
    d = lock_drift(Path(args.root) / args.project)
    for x in d:
        print("LỆCH:", x)
    print("khớp" if not d else f"{len(d)} lệch")
    return 0 if not d else 1


# ---- sheet -----------------------------------------------------------------

SHEET_CSS = (
    "body{margin:0;padding:22px 26px 30px;background:var(--pal-wall_wood_dark);color:var(--pal-cloth_white);font:14px/1.35 system-ui,sans-serif}"
    "h1{font-size:19px;margin:0 0 14px}h2{font-size:13px;letter-spacing:.08em;text-transform:uppercase;opacity:.75;margin:20px 0 8px}"
    ".grid{display:flex;flex-wrap:wrap;gap:14px}figure{margin:0;background:var(--pal-wall_wood);border-radius:10px;padding:8px 8px 6px;text-align:center}"
    "figcaption{font-size:12px;opacity:.85;margin-top:4px}svg.cell{display:block}.row{display:flex;gap:10px;align-items:flex-end;flex-wrap:wrap}"
)


def render_png(html: Path, png: Path, width: int) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 800}, device_scale_factor=1.5)
        pg.goto(html.resolve().as_uri())
        pg.screenshot(path=str(png), full_page=True)
        b.close()


def cmd_sheet(args) -> int:
    idx = load_index()
    # token của MỌI palette mà asset tham chiếu (thiếu → fill không hợp lệ → ảnh đen)
    refs = ["base"] + sorted({p for e in idx["items"] for p in e.get("palettes", ["base"])} - {"base"})
    tokens = load_palette(LIB, refs)
    root_vars = ":root{" + ";".join(f"--pal-{k}:{v}" for k, v in tokens.items()) + "}"
    out = LIB / "sheets"
    out.mkdir(exist_ok=True)

    props = [e for e in idx["items"] if e["kind"] == "prop"]
    figs = []
    for e in props:
        txt = (LIB / e["file"]).read_text(encoding="utf-8")
        w, h = e["size"]
        k = 190 / max(w, h) if max(w, h) > 190 else 1
        for st in e["states"]:
            svg = txt.replace(f'data-state="{e["default_state"]}"', f'data-state="{st}"', 1)
            svg = svg.replace("<svg ", f'<svg class="cell" width="{w * k:.0f}" height="{h * k:.0f}" ', 1)
            figs.append(f"<figure>{svg}<figcaption>{e['id']} · {st}</figcaption></figure>")
    (out / "props.html").write_text(f"<!doctype html><meta charset=utf-8><style>{root_vars}{SHEET_CSS}</style><h1>Đạo cụ — mọi trạng thái</h1><div class='grid'>{''.join(figs)}</div>", encoding="utf-8")
    render_png(out / "props.html", out / "props.png", 1500)
    (out / "props.html").unlink()

    locs = [e for e in idx["items"] if e["kind"] == "location"]
    rows = []
    for e in locs:  # mỗi bối cảnh một hàng, đủ mọi trạng thái ánh sáng
        txt = (LIB / e["file"]).read_text(encoding="utf-8")
        figs = []
        for st in e["light_states"]:
            svg = txt.replace(f'data-light="{e["default_light"]}"', f'data-light="{st}"', 1)
            svg = svg.replace("<svg ", '<svg class="cell" width="300" height="169" ', 1)
            figs.append(f"<figure>{svg}<figcaption>{e['id']} · {st}</figcaption></figure>")
        rows.append(f"<div class='grid'>{''.join(figs)}</div>")
    (out / "locations.html").write_text(f"<!doctype html><meta charset=utf-8><style>{root_vars}{SHEET_CSS}.grid{{margin-bottom:14px}}</style><h1>Bối cảnh — mọi trạng thái ánh sáng (mỗi hàng một bối cảnh)</h1>{''.join(rows)}", encoding="utf-8")
    render_png(out / "locations.html", out / "locations.png", 2180)
    (out / "locations.html").unlink()
    print("đã render library/sheets/props.png, locations.png")
    return 0


# ---- promote ---------------------------------------------------------------

def cmd_promote(args) -> int:
    idx = load_index()
    if any(e["id"] == args.id for e in idx["items"]):
        print(f"LỖI: '{args.id}' đã có trong library. Sửa trực tiếp ở library rồi reindex (R2.3), đừng promote trùng.", file=sys.stderr)
        return 1
    src = Path(args.root) / args.project / args.file if not Path(args.file).is_absolute() else Path(args.file)
    if not src.exists():
        print(f"LỖI: không thấy {src}", file=sys.stderr)
        return 1
    dest_rel = f"{KIND_DIR[args.kind]}/{args.id}.svg"
    dest = LIB / dest_rel
    dest.write_text(strip_palette(src.read_text(encoding="utf-8")), encoding="utf-8")
    states = [s for s in args.states.split(",") if s]
    entry = {
        "id": args.id, "kind": args.kind, "file": dest_rel, "description": args.desc,
        "size": [int(x) for x in args.size.split(",")] if args.size else None,
        "tags": [t for t in (args.tags or "").split(",") if t], "palettes": ["base"],
        "origin": f"project:{args.project}",
    }
    if args.kind == "prop":
        entry.update(anchor="bottom-center", states=states, default_state=args.default or states[0], scene_s=float(args.scene_s or 0.5))
    else:
        entry.update(layers=["far", "mid", "near"], light_states=states, default_light=args.default or states[0], floor_y=900,
                     stand={}, slots={}, crop_9x16={})
    if entry["size"] is None:
        m = re.search(r'viewBox="[\d.\-]+\s+[\d.\-]+\s+([\d.]+)\s+([\d.]+)"', dest.read_text(encoding="utf-8"))
        entry["size"] = [int(float(m.group(1))), int(float(m.group(2)))] if m else [0, 0]
    if args.meta:
        entry.update(json.loads(args.meta))
    errs, warns = check_asset(entry)
    if errs:
        dest.unlink()
        print("Chưa đạt chuẩn library, không promote:\n  " + "\n  ".join(errs), file=sys.stderr)
        return 1
    idx["items"].append(entry)
    save_index(idx)
    cmd_reindex(args)
    print(f"đã promote {args.id} → library/{dest_rel}. Nhớ chạy `library.py sheet` và commit.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Quản lý library/ dùng chung.")
    ap.add_argument("--root", default="projects", help="thư mục chứa project")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--kind"); p.add_argument("--tag"); p.add_argument("--json", action="store_true"); p.set_defaults(f=cmd_list)
    p = sub.add_parser("show"); p.add_argument("id"); p.set_defaults(f=cmd_show)
    sub.add_parser("check").set_defaults(f=cmd_check)
    sub.add_parser("reindex").set_defaults(f=cmd_reindex)
    sub.add_parser("sheet").set_defaults(f=cmd_sheet)
    p = sub.add_parser("use"); p.add_argument("--project", required=True); p.add_argument("ids", nargs="+"); p.set_defaults(f=cmd_use)
    p = sub.add_parser("lock-check"); p.add_argument("--project", required=True); p.set_defaults(f=cmd_lock_check)
    p = sub.add_parser("promote")
    p.add_argument("--project", required=True); p.add_argument("--kind", required=True, choices=list(KIND_DIR))
    p.add_argument("--id", required=True); p.add_argument("--file", required=True, help="đường dẫn trong project, vd assets/props/x.svg")
    p.add_argument("--states", required=True, help="prop: data-state; location: data-light, cách nhau dấu phẩy")
    p.add_argument("--tags"); p.add_argument("--desc", required=True); p.add_argument("--size"); p.add_argument("--default")
    p.add_argument("--scene-s"); p.add_argument("--meta", help="JSON bổ sung (stand/slots/parts...)")
    p.set_defaults(f=cmd_promote)
    args = ap.parse_args()
    return args.f(args)


if __name__ == "__main__":
    sys.exit(main())
