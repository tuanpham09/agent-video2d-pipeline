#!/usr/bin/env python3
"""build_video.py — MỘT generator dựng video từ dữ liệu (RULES R1.6): manifest.json + bible.json + shotlist.json
+ library đã khoá → dự án HyperFrames (index.html + compositions/<shot>.html + assets/).

Không viết tay HTML/SVG cho từng shot. Mọi mốc thời gian lấy từ manifest (R1.2/R9.4) + `span` của shot.
Màu: không có hex trong file này (R2.5); tông nền lấy từ token palette của project.

Dùng:
  python .agents/skills/video-pipeline/scripts/build_video.py --project projects/<slug> \\
      [--out projects/<slug>/video_demo] [--until SH010 | --shots SH001,SH002] [--scenes S01]
Đầu ra là file sinh tự động (R1.3): sửa shotlist/bible/library rồi chạy lại, không sửa tay.

Quy ước dựng (đã khớp library/README.md):
  • Mỗi shot = một sub-composition `compositions/<id>.html` (host, root, timeline cùng id).
  • Sân khấu = <svg viewBox="0 0 1920 1080">; camera = tween thuộc tính viewBox (giữ tỉ lệ 16:9).
  • Bối cảnh / đạo cụ / rig đều nhúng là <svg> lồng nhau; rig đặt theo `stand` {x,y,s} (chân ở (260,580)).
  • Trạng thái đổi bằng data-* (rig: emotion|mouth|pose|stance|gaze|blink|khan; đạo cụ: data-state; bối cảnh: data-light).
  • Sống động tất định: thở, chớp mắt (seed theo shot+nhân vật), ngọn nến, khẩu hình theo số âm tiết.
Shotlist mở rộng cho generator (check_shots bỏ qua): characters[].at/stance/pose/gaze/scale, props[].at/dx/dy/scale/key,
  focus ("<char>" | "prop:<id>" | "slot:<tên>"), beats[].set = {"<char>": {emotion|pose|gaze|stance: v}, "light": v, "prop:<key>": state}.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
import shutil
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(HERE))
import library as L
from timing_lib import beat_time, sentence_ends  # noqa: E402
from behaviors import expand_shot  # noqa: E402

W, H = 1920, 1080
ZOOM = {"wide": 1.0, "medium": 1.6, "close": 2.4, "macro": 3.2, "ots": 1.8}
GSAP_SRC = "https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"
MOUTH_PATTERN = ["half", "open", "half", "round", "open", "half"]


def jload(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8-sig"))


def esc_attr(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;")


# ---- xử lý SVG nhúng -------------------------------------------------------

def prefix_ids(svg: str, pref: str) -> str:
    ids = set(re.findall(r'\bid="([^"]+)"', svg))
    for i in sorted(ids, key=len, reverse=True):
        svg = re.sub(rf'\bid="{re.escape(i)}"', f'id="{pref}{i}"', svg)
        svg = svg.replace(f"url(#{i})", f"url(#{pref}{i})")
        svg = re.sub(rf'href="#{re.escape(i)}"', f'href="#{pref}{i}"', svg)
    return svg


def strip_prolog(svg: str) -> str:
    return re.sub(r"<\?xml[^>]*\?>\s*", "", svg).strip()


def place_svg(svg: str, x: float, y: float, w: float, h: float) -> str:
    return svg.replace("<svg ", f'<svg x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" ', 1)


def set_attr_on_tag(tag: str, name: str, value: str) -> str:
    if re.search(rf'\b{name}="[^"]*"', tag):
        return re.sub(rf'\b{name}="[^"]*"', f'{name}="{value}"', tag, count=1)
    return tag[:-1] + f' {name}="{value}">'


def tag_with_attr(svg: str, attr: str, new_id: str, value: str | None = None) -> tuple[str, str]:
    """Gắn id vào phần tử đầu tiên có thuộc tính `attr`; (tuỳ chọn) đổi giá trị. Trả (svg, id)."""
    m = re.search(rf"<[a-zA-Z][^<>]*\b{attr}=\"[^\"]*\"[^<>]*>", svg)
    if not m:
        raise ValueError(f"không có phần tử nào mang {attr}")
    tag = m.group(0)
    new = set_attr_on_tag(tag, "id", new_id)
    if value is not None:
        new = set_attr_on_tag(new, attr, value)
    return svg[: m.start()] + new + svg[m.end():], new_id


# ---- hình học ---------------------------------------------------------------

class Stage:
    """Một shot: đặt bối cảnh, đạo cụ, nhân vật; ghi lại toạ độ để dựng camera."""

    def __init__(self, shot: dict, ctx: "Ctx"):
        self.shot, self.ctx, self.sid = shot, ctx, shot["id"]
        self.parts: list[tuple[float, int, str]] = []  # (y, thứ tự, svg)
        self.chars: dict[str, dict] = {}
        self.props: dict[str, dict] = {}
        self.prop_ids: dict[str, str] = {}
        self.light_id = ""
        self.loc = ctx.loc_entry(shot["location"])
        self.n = 0

    def uid(self, kind: str) -> str:
        self.n += 1
        return f"{self.sid}-{kind}{self.n}"

    def scene(self) -> str:
        lib_id = self.ctx.bible_loc[self.shot["location"]]["lib"]
        svg = strip_prolog((self.ctx.proj / "assets" / "bg" / f"{lib_id}.svg").read_text(encoding="utf-8"))
        svg = prefix_ids(svg, f"{self.sid}-bg-")
        svg, self.light_id = tag_with_attr(svg, "data-light", f"{self.sid}-light", self.shot["light"])
        return place_svg(svg, 0, 0, W, H)

    def resolve(self, spec: dict) -> tuple[float, float]:
        at = spec["at"]
        dx, dy = spec.get("dx", 0), spec.get("dy", 0)
        if at.startswith("stand:"):
            s = self.loc["stand"][at.split(":")[1]]
            return s["x"] + dx, s["y"] + dy
        if "." in at:
            parent, slot = at.split(".")
            p = self.props[parent]
            sx, sy = p["slots"][slot]["x"], p["slots"][slot]["y"]
            return p["x0"] + sx * p["k"] + dx, p["y0"] + sy * p["k"] + dy
        s = self.loc["slots"][at]
        return s["x"] + dx, s["y"] + dy

    def add_prop(self, spec: dict) -> None:
        bp = self.ctx.bible_prop[spec["id"]]
        e = self.ctx.lib_entry(bp["lib"])
        key = spec.get("key", spec["id"])
        x, y = self.resolve(spec)
        k = spec.get("scale", e.get("scene_s", 1.0))
        w, h = e["size"]
        pid = self.uid("p")
        svg = strip_prolog((self.ctx.proj / "assets" / "props" / f"{bp['lib']}.svg").read_text(encoding="utf-8"))
        svg = prefix_ids(svg, f"{pid}-")
        svg, tid = tag_with_attr(svg, "data-state", pid, spec["state"])
        self.parts.append((y, 0, place_svg(svg, x - w * k / 2, y - h * k, w * k, h * k)))
        self.props[key] = {"x": x, "y": y, "k": k, "x0": x - w * k / 2, "y0": y - h * k, "w": w, "h": h, "slots": e.get("slots", {})}
        self.prop_ids[key] = tid

    def add_char(self, spec: dict) -> None:
        cid = spec["id"]
        st = self.loc["stand"][spec["at"]]
        s = st["s"] * spec.get("scale", 1.0)
        svg = strip_prolog((self.ctx.proj / "assets" / "rig" / f"{cid}.svg").read_text(encoding="utf-8"))
        svg = prefix_ids(svg, f"{self.sid}-{cid}-")
        m = re.search(rf'<g[^>]*class="rig rig-{re.escape(cid)}"[^>]*>', svg)
        if not m:
            raise ValueError(f"rig {cid}: không thấy <g class=\"rig rig-{cid}\">")
        tag = set_attr_on_tag(m.group(0), "id", f"{self.sid}-{cid}")
        if spec.get("view") == "auto":
            raise ValueError(f"{self.sid}: characters[].view=auto chưa hỗ trợ — dùng beat.set {{view: auto}} (cần vị trí theo thời gian)")
        for a in ("emotion", "pose", "stance", "gaze", "view"):
            if spec.get(a):
                tag = set_attr_on_tag(tag, f"data-{a}", spec[a])
        svg = svg[: m.start()] + tag + svg[m.end():]
        self.parts.append((st["y"], 1, place_svg(svg, st["x"] - 260 * s, st["y"] - 580 * s, 520 * s, 600 * s)))
        self.chars[cid] = {"x": st["x"], "y": st["y"], "s": s, "mouth": bool(spec.get("mouth")), "id": f"{self.sid}-{cid}"}

    def hand_pos(self, cid: str, side: str) -> tuple[float, float]:
        """Vị trí tay nghỉ (l|r) của nhân vật trong toạ độ cảnh. Đọc pivot vai từ rig.json; tay nghỉ ở y=462 trong viewBox rig."""
        c = self.chars[cid]
        piv = jload(self.ctx.proj / "assets" / "rig" / f"{cid}.rig.json")["pivots"][f"arm-{side}"]
        vx = float(piv.split("px")[0])
        s = c["s"]
        return c["x"] - 260 * s + vx * s, c["y"] - 580 * s + 462 * s

    def hand_over_js(self, b: dict, t: float) -> list[str]:
        """Đạo cụ chuyển tay (R11.5): nhấc từ vị trí hiện tại lên tay người cho, rồi chuyển sang tay người nhận. Cần physical=true (SFX, R6.1)."""
        ho = b["hand_over"]
        key, g, r = ho.get("prop"), ho.get("from"), ho.get("to")
        if not b.get("physical"):
            raise ValueError(f"{self.sid}: hand_over phải có physical=true (R6.1: cần SFX)")
        if key not in self.props:
            raise ValueError(f"{self.sid}: hand_over prop '{key}' không có trong shot")
        if g not in self.chars or r not in self.chars or g == r:
            raise ValueError(f"{self.sid}: hand_over cần from/to là hai nhân vật khác nhau trong shot")
        side_g = "l" if self.chars[r]["x"] > self.chars[g]["x"] else "r"  # tay phía người nhận
        side_r = "r" if side_g == "l" else "l"
        p, pid = self.props[key], self.prop_ids[key]
        half_w, half_h = p["w"] * p["k"] / 2, p["h"] * p["k"] / 2

        def top_left(xy):  # gốc của đạo cụ là góc trên-trái; đặt tâm đạo cụ vào tay
            return xy[0] - half_w, xy[1] - half_h

        d = float(ho.get("dur", 0.9))
        d1 = d * 0.4
        gx, gy = top_left(self.hand_pos(g, side_g))
        rx, ry = top_left(self.hand_pos(r, side_r))
        p["x0"], p["y0"] = rx, ry
        p["x"], p["y"] = rx + half_w, ry + half_h
        return [
            f'tl.to("#{pid}", {{attr: {{x: {gx:.1f}, y: {gy:.1f}}}, duration: {d1:.2f}, ease: "power1.inOut"}}, {t:.2f});',
            f'tl.to("#{pid}", {{attr: {{x: {rx:.1f}, y: {ry:.1f}}}, duration: {d - d1:.2f}, ease: "power1.inOut"}}, {t + d1:.2f});',
        ]

    def focus_point(self) -> tuple[float, float]:
        f, size = self.shot.get("focus"), self.shot["size"]
        if f in self.chars:
            c = self.chars[f]
            up = 430 if size in ("close", "macro") else 320
            return c["x"], c["y"] - up * c["s"]
        if f and f.startswith("prop:"):
            p = self.props[f.split(":")[1]]
            return p["x"], p["y"] - p["h"] * p["k"] / 2
        if f and f.startswith("slot:"):
            s = self.loc["slots"][f.split(":")[1]]
            return s["x"], s["y"]
        return W / 2, H / 2

    def camera(self) -> tuple[str, str]:
        size, cam = self.shot["size"], self.shot.get("camera", "static")
        z = ZOOM[size]
        fx, fy = self.focus_point()
        if size == "wide":  # toàn cảnh: nghiêng nhẹ về tiêu điểm, không dịch hết
            fx, fy = W / 2 + (fx - W / 2) * 0.35, H / 2 + (fy - H / 2) * 0.2
        z0, z1, shift = z, z, 0.0
        if cam == "push_in":
            z1 = z * 1.12
        elif cam == "pull_out":
            z0, z1 = z * 1.12, z
        elif cam in ("pan_l", "pan_r"):
            shift = 70 if cam == "pan_r" else -70

        def vb(zz: float, dx: float) -> str:
            w, h = W / zz, H / zz
            x = min(max(fx + dx - w / 2, 0), W - w)
            y = min(max(fy - h / 2, 0), H - h)
            return f"{x:.1f} {y:.1f} {w:.1f} {h:.1f}"
        return vb(z0, -shift), vb(z1, shift)

    def svg(self) -> str:
        self.parts.sort(key=lambda p: (p[0], p[1]))
        v0, _ = self.camera()
        body = "".join(p[2] for p in self.parts)
        return (f'<svg id="{self.sid}-stage" xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
                f'viewBox="{v0}" data-layout-allow-overflow>{self.scene_svg}{body}</svg>')


class Ctx:
    def __init__(self, proj: Path):
        self.proj = proj
        self.manifest = jload(proj / "audio" / "manifest.json")
        self.bible = jload(proj / "script" / "bible.json")
        self.shotlist = jload(proj / "script" / "shotlist.json")
        self.idx = {e["id"]: e for e in L.load_index()["items"]}
        self.lock = jload(proj / "assets" / "LIBRARY.lock.json") if (proj / "assets" / "LIBRARY.lock.json").exists() else {"items": {}}
        self.bible_loc = {l["id"]: l for l in self.bible["locations"]}
        self.bible_prop = {p["id"]: p for p in self.bible["props"]}
        self.chars = {c["id"]: c for c in self.bible["characters"]}
        self.lines = {ln["id"]: ln for sc in self.manifest["scenes"] for ln in sc["lines"]}
        self.warn: list[str] = []

    def lib_entry(self, lib_id: str) -> dict:
        e = self.idx[lib_id]
        locked = self.lock.get("items", {}).get(lib_id, {}).get("version")
        if locked is not None and locked != e.get("version"):
            self.warn.append(f"{lib_id}: library v{e.get('version')} ≠ bản khoá của project v{locked} (anchor lấy từ library hiện tại)")
        return e

    def loc_entry(self, bible_loc_id: str) -> dict:
        return self.lib_entry(self.bible_loc[bible_loc_id]["lib"])


# ---- timeline từng shot ------------------------------------------------------

def rng_for(*parts: str) -> random.Random:
    return random.Random("|".join(parts))


def shot_window(shot: dict, ctx: Ctx) -> tuple[float, float]:
    ls = [ctx.lines[i] for i in shot["line_ids"]]
    start = min(l["start"] for l in ls)
    end = max(l["start"] + l["duration"] for l in ls)
    sp = shot.get("span")
    return (start + sp[0], start + sp[1]) if sp else (start, end)


def js(v) -> str:
    return json.dumps(v, ensure_ascii=False)


class PosTrack:
    """Tâm x (toạ độ cảnh) của một nhân vật theo thời gian trong shot — để quay mắt đúng khi đang đi."""

    def __init__(self, x0: float):
        self.x0, self.segs = x0, []  # segs: (t0, dur, xa, xb)

    def x_at(self, t: float) -> float:
        x = self.x0
        for t0, d, xa, xb in self.segs:
            if t >= t0 + d:
                x = xb
            elif t >= t0:
                x = xa + (xb - xa) * (t - t0) / d
                break
            else:
                break
        return x

    def end_x(self) -> float:
        return self.segs[-1][3] if self.segs else self.x0


def gaze_toward(from_x: float, to_x: float) -> str:
    if abs(to_x - from_x) < 1:
        return "center"
    return "left" if to_x < from_x else "right"


def facing_view(cid: str, t: float, tracks: dict) -> str:
    """view tq-r|tq-l quay mặt về nhân vật gần nhất trong shot; một mình hoặc trùng x → front."""
    me = tracks[cid].x_at(t)
    others = [tr.x_at(t) for k, tr in tracks.items() if k != cid]
    if not others:
        return "front"
    nearest = min(others, key=lambda x: abs(x - me))
    if abs(nearest - me) < 1:
        return "front"
    return "tq-r" if nearest > me else "tq-l"


def nod_js(sel: str, t: float) -> str:
    # gật: cả thân rig xuống 2.5 px rồi về chỗ cũ (yoyo 2 nhịp = kết thúc đúng vị trí ban đầu)
    return f'tl.to("{sel}", {{attr: {{y: "+=2.5"}}, duration: 0.14, repeat: 1, yoyo: true, ease: "sine.inOut"}}, {t:.2f});'


def flinch_js(sel: str, t: float) -> str:
    return f'tl.to("{sel}", {{attr: {{x: "-=6"}}, duration: 0.08, repeat: 1, yoyo: true, ease: "power2.out"}}, {t:.2f});'


def build_shot_js(st: Stage, dur: float, abs0: float, ctx: Ctx) -> str:
    sid, out = st.sid, []
    v0, v1 = st.camera()
    out.append(f'tl.fromTo("#{sid}-stage", {{attr: {{viewBox: {js(v0)}}}}}, {{attr: {{viewBox: {js(v1)}}}, duration: {dur:.3f}, ease: "none"}}, 0);')
    for cid, c in st.chars.items():
        idle = ctx.chars[cid].get("idle", {})
        half = float(idle.get("breath_s", 3.6)) / 2
        n = max(1, int(dur // half))
        sel = f"#{c['id']}"
        out.append(f'tl.fromTo("{sel} .head", {{y: 0}}, {{y: -2.5, duration: {half:.2f}, ease: "sine.inOut", yoyo: true, repeat: {n - 1}}}, 0);')
        out.append(f'tl.fromTo("{sel} .torso", {{y: 0}}, {{y: -1.2, duration: {half:.2f}, ease: "sine.inOut", yoyo: true, repeat: {n - 1}}}, 0);')
        r = rng_for(sid, cid)
        lo, hi = (idle.get("blink_s") or [2.5, 5.0])[:2]
        t = r.uniform(0.6, 1.8)
        while t < dur - 0.2:
            out.append(f'tl.set("{sel}", {{attr: {{"data-blink": 1}}}}, {t:.2f}); tl.set("{sel}", {{attr: {{"data-blink": 0}}}}, {t + 0.12:.2f});')
            t += r.uniform(lo, hi)
        if c["mouth"]:  # khẩu hình theo số âm tiết của các line do nhân vật nói trong shot
            for lid in st.shot["line_ids"]:
                ln = ctx.lines[lid]
                if ln["speaker"] != cid:
                    continue
                words = ln["text"].split()
                step = ln["duration"] / max(1, len(words))
                for i in range(len(words)):
                    tt = ln["start"] - abs0 + i * step
                    if 0 <= tt < dur:
                        out.append(f'tl.set("{sel}", {{attr: {{"data-mouth": "{MOUTH_PATTERN[(i + len(cid)) % len(MOUTH_PATTERN)]}"}}}}, {tt:.2f});')
                end = ln["start"] - abs0 + ln["duration"]
                if 0 <= end < dur:
                    out.append(f'tl.set("{sel}", {{attr: {{"data-mouth": "closed"}}}}, {end:.2f});')
    for key, pid in st.prop_ids.items():
        if st.ctx.bible_prop.get(key.split("-")[0], {}).get("lib") == "candle" or key.startswith("nen"):
            r = rng_for(sid, key)
            n = max(1, int(dur // 0.4))
            out.append(f'tl.fromTo("#{pid} .flame", {{scaleY: 1, scaleX: 1, transformOrigin: "50% 100%"}}, '
                       f'{{scaleY: 1.08, scaleX: 0.95, duration: 0.4, ease: "sine.inOut", yoyo: true, repeat: {n - 1}}}, {r.uniform(0, 0.3):.2f});')

    # --- beat đã quy ra giây trong shot (theo từ nếu có word)
    beats = []
    for b in st.shot.get("beats", []):
        beats.append((beat_time(b, ctx.lines, abs0), b))
    beats.sort(key=lambda x: x[0])

    # --- quỹ đạo vị trí: di chuyển khai bằng beat `move` (tuần tự theo thời gian)
    tracks = {cid: PosTrack(c["x"]) for cid, c in st.chars.items()}
    for t, b in beats:
        mv = b.get("move")
        if not mv:
            continue
        cid = mv["char"]
        if cid not in st.chars:
            raise ValueError(f"{sid}: move cho '{cid}' không có trong shot")
        tgt = st.loc["stand"].get(mv["to"])
        if not tgt:
            raise ValueError(f"{sid}: move.to '{mv['to']}' không phải anchor stand (L/C/R)")
        d = float(mv.get("dur", 1.2))
        tr = tracks[cid]
        xa = tr.end_x()
        tr.segs.append((t, d, xa, tgt["x"]))

    # --- người nghe & người nói tự động: quay mắt theo vị trí tại thời điểm line bắt đầu; người nghe gật ở dấu câu
    explicit_react: dict[str, list[float]] = {}
    for t_b, b in beats:
        if isinstance(b.get("react"), dict):
            explicit_react.setdefault(b["react"]["char"], []).append(t_b)
    auto = []
    for ln in (ctx.lines[i] for i in st.shot["line_ids"]):
        spk = ln["speaker"]
        t_line = max(0.0, ln["start"] - abs0)
        if spk not in st.chars:
            continue
        listeners = [k for k in st.chars if k != spk]
        for lk in listeners:
            auto.append((t_line, f'tl.set("#{st.chars[lk]["id"]}", {{attr: {{"data-gaze": {js(gaze_toward(tracks[lk].x_at(t_line), tracks[spk].x_at(t_line)))}}}}}, {t_line:.2f});'))
            for te in sentence_ends(ln["text"], ln["start"], ln["duration"], ln.get("words")):
                tt = te - abs0
                # bỏ gật tự động nếu đã có gật tường minh gần đó (tránh hai tween cùng lệch = gật đôi)
                if 0 <= tt < dur and not any(abs(tt - x) < 0.3 for x in explicit_react.get(lk, [])):
                    auto.append((tt, nod_js(f"#{st.chars[lk]['id']}", tt)))
        if listeners:
            lk0 = listeners[0]
            auto.append((t_line, f'tl.set("#{st.chars[spk]["id"]}", {{attr: {{"data-gaze": {js(gaze_toward(tracks[spk].x_at(t_line), tracks[lk0].x_at(t_line)))}}}}}, {t_line:.2f});'))
    out.extend(s for _, s in sorted(auto, key=lambda x: x[0]))

    # --- trạng thái đạo cụ/ánh sáng/nhân vật theo beat, di chuyển, nhìn, phản ứng
    for t, b in beats:
        for target, val in (b.get("set") or {}).items():
            if target == "light":
                out.append(f'tl.set("#{st.light_id}", {{attr: {{"data-light": {js(val)}}}}}, {t:.2f});')
            elif target.startswith("prop:"):
                out.append(f'tl.set("#{st.prop_ids[target[5:]]}", {{attr: {{"data-state": {js(val)}}}}}, {t:.2f});')
            elif target in st.chars:
                if val.get("view") == "auto":  # quay mặt về nhân vật gần nhất tại thời điểm beat (không tự quay lại khi người kia đi chỗ khác)
                    val = {**val, "view": facing_view(target, t, tracks)}
                attrs = {f"data-{k}": v for k, v in val.items()}
                out.append(f'tl.set("#{st.chars[target]["id"]}", {{attr: {js(attrs)}}}, {t:.2f});')
            else:
                raise ValueError(f"{sid}: beat.set có khoá lạ '{target}'")
        if b.get("move"):
            mv = b["move"]
            cid = mv["char"]
            c = st.chars[cid]
            d = float(mv.get("dur", 1.2))
            tgt = st.loc["stand"][mv["to"]]
            x_new = tgt["x"] - 260 * c["s"]
            k = max(1, round(d / 0.5))
            out.append(f'tl.set("#{c["id"]}", {{attr: {{"data-gaze": {js(gaze_toward(tracks[cid].x_at(t), tgt["x"]))}}}}}, {t:.2f});')
            out.append(f'tl.to("#{c["id"]}", {{attr: {{x: {x_new:.1f}}}, duration: {d:.2f}, ease: "power1.inOut"}}, {t:.2f});')
            # bước nhẹ: bob 3 px (chạy: 6 px), 2k nhịp đều (kết thúc đúng cao độ ban đầu)
            bob = 6 if mv.get("gait") == "run" else 3
            out.append(f'tl.to("#{c["id"]}", {{attr: {{y: "-={bob}"}}, duration: {d / (2 * k):.3f}, repeat: {2 * k - 1}, yoyo: true, ease: "sine.inOut"}}, {t:.2f});')
            # bước chân: đổi walk-a/walk-b ~0.3 s/nhịp trong lúc đi, kết thúc về idle (R5.4, R11.3)
            gait = mv.get("gait", "walk")
            if gait not in ("walk", "run"):
                raise ValueError(f"{sid}: move.gait phải là walk|run (nhận '{gait}')")
            steps = max(2, int(d / (0.16 if gait == "run" else 0.3)))
            for i in range(steps):
                out.append(f'tl.set("#{c["id"]}", {{attr: {{"data-pose": "{gait}-{"a" if i % 2 == 0 else "b"}"}}}}, {t + i * d / steps:.2f});')
            out.append(f'tl.set("#{c["id"]}", {{attr: {{"data-pose": "idle"}}}}, {t + d:.2f});')
            c["x"] = tgt["x"]  # bản ghi tĩnh dùng cho các bước sau (tracks giữ quỹ đạo chính xác)
        if b.get("hand_over"):
            out.extend(st.hand_over_js(b, t))
        if b.get("look"):
            lk = b["look"]
            out.append(f'tl.set("#{st.chars[lk["char"]]["id"]}", {{attr: {{"data-gaze": {js(gaze_toward(tracks[lk["char"]].x_at(t), tracks[lk["target"]].x_at(t)))}}}}}, {t:.2f});')
        if b.get("react"):
            rc = b["react"]
            sel = f"#{st.chars[rc['char']]['id']}"
            preset = rc.get("preset", "nod")
            if preset == "nod":
                out.append(nod_js(sel, t))
            elif preset == "flinch":
                out.append(flinch_js(sel, t))
            else:
                raise ValueError(f"{sid}: react.preset '{preset}' không hỗ trợ (nod|flinch)")
    return "\n    ".join(out)


def shot_html(st: Stage, dur: float, abs0: float, ctx: Ctx, pal_css: str) -> str:
    st.scene_svg = st.scene()
    for p in st.shot.get("props", []):
        st.add_prop(p)
    for c in st.shot.get("characters", []):
        st.add_char(c)
    body_js = build_shot_js(st, dur, abs0, ctx)
    return f"""<template>
  <style>
    {pal_css}
    #root {{ position: absolute; inset: 0; overflow: hidden; background: var(--pal-ink); }}
    #root > svg {{ display: block; }}
  </style>
  <div id="root" data-composition-id="{st.sid}" data-width="{W}" data-height="{H}" data-layout-allow-overflow>
    {st.svg()}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
    {body_js}
    window.__timelines["{st.sid}"] = tl;
  </script>
</template>
"""


# ---- chính -------------------------------------------------------------------

def wav_seconds(p: Path) -> float | None:
    try:
        with wave.open(str(p)) as w:
            return w.getnframes() / w.getframerate()
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--until", help="dựng các shot từ đầu tới shot này (gồm cả nó)")
    ap.add_argument("--shots", help="id shot cách nhau dấu phẩy")
    ap.add_argument("--scenes", help="chỉ các scene này")
    args = ap.parse_args()

    proj = args.project.resolve()
    out = (args.out or proj / "video_demo").resolve()
    ctx = Ctx(proj)
    shots = ctx.shotlist["shots"]
    if args.shots:
        want = set(args.shots.split(","))
        shots = [s for s in shots if s["id"] in want]
    if args.until:
        ids = [s["id"] for s in shots]
        if args.until not in ids:
            print(f"LỖI: --until {args.until} không có trong shotlist", file=sys.stderr)
            return 1
        shots = shots[: ids.index(args.until) + 1]
    if args.scenes:
        sc = set(args.scenes.split(","))
        keep = {ln["id"] for s in ctx.manifest["scenes"] if s["id"] in sc for ln in s["lines"]}
        shots = [s for s in shots if set(s["line_ids"]) <= keep]
    if not shots:
        print("LỖI: không có shot nào để dựng", file=sys.stderr)
        return 1

    refs = ctx.bible.get("style", {}).get("palette_ref") or ["base"]
    pal = L.load_palette(L.LIB, refs, ctx.bible.get("style", {}).get("palette", {}))
    pal_css = ":root { " + "; ".join(f"--pal-{k}: {v}" for k, v in pal.items()) + " }"

    wins = [shot_window(s, ctx) for s in shots]
    t0 = wins[0][0]
    ends = [wins[i + 1][0] if i + 1 < len(shots) else wins[i][1] for i in range(len(shots))]  # lấp khoảng nghỉ giữa các line
    total = ends[-1] - t0

    (out / "compositions").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "sfx").mkdir(parents=True, exist_ok=True)
    (out / "assets" / "audio").mkdir(parents=True, exist_ok=True)
    for name in ("hyperframes.json", "meta.json", "package.json"):
        src = proj / "video" / name
        if src.exists() and not (out / name).exists():
            shutil.copy2(src, out / name)

    hosts, audios, sfx_n = [], [], 0
    for i, (s, (a0, _), end) in enumerate(zip(shots, wins, ends)):
        start, dur = a0 - t0, end - a0
        s = expand_shot(s, ctx.lines, a0)  # bung macro hành vi (library/behaviors) → beat thường + SFX
        st = Stage(s, ctx)
        (out / "compositions" / f"{s['id']}.html").write_text(shot_html(st, dur, a0, ctx, pal_css), encoding="utf-8")
        hosts.append(f'    <div id="{s["id"]}" class="clip" data-composition-id="{s["id"]}" data-composition-src="compositions/{s["id"]}.html" '
                     f'data-start="{start:.3f}" data-duration="{dur:.3f}" data-track-index="1" data-track-kind="graphics" '
                     f'data-width="{W}" data-height="{H}"></div>')
        for fx in s.get("sfx", []):
            src = REPO / fx["src"]
            if not src.exists():
                ctx.warn.append(f"{s['id']}: thiếu file SFX {fx['src']}")
                continue
            dest = out / "assets" / "sfx" / src.name
            shutil.copy2(src, dest)
            sfx_n += 1
            d = wav_seconds(dest)
            audios.append(f'    <audio id="sfx-{s["id"]}-{sfx_n}" class="clip" src="assets/sfx/{src.name}" data-start="{start + fx["t"]:.3f}" '
                          f'{f"data-duration=\"{d:.3f}\" " if d else ""}data-volume="0.8" data-track-index="3"></audio>')

    voice = proj / "audio" / "voiceover.wav"
    if voice.exists():
        shutil.copy2(voice, out / "assets" / "audio" / "voiceover.wav")
        audios.insert(0, f'    <audio id="voice" class="clip" src="assets/audio/voiceover.wav" data-start="0" data-duration="{total:.3f}" '
                         f'data-media-start="{t0:.3f}" data-volume="1" data-track-index="2"></audio>')
    else:
        ctx.warn.append("thiếu audio/voiceover.wav (file sinh bằng build_voiceover.py, không commit) — video dựng KHÔNG có giọng")

    index = f"""<!doctype html>
<html lang="vi" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <title>{esc_attr(ctx.bible.get("meta", {}).get("title", proj.name))} — dựng tự động</title>
    <script src="{GSAP_SRC}"></script>
    <style>
      {pal_css}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: var(--pal-ink); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{total:.3f}" data-width="{W}" data-height="{H}">
{chr(10).join(hosts)}
{chr(10).join(audios)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
"""
    (out / "index.html").write_text(index, encoding="utf-8")
    print(json.dumps({"status": "ok", "out": str(out), "shots": len(shots), "duration_s": round(total, 3),
                      "t0": round(t0, 3), "sfx": sfx_n, "voice": voice.exists(), "warnings": ctx.warn}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
