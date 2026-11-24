#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử các phần roadmap v3 (không cần VieNeu, không cần trình duyệt):
  - timing_lib: mốc theo từ, beat theo từ, ranh giới
  - check_shots E7 (mỗi nhân vật trong shot nhiều người phải có hành vi tường minh) và E8 (beat theo từ)
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
                    sh["beats"] = [b for b in sh["beats"] if not (b.get("react") or (b.get("set") or {}).get("host") or (b.get("args") or {}).get("char") == "host")]

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


def test_behaviors() -> None:
    print("behaviors (macro hành vi mẫu)")
    sys.path.insert(0, str(SCRIPTS))
    from behaviors import check_library, load_library, expand_shot  # noqa: E402
    lib = load_library()
    ok("thư viện macro hợp lệ (0 lỗi)", check_library(lib) == [], str(check_library(lib)))

    lines = {"L": {"text": "Một hai ba bốn năm.", "start": 10.0, "duration": 5.0}}
    shot = {"id": "SH999", "line_ids": ["L"], "beats": [
        {"line_id": "L", "word": 2, "macro": "nghe_gat", "args": {"char": "a"}},
        {"line_id": "L", "t": 1.0, "macro": "cham_khan", "args": {"char": "a"}}]}
    out = expand_shot(shot, lines, 10.0)
    ok("bung đúng: react nod + set pose reach-l", out["beats"][0]["react"] == {"char": "a", "preset": "nod"}
       and out["beats"][1]["set"] == {"a": {"pose": "reach-l"}}, str(out["beats"]))
    ok("macro vật lý tự thêm SFX đúng thời điểm (t=1.0)", [f["t"] for f in out["sfx"]] == [1.0] and out["beats"][1]["physical"] is True)
    ok("không sửa dữ liệu vào", "macro" in shot["beats"][0] and "sfx" not in shot)
    for bad, why in (({"macro": "khong_co"}, "macro lạ"), ({"macro": "nghe_gat"}, "thiếu tham số"),
                     ({"macro": "nghe_gat", "args": {"char": "a", "x": 1}}, "tham số lạ")):
        try:
            expand_shot({"id": "S", "beats": [{"line_id": "L", "t": 0, **bad}]}, lines, 10.0)
            ok(f"từ chối {why}", False, "không ném lỗi")
        except ValueError:
            ok(f"từ chối {why}", True)

    # end-to-end: thay beat SH008 bằng macro → check_shots qua và HTML dựng ra GIỐNG HỆT bản beat tay
    def to_macros(s):
        for sh in s["shots"]:
            if sh["id"] == "SH008":
                keep = [b for b in sh["beats"] if b.get("t") == 0.3]
                sh["beats"] = keep + [
                    {"line_id": "S01_L07", "t": 2.4, "macro": "cham_khan", "args": {"char": "me"}},
                    {"line_id": "S01_L07", "word": 9, "macro": "nhin_sang", "args": {"char": "host", "target": "me"}},
                    {"line_id": "S01_L07", "word": 17, "edge": "end", "macro": "nghe_gat", "args": {"char": "host"}}]
                sh["sfx"] = []
    with tempfile.TemporaryDirectory() as td:
        a, b = Path(td) / "ra" / "p", Path(td) / "rb" / "p"  # cùng tên thư mục project (index.html có <title> theo tên)
        a.mkdir(parents=True); b.mkdir(parents=True)
        write_min_project(a)
        write_min_project(b, to_macros)
        code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(b), "--scenes", "S01"])
        ok("check_shots qua khi dùng macro (E5/E7/R6.1 thấy beat đã bung)", code == 0, out[-300:])
        for d, name in ((a, "va"), (b, "vb")):
            c, o = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--shots", "SH008", "--out", str(Path(td) / name)])
            ok(f"build_video dựng được ({name})", c == 0, o[-200:])
        ha = (Path(td) / "va" / "compositions" / "SH008.html").read_text(encoding="utf-8")
        hb = (Path(td) / "vb" / "compositions" / "SH008.html").read_text(encoding="utf-8")
        ok("HTML từ macro giống hệt HTML từ beat viết tay", ha == hb)
        ia = (Path(td) / "va" / "index.html").read_text(encoding="utf-8")
        ib = (Path(td) / "vb" / "index.html").read_text(encoding="utf-8")
        ok("index (gồm SFX) giống hệt", ia == ib)

    def no_sfx(s):
        to_macros(s)
        for sh in s["shots"]:
            if sh["id"] == "SH008":
                sh["beats"][1]["args"]["char"] = "me"
                sh["beats"] = [x for x in sh["beats"] if x.get("macro") != "cham_khan"] + [
                    {"line_id": "S01_L07", "t": 2.4, "do": "chạm khăn", "physical": True, "set": {"me": {"pose": "reach-l"}}}]
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d, no_sfx)
        code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        ok("beat vật lý viết tay thiếu SFX vẫn bị bắt (gate không bị macro làm lỏng)", code == 1 and "chưa có SFX" in out, out[-300:])

    def ghost(s):
        for sh in s["shots"]:
            if sh["id"] == "SH008":
                sh["beats"].append({"line_id": "S01_L07", "t": 1.0, "macro": "nhin_sang", "args": {"char": "host", "target": "ma"}})
                sh["beats"].append({"line_id": "S01_L07", "t": 1.2, "macro": "trao_do", "args": {"prop": "khong_co", "from": "me", "to": "host"}})
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d, ghost)
        code, out = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        ok("E9: macro nhắc nhân vật/đạo cụ không có trong shot bị báo",
           code == 1 and "nhân vật 'ma' không có trong shot" in out and "prop 'khong_co'" in out and "macro nhin_sang" in out, out[-400:])


def test_actions() -> None:
    print("hành động mới (quỳ, lạy, chạy, ngất, ôm đầu)")
    sys.path.insert(0, str(SCRIPTS))
    from behaviors import expand_shot, load_library  # noqa: E402
    lib = load_library()
    lines = {"L": {"text": "Một hai ba bốn năm.", "start": 10.0, "duration": 5.0}}
    out = expand_shot({"id": "S", "beats": [{"line_id": "L", "t": 1.0, "macro": "ngat", "args": {"char": "a"}}]}, lines, 10.0)
    ts = [round(b["dt"] + 1.0, 2) for b in out["beats"]]
    ok("ngất = 3 khung (t, +0.18, +0.36) stagger → tilt → lie", ts == [1.0, 1.18, 1.36]
       and [b["set"]["a"]["stance"] for b in out["beats"]] == ["stagger", "tilt", "lie"], str(out["beats"]))
    ok("ngất: chỉ khung cuối là vật lý và SFX ngã đúng khung cuối", [b["physical"] for b in out["beats"]] == [False, False, True]
       and abs(out["sfx"][0]["t"] - 1.36) < 1e-6, str(out["sfx"]))
    ok("chạy: move có gait=run", expand_shot({"id": "S", "beats": [{"line_id": "L", "t": 0, "macro": "chay_toi", "args": {"char": "a", "to": "R"}}]},
                                           lines, 10.0)["beats"][1]["move"]["gait"] == "run")

    def acts(s):
        for sh in s["shots"]:
            if sh["id"] == "SH008":
                keep = [b for b in sh["beats"] if b.get("t") == 0.3]
                sh["beats"] = keep + [
                    {"line_id": "S01_L07", "t": 0.5, "macro": "chay_toi", "args": {"char": "host", "to": "L", "dur": 0.8}},
                    {"line_id": "S01_L07", "t": 1.4, "macro": "quy_xuong", "args": {"char": "host"}},
                    {"line_id": "S01_L07", "t": 2.0, "macro": "om_dau", "args": {"char": "me"}},
                    {"line_id": "S01_L07", "word": 9, "macro": "nhin_sang", "args": {"char": "host", "target": "me"}},
                    {"line_id": "S01_L07", "t": 2.6, "macro": "ngat", "args": {"char": "me"}},
                    {"line_id": "S01_L07", "word": 17, "edge": "end", "macro": "nghe_gat", "args": {"char": "host"}}]
                sh["sfx"] = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d, acts)
        code, o = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        ok("check_shots qua với macro hành động", code == 0, o[-300:])
        c, o = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--shots", "SH008", "--out", str(Path(td) / "v")])
        ok("build_video dựng được", c == 0, o[-200:])
        h = (Path(td) / "v" / "compositions" / "SH008.html").read_text(encoding="utf-8")
        ok("HTML có nhịp chạy run-a/run-b, stance kneel và lie", all(k in h for k in ('"run-a"', '"run-b"', '"kneel"', '"lie"', '"stagger"')))

    def bad_state(s):
        for sh in s["shots"]:
            if sh["id"] == "SH008":
                sh["beats"].append({"line_id": "S01_L07", "t": 1.0, "do": "bay", "set": {"host": {"stance": "bay_len"}}})
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d, bad_state)
        code, o = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        ok("E10: stance ngoài rig.json bị báo", code == 1 and "E10" in o and "bay_len" in o, o[-300:])


def test_combos_autoface() -> None:
    print("chuỗi ghép sẵn + tự quay mặt (view: auto)")
    sys.path.insert(0, str(SCRIPTS))
    from behaviors import expand_shot  # noqa: E402
    lines = {"L": {"text": "Một hai ba bốn năm.", "start": 10.0, "duration": 5.0}}

    def ex(macro, args, t=1.0):
        return expand_shot({"id": "S", "beats": [{"line_id": "L", "t": t, "macro": macro, "args": args}]}, lines, 10.0)

    o = ex("cau_xin", {"char": "a"})
    ok("cau_xin: quỳ → lạy → quỳ ở t, t+1.2, t+2.4, SFX khớp từng nhịp",
       [round(b["dt"] + 1.0, 2) for b in o["beats"]] == [1.0, 2.2, 3.4]
       and [b["set"]["a"]["stance"] for b in o["beats"]] == ["kneel", "lay", "kneel"]
       and [round(f["t"], 2) for f in o["sfx"]] == [1.0, 2.2, 3.4] and all(b["physical"] for b in o["beats"]), str(o["sfx"]))
    o = ex("cau_xin", {"char": "a", "gap": 0.8, "gap2": 1.6})
    ok("cau_xin: đổi nhịp bằng tham số (gap/gap2) cả beat lẫn SFX", [round(f["t"], 2) for f in o["sfx"]] == [1.0, 1.8, 2.6]
       and [round(b["dt"], 2) for b in o["beats"]] == [0.0, 0.8, 1.6])
    o = ex("soc_roi_ngat", {"char": "a", "suf": "-r"})
    ok("soc_roi_ngat: 6 beat, chỉ khung nằm là vật lý, SFX ngã +1.16 s, hướng -r",
       len(o["beats"]) == 6 and [b["physical"] for b in o["beats"]] == [False] * 5 + [True]
       and abs(o["sfx"][0]["t"] - 2.16) < 1e-6 and o["beats"][-1]["set"]["a"]["stance"] == "lie-r", str(o["beats"][-1]))
    o = ex("chay_roi_om_dau", {"char": "a", "to": "R"})
    ok("chay_roi_om_dau: chạy rồi ôm đầu sau `after` giây", o["beats"][1]["move"]["gait"] == "run"
       and o["beats"][3]["set"]["a"]["pose"] == "cover-head" and round(o["beats"][3]["dt"], 2) == 1.0)
    ok("so_roi_bo_chay/vai_chao bung được", len(ex("so_roi_bo_chay", {"char": "a", "to": "L"})["beats"]) == 4
       and len(ex("vai_chao", {"char": "a"})["beats"]) == 2)

    def combos(s):
        for sh in s["shots"]:
            if sh["id"] == "SH008":
                keep = [b for b in sh["beats"] if b.get("t") == 0.3]
                sh["beats"] = keep + [
                    {"line_id": "S01_L07", "t": 0.4, "macro": "cau_xin", "args": {"char": "host"}},
                    {"line_id": "S01_L07", "t": 1.0, "macro": "soc_roi_ngat", "args": {"char": "me", "suf": "-r"}},
                    {"line_id": "S01_L07", "word": 9, "macro": "nhin_sang", "args": {"char": "host", "target": "me"}},
                    {"line_id": "S01_L07", "word": 17, "edge": "end", "macro": "nghe_gat", "args": {"char": "host"}}]
                sh["sfx"] = []
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d, combos)
        code, o = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        ok("check_shots qua với chuỗi ghép sẵn (SFX từng nhịp vật lý khớp)", code == 0, o[-300:])
        c, o = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--shots", "SH008", "--out", str(Path(td) / "v")])
        h = (Path(td) / "v" / "compositions" / "SH008.html").read_text(encoding="utf-8") if c == 0 else ""
        ok("auto-face: host (trái) quỳ quay tq-r về phía me", c == 0 and '"data-view": "tq-r"' in h, o[-200:])
        ok("chuỗi ngất: có stagger-r → tilt-r → lie-r", all(k in h for k in ('"stagger-r"', '"tilt-r"', '"lie-r"')))

    def auto_me(s):
        for sh in s["shots"]:
            if sh["id"] == "SH008":
                sh["beats"].append({"line_id": "S01_L07", "t": 1.5, "do": "mẹ quay mặt", "set": {"me": {"view": "auto"}}})
    with tempfile.TemporaryDirectory() as td:
        d = Path(td) / "p"
        d.mkdir()
        write_min_project(d, auto_me)
        code, o = run([str(SCRIPTS / "check_shots.py"), "--project", str(d), "--scenes", "S01"])
        c, o2 = run([str(SCRIPTS / "build_video.py"), "--project", str(d), "--shots", "SH008", "--out", str(Path(td) / "v")])
        h = (Path(td) / "v" / "compositions" / "SH008.html").read_text(encoding="utf-8") if c == 0 else ""
        ok("auto-face: me (phải) quay tq-l về phía host; E10 chấp nhận view=auto", code == 0 and c == 0 and '"data-view": "tq-l"' in h, o[-200:] + o2[-200:])


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


def main() -> int:
    test_timing_lib()
    test_check_shots()
    test_build_video_tweens()
    test_hand_over()
    test_behaviors()
    test_actions()
    test_combos_autoface()
    test_schemas()
    test_check_audio()
    print(f"\n{'TẤT CẢ QUA' if not FAILS else f'THẤT BẠI {len(FAILS)}: ' + '; '.join(FAILS)}")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
