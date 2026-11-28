#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate âm thanh giọng đọc (RULES R12.3) — chạy SAU build_voiceover.py, TRƯỚC khi dựng video.

Đọc: <project>/audio/manifest.json + audio/lines/*.wav + audio/voiceover.wav

Kiểm (E = lỗi làm fail, W = cảnh báo):
  E1  manifest tồn tại, engine = vieneu-v3-turbo, speed ∈ [1.2, 1.3] (R6.3)
  E2  mọi line có file wav; sample rate = manifest.sample_rate
  E3  thời lượng file wav khớp manifest.duration (±0.05 s) — lệch = timing không thật
  E4  không clip: peak < 0.99 (full scale)
  E5  không câm: line có chữ mà RMS > −55 dBFS
  E6  các line không chồng nhau theo manifest (start_{i+1} ≥ start_i + duration_i − 0.001)
  E7  voiceover.wav tồn tại và dài ≈ tổng manifest (±0.1 s)
  W1  mức RMS mỗi line ngoài [−32, −12] dBFS (âm lượng lệch giữa các nhân vật)
  W2  khoảng lặng giữa hai line > 3 s (nhịp hụt)
  W3  khoảng lặng trong một line > 1.2 s (đọc ngắt bất thường)

Mã thoát: 0 = qua, 1 = có lỗi (--strict: cả cảnh báo).
Dùng:  python .agents/skills/voice-sync/scripts/check_audio.py --project projects/<slug> [--json] [--strict]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    import numpy as np
    import soundfile as sf
except ImportError as exc:  # pragma: no cover
    print(f"Thiếu thư viện: {exc.name}. Cài: pip install numpy soundfile", file=sys.stderr)
    sys.exit(2)

ENGINE = "vieneu-v3-turbo"
SPEED_MIN, SPEED_MAX = 1.2, 1.3
DUR_TOL = 0.05
TOTAL_TOL = 0.1
PEAK_MAX = 0.99
SILENT_DB = -55.0
LOUD_RANGE = (-32.0, -12.0)
GAP_LINE_MAX = 3.0
INNER_SILENCE_MAX = 1.2
SILENCE_FRAME_DB = -45.0
FRAME_S = 0.02


def db(x: float) -> float:
    return 20 * np.log10(max(x, 1e-9))


def longest_silence(samples: np.ndarray, sr: int) -> float:
    """Khoảng lặng dài nhất (giây) theo khung 20 ms, ngưỡng −45 dBFS."""
    n = int(sr * FRAME_S)
    if n <= 0 or len(samples) < n:
        return 0.0
    frames = samples[: len(samples) // n * n].reshape(-1, n)
    rms = np.sqrt((frames ** 2).mean(axis=1))
    quiet = db_arr(rms) < SILENCE_FRAME_DB
    best = cur = 0
    for q in quiet:
        cur = cur + 1 if q else 0
        best = max(best, cur)
    return best * FRAME_S


def db_arr(x: np.ndarray) -> np.ndarray:
    return 20 * np.log10(np.maximum(x, 1e-9))


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    return data.mean(axis=1), sr


def check(proj: Path, strict: bool) -> dict:
    errors: list[str] = []
    warns: list[str] = []
    man_path = proj / "audio" / "manifest.json"
    if not man_path.exists():
        return {"ok": False, "errors": ["E1: không có audio/manifest.json — chạy build_voiceover.py trên máy có VieNeu"],
                "warnings": [], "lines": 0}
    man = json.loads(man_path.read_text(encoding="utf-8-sig"))

    if man.get("engine") != ENGINE:
        errors.append(f"E1: engine '{man.get('engine')}' ≠ '{ENGINE}' — giọng không phải VieNeu v3 Turbo")
    speed = float(man.get("speed", 0))
    if not (SPEED_MIN <= speed <= SPEED_MAX):
        errors.append(f"E1: speed {speed} ngoài dải {SPEED_MIN}–{SPEED_MAX} (R6.3)")

    sr_man = int(man.get("sample_rate", 0))
    lines = [ln for sc in man["scenes"] for ln in sc["lines"]]
    missing: list[str] = []
    prev_end = None
    for ln in lines:
        lid = ln["id"]
        # E6: không chồng (theo manifest)
        if prev_end is not None and ln["start"] < prev_end - 0.001:
            errors.append(f"E6: {lid} bắt đầu {ln['start']:.3f}s trước khi câu trước kết thúc {prev_end:.3f}s")
        prev_end = ln["start"] + ln["duration"]

        wav = proj / ln["audio"]
        if not wav.exists():
            missing.append(lid)
            continue
        x, sr = load_mono(wav)
        if sr_man and sr != sr_man:
            errors.append(f"E2: {lid}: sample rate {sr} ≠ manifest {sr_man}")
        real = len(x) / sr
        if abs(real - ln["duration"]) > DUR_TOL:
            errors.append(f"E3: {lid}: file dài {real:.3f}s, manifest ghi {ln['duration']:.3f}s (lệch > {DUR_TOL}s)")
        peak = float(np.max(np.abs(x))) if len(x) else 0.0
        if peak >= PEAK_MAX:
            errors.append(f"E4: {lid}: clip (peak {peak:.3f} ≥ {PEAK_MAX})")
        rms_db = float(db(np.sqrt((x ** 2).mean()))) if len(x) else -120.0
        if ln.get("text", "").strip() and rms_db < SILENT_DB:
            errors.append(f"E5: {lid}: gần như câm (RMS {rms_db:.1f} dBFS)")
        if ln.get("text", "").strip() and not (LOUD_RANGE[0] <= rms_db <= LOUD_RANGE[1]):
            warns.append(f"W1: {lid}: RMS {rms_db:.1f} dBFS ngoài {LOUD_RANGE} — kiểm mức giữa các nhân vật")
        inner = longest_silence(x, sr)
        if inner > INNER_SILENCE_MAX:
            warns.append(f"W3: {lid}: khoảng lặng {inner:.2f}s bên trong câu (đọc ngắt bất thường)")

    if missing:
        head = ", ".join(missing[:5]) + (" …" if len(missing) > 5 else "")
        errors.append(f"E2: thiếu {len(missing)}/{len(lines)} file wav ({head}) — chạy build_voiceover.py trên máy có VieNeu")

    # W2: khoảng lặng giữa các line
    for a, b in zip(lines, lines[1:]):
        gap = b["start"] - (a["start"] + a["duration"])
        if gap > GAP_LINE_MAX:
            warns.append(f"W2: khoảng lặng {gap:.2f}s giữa {a['id']} và {b['id']}")

    # E7: voiceover tổng
    full = proj / man.get("full_audio", "audio/voiceover.wav")
    total = float(man.get("duration", 0))
    if not full.exists():
        errors.append(f"E7: thiếu {full.relative_to(proj)}")
    else:
        fx, fsr = sf.info(str(full)).frames, sf.info(str(full)).samplerate
        if abs(fx / fsr - total) > TOTAL_TOL:
            errors.append(f"E7: voiceover dài {fx / fsr:.3f}s, manifest ghi {total:.3f}s")

    failed = bool(errors) or (strict and bool(warns))
    return {"ok": not failed, "engine": man.get("engine"), "speed": speed, "lines": len(lines),
            "duration_s": total, "errors": errors, "warnings": warns}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rep = check(args.project.resolve(), args.strict)
    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        for w in rep["warnings"]:
            print("  !", w)
        for e in rep["errors"]:
            print("  ✗", e)
        print(f"check_audio: {rep['lines']} line, {len(rep['errors'])} lỗi, {len(rep['warnings'])} cảnh báo → {'OK' if rep['ok'] else 'FAIL'}")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
