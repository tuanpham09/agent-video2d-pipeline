#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_voiceover.py — đọc toàn bộ script.json bằng VieNeu-TTS v3 Turbo,
xuất audio từng câu, audio tổng, manifest timing tuyệt đối và phụ đề SRT.

Đặc điểm:
- Một process, một model: nạp VieNeu một lần cho cả kịch bản.
- Nhiều nhân vật: preset voice hoặc clone từ ref_audio 3–8 s.
- Cache theo nội dung: sửa 1 câu chỉ đọc lại câu đó.
- Tốc độ đọc: mặc định 1.25× (khuyến nghị 1.2–1.3), hạ/tăng bằng --speed; dùng
  ffmpeg atempo nên giữ nguyên cao độ giọng. Tốc độ riêng từng nhân vật khai
  `speed` trong script.json (characters[] hoặc từng line) hoặc voice_map.json;
  --speed chỉ là mặc định chung khi không khai riêng (xem `load_script`).
- Timing tuyệt đối (start/duration) để HyperFrames đặt audio + caption khớp.

Ví dụ:
  python build_voiceover.py --script projects/demo/script/script.json --out projects/demo/audio
  python build_voiceover.py --script ... --out ... --dry-run
  python build_voiceover.py --script ... --out ... --speed 1.2
  python build_voiceover.py --script ... --out ... --force --gap 0.2
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

try:
    import numpy as np
    import soundfile as sf
except ImportError as exc:  # pragma: no cover
    print(
        json.dumps(
            {
                "status": "error",
                "error_type": "MissingDependency",
                "message": f"Thiếu thư viện: {exc.name}. Cài bằng: pip install numpy soundfile",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    sys.exit(1)

ENGINE = "vieneu-v3-turbo"
TAG_RE = re.compile(r"\[[^\]]{1,24}\]")
CLEAN_CHARS = re.compile(r"\s+")

# VieNeu-TTS v3 Turbo hiểu đúng 3 cue phi ngôn ngữ; mọi tag khác bị đọc thành chữ.
EMOTION_TAGS = {
    "cười", "cuoi", "chuckle",
    "thở dài", "tho dai", "sigh",
    "hắng giọng", "hang giong", "clear throat",
}

# Tốc độ đọc cho video. 1.2–1.3 là dải khuyến nghị; 1.25 là mặc định.
DEFAULT_SPEED = 1.25
SPEED_MIN, SPEED_MAX = 1.0, 2.0


# ---------------------------------------------------------------- utilities


def die(error_type: str, message: str, detail: list[str] | None = None) -> None:
    payload = {"status": "error", "error_type": error_type, "message": message}
    if detail:
        payload["detail"] = detail
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    sys.exit(1)


def clean_caption(text: str) -> str:
    value = CLEAN_CHARS.sub(" ", TAG_RE.sub("", text))
    value = re.sub(r"\s+([,.;:!?…])", r"\1", value)
    return value.strip()


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value)


def unsupported_tags(text: str) -> list[str]:
    """Trả về các tag không nằm trong 3 cue mà VieNeu v3 Turbo hiểu.

    So khớp y như phonemizer của model: strip + lower, không gộp khoảng trắng bên trong
    (nên ``[thở  dài]`` hai dấu cách vẫn bị coi là tag lạ và sẽ bị đọc thành chữ).
    """
    bad: list[str] = []
    for raw in TAG_RE.findall(text):
        if raw[1:-1].strip().lower() not in EMOTION_TAGS and raw not in bad:
            bad.append(raw)
    return bad


def srt_time(seconds: float) -> str:
    ms = int(round(max(0.0, seconds) * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap_two_lines(text: str, width: int = 42) -> str:
    if len(text) <= width:
        return text
    words, best, best_delta = text.split(), None, 10**9
    for i in range(1, len(words)):
        left, right = " ".join(words[:i]), " ".join(words[i:])
        delta = abs(len(left) - len(right))
        if max(len(left), len(right)) <= width and delta < best_delta:
            best, best_delta = (left, right), delta
    if best:
        return best[0] + "\n" + best[1]
    return text


def split_caption(text: str, budget: int = 84) -> list[str]:
    text = clean_caption(text)
    if not text:
        return []
    if len(text) <= budget:
        return [text]
    words, chunks, cur = text.split(), [], ""
    for word in words:
        candidate = (cur + " " + word).strip()
        if cur and len(candidate) > budget * 0.72:
            chunks.append(cur)
            cur = word
        else:
            cur = candidate
    if cur:
        chunks.append(cur)
    return chunks or [text]


def apply_speed(src: Path, dst: Path, speed: float, sample_rate: int) -> None:
    """Đổi tốc độ đọc bằng ``ffmpeg atempo`` (giữ cao độ, không đổi pitch)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        die(
            "MissingDependency",
            "Cần ffmpeg để đổi tốc độ đọc. Cài ffmpeg hoặc chạy với --speed 1.0.",
        )
    cmd = [
        ffmpeg, "-y", "-loglevel", "error", "-i", str(src),
        "-filter:a", f"atempo={speed:.4f}",
        "-ar", str(sample_rate), "-ac", "1", str(dst),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        die("SpeedFailed", f"ffmpeg atempo lỗi cho {src.name}", [proc.stderr.strip()[:400]])


def rel(path: Path, base: Path) -> str:
    try:
        return path.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


# ---------------------------------------------------------------- validation


def resolve_speed(raw: object, where: str, default: float) -> float:
    """Tốc độ đọc cho một nhân vật/line: số trong [SPEED_MIN, SPEED_MAX]; thiếu thì lấy mặc định."""
    if raw is None:
        return default
    try:
        value = float(raw)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        value = float("nan")
    if not (SPEED_MIN <= value <= SPEED_MAX):  # nan cũng rớt vào đây
        die("InvalidSpeed", f"{where}: speed '{raw}' ngoài dải {SPEED_MIN}–{SPEED_MAX} hoặc không phải số.")
    return value


def load_script(path: Path, base: Path, overrides: dict, default_speed: float = DEFAULT_SPEED) -> tuple[dict, dict]:
    try:
        script = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        die("ScriptNotFound", f"Không thấy file kịch bản: {path}")
    except json.JSONDecodeError as exc:
        die("InvalidJson", f"script.json sai JSON: {exc}")

    characters = script.get("characters")
    scenes = script.get("scenes")
    if not isinstance(characters, list) or not characters:
        die("InvalidScript", "script.json thiếu 'characters' (cần ít nhất 1 nhân vật).")
    if not isinstance(scenes, list) or not scenes:
        die(
            "InvalidScript",
            "'scenes' đang rỗng. Viết kịch bản theo references/script-schema.md trước khi build voice.",
        )

    cast: dict[str, dict] = {}
    for raw in characters:
        cid = raw.get("id")
        if not cid:
            die("InvalidScript", f"Nhân vật thiếu 'id': {raw}")
        if cid in cast:
            die("InvalidScript", f"Trùng id nhân vật: {cid}")
        merged = dict(raw)
        merged.update(overrides.get(cid, {}))
        voice = (merged.get("voice") or "").strip() or None
        ref_raw = (merged.get("ref_audio") or "").strip() or None
        ref_path = None
        if ref_raw:
            candidate = Path(ref_raw)
            ref_path = candidate if candidate.is_absolute() else (base / candidate)
            if not ref_path.exists():
                die("MissingRefAudio", f"ref_audio của '{cid}' không tồn tại: {ref_path}")
        if not voice and not ref_path:
            die("InvalidScript", f"Nhân vật '{cid}' cần 'voice' hoặc 'ref_audio'.")
        cast[cid] = {
            "id": cid,
            "name": merged.get("name") or cid,
            "role": merged.get("role") or "narrator",
            "voice": voice,
            "ref_audio": ref_path,
            "temperature": float(merged.get("temperature", 0.8)),
            "denoise": bool(merged.get("denoise", True)),
            # tốc độ riêng từng nhân vật: characters[].speed (hoặc voice_map) thắng --speed chung
            "speed": resolve_speed(merged.get("speed"), f"nhân vật '{cid}'", default_speed),
        }

    seen_scenes: set[str] = set()
    seen_lines: set[str] = set()
    speeds: dict[str, float] = {}  # tốc độ riêng từng line: line.speed > character.speed > --speed
    warnings: list[str] = []
    total_lines = 0
    for index, scene in enumerate(scenes):
        sid = scene.get("id") or f"S{index + 1:02d}"
        scene["id"] = sid
        if sid in seen_scenes:
            die("InvalidScript", f"Trùng id scene: {sid}")
        seen_scenes.add(sid)
        lines = scene.get("lines")
        if not isinstance(lines, list) or not lines:
            die("InvalidScript", f"Scene '{sid}' không có 'lines'.")
        if len(lines) > 25:
            warnings.append(f"{sid}: {len(lines)} line trong một scene — nên chia beat.")
        for j, line in enumerate(lines):
            lid = line.get("id") or f"{sid}_L{j + 1:02d}"
            line["id"] = lid
            if lid in seen_lines:
                die("InvalidScript", f"Trùng id line: {lid}")
            seen_lines.add(lid)
            if line.get("speaker") not in cast:
                die(
                    "InvalidScript",
                    f"{lid}: speaker '{line.get('speaker')}' không có trong characters.",
                )
            speeds[lid] = resolve_speed(line.get("speed"), f"{lid}", cast[line["speaker"]]["speed"])
            text = (line.get("text") or "").strip()
            if not text or not clean_caption(text):
                die("InvalidScript", f"{lid}: text rỗng.")
            if len(text.split()) > 25:
                warnings.append(f"{lid}: {len(text.split())} từ — cắt ngắn để dễ đọc.")
            bad_tags = unsupported_tags(text)
            if bad_tags:
                warnings.append(
                    f"{lid}: tag không hỗ trợ {' '.join(bad_tags)} — VieNeu chỉ hiểu "
                    "[cười] [thở dài] [hắng giọng]; các từ này sẽ bị đọc thành chữ."
                )
            if "<|emotion_" in text:
                warnings.append(
                    f"{lid}: chứa token thô <|emotion_k|> — dùng [cười] / [thở dài] / [hắng giọng] thay thế."
                )
            total_lines += 1

    unused = set(cast) - {line["speaker"] for s in scenes for line in s["lines"]}
    if unused:
        warnings.append(f"Nhân vật không dùng: {', '.join(sorted(unused))}")

    return script, {"cast": cast, "warnings": warnings, "lines": total_lines, "speeds": speeds}


# ---------------------------------------------------------------- synthesis


def ref_fingerprint(path: Path) -> str:
    stat = path.stat()
    return f"{path.resolve()}|{stat.st_size}|{int(stat.st_mtime)}"


def make_key(text: str, char: dict, speed: float = 1.0) -> str:
    payload = {
        "engine": ENGINE,
        "text": text,
        "temperature": char["temperature"],
        "voice": char["voice"],
        "speed": round(float(speed), 4),
        "ref": ref_fingerprint(char["ref_audio"]) if char["ref_audio"] else None,
        "denoise": char["denoise"] if char["ref_audio"] else None,
    }
    return hashlib.sha1(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


class Speaker:
    """Nạp VieNeu một lần, đọc từng line."""

    def __init__(self) -> None:
        try:
            from vieneu import Vieneu
        except ImportError:
            die("PackageNotInstalled", "Chưa cài 'vieneu'. Chạy: pip install vieneu (hoặc pip install \"vieneu[cuda]\").")
        started = time.time()
        self.model = Vieneu()
        self.voice_ids: list[str] = []
        self._lookup: dict[str, str] = {}
        self._alias_lookup: dict[str, str] = {}
        try:
            self.voice_ids = [str(vid) for _, vid in self.model.list_preset_voices()]
            self._lookup = {v.strip().casefold(): v for v in self.voice_ids}
            # vieneu >= 3.8 giữ tên cũ làm alias ("Minh Quân" -> "Hải Đăng").
            for name, preset in (getattr(self.model, "_preset_voices", {}) or {}).items():
                for alias in preset.get("aliases") or []:
                    self._alias_lookup[str(alias).strip().casefold()] = name
        except Exception:  # model cũ không có list_preset_voices
            pass
        print(f"[vieneu] model sẵn sàng sau {time.time() - started:.1f}s", file=sys.stderr)

    def canonical_name(self, name: str | None) -> str | None:
        """Tên chuẩn cho một preset/alias; ``None`` nếu model không có giọng đó."""
        if not name:
            return None
        key = name.strip()
        hit = self._lookup.get(key.casefold()) or self._alias_lookup.get(key.casefold())
        if hit:
            return hit
        resolver = getattr(self.model, "resolve_voice_name", None)
        if resolver is None:
            return None
        try:
            return resolver(key)
        except Exception:  # noqa: BLE001
            return None

    def check_cast(self, cast: dict) -> list[str]:
        """Trả về danh sách lỗi giọng không tồn tại, kèm gợi ý gần giống."""
        if not self._lookup:
            return []
        problems: list[str] = []
        for cid, char in cast.items():
            if char["ref_audio"]:
                continue
            name = (char["voice"] or "").strip()
            if self.canonical_name(name):
                continue
            close = difflib.get_close_matches(name, self.voice_ids, n=12, cutoff=0.45)
            close = [c for c in close if c[:1].isupper() or any(ord(ch) > 127 for ch in c)][:5] or close[:5]
            hint = f" — gần giống: {', '.join(close)}" if close else ""
            problems.append(f"{cid}: '{name}'{hint}")
        return problems

    def synth(self, text: str, char: dict, out: Path) -> None:
        kwargs: dict = {"text": text, "temperature": char["temperature"]}
        if char["ref_audio"]:
            kwargs["ref_audio"] = str(char["ref_audio"].resolve())
            kwargs["denoise"] = char["denoise"]
        else:
            kwargs["voice"] = char["voice"]
        try:
            audio = self.model.infer(**kwargs)
        except TypeError:
            kwargs.pop("temperature", None)
            audio = self.model.infer(**kwargs)
        out.parent.mkdir(parents=True, exist_ok=True)
        self.model.save(audio, str(out))

    def synth_batch(self, batch: list[tuple[str, dict, Path]]) -> None:
        """Sinh một mẻ các câu cùng nhân vật/giọng bằng infer_batch để tối ưu tốc độ."""
        if not batch:
            return
        if not hasattr(self.model, "infer_batch") or len(batch) == 1:
            for text, char, out in batch:
                self.synth(text, char, out)
            return

        texts = [b[0] for b in batch]
        char = batch[0][1]
        kwargs: dict = {"texts": texts, "temperature": char["temperature"]}
        if char["ref_audio"]:
            kwargs["ref_audio"] = str(char["ref_audio"].resolve())
            kwargs["denoise"] = char["denoise"]
        else:
            kwargs["voice"] = char["voice"]

        try:
            audios = self.model.infer_batch(**kwargs)
        except Exception:
            # Fallback nếu infer_batch gặp lỗi
            for text, char, out in batch:
                self.synth(text, char, out)
            return

        for (_, _, out), audio in zip(batch, audios):
            out.parent.mkdir(parents=True, exist_ok=True)
            self.model.save(audio, str(out))


def read_mono(path: Path, target_sr: int, warn: set[str]) -> tuple[np.ndarray, float]:
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)
    mono = data.mean(axis=1) if data.shape[1] > 1 else data[:, 0]
    duration = len(mono) / float(sr)
    if sr != target_sr:
        if str(path) not in warn:
            print(f"[resample] {path.name}: {sr} Hz → {target_sr} Hz", file=sys.stderr)
            warn.add(str(path))
        count = int(round(len(mono) * target_sr / sr))
        mono = np.interp(
            np.linspace(0.0, len(mono), count, endpoint=False),
            np.arange(len(mono), dtype=np.float64),
            mono,
        ).astype(np.float32)
    return mono, duration


# ---------------------------------------------------------------- captions


def build_srt(scenes: list[dict], path: Path) -> None:
    cues: list[tuple[float, float, str]] = []
    for scene in scenes:
        for line in scene["lines"]:
            chunks = split_caption(line["text"])
            if not chunks:
                continue
            total_chars = sum(len(c) for c in chunks) or 1
            cursor = line["start"]
            for chunk in chunks:
                span = line["duration"] * (len(chunk) / total_chars)
                cues.append((cursor, cursor + span, wrap_two_lines(chunk)))
                cursor += span
    blocks = []
    for index, (start, end, text) in enumerate(cues, start=1):
        blocks.append(f"{index}\n{srt_time(start)} --> {srt_time(end)}\n{text}\n")
    path.write_text("\n".join(blocks), encoding="utf-8")


def build_timing_md(manifest: dict, path: Path) -> None:
    rows = ["| Scene | Bắt đầu | Dài | Lines | Nhân vật |", "| --- | --- | --- | --- | --- |"]
    for scene in manifest["scenes"]:
        speakers = sorted({line["speaker"] for line in scene["lines"]})
        rows.append(
            f"| {scene['id']} {scene.get('title', '')} | {scene['start']:.2f}s | "
            f"{scene['duration']:.2f}s | {len(scene['lines'])} | {', '.join(speakers)} |"
        )
    path.write_text(
        "# Timing\n\n" + "\n".join(rows) + f"\n\nTổng: **{manifest['duration']:.2f}s**\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh voiceover đồng bộ từ script.json bằng VieNeu-TTS.")
    ap.add_argument("--script", type=Path, required=True, help="đường dẫn script/script.json")
    ap.add_argument("--out", type=Path, required=True, help="thư mục audio đầu ra")
    ap.add_argument("--voice-map", type=Path, help="JSON override giọng (mặc định: <out>/voice_map.json nếu có)")
    ap.add_argument("--gap", type=float, default=0.18, help="khoảng lặng mặc định giữa các line (giây)")
    ap.add_argument("--scene-gap", type=float, default=0.35, help="khoảng lặng mặc định giữa các scene")
    ap.add_argument("--tail", type=float, default=0.4, help="khoảng lặng cuối video")
    ap.add_argument("--sample-rate", type=int, default=48000)
    ap.add_argument(
        "--speed", type=float, default=DEFAULT_SPEED,
        help=f"tốc độ đọc mặc định chung (atempo), khuyến nghị 1.2–1.3 (mặc định {DEFAULT_SPEED}); 1.0 = giữ nguyên. "
             "Tốc độ riêng từng nhân vật khai `speed` trong script.json/voice_map.json sẽ thắng giá trị này",
    )
    ap.add_argument("--force", action="store_true", help="bỏ qua cache, đọc lại tất cả")
    ap.add_argument("--dry-run", action="store_true", help="chỉ validate và in kế hoạch, không gọi model")
    ap.add_argument("--no-srt", action="store_true")
    ap.add_argument("--no-scenes", action="store_true", help="không xuất audio theo scene")
    ap.add_argument("--json", action="store_true", help="in summary dạng JSON gọn")
    args = ap.parse_args()

    if not (SPEED_MIN <= args.speed <= SPEED_MAX):
        die(
            "InvalidSpeed",
            f"--speed {args.speed} ngoài dải {SPEED_MIN}–{SPEED_MAX}. Khuyến nghị 1.2–1.3.",
        )
    if args.speed != 1.0 and not args.dry_run and not shutil.which("ffmpeg"):
        die(
            "MissingDependency",
            "Cần ffmpeg để đổi tốc độ đọc. Cài ffmpeg hoặc chạy với --speed 1.0.",
        )

    script_path = args.script.resolve()
    base = script_path.parent.parent  # <project>/script/script.json → <project>
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    lines_dir = out_dir / "lines"
    lines_dir.mkdir(parents=True, exist_ok=True)

    voice_map_path = args.voice_map or (out_dir / "voice_map.json")
    overrides: dict = {}
    if voice_map_path.exists():
        try:
            overrides = json.loads(voice_map_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError as exc:
            die("InvalidVoiceMap", f"{voice_map_path} sai JSON: {exc}")

    script, info = load_script(script_path, base, overrides, args.speed)
    cast = info["cast"]
    scenes = script["scenes"]

    plan: list[str] = []
    for scene in scenes:
        for line in scene["lines"]:
            char = cast[line["speaker"]]
            target = char["voice"] or f"clone:{Path(char['ref_audio']).name}"
            plan.append(f"{line['id']:<10} {char['name']:<14} {target}")

    if args.dry_run:
        print(
            json.dumps(
                {
                    "status": "dry-run",
                    "lines": info["lines"],
                    "scenes": len(scenes),
                    "speed": args.speed,
                    "characters": {
                        cid: {"name": c["name"], "voice": c["voice"], "clone": bool(c["ref_audio"]),
                              "speed": c["speed"]}
                        for cid, c in cast.items()
                    },
                    "warnings": info["warnings"],
                    "plan": plan,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    speaker = Speaker()
    for cid, char in cast.items():
        if char["ref_audio"] or not char["voice"]:
            continue
        canon = speaker.canonical_name(char["voice"])
        if canon and canon != char["voice"]:
            print(f"[alias] {cid}: '{char['voice']}' → '{canon}'", file=sys.stderr)
            char["voice"] = canon
    missing_voices = speaker.check_cast(cast)
    if missing_voices:
        die(
            "VoiceNotFound",
            "Có giọng không tồn tại trong model. Xem danh mục: python .agents/skills/vieneu-tts/scripts/list_voices.py",
            missing_voices,
        )
    warn_once: set[str] = set()
    durations: dict[str, float] = {}
    cache_hits = 0
    failures: list[str] = []
    total = info["lines"]
    done = 0
    started = time.time()

    # Thu thập danh sách lines cần đọc (uncached) vs cache hits
    uncached_queue: list[dict] = []
    line_entries: list[dict] = []

    for scene in scenes:
        for line in scene["lines"]:
            lid = line["id"]
            char = cast[line["speaker"]]
            wav = lines_dir / f"{safe_name(lid)}.wav"
            meta_path = lines_dir / f"{safe_name(lid)}.json"
            line_speed = info["speeds"][lid]
            key = make_key(line["text"].strip(), char, line_speed)

            cached = False
            if not args.force and wav.exists() and meta_path.exists():
                try:
                    meta = json.loads(meta_path.read_text(encoding="utf-8-sig"))
                    cached = meta.get("key") == key
                except json.JSONDecodeError:
                    cached = False

            entry = {
                "lid": lid,
                "text": line["text"].strip(),
                "char": char,
                "wav": wav,
                "meta_path": meta_path,
                "key": key,
                "speed": line_speed,
                "cached": cached,
            }
            line_entries.append(entry)
            if cached:
                cache_hits += 1
                durations[lid] = float(json.loads(meta_path.read_text(encoding="utf-8-sig"))["duration"])
            else:
                uncached_queue.append(entry)

    # Đọc batch các câu chưa cache (gom theo cùng nhân vật, tối đa 4 câu/mẻ)
    BATCH_SIZE = 4
    if uncached_queue:
        # Gom các câu liên tiếp cùng nhân vật
        batches: list[list[dict]] = []
        curr_batch: list[dict] = []
        for item in uncached_queue:
            if curr_batch and (
                curr_batch[0]["char"]["id"] != item["char"]["id"] or len(curr_batch) >= BATCH_SIZE
            ):
                batches.append(curr_batch)
                curr_batch = []
            curr_batch.append(item)
        if curr_batch:
            batches.append(curr_batch)

        batch_done = 0
        for batch in batches:
            t0 = time.time()
            synth_items = []
            for item in batch:
                raw = lines_dir / f".{safe_name(item['lid'])}.raw.wav"
                target = raw if item["speed"] != 1.0 else item["wav"]
                synth_items.append((item["text"], item["char"], target))

            try:
                speaker.synth_batch(synth_items)
            except Exception as exc:  # noqa: BLE001
                for item in batch:
                    failures.append(f"{item['lid']}: {exc}")
                continue

            for item, (_, _, target) in zip(batch, synth_items):
                raw = lines_dir / f".{safe_name(item['lid'])}.raw.wav"
                if item["speed"] != 1.0 and raw.exists():
                    apply_speed(raw, item["wav"], item["speed"], args.sample_rate)
                    raw.unlink(missing_ok=True)

                _, duration = read_mono(item["wav"], args.sample_rate, warn_once)
                item["meta_path"].write_text(
                    json.dumps(
                        {
                            "key": item["key"],
                            "duration": round(duration, 4),
                            "engine": ENGINE,
                            "speed": item["speed"],
                        },
                        ensure_ascii=False,
                    ),
                    encoding="utf-8",
                )
                durations[item["lid"]] = duration
                batch_done += 1
                print(
                    f"[{cache_hits + batch_done}/{total}] {item['lid']} ({item['char']['name']}) {duration:.2f}s ({time.time() - t0:.1f}s)",
                    file=sys.stderr,
                )

    if failures:
        die(
            "SynthesisFailed",
            f"{len(failures)} line đọc lỗi — chưa ghi manifest.",
            failures[:10],
        )

    # ----- timing
    cursor = 0.0
    manifest_scenes: list[dict] = []
    for scene in scenes:
        scene_start = cursor
        manifest_lines: list[dict] = []
        for line in scene["lines"]:
            lid = line["id"]
            duration = durations[lid]
            gap = float(line.get("pause_after", args.gap))
            manifest_lines.append(
                {
                    "id": lid,
                    "speaker": line["speaker"],
                    "text": line["text"].strip(),
                    "caption": clean_caption(line["text"]),
                    "on_screen": line.get("on_screen") or clean_caption(line["text"]),
                    "audio": rel(lines_dir / f"{safe_name(lid)}.wav", base),
                    "start": round(cursor, 4),
                    "duration": round(duration, 4),
                    "gap_after": round(gap, 4),
                    "speed": info["speeds"][lid],
                }
            )
            cursor += duration + gap
        last_gap = float(scene["lines"][-1].get("pause_after", args.gap))
        scene_end = cursor - last_gap
        scene_gap = float(scene.get("pause_after", args.scene_gap))
        manifest_scenes.append(
            {
                "id": scene["id"],
                "title": scene.get("title") or scene["id"],
                "goal": scene.get("goal") or "",
                "visual": scene.get("visual") or "",
                "start": round(scene_start, 4),
                "duration": round(scene_end - scene_start, 4),
                "audio": rel(out_dir / "scenes" / f"{safe_name(scene['id'])}.wav", base),
                "lines": manifest_lines,
            }
        )
        cursor = scene_end + scene_gap

    total_duration = round(manifest_scenes[-1]["start"] + manifest_scenes[-1]["duration"] + args.tail, 4)

    # ----- full mix + scene slices
    frames = int(math.ceil(total_duration * args.sample_rate))
    mix = np.zeros(frames, dtype=np.float32)
    for scene in manifest_scenes:
        for line in scene["lines"]:
            mono, _ = read_mono(base / line["audio"], args.sample_rate, warn_once)
            at = int(round(line["start"] * args.sample_rate))
            end = min(frames, at + len(mono))
            if end > at:
                mix[at:end] += mono[: end - at]
    peak = float(np.max(np.abs(mix))) if frames else 0.0
    if peak > 1.0:
        mix /= peak
    full_audio = out_dir / "voiceover.wav"
    sf.write(str(full_audio), mix, args.sample_rate, subtype="PCM_16")

    if not args.no_scenes:
        scenes_dir = out_dir / "scenes"
        scenes_dir.mkdir(parents=True, exist_ok=True)
        for scene in manifest_scenes:
            a = int(round(scene["start"] * args.sample_rate))
            b = int(round((scene["start"] + scene["duration"]) * args.sample_rate))
            sf.write(str(scenes_dir / f"{safe_name(scene['id'])}.wav"), mix[a:b], args.sample_rate, subtype="PCM_16")

    manifest = {
        "version": 1,
        "engine": ENGINE,
        "sample_rate": args.sample_rate,
        # tốc độ chung (mặc định --speed, giữ trong 1.2–1.3 cho schema/check_audio);
        # tốc độ thật từng line nằm ở lines[].speed, từng nhân vật ở characters[].speed
        "speed": args.speed,
        "duration": total_duration,
        "full_audio": rel(full_audio, base),
        "captions": rel(out_dir / "captions.srt", base),
        "characters": {
            cid: {
                "name": char["name"],
                "role": char["role"],
                "voice": char["voice"],
                "clone": rel(char["ref_audio"], base) if char["ref_audio"] else None,
                "speed": char["speed"],
            }
            for cid, char in cast.items()
        },
        "scenes": manifest_scenes,
    }
    if any(abs(s - args.speed) > 1e-9 for s in info["speeds"].values()):
        manifest["speed_note"] = (
            "tốc độ riêng từng nhân vật (khai speed trong script.json/voice_map.json; "
            f"--speed {args.speed} chỉ là mặc định chung): "
            + ", ".join(f"{cid} {c['speed']}" for cid, c in cast.items())
        )
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not args.no_srt:
        build_srt(manifest_scenes, out_dir / "captions.srt")
    build_timing_md(manifest, out_dir / "timing.md")

    summary = {
        "status": "success",
        "lines": total,
        "cache_hits": cache_hits,
        "rendered": total - cache_hits,
        "scenes": len(manifest_scenes),
        "duration_seconds": total_duration,
        "sample_rate": args.sample_rate,
        "speeds": {cid: c["speed"] for cid, c in cast.items()},
        "full_audio": str(full_audio),
        "manifest": str(manifest_path),
        "captions": str(out_dir / "captions.srt"),
        "elapsed_seconds": round(time.time() - started, 1),
        "warnings": info["warnings"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
