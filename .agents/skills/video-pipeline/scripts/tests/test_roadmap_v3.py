#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử các phần roadmap v3 (không cần VieNeu, không cần trình duyệt):
  - timing_lib: mốc theo từ, beat theo từ, ranh giới
  - check_shots E7 (mỗi nhân vật trong shot nhiều người phải có hành vi tường minh) và E8 (beat theo từ),
    E9 (pose/emotion/stance/gaze phải có trong rig) và E10 (nhân vật không đứng đè lên đạo cụ)
    và E11 (focus phải trỏ tới thứ có thật trong shot; bắt lỗi thiếu tiền tố prop: kiểu SH006 demo #3)
  - check_sync: layout 1 track giọng duy nhất được chấp nhận (kiểm src, duration, file wav);
    layout clip-riêng từng line vẫn kiểm nghiêm; dựng từng phần chỉ kiểm line được phủ
  - build_video: beat move/look/react sinh tween đúng; người nghe tự gật không trùng gật tường minh
  - check_audio: bắt đúng clip, câm, sai thời lượng, chồng lấn; câu đạt không báo lỗi
  - freeze_manifest (Opt round 2): khóa timing đã duyệt vào audio/timing.md; script đổi -> cảnh báo exit 2, --force mới khóa lại
  - render.py --shots (Opt round 2): shot không có composition / xung đột --delivery -> exit 1 (không cần Chrome)
  - build_voiceover lazy-load (Opt round 3, mục 5): quét cache trước khi nạp model; all-cached thì bỏ qua hẳn Speaker; alias sau canonicalize vẫn hit cache cũ
  - concat_shots (Opt round 3, mục 1): nối shot + mux giọng/SFX; gate duration từng shot, fps giống nhau, thiếu file
  - detect_issues (Opt round 3, mục 2): black/freeze/silence trên video tổng hợp; map khoảng bị cờ vào shot
  - gates.py --auto-skip (Opt round 3, backlog): bỏ bước Chrome khi diff chỉ chạm .py/.md và video/ không mới hơn code

Chạy:  python .agents/skills/video-pipeline/scripts/tests/test_roadmap_v3.py
Mã thoát 0 = tất cả qua. Không ghi vào project thật (dùng thư mục tạm).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
REPO = HERE.parents[4]
sys.path.insert(0, str(SCRIPTS))
from timing_lib import beat_time, sentence_ends, word_spans  # noqa: E402

PROJ = REPO / "projects" / "than-trung-chiec-khan-tang-thu-32"
FAILS: list[str] = []


def ok(name: str, cond: bool, detail: str = "") -> None:
    print(("  ✓ " if cond else "  ✗ ") + name + ("" if cond else f"  [{detail}]"))
    if not cond:
        FAILS.append(name)


def test_timing_lib() -> None:
    print("timing_lib")
    sp = word_spans("Một hai ba.", 10.0, 2.0)
    ok("số từ khớp", len(sp) == 3)
    ok("bắt đầu đúng line", abs(sp[0]["start"] - 10.0) < 1e-9)
    ok("kết thúc đúng line", abs(sp[-1]["end"] - 12.0) < 1e-9)
    ok("liên tục, không chồng", all(abs(a["end"] - b["start"]) < 1e-9 for a, b in zip(sp, sp[1:])))
    ok("dấu chấm kéo dài từ cuối", sp[-1]["end"] - sp[-1]["start"] > sp[0]["end"] - sp[0]["start"])
    real = [{"start": 0.0, "end": 0.5}, {"start": 0.6, "end": 1.0}, {"start": 1.0, "end": 2.0}]
    sp2 = word_spans("a b c", 5.0, 2.0, real)
    ok("mốc thật (words) được ưu tiên", abs(sp2[1]["start"] - 5.6) < 1e-9)
    ok("câu kết thúc bằng dấu chấm có mốc gật", len(sentence_ends("Một hai. Ba bốn!", 0.0, 4.0)) == 2)

    lines = {"L1": {"text": "Một hai ba bốn", "start": 1.0, "duration": 4.0}}
    spans = word_spans(lines["L1"]["text"], 1.0, 4.0)
    ok("beat theo từ quy ra giây trong shot", abs(beat_time({"line_id": "L1", "word": 2}, lines, 0.5) - (spans[2]["start"] - 0.5)) < 1e-9)
    b_start = beat_time({"line_id": "L1", "word": 0}, lines, 1.0)
    ok("beat word=0 bằng đầu line trừ abs0", abs(b_start - 0.0) < 1e-9, str(b_start))
    try:
        beat_time({"line_id": "L1", "word": 9}, lines, 0.0)
        ok("word ngoài số từ bị từ chối", False)
    except ValueError:
        ok("word ngoài số từ bị từ chối", True)


def write_min_project(dst: Path, shotlist_mut=None) -> None:
    """Sao chép tối thiểu project thật (script/ + audio/ + assets/) để kiểm gate mà không chạm dữ liệu thật."""
    for sub in ("script", "audio", "assets"):
        shutil.copytree(PROJ / sub, dst / sub, ignore=shutil.ignore_patterns("video*", "*.png"))
    if shotlist_mut:
        p = dst / "script" / "shotlist.json"
        s = json.loads(p.read_text(encoding="utf-8"))
        shotlist_mut(s)
        p.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")


def run(cmd: list[str]) -> tuple[int, str]:
    r = subprocess.run([sys.executable, *cmd], capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout + r.stderr


def test_check_shots() -> None:
    print("check_shots (S01)")
    code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(PROJ), "--scenes", "S01"])
    ok("S01 thật qua gate", code == 0, out[-300:])
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()

        def drop_host_beats(s):
            for sh in s["shots"]:
                if sh["id"] == "SH008":
                    sh["beats"] = [b for b in sh["beats"] if not (b.get("react") or (b.get("set") or {}).get("host"))]

        write_min_project(d, drop_host_beats)
        code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        ok("E7: bỏ beat của host ở SH008 thì gate FAIL", code == 1 and "không có hành vi tường minh" in out, out[-300:])

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()

        def bad_word(s):
            for sh in s["shots"]:
                if sh["id"] == "SH010":
                    sh["beats"][0]["word"] = 999
                    sh["beats"][0].pop("t", None)

        write_min_project(d, bad_word)
        code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        ok("E8: word ngoài số từ bị báo", code == 1 and "ngoài" in out, out[-300:])

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()

        def bad_pose(s):
            for sh in s["shots"]:
                if sh["id"] == "SH008":
                    sh["characters"][0]["pose"] = "reach-r"
                    for b in sh["beats"]:
                        st = b.get("set") or {}
                        if any("pose" in v for v in st.values()):
                            cid = next(iter(st))
                            b["set"][cid]["pose"] = "reach-r"
                            break

        write_min_project(d, bad_pose)
        code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01", "--repo", str(REPO)])
        ok("E9: pose không có trong rig bị báo (characters[] và beat set)",
           code == 1 and out.count("(E9)") >= 2 and "reach-r" in out, out[-300:])

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()

        def overlap_prop(s):
            for sh in s["shots"]:
                if sh["id"] == "SH008":
                    for p in sh["props"]:
                        if p.get("id") == "mam_tre":
                            p["at"] = "stand:C"
                            p["dx"] = -230

        write_min_project(d, overlap_prop)
        code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01", "--repo", str(REPO)])
        ok("E10: nhân vật đứng đè lên đạo cụ bị báo",
           code == 1 and "(E10)" in out and "mam_tre" in out, out[-300:])

    # E11 (Opt round 3, mục 6): focus phải trỏ tới thứ có thật trong shot.
    # SH001 (S01): focus gốc ong_cuu, chars [ong_cuu], props [ban_tho, nen, bat_huong].
    e11_cases = [
        ("E11: focus đạo cụ thiếu tiền tố prop: (bug SH006 demo #3)",
         "mam_tre", "thiếu tiền tố"),
        ("E11: focus prop: có trong bible nhưng không trong shot",
         "prop:mam_tre", "không có trong shot này"),
        ("E11: focus prop: không có trong bible",
         "prop:khan_khong_co", "không có trong bible"),
        ("E11: focus nhân vật có trong bible nhưng không trong shot",
         "me", "không có trong shot này"),
        ("E11: focus slot: không có trong bối cảnh",
         "slot:khong_co", "không có trong bối cảnh"),
    ]
    for label, focus_val, needle in e11_cases:
        with tempfile.TemporaryDirectory() as td:
            d = Path(td) / "p"
            d.mkdir()

            def bad_focus(s, fv=focus_val):
                for sh in s["shots"]:
                    if sh["id"] == "SH001":
                        sh["focus"] = fv

            write_min_project(d, bad_focus)
            code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01", "--repo", str(REPO)])
            ok(label, code == 1 and "(E11)" in out and needle in out, out[-300:])


def test_build_video_tweens() -> None:
    print("build_video (tween move/look/react, người nghe)")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()

        def add_move(s):
            for sh in s["shots"]:
                if sh["id"] == "SH010":
                    sh["beats"].append({"line_id": "S01_L09a", "t": 0.6, "do": "chị bước sang phải", "physical": False,
                                        "move": {"char": "host", "to": "R", "dur": 1.5}})

        write_min_project(d, add_move)
        out_dir = Path(td) / "video"
        code, out = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--shots", "SH010", "--out", str(out_dir)])
        ok("dựng được shot có move", code == 0, out[-300:])
        html = (out_dir / "compositions" / "SH010.html").read_text(encoding="utf-8")
        ok("move sinh tween x về anchor R (1200 = 1460 − 260)", 'attr: {x: 1200.0}, duration: 1.50' in html)
        ok("move sinh bob y đúng 2k nhịp", 'y: "-=3"' in html)
        ok("move đổi gaze theo hướng đi", "tl.set(\"#SH010-host\", {attr: {\"data-gaze\": \"right\"}}, 0.60)" in html)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d)
        out_dir = Path(td) / "video"
        code, out = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--scenes", "S01", "--out", str(out_dir)])
        ok("dựng toàn S01 không lỗi", code == 0, out[-300:])
        html = (out_dir / "compositions" / "SH012.html").read_text(encoding="utf-8")
        ok("không gật đôi: SH012 chỉ có đúng một tween gật (beat tường minh, người nghe tự động bị bỏ)",
           html.count('"+=2.5"') == 1, str(html.count('"+=2.5"')))


def test_hand_over() -> None:
    print("build_video (hand_over: đạo cụ chuyển tay)")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()

        def add_ho(s, physical=True):
            for sh in s["shots"]:
                if sh["id"] == "SH008":
                    sh["beats"].append({"line_id": sh["beats"][0]["line_id"], "t": 2.4, "do": "đưa mâm", "physical": physical,
                                        "hand_over": {"prop": "mam_tre", "from": "me", "to": "host", "dur": 0.9}})

        write_min_project(d, add_ho)
        out_dir = Path(td) / "video"
        code, out = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--shots", "SH008", "--out", str(out_dir)])
        ok("hand_over dựng được", code == 0, out[-300:])
        html = (out_dir / "compositions" / "SH008.html").read_text(encoding="utf-8")
        ok("đạo cụ được tween tới tay người nhận (hai đoạn: nhấc rồi chuyển)",
           len(__import__("re").findall(r'tl\.to\("#SH008-p\d+", \{attr: \{x: [-\d.]+, y: [-\d.]+\}, duration: [\d.]+, ease: "power1.inOut"\}, 2\.[47]\d\)', html)) == 2)

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()

        def add_ho_nophys(s):
            add_ho(s, physical=False)

        write_min_project(d, add_ho_nophys)
        code, out = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--shots", "SH008", "--out", str(Path(td) / "v")])
        ok("hand_over không physical bị từ chối (R6.1)", code != 0 and "physical=true" in out, out[-200:])


def test_schemas() -> None:
    print("validate_schemas (JSON Schema, P0)")
    code, out = run([str(SCRIPTS / "validate_schemas.py"), "--project", str(PROJ)])
    ok("project S01 thật đúng cấu trúc bốn file", code == 0, out[-300:])
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d)
        m = json.loads((d / "audio" / "manifest.json").read_text(encoding="utf-8"))
        m["speed"] = 1.5
        (d / "audio" / "manifest.json").write_text(json.dumps(m, ensure_ascii=False), encoding="utf-8")
        code, out = run([str(SCRIPTS / "validate_schemas.py"), "--project", str(d)])
        ok("manifest speed 1.5 bị schema từ chối", code == 1 and "speed" in out, out[-300:])


def test_check_audio() -> None:
    print("check_audio (wav giả)")
    import numpy as np
    import soundfile as sf

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "audio" / "lines").mkdir(parents=True)
        sr = 48000
        rng = np.random.default_rng(0)

        def sig(sec, amp):
            return (amp * rng.uniform(-1, 1, int(sr * sec))).astype("float32")

        spec = [
            ("ok", 0.0, 2.0, sig(2.0, 0.1)),
            ("clip", 2.5, 2.0, np.clip(sig(2.0, 3.0), -1, 1).astype("float32")),
            ("mute", 5.0, 2.0, np.zeros(int(sr * 2), dtype="float32")),
            ("long", 7.5, 2.0, sig(3.0, 0.1)),
            ("over", 8.0, 2.0, sig(2.0, 0.1)),
        ]
        lines = []
        for lid, st, du, x in spec:
            sf.write(d / "audio" / "lines" / f"{lid}.wav", x, sr)
            lines.append({"id": lid, "speaker": "host", "text": "Câu thử.", "start": st, "duration": du,
                          "audio": f"audio/lines/{lid}.wav"})
        sf.write(d / "audio" / "voiceover.wav", sig(9.5, 0.1), sr)
        man = {"version": 1, "engine": "vieneu-v3-turbo", "sample_rate": sr, "speed": 1.25, "duration": 9.5,
               "full_audio": "audio/voiceover.wav", "scenes": [{"id": "S01", "lines": lines}]}
        (d / "audio" / "manifest.json").write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")
        code, out = run([str(SCRIPTS.parent.parent / "voice-sync" / "scripts" / "check_audio.py"), "--project", str(d)])
        ok("bắt clip (E4)", "E4: clip" in out, out[-400:])
        ok("bắt câm (E5)", "E5: mute" in out)
        ok("bắt sai thời lượng (E3)", "E3: long" in out)
        ok("bắt chồng lấn (E6)", "E6: over" in out)
        ok("câu đạt không bị báo", "E4: ok" not in out and "E5: ok" not in out and "E3: ok" not in out and "E6: ok" not in out)
        ok("gate tổng FAIL", code == 1)

        man["speed"] = 1.5
        (d / "audio" / "manifest.json").write_text(json.dumps(man, ensure_ascii=False), encoding="utf-8")
        code, out = run([str(SCRIPTS.parent.parent / "voice-sync" / "scripts" / "check_audio.py"), "--project", str(d)])
        ok("speed ngoài 1.2–1.3 bị báo (E1)", "E1: speed 1.5" in out)


def test_check_sync() -> None:
    print("check_sync (voice track duy nhất / clip-riêng / dựng từng phần)")
    import wave

    def silent_wav(path: Path, seconds: float, sr: int = 48000) -> None:
        n = int(seconds * sr)
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes(b"\x00\x00" * n)

    def voice_tag(dur: str, src: str = "assets/audio/voiceover.wav") -> str:
        return (f'    <audio id="voice" class="clip" src="{src}" data-start="0" data-duration="{dur}" '
                f'data-media-start="0.000" data-volume="1" data-track-index="2"></audio>\n')

    def sync(tmp: Path, index: Path) -> tuple[int, str]:
        return run([str(SCRIPTS / "check_sync.py"), "--manifest", str(tmp / "audio" / "manifest.json"),
                    "--index", str(index)])

    # per-line layout cũ (video/ đầy đủ, 414 clip) vẫn phải pass
    code, out = run([str(SCRIPTS / "check_sync.py"), "--manifest", str(PROJ / "audio" / "manifest.json"),
                     "--index", str(PROJ / "video" / "index.html")])
    ok("layout clip-riêng cũ (414 clip) vẫn pass", code == 0, out[-300:])

    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d)
        out_dir = Path(td) / "video_demo"
        code, out = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--scenes", "S01", "--out", str(out_dir)])
        ok("dựng S01 (không voice) được", code == 0, out[-300:])
        idx = out_dir / "index.html"
        code, out = sync(d, idx)
        ok("không voice + không clip -> FAIL, chỉ đòi 13 clip S01 (đã scope, không đòi 414)",
           code == 1 and "thiếu 13 audio clip" in out and "cắt mất lời" not in out, out[-300:])

        # thêm track giọng đúng -> pass
        html = idx.read_text(encoding="utf-8")
        (out_dir / "assets" / "audio").mkdir(parents=True, exist_ok=True)
        silent_wav(out_dir / "assets" / "audio" / "voiceover.wav", 46.323)
        idx.write_text(html.replace("    </div>\n    <script>", voice_tag("46.323") + "    </div>\n    <script>", 1),
                       encoding="utf-8")
        code, out = sync(d, idx)
        ok("track giọng duy nhất đúng duration + file wav khớp -> pass", code == 0, out[-300:])

        # duration lệch -> fail
        idx.write_text(html.replace("    </div>\n    <script>", voice_tag("40.000") + "    </div>\n    <script>", 1),
                       encoding="utf-8")
        code, out = sync(d, idx)
        ok("track giọng lệch duration -> FAIL", code == 1 and "track giọng" in out, out[-300:])

        # src không tồn tại -> fail
        idx.write_text(html.replace("    </div>\n    <script>",
                                    voice_tag("46.323", "assets/audio/khong-co.wav") + "    </div>\n    <script>", 1),
                       encoding="utf-8")
        code, out = sync(d, idx)
        ok("track giọng trỏ file không tồn tại -> FAIL", code == 1 and "không tồn tại" in out, out[-300:])


def test_freeze_manifest() -> None:
    print("freeze_manifest (khóa timing + cảnh báo khi script đổi)")
    fm = str(REPO / ".agents" / "skills" / "voice-sync" / "scripts" / "freeze_manifest.py")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        (d / "audio").mkdir(parents=True)
        (d / "script").mkdir(parents=True)
        manifest = {"duration": 10.0,
                    "characters": {"host": {"voice": "Đức Trí", "speed": 1.3}},
                    "scenes": [{"id": "S01", "lines": [
                        {"id": "S01_L01", "speaker": "host", "text": "Xin chào.",
                         "start": 0.0, "duration": 1.5, "speed": 1.3}]}]}
        (d / "audio" / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
        script = {"characters": [], "scenes": [{"id": "S01", "lines": [{"id": "S01_L01", "text": "Xin chào."}]}]}
        sp = d / "script" / "script.json"
        sp.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
        code, out = run([fm, "--project", str(d)])
        tm = d / "audio" / "timing.md"
        ok("khóa lần đầu -> exit 0 + timing.md có SHA",
           code == 0 and tm.is_file() and "Script SHA:" in tm.read_text(encoding="utf-8"), out[-200:])
        code, out = run([fm, "--project", str(d)])
        ok("chạy lại khi script không đổi -> exit 0", code == 0, out[-200:])
        script["scenes"][0]["lines"][0]["text"] = "Xin chào nhé."
        sp.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
        code, out = run([fm, "--project", str(d)])
        ok("script đổi -> exit 2 + cảnh báo", code == 2 and "CẢNH BÁO" in out, out[-200:])
        code, out = run([fm, "--project", str(d), "--force"])
        ok("--force khóa lại -> exit 0", code == 0, out[-200:])


def test_render_shots() -> None:
    print("render.py --shots (chỉ render shot riêng, không cần Chrome)")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        (d / "video" / "compositions").mkdir(parents=True)
        (d / "video" / "compositions" / "SH001.html").write_text("<template></template>", encoding="utf-8")
        code, out = run([str(SCRIPTS / "render.py"), "--project", str(d), "--shots", "SH999"])
        ok("shot không có composition -> exit 1", code == 1 and "không có composition" in out, out[-200:])
        code, out = run([str(SCRIPTS / "render.py"), "--project", str(d), "--shots", "SH999", "--delivery"])
        ok("--shots + --delivery KHÔNG xung đột nữa (mục 1: ra output/shots/<id>.mp4) — thiếu composition mới fail",
           code == 1 and "không có composition" in out and "xung đột" not in out, out[-200:])


def _silent_wav(path: Path, seconds: float, sr: int = 48000) -> None:
    import wave

    n = int(seconds * sr)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(b"\x00\x00" * n)


def _flat_mp4(path: Path, seconds: float, fps: int = 30, size: str = "640x360") -> None:
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", f"color=c=red:s={size}:r={fps}:d={seconds}",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-300:]


def test_concat_shots() -> None:
    print("concat_shots (Opt round 3, mục 1: nối shot + mux giọng/SFX)")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        (d / "audio").mkdir(parents=True)
        (d / "script").mkdir(parents=True)
        (d / "output" / "shots").mkdir(parents=True)
        manifest = {"duration": 7.0, "scenes": [{"id": "S01", "lines": [
            {"id": "L1", "speaker": "host", "text": "Một.", "start": 0.0, "duration": 4.0},
            {"id": "L2", "speaker": "host", "text": "Hai.", "start": 4.0, "duration": 3.0}]}]}
        (d / "audio" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        shotlist = {"shots": [
            {"id": "SH001", "line_ids": ["L1"],
             "sfx": [{"cue": "test", "src": "sfx/test.wav", "t": 0.5}]},
            {"id": "SH002", "line_ids": ["L2"]}]}
        (d / "script" / "shotlist.json").write_text(json.dumps(shotlist), encoding="utf-8")
        _silent_wav(d / "audio" / "voiceover.wav", 7.0)
        (d / "sfx").mkdir()
        _silent_wav(d / "sfx" / "test.wav", 0.5)
        _flat_mp4(d / "output" / "shots" / "SH001.mp4", 4.0)
        _flat_mp4(d / "output" / "shots" / "SH002.mp4", 3.0)
        code, out = run([str(SCRIPTS / "concat_shots.py"), "--project", str(d), "--repo", str(d)])
        ok("nối 2 shot + mux giọng/SFX -> exit 0", code == 0, out[-300:])
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                            "-of", "csv=p=0", str(d / "output" / "final-concat.mp4")],
                           capture_output=True, text=True)
        ok("file nối dài ~7.0s", r.returncode == 0 and abs(float(r.stdout.strip()) - 7.0) < 0.3,
           r.stdout.strip())
        _flat_mp4(d / "output" / "shots" / "SH002.mp4", 3.6)
        code, out = run([str(SCRIPTS / "concat_shots.py"), "--project", str(d), "--repo", str(d)])
        ok("shot lệch 0.6s > ngưỡng 0.15s -> exit 1", code == 1 and "lệch" in out, out[-300:])
        _flat_mp4(d / "output" / "shots" / "SH002.mp4", 3.0, fps=25)
        code, out = run([str(SCRIPTS / "concat_shots.py"), "--project", str(d), "--repo", str(d)])
        ok("fps khác nhau -> exit 1", code == 1 and "fps" in out, out[-300:])
        _flat_mp4(d / "output" / "shots" / "SH002.mp4", 3.0)
        (d / "output" / "shots" / "SH001.mp4").unlink()
        code, out = run([str(SCRIPTS / "concat_shots.py"), "--project", str(d), "--repo", str(d)])
        ok("thiếu file shot -> exit 1", code == 1 and "thiếu" in out, out[-300:])
    # cửa sổ gap-inclusive (khớp build_video.py: ends[i] = wins[i+1][0]) + pad tail
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        (d / "audio").mkdir(parents=True)
        (d / "script").mkdir(parents=True)
        (d / "output" / "shots").mkdir(parents=True)
        manifest = {"duration": 7.5, "scenes": [{"id": "S01", "lines": [
            {"id": "L1", "speaker": "host", "text": "Một.", "start": 0.0, "duration": 4.0},
            {"id": "L2", "speaker": "host", "text": "Hai.", "start": 4.5, "duration": 2.5}]}]}
        (d / "audio" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        shotlist = {"shots": [
            {"id": "SH001", "line_ids": ["L1"]},
            {"id": "SH002", "line_ids": ["L2"]}]}
        (d / "script" / "shotlist.json").write_text(json.dumps(shotlist), encoding="utf-8")
        _silent_wav(d / "audio" / "voiceover.wav", 7.5)
        _flat_mp4(d / "output" / "shots" / "SH001.mp4", 4.5)
        _flat_mp4(d / "output" / "shots" / "SH002.mp4", 2.5)
        code, out = run([str(SCRIPTS / "concat_shots.py"), "--project", str(d), "--repo", str(d)])
        ok("gap 0.5s: shot 4.5s (gap-inclusive) -> exit 0", code == 0, out[-300:])
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                            "-show_entries", "stream=duration", "-of", "csv=p=0",
                            str(d / "output" / "final-concat.mp4")],
                           capture_output=True, text=True)
        ok("pad tail: video stream ~7.5s (khớp giọng)",
           r.returncode == 0 and abs(float(r.stdout.strip()) - 7.5) < 0.15, r.stdout.strip())
        _flat_mp4(d / "output" / "shots" / "SH001.mp4", 4.0)
        code, out = run([str(SCRIPTS / "concat_shots.py"), "--project", str(d), "--repo", str(d)])
        ok("shot chỉ dài bằng line (4.0s, thiếu gap) -> exit 1", code == 1 and "lệch" in out,
           out[-300:])


def test_detect_issues() -> None:
    print("detect_issues (Opt round 3, mục 2: black/freeze/silence)")
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        src = d / "base.mp4"
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                            "-i", "testsrc=size=320x180:rate=30:d=6",
                            "-f", "lavfi", "-i", "sine=frequency=440:d=6",
                            "-shortest", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                            "-c:a", "aac", str(src)], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr[-300:]
        code, out = run([str(SCRIPTS / "detect_issues.py"), "--video", str(src)])
        ok("video sạch -> exit 0 + 'sạch'", code == 0 and "sạch" in out, out[-300:])
        black = d / "black.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src),
                        "-vf", "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,2,5)'",
                        "-c:a", "copy", str(black)], check=True, capture_output=True)
        code, out = run([str(SCRIPTS / "detect_issues.py"), "--video", str(black)])
        ok("đen 3s -> cờ đen", code == 0 and "đen 2.00" in out, out[-300:])
        mute = d / "mute.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src),
                        "-af", "volume=0:enable='between(t,2,5)'",
                        "-c:v", "copy", str(mute)], check=True, capture_output=True)
        code, out = run([str(SCRIPTS / "detect_issues.py"), "--video", str(mute)])
        ok("câm 3s -> cờ câm", code == 0 and "câm" in out, out[-300:])
        frz = d / "freeze.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src), "-filter_complex",
                        "[0:v]trim=0:2,setpts=PTS-STARTPTS[a];[0:v]trim=2:2.033,setpts=PTS-STARTPTS,loop=loop=89:size=1:start=0,setpts=N/30/TB[b];[0:v]trim=5,setpts=PTS-STARTPTS[c];[a][b][c]concat=n=3:v=1:a=0[v]",
                        "-map", "[v]", "-map", "0:a", "-c:a", "copy", str(frz)],
                       check=True, capture_output=True)
        code, out = run([str(SCRIPTS / "detect_issues.py"), "--video", str(frz)])
        ok("đứng hình 3s -> cờ đứng hình", code == 0 and "đứng hình" in out, out[-300:])
        # map khoảng đen vào shot: đen 0.5–2.5s nằm trọn trong SH001 (0–3s)
        black1 = d / "black1.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(src),
                        "-vf", "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,0.5,2.5)'",
                        "-c:a", "copy", str(black1)], check=True, capture_output=True)
        p = d / "p"
        (p / "audio").mkdir(parents=True)
        (p / "script").mkdir(parents=True)
        manifest = {"duration": 6.0, "scenes": [{"id": "S01", "lines": [
            {"id": "L1", "speaker": "host", "text": "Một.", "start": 0.0, "duration": 3.0},
            {"id": "L2", "speaker": "host", "text": "Hai.", "start": 3.0, "duration": 3.0}]}]}
        (p / "audio" / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        shotlist = {"shots": [{"id": "SH001", "line_ids": ["L1"]}, {"id": "SH002", "line_ids": ["L2"]}]}
        (p / "script" / "shotlist.json").write_text(json.dumps(shotlist), encoding="utf-8")
        code, out = run([str(SCRIPTS / "detect_issues.py"), "--project", str(p), "--video", str(black1)])
        ok("khoảng đen map đúng shot SH001 (không lẫn SH002)",
           code == 0 and "SH001" in out and "SH002" not in out, out[-300:])
        # đuôi câm cuối video được miễn (giọng hết trước khi hình hết là bình thường).
        # Lưu ý: audio stream phải DÀI bằng video (3s sine + 3s lặng pad) thì
        # silencedetect mới thấy khoảng lặng — stream audio kết thúc sớm thì
        # ffmpeg không còn gì để phân tích, không cờ gì cả.
        tail = d / "tail.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                        "-i", "testsrc=size=320x180:rate=30:d=6",
                        "-f", "lavfi", "-i", "sine=frequency=440:d=3",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
                        "-af", "apad=whole_dur=6", "-t", "6", str(tail)], check=True, capture_output=True)
        code, out = run([str(SCRIPTS / "detect_issues.py"), "--video", str(tail)])
        ok("câm 3s ở đuôi video -> miễn, không tính lỗi",
           code == 0 and "đuôi video" in out, out[-300:])


def test_gates_auto_skip() -> None:
    print("gates.py --auto-skip (Opt round 3, backlog: bỏ bước Chrome khi chỉ đổi .py/.md)")
    import importlib.util
    import os
    import time

    spec = importlib.util.spec_from_file_location("gates", str(SCRIPTS / "gates.py"))
    gates = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gates)

    def make_repo(td: Path) -> Path:
        repo = td / "repo"
        (repo / ".agents" / "skills" / "test").mkdir(parents=True)

        def git(*a):
            r = subprocess.run(["git", *a], cwd=repo, capture_output=True, text=True)
            assert r.returncode == 0, r.stderr[-300:]

        git("init", "-q")
        git("config", "user.email", "t@t.t")
        git("config", "user.name", "t")
        (repo / ".agents" / "skills" / "test" / "x.py").write_text("x = 1\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-qm", "init")
        return repo

    with tempfile.TemporaryDirectory() as td:
        repo = make_repo(Path(td))
        ok2, _ = gates.only_py_md_changed(repo)
        ok("cây sạch -> đủ điều kiện skip", ok2)
        (repo / ".agents" / "skills" / "test" / "x.py").write_text("x = 2\n", encoding="utf-8")
        ok2, _ = gates.only_py_md_changed(repo)
        ok("chỉ .py đổi -> đủ điều kiện skip", ok2)
        (repo / "data.json").write_text("{}", encoding="utf-8")
        ok2, _ = gates.only_py_md_changed(repo)
        ok("thêm file .json đổi -> KHÔNG skip", not ok2)
        (repo / "data.json").unlink()
        proj = Path(td) / "p"
        (proj / "video").mkdir(parents=True)
        (proj / "video" / "index.html").write_text("<html></html>", encoding="utf-8")
        old = time.time() - 3600
        os.utime(proj / "video" / "index.html", (old, old))
        ok("video/ cũ hơn code -> không rebuild",
           not gates.video_newer_than_code(proj, repo))
        now = time.time()
        os.utime(proj / "video" / "index.html", (now, now))
        ok("video/ mới hơn code -> vừa rebuild",
           gates.video_newer_than_code(proj, repo))
    # end-to-end: --auto-skip trên bản copy demo #3 + repo giả -> SKIP hyperframes, không chạy Chrome
    demo = REPO / "projects" / "demo-30s-than-trung"
    with tempfile.TemporaryDirectory() as td:
        repo = make_repo(Path(td))
        py = repo / ".agents" / "skills" / "test" / "x.py"
        py.write_text("x = 2\n", encoding="utf-8")  # chỉ .py đổi
        d = Path(td) / "demo"
        shutil.copytree(demo, d, ignore=shutil.ignore_patterns("output"))
        old = time.time() - 3600  # video/ cũ hơn lần sửa .py (py vừa touch = now)
        for p in (d / "video").rglob("*"):
            if p.is_file():
                os.utime(p, (old, old))
        code, out = run([str(SCRIPTS / "gates.py"), "--project", str(d),
                         "--auto-skip", "--repo", str(repo), "--scenes", "S01"])
        ok("--auto-skip: bỏ hyperframes, 3 gate Python vẫn chạy",
           code == 0 and "[SKIP] hyperframes" in out, out[-400:])


def test_lazy_load() -> None:
    print("build_voiceover lazy-load (Opt round 3, mục 5: quét cache trước khi nạp model)")
    import importlib.util

    vs = REPO / ".agents" / "skills" / "voice-sync" / "scripts"
    spec = importlib.util.spec_from_file_location("build_voiceover", str(vs / "build_voiceover.py"))
    bv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bv)
    char = {"id": "host", "name": "Host", "voice": "Đức Trí",
            "temperature": 0.85, "ref_audio": None, "denoise": False}
    cast = {"host": char}
    speeds = {"L1": 1.3, "L2": 1.3, "L3": 1.3}
    scenes = [{"id": "S01", "lines": [
        {"id": "L1", "speaker": "host", "text": "Xin chào."},
        {"id": "L2", "speaker": "host", "text": "Tạm biệt."},
        {"id": "L3", "speaker": "host", "text": "Alo."}]}]
    with tempfile.TemporaryDirectory() as td:
        lines_dir = Path(td) / "lines"
        lines_dir.mkdir(parents=True)
        # L1: cache khớp key -> hit. L2: không có file -> miss.
        k1 = bv.make_key("Xin chào.", char, 1.3)
        (lines_dir / "L1.wav").write_bytes(b"RIFF....")
        (lines_dir / "L1.json").write_text(
            json.dumps({"key": k1, "duration": 1.5}), encoding="utf-8")
        entries, uncached, hits, durs = bv.scan_cache(scenes, cast, speeds, lines_dir)
        ok("scan_cache: L1 hit, L2+L3 miss",
           hits == 1 and [e["lid"] for e in uncached] == ["L2", "L3"]
           and durs.get("L1") == 1.5, f"hits={hits} uncached={[e['lid'] for e in uncached]}")
        # L3: meta ghi bằng tên chuẩn "Hải Đăng", script ghi alias "Minh Quân".
        # Dùng scenes chỉ có L3 để không lẫn với L1 (ghi bằng "Đức Trí").
        char_alias = {"id": "host", "name": "Host", "voice": "Minh Quân",
                      "temperature": 0.85, "ref_audio": None, "denoise": False}
        k3 = bv.make_key("Alo.", {**char_alias, "voice": "Hải Đăng"}, 1.3)
        (lines_dir / "L3.wav").write_bytes(b"RIFF....")
        (lines_dir / "L3.json").write_text(
            json.dumps({"key": k3, "duration": 0.8}), encoding="utf-8")
        scenes3 = [{"id": "S01", "lines": [{"id": "L3", "speaker": "host", "text": "Alo."}]}]
        _, uncached2, _, _ = bv.scan_cache(scenes3, {"host": char_alias}, {"L3": 1.3}, lines_dir)
        ok("quét bằng tên alias -> L3 miss (key khác tên chuẩn)",
           [e["lid"] for e in uncached2] == ["L3"])
        char_alias["voice"] = "Hải Đăng"  # mô phỏng canonicalize sau khi nạp model
        uncached3, hits3, durs3 = bv.rescan_after_canonicalize(uncached2, 0, {})
        ok("sau canonicalize, quét lại -> L3 hit cache cũ",
           hits3 == 1 and durs3.get("L3") == 0.8 and uncached3 == [], f"hits={hits3}")
    # End-to-end: chạy lại trên bản copy demo #3 (7 line đã cache) bằng python
    # của test venv — KHÔNG có vieneu. Nếu code hồi quy (nạp model trước khi
    # quét cache) thì chết PackageNotInstalled, exit != 0.
    demo = REPO / "projects" / "demo-30s-than-trung"
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "demo"
        shutil.copytree(demo / "script", d / "script")
        shutil.copytree(demo / "audio", d / "audio")
        code, out = run([str(vs / "build_voiceover.py"),
                         "--script", str(d / "script" / "script.json"),
                         "--out", str(d / "audio")])
        ok("chạy lại all-cached: exit 0 + bỏ qua nạp model",
           code == 0 and "bỏ qua nạp model" in out, out[-300:])


def main() -> int:
    test_timing_lib()
    test_check_shots()
    test_build_video_tweens()
    test_hand_over()
    test_schemas()
    test_check_audio()
    test_check_sync()
    test_freeze_manifest()
    test_render_shots()
    test_lazy_load()
    test_concat_shots()
    test_detect_issues()
    test_gates_auto_skip()
    print(f"\n{'TẤT CẢ QUA' if not FAILS else f'THẤT BẠI {len(FAILS)}: ' + '; '.join(FAILS)}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
