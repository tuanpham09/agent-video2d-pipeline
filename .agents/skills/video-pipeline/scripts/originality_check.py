#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate chống reup: đo mức trùng LỜI giữa script.json và transcript nguồn.

Chỉ đo văn bản (cụm n từ liên tiếp). Không đo được cốt truyện, nhân vật, cú twist:
phần đó phải qua checklist "Viết lại" trong references/workflow-v2.md.

Dùng:
  python .agents/skills/video-pipeline/scripts/originality_check.py \
      --script projects/<slug>/script/script.json \
      --source projects/<slug>/source/transcript-sentences.json
  # nhiều nguồn: lặp --source; hỗ trợ .json (list câu / {text}) và .md/.txt (mỗi dòng 1 câu)

Mã thoát: 0 = qua gate, 1 = trùng quá ngưỡng.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def norm(text: str) -> list[str]:
    text = text.lower()
    text = re.sub(r"\[[^\]]*\]", " ", text)  # tag cảm xúc [cười]
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()


def ngrams(words: list[str], n: int) -> set[tuple[str, ...]]:
    return set(zip(*[words[i:] for i in range(n)])) if len(words) >= n else set()


def json_texts(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from json_texts(item)
    elif isinstance(node, dict):
        for key in ("text", "sentence"):
            if isinstance(node.get(key), str):
                yield node[key]
                return
        for value in node.values():
            if isinstance(value, (list, dict)):
                yield from json_texts(value)


def load_source(path: Path) -> list[str]:
    raw = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        return list(json_texts(json.loads(raw)))
    return [ln.strip() for ln in raw.splitlines() if ln.strip()]


def proper_names(sentences: list[str]) -> Counter:
    """Từ viết hoa không đứng đầu câu (tên người/địa danh), đếm tần suất."""
    counts: Counter = Counter()
    for sent in sentences:
        tokens = re.findall(r"[^\W\d_]+", sent)
        for tok in tokens[1:]:
            if tok[0].isupper() and len(tok) > 1:
                counts[tok.lower()] += 1
    return Counter({k: v for k, v in counts.items() if v >= 2})


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate chống reup: so lời script với transcript nguồn.")
    ap.add_argument("--script", type=Path, required=True)
    ap.add_argument("--source", type=Path, action="append", required=True)
    ap.add_argument("--n", type=int, default=4, help="độ dài cụm từ so khớp (mặc định 4)")
    ap.add_argument("--line-threshold", type=float, default=0.5, help="line coi là sao chép nếu overlap >= ngưỡng")
    ap.add_argument("--max-copied-pct", type=float, default=10.0, help="%% line sao chép tối đa để qua gate")
    ap.add_argument("--max-mean-overlap", type=float, default=0.20)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    script = json.loads(args.script.read_text(encoding="utf-8-sig"))
    lines = [(ln["id"], ln["text"]) for sc in script.get("scenes", []) for ln in sc.get("lines", [])]
    if not lines:
        print("✗ script.json chưa có line nào — không có gì để kiểm originality", file=sys.stderr)
        return 1

    source_sentences: list[str] = []
    for path in args.source:
        loaded = load_source(path)
        if not loaded:
            print(f"✗ nguồn rỗng hoặc không đọc được câu nào: {path}", file=sys.stderr)
            return 1
        source_sentences += loaded
    src_grams: set = set()
    src_norm_sentences: set[str] = set()
    for sent in source_sentences:
        words = norm(sent)
        src_grams |= ngrams(words, args.n)
        src_norm_sentences.add(" ".join(words))
    if not src_norm_sentences - {""}:
        print("✗ nguồn không có từ nào sau khi chuẩn hoá — gate không thể so sánh", file=sys.stderr)
        return 1
    # để bắt line ngắn bị cắt ra từ câu nguồn dài: tìm cụm liền mạch theo ranh giới từ
    src_blob = " " + " | ".join(src_norm_sentences) + " "
    min_frag = min(3, args.n)

    overlaps: list[float] = []
    copied: list[tuple[float, str, str]] = []
    exact = 0
    for lid, text in lines:
        words = norm(text)
        grams = ngrams(words, args.n)
        if " ".join(words) in src_norm_sentences:
            exact += 1
        if not grams:  # line ngắn hơn n từ: tính trùng nếu là cụm liền mạch của một câu nguồn
            frag = " " + " ".join(words) + " "
            hit = len(words) >= min_frag and frag in src_blob
            overlaps.append(1.0 if hit else 0.0)
        else:
            overlaps.append(len(grams & src_grams) / len(grams))
        if overlaps[-1] >= args.line_threshold:
            copied.append((overlaps[-1], lid, text))

    total = len(lines)
    copied_pct = 100.0 * len(copied) / total if total else 0.0
    mean_overlap = statistics.mean(overlaps) if overlaps else 0.0

    src_names = proper_names(source_sentences)
    script_words = set(w for _, t in lines for w in norm(t))
    kept_names = [n for n in src_names if n in script_words]
    name_retention = len(kept_names) / len(src_names) if src_names else 0.0

    errors: list[str] = []
    warnings: list[str] = []
    if copied_pct > args.max_copied_pct:
        errors.append(
            f"{len(copied)}/{total} line ({copied_pct:.0f}%) trùng >= {args.line_threshold:.0%} cụm {args.n} từ "
            f"với nguồn (ngưỡng {args.max_copied_pct:.0f}%)"
        )
    if mean_overlap > args.max_mean_overlap:
        errors.append(f"overlap trung bình {mean_overlap:.2f} > ngưỡng {args.max_mean_overlap:.2f}")
    if name_retention >= 0.6 and len(src_names) >= 5:
        warnings.append(
            f"giữ {len(kept_names)}/{len(src_names)} tên riêng của nguồn ({name_retention:.0%}): "
            "kiểm tra đã đổi nhân vật/địa danh chưa"
        )
    warnings.append("script này chỉ đo lời; cốt truyện/twist phải qua checklist 'Viết lại' (workflow-v2.md)")

    report = {
        "status": "ok" if not errors else "error",
        "lines": total,
        "copied_lines": len(copied),
        "copied_pct": round(copied_pct, 1),
        "exact_sentence_matches": exact,
        "mean_overlap": round(mean_overlap, 3),
        "proper_name_retention": round(name_retention, 2),
        "worst": [{"overlap": round(o, 2), "line": i, "text": t} for o, i, t in sorted(copied, reverse=True)[:10]],
        "errors": errors,
        "warnings": warnings,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"script   : {total} line | nguồn: {len(source_sentences)} câu")
        print(f"trùng    : {len(copied)} line ({copied_pct:.0f}%) >= {args.line_threshold:.0%}; khớp nguyên câu: {exact}")
        print(f"overlap  : trung bình {mean_overlap:.2f}")
        print(f"tên riêng: giữ {len(kept_names)}/{len(src_names)}")
        for o, i, t in sorted(copied, reverse=True)[:5]:
            print(f"   {o:.2f} {i}: {t[:90]}")
        for w in warnings:
            print(f"  ! {w}")
        for e in errors:
            print(f"  ✗ {e}")
        print("OK" if not errors else f"FAIL ({len(errors)} lỗi)")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
