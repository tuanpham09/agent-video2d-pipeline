#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gate logic & liền mạch của KỊCH BẢN (chạy trước TTS, R1.5).

Đọc script/script.json (scene.setting / cast / staging), script/bible.json (locations kind+connects, props states,
characters) và, nếu có, script/shotlist.json. Mô phỏng "thế giới" qua các cảnh như script supervisor ghi continuity:
nhân vật đang ở đâu, ai đang cầm đạo cụ gì, đạo cụ đang ở state nào, giờ trong truyện có đi xuôi không.
Tham khảo: scene heading INT/EXT + địa điểm + thời gian, CONTINUOUS/LATER (Final Draft / Fountain), continuity sheet, theo dõi
trạng thái vật (SCORE, arXiv 2503.23512). Chi tiết: references/script-continuity-guide.md.

Mã lỗi:
  SL1  scene thiếu / sai setting (location ∉ bible, int_ext ≠ kind của location, time/frame/link lạ)   [thiếu: lỗi khi --strict, else cảnh báo]
  SL2  người nói (không phải narrator) không có trong cast của cảnh
  SL3  link không hợp lệ: continuous phải cùng chỗ hoặc kề nhau (bible.connects); later phải cùng chỗ + thời gian trôi; travel cần link_note
  SL4  nhân vật đổi địa điểm giữa hai cảnh mà không khai `from` (đi từ đâu); from ≠ chỗ cũ mà thiếu link_note
  SL5  staging sai: enter/exit không nối kề, hành động sau khi đã exit, who không có trong cast, after/line không có hoặc ngược thứ tự
  SL6  đạo cụ: cầm/đưa/đặt sai (không giữ mà đưa, người khác đang cầm, state ∉ bible.props.states), đổi người cầm giữa cảnh không có give/take
  SL7  mốc truyện (story_time) đi lùi trong cảnh present, hoặc giờ không khớp time (cảnh báo)
  SL8  cast ∉ bible.characters
  SL9  (cảnh báo) shot ≥ 2 người mà có người không có hành động nào trong staging; nhân vật "biến mất" giữa hai cảnh liền nhau
  SL10 (cảnh báo, heuristic) lời có vẻ của nhân vật khác (tao/mày dưới người kể), tự xưng ngôi ba, tên riêng gõ lệch 1 ký tự
  SL11 shot.location ≠ địa điểm hiệu lực của line trong scene (cutaway/insert chỉ cảnh báo)

Dùng (từ gốc repo):
  python .agents/skills/video-pipeline/scripts/check_script_logic.py --project projects/<slug> [--scenes S01,S02] [--strict] [--json]
Mã thoát: 0 = không lỗi, 1 = có lỗi. Không thay cho việc người đọc kịch bản một lượt.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TIMES = {"day", "night", "dawn", "dusk"}
FRAMES = {"present", "flashback", "dream", "phone", "cutaway"}
LINKS = {"continuous", "later", "cut", "travel"}
VERBS = {"enter", "exit", "move", "sit", "stand", "take", "give", "put", "set_state", "look", "react", "gesture"}
PRESENCE = {"physical", "remote", "voice"}
TIME_HOURS = {  # giờ (0–24) hợp với từng mốc, để cảnh báo lệch
    "night": [(18.5, 24), (0, 5.5)], "dawn": [(4.5, 7.5)], "day": [(6, 18)], "dusk": [(16.5, 19.5)],
}
ST_RE = re.compile(r"^[A-Za-z]*\s*(\d+)\s+(\d{1,2}):(\d{2})$")  # "N2 03:40" → ngày 2, 03:40
MOVE_TO_TIME = None


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def parse_st(s) -> float | None:
    m = ST_RE.match(str(s or "").strip())
    return int(m.group(1)) * 1440 + int(m.group(2)) * 60 + int(m.group(3)) if m else None


def hour_ok(time: str, st: float) -> bool:
    h = (st % 1440) / 60
    return any(a <= h <= b for a, b in TIME_HOURS.get(time, [(0, 24)]))


def typo_dup(w: str, k: str) -> bool:
    """w = k với một ký tự bị gõ lặp ('Cửuu' ← 'Cửu'). Chỉ bắt kiểu này để khỏi báo nhầm từ thường ('Thân' vs 'Thần')."""
    return len(w) == len(k) + 1 and any(k[:i] + k[i] + k[i:] == w for i in range(len(k)))


class Gate:
    def __init__(self, script: dict, bible: dict, shotlist: dict | None, only: set[str] | None, strict: bool):
        self.script, self.bible, self.shotlist, self.only, self.strict = script, bible, shotlist, only, strict
        self.errors: list[str] = []
        self.warns: list[str] = []
        self.locs = {l["id"]: l for l in bible.get("locations", [])}
        self.props = {p["id"]: p for p in bible.get("props", [])}
        self.bchars = {c["id"] for c in bible.get("characters", [])}
        self.narr = {c["id"] for c in script.get("characters", []) if c.get("role") == "narrator"}
        self.adj: dict[str, set[str]] = {k: set() for k in self.locs}
        for l in bible.get("locations", []):
            for c in l.get("connects", []) or []:
                to = c.get("to") if isinstance(c, dict) else c
                if to in self.locs:
                    self.adj[l["id"]].add(to)
                    if not (isinstance(c, dict) and c.get("oneway")):
                        self.adj[to].add(l["id"])
        # thế giới
        self.pos: dict[str, str] = {}          # nhân vật → địa điểm cuối cùng thấy
        self.hold: dict[str, str | None] = {}  # đạo cụ → người cầm
        self.pstate: dict[str, str] = {}       # đạo cụ → state
        self.last_present: dict | None = None  # {"scene","loc","st","cast":set}
        self.eff_loc: dict[str, str] = {}      # line_id → địa điểm hiệu lực
        self.scene_of_line: dict[str, str] = {}

    def err(self, code: str, sid: str, msg: str) -> None:
        self.errors.append(f"{sid}: {msg} ({code})")

    def warn(self, code: str, sid: str, msg: str) -> None:
        self.warns.append(f"{sid}: {msg} ({code})")

    def connected(self, a: str, b: str) -> bool:
        return a == b or b in self.adj.get(a, set())

    # ---------- một cảnh ----------
    def scene(self, sc: dict) -> None:
        sid = sc["id"]
        lines = sc.get("lines", [])
        lids = [l["id"] for l in lines]
        for l in lines:
            self.scene_of_line[l["id"]] = sid
        st = sc.get("setting")
        if not st:
            (self.err if self.strict else self.warn)("SL1", sid, "chưa có `setting` (location, int_ext, time, frame, link)")
            return
        loc, ie, tm = st.get("location"), st.get("int_ext"), st.get("time")
        frame, link = st.get("frame", "present"), st.get("link", "cut")
        if loc not in self.locs:
            self.err("SL1", sid, f"setting.location '{loc}' không có trong bible.locations")
            return
        kind = self.locs[loc].get("kind")
        if ie not in ("int", "ext"):
            self.err("SL1", sid, "setting.int_ext phải là 'int' hoặc 'ext'")
        elif kind and kind != ie:
            self.err("SL1", sid, f"setting.int_ext='{ie}' nhưng bible.locations.{loc}.kind='{kind}'")
        elif not kind:
            self.warn("SL1", sid, f"bible.locations.{loc} chưa khai `kind` (int|ext)")
        if tm not in TIMES:
            self.err("SL1", sid, f"setting.time '{tm}' ∉ {sorted(TIMES)}")
        if frame not in FRAMES:
            self.err("SL1", sid, f"setting.frame '{frame}' ∉ {sorted(FRAMES)}")
        if link not in LINKS:
            self.err("SL1", sid, f"setting.link '{link}' ∉ {sorted(LINKS)}")
        stm = parse_st(st.get("story_time"))
        if st.get("story_time") and stm is None:
            self.err("SL7", sid, f"story_time '{st.get('story_time')}' sai dạng; dùng 'N<ngày> HH:MM', vd 'N1 15:00'")
        if stm is not None and tm in TIMES and not hour_ok(tm, stm):
            self.warn("SL7", sid, f"story_time {st['story_time']} không hợp time='{tm}'")

        cast = {c["id"]: c for c in sc.get("cast", []) or []}
        for cid in cast:
            if cid not in self.bchars:
                self.err("SL8", sid, f"cast '{cid}' không có trong bible.characters")
        for l in lines:  # SL2
            if l["speaker"] not in self.narr and l["speaker"] not in cast:
                self.err("SL2", sid, f"line {l['id']}: '{l['speaker']}' nói nhưng không có trong cast (khai presence 'voice'/'remote' nếu chỉ nghe/qua điện thoại)")
        self.heuristics(sid, lines)

        # staging + moves → vị trí hiệu lực của từng line
        staging = sc.get("staging", []) or []
        moves = sorted((st.get("moves") or []), key=lambda m: lids.index(m["after"]) if m.get("after") in lids else -1)
        cur = loc
        order = {lid: i for i, lid in enumerate(lids)}
        mv = {m.get("after"): m for m in moves}
        for m in moves:
            if m.get("after") not in order:
                self.err("SL5", sid, f"setting.moves.after '{m.get('after')}' không phải line của cảnh")
            elif m.get("to") not in self.locs:
                self.err("SL5", sid, f"setting.moves.to '{m.get('to')}' không có trong bible.locations")
        for lid in lids:
            self.eff_loc[lid] = cur
            m = mv.get(lid)
            if m and m.get("to") in self.locs:
                if not self.connected(cur, m["to"]):
                    self.err("SL3", sid, f"moves: {cur} → {m['to']} không nối kề (bible.connects)")
                cur = m["to"]
        end_loc = cur

        is_present = frame == "present"
        saved = (dict(self.hold), dict(self.pstate), dict(self.pos))  # cảnh ngoài hiện tại: kiểm staging nhưng không đổi thế giới

        # SL3: link so với cảnh present liền trước
        lp = self.last_present
        if link in ("continuous", "later") and not lp:
            self.err("SL3", sid, f"link '{link}' nhưng không có cảnh present liền trước")
        if lp and is_present:
            if link == "continuous" and not self.connected(lp["end_loc"], loc):
                self.err("SL3", sid, f"link continuous: {lp['end_loc']} → {loc} không cùng chỗ cũng không nối kề; dùng cut/travel hoặc thêm connects vào bible")
            if link == "later":
                if loc != lp["end_loc"]:
                    self.err("SL3", sid, f"link later phải cùng địa điểm với cảnh trước ({lp['end_loc']}), đây là {loc}")
                if stm is not None and lp["st"] is not None and stm <= lp["st"]:
                    self.err("SL3", sid, "link later nhưng story_time không lớn hơn cảnh trước")
            if link == "travel" and not st.get("link_note"):
                self.err("SL3", sid, "link travel cần `link_note` (đi bằng gì, mất bao lâu)")
            if link == "travel" and loc == lp["end_loc"]:
                self.warn("SL3", sid, "link travel nhưng cùng địa điểm với cảnh trước")
            if stm is not None and lp["st"] is not None and stm < lp["st"]:
                self.err("SL7", sid, f"story_time {st['story_time']} nhỏ hơn cảnh present trước ({lp['story_time']}); cảnh hồi tưởng phải khai frame: flashback")
        elif stm is None:
            pass

        # SL4: đổi địa điểm giữa hai cảnh
        phys = {cid: c for cid, c in cast.items() if c.get("presence", "physical") == "physical"}
        for cid, c in (phys.items() if is_present else []):
            if c.get("presence", "physical") not in PRESENCE:
                self.err("SL1", sid, f"cast {cid}: presence lạ")
            late = c.get("start") is False
            prev = self.pos.get(cid)
            if late:
                continue  # vào giữa cảnh: kiểm ở staging.enter
            if prev and prev != loc:
                frm = c.get("from")
                if not frm:
                    self.err("SL4", sid, f"{cid} từ {prev} (cảnh trước) sang {loc} nhưng chưa khai cast.from — đi từ đâu tới đâu?")
                else:
                    if frm not in self.locs:
                        self.err("SL4", sid, f"{cid}.from '{frm}' không có trong bible.locations")
                    elif link == "continuous" and frm != prev:
                        self.err("SL4", sid, f"{cid}: link continuous nên from phải là {prev} (chỗ cũ), đang là {frm}")
                    elif frm != prev and not st.get("link_note"):
                        self.warn("SL4", sid, f"{cid}.from={frm} khác chỗ cũ {prev}; cần link_note giải thích khoảng giữa")
                    if frm in self.locs and not self.connected(frm, loc):
                        if link == "continuous":
                            self.err("SL4", sid, f"{cid}: {frm} → {loc} không nối kề")
                        elif link != "travel" and not st.get("link_note"):
                            self.warn("SL4", sid, f"{cid}: {frm} → {loc} không kề nhau (bible.connects); ghi link_note (đi qua đâu) hoặc dùng link travel")
        if lp and is_present and link in ("continuous", "later") and loc == lp["end_loc"]:
            for cid in lp["cast"]:
                if cid not in phys and self.pos.get(cid) == loc:
                    self.warn("SL9", sid, f"{cid} có ở cảnh trước cùng chỗ nhưng biến mất ở cảnh này mà không có exit")

        # đạo cụ giữ qua cảnh
        for cid, c in phys.items():
            for p in c.get("holding", []) or []:
                if p not in self.props:
                    self.err("SL6", sid, f"{cid}.holding '{p}' không có trong bible.props")
                    continue
                h = self.hold.get(p)
                if is_present and h and h != cid and not any(s.get("do") in ("give", "take") and s.get("prop") == p for s in staging):
                    self.err("SL6", sid, f"{p} đang do {h} cầm (cảnh trước) nhưng cảnh này {cid} cầm mà không có give/take")
                self.hold[p] = cid

        # staging
        present_now = {cid for cid, c in phys.items() if c.get("start") is not False}
        gone: set[str] = set()
        acted: set[str] = set()
        last_i = -1
        loc_now = loc
        for s in staging:
            who, do = s.get("who"), s.get("do")
            aft = s.get("after")
            if do not in VERBS:
                self.err("SL5", sid, f"staging do '{do}' ∉ {sorted(VERBS)}")
                continue
            if aft is not None:
                if aft not in order:
                    self.err("SL5", sid, f"staging.after '{aft}' không phải line của cảnh")
                elif order[aft] < last_i:
                    self.err("SL5", sid, f"staging.after '{aft}' đứng trước mục staging trước đó; sắp theo thứ tự line")
                else:
                    last_i = order[aft]
                    loc_now = self.eff_loc.get(aft, loc_now)
            if who not in phys:
                self.err("SL5", sid, f"staging {do}: who '{who}' không có trong cast (physical)")
                continue
            acted.add(who)
            if who in gone:
                self.err("SL5", sid, f"{who} đã exit nhưng còn {do} ở '{aft}'")
                continue
            if do == "enter":
                if who in present_now:
                    self.err("SL5", sid, f"{who} đã có mặt từ đầu cảnh mà còn enter (đặt cast.start=false nếu vào giữa cảnh)")
                frm = s.get("from")
                if frm not in self.locs or not self.connected(frm, loc_now) or frm == loc_now:
                    self.err("SL5", sid, f"enter {who}: from '{frm}' phải là địa điểm KỀ {loc_now} (bible.connects)")
                if not s.get("via"):
                    self.warn("SL5", sid, f"enter {who}: nên khai `via` (cửa/lối nào)")
                present_now.add(who)
            elif do == "exit":
                to = s.get("to")
                if to not in self.locs or not self.connected(loc_now, to) or to == loc_now:
                    self.err("SL5", sid, f"exit {who}: to '{to}' phải là địa điểm KỀ {loc_now} (bible.connects)")
                else:
                    self.pos[who] = to
                present_now.discard(who)
                gone.add(who)
            elif do in ("take", "give", "put", "set_state"):
                p = s.get("prop")
                if p not in self.props:
                    self.err("SL6", sid, f"staging {do}: prop '{p}' không có trong bible.props")
                    continue
                if do == "take":
                    h = self.hold.get(p)
                    if h and h != who:
                        self.err("SL6", sid, f"{who} take {p} nhưng {h} đang cầm (phải give)")
                    self.hold[p] = who
                elif do == "give":
                    to = s.get("to")
                    if self.hold.get(p) != who:
                        self.err("SL6", sid, f"{who} give {p} nhưng {who} không cầm nó (holding/take trước)")
                    if to not in phys:
                        self.err("SL6", sid, f"give {p}: nhận '{to}' không có trong cast")
                    else:
                        acted.add(to)
                        self.hold[p] = to
                elif do == "put":
                    if self.hold.get(p) != who:
                        self.err("SL6", sid, f"{who} put {p} nhưng không cầm nó")
                    self.hold[p] = None
                else:  # set_state
                    state = s.get("state")
                    if state not in (self.props[p].get("states") or []):
                        self.err("SL6", sid, f"set_state {p}: '{state}' ∉ bible states {self.props[p].get('states')}")
                    self.pstate[p] = state
        late_missing = [cid for cid, c in phys.items() if c.get("start") is False and cid not in {s.get('who') for s in staging if s.get('do') == 'enter'}]
        for cid in late_missing:
            self.err("SL5", sid, f"{cid} có cast.start=false nhưng không có staging enter")
        if len(phys) >= 2:
            for cid in phys:
                if cid not in acted and not phys[cid].get("role_note"):
                    self.warn("SL9", sid, f"{cid} không có hành động nào trong staging dù cảnh có ≥ 2 người (R11.1); thêm hành động hoặc role_note")

        if not is_present:
            self.hold, self.pstate, self.pos = saved
            return
        # cập nhật thế giới
        for cid in phys:
            if cid not in gone:
                self.pos[cid] = end_loc
        self.last_present = {"scene": sid, "end_loc": end_loc, "st": stm, "story_time": st.get("story_time"), "cast": set(phys)}

    # ---------- heuristics ----------
    def heuristics(self, sid: str, lines: list[dict]) -> None:
        known: set[str] = set()
        for c in self.script.get("characters", []):
            for t in re.findall(r"[^\W\d_]{3,}", re.sub(r"\(.*?\)", "", c.get("name", ""))):
                known.add(t)
        for l in lines:
            t, sp = l["text"], l["speaker"]
            if sp in self.narr and re.search(r"\b(tao|mày|mầy)\b", t, re.I) and not re.search(r"[\"“”]", t):
                self.warn("SL10", sid, f"{l['id']}: người kể dùng 'tao/mày' — có phải lời nhân vật khác? (đổi speaker hoặc dẫn lại bằng ngôi thứ nhất)")
            for c in self.script.get("characters", []):
                nm = re.sub(r"\(.*?\)", "", c.get("name", "")).strip()
                if sp == c["id"] and nm and re.match(rf"^\s*{re.escape(nm)}\s+(nói|bảo|hỏi|dặn)\b", t, re.I):
                    self.warn("SL10", sid, f"{l['id']}: '{sp}' tự gọi mình bằng tên ở ngôi ba ('{t[:30]}…'): lời của người kể, hay bỏ 'X nói'")
            for w in re.findall(r"[^\W\d_]{3,}", t):
                if w[0].isupper() and w not in known:
                    for k in known:
                        if typo_dup(w, k):
                            self.warn("SL10", sid, f"{l['id']}: '{w}' gần giống tên '{k}' (gõ nhầm?)")
                            break

    # ---------- shotlist ----------
    def check_shotlist(self) -> None:
        if not self.shotlist:
            return
        for sh in self.shotlist.get("shots", []):
            lids = sh.get("line_ids") or []
            if not lids or lids[0] not in self.eff_loc:
                continue
            want = self.eff_loc[lids[0]]
            sc = self.scene_of_line.get(lids[0], "?")
            if sh.get("location") != want:
                msg = f"shot {sh['id']}: location '{sh.get('location')}' ≠ địa điểm của kịch bản cho {lids[0]} ('{want}')"
                (self.warn if sh.get("kind") in ("cutaway", "insert") else self.err)("SL11", sc, msg)

    def run(self) -> None:
        for sc in self.script["scenes"]:
            if self.only and sc["id"] not in self.only:
                for l in sc.get("lines", []):
                    self.scene_of_line[l["id"]] = sc["id"]
                continue
            self.scene(sc)
        self.check_shotlist()
        miss = [s["id"] for s in self.script["scenes"] if not s.get("setting") and (not self.only or s["id"] in self.only)]
        if miss and not self.strict:
            self.warns.append(f"{len(miss)} cảnh chưa có setting ({miss[0]}…{miss[-1]}): chạy --strict trước khi chốt kịch bản/TTS")


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate logic & liền mạch của kịch bản.")
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--scenes", help="chỉ kiểm các cảnh này (S01,S02); thế giới vẫn tính từ các cảnh trước nếu liệt kê đủ")
    ap.add_argument("--strict", action="store_true", help="cảnh thiếu setting là LỖI (dùng khi chốt kịch bản)")
    ap.add_argument("--shotlist", type=Path)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    proj = a.project
    script, bible = load(proj / "script" / "script.json"), load(proj / "script" / "bible.json")
    sl = a.shotlist or proj / "script" / "shotlist.json"
    g = Gate(script, bible, load(sl) if sl.is_file() else None, set(a.scenes.split(",")) if a.scenes else None, a.strict)
    g.run()
    if a.json:
        print(json.dumps({"status": "ok" if not g.errors else "error", "errors": g.errors, "warnings": g.warns}, ensure_ascii=False, indent=2))
    else:
        n = len(script["scenes"])
        done = sum(1 for s in script["scenes"] if s.get("setting"))
        print(f"kịch bản : {n} cảnh, {done} cảnh đã có setting")
        for w in g.warns:
            print(f"  ! {w}")
        for e in g.errors:
            print(f"  LỖI: {e}")
        print("OK" if not g.errors else f"FAIL: {len(g.errors)} lỗi")
    return 0 if not g.errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
