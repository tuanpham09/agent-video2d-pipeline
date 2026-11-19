#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo khung project video mới trong ./projects/<slug>/.

Ví dụ:
  python .agents/skills/video-pipeline/scripts/scaffold_project.py "review-ai-2026" \
      --title "AI năm 2026 đã làm được gì" --format 9:16 --fps 30
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

FORMATS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}

PROJECT_MD = """# {title}

- Slug: `{slug}`
- Format: {fmt} ({w}×{h} @ {fps}fps)
- Tạo ngày: {today}

## Trạng thái

- [ ] 0. Brief — người xem, promise, kênh đích
- [ ] 1. Transcript + metadata (`source/`)
- [ ] 2. Kịch bản (`script/script.md`, `script/script.json`) — đã duyệt
- [ ] 3. Giọng đọc (`audio/voiceover.wav`, `audio/manifest.json`) — đã nghe
- [ ] 4. Dựng HyperFrames (`video/`) — preview đã duyệt
- [ ] 5. Render + QC (`output/final.mp4`)
- [ ] 6. Đóng gói (`output/publish.md`)

## Ghi chú / bài học

-
"""


def build_script_stub(slug: str, title: str, fmt: str, fps: int) -> dict:
    w, h = FORMATS[fmt]
    return {
        "meta": {
            "project": slug,
            "title": title,
            "format": fmt,
            "width": w,
            "height": h,
            "fps": fps,
            "language": "vi",
        },
        "characters": [
            {
                "id": "host",
                "name": "Người dẫn",
                "role": "narrator",
                "voice": "Hải Đăng",
                "temperature": 0.8,
            }
        ],
        "scenes": [],
    }


def write_new(path: Path, content: str, force: bool) -> bool:
    if path.exists() and not force:
        print(f"skip (đã tồn tại): {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Tạo khung project video.")
    ap.add_argument("slug", help="tên project, chữ thường, gạch nối")
    ap.add_argument("--title", default="Chưa đặt tên", help="tựa nháp")
    ap.add_argument("--format", default="9:16", choices=sorted(FORMATS))
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--root", default="projects", help="thư mục chứa project")
    ap.add_argument("--force", action="store_true", help="ghi đè file khung")
    args = ap.parse_args()

    slug = args.slug.strip().lower().replace(" ", "-")
    project = Path(args.root) / slug
    if project.exists() and not args.force:
        print(f"LỖI: {project} đã tồn tại. Dùng --force nếu muốn ghi đè file khung.", file=sys.stderr)
        return 1

    for sub in (
        "source",
        "script",
        "audio/lines",
        "audio/scenes",
        "assets/fonts",
        "assets/images",
        "assets/music",
        "assets/sfx",
        "video",
        "output",
    ):
        (project / sub).mkdir(parents=True, exist_ok=True)

    w, h = FORMATS[args.format]
    created = 0

    created += write_new(
        project / "PROJECT.md",
        PROJECT_MD.format(
            title=args.title, slug=slug, fmt=args.format, w=w, h=h, fps=args.fps, today=date.today()
        ),
        args.force,
    )

    script_path = project / "script" / "script.json"
    created += write_new(
        script_path,
        json.dumps(build_script_stub(slug, args.title, args.format, args.fps), ensure_ascii=False, indent=2) + "\n",
        args.force,
    )

    created += write_new(
        project / "script" / "brief.md",
        f"""# Brief — {args.title}

## Người xem mục tiêu
- Một câu: ...

## Promise (họ nhận được gì)
- ...

## Góc tiếp cận / khác biệt
- ...

## Nguồn
- Transcript: `source/...`
- Video gốc: ...
- Ghi chú: ...
""",
        args.force,
    )

    created += write_new(project / "audio" / "voice_map.json", "{}\n", args.force)
    created += write_new(project / "source" / ".gitkeep", "", args.force)
    created += write_new(project / "output" / ".gitkeep", "", args.force)

    print(json.dumps(
        {
            "status": "ok",
            "project": str(project.resolve()),
            "files_created": created,
            "next": [
                f'python .agents/skills/voice-sync/scripts/build_voiceover.py --script "{script_path}" --out "{project / "audio"}"',
                f'npx hyperframes init "{project / "video"}" --skip-skills --non-interactive --resolution '
                + {"9:16": "portrait", "16:9": "landscape", "1:1": "square"}[args.format],
            ],
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
