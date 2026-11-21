#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo khung project video mới trong ./projects/<slug>/ theo workflow v2.

Chế độ (xem references/workflow-v2.md):
  a  làm video từ URL (QA nguồn -> viết lại chống reup)        [mặc định]
  b  clone công thức video từ URL (QA + style_sheet + viết lại)
  c  làm video từ ý tưởng (idea -> concept -> outline -> kịch bản)

Ví dụ:
  python .agents/skills/video-pipeline/scripts/scaffold_project.py "review-ai-2026" \
      --title "AI năm 2026 đã làm được gì" --format 9:16 --mode a
  python .agents/skills/video-pipeline/scripts/scaffold_project.py "truyen-ma-lang-x" \
      --mode c --format 16:9 --speed 1.3
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[4]


def rules_version() -> int:
    """Phiên bản luật hiện tại trong RULES.md (để ghi tem vào PROJECT.md)."""
    f = REPO / "RULES.md"
    m = re.search(r"Phiên bản luật:\s*\*{0,2}\s*(\d+)", f.read_text(encoding="utf-8")) if f.exists() else None
    return int(m.group(1)) if m else 1


FORMATS = {
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
    "1:1": (1080, 1080),
}

MODE_NAMES = {
    "a": "A — làm mới từ URL",
    "b": "B — clone công thức từ URL",
    "c": "C — từ ý tưởng",
}

EMOTION_VOCAB = [
    "calm", "focused", "worried", "afraid", "shocked", "dread",
    "sad", "grief", "angry", "suspicious", "relieved",
]

def mode_aware(text: str, mode: str) -> str:
    """Chế độ C không có transcript nguồn: originality_check.py (cần --source) không áp dụng → thay bằng quyết định I4."""
    if mode != "c":
        return text
    text = text.replace(" · `originality_check.py` · ", " · ý tưởng gốc: quyết định I4 trong `script/concept.md` · ")
    text = text.replace("- [ ] `originality_check.py` chạy lại trên script cuối", "- [ ] Ý tưởng gốc: đối chiếu lại quyết định I4 (`script/concept.md`) với script cuối")
    return text


PHASE_SOURCE = """\
## Giai đoạn A — QA nguồn
- [ ] `source/qa.md`: loại nội dung, tình trạng quyền, ý tưởng chung vs biểu đạt riêng, mức rủi ro
- [ ] 👤 Người dùng xác nhận quyết định PROCEED / CẦN XIN PHÉP / DỪNG
{style_line}
## Giai đoạn B — Viết lại chống reup
- [ ] `script/rewrite_plan.md` + `script/diff_matrix.md`
- [ ] `script/script.md` + `script/script.json`
- [ ] `originality_check.py` = OK
- [ ] 👤 Duyệt script + packaging
"""

PHASE_IDEA = """\
## Giai đoạn I — Ý tưởng (chế độ C)
- [ ] I1 `script/idea.md` — xác nhận ý hiểu 👤
- [ ] I2 `script/concept.md` + `script/bible.json` — thể loại, nhân vật, bối cảnh 👤
- [ ] I3 `script/outline.md` — đề cương, thời lượng mục tiêu 👤
- [ ] I4 kiểm tra ý tưởng gốc (không dùng tác phẩm có bản quyền)
- [ ] I5 `script/script.md` + `script/script.json` — đo thời lượng bằng `--dry-run` 👤
"""

PROJECT_MD = """# {title}

- Slug: `{slug}`
- Chế độ: {mode_name}
- Format: {fmt} ({w}×{h} @ {fps}fps) · tốc độ đọc `--speed {speed}`
- Tạo ngày: {today}

**Luật áp dụng: RULES.md v{rules_v}** — đọc `RULES.md` (gốc repo) trước mọi việc; luật cao hơn skill/workflow/file này.

Quy trình: `.agents/skills/video-pipeline/references/workflow-v2.md`. Cập nhật file này sau mỗi gate.

{phase_front}
## Giai đoạn C — Demo 30–40 s
- [ ] Chọn lát cắt, tạo `script/script.demo.json` (giữ nguyên id line)
- [ ] C0 tra thư viện: `library.py list` → gán `lib` cho từng nhân vật (archetype/outfit), bối cảnh, đạo cụ trong bible (R2.1); `library.py use` để chốt phiên bản
- [ ] C1 bible + rig + pose sheet (`script/bible.json`, `assets/rig|props|bg/`); asset chưa có trong library → làm đúng chuẩn library (R2.5–R2.7)
- [ ] C2 `script/shotlist.json` — mỗi line ≥ 1 beat diễn
- [ ] C3 giọng (`audio/manifest.json`) — đã nghe
- [ ] C4 SFX theo cue
- [ ] C5 dựng HyperFrames (`video/`)
- [ ] C6 QC: `check_rules.py` · `originality_check.py` · `check_shots.py --scenes ...` · `check_sync.py` · `hyperframes check --json`
- [ ] 👤 Duyệt demo: nhân vật · diễn xuất · SFX & mix · bối cảnh/đạo cụ · nhịp shot · giọng

## Đã khóa ở demo
(điền khi duyệt: bible, giọng + tốc độ, thông số mix, style, danh sách cue SFX)

-

## Giai đoạn D — Full
- [ ] Voice full → `check_sync.py`
- [ ] Shotlist + `check_shots.py --scenes Sxx` theo từng scene, kiểm liên tục mỗi 5 scene
- [ ] QC cuối (không `--scenes`), duration = `manifest.duration` ± 0,1 s
- [ ] Render `--quality delivery` → `output/final.mp4`

## Giai đoạn E — Đóng gói
- [ ] `output/publish.md` theo `references/packaging.md`
- [ ] `originality_check.py` chạy lại trên script cuối
- [ ] **Đưa asset mới vào library** (R2.4): `library.py promote ...` hoặc khai `"scope": "project-only"` + `reason` trong bible; `check_rules.py --phase final` sạch

## Ngoại lệ so với RULES.md
(chỉ khi người dùng cho phép rõ ràng: luật nào, vì sao, người dùng nói gì)

- (chưa có)

## Ghi chú / bài học

-
"""

BIBLE_STUB = {
    "emotion_vocab": EMOTION_VOCAB,
    "style": {"line": "", "palette_ref": ["base"], "palette": {}},
    "characters": [],
    "locations": [],
    "props": [],
}

QA_MD = """# QA nguồn — {title}

- URL: ...
- Chế độ: {mode_name}

## Loại nội dung
- [ ] truyện hư cấu / kiến thức / tin tức / review / hướng dẫn: ...

## Tình trạng quyền
- [ ] tự do (CC, public domain) / có giấy phép / chưa rõ: ...
- Giấy phép/xin phép: `source/permission.md` (bắt buộc nếu rủi ro CAO)

## Ý tưởng chung (được dùng)
-

## Biểu đạt riêng của tác giả (KHÔNG dùng)
- cốt truyện cụ thể, tên + quan hệ nhân vật, thứ tự tiết lộ, twist, kết, chi tiết đặc trưng, câu chữ:

## Sự thật cần đối chiếu (≥ 2 nguồn độc lập)
-

## Mức rủi ro
- THẤP / TRUNG BÌNH / CAO: ...

## Quyết định
- PROCEED / CẦN XIN PHÉP / DỪNG: ...
"""

STYLE_SHEET_MD = """# Style sheet (chế độ B) — chỉ ghi số đo, không dựng lại khung hình của nguồn

- Nhịp shot trung bình: ... s
- Tỉ lệ cỡ cảnh (wide / medium / close / macro / ots): ...
- Bảng màu: ...
- Font / kiểu chữ: ...
- Cấu trúc hook → payoff: ...
- Mật độ SFX, kiểu mix: ...
"""

REWRITE_PLAN_MD = """# Kế hoạch viết lại — {title}

## Giữ (chỉ ý tưởng chung)
-

## Đổi
- Nhân vật (tên, quan hệ, nghề, tuổi):
- Bối cảnh (địa danh, thời điểm, đạo cụ trung tâm):
- Cấu trúc kể (ngôi kể / thứ tự tiết lộ):
- Điểm ngoặt (≥ 2 trong 3 bị thay) và kết:
"""

DIFF_MATRIX_MD = """# Diff matrix — beat gốc → beat mới

| # | Beat gốc | Beat mới | Khác ở đâu (nhân vật / bối cảnh / diễn biến / kết) |
| - | --- | --- | --- |
| 1 | | | |
"""

IDEA_MD = """# I1 — Xác nhận ý hiểu

## Ý tưởng gốc (nguyên văn)
>

## Ý hiểu (5–7 dòng): chuyện gì xảy ra, ai là trung tâm, vì sao người xem quan tâm, cảm xúc muốn tạo
-

## Promise
- Sau video này, người xem sẽ ______

## Người xem mục tiêu
-

## Điểm chưa chắc (tối đa 3 câu hỏi)
1.
"""

CONCEPT_MD = """# I2 — Thể loại, nhân vật, bối cảnh

- Thể loại + tông: ...
- Kênh đích + format: ...
- Tốc độ đọc: `--speed {speed}`
- Phong cách hình (nét vẽ, bảng màu, ánh sáng chủ đạo): ...

## Nhân vật (đồng bộ với `bible.json`)
| id | Tên | Tuổi / nghề / quan hệ | Ngoại hình, trang phục | Giọng VieNeu |
| - | --- | --- | --- | --- |

## Bối cảnh (tối đa 3–4 địa điểm cho bản đầu)
| id | Địa điểm | Thời điểm | Đạo cụ trung tâm + trạng thái |
| - | --- | --- | --- |

## Kiểm tra ý tưởng gốc (I4)
- [ ] không dùng nhân vật/thế giới/khẩu quyết/cốt truyện của tác phẩm có bản quyền
- [ ] tập tục/truyền thuyết chỉ là motif; cách kể và nhân vật là của dự án
- [ ] sự thật dùng trong truyện có nguồn trong `brief.md`
"""

OUTLINE_MD = """# I3 — Đề cương

- Thời lượng mục tiêu: ___ phút (≈ 216 từ/phút ở 1.3×) · số chương: ___
- Hook ≤ 30 s khớp promise · re-hook ở 40–60% · pattern interrupt mỗi ~8–10 phút (video > 15 phút)

## Chương 1 — ...
- Mục tiêu:
- Beat chính / điểm ngoặt:
- Vòng lặp tò mò (mở → đóng):
- Nhân vật / địa điểm:
"""

BRIEF_MD = """# Brief — {title}

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
    ap = argparse.ArgumentParser(description="Tạo khung project video (workflow v2).")
    ap.add_argument("slug", help="tên project, chữ thường, gạch nối")
    ap.add_argument("--title", default="Chưa đặt tên", help="tựa nháp")
    ap.add_argument("--mode", default="a", choices=sorted(MODE_NAMES), help="a: URL, b: clone URL, c: từ ý tưởng")
    ap.add_argument("--format", default="9:16", choices=sorted(FORMATS))
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--speed", type=float, default=None, help="tốc độ đọc ghi vào PROJECT.md (mặc định 1.25; truyện ma/chế độ c: 1.3)")
    ap.add_argument("--root", default="projects", help="thư mục chứa project")
    ap.add_argument("--force", action="store_true", help="ghi đè file khung")
    args = ap.parse_args()
    if args.speed is not None and not (1.2 <= args.speed <= 1.3):
        ap.error(f"--speed {args.speed} ngoài dải cho phép 1.2–1.3 (RULES R6.3); cần ngoại lệ thì người dùng nói rõ và ghi vào PROJECT.md mục Ngoại lệ")

    speed = args.speed if args.speed is not None else (1.3 if args.mode == "c" else 1.25)
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
        "assets/rig",
        "assets/props",
        "assets/bg",
        "video",
        "output",
    ):
        (project / sub).mkdir(parents=True, exist_ok=True)

    w, h = FORMATS[args.format]
    mode_name = MODE_NAMES[args.mode]
    created = 0

    if args.mode == "c":
        phase_front = PHASE_IDEA
    else:
        style_line = "- [ ] `source/style_sheet.md` — nhịp/cỡ cảnh/màu/font/mix đã đo (chỉ chế độ B)\n" if args.mode == "b" else ""
        phase_front = PHASE_SOURCE.format(style_line=style_line)

    created += write_new(
        project / "PROJECT.md",
        mode_aware(PROJECT_MD.format(
            title=args.title, slug=slug, mode_name=mode_name, fmt=args.format,
            w=w, h=h, fps=args.fps, speed=speed, today=date.today(), phase_front=phase_front,
            rules_v=rules_version(),
        ), args.mode),
        args.force,
    )

    script_path = project / "script" / "script.json"
    created += write_new(
        script_path,
        json.dumps(build_script_stub(slug, args.title, args.format, args.fps), ensure_ascii=False, indent=2) + "\n",
        args.force,
    )
    created += write_new(project / "script" / "brief.md", BRIEF_MD.format(title=args.title), args.force)
    created += write_new(
        project / "script" / "bible.json",
        json.dumps(BIBLE_STUB, ensure_ascii=False, indent=2) + "\n",
        args.force,
    )
    created += write_new(
        project / "script" / "shotlist.json",
        json.dumps({"meta": {"project": slug}, "shots": []}, ensure_ascii=False, indent=2) + "\n",
        args.force,
    )

    fmt_args = dict(title=args.title, mode_name=mode_name, speed=speed)
    if args.mode == "c":
        created += write_new(project / "script" / "idea.md", IDEA_MD, args.force)
        created += write_new(project / "script" / "concept.md", CONCEPT_MD.format(**fmt_args), args.force)
        created += write_new(project / "script" / "outline.md", OUTLINE_MD, args.force)
    else:
        created += write_new(project / "source" / "qa.md", QA_MD.format(**fmt_args), args.force)
        created += write_new(project / "script" / "rewrite_plan.md", REWRITE_PLAN_MD.format(**fmt_args), args.force)
        created += write_new(project / "script" / "diff_matrix.md", DIFF_MATRIX_MD, args.force)
        if args.mode == "b":
            created += write_new(project / "source" / "style_sheet.md", STYLE_SHEET_MD, args.force)

    created += write_new(project / "audio" / "voice_map.json", "{}\n", args.force)
    created += write_new(project / "source" / ".gitkeep", "", args.force)
    created += write_new(project / "output" / ".gitkeep", "", args.force)

    if args.mode == "c":
        first = "Làm Giai đoạn I1: viết script/idea.md (nhắc lại ý hiểu) và chờ người dùng xác nhận."
    else:
        first = (
            "Làm Giai đoạn A: lấy transcript, copy transcript.md + transcript-sentences.json + meta.json vào source/ "
            "(originality_check.py đọc source/transcript-sentences.json), rồi điền source/qa.md; chờ người dùng xác nhận."
        )

    print(json.dumps(
        {
            "status": "ok",
            "project": str(project.resolve()),
            "mode": mode_name,
            "speed": speed,
            "files_created": created,
            "next": [
                "Đọc RULES.md (gốc repo). Trước khi tạo nhân vật/đạo cụ/bối cảnh: `python .agents/skills/video-pipeline/scripts/library.py list` (R2.1).",
                first,
                "Chưa chạy TTS/HyperFrames trước khi script được duyệt (xem references/workflow-v2.md).",
                "khi script đã duyệt: tạo script/script.demo.json (lát cắt 30–40 s, giữ nguyên id) và chỉ làm giọng cho bản demo: "
                f'python .agents/skills/voice-sync/scripts/build_voiceover.py --script "{project / "script" / "script.demo.json"}" '
                f'--out "{project / "audio"}" --speed {speed}',
                "giọng cho script ĐẦY ĐỦ (script/script.json) chỉ chạy ở Giai đoạn D, sau khi người dùng duyệt demo.",
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
