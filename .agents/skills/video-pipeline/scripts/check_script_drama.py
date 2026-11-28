#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate KỊCH TÍNH của kịch bản (chạy cùng check_script_logic, trước TTS, R1.5).

Đọc script/script.json: khối `drama` (promise, genre, tension_pattern, rules, loops, motives) và `scene.drama`
(beat, tension, turn, hook_out, causes). Biến "gài mở – đóng" thành dữ liệu kiểm được, theo mô hình Foreshadow–Trigger–Payoff
(arXiv 2601.07033: mỗi setup là một "nợ nhân quả" phải trả; payoff không được đến trước trigger), cấu trúc kinh dị (setup lời cảnh báo →
"vì sao bây giờ" → thảm hoạ đầu → điểm không quay lại → midpoint → đỉnh → mở/đóng), và quy tắc giữ chân video ngắn (hook 1–3 s,
không dẫn nhập, không để quãng dài không có biến cố). Chi tiết: references/script-drama-guide.md.

Mã lỗi:
  DR1  thiếu/sai khối drama (promise, genre, tension_pattern, loops≥1) hoặc scene.drama thiếu     [thiếu: lỗi khi --strict, else cảnh báo]
  DR2  hook: câu đầu quá dài (>14 từ) / chào hỏi dẫn nhập / cảnh 1 không phải beat hook / chưa gài vòng lặp nào trong 6 câu đầu
  DR3  loop sai: plant/trigger/payoff không phải line id thật; sai thứ tự plant<trigger<payoff (payoff đến sớm = lỗi);
       plant và payoff cách <3 câu (cảnh báo: không có thời gian để người xem quên)
  DR4  loop không có payoff (lỗi, trừ tối đa 1 loop `open: true` làm tease cho phần sau)
  DR5  rule (luật của siêu nhiên/lời nguyền): thiếu `cost`, plant sau lần dùng đầu, hoặc không có `violations` (cảnh báo: luật không ảnh hưởng gì)
  DR6  nhịp căng: tension ngoài 0–10, thiếu đúng 1 cảnh `climax`, đỉnh không phải climax, cuối không dịu, ≥4 cảnh liền cùng mức (phẳng),
       pattern escalating_peaks: đỉnh 1/3 cuối phải cao hơn đỉnh 1/3 đầu ≥2; slow_burn: trung bình 1/3 cuối cao hơn đầu ≥1.5; midpoint ngoài 35–65%
  DR7  cảnh (trừ cuối) thiếu `turn` (điều thay đổi) hoặc `hook_out` (câu hỏi/đe doạ kéo sang cảnh sau); quãng >20 câu không có biến cố
  DR8  loop `mystery`: cần ≥2 `clues` (công bằng với người xem), mọi clue đứng trước payoff
  DR9  cảnh (trừ cảnh 1) thiếu `causes` (cảnh/loop gây ra nó) hoặc trỏ tới cảnh đứng sau (nhân quả ngược)   [cảnh báo]
  DR10 motives: nhân vật ∉ bible, thiếu want/obstacle, hoặc không có cặp (nhân vật chính, đối trọng)

Dùng (từ gốc repo):
  python .agents/skills/video-pipeline/scripts/check_script_drama.py --project projects/<slug> [--strict] [--json]
Mã thoát: 0 = không lỗi, 1 = có lỗi. Công cụ kiểm cấu trúc, không đánh giá được kịch bản có HAY hay không:
phần đó do review độc lập (references/script-review-protocol.md) và người duyệt.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

GENRES = {"ghost_ritual", "feud_curse", "love_charm", "mystery", "other"}
PATTERNS = {"escalating_peaks", "slow_burn"}
LOOP_TYPES = {"clue", "object", "rule", "promise", "mystery", "red_herring", "line"}
BEATS = ["hook", "setup", "warning", "inciting", "first_disaster", "point_of_no_return", "debate", "plan", "midpoint",
         "escalation", "lowest", "climax", "reveal", "resolution", "aftermath"]
GREETING = re.compile(r"^\s*(xin chào|chào các bạn|chào mọi người|hôm nay (mình|tôi|chúng ta)|trong video (này|hôm nay)|hello)", re.I)
HOOK_MAX_WORDS = 14
STALL_LINES = 20
FIRST_PLANT_WITHIN = 6


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def words(t: str) -> int:
    return len(re.findall(r"\S+", t or ""))


class Gate:
    def __init__(self, script: dict, bible: dict | None, strict: bool):
        self.S, self.B, self.strict = script, bible or {}, strict
        self.errors: list[tuple[str, str]] = []
        self.warns: list[tuple[str, str]] = []
        self.scenes = script.get("scenes", [])
        self.order: dict[str, int] = {}
        self.scene_of: dict[str, int] = {}
        self.text: dict[str, str] = {}
        n = 0
        for si, s in enumerate(self.scenes):
            for ln in s.get("lines", []):
                self.order[ln["id"]] = n
                self.scene_of[ln["id"]] = si
                self.text[ln["id"]] = ln.get("text", "")
                n += 1
        self.total = n

    def err(self, code: str, msg: str):
        self.errors.append((code, msg))

    def warn(self, code: str, msg: str):
        self.warns.append((code, msg))

    def missing(self, code: str, msg: str):
        (self.err if self.strict else self.warn)(code, msg)

    # ------------------------------------------------------------------
    def run(self):
        d = self.S.get("drama")
        if not isinstance(d, dict):
            self.missing("DR1", "kịch bản chưa có khối `drama` (promise, genre, tension_pattern, rules, loops, motives)")
            self.scene_blocks(None)
            return
        self.header(d)
        events = self.loops(d)
        events |= self.rules(d)
        self.scene_blocks(d, events)
        self.motives(d)
        self.hook(d)

    # ---- DR1 ----------------------------------------------------------
    def header(self, d: dict):
        if not str(d.get("promise", "")).strip():
            self.missing("DR1", "drama.promise trống: câu hứa với người xem (hook phải mở đúng câu này, payoff phải đóng nó)")
        if d.get("genre") not in GENRES:
            self.missing("DR1", f"drama.genre '{d.get('genre')}' ∉ {sorted(GENRES)}")
        if d.get("tension_pattern") not in PATTERNS:
            self.missing("DR1", f"drama.tension_pattern '{d.get('tension_pattern')}' ∉ {sorted(PATTERNS)}")
        if not d.get("loops"):
            self.missing("DR1", "drama.loops rỗng: chưa gài vòng lặp (setup→payoff) nào")
        elif len(d["loops"]) < 3:
            self.warn("DR1", f"chỉ {len(d['loops'])} loop: kịch bản dài 10–30 phút nên có ≥3 để giữ chân")

    # ---- DR3, DR4, DR8 -------------------------------------------------
    def ref(self, code: str, where: str, lid) -> int | None:
        if lid not in self.order:
            self.err(code, f"{where}: '{lid}' không phải line id trong script")
            return None
        return self.order[lid]

    def loops(self, d: dict) -> set[int]:
        events: set[int] = set()
        opens = 0
        seen = set()
        for lp in d.get("loops", []):
            lid = lp.get("id", "?")
            where = f"loop {lid}"
            if lid in seen:
                self.err("DR3", f"{where}: id trùng")
            seen.add(lid)
            if lp.get("type") not in LOOP_TYPES:
                self.err("DR3", f"{where}: type '{lp.get('type')}' ∉ {sorted(LOOP_TYPES)}")
            if not str(lp.get("question", "")).strip():
                self.warn("DR3", f"{where}: thiếu `question` (người xem đang tự hỏi gì?)")
            pl = self.ref("DR3", where + ".plant", lp.get("plant"))
            tr = self.ref("DR3", where + ".trigger", lp["trigger"]) if lp.get("trigger") else None
            if pl is not None:
                events.add(pl)
            if tr is not None:
                events.add(tr)
            if lp.get("open"):
                opens += 1
                if lp.get("payoff"):
                    self.warn("DR4", f"{where}: đánh dấu open nhưng lại có payoff")
            pay = None
            if lp.get("payoff"):
                pay = self.ref("DR3", where + ".payoff", lp["payoff"])
                if pay is not None:
                    events.add(pay)
            elif not lp.get("open"):
                self.err("DR4", f"{where}: gài rồi không mở/đóng (không có payoff, không `open`): nợ nhân quả chưa trả")
            if pl is not None and tr is not None and tr <= pl:
                self.err("DR3", f"{where}: trigger ({lp['trigger']}) không đứng sau plant ({lp['plant']})")
            if tr is not None and pay is not None and pay < tr:
                self.err("DR3", f"{where}: payoff ({lp['payoff']}) đến TRƯỚC trigger ({lp['trigger']}): tiết lộ sớm")
            if pl is not None and pay is not None:
                if pay <= pl:
                    self.err("DR3", f"{where}: payoff ({lp['payoff']}) không đứng sau plant ({lp['plant']})")
                elif pay - pl < 3:
                    self.warn("DR3", f"{where}: plant và payoff cách {pay - pl} câu: chưa kịp thành bí ẩn")
            if lp.get("type") == "mystery":
                clues = lp.get("clues", [])
                if len(clues) < 2:
                    self.err("DR8", f"{where}: mystery cần ≥2 clues rải trước payoff (công bằng với người xem), có {len(clues)}")
                for c in clues:
                    ci = self.ref("DR8", where + ".clues", c)
                    if ci is None:
                        continue
                    events.add(ci)
                    if pay is not None and ci >= pay:
                        self.err("DR8", f"{where}: clue {c} đứng sau/đúng payoff {lp['payoff']}")
        if opens > 1:
            self.err("DR4", f"{opens} loop `open`: chỉ cho tối đa 1 (tease phần sau); còn lại phải đóng")
        return events

    # ---- DR5 ------------------------------------------------------------
    def rules(self, d: dict) -> set[int]:
        events: set[int] = set()
        for r in d.get("rules", []):
            rid = r.get("id", "?")
            where = f"rule {rid}"
            if not str(r.get("text", "")).strip():
                self.err("DR5", f"{where}: thiếu `text` (luật là gì)")
            if not str(r.get("cost", "")).strip():
                self.err("DR5", f"{where}: thiếu `cost` (vi phạm/ dùng luật thì trả giá gì): luật không giá thì không có kịch tính")
            pl = self.ref("DR5", where + ".plant", r.get("plant"))
            fu = self.ref("DR5", where + ".first_use", r["first_use"]) if r.get("first_use") else None
            if pl is not None:
                events.add(pl)
            if pl is not None and fu is not None:
                events.add(fu)
                if fu < pl:
                    self.err("DR5", f"{where}: dùng luật ({r['first_use']}) trước khi người xem được biết luật ({r['plant']})")
            vio = r.get("violations", [])
            if not vio:
                self.warn("DR5", f"{where}: không có `violations`: luật không ảnh hưởng gì tới cốt truyện")
            for v in vio:
                vi = self.ref("DR5", where + ".violations", v)
                if vi is None:
                    continue
                events.add(vi)
                if pl is not None and vi <= pl:
                    self.err("DR5", f"{where}: vi phạm {v} đứng trước/đúng chỗ luật được nêu {r['plant']}")
        return events

    # ---- DR2 ------------------------------------------------------------
    def hook(self, d: dict):
        if not self.scenes or not self.scenes[0].get("lines"):
            return
        first = self.scenes[0]["lines"][0]
        t = first.get("text", "")
        if GREETING.search(t):
            self.err("DR2", f"{first['id']}: câu đầu là chào hỏi/dẫn nhập ('{t[:40]}…'): vào thẳng hook (60% rời đi lúc dẫn nhập, nguồn blog, chưa kiểm)")
        if words(t) > HOOK_MAX_WORDS:
            self.warn("DR2", f"{first['id']}: câu hook {words(t)} từ > {HOOK_MAX_WORDS}: khó gói trong 1–3 s đọc")
        sd = self.scenes[0].get("drama") or {}
        if sd and sd.get("beat") != "hook":
            self.warn("DR2", f"cảnh đầu có beat '{sd.get('beat')}' ≠ hook")
        plants = [self.order.get(lp.get("plant"), 10**9) for lp in d.get("loops", [])]
        plants += [self.order.get(r.get("plant"), 10**9) for r in d.get("rules", [])]
        if plants and min(plants) >= FIRST_PLANT_WITHIN:
            self.err("DR2", f"vòng lặp đầu tiên chỉ được gài ở câu #{min(plants) + 1}: phải trong {FIRST_PLANT_WITHIN} câu đầu")
        elif not plants:
            self.missing("DR2", "chưa có vòng lặp nào để mở hook")

    # ---- DR6, DR7, DR9 --------------------------------------------------
    def scene_blocks(self, d: dict | None, events: set[int] | None = None):
        ids = [s["id"] for s in self.scenes]
        idx = {sid: i for i, sid in enumerate(ids)}
        tens: list[float | None] = []
        climax = []
        beats_at: dict[str, float] = {}
        cum = 0
        for si, s in enumerate(self.scenes):
            sd = s.get("drama")
            sid = s["id"]
            n = len(s.get("lines", []))
            if not isinstance(sd, dict):
                self.missing("DR1", f"{sid}: thiếu `drama` (beat, tension, turn, hook_out, causes)")
                tens.append(None)
                cum += n
                continue
            b = sd.get("beat")
            if b not in BEATS:
                self.err("DR1", f"{sid}: drama.beat '{b}' ∉ {BEATS}")
            else:
                beats_at.setdefault(b, (cum + n / 2) / max(self.total, 1))
                if b == "climax":
                    climax.append(si)
            t = sd.get("tension")
            if not isinstance(t, (int, float)) or not 0 <= t <= 10:
                self.err("DR6", f"{sid}: tension '{t}' phải là số 0–10")
                tens.append(None)
            else:
                tens.append(float(t))
            last = si == len(self.scenes) - 1
            if not last:
                if not str(sd.get("turn", "")).strip():
                    self.warn("DR7", f"{sid}: thiếu `turn` (cảnh này đổi điều gì? không đổi gì = cắt hoặc gộp)")
                if not str(sd.get("hook_out", "")).strip():
                    self.warn("DR7", f"{sid}: thiếu `hook_out` (câu hỏi/đe doạ kéo người xem sang cảnh sau)")
            if sd.get("turn_at"):
                ti = self.ref("DR7", f"{sid}.turn_at", sd["turn_at"])
                if ti is not None and events is not None:
                    events.add(ti)
            if si > 0:
                cs = sd.get("causes")
                if not cs:
                    self.warn("DR9", f"{sid}: thiếu `causes` (cảnh/loop nào gây ra cảnh này?)")
                else:
                    lpid = {lp.get("id") for lp in (d or {}).get("loops", [])} | {r.get("id") for r in (d or {}).get("rules", [])}
                    for c in cs:
                        if c in idx:
                            if idx[c] >= si:
                                self.warn("DR9", f"{sid}: causes '{c}' đứng sau/đúng cảnh này (nhân quả ngược)")
                        elif c not in lpid:
                            self.warn("DR9", f"{sid}: causes '{c}' không phải cảnh hay loop/rule")
            cum += n
        self.tension_shape(d, tens, climax, beats_at)
        if events is not None:
            self.stalls(events)

    def tension_shape(self, d, tens, climax, beats_at):
        vals = [t for t in tens if t is not None]
        if len(vals) < len(tens) or len(vals) < 3:
            return
        if len(climax) != 1:
            self.missing("DR6", f"cần đúng 1 cảnh beat `climax`, có {len(climax)}")
        else:
            ci = climax[0]
            if tens[ci] < max(tens):
                self.err("DR6", f"cảnh climax ({self.scenes[ci]['id']}) có tension {tens[ci]:g} < đỉnh {max(tens):g}: đỉnh phải là climax")
            if ci < len(tens) - 1 and max(tens[ci + 1:]) >= tens[ci]:
                self.warn("DR6", "sau climax vẫn có cảnh căng bằng/hơn: cần dịu xuống (resolution)")
        if tens[-1] >= max(tens) and len(set(tens)) > 1 and len(climax) == 1 and climax[0] != len(tens) - 1:
            self.warn("DR6", "cảnh cuối căng bằng đỉnh mà không phải climax")
        run = 1
        for a, b in zip(tens, tens[1:]):
            run = run + 1 if a == b else 1
            if run >= 4:
                self.warn("DR6", f"≥4 cảnh liền cùng tension {a:g}: nhịp phẳng, người xem ngừng chờ")
                break
        k = max(1, len(tens) // 3)
        head, tail = tens[:k], tens[-k:]
        pat = (d or {}).get("tension_pattern")
        if pat == "escalating_peaks" and max(tail) - max(head) < 2:
            self.err("DR6", f"escalating_peaks: đỉnh 1/3 cuối ({max(tail):g}) phải cao hơn đỉnh 1/3 đầu ({max(head):g}) ≥2")
        if pat == "slow_burn" and sum(tail) / k - sum(head) / k < 1.5:
            self.err("DR6", "slow_burn: trung bình 1/3 cuối phải cao hơn 1/3 đầu ≥1.5")
        mp = beats_at.get("midpoint")
        if mp is not None and not 0.35 <= mp <= 0.65:
            self.warn("DR6", f"midpoint ở {mp:.0%} thời lượng (theo số câu), nên 35–65%")

    def stalls(self, events: set[int]):
        ev = sorted(events)
        if not ev:
            return
        prev = -1
        for e in ev + [self.total]:
            if e - prev > STALL_LINES:
                a = self.line_at(prev + 1)
                b = self.line_at(min(e, self.total - 1))
                self.warn("DR7", f"{e - prev - 1} câu liền ({a} → {b}) không có biến cố (plant/payoff/clue/vi phạm luật/turn_at): người xem dễ rời đi")
            prev = e

    def line_at(self, i: int) -> str:
        for k, v in self.order.items():
            if v == i:
                return k
        return str(i)

    # ---- DR10 ------------------------------------------------------------
    def motives(self, d: dict):
        ms = d.get("motives", [])
        chars = {c.get("id") for c in self.B.get("characters", [])} if self.B else None
        roles = set()
        for m in ms:
            cid = m.get("char")
            if chars is not None and cid not in chars:
                self.err("DR10", f"motive: nhân vật '{cid}' ∉ bible.characters")
            for k in ("want", "obstacle"):
                if not str(m.get(k, "")).strip():
                    self.err("DR10", f"motive {cid}: thiếu `{k}`")
            roles.add(m.get("role"))
        if not ms:
            self.missing("DR10", "drama.motives rỗng: ai muốn gì, bị cản bởi gì (kịch tính = muốn + cản)")
        elif not ({"protagonist"} <= roles and ({"antagonist", "force"} & roles)):
            self.warn("DR10", "motives nên có role `protagonist` và `antagonist` (hoặc `force` cho thế lực/lời nguyền)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", required=True)
    ap.add_argument("--script")
    ap.add_argument("--strict", action="store_true", help="thiếu drama / scene.drama là lỗi")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    proj = Path(a.project)
    sp = Path(a.script) if a.script else proj / "script" / "script.json"
    if not sp.exists():
        print(f"LỖI: không có {sp}")
        return 1
    bp = proj / "script" / "bible.json"
    g = Gate(load(sp), load(bp) if bp.exists() else None, a.strict)
    g.run()
    if a.json:
        print(json.dumps({"errors": g.errors, "warnings": g.warns}, ensure_ascii=False, indent=1))
    else:
        d = g.S.get("drama") or {}
        print(f"kịch tính: {len(g.scenes)} cảnh, {len(d.get('loops', []))} loop, {len(d.get('rules', []))} rule")
        for c, m in g.warns:
            print(f"  ! {m} ({c})")
        for c, m in g.errors:
            print(f"  LỖI: {m} ({c})")
        print("OK" if not g.errors else f"FAIL: {len(g.errors)} lỗi")
    return 1 if g.errors else 0


if __name__ == "__main__":
    sys.exit(main())
