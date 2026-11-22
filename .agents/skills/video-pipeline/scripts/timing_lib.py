#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Thời điểm theo từ và quy đổi beat → giây. Dùng chung cho build_video.py và check_shots.py
(để generator và gate không bao giờ lệch nhau).

Nguồn mốc từ, theo thứ tự ưu tiên:
  1. line["words"] trong manifest — mốc THẬT (từ căn chỉnh ASR, khi đã có):
       [{"w": "Ở", "start": 0.00, "end": 0.21}, ...]  (giây, tính từ đầu line)
  2. ước lượng theo độ dài chữ và dấu câu trong line (đủ cho dựng nháp; không phải mốc thật).

Beat neo theo từ (shotlist):
  {"line_id": "S01_L07", "word": 3}              → bắt đầu từ thứ 3 (0-based)
  {"line_id": "S01_L07", "word": 3, "edge": "end"} → kết thúc từ thứ 3
  {"line_id": "S01_L07", "t": 2.4}              → giây tuyệt đối trong shot (cách cũ, vẫn hỗ trợ)

Dùng: from timing_lib import word_spans, beat_time  (thêm thư mục scripts/ vào sys.path)
"""
from __future__ import annotations

import re

# Dấu câu kéo dài thêm "trọng số" để ước lượng nghỉ tự nhiên sau từ (đơn vị: như một chữ cái).
PUNCT_EXTRA = {",": 1.5, ";": 2.0, ":": 2.0, ".": 3.0, "!": 3.0, "?": 3.0, "…": 3.0, "—": 2.0}
EPS = 1e-6


def _weight(token: str) -> float:
    letters = re.findall(r"\w", token)
    w = max(1.0, float(len(letters)))
    for ch in token:
        w += PUNCT_EXTRA.get(ch, 0.0)
    return w


def word_spans(text: str, start: float, duration: float, words: list[dict] | None = None) -> list[dict]:
    """Trả về [{"w", "start", "end", "punct"}] với start/end là giây TUYỆT ĐỐI của video-line.

    `start` là mốc bắt đầu của line trong manifest; `duration` là độ dài line.
    Nếu `words` (mốc thật) có sẵn và đủ số từ, dùng nó; ngược lại ước lượng theo trọng số.
    """
    tokens = text.split()
    if not tokens:
        return []
    if words and len(words) == len(tokens):
        return [
            {"w": tokens[i], "start": start + float(words[i]["start"]), "end": start + float(words[i]["end"]),
             "punct": tokens[i][-1:] if tokens[i][-1:] in PUNCT_EXTRA else ""}
            for i in range(len(tokens))
        ]
    weights = [_weight(t) for t in tokens]
    total = sum(weights)
    out, cur = [], start
    for tok, wgt in zip(tokens, weights):
        span = duration * wgt / total
        out.append({"w": tok, "start": cur, "end": cur + span, "punct": tok[-1:] if tok[-1:] in PUNCT_EXTRA else ""})
        cur += span
    if out:  # chống sai số làm tròn: từ cuối kết thúc đúng đuôi line
        out[-1]["end"] = start + duration
    return out


def beat_time(beat: dict, lines: dict, shot_abs0: float) -> float:
    """Giây trong shot (tính từ shot_abs0) của một beat. Ném ValueError nếu beat theo từ sai."""
    if "word" in beat:
        ln = lines[beat["line_id"]]
        spans = word_spans(ln["text"], ln["start"], ln["duration"], ln.get("words"))
        idx = int(beat["word"])
        if not (0 <= idx < len(spans)):
            raise ValueError(f"beat {beat.get('line_id')}: word={idx} ngoài 0..{len(spans) - 1}")
        key = "end" if beat.get("edge") == "end" else "start"
        return spans[idx][key] - shot_abs0
    if "t" not in beat:
        raise ValueError(f"beat {beat.get('line_id')}: thiếu cả `t` lẫn `word`")
    return float(beat["t"])


def sentence_ends(text: str, start: float, duration: float, words: list[dict] | None = None) -> list[float]:
    """Mốc (giây tuyệt đối) ngay sau các từ kết câu (. ! ? …) — chỗ người nghe gật."""
    return [s["end"] for s in word_spans(text, start, duration, words) if s["punct"] in (".", "!", "?", "…")]
