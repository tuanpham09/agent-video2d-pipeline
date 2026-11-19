#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""list_voices.py — danh sách giọng preset của VieNeu-TTS.

vieneu >= 3.8 trả về 25 giọng chuẩn, nhãn dạng
``"⭐ Hải Đăng — Nam · Bắc · Phong cách tự nhiên"`` (⭐ = editors' pick) và tên cũ
được giữ làm alias (``Minh Quân`` → ``Hải Đăng``). Bản cũ (<= 3.7) trả về ~166
``voice_id`` gồm cả biến thể alias; script vẫn gộp được.

Dùng:
  python list_voices.py                    # bảng cho người đọc
  python list_voices.py --region Bắc
  python list_voices.py --sex Nữ --character Kể chuyện
  python list_voices.py --recommended
  python list_voices.py --json
  python list_voices.py --markdown
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REGION_ORDER = {"Bắc": 0, "Trung": 1, "Nam": 2}
SEX_ORDER = {"Nam": 0, "Nữ": 1}
STAR_CHARS = "⭐★✦✩✪*"


def strip_diacritics(value: str) -> str:
    value = value.replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in unicodedata.normalize("NFD", value) if unicodedata.category(c) != "Mn")


def canon_key(name: str) -> str:
    # Model sinh alias theo 2 kiểu: bỏ "đ" (oantrang) hoặc đổi "đ"->"d"
    # (doantrang). Bỏ hết "d" để hai kiểu gộp về một; tên tiếng Việt không có
    # cặp tối thiểu nào chỉ khác chữ "d" nên an toàn.
    value = strip_diacritics(name).lower()
    value = re.sub(r"^vieneu[\s_-]*", "", value)
    value = re.sub(r"[^a-z0-9]+", "", value).replace("d", "")
    return {"aamnhua": "aambua"}.get(value, value)


def has_diacritics(value: str) -> bool:
    return any(ord(c) > 127 for c in value)


def strip_star(label: str) -> tuple[str, bool]:
    """Tách dấu ⭐/★ ở đầu nhãn; trả ``(label_sạch, featured)``."""
    text = label.lstrip()
    featured = False
    while text and text[0] in STAR_CHARS:
        featured = True
        text = text[1:].lstrip()
    return text, featured


def parse_label(label: str) -> dict:
    clean, featured = strip_star(label)
    parts = [p.strip() for p in clean.split("·")]
    head = parts[0]
    if "—" in head:
        name, sex = [p.strip() for p in head.split("—", 1)]
    else:
        name, sex = head.strip(), ""
    region = parts[1].strip() if len(parts) > 1 else ""
    char = parts[2].strip() if len(parts) > 2 else ""
    if "Khuyên dùng" in char:
        featured = True
    char = re.sub(r"\s*\(.*?\)", "", char)
    char = char.replace("Phong cách ", "").replace("Giọng đọc ", "").strip()
    low = char.lower()
    if "trầm ấm" in low:
        char = "Trầm ấm (Studio)"
    elif "tự nhiên" in low:
        char = "Tự nhiên"
    elif "tin tức" in low:
        char = "Tin tức"
    elif "kể chuyện" in low:
        char = "Kể chuyện"
    elif "đọc truyện" in low:
        char = "Đọc truyện"
    elif not char:
        char = "Khác"
    region = region.replace("Miền ", "").strip()
    return {
        "name": name,
        "sex": sex,
        "region": region,
        "character": char,
        "recommended": featured,
        "raw": label,
    }


def score(entry: dict) -> int:
    name = entry["name"]
    value = 0
    if has_diacritics(name):
        value += 4
    if name[:1].isupper():
        value += 2
    if "_" in name:
        value -= 1
    if name.lower().startswith("vieneu"):
        value -= 6
    if " " not in name and len(name) > 3:
        value -= 1
    if entry.get("character") not in ("", "Khác"):
        value += 1
    if entry.get("recommended"):
        value += 8
    return value


def collect() -> tuple[list[dict], int, str | None]:
    """Trả ``(giọng, số nhãn model trả về, giọng mặc định)``."""
    from vieneu import Vieneu

    model = Vieneu()
    pairs = model.list_preset_voices()
    default_voice = getattr(model, "_default_voice", None)
    presets = getattr(model, "_preset_voices", {}) or {}

    groups: dict[str, list[dict]] = {}
    for label, voice_id in pairs:
        parsed = parse_label(label)
        parsed["id"] = voice_id
        parsed["label"] = label
        preset = presets.get(voice_id) or {}
        parsed["aliases"] = [str(a) for a in (preset.get("aliases") or [])]
        parsed["featured"] = preset.get("featured")
        if parsed["featured"] is not None:
            parsed["recommended"] = True
        groups.setdefault(canon_key(voice_id) or canon_key(parsed["name"]), []).append(parsed)

    voices: list[dict] = []
    for entries in groups.values():
        best = max(entries, key=lambda e: (score(e), len(e["label"])))
        best = dict(best)
        names = {e["id"] for e in entries}
        for entry in entries:
            names.update(entry.get("aliases") or [])
        names.discard(best["id"])
        best["aliases"] = sorted(names)
        voices.append(best)

    def sort_key(v: dict) -> tuple:
        featured = v.get("featured")
        return (
            REGION_ORDER.get(v["region"], 9),
            SEX_ORDER.get(v["sex"], 9),
            v["character"],
            v["name"],
        ) if featured is None else (
            -1, 0, "", str(featured).zfill(2)
        )

    # Editors' picks đứng đầu, giữ đúng thứ tự `featured`; phần còn lại theo vùng/giới.
    voices.sort(key=sort_key)
    return voices, len(pairs), default_voice


def main() -> int:
    ap = argparse.ArgumentParser(description="Liệt kê giọng preset VieNeu-TTS (đã gộp alias).")
    ap.add_argument("--region", help="Bắc | Trung | Nam")
    ap.add_argument("--sex", help="Nam | Nữ")
    ap.add_argument("--character", help="Tự nhiên | Tin tức | Kể chuyện | Đọc truyện | Studio")
    ap.add_argument("--recommended", action="store_true", help="chỉ giọng được đánh dấu khuyên dùng")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--markdown", action="store_true", help="xuất bảng markdown để dán vào docs")
    args = ap.parse_args()

    try:
        voices, total_ids, default_voice = collect()
    except ImportError:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "Chưa cài 'vieneu'. Chạy: pip install vieneu",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    selected = voices
    if args.region:
        selected = [v for v in selected if v["region"].casefold() == args.region.casefold()]
    if args.sex:
        selected = [v for v in selected if v["sex"].casefold() == args.sex.casefold()]
    if args.character:
        selected = [v for v in selected if v["character"].casefold() == args.character.casefold()]
    if args.recommended:
        selected = [v for v in selected if v["recommended"]]

    if args.json:
        print(
            json.dumps(
                {
                    "status": "success",
                    "default_voice": default_voice,
                    "total_labels": total_ids,
                    "total_voices": len(voices),
                    "filtered": len(selected),
                    "voices": [
                        {
                            "voice": v["name"],
                            "sex": v["sex"],
                            "region": v["region"],
                            "character": v["character"],
                            "recommended": v["recommended"],
                            "featured": v.get("featured"),
                            "default": v["name"] == default_voice,
                            "aliases": v["aliases"],
                        }
                        for v in selected
                    ],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if args.markdown:
        print("| Voice | Vùng | Giới | Phong cách | Ghi chú |")
        print("| --- | --- | --- | --- | --- |")
        for v in selected:
            notes = []
            if v["name"] == default_voice:
                notes.append("mặc định")
            if v["recommended"]:
                notes.append("★ khuyên dùng")
            if v["aliases"]:
                notes.append("alias: " + ", ".join(f"`{a}`" for a in v["aliases"]))
            print(f"| `{v['name']}` | {v['region']} | {v['sex']} | {v['character']} | {'; '.join(notes)} |")
        return 0

    region = sex = char = None
    for v in selected:
        if (v["region"], v["sex"], v["character"]) != (region, sex, char):
            region, sex, char = v["region"], v["sex"], v["character"]
            print(f"\n{region} · {sex} · {char}")
        star = " ★" if v["recommended"] else ""
        mark = " (mặc định)" if v["name"] == default_voice else ""
        print(f"  - {v['name']}{star}{mark}")
    print(f"\n{len(selected)}/{len(voices)} giọng ({total_ids} nhãn từ model)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
