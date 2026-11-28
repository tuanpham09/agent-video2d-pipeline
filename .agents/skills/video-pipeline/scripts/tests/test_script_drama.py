#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test check_script_drama.py: bản đúng sạch; mỗi biến thể hỏng phải bị bắt đúng mã."""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from check_script_drama import Gate  # noqa: E402

BIBLE = {"characters": [{"id": "host"}, {"id": "ngan"}, {"id": "hung"}]}


def L(sid, n, text="Câu thoại ngắn."):
    return {"id": f"{sid}_L{n:02d}", "speaker": "host", "text": text}


def scene(sid, n, **drama):
    return {"id": sid, "lines": [L(sid, i + 1) for i in range(n)], "drama": drama}


def base():
    s = [
        scene("S1", 6, beat="hook", tension=3, turn="nhóm thách nhau cầu cơ", hook_out="ai sẽ hỏi câu thứ ba?"),
        scene("S2", 6, beat="warning", tension=4, turn="cơ trả lời đúng tên người chết", hook_out="vì sao nó biết?", causes=["S1"]),
        scene("S3", 6, beat="first_disaster", tension=6, turn="Hưng bỏ vòng tròn muối", hook_out="Hưng đi đâu?", causes=["S2", "R1"]),
        scene("S4", 6, beat="midpoint", tension=5, turn="Ngân nhận ra cơ gọi bằng tên cũ", hook_out="tên cũ là của ai?", causes=["S3"]),
        scene("S5", 6, beat="escalation", tension=7, turn="Hưng không có bóng", hook_out="quay lại nghĩa địa", causes=["S4", "M1"]),
        scene("S6", 6, beat="climax", tension=9, turn="Hưng đã chết từ ba ngày trước", hook_out="cơ còn một câu hỏi", causes=["S5"]),
        scene("S7", 3, beat="resolution", tension=4, turn="tiễn cơ", hook_out="", causes=["S6"]),
    ]
    d = {
        "promise": "vì sao cơ biết tên người chết",
        "genre": "ghost_ritual",
        "tension_pattern": "escalating_peaks",
        "rules": [{"id": "R1", "text": "chỉ hỏi ba câu", "cost": "câu thứ tư gọi người hỏi", "plant": "S1_L03",
                   "first_use": "S2_L02", "violations": ["S3_L04"]}],
        "loops": [
            {"id": "M1", "type": "mystery", "question": "ai là người trả lời?", "plant": "S1_L02",
             "clues": ["S2_L03", "S4_L02"], "payoff": "S6_L05"},
            {"id": "O1", "type": "object", "question": "chiếc nhẫn của Hưng", "plant": "S1_L05",
             "trigger": "S4_L05", "payoff": "S6_L02"},
            {"id": "P1", "type": "promise", "question": "đừng quay lại", "plant": "S2_L05", "payoff": "S7_L02"},
        ],
        "motives": [{"char": "ngan", "role": "protagonist", "want": "về an toàn", "obstacle": "cơ gọi tên"},
                    {"char": "hung", "role": "antagonist", "want": "không ai biết mình chết", "obstacle": "cơ nói thật"}],
    }
    return {"drama": d, "scenes": s}


def run(script, strict=True):
    g = Gate(script, BIBLE, strict)
    g.run()
    return g


def codes(g):
    return {c for c, _ in g.errors}, {c for c, _ in g.warns}


def must(name, mut, code, kind="err"):
    s = base()
    mut(s)
    e, w = codes(run(s))
    ok = code in (e if kind == "err" else w)
    print(("ok   " if ok else "FAIL ") + f"{name} → {code} ({kind}); errors={sorted(e)} warns={sorted(w)}")
    return ok


def main():
    g = run(base())
    e, w = codes(g)
    res = [not e]
    print(("ok   " if not e else "FAIL ") + f"baseline sạch; errors={g.errors} warns={g.warns}")
    res.append(must("không có drama (strict)", lambda s: s.pop("drama"), "DR1"))
    res.append(must("loop thiếu payoff", lambda s: s["drama"]["loops"][2].pop("payoff"), "DR4"))
    res.append(must("2 loop open", lambda s: [s["drama"]["loops"][1].pop("payoff"), s["drama"]["loops"][1].update(open=True),
                                              s["drama"]["loops"][2].pop("payoff"), s["drama"]["loops"][2].update(open=True)], "DR4"))
    res.append(must("payoff trước trigger", lambda s: s["drama"]["loops"][1].update(payoff="S3_L01"), "DR3"))
    res.append(must("payoff trước plant", lambda s: s["drama"]["loops"][2].update(payoff="S1_L01"), "DR3"))
    res.append(must("line id không có", lambda s: s["drama"]["loops"][2].update(payoff="S9_L01"), "DR3"))
    res.append(must("plant sát payoff", lambda s: s["drama"]["loops"][2].update(plant="S7_L01"), "DR3", "warn"))
    res.append(must("mystery chỉ 1 clue", lambda s: s["drama"]["loops"][0].update(clues=["S2_L03"]), "DR8"))
    res.append(must("clue sau payoff", lambda s: s["drama"]["loops"][0].update(clues=["S2_L03", "S6_L06"]), "DR8"))
    res.append(must("rule không cost", lambda s: s["drama"]["rules"][0].pop("cost"), "DR5"))
    res.append(must("dùng luật trước khi nêu luật", lambda s: s["drama"]["rules"][0].update(plant="S2_L04", first_use="S2_L02"), "DR5"))
    res.append(must("rule không vi phạm", lambda s: s["drama"]["rules"][0].update(violations=[]), "DR5", "warn"))
    res.append(must("hook chào hỏi", lambda s: s["scenes"][0]["lines"][0].update(text="Xin chào các bạn, hôm nay mình kể chuyện ma"), "DR2"))
    res.append(must("hook quá dài", lambda s: s["scenes"][0]["lines"][0].update(text=" ".join(["từ"] * 20)), "DR2", "warn"))
    res.append(must("gài đầu quá muộn", lambda s: [s["drama"]["loops"][0].update(plant="S2_L01"), s["drama"]["loops"][1].update(plant="S2_L02"),
                                                    s["drama"]["loops"][2].update(plant="S2_L05"), s["drama"]["rules"][0].update(plant="S2_L01", first_use="S2_L02")], "DR2"))
    res.append(must("thiếu climax", lambda s: s["scenes"][5]["drama"].update(beat="escalation"), "DR6"))
    res.append(must("đỉnh không phải climax", lambda s: s["scenes"][4]["drama"].update(tension=10), "DR6"))
    res.append(must("tension ngoài 0-10", lambda s: s["scenes"][2]["drama"].update(tension=12), "DR6"))
    res.append(must("không leo thang", lambda s: [d.update(tension=5) for d in (x["drama"] for x in s["scenes"][:6])] and s["scenes"][5]["drama"].update(tension=6), "DR6"))
    res.append(must("nhịp phẳng", lambda s: [s["scenes"][i]["drama"].update(tension=5) for i in range(1, 5)], "DR6", "warn"))
    res.append(must("cảnh thiếu turn", lambda s: s["scenes"][1]["drama"].pop("turn"), "DR7", "warn"))
    res.append(must("cảnh thiếu hook_out", lambda s: s["scenes"][2]["drama"].pop("hook_out"), "DR7", "warn"))
    res.append(must("quãng dài không biến cố", lambda s: s["scenes"][2].update(lines=[L("S3", i + 1) for i in range(40)]), "DR7", "warn"))
    res.append(must("thiếu causes", lambda s: s["scenes"][3]["drama"].pop("causes"), "DR9", "warn"))
    res.append(must("nhân quả ngược", lambda s: s["scenes"][1]["drama"].update(causes=["S5"]), "DR9", "warn"))
    res.append(must("motive ∉ bible", lambda s: s["drama"]["motives"][0].update(char="ma_la"), "DR10"))
    res.append(must("motive thiếu obstacle", lambda s: s["drama"]["motives"][1].pop("obstacle"), "DR10"))
    res.append(must("không có antagonist", lambda s: s["drama"]["motives"][1].update(role="support"), "DR10", "warn"))
    # không báo oan: không strict thì thiếu drama chỉ cảnh báo
    s = base(); s.pop("drama")
    e, w = codes(run(s, strict=False))
    ok = not e and "DR1" in w
    res.append(ok)
    print(("ok   " if ok else "FAIL ") + f"không strict: thiếu drama chỉ cảnh báo; errors={sorted(e)}")
    # slow_burn đúng mẫu không bị báo oan
    s = base(); s["drama"]["tension_pattern"] = "slow_burn"
    e, w = codes(run(s))
    res.append(not e)
    print(("ok   " if not e else "FAIL ") + f"slow_burn hợp lệ; errors={sorted(e)}")
    print("OK" if all(res) else f"FAIL: {res.count(False)} ca")
    return 0 if all(res) else 1


if __name__ == "__main__":
    sys.exit(main())
