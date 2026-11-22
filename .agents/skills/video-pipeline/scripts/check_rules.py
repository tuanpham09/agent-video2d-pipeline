#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate tuân thủ RULES.md ở cấp project (và library).

  python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/<slug>
        [--phase demo|full|final] [--fix] [--strict] [--json]

Kiểm những gì máy kiểm được:
  R0.1  PROJECT.md có tem "Luật áp dụng: RULES.md vN" khớp phiên bản hiện tại
  R0.5  AGENTS.md / CLAUDE.md lồng trong project mở đầu bằng dòng trỏ về RULES.md (--fix tự thêm)
  R2.1  mọi nhân vật/bối cảnh/đạo cụ trong bible có `lib` (id trong library) hoặc scope=project-only + reason
  R2.2  asset library dùng trong bible đã được `library.py use` (có trong LIBRARY.lock.json, file còn đó)
  R2.5  không hex/rgb trong params rig của bible và trong generator dựng cảnh của project
  R2.8  nhân vật có rig nên khai archetype (cảnh báo nếu chỉ ghi đè rời)
  R2.9  library.py check sạch
  R2.10 lock không lệch library (cảnh báo)
  R2.4/R8.4 (--phase final) asset trong assets/{props,bg} không có trong lock phải là project-only đã khai báo
CRAFT (craft-playbook.md; đề xuất R10.4/R10.7, AGENTS.md "Tay nghề"):
  mỗi nhân vật có rig trong bible phải có assets/rig/sheets/<id>.png (pose sheet để xem/duyệt)
  nếu đã dựng video (video_demo/ hoặc video/ có index.html): PROJECT.md phải có nhật ký gate nêu
  "snapshot"/"ảnh đã xem" (bằng chứng đã nhìn ảnh thật, không chỉ chạy lệnh)
Trạng thái bible so với library: states của prop ⊆ states library; light_states ⊆ light library.

Mã thoát 1 nếu có lỗi (--strict: cảnh báo cũng là lỗi).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import library as lib  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = lib.REPO
POINTER = "> **Luật chung của repo: đọc và tuân theo `RULES.md` (gốc repo) trước mọi việc. File này không được nới luật đó.**"
HEX = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGB = re.compile(r"\b(?:rgb|rgba|hsl|hsla)\s*\(", re.I)


def rules_version() -> int:
    m = re.search(r"Phiên bản luật:\s*\*{0,2}\s*(\d+)", (REPO / "RULES.md").read_text(encoding="utf-8"))
    return int(m.group(1)) if m else 0


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def nested_guides(proj: Path) -> list[Path]:
    out = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        for f in proj.rglob(name):
            if "node_modules" in f.parts or ".hyperframes" in f.parts:
                continue
            out.append(f)
    return sorted(out)


def check_project(proj: Path, phase: str, fix: bool) -> tuple[list[str], list[str], list[str]]:
    errs: list[str] = []
    warns: list[str] = []
    fixed: list[str] = []
    ver = rules_version()

    # R0.1
    pm = proj / "PROJECT.md"
    if pm.exists():
        txt = pm.read_text(encoding="utf-8")
        m = re.search(r"Luật áp dụng:\s*RULES\.md\s*v(\d+)", txt)
        if not m:
            (errs if phase == "final" else warns).append(f"R0.1: PROJECT.md chưa có dòng 'Luật áp dụng: RULES.md v{ver}'")
        elif int(m.group(1)) != ver:
            warns.append(f"R0.1: PROJECT.md ghi luật v{m.group(1)}, hiện là v{ver} — đọc lại RULES.md rồi cập nhật dòng này")
    else:
        warns.append("R0.1: không có PROJECT.md")

    # R0.5
    for f in nested_guides(proj):
        head = "\n".join(f.read_text(encoding="utf-8").splitlines()[:6])
        if "RULES.md" not in head:
            if fix:
                f.write_text(POINTER + "\n\n" + f.read_text(encoding="utf-8"), encoding="utf-8")
                fixed.append(f"R0.5: đã thêm dòng trỏ RULES.md vào {f.relative_to(REPO)}")
            else:
                errs.append(f"R0.5: {f.relative_to(REPO)} không mở đầu bằng dòng trỏ về RULES.md (chạy --fix)")

    bp = proj / "script" / "bible.json"
    if not bp.exists():
        errs.append("không có script/bible.json")
        return errs, warns, fixed
    bible = load(bp)
    idx = {e["id"]: e for e in lib.load_index()["items"]}
    lock_path = proj / "assets" / "LIBRARY.lock.json"
    lock = load(lock_path) if lock_path.exists() else {"items": {}}

    # palette_ref
    for ref in bible.get("style", {}).get("palette_ref", []):
        if not (lib.LIB / "palettes" / f"{ref}.json").exists():
            errs.append(f"R2.1: style.palette_ref '{ref}' không có trong library/palettes")

    # nhân vật
    arch = json.loads((lib.LIB / "rigs" / "archetypes.json").read_text(encoding="utf-8"))
    for c in bible.get("characters", []):
        rig = c.get("rig")
        if not rig:
            continue
        for k, v in rig.items():
            if isinstance(v, str) and HEX.fullmatch(v.strip()):
                errs.append(f"R2.5: nhân vật {c['id']}: rig.{k} = {v} là hex; dùng token màu")
        a, o = rig.get("archetype"), rig.get("outfit")
        if not a:
            warns.append(f"R2.8: nhân vật {c['id']} không khai archetype (tra library/rigs/archetypes.json trước; nếu cần khuôn mới thì thêm vào đó)")
        elif a not in arch["archetypes"]:
            errs.append(f"R2.1: nhân vật {c['id']}: archetype '{a}' không có trong library")
        if o and o not in arch["outfits"]:
            errs.append(f"R2.1: nhân vật {c['id']}: outfit '{o}' không có trong library")

    # bối cảnh & đạo cụ
    used_lib = set()
    for kind, key, state_key, lib_state_key in (
        ("location", "locations", "light_states", "light_states"),
        ("prop", "props", "states", "states"),
    ):
        for item in bible.get(key, []):
            iid = item.get("id", "?")
            if item.get("scope") == "project-only":
                if not item.get("reason"):
                    errs.append(f"R2.4: {kind} {iid} là project-only nhưng thiếu 'reason'")
                continue
            ref = item.get("lib")
            if not ref:
                errs.append(f"R2.1: {kind} {iid} không có 'lib' (id trong library) và không phải project-only — tra `library.py list` rồi gán, hoặc tạo mới theo chuẩn + promote")
                continue
            e = idx.get(ref)
            if not e or e["kind"] != kind:
                errs.append(f"R2.1: {kind} {iid}: lib '{ref}' không có trong library (hoặc sai loại)")
                continue
            used_lib.add(ref)
            allowed = set(e.get(lib_state_key, []))
            bad = [s for s in item.get(state_key, []) if s not in allowed]
            if bad:
                errs.append(f"R2.3: {kind} {iid}: trạng thái {bad} không có ở {ref} (library: {sorted(allowed)}); thêm state vào library, đừng bịa trong bible")

    # lock (R2.2)
    for ref in sorted(used_lib):
        ent = lock.get("items", {}).get(ref)
        if not ent:
            errs.append(f"R2.2: {ref} dùng trong bible nhưng chưa `library.py use` (không có trong LIBRARY.lock.json)")
        elif not (proj / ent["file"]).exists():
            errs.append(f"R2.2: {ref}: thiếu file {ent['file']} (chạy lại `library.py use`)")
    for d in lib.lock_drift(proj):
        warns.append(f"R2.10: {d}")

    # generator: hex (R2.5)
    for f in sorted(proj.rglob("*.py")):
        rel = f.relative_to(proj)
        if not re.match(r"(build|generate|compose)_", f.name):
            continue
        n = len(HEX.findall(f.read_text(encoding="utf-8", errors="ignore"))) + len(RGB.findall(f.read_text(encoding="utf-8", errors="ignore")))
        if n:
            legacy = any(part.startswith("preview") for part in rel.parts)
            (warns if legacy else errs).append(
                f"R2.5: {rel} có {n} màu viết cứng" + (" (generator preview cũ — thay bằng generator dùng library/token khi làm bản full)" if legacy else "; dùng token từ palette")
            )

    # CRAFT: pose sheet + bằng chứng đã xem ảnh (craft-playbook.md)
    for c in bible.get("characters", []):
        if c.get("rig") and not (proj / "assets" / "rig" / "sheets" / f"{c['id']}.png").exists():
            errs.append(f"CRAFT: nhân vật {c['id']} chưa có assets/rig/sheets/{c['id']}.png — chạy build_rig.py rồi MỞ pose sheet xem/duyệt (craft-playbook §2)")
    if any((proj / d / "index.html").exists() for d in ("video_demo", "video")):
        pm_txt = pm.read_text(encoding="utf-8") if pm.exists() else ""
        if not re.search(r"snapshot|ảnh đã xem", pm_txt, re.I):
            errs.append("CRAFT: đã dựng video nhưng nhật ký gate trong PROJECT.md không nêu snapshot/ảnh đã xem — render ảnh, MỞ xem, rồi ghi (craft-playbook §1, §8)")

    # phase final: asset chưa promote (R2.4/R8.4)
    if phase == "final":
        declared_project_only = {i["id"] for k in ("locations", "props") for i in bible.get(k, []) if i.get("scope") == "project-only"}
        locked_files = {v["file"] for v in lock.get("items", {}).values()}
        for sub in ("props", "bg"):
            d = proj / "assets" / sub
            if not d.exists():
                continue
            for f in sorted(d.glob("*.svg")):
                rel = str(f.relative_to(proj))
                if rel not in locked_files and f.stem not in declared_project_only:
                    errs.append(f"R2.4: {rel} không từ library và chưa khai project-only — `library.py promote` hoặc khai trong bible")
        for c in bible.get("characters", []):
            if c.get("rig") and not c["rig"].get("archetype"):
                errs.append(f"R2.8: nhân vật {c['id']} chưa có archetype (promote khuôn mới vào library/rigs/archetypes.json)")
    return errs, warns, fixed


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate tuân thủ RULES.md.")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--phase", choices=["demo", "full", "final"], default="demo")
    ap.add_argument("--fix", action="store_true", help="tự sửa những gì sửa được (dòng trỏ RULES.md)")
    ap.add_argument("--strict", action="store_true", help="cảnh báo cũng làm fail")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--skip-library", action="store_true", help="bỏ library.py check")
    args = ap.parse_args()

    proj = args.project.resolve()
    if not proj.exists():
        print(f"LỖI: không có {proj}", file=sys.stderr)
        return 1
    errs, warns, fixed = check_project(proj, args.phase, args.fix)
    if not args.skip_library:
        le, lw, _ = lib.run_check()
        errs += [f"R2.9 library: {e}" for e in le]
        warns += [f"library: {w}" for w in lw]

    failed = bool(errs) or (args.strict and bool(warns))
    if args.json:
        print(json.dumps({"ok": not failed, "phase": args.phase, "rules_version": rules_version(),
                          "errors": errs, "warnings": warns, "fixed": fixed}, ensure_ascii=False, indent=2))
    else:
        for x in fixed:
            print("ĐÃ SỬA:", x)
        for w in warns:
            print("CẢNH BÁO:", w)
        for e in errs:
            print("LỖI:", e)
        print(f"check_rules ({args.phase}, luật v{rules_version()}): {len(errs)} lỗi, {len(warns)} cảnh báo → {'FAIL' if failed else 'OK'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
