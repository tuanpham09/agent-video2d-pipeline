#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Khóa timing giọng đã duyệt (Opt round 2, mục 5).

VieNeu đọc lại cùng một câu cũng lệch ±0,1s mỗi lần, nên rebuild giọng vô cớ
làm mọi timing downstream (shot, SFX, render) trôi theo. Quy tắc: khi giọng đã
duyệt, chạy script này để ghi `audio/timing.md` (thời lượng từng line + SHA của
`script.json`), rồi commit `audio/manifest.json` + `audio/timing.md`. Chỉ rebuild
giọng khi đổi chữ — chạy lại script này sẽ cảnh báo nếu script đã đổi so với
bản khóa (lúc đó mới đọc lại giọng + khóa lại).

Dùng (từ gốc repo):
  python .agents/skills/voice-sync/scripts/freeze_manifest.py --project projects/<slug>
  python .agents/skills/voice-sync/scripts/freeze_manifest.py --project projects/<slug> --force   # khóa lại sau khi đổi chữ + đọc lại giọng
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path


def script_sha(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:12]


def main() -> int:
    ap = argparse.ArgumentParser(description="Khóa timing giọng đã duyệt vào audio/timing.md.")
    ap.add_argument("--project", type=Path, required=True, help="thư mục project, vd projects/<slug>")
    ap.add_argument("--force", action="store_true", help="khóa lại (sau khi đổi chữ + đọc lại giọng)")
    args = ap.parse_args()

    proj = args.project
    manifest_path = proj / "audio" / "manifest.json"
    script_path = proj / "script" / "script.json"
    timing_path = proj / "audio" / "timing.md"
    if not manifest_path.is_file():
        print(f"LỖI: chưa có {manifest_path} — chạy build_voiceover.py trước", file=sys.stderr)
        return 1
    if not script_path.is_file():
        print(f"LỖI: thiếu {script_path}", file=sys.stderr)
        return 1

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sha = script_sha(script_path)

    old_sha: str | None = None
    if timing_path.is_file():
        for line in timing_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("Script SHA:"):
                old_sha = line.split(":", 1)[1].strip()
    if old_sha and old_sha != sha and not args.force:
        print(f"CẢNH BÁO: script.json đã đổi so với bản khóa (SHA {old_sha} -> {sha}).", file=sys.stderr)
        print("  Chỉ khóa lại sau khi đã đọc lại giọng cho chữ mới (dùng --force).", file=sys.stderr)
        return 2

    chars = manifest.get("characters", {})
    rows = ["| Line | Nhân vật (giọng, tốc độ) | Bắt đầu | Dài | Chữ |",
            "| --- | --- | --- | --- | --- |"]
    for scene in manifest.get("scenes", []):
        for ln in scene.get("lines", []):
            c = chars.get(ln.get("speaker"), {})
            who = f"{ln.get('speaker')} ({c.get('voice', '?')}, {ln.get('speed', c.get('speed', '?'))})"
            rows.append(f"| {ln['id']} | {who} | {ln['start']:.2f}s | {ln['duration']:.2f}s | {ln['text']} |")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    timing_path.write_text(
        "# Timing giọng đã duyệt (khóa)\n\n"
        f"Khóa lúc: {stamp}\n\n"
        f"Script SHA: {sha}\n\n"
        f"Tổng thời lượng manifest: **{manifest.get('duration', 0):.2f}s**\n\n"
        + "\n".join(rows) + "\n\n"
        "Luật: chỉ rebuild giọng khi đổi chữ (xem workflow-v2.md, giai đoạn D). "
        "Chạy lại freeze_manifest.py mà script đã đổi thì nó cảnh báo, không ghi đè.\n",
        encoding="utf-8",
    )
    n = sum(len(s.get("lines", [])) for s in manifest.get("scenes", []))
    print(f"đã khóa timing: {n} line, tổng {manifest.get('duration', 0):.2f}s, script SHA {sha} -> {timing_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
