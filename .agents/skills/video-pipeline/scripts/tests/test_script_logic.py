#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm thử check_script_logic.py bằng kịch bản mini dựng trong bộ nhớ: bản đúng phải sạch; mỗi biến thể hỏng phải bắt đúng mã lỗi.

Chạy:  python .agents/skills/video-pipeline/scripts/tests/test_script_logic.py   (mã thoát 0 = qua hết)
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from check_script_logic import Gate  # noqa: E402

BIBLE = {
    "characters": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
    "locations": [
        {"id": "nha", "kind": "int", "connects": [{"to": "san", "via": "cửa"}]},
        {"id": "san", "kind": "ext", "connects": [{"to": "ngo", "via": "cổng"}]},
        {"id": "ngo", "kind": "ext"},
        {"id": "xa", "kind": "ext"},
    ],
    "props": [{"id": "den", "states": ["lit", "out"]}, {"id": "khan", "states": ["folded", "spread"]}],
}
SCRIPT = {
    "characters": [{"id": "host", "name": "Lâm", "role": "narrator"}, {"id": "a", "name": "An", "role": "character"},
                   {"id": "b", "name": "Bình", "role": "character"}, {"id": "c", "name": "Cúc", "role": "character"}],
    "scenes": [
        {"id": "S01", "title": "t", "lines": [{"id": "S01_L01", "speaker": "a", "text": "x"}, {"id": "S01_L02", "speaker": "b", "text": "y"}],
         "setting": {"location": "nha", "int_ext": "int", "time": "night", "story_time": "N1 22:00", "frame": "present", "link": "cut"},
         "cast": [{"id": "a", "holding": ["khan"]}, {"id": "b"}],
         "staging": [{"after": "S01_L01", "who": "a", "do": "give", "prop": "khan", "to": "b"},
                     {"after": "S01_L02", "who": "b", "do": "exit", "to": "san", "via": "cửa"}]},
        {"id": "S02", "title": "t", "lines": [{"id": "S02_L01", "speaker": "host", "text": "z"}, {"id": "S02_L02", "speaker": "b", "text": "w"}],
         "setting": {"location": "san", "int_ext": "ext", "time": "night", "story_time": "N1 22:05", "frame": "present", "link": "continuous"},
         "cast": [{"id": "b", "from": "nha"}, {"id": "c", "start": False}],
         "staging": [{"after": "S02_L01", "who": "c", "do": "enter", "from": "ngo", "via": "cổng"},
                     {"after": "S02_L02", "who": "b", "do": "gesture"}]},
    ],
}
FAILS: list[str] = []


def run(mut=None, strict=True):
    sc = copy.deepcopy(SCRIPT)
    if mut:
        mut(sc)
    g = Gate(sc, BIBLE, None, None, strict)
    g.run()
    return g


def expect(name: str, g: Gate, code: str | None, kind: str = "err") -> None:
    msgs = g.errors if kind == "err" else g.warns
    hit = [m for m in msgs if code and f"({code})" in m]
    if code is None:
        ok = not g.errors
        what = "sạch" if ok else f"lẽ ra sạch nhưng có: {g.errors}"
    else:
        ok = bool(hit)
        what = f"bắt {code}" if ok else f"KHÔNG bắt {code}; errors={g.errors} warns={g.warns}"
    print(("  ✓ " if ok else "  ✗ ") + f"{name}: {what}")
    if not ok:
        FAILS.append(name)


def S(sc, i):
    return sc["scenes"][i]


def main() -> int:
    expect("bản đúng", run(), None)
    expect("thiếu setting (strict)", run(lambda s: S(s, 0).pop("setting")), "SL1")
    expect("location lạ", run(lambda s: S(s, 0)["setting"].update(location="khong_co")), "SL1")
    expect("int_ext ≠ kind", run(lambda s: S(s, 0)["setting"].update(int_ext="ext")), "SL1")
    expect("người nói không có trong cast", run(lambda s: S(s, 0)["cast"].pop(1)), "SL2")
    expect("continuous không kề nhau", run(lambda s: (S(s, 1)["setting"].update(location="xa", int_ext="ext"), S(s, 1)["cast"][0].update(**{"from": "nha"}))), "SL3")
    expect("later khác chỗ", run(lambda s: S(s, 1)["setting"].update(link="later")), "SL3")
    expect("travel thiếu link_note", run(lambda s: S(s, 1)["setting"].update(link="travel")), "SL3")
    expect("đổi chỗ không khai from", run(lambda s: (S(s, 0)["staging"].pop(1), S(s, 1)["cast"][0].pop("from"))), "SL4")
    expect("continuous from ≠ chỗ cũ", run(lambda s: (S(s, 0)["staging"].pop(1), S(s, 1)["cast"][0].update(**{"from": "san"}))), "SL4")
    expect("exit rồi sang cảnh sau không cần from", run(lambda s: S(s, 1)["cast"][0].pop("from")), None)
    expect("enter từ chỗ không kề", run(lambda s: S(s, 1)["staging"][0].update(**{"from": "xa"})), "SL5")
    expect("hành động sau exit", run(lambda s: S(s, 0)["staging"].append({"after": "S01_L02", "who": "b", "do": "gesture"})), "SL5")
    expect("staging ngược thứ tự line", run(lambda s: S(s, 0)["staging"].reverse()), "SL5")
    expect("start=false thiếu enter", run(lambda s: S(s, 1)["staging"].pop(0)), "SL5")
    expect("give khi không cầm", run(lambda s: S(s, 0)["cast"][0].pop("holding")), "SL6")
    expect("state ngoài bible", run(lambda s: S(s, 0)["staging"].insert(0, {"after": "S01_L01", "who": "a", "do": "set_state", "prop": "den", "state": "bay"})), "SL6")
    expect("story_time đi lùi", run(lambda s: S(s, 1)["setting"].update(story_time="N1 21:00")), "SL7")
    expect("cast ∉ bible", run(lambda s: S(s, 0)["cast"].append({"id": "zzz"})), "SL8")
    expect("giờ không hợp time (cảnh báo)", run(lambda s: S(s, 0)["setting"].update(story_time="N1 12:00")), "SL7", "warn")
    expect("shot lệch địa điểm", _shot_mismatch(), "SL11")
    expect("flashback không làm đổi thế giới", _flashback_ok(), None)
    expect("moves không kề, chưa trôi thời gian", run(lambda s: S(s, 1)["setting"].update(moves=[{"after": "S02_L01", "to": "xa"}])), "SL3")
    expect("moves không kề nhưng đã trôi ≥ 30 phút", run(lambda s: S(s, 1)["setting"].update(moves=[{"after": "S02_L01", "to": "xa", "story_time": "N1 23:00"}])), None)
    expect("moves có via đi 2 bước", run(lambda s: S(s, 0)["setting"].update(moves=[{"after": "S01_L01", "to": "ngo", "via": "ra cửa rồi ra cổng"}])), None)
    expect("moves 2 bước thiếu via", run(lambda s: S(s, 0)["setting"].update(moves=[{"after": "S01_L01", "to": "ngo"}])), "SL3")
    expect("_env set_state hợp lệ", run(lambda s: S(s, 0)["staging"].insert(0, {"after": "S01_L01", "who": "_env", "do": "set_state", "prop": "den", "state": "out"})), None)
    expect("_env làm việc khác set_state", run(lambda s: S(s, 0)["staging"].insert(0, {"after": "S01_L01", "who": "_env", "do": "move"})), "SL5")
    expect("moves.story_time đi lùi", run(lambda s: S(s, 1)["setting"].update(moves=[{"after": "S02_L01", "to": "ngo", "story_time": "N1 20:00"}])), "SL7")
    expect("tên gõ lặp ký tự (cảnh báo)", run(lambda s: S(s, 0)["lines"][0].update(text="Anh Lâmm đến")), "SL10", "warn")
    print("OK" if not FAILS else f"FAIL: {len(FAILS)} ca ({', '.join(FAILS)})")
    return 0 if not FAILS else 1


def _shot_mismatch() -> Gate:
    sc = copy.deepcopy(SCRIPT)
    g = Gate(sc, BIBLE, {"shots": [{"id": "SH1", "line_ids": ["S01_L01"], "location": "san", "kind": "speaker"}]}, None, True)
    g.run()
    return g


def _flashback_ok() -> Gate:
    sc = copy.deepcopy(SCRIPT)
    fb = {"id": "S03", "title": "t", "lines": [{"id": "S03_L01", "speaker": "host", "text": "q"}],
          "setting": {"location": "xa", "int_ext": "ext", "time": "day", "frame": "flashback", "link": "cut"},
          "cast": [{"id": "a"}], "staging": []}
    sc["scenes"].insert(1, fb)  # chen giữa S01 và S02: S02 vẫn phải so với S01 (present), không so với flashback
    sc["scenes"][2]["id"] = "S02"
    g = Gate(sc, BIBLE, None, None, True)
    g.run()
    return g


if __name__ == "__main__":
    raise SystemExit(main())
