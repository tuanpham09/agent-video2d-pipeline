#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm cấu trúc bốn file dữ liệu của project theo JSON Schema (roadmap v3, P0).

Kiểm: script/script.json, script/bible.json, script/shotlist.json, audio/manifest.json
Schema: .agents/skills/video-pipeline/schemas/<tên>.schema.json (draft 2020-12)

Mã thoát: 0 = đúng cấu trúc, 1 = có lỗi cấu trúc, 2 = thiếu thư viện jsonschema.
File không tồn tại: báo "bỏ qua" (manifest chỉ có sau khi đọc giọng); --require-all để coi là lỗi.
Dùng: python .agents/skills/video-pipeline/scripts/validate_schemas.py --project projects/<slug> [--require-all]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    print("Thiếu thư viện jsonschema. Cài: pip install jsonschema", file=sys.stderr)
    sys.exit(2)

HERE = Path(__file__).resolve().parent
SCHEMA_DIR = HERE.parent / "schemas"
TARGETS = {
    "script": "script/script.json",
    "bible": "script/bible.json",
    "shotlist": "script/shotlist.json",
    "manifest": "audio/manifest.json",
}


def fmt_path(err) -> str:
    parts = [str(p) for p in err.absolute_path]
    return "/".join(parts) if parts else "(gốc)"


def check(proj: Path, require_all: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []
    for name, rel in TARGETS.items():
        f = proj / rel
        if not f.exists():
            (errors if require_all else notes).append(f"{name}: không có {rel}" + ("" if require_all else " — bỏ qua"))
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            errors.append(f"{name}: JSON hỏng ở dòng {exc.lineno}: {exc.msg}")
            continue
        schema = json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        errs = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
        for e in errs[:50]:
            errors.append(f"{name} [{fmt_path(e)}]: {e.message[:200]}")
        if len(errs) > 50:
            errors.append(f"{name}: còn {len(errs) - 50} lỗi nữa")
        if not errs:
            notes.append(f"{name}: đúng cấu trúc ({rel})")
    return errors, notes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--require-all", action="store_true")
    args = ap.parse_args()
    errors, notes = check(args.project.resolve(), args.require_all)
    for n in notes:
        print("  ✓", n)
    for e in errors:
        print("  ✗", e)
    ok = not errors
    print(f"validate_schemas: {len(errors)} lỗi → {'OK' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
