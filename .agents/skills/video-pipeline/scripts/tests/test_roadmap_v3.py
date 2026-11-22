#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử các phần roadmap v3 (không cần VieNeu, không cần trình duyệt):
  - timing_lib: mốc theo từ, beat theo từ, ranh giới
  - check_shots E7 (mỗi nhân vật trong shot nhiều người phải có hành vi tường minh) và E8 (beat theo từ),
    E9 (pose/emotion/stance/gaze phải có trong rig) và E10 (nhân vật không đứng đè lên đạo cụ)
  - check_sync: layout 1 track giọng duy nhất được chấp nhận (kiểm src, duration, file wav);
    layout clip-riêng từng line vẫn kiểm nghiêm; dựng từng phần chỉ kiểm line được phủ
  - build_video: beat move/look/react sinh tween đúng; người nghe tự gật không trùng gật tường minh
  - check_audio: bắt đúng clip, câm, sai thời lượng, chồng lấn; câu đạt không báo lỗi

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


def main() -> int:
    test_timing_lib()
    test_check_shots()
    test_build_video_tweens()
    test_hand_over()
    test_schemas()
    test_check_audio()
    test_check_sync()
    print(f"\n{'TẤT CẢ QUA' if not FAILS else f'THẤT BẠI {len(FAILS)}: ' + '; '.join(FAILS)}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
