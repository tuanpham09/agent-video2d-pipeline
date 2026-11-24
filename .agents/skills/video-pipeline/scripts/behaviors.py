#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""behaviors.py — bung "hành vi mẫu" (macro) thành beat thường. Dùng chung cho build_video.py và check_shots.py
(generator và gate thấy cùng một danh sách beat, nên E5/E7/R6.1 vẫn áp dụng đủ).

Beat dùng macro trong shotlist:
  {"line_id": "S01_L07", "word": 9, "macro": "nhin_sang", "args": {"char": "host", "target": "me"}}
Neo thời gian (`t` | `word` + `edge`) lấy từ chính beat; mỗi bước của macro có `dt` (giây, cộng thêm).
Tất định: cùng đầu vào → cùng đầu ra. Không sửa dữ liệu đầu vào (trả bản sao).
Thư viện: library/behaviors/behaviors.json (chỉ thêm macro mới; không đổi tên/xoá, R2.3).

  python behaviors.py list            # liệt kê macro
  python behaviors.py check           # kiểm tra thư viện macro
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from timing_lib import beat_time  # noqa: E402

REPO = Path(__file__).resolve().parents[4]
LIB = REPO / "library" / "behaviors" / "behaviors.json"
STEP_KEYS = {"dt", "set", "move", "look", "react", "hand_over"}
ANCHOR_KEYS = ("line_id", "t", "word", "edge")
_PH = re.compile(r"\{([a-z_]+)\}")


def load_library(path: Path = LIB) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))["behaviors"]


def _sub(obj, args: dict):
    """Thay {tên} trong mọi chuỗi. Chuỗi chỉ gồm đúng một {tên} giữ nguyên kiểu giá trị (vd dur số)."""
    if isinstance(obj, dict):
        return {_sub(k, args): _sub(v, args) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sub(v, args) for v in obj]
    if isinstance(obj, str):
        m = _PH.fullmatch(obj)
        if m and m.group(1) in args:
            return args[m.group(1)]
        return _PH.sub(lambda mm: str(args[mm.group(1)]) if mm.group(1) in args else mm.group(0), obj)
    return obj


def resolve_args(name: str, macro: dict, given: dict) -> dict:
    params = macro.get("params", {})
    unknown = set(given) - set(params)
    if unknown:
        raise ValueError(f"macro '{name}': tham số lạ {sorted(unknown)} (hợp lệ: {sorted(params)})")
    out = {}
    for k, default in params.items():
        if k in given:
            out[k] = given[k]
        elif default is not None:
            out[k] = default
        else:
            raise ValueError(f"macro '{name}': thiếu tham số bắt buộc '{k}'")
    return out


def expand_shot(shot: dict, lines: dict, abs0: float, lib: dict | None = None) -> dict:
    """Trả shot mới: beat có `macro` được thay bằng các beat thường (cùng neo, cộng dt), `sfx` của macro thêm vào shot.sfx."""
    if not any("macro" in b for b in shot.get("beats", [])):
        return shot
    lib = lib if lib is not None else load_library()
    sid = shot.get("id", "?")
    new = copy.deepcopy(shot)
    beats, sfx = [], list(new.get("sfx", []))
    for b in new.get("beats", []):
        if "macro" not in b:
            beats.append(b)
            continue
        name = b["macro"]
        if name not in lib:
            raise ValueError(f"{sid}: macro '{name}' không có trong library/behaviors (có: {sorted(lib)})")
        m = lib[name]
        args = resolve_args(name, m, b.get("args", {}))
        t0 = beat_time({k: b[k] for k in ANCHOR_KEYS if k in b}, lines, abs0)
        do = b.get("do") or _sub(m["do"], args)
        for st in m["steps"]:
            nb = {k: b[k] for k in ANCHOR_KEYS if k in b}
            nb["dt"] = float(st.get("dt", 0.0))
            nb["do"] = do
            nb["physical"] = bool(m.get("physical", False))
            nb["from_macro"] = name
            for k in STEP_KEYS - {"dt"}:
                if k in st:
                    nb[k] = _sub(st[k], args)
            if "hand_over" in nb and "dur" in nb["hand_over"]:
                nb["hand_over"]["dur"] = float(nb["hand_over"]["dur"])
            if "move" in nb and "dur" in nb["move"]:
                nb["move"]["dur"] = float(nb["move"]["dur"])
            beats.append(nb)
        for fx in m.get("sfx", []):
            sfx.append({"cue": fx["cue"], "src": fx["src"], "t": round(t0 + float(fx.get("dt", 0.0)), 3), "from_macro": name})
    new["beats"] = beats
    new["sfx"] = sfx
    return new


def check_library(lib: dict) -> list[str]:
    errs = []
    for name, m in lib.items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            errs.append(f"{name}: id macro phải là [a-z][a-z0-9_]*")
        for k in ("desc", "params", "do", "steps"):
            if k not in m:
                errs.append(f"{name}: thiếu `{k}`")
        params = set(m.get("params", {}))
        if not m.get("steps"):
            errs.append(f"{name}: `steps` rỗng")
        for i, st in enumerate(m.get("steps", [])):
            extra = set(st) - STEP_KEYS
            if extra:
                errs.append(f"{name}.steps[{i}]: khoá lạ {sorted(extra)}")
            if not (set(st) & (STEP_KEYS - {"dt"})):
                errs.append(f"{name}.steps[{i}]: không có thao tác set/move/look/react/hand_over")
        blob = json.dumps([m.get("steps"), m.get("do")], ensure_ascii=False)
        for ph in set(_PH.findall(blob)):
            if ph not in params:
                errs.append(f"{name}: dùng {{{ph}}} nhưng không khai trong params")
        if m.get("physical") and not m.get("sfx"):
            errs.append(f"{name}: physical=true nhưng không có `sfx` (R6.1)")
        for fx in m.get("sfx", []):
            if not (REPO / fx["src"]).exists():
                errs.append(f"{name}: file SFX không tồn tại: {fx['src']}")
    return errs


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "list"
    lib = load_library()
    if cmd == "list":
        for n, m in lib.items():
            print(f"{n:16s} {', '.join(m['params'])} — {m['desc']}")
        return 0
    if cmd == "check":
        errs = check_library(lib)
        for e in errs:
            print("  ✗", e)
        print(f"behaviors: {len(lib)} macro, {len(errs)} lỗi")
        return 1 if errs else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
