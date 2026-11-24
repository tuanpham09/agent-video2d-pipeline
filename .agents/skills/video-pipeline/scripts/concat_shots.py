#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""concat_shots.py — nối mp4 từng shot thành video hoàn chỉnh (Opt round 3, mục 1, nấc 1).

Luồng render tăng dần: sửa 1 shot → render.py --shots <id> --delivery (ra
output/shots/<id>.mp4 ổn định) → nối lại bằng script này, KHÔNG render lại cả
video. Chỉ thắng khi sửa ÍT shot (1 shot ~15–20s + nối ~10s, so với render
delivery cả video ~135s cho 30s video, ~3,7 giờ cho video 34 phút). Build lần
đầu vẫn render đủ — nối không thay thế build đầu.

Cách nối: video nối bằng concat demuxer, stream-copy (KHÔNG re-encode) — khả
thi vì các shot nối tiếp nhau không chồng/không crossfade (build_video.py:
ends[i] = wins[i+1][0]) và cùng thông số (cùng composition 1920×1080, cùng
fps). Giọng + SFX chỉ sống trong index.html (compositions chỉ có SVG+GSAP)
nên nối xong phải mux lại: voiceover.wav từ 0 + từng SFX adelay theo start
tuyệt đối (shot_start + sfx.t) + amix, volume SFX 0.8 — đúng như
build_video.py đặt data-volume trong index.html.

Gate trước khi nối (fail nếu sai):
  - đủ file output/shots/<id>.mp4 cho mọi shot trong shotlist
  - duration từng shot lệch ≤ --tolerance (mặc định 0.15s) so với cửa sổ shot
    (bắt drift ±0,1s của VieNeu / Chrome stall từng gặp ở vòng 2)
  - thông số video (codec, width, height, fps, pix_fmt) giống nhau giữa các shot
  - tổng duration lệch ≤ 0.3s so với manifest (drift từng shot cộng dồn)
Không dùng -shortest khi mux: thay vào đó khớp độ dài video với giọng bằng
pad frame cuối (video ngắn hơn giọng do tail sau line cuối) hoặc cắt -t
(video dài hơn giọng) — video ra có video stream đúng bằng giọng, không
thiếu đuôi như bản nối thô (từng ngắn 0.27s ở demo #4).

Ví dụ:
  python .agents/skills/video-pipeline/scripts/render.py --project projects/demo-30s-than-trung --shots SH006 --delivery
  python .agents/skills/video-pipeline/scripts/concat_shots.py --project projects/demo-30s-than-trung
  python .agents/skills/video-pipeline/scripts/concat_shots.py --project projects/demo-30s-than-trung --out output/final-concat.mp4 --json
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

TOLERANCE = 0.15   # lệch duration từng shot cho phép (giây)
TOTAL_TOLERANCE = 0.3  # lệch tổng duration cho phép (giây)
SFX_VOLUME = 0.8   # khớp data-volume="0.8" của build_video.py


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def shot_windows(proj: Path) -> tuple[dict[str, tuple[float, float]], dict[str, list[dict]]]:
    """Cửa sổ tuyệt đối từng shot + SFX cue với start tuyệt đối.

    Cửa sổ = cửa sổ COMPOSITION của build_video.py (không phải cửa sổ line):
    start = đầu line/span, end = ĐẦU shot sau (lấp gap giữa các line),
    shot cuối end = cuối cửa sổ line/span của mình. File mp4 từng shot
    render đúng cửa sổ này (làm tròn lên khung hình 30fps), nên gate
    duration so với cửa sổ này mới đúng.
    """
    manifest = load_json(proj / "audio" / "manifest.json")
    shotlist = load_json(proj / "script" / "shotlist.json")
    lines: dict[str, dict] = {}
    for sc in manifest["scenes"]:
        for ln in sc["lines"]:
            lines[ln["id"]] = ln
    windows: dict[str, tuple[float, float]] = {}
    sfx: dict[str, list[dict]] = {}
    order: list[str] = []
    for shot in shotlist.get("shots", []):
        sid = shot.get("id", "?")
        lids = [lid for lid in shot.get("line_ids", []) if lid in lines]
        if not lids:
            continue
        start = min(lines[l]["start"] for l in lids)
        end = max(lines[l]["start"] + lines[l]["duration"] for l in lids)
        span = shot.get("span")
        if isinstance(span, list) and len(span) == 2:
            windows[sid] = (start + float(span[0]), start + float(span[1]))
        else:
            windows[sid] = (start, end)
        order.append(sid)
        sfx[sid] = [{"src": c.get("src", ""), "t": float(c.get("t", 0.0)),
                     "abs_start": windows[sid][0] + float(c.get("t", 0.0))}
                    for c in shot.get("sfx", [])]
    # KHỚP build_video.py (dòng 527): composition từng shot chạy tới ĐẦU shot
    # sau (lấp khoảng nghỉ giữa các line), shot cuối dừng ở cuối cửa sổ mình.
    # File mp4 từng shot vì vậy dài hơn (cửa sổ line/span) đúng bằng gap
    # (~0.18s) — gate duration PHẢI so với cửa sổ này, không phải cửa sổ line.
    # (detect_issues.py vẫn dùng cửa sổ line vì nó map sự kiện âm thanh
    # theo line; khác mục đích, không đổi.)
    for i, sid in enumerate(order):
        if i + 1 < len(order):
            windows[sid] = (windows[sid][0], windows[order[i + 1]][0])
    return windows, sfx


def probe(video: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error",
                        "-show_entries", "stream=codec_name,width,height,r_frame_rate,pix_fmt",
                        "-show_entries", "format=duration",
                        "-of", "json", str(video)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"✗ ffprobe lỗi trên {video}:\n{r.stderr[-500:]}", file=sys.stderr)
        sys.exit(2)
    d = json.loads(r.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_name") != "aac"
              and "width" in s), None)
    if v is None:
        print(f"✗ {video} không có video stream", file=sys.stderr)
        sys.exit(2)
    return {"duration": float(d["format"]["duration"]),
            "codec": v["codec_name"], "width": v["width"], "height": v["height"],
            "fps": v["r_frame_rate"], "pix_fmt": v["pix_fmt"]}


def resolve_sfx(src: str, repo: Path, proj: Path) -> Path | None:
    """Tìm file SFX thật: ưu tiên bản đã copy vào video/assets/sfx (đúng file
    render dùng), rồi repo/<src>, rồi audio/sfx/<tên>.wav (synth:)."""
    if not src:
        return None
    if src.startswith("synth:"):
        p = proj / "audio" / "sfx" / f"{src[len('synth:'):].strip()}.wav"
        return p if p.is_file() else None
    for cand in (proj / "video" / "assets" / "sfx" / Path(src).name,
                 repo / src, proj / src):
        if cand.is_file():
            return cand
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="Nối mp4 từng shot + mux giọng/SFX thành video hoàn chỉnh.")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path("."), help="gốc repo, để tìm file SFX")
    ap.add_argument("--shots-dir", type=Path, help="thư mục chứa <id>.mp4 (mặc định <project>/output/shots)")
    ap.add_argument("--out", type=Path, help="file ra (mặc định <project>/output/final-concat.mp4)")
    ap.add_argument("--voice", type=Path, help="file giọng (mặc định <project>/audio/voiceover.wav)")
    ap.add_argument("--tolerance", type=float, default=TOLERANCE,
                    help=f"lệch duration từng shot cho phép (mặc định {TOLERANCE}s)")
    ap.add_argument("--total-tolerance", type=float, default=TOTAL_TOLERANCE)
    ap.add_argument("--sfx-volume", type=float, default=SFX_VOLUME)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    proj = args.project
    shots_dir = args.shots_dir or (proj / "output" / "shots")
    out = args.out or (proj / "output" / "final-concat.mp4")
    voice = args.voice or (proj / "audio" / "voiceover.wav")

    windows, sfx_map = shot_windows(proj)
    if not windows:
        print("✗ không có shot nào (manifest/shotlist rỗng?)", file=sys.stderr)
        return 1
    sids = [sid for sid, _ in sorted(windows.items(), key=lambda kv: kv[1][0])]
    manifest = load_json(proj / "audio" / "manifest.json")
    total_expected = float(manifest.get("duration", 0.0))
    t0 = min(w[0] for w in windows.values())

    errors: list[str] = []
    # --- gate 1: đủ file + duration từng shot + thông số giống nhau
    infos: dict[str, dict] = {}
    for sid in sids:
        f = shots_dir / f"{sid}.mp4"
        if not f.is_file():
            errors.append(f"thiếu {f} — render trước: render.py --project {proj} --shots {sid} --delivery")
            continue
        infos[sid] = probe(f)
        want = windows[sid][1] - windows[sid][0]
        got = infos[sid]["duration"]
        if abs(got - want) > args.tolerance:
            errors.append(f"{sid}: duration {got:.2f}s lệch {got - want:+.2f}s so với cửa sổ {want:.2f}s "
                          f"(ngưỡng ±{args.tolerance}s) — render lại shot này")
    if infos:
        first = next(iter(infos.values()))
        params = ("codec", "width", "height", "fps", "pix_fmt")
        for sid, info in infos.items():
            for k in params:
                if info[k] != first[k]:
                    errors.append(f"{sid}: {k}={info[k]} khác shot đầu {first[k]} — "
                                  f"stream-copy concat yêu cầu thông số giống nhau")
    if errors:
        print("✗ gate concat FAIL:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    total_got = sum(infos[s]["duration"] for s in sids)
    # Tổng kỳ vọng = cuối cửa sổ shot cuối (cuối line cuối), KHÔNG phải
    # manifest duration: manifest còn tail sau line cuối (~0.4s) mà shot
    # không cover — tail được bù bằng pad frame cuối ở dưới. So với manifest
    # thì tổng luôn thiếu đúng bằng tail và gate sẽ fail oan khi tail > 0.3s.
    total_expected_video = max(w[1] for w in windows.values()) - t0
    if abs(total_got - total_expected_video) > args.total_tolerance:
        print(f"✗ tổng duration {total_got:.2f}s lệch {total_got - total_expected_video:+.2f}s "
              f"so với cuối shot cuối {total_expected_video:.2f}s (ngưỡng ±{args.total_tolerance}s) — "
              f"drift cộng dồn, render lại shot lệch nhiều nhất", file=sys.stderr)
        return 1

    # --- khớp độ dài video với giọng (tail): shot cuối dừng ở cuối line,
    # nhưng manifest còn tail (giọng 28.53s vs line cuối hết 28.13s) nên
    # video nối thường NGẮN hơn giọng ~0.27s. Bù bằng đoạn giữ frame cuối
    # (stream-copy, không encode lại toàn video); ngược lại thì cắt -t.
    # Không làm: video ra thiếu đuôi, player dừng hình/đen 0.27s cuối.
    pad_file: str | None = None
    trim_to: float | None = None
    fps0 = 30.0
    try:
        fps0 = float(infos[sids[0]]["fps"].split("/")[0]) / float(infos[sids[0]]["fps"].split("/")[1])
    except Exception:  # noqa: BLE001
        fps0 = 30.0
    if voice.is_file():
        ar = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                             "-of", "csv=p=0", str(voice)], capture_output=True, text=True)
        try:
            audio_total = float(ar.stdout.strip())
        except ValueError:
            audio_total = 0.0
        if audio_total > 0:
            diff = audio_total - total_got
            if diff > 1.0 / fps0:
                pad_frames = int(math.ceil(diff * fps0))
                pad_dur = pad_frames / fps0
                last_shot = shots_dir / f"{sids[-1]}.mp4"
                tmpdir = Path(tempfile.gettempdir())
                frame_png = tmpdir / f"concat-pad-{os.getpid()}.png"
                pad_file = str(tmpdir / f"concat-pad-{os.getpid()}.mp4")
                r1 = subprocess.run(["ffmpeg", "-v", "error", "-y", "-sseof", "-0.1", "-i",
                                     str(last_shot), "-frames:v", "1", str(frame_png)],
                                    capture_output=True, text=True)
                r2 = subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1",
                                     "-framerate", str(int(fps0)), "-t", f"{pad_dur:.3f}",
                                     "-i", str(frame_png), "-c:v", "libx264",
                                     "-profile:v", "high", "-level", "4.0",
                                     "-pix_fmt", "yuv420p", "-r", str(int(fps0)),
                                     "-video_track_timescale", "15360", pad_file],
                                    capture_output=True, text=True) if r1.returncode == 0 else None
                if r1.returncode != 0 or r2 is None or r2.returncode != 0:
                    print(f"! không tạo được pad cuối ({(r2.stderr if r2 else r1.stderr)[-300:]}) — "
                          f"video ra sẽ ngắn hơn giọng {diff:.2f}s", file=sys.stderr)
                    pad_file = None
                else:
                    print(f"  pad cuối {pad_dur:.2f}s (giữ frame cuối {sids[-1]} cho khớp tail "
                          f"giọng {audio_total:.2f}s)")
                if frame_png.is_file():
                    frame_png.unlink(missing_ok=True)
            elif diff < -1.0 / fps0:
                trim_to = audio_total

    # --- SFX: resolve file, bỏ cue thiếu file (báo rõ, không lặng)
    sfx_inputs: list[tuple[Path, float]] = []
    missing_sfx: list[str] = []
    for sid in sids:
        for cue in sfx_map.get(sid, []):
            p = resolve_sfx(cue["src"], args.repo, proj)
            if p is None:
                missing_sfx.append(f"{sid}: {cue['src']}")
            else:
                sfx_inputs.append((p, cue["abs_start"]))
    if missing_sfx:
        print("! bỏ qua SFX thiếu file (video vẫn nối, không có tiếng này):", file=sys.stderr)
        for m in missing_sfx:
            print(f"  - {m}", file=sys.stderr)

    # --- build ffmpeg: concat video (stream-copy) + mux audio
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as lf:
        for sid in sids:
            lf.write(f"file '{(shots_dir / f'{sid}.mp4').resolve().as_posix().replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\n")
        if pad_file:
            lf.write(f"file '{Path(pad_file).resolve().as_posix()}'\n")
        list_file = lf.name
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", list_file]
    audio_inputs: list[str] = []
    if voice.is_file():
        cmd += ["-i", str(voice)]
        audio_inputs.append("voice")
    else:
        print(f"! thiếu {voice} — video nối KHÔNG có giọng", file=sys.stderr)
    for p, _ in sfx_inputs:
        cmd += ["-i", str(p)]
    n_audio = len(audio_inputs) + len(sfx_inputs)
    if n_audio == 0:
        cmd += ["-map", "0:v", "-c:v", "copy", "-movflags", "+faststart", str(out)]
    elif n_audio == 1:
        # chỉ giọng: map thẳng, không amix
        cmd += ["-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(out)]
    else:
        # giọng + SFX: chuẩn hoá sample rate/kênh, adelay theo start tuyệt đối, amix
        filt: list[str] = []
        labels: list[str] = []
        v_idx = 1
        if t0 > 0.001:
            filt.append(f"[{v_idx}:a]atrim=start={t0:.3f},asetpts=PTS-STARTPTS,aresample=48000,aformat=channel_layouts=stereo[voice]")
        else:
            filt.append(f"[{v_idx}:a]aresample=48000,aformat=channel_layouts=stereo[voice]")
        labels.append("[voice]")
        for i, (_, start) in enumerate(sfx_inputs):
            idx = 2 + i
            ms = int(round(start * 1000))
            filt.append(f"[{idx}:a]aresample=48000,aformat=channel_layouts=stereo,"
                        f"adelay={ms}|{ms},volume={args.sfx_volume}[sfx{i}]")
            labels.append(f"[sfx{i}]")
        filt.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=first[a]")
        cmd += ["-filter_complex", ";".join(filt),
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", str(out)]
    if trim_to is not None:
        # video dài hơn giọng: cắt output đúng bằng giọng (giọng không đổi)
        cmd = cmd[:-1] + ["-t", f"{trim_to:.3f}", cmd[-1]]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if pad_file and os.path.isfile(pad_file):
        os.unlink(pad_file)
    if r.returncode != 0:
        print(f"✗ ffmpeg nối lỗi (exit {r.returncode}):\n{r.stderr[-1200:]}", file=sys.stderr)
        return 1
    got_total = probe(out)["duration"]
    drift = got_total - total_expected
    if args.json:
        print(json.dumps({"output": str(out), "shots": sids, "video_duration": round(got_total, 3),
                          "manifest_duration": round(total_expected, 3), "drift": round(drift, 3),
                          "sfx_mixed": len(sfx_inputs), "sfx_missing": missing_sfx,
                          "voice": str(voice) if voice.is_file() else None},
                         ensure_ascii=False, indent=2))
    else:
        print(f"✓ nối {len(sids)} shot -> {out}")
        print(f"  video {got_total:.2f}s, manifest {total_expected:.2f}s, drift {drift:+.2f}s")
        print(f"  giọng: {'có' if voice.is_file() else 'THIẾU'}, SFX mux: {len(sfx_inputs)}, thiếu file: {len(missing_sfx)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
