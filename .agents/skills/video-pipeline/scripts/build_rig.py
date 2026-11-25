#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh rig SVG nhân vật + pose sheet từ script/bible.json.

Mỗi nhân vật trong bible có khối "rig" (tham số). Gộp theo thứ tự:
library/rigs/archetypes.json (archetype → outfit) → khoá ghi đè trong bible.
Màu là TOKEN (không hex): lấy từ library/palettes/<style.palette_ref...>.json
rồi style.palette của bible (chỉ để ghi đè đặc thù của project).
Một rig = một file SVG tự chứa, nhóm có tên + CSS điều khiển bằng thuộc tính:

  <g class="rig rig-<id>" data-emotion="calm" data-mouth="auto" data-pose="idle"
                          data-stance="stand" data-gaze="center" data-blink="0" data-khan="on">

  data-emotion  emotion_vocab của bible (calm, focused, worried, afraid, shocked,
                dread, sad, grief, angry, suspicious, relieved)
  data-mouth    auto | closed | half | open | round   (auto = theo cảm xúc)
  data-pose     idle | clasp | point-l | reach-l | raise-both
  data-stance   stand | sit | kneel | lay | stagger[-r] | tilt[-r] | lie[-r]   (quỳ, lạy, loạng choạng, nghiêng đổ, nằm/ngất)
  data-gaze     center | left | right | up | down
  data-blink    0 | 1
  data-khan     on | off   (khăn tang trên đầu; dùng cho trạng thái đạo cụ)

Quy ước trái/phải theo GIẢI PHẪU nhân vật: "l" = bên trái nhân vật = bên PHẢI người xem.
Khớp vai/khuỷu dùng transform-origin theo toạ độ viewBox của chính file rig
(transform-box: view-box, giá trị ghi trong bible.pivots) nên không lệch khi
đặt rig vào cảnh bằng transform bên ngoài. Chi tiết mặt dùng 50% 50% (fill-box).

Dùng:
  python .agents/skills/video-pipeline/scripts/build_rig.py \
      --bible projects/<slug>/script/bible.json --out projects/<slug>/assets/rig
  thêm --no-sheet để bỏ pose sheet (cần playwright + chromium); --library để đổi thư mục library.
  thêm --script projects/<slug>/script/script.json để khớp id/giọng với kịch bản.
Mỗi nhân vật xuất <id>.svg + <id>.rig.json (viewBox, pivot, danh sách trạng thái) cho generator dựng cảnh.
LUẬT NHÚNG: rig chỉ được nhúng vào cảnh dưới dạng <svg> lồng nhau (có viewBox riêng), KHÔNG chép <g>
trần vào svg cảnh, vì pivot dùng transform-box: view-box (RULES.md R3.4).

Kiểm trước khi ghi file (trừ --no-check): tay ở mọi pose × (đứng|ngồi) và đầu/thân có nằm
trong viewBox không (tính giải tích, có scale), và (nếu có --script) id + giọng khớp.
Đây KHÔNG phải kiểm render: vẫn phải xem pose sheet.

Nhân vật mới nên clone từ nhân vật cũ: {"id": "chu_tu", "extends": "chu_hai", "rig_params": {chỉ phần khác}}.
Hoặc chọn khuôn: "rig": {"archetype": "adult_m", "outfit": "mourning", ...ghi đè}  (library/rigs/archetypes.json).

Khai báo rig trong bible: "rig": {tham số}  hoặc  "rig": "assets/rig/<id>.svg" + "rig_params": {tham số}.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CX = 260
FLOOR = 580
VB_W, VB_H = 520, 600  # rộng hơn để tay vươn/chỉ không bị cắt
SHOULDER_Y = 318
ELBOW_Y = 388
NECK_Y = 275

# brow rot: dương = đầu mày phía trong nhướn lên; mc: >0 cười, <0 mếu
EMOTIONS = {
    "calm": dict(byl=0, byr=0, br=0, lid=0.0, ps=1.0, es=1.0, shade=0.0, tear=0, mouth="closed", mc=0.9, gx=0),
    "focused": dict(byl=2, byr=2, br=-7, lid=0.18, ps=1.0, es=1.0, shade=0.0, tear=0, mouth="closed", mc=0.15, gx=0),
    "worried": dict(byl=-3, byr=-3, br=14, lid=0.0, ps=0.95, es=1.0, shade=0.0, tear=0, mouth="closed", mc=-0.9, gx=0),
    "afraid": dict(byl=-9, byr=-9, br=10, lid=0.0, ps=0.7, es=1.12, shade=0.0, tear=0, mouth="half", mc=0.0, gx=0),
    "shocked": dict(byl=-11, byr=-11, br=0, lid=0.0, ps=0.5, es=1.15, shade=0.0, tear=0, mouth="round", mc=0.0, gx=0),
    "dread": dict(byl=-2, byr=-2, br=8, lid=0.32, ps=0.7, es=1.0, shade=0.28, tear=0, mouth="closed", mc=-1.1, gx=0),
    "sad": dict(byl=-2, byr=-2, br=16, lid=0.28, ps=1.0, es=1.0, shade=0.0, tear=0, mouth="closed", mc=-1.0, gx=0),
    "grief": dict(byl=-3, byr=-3, br=20, lid=0.42, ps=1.0, es=1.0, shade=0.0, tear=1, mouth="half", mc=0.0, gx=0),
    "angry": dict(byl=3, byr=3, br=-18, lid=0.2, ps=0.9, es=1.0, shade=0.0, tear=0, mouth="closed", mc=-1.3, gx=0),
    "suspicious": dict(byl=-9, byr=3, br=-4, lid=0.34, ps=1.0, es=1.0, shade=0.0, tear=0, mouth="closed", mc=-0.3, gx=6),
    "relieved": dict(byl=-4, byr=-4, br=8, lid=0.3, ps=1.0, es=1.0, shade=0.0, tear=0, mouth="closed", mc=1.7, gx=0),
}

# (góc cánh trên, góc cẳng tay) cho [arm-l, arm-r]; arm-r là ảnh gương của arm-l
POSES = {
    "idle": ((-4, 0), (4, 0)),
    "clasp": ((-8, 92), (8, -92)),
    "point-l": ((-72, -8), (4, 0)),
    "reach-l": ((-95, -4), (4, 0)),
    "raise-both": ((-50, -130), (50, 130)),
    # đi bộ: tay giữ idle; hai chân ngược pha (xem LEG_POSES). Generator chuyển walk-a ↔ walk-b khi di chuyển.
    "walk-a": ((-4, 0), (4, 0)),
    "walk-b": ((-4, 0), (4, 0)),
    # chạy: tay gập, vung ngược pha (l = trái nhân vật). Chân: LEG_POSES, bước dài + nhấc cao hơn đi bộ.
    "run-a": ((-62, -88), (14, 30)),
    "run-b": ((-14, -30), (62, 88)),
    # ôm đầu / che mặt khi sợ: hai cánh tay gập lên che đầu
    "cover-head": ((-150, -135), (150, 135)),
    # chắp tay vái: như clasp nhưng cao hơn (trước ngực) — đi kèm stance quỳ để lạy
    "pray": ((-14, 112), (14, -112)),
    # lạy: hai tay chống xuống đất phía trước, hơi xoè (dùng với stance lay)
    "prostrate": ((-30, -8), (30, 8)),
}

# Đi bộ NHÌN CHÍNH DIỆN: chân nhấc lên (dịch lên 10 px, vào giữa 4 px), chân kia tựa đất.
# Không xoay đối xứng (sẽ thành dang chân / khép chéo). [leg-l, leg-r]; leg-l = chân trái nhân vật (bên phải người xem).
LEG_POSES = {
    "walk-a": ("translate(6px,-16px)", "translate(0px,0px)"),
    "walk-b": ("translate(0px,0px)", "translate(-6px,-16px)"),
    "run-a": ("translate(10px,-34px)", "translate(-4px,0px)"),
    "run-b": ("translate(4px,0px)", "translate(-10px,-34px)"),
}
HIP_Y = 470
# Góc nhìn (data-view): front = nhìn thẳng; tq-r / tq-l = 3/4, mặt quay về bên PHẢI / TRÁI của người xem.
# Sinh từ cùng tham số rig (không vẽ riêng từng nhân vật): đổi bằng CSS trên nhóm .view/.feat, chi phí render bằng 0.
VIEWS = ("front", "tq-r", "tq-l")
# Tư thế thân (data-stance): đứng/ngồi + quỳ, lạy (quỳ rạp), loạng choạng, nghiêng đổ, nằm (ngất).
STANCES = ("stand", "sit", "kneel", "lay", "stagger", "tilt", "lie", "stagger-r", "tilt-r", "lie-r")  # "-r" = ngã về bên phải người xem (mặc định ngã về trái)
KNEEL_DY = 74
LIE_PIVOT_Y, LIE_DY = 340, 183  # nằm ngửa: quay -90° quanh giữa thân rồi hạ xuống sát đất
VIEW_BODY_SX, VIEW_BODY_DX, VIEW_FEAT_DX, VIEW_HAIR_DX, VIEW_FAR_EYE = 0.88, 5, 13, 0, 0.72
VIEW_CHEEK_BACK = 19
LEG_X = {"l": CX + 24, "r": CX - 24}  # tâm hông theo toạ độ viewBox

GAZE = {"center": (0, 0), "left": (-5, 0), "right": (5, 0), "up": (0, -4), "down": (0, 4)}

REPO = Path(__file__).resolve().parents[4]
DEFAULT_LIBRARY = REPO / "library"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from library import load_palette  # noqa: E402  (một nguồn gộp palette)


def resolve_rig(char: dict, catalog: dict) -> dict:
    """archetype → outfit → khoá ghi đè của chính nhân vật."""
    spec = char["rig"]
    if isinstance(spec, dict):
        raw = dict(spec)
    elif isinstance(spec, str):  # "rig": "đường/dẫn.svg" + rig_params
        raw = dict(char.get("rig_params") or {})
        raw.setdefault("file", spec)
    else:
        raise SystemExit(f"LỖI: {char['id']}: 'rig' phải là object tham số hoặc đường dẫn .svg, nhận {type(spec).__name__}")
    merged: dict = {}
    for key, table in (("archetype", "archetypes"), ("outfit", "outfits")):
        name = raw.get(key)
        if name:
            if name not in catalog.get(table, {}):
                raise SystemExit(f"LỖI: {char['id']}: {key} '{name}' không có trong library/rigs/archetypes.json")
            merged.update(catalog[table][name]["params"])
    merged.update({k: v for k, v in raw.items() if k not in ("archetype", "outfit")})
    merged["archetype"], merged["outfit"] = raw.get("archetype"), raw.get("outfit")
    return merged


def rig_params_of(char: dict) -> dict:
    spec = char.get("rig")
    if isinstance(spec, dict):
        return dict(spec)
    return dict(char.get("rig_params") or {})


def resolve_extends(chars: list[dict]) -> list[dict]:
    """Nhân vật có "extends": "<id khác trong bible>" = bản sao của nhân vật đó, chỉ ghi đè tham số khác đi.
    Tham số rig = rig của gốc + ghi đè của chính nó (rig / rig_params); file SVG riêng theo id mới."""
    by_id = {c["id"]: c for c in chars}

    def params(c: dict, seen: tuple = ()) -> dict:
        if c["id"] in seen:
            raise ValueError(f"extends vòng tròn: {' → '.join(seen + (c['id'],))}")
        base = c.get("extends")
        if not base:
            return rig_params_of(c)
        if base not in by_id:
            raise ValueError(f"{c['id']}: extends '{base}' không có trong bible")
        merged = params(by_id[base], seen + (c["id"],))
        merged.pop("file", None)
        merged.update(rig_params_of(c))
        return merged

    out = []
    for c in chars:
        if c.get("extends"):
            c = {**c, "rig": params(c)}
        out.append(c)
    return out


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def esc_attr(s: str) -> str:
    """Giá trị thuộc tính XML: thêm escape dấu nháy kép (tên như Lan "Bé" không làm hỏng aria-label)."""
    return esc(s).replace('"', "&quot;")


class Rig:
    """Một nhân vật + palette đã giải quyết."""

    def __init__(self, char: dict, palette: dict, catalog: dict | None = None):
        self.char = char
        self.id = char["id"]
        p = resolve_rig(char, catalog or {})
        self.p = p
        self.pal = palette
        self.shadow = bool(p.get("shadow"))
        self.missing: set[str] = set()

    def c(self, key: str | None, fallback: str = "ink") -> str:
        """Giải token màu → hex. Token lạ bị ghi nhận và làm hỏng build (không gõ hex trong bible/generator)."""
        if key is None:
            return "none"
        if key in self.pal:
            return self.pal[key]
        self.missing.add(key)
        return self.pal[fallback]

    # ---- hình học -------------------------------------------------------
    @property
    def scale(self) -> float:
        return float(self.p.get("scale", 1.0))

    @property
    def body_w(self) -> float:
        return float(self.p.get("body_w", 100))

    def shoulder(self, side: str) -> tuple[float, float]:
        off = self.body_w / 2 - 8
        return (CX + off, SHOULDER_Y) if side == "l" else (CX - off, SHOULDER_Y)

    def pivots(self) -> dict:
        sl, sr = self.shoulder("l"), self.shoulder("r")
        return {
            "arm-l": f"{sl[0]:g}px {sl[1]:g}px", "arm-r": f"{sr[0]:g}px {sr[1]:g}px",
            "fore-l": f"{sl[0]:g}px {ELBOW_Y}px", "fore-r": f"{sr[0]:g}px {ELBOW_Y}px",
            "note": "transform-box: view-box; toạ độ theo viewBox 0 0 520 600 của file rig (trước scale)",
        }

    def crop(self, x0=None, y0=92, x1=None, y1=322) -> str:
        """viewBox cắt đầu + vai, đã tính scale quanh chân."""
        hs = float(self.p.get("head_scale", 1.0))
        y0 = NECK_Y - (NECK_Y - y0) * hs
        x0 = CX - 90 * hs if x0 is None else x0
        x1 = CX + 90 * hs if x1 is None else x1
        s = self.scale
        tx = lambda x: CX + (x - CX) * s
        ty = lambda y: FLOOR - (FLOOR - y) * s
        return f"{tx(x0):.1f} {ty(y0):.1f} {tx(x1) - tx(x0):.1f} {ty(y1) - ty(y0):.1f}"

    # ---- thành phần ------------------------------------------------------
    def legs(self) -> str:
        ink, pants, shoe = self.c("ink"), self.c(self.p.get("pants", "robe_mourning_dark")), self.c("shoe")
        if self.shadow:
            ink, pants, shoe = self.c("shadow_ink"), self.c("shadow_body"), self.c("shadow_ink")
        out = ['<g class="legs">']
        for side, x in (("r", CX - 36), ("l", CX + 12)):  # r = chân phải nhân vật (bên trái người xem)
            out.append(f'<g class="leg leg-{side}">')
            out.append(f'<rect x="{x}" y="{HIP_Y}" width="24" height="98" rx="10" fill="{pants}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<ellipse cx="{x + 12}" cy="572" rx="23" ry="11" fill="{shoe}" stroke="{ink}" stroke-width="3"/>')
            out.append("</g>")
        out.append("</g>")
        return "".join(out)

    def lap(self) -> str:
        ink = self.c("shadow_ink" if self.shadow else "ink")
        col = self.c("shadow_body" if self.shadow else self.p.get("pants", "robe_mourning_dark"))
        return (f'<ellipse class="lap" cx="{CX}" cy="500" rx="{self.body_w * 0.95:g}" ry="30" '
                f'fill="{col}" stroke="{ink}" stroke-width="6"/>')

    def kleg(self) -> str:
        """Chân khi quỳ NHÌN NGHIÊNG (view tq-r/tq-l): đùi chìa về phía mặt quay, cẳng chân gập ra sau nằm sát đất, gót giày dựng lên.
        Toạ độ trong .body (đã dịch KNEEL_DY khi quỳ). Chỉ hiện khi stance kneel|lay và view khác front."""
        ink = self.c("shadow_ink" if self.shadow else "ink")
        pants = self.c("shadow_body" if self.shadow else self.p.get("pants", "robe_mourning_dark"))
        shoe = self.c("shadow_ink" if self.shadow else "shoe")
        out = []
        for d, name in ((1, "r"), (-1, "l")):  # d=+1: mặt quay phải người xem → gối chìa sang phải
            kx, bx = CX + d * 66, CX - d * 62
            out.append(f'<g class="kleg kleg-{name}">')
            for w, col in ((32, ink), (22, pants)):  # cẳng chân (sau) rồi bàn chân rồi đùi (trước): viền + ruột
                out.append(f'<line x1="{kx}" y1="492" x2="{bx}" y2="494" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
            out.append(f'<ellipse cx="{bx - d * 8}" cy="486" rx="11" ry="19" fill="{shoe}" stroke="{ink}" stroke-width="3"/>')
            for w, col in ((38, ink), (28, pants)):
                out.append(f'<line x1="{CX - d * 4}" y1="474" x2="{kx}" y2="484" stroke="{col}" stroke-width="{w}" stroke-linecap="round"/>')
            out.append("</g>")
        return "".join(out)

    def kfeet(self) -> str:
        """Gót chân khi quỳ: hai mũi giày thò ra hai bên váy, ở sát đất (nằm ngoài .body để không bị dịch xuống)."""
        ink = self.c("shadow_ink" if self.shadow else "ink")
        shoe = self.c("shadow_ink" if self.shadow else "shoe")
        dx = self.body_w * 0.62
        return "".join(
            f'<ellipse class="kfoot" cx="{CX + sg * dx:g}" cy="573" rx="22" ry="10" fill="{shoe}" stroke="{ink}" stroke-width="3"/>'
            for sg in (-1, 1))

    def torso(self) -> str:
        bw = self.body_w
        ink = self.c("shadow_ink" if self.shadow else "ink")
        robe = self.c("shadow_body" if self.shadow else self.p.get("robe", "robe_mourning"))
        skin = self.c("shadow_body" if self.shadow else self.p.get("skin", "skin"))
        x = CX - bw / 2
        parts = [
            f'<rect class="neck" x="{CX - 12}" y="266" width="24" height="44" rx="6" fill="{skin}" stroke="{ink}" stroke-width="5"/>',
            f'<rect class="torso" x="{x:g}" y="300" width="{bw:g}" height="195" rx="26" fill="{robe}" stroke="{ink}" stroke-width="6"/>',
            f'<path class="collar" d="M {CX - 20} 302 L {CX} 338 L {CX + 20} 302 Z" fill="{skin}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>',
        ]
        if self.p.get("sash"):
            parts.append(f'<rect class="sash" x="{x + 2:g}" y="424" width="{bw - 4:g}" height="16" fill="{self.c(self.p["sash"])}" stroke="{ink}" stroke-width="3"/>')
        if self.p.get("necklace") == "silver_lock":
            # Kiềng bạc / khoá bạc đeo cổ hộ mệnh của trẻ con làng quê Việt
            parts.append(f'<path d="M {CX - 24} 306 Q {CX} 340 {CX + 24} 306" stroke="{self.c("paper")}" stroke-width="3.5" fill="none"/>')
            parts.append(f'<rect x="{CX - 8}" y="330" width="16" height="12" rx="3" fill="{self.c("paper")}" stroke="{ink}" stroke-width="2"/>')
        if self.shadow:  # rách vải rủ từ vai
            kh = self.c("khan_white")
            for dx, h in ((-bw * 0.32, 120), (bw * 0.34, 96)):
                parts.append(f'<path d="M {CX + dx:g} 330 q -10 {h / 2:g} 6 {h}" stroke="{ink}" stroke-width="20" stroke-linecap="round" fill="none"/>'
                             f'<path d="M {CX + dx:g} 330 q -10 {h / 2:g} 6 {h}" stroke="{kh}" stroke-width="12" stroke-linecap="round" fill="none"/>')
        return "".join(parts)

    def arm(self, side: str) -> str:
        sx, sy = self.shoulder(side)
        ink = self.c("shadow_ink" if self.shadow else "ink")
        sleeve = self.c("shadow_body" if self.shadow else self.p.get("sleeve", "robe_mourning_dark"))
        skin = self.c("shadow_body" if self.shadow else self.p.get("skin", "skin"))
        hand_ink = ink
        return (
            f'<g class="arm arm-{side}">'
            f'<line x1="{sx:g}" y1="{sy}" x2="{sx:g}" y2="{ELBOW_Y}" stroke="{ink}" stroke-width="36" stroke-linecap="round"/>'
            f'<line x1="{sx:g}" y1="{sy}" x2="{sx:g}" y2="{ELBOW_Y}" stroke="{sleeve}" stroke-width="26" stroke-linecap="round"/>'
            f'<g class="fore fore-{side}">'
            f'<line x1="{sx:g}" y1="{ELBOW_Y}" x2="{sx:g}" y2="450" stroke="{ink}" stroke-width="34" stroke-linecap="round"/>'
            f'<line x1="{sx:g}" y1="{ELBOW_Y}" x2="{sx:g}" y2="450" stroke="{sleeve}" stroke-width="24" stroke-linecap="round"/>'
            f'<circle class="hand" cx="{sx:g}" cy="462" r="15" fill="{skin}" stroke="{hand_ink}" stroke-width="4"/>'
            f'</g></g>'
        )

    def head(self) -> str:
        p = self.p
        sh = self.shadow
        ink = self.c("shadow_ink" if sh else p.get("ink", "ink"))
        skin = self.c("shadow_body" if sh else p.get("skin", "skin"))
        hair = self.c(p.get("hair_color", "hair_black"))
        brow_col = self.c(p.get("brow_color", p.get("hair_color", "hair_black")))
        hy = 14 * float(p.get("hunch", 0))
        hs = float(p.get("head_scale", 1.0))
        out = [f'<g class="head" transform="translate(0 {hy:g})">']
        if hs != 1.0:  # đầu to/nhỏ quanh gốc cổ (trẻ em: đầu to)
            out.append(f'<g class="head-scale" transform="translate({CX} {NECK_Y}) scale({hs:g}) translate({-CX} {-NECK_Y})">')

        hair_style = p.get("hair", "short")
        hat = p.get("hat")
        if hair_style in ("bun",) and not hat:
            out.append(f'<ellipse cx="{CX}" cy="205" rx="62" ry="66" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<circle class="bun" cx="{CX}" cy="132" r="24" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
        elif hair_style == "pigtails" and not hat:
            # Hai búi/bím tóc hai bên cho bé gái / thiếu nữ
            out.append(f'<ellipse cx="{CX}" cy="205" rx="62" ry="66" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<circle class="bun-r" cx="{CX - 56}" cy="162" r="18" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<circle class="bun-l" cx="{CX + 56}" cy="162" r="18" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
        elif hair_style == "topknot" and not hat:
            # Chỏm tóc / đào lộn hột cho bé trai nhỏ dân gian Việt Nam
            out.append(f'<circle class="topknot" cx="{CX}" cy="138" r="17" fill="{hair}" stroke="{ink}" stroke-width="4.5"/>')
            out.append(f'<path d="M {CX - 6} 144 Q {CX} 156 {CX + 6} 144" stroke="{ink}" stroke-width="3" fill="none"/>')
        elif hair_style == "bob" and not hat:
            # Tóc ngang vai, không búi: đầu tròn, hai mảng tóc buông xuống cằm
            out.append(f'<ellipse cx="{CX}" cy="205" rx="66" ry="70" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<path d="M {CX - 62} 215 Q {CX - 72} 262 {CX - 56} 290 L {CX - 40} 268 Z" fill="{hair}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>')
            out.append(f'<path d="M {CX + 62} 215 Q {CX + 72} 262 {CX + 56} 290 L {CX + 40} 268 Z" fill="{hair}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>')
        elif hair_style == "long_tied" and not hat:
            # Tóc nữ trẻ: búi củ tỏi cao gọn gàng + tóc mai buông nhẹ
            out.append(f'<ellipse cx="{CX}" cy="205" rx="62" ry="66" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<circle class="bun" cx="{CX}" cy="132" r="22" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<path d="M {CX - 56} 226 Q {CX - 58} 265 {CX - 50} 285" stroke="{hair}" stroke-width="6" stroke-linecap="round" fill="none"/>')
            out.append(f'<path d="M {CX + 56} 226 Q {CX + 58} 265 {CX + 50} 285" stroke="{hair}" stroke-width="6" stroke-linecap="round" fill="none"/>')
        # tai
        for dx in (-58, 58):
            out.append(f'<circle class="ear ear-{"r" if dx < 0 else "l"}" cx="{CX + dx}" cy="226" r="10" fill="{skin}" stroke="{ink}" stroke-width="4"/>')
        # mặt
        out.append(f'<ellipse class="face" cx="{CX}" cy="215" rx="58" ry="62" fill="{skin}" stroke="{ink}" stroke-width="6"/>')
        # tóc trước
        if hair_style in ("short", "bun", "pigtails", "long_tied", "bob") and not hat:
            out.append(
                f'<path class="hair-front" d="M {CX - 60} 206 Q {CX - 64} 148 {CX} 146 Q {CX + 64} 148 {CX + 60} 206 '
                f'Q {CX + 42} 176 {CX} 174 Q {CX - 42} 176 {CX - 60} 206 Z" fill="{hair}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>')
        elif hair_style == "topknot" and not hat:
            # tóc chỏm trán con nít
            out.append(f'<path class="hair-front" d="M {CX - 22} 175 Q {CX} 152 {CX + 22} 175 Q {CX} 190 {CX - 22} 175 Z" fill="{hair}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>')
        out.append('<g class="feat">')  # nét mặt: dịch ngang khi quay 3/4
        # nếp nhăn
        wr = int(p.get("wrinkles", 0))
        if wr >= 1:
            w = f'stroke="{ink}" stroke-width="2.6" stroke-linecap="round" fill="none" opacity="0.5"'
            out.append(f'<path d="M {CX - 30} 190 Q {CX} 184 {CX + 30} 190" {w}/>')
            out.append(f'<path class="chk-r" d="M {CX - 52} 232 l 8 3 M {CX - 52} 241 l 8 -2" {w}/>')
            out.append(f'<path class="chk-l" d="M {CX + 52} 232 l -8 3 M {CX + 52} 241 l -8 -2" {w}/>')
        if wr >= 2:
            out.append(f'<path d="M {CX - 26} 178 Q {CX} 172 {CX + 26} 178" {w}/>')
            out.append(f'<path class="chk-r" d="M {CX - 32} 248 Q {CX - 26} 262 {CX - 18} 268" {w}/>')
            out.append(f'<path class="chk-l" d="M {CX + 32} 248 Q {CX + 26} 262 {CX + 18} 268" {w}/>')
        # mũi
        out.append(f'<path d="M {CX - 5} 236 Q {CX} 242 {CX + 6} 236" stroke="{ink}" stroke-width="3.5" stroke-linecap="round" fill="none"/>')
        # mắt
        eye_rx, eye_ry = (20, 22) if sh else (13, 15)
        for side, ex in (("r", CX - 24), ("l", CX + 24)):
            sclera = self.c("shadow_eye" if sh else "eye_white")
            pup = self.c("shadow_pupil" if sh else "pupil")
            pr = 6 if sh else 6.5
            cloud = (p.get("cloudy_eye") == side)
            out.append(
                f'<g class="eye eye-{side}">'
                f'<ellipse class="sclera" cx="{ex}" cy="222" rx="{eye_rx}" ry="{eye_ry}" fill="{sclera}" stroke="{ink}" stroke-width="4"/>'
                f'<circle class="pupil" cx="{ex}" cy="224" r="{pr}" fill="{pup}"/>'
                + (f'<circle class="cloud" cx="{ex}" cy="223" r="11" fill="{self.c("cloud")}" opacity="0.88"/>' if cloud else "")
                + f'<ellipse class="lid" cx="{ex}" cy="222" rx="{eye_rx + 1.5}" ry="{eye_ry + 1.5}" fill="{skin}"/>'
                f'</g>'
            )
        # sẹo
        if p.get("scar"):
            sx = CX + 28 if p["scar"] == "l" else CX - 28
            out.append(f'<path class="scar scar-{p["scar"]}" d="M {sx - 4} 190 L {sx + 6} 206" stroke="{self.c("scar")}" stroke-width="3.4" stroke-linecap="round"/>')
        # mày
        if not sh:
            out.append(f'<path class="brow brow-r" d="M {CX - 38} 200 Q {CX - 24} 192 {CX - 10} 200" stroke="{brow_col}" stroke-width="5.5" stroke-linecap="round" fill="none"/>')
            out.append(f'<path class="brow brow-l" d="M {CX + 10} 200 Q {CX + 24} 192 {CX + 38} 200" stroke="{brow_col}" stroke-width="5.5" stroke-linecap="round" fill="none"/>')
        # nước mắt
        out.append(
            f'<path class="tears" d="M {CX - 30} 238 q -3 14 0 22 M {CX + 30} 238 q 3 14 0 22" stroke="#cfe6ee" stroke-width="5" stroke-linecap="round" fill="none"/>')
        # râu
        if p.get("beard"):
            out.append(f'<path class="beard" d="M {CX - 26} 274 Q {CX} 322 {CX + 26} 274 Q {CX} 290 {CX - 26} 274 Z" '
                       f'fill="{self.c(p.get("beard_color", "hair_white"))}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>')
        if p.get("mustache"):
            out.append(f'<path class="mustache" d="M {CX - 22} 254 Q {CX - 10} 244 {CX} 252 Q {CX + 10} 244 {CX + 22} 254 Q {CX + 10} 258 {CX} 256 Q {CX - 10} 258 {CX - 22} 254 Z" '
                       f'fill="{hair}" stroke="{ink}" stroke-width="3" stroke-linejoin="round"/>')
        # miệng
        mline = self.c("shadow_line" if sh else "ink")
        mfill = self.c("shadow_ink" if sh else "mouth_dark")
        ms = 1.9 if sh else 1.0
        out.append(
            f'<g class="mouth" transform="translate({CX} 262) scale({ms})">'
            f'<path class="m-closed" d="M -16 -2 Q 0 8 16 -2" stroke="{mline}" stroke-width="4.5" stroke-linecap="round" fill="none"/>'
            f'<ellipse class="m-half" cx="0" cy="1" rx="11" ry="5.5" fill="{mfill}" stroke="{mline}" stroke-width="4"/>'
            f'<ellipse class="m-open" cx="0" cy="3" rx="12" ry="12" fill="{mfill}" stroke="{mline}" stroke-width="4"/>'
            f'<ellipse class="m-round" cx="0" cy="2" rx="7" ry="8" fill="{mfill}" stroke="{mline}" stroke-width="4"/>'
            f'</g>'
        )
        # bóng tối phủ cả mặt (sau mắt/mày/miệng để mí mắt không nổi sáng hơn da)
        out.append(f'<ellipse class="shade" cx="{CX}" cy="215" rx="58" ry="62" fill="#000"/>')
        out.append("</g>")
        # mũ / khăn
        if hat == "khan-xep":
            hc = self.c("robe_indigo_dark")
            out.append(
                f'<path class="hat" d="M {CX - 63} 182 Q {CX - 70} 118 {CX} 108 Q {CX + 70} 118 {CX + 63} 182 '
                f'Q {CX} 160 {CX - 63} 182 Z" fill="{hc}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>'
                f'<path d="M {CX - 50} 150 Q {CX} 128 {CX + 50} 150 M {CX - 56} 168 Q {CX} 146 {CX + 56} 168" stroke="{ink}" stroke-width="3" fill="none" opacity="0.6"/>')
        if p.get("headband"):
            kh = self.c("khan_white")
            out.append(
                f'<g class="acc-khan">'
                f'<path d="M {CX + 56} 176 Q {CX + 88} 216 {CX + 74} 276" stroke="{ink}" stroke-width="20" stroke-linecap="round" fill="none"/>'
                f'<path d="M {CX + 56} 176 Q {CX + 88} 216 {CX + 74} 276" stroke="{kh}" stroke-width="12" stroke-linecap="round" fill="none"/>'
                f'<path d="M {CX - 60} 167 Q {CX} 148 {CX + 60} 167 L {CX + 60} 183 Q {CX} 164 {CX - 60} 183 Z" fill="{kh}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>'
                f'</g>'
            )
        if hs != 1.0:
            out.append("</g>")
        out.append("</g>")
        return "".join(out)

    # ---- CSS -------------------------------------------------------------
    def css(self) -> str:
        r = f".rig-{self.id}"
        sl, sr = self.shoulder("l"), self.shoulder("r")
        lines = [
            f"{r} .arm,{r} .fore{{transform-box:view-box}}",
            f"{r} .arm-l{{transform-origin:{sl[0]:g}px {sl[1]:g}px}}",
            f"{r} .arm-r{{transform-origin:{sr[0]:g}px {sr[1]:g}px}}",
            f"{r} .fore-l{{transform-origin:{sl[0]:g}px {ELBOW_Y}px}}",
            f"{r} .fore-r{{transform-origin:{sr[0]:g}px {ELBOW_Y}px}}",
            f"{r} .eye,{r} .sclera,{r} .pupil,{r} .brow,{r} .m-closed{{transform-box:fill-box;transform-origin:50% 50%}}",
            f"{r} .lid{{transform-box:fill-box;transform-origin:50% 0%;transform:scaleY(var(--lid,0))}}",
            f"{r} .eye{{transform:scale(calc(var(--es,1) * var(--exs,1)),var(--es,1))}}",
            f"{r} .pupil{{transform:translate(var(--gx,0px),var(--gy,0px)) scale(var(--ps,1))}}",
            f"{r} .brow-r{{transform:translateY(calc(var(--byr,0) * 1px)) rotate(calc(var(--br,0) * -1deg))}}",
            f"{r} .brow-l{{transform:translateY(calc(var(--byl,0) * 1px)) rotate(calc(var(--br,0) * 1deg))}}",
            f"{r} .shade{{opacity:var(--shade,0)}}",
            f"{r} .tears{{opacity:var(--tear,0)}}",
            f"{r} .m-closed{{transform:scaleY(var(--mc,.9))}}",
            f"{r} .mouth *{{display:none}}",  # không dùng ">": scoper CSS của HyperFrames bỏ cả khối <style> khi gặp combinator con
            f"{r}[data-khan='off'] .acc-khan{{display:none}}",
            f"{r} .lap{{display:none}}",
            f"{r}[data-stance='sit'] .lap{{display:inline}}",
            f"{r} .leg{{transform-box:view-box}}",
            f"{r} .leg-l{{transform-origin:{LEG_X['l']}px {HIP_Y}px}}",
            f"{r} .leg-r{{transform-origin:{LEG_X['r']}px {HIP_Y}px}}",
            f"{r}[data-stance='sit'] .legs{{display:none}}",
            f"{r}[data-stance='sit'] .body{{transform:translateY(56px)}}",
            f"{r} .kfoot{{display:none}}",
            f"{r}[data-stance='kneel'] .legs,{r}[data-stance='lay'] .legs{{display:none}}",
            f"{r}[data-stance='kneel'] .lap,{r}[data-stance='lay'] .lap{{display:inline}}",
            f"{r}[data-stance='kneel'] .kfoot,{r}[data-stance='lay'] .kfoot{{display:inline}}",
            f"{r}[data-stance='kneel'] .lap,{r}[data-stance='lay'] .lap{{transform:translateY(-22px)}}",
            f"{r} .kleg{{display:none}}",
            # quỳ nhìn nghiêng: thay váy trải bằng đùi + cẳng chân gập thật (thấy rõ dáng quỳ)
            f"{r}[data-stance='kneel'][data-view='tq-r'] .kleg-r,{r}[data-stance='lay'][data-view='tq-r'] .kleg-r,"
            f"{r}[data-stance='kneel'][data-view='tq-l'] .kleg-l,{r}[data-stance='lay'][data-view='tq-l'] .kleg-l{{display:inline}}",
            f"{r}[data-stance='kneel'][data-view^='tq'] .lap,{r}[data-stance='lay'][data-view^='tq'] .lap,"
            f"{r}[data-stance='kneel'][data-view^='tq'] .kfoot,{r}[data-stance='lay'][data-view^='tq'] .kfoot{{display:none}}",  # váy trải sát đất, không tràn dưới sàn
            f"{r}[data-stance='kneel'] .body,{r}[data-stance='lay'] .body{{transform:translateY({KNEEL_DY}px)}}",
            # lạy: thân và tay dẹt lại (cúi rạp nhìn chính diện), đầu hạ xuống theo vai
            # thân trên (thân+tay+đầu) nghiêng quanh hông theo --lean (độ, do generator đặt khi với tay; mặc định 0)
            f"{r} .upper{{transform-box:view-box;transform-origin:{CX}px {HIP_Y}px;transform:rotate(calc(var(--lean,0) * 1deg))}}",
            f"{r} .trunk,{r} .arms{{transform-box:view-box;transform-origin:{CX}px 495px}}",
            f"{r}[data-stance='lay'] .trunk,{r}[data-stance='lay'] .arms{{transform:scaleY(.42)}}",
            f"{r}[data-stance='lay'] .headg{{transform:translateY(112px)}}",
        ]
        lines += [
            f"{r} .view{{transform-box:view-box;transform-origin:{CX}px 0px}}",
            f"{r} .feat,{r} .hair-front,{r} .bun-r,{r} .bun-l{{transform-box:view-box;transform-origin:{CX}px 215px}}",
        ]
        for view, d in (("tq-r", 1), ("tq-l", -1)):
            vs = f"{r}[data-view='{view}']"
            far_eye, far_ear = ("l", "l") if d > 0 else ("r", "r")  # mắt/tai phía mặt quay tới là phía "xa"
            lines += [
                f"{vs} .view{{transform:translateX({d * VIEW_BODY_DX}px) scaleX({VIEW_BODY_SX})}}",
                f"{vs} .feat{{transform:translateX({d * VIEW_FEAT_DX}px)}}",
                f"{vs} .hair-front{{transform:translateX({d * VIEW_HAIR_DX}px)}}",
                f"{vs} .bun-{'l' if d > 0 else 'r'}{{transform:scale({VIEW_FAR_EYE})}}",
                # nếp nhăn má/sẹo ở phía mặt quay tới bị dồn sát mép: kéo ngược một đoạn
                f"{vs} .chk-{'l' if d > 0 else 'r'},{vs} .scar-{'l' if d > 0 else 'r'}{{transform:translateX({-d * VIEW_CHEEK_BACK}px)}}",
                f"{vs} .eye-{far_eye}{{--exs:{VIEW_FAR_EYE}}}",
                f"{vs} .ear-{far_ear}{{display:none}}",
            ]
        # đổ người: quay quanh chân (loạng choạng → nghiêng → nằm). Đặt SAU luật view để thắng.
        lines += [
            f"{r}[data-stance='stagger'] .view{{transform-origin:{CX}px {FLOOR}px;transform:rotate(-12deg)}}",
            f"{r}[data-stance='tilt'] .view{{transform-origin:{CX}px {FLOOR}px;transform:translateX(115px) rotate(-42deg)}}",
            f"{r}[data-stance='lie'] .view{{transform-origin:{CX}px {LIE_PIVOT_Y}px;transform:translateY({LIE_DY}px) rotate(-90deg)}}",
            f"{r}[data-stance='stagger-r'] .view{{transform-origin:{CX}px {FLOOR}px;transform:rotate(12deg)}}",
            f"{r}[data-stance='tilt-r'] .view{{transform-origin:{CX}px {FLOOR}px;transform:translateX(-115px) rotate(42deg)}}",
            f"{r}[data-stance='lie-r'] .view{{transform-origin:{CX}px {LIE_PIVOT_Y}px;transform:translateY({LIE_DY}px) rotate(90deg)}}",
            f"{r}[data-stance='lie'] .lid,{r}[data-stance='lie-r'] .lid{{transform:scaleY(1)}}",
            f"{r}[data-stance='lie'] .tears,{r}[data-stance='lie-r'] .tears{{display:none}}",
            f"{r}[data-pose^='run'] .body{{transform-box:view-box;transform-origin:{CX}px {HIP_Y}px}}",
        ]
        for name, e in EMOTIONS.items():
            sel = f"{r}[data-emotion='{name}']"
            lines.append(
                f"{sel}{{--byl:{e['byl']};--byr:{e['byr']};--br:{e['br']};--lid:{e['lid']};--ps:{e['ps']};"
                f"--es:{e['es']};--shade:{e['shade']};--tear:{e['tear']};--mc:{e['mc']};--gx:{e['gx']}px}}"
            )
            lines.append(f"{sel}[data-mouth='auto'] .m-{e['mouth']}{{display:inline}}")
        for m in ("closed", "half", "open", "round"):
            lines.append(f"{r}[data-mouth='{m}'] .m-{m}{{display:inline}}")
        # blink phải thắng --lid của mọi cảm xúc: selector đặc hiệu hơn (2 thuộc tính) và đặt sau
        lines.append(f"{r}[data-blink='1'][data-emotion]{{--lid:1}}")
        for g, (gx, gy) in GAZE.items():
            if g != "center":
                lines.append(f"{r}[data-gaze='{g}']{{--gx:{gx}px;--gy:{gy}px}}")
        for name, ((ul, fl), (ur, fr)) in POSES.items():
            sel = f"{r}[data-pose='{name}']"
            # --ik-* (do generator đặt khi beat `reach`, xem ik.py) thắng góc của pose; không đặt thì dùng góc pose như cũ
            lines.append(f"{sel} .arm-l{{transform:rotate(calc(var(--ik-ul,{ul}) * 1deg))}}")
            lines.append(f"{sel} .fore-l{{transform:rotate(calc(var(--ik-fl,{fl}) * 1deg))}}")
            lines.append(f"{sel} .arm-r{{transform:rotate(calc(var(--ik-ur,{ur}) * 1deg))}}")
            lines.append(f"{sel} .fore-r{{transform:rotate(calc(var(--ik-fr,{fr}) * 1deg))}}")
        for name, (tl_, tr_) in LEG_POSES.items():
            sel = f"{r}[data-pose='{name}']"
            lines.append(f"{sel} .leg-l{{transform:{tl_}}}")
            lines.append(f"{sel} .leg-r{{transform:{tr_}}}")
        return "\n".join(lines)

    # ---- tổng hợp --------------------------------------------------------
    def inner(self, state: dict) -> str:
        s = self.scale
        attrs = {
            "data-emotion": state.get("emotion", "calm"),
            "data-mouth": state.get("mouth", "auto"),
            "data-pose": state.get("pose", "idle"),
            "data-stance": state.get("stance", "stand"),
            "data-gaze": state.get("gaze", "center"),
            "data-view": state.get("view", "front"),
            "data-blink": str(state.get("blink", 0)),
            "data-khan": state.get("khan", self.p.get("khan_default", "on")),
        }
        a = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        return (
            f'<g class="rig rig-{self.id}" {a}>'
            f'<ellipse class="floor-shadow" cx="{CX}" cy="578" rx="{self.body_w * 0.9:g}" ry="9" fill="#000" opacity="0.28"/>'
            f'<g class="scale" transform="translate({CX} {FLOOR}) scale({s:g}) translate({-CX} {-FLOOR})">'
            f'<g class="view">{self.kfeet()}<g class="body">{self.legs()}{self.lap()}{self.kleg()}<g class="upper"><g class="trunk">{self.torso()}</g>'
            f'<g class="arms">{self.arm("r")}{self.arm("l")}</g><g class="headg">{self.head()}</g></g></g></g>'
            f'</g></g>'
        )

    def svg(self, state: dict | None = None, viewbox: str | None = None, standalone: bool = True) -> str:
        vb = viewbox or f"0 0 {VB_W} {VB_H}"
        title_raw = f"{self.char.get('name', self.id)} ({self.id})"
        title = esc(title_raw)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{esc_attr(title_raw)}">'
            f'<title>{title}</title><style>{self.css()}</style>{self.inner(state or {})}</svg>'
        )


# ---- kiểm tràn khung & khớp script ----------------------------------------

def _rot(v: tuple[float, float], deg: float) -> tuple[float, float]:
    """Xoay như CSS rotate() trong hệ toạ độ SVG (y xuống)."""
    import math
    a = math.radians(deg)
    return (v[0] * math.cos(a) - v[1] * math.sin(a), v[0] * math.sin(a) + v[1] * math.cos(a))


def bounds_errors(rig: Rig) -> list[str]:
    """Kiểm giải tích (không render): tay ở mọi tư thế × stance, đầu/mũ/khăn, thân; có tính scale + sit.
    Không thay cho việc xem pose sheet — chỉ bắt lỗi tràn khung hiển nhiên."""
    errs: list[str] = []
    elbow = (0.0, ELBOW_Y - SHOULDER_Y)
    hand = (0.0, 462.0 - ELBOW_Y)
    hand_r = 15 + 2  # bán kính + nửa nét
    s = rig.scale

    def to_view(x: float, y: float) -> tuple[float, float]:
        return CX + (x - CX) * s, FLOOR - (FLOOR - y) * s

    def check(label: str, x0: float, y0: float, x1: float, y1: float) -> None:
        ax0, ay0 = to_view(x0, y0)
        ax1, ay1 = to_view(x1, y1)
        if ax0 < 0 or ay0 < 0 or ax1 > VB_W or ay1 > VB_H:
            errs.append(f"{rig.id}: {label} tràn viewBox {VB_W}x{VB_H} (x {ax0:.0f}..{ax1:.0f}, y {ay0:.0f}..{ay1:.0f})")

    for stance, dy in (("stand", 0.0), ("sit", 56.0)):
        for name, ((ul, fl), (ur, fr)) in POSES.items():
            for side, (u, f) in (("l", (ul, fl)), ("r", (ur, fr))):
                sx, sy = rig.shoulder(side)
                e = _rot(elbow, u)
                h = _rot((elbow[0] + _rot(hand, f)[0], elbow[1] + _rot(hand, f)[1]), u)
                for pt, rad in ((e, 18), (h, hand_r)):
                    x, y = sx + pt[0], sy + pt[1] + dy
                    check(f"tay {side} pose={name} stance={stance}", x - rad, y - rad, x + rad, y + rad)

    bw, p = rig.body_w, rig.p
    hunch = 14 * float(p.get("hunch", 0))
    top = 105.0 if (p.get("hat") or p.get("hair", "short") == "bun") else 144.0
    half = max(bw / 2 + 4, 70.0, 75.0 if p.get("hair") == "pigtails" else (62.5 if p.get("hair") == "bun" else 0))
    right = CX + (100.0 if p.get("headband") else half)
    # đầu bị dời xuống 14*hunch (head()), thân thì không → kiểm riêng để không báo tràn oan ở scale lớn
    check("đầu", CX - half, top + hunch, right, 330.0 + hunch)
    check("thân", CX - (bw / 2 + 4), 300.0, CX + (bw / 2 + 4), 590.0)
    return errs


def script_errors(rigs: list[Rig], script_path: Path) -> list[str]:
    """Nhân vật có rig phải có trong script.json và cùng giọng (nếu cả hai khai)."""
    sc = json.loads(script_path.read_text(encoding="utf-8-sig"))
    by_id = {c["id"]: c for c in sc.get("characters", [])}
    errs: list[str] = []
    for r in rigs:
        sc_char = by_id.get(r.id)
        if sc_char is None:
            errs.append(f"{r.id}: có rig trong bible nhưng không có trong {script_path.name}")
            continue
        bv, sv = r.char.get("voice"), sc_char.get("voice")
        if bv and sv and bv != sv:
            errs.append(f"{r.id}: giọng bible '{bv}' ≠ script '{sv}'")
    return errs


# ---- pose sheet -----------------------------------------------------------

def sheet_html(rig: Rig, emotions: list[str]) -> str:
    ch = rig.char
    cells_e = "".join(
        f'<figure>{rig.svg({"emotion": e}, rig.crop())}<figcaption>{e}</figcaption></figure>' for e in emotions
    )
    cells_m = "".join(
        f'<figure>{rig.svg({"emotion": "calm", "mouth": m}, rig.crop())}<figcaption>mouth: {m}</figcaption></figure>'
        for m in ("closed", "half", "open", "round")
    )
    cells_sit = "".join(
        f'<figure>{rig.svg({"emotion": e, "stance": "sit"}, rig.crop(y1=420))}<figcaption>sit · {e}</figcaption></figure>' for e in emotions
    )
    poses = [("idle", {}), ("clasp", {"emotion": "worried"}), ("point-l", {"emotion": "focused"}),
             ("reach-l", {"emotion": "afraid"}), ("raise-both", {"emotion": "shocked"}),
             ("walk-a", {"emotion": "focused"}), ("walk-b", {"emotion": "focused"}),
             ("sit", {"stance": "sit", "emotion": "calm"})]
    cells_p = "".join(
        f'<figure class="tall">{rig.svg({"pose": "idle" if n == "sit" else n, **st})}<figcaption>{n}</figcaption></figure>'
        for n, st in poses
    )
    cells_v = "".join(
        f'<figure class="tall">{rig.svg({"view": v})}<figcaption>view: {v}</figcaption></figure>' for v in VIEWS
    ) + "".join(
        f'<figure>{rig.svg({"view": v, "emotion": e, "mouth": m}, rig.crop())}<figcaption>{v} · {e} · {m}</figcaption></figure>'
        for v, e, m in (("tq-r", "calm", "closed"), ("tq-r", "worried", "open"), ("tq-l", "calm", "closed"), ("tq-l", "afraid", "open"))
    )
    acts = [("kneel · pray", {"stance": "kneel", "pose": "pray", "emotion": "grief"}),
            ("lay (lạy)", {"stance": "lay", "pose": "prostrate", "emotion": "grief"}),
            ("kneel · tq-r (nghiêng)", {"stance": "kneel", "pose": "pray", "emotion": "grief", "view": "tq-r"}),
            ("kneel · tq-l (nghiêng)", {"stance": "kneel", "pose": "pray", "emotion": "grief", "view": "tq-l"}),
            ("lay · tq-r (nghiêng)", {"stance": "lay", "pose": "prostrate", "emotion": "grief", "view": "tq-r"}),
            ("run-a", {"pose": "run-a", "emotion": "afraid"}), ("run-b", {"pose": "run-b", "emotion": "afraid"}),
            ("cover-head", {"pose": "cover-head", "emotion": "afraid"}),
            ("stagger", {"stance": "stagger", "emotion": "shocked", "pose": "raise-both"}),
            ("tilt", {"stance": "tilt", "emotion": "shocked", "pose": "raise-both"}),
            ("lie (ngất)", {"stance": "lie", "emotion": "calm"})]
    cells_a = "".join(f'<figure class="tall">{rig.svg(st)}<figcaption>{n}</figcaption></figure>' for n, st in acts)
    meta = f"{esc(ch.get('name', rig.id))} · giọng {esc(str(ch.get('voice', '?')))} · {esc(ch.get('design', ''))}"
    return f"""<!doctype html><html lang="vi"><meta charset="utf-8">
<style>
:root{{color-scheme:dark}}
body{{margin:0;padding:24px 28px 32px;background:#2a2018;color:#eadfce;font:14px/1.4 system-ui,sans-serif;width:1480px}}
h1{{font-size:20px;margin:0 0 4px}} .meta{{opacity:.75;margin-bottom:16px;max-width:1400px}}
h2{{font-size:13px;letter-spacing:.08em;text-transform:uppercase;opacity:.7;margin:20px 0 8px}}
.grid{{display:grid;grid-template-columns:repeat(6,230px);gap:10px 14px}}
figure{{margin:0;background:#3a2d22;border-radius:10px;padding:6px 6px 8px;text-align:center}}
figure svg{{width:218px;height:auto;display:block}}
figure.tall svg{{width:218px;height:436px}}
figcaption{{font-size:12px;opacity:.85;margin-top:2px}}
</style>
<h1>{esc(rig.id)} — pose sheet</h1><div class="meta">{meta}</div>
<h2>Biểu cảm ({len(emotions)})</h2><div class="grid">{cells_e}</div>
<h2>Biểu cảm khi ngồi ({len(emotions)})</h2><div class="grid">{cells_sit}</div>
<h2>Hình miệng</h2><div class="grid">{cells_m}</div>
<h2>Tư thế</h2><div class="grid">{cells_p}</div>
<h2>Góc nhìn 3/4 (view)</h2><div class="grid">{cells_v}</div>
<h2>Hành động: quỳ, lạy, chạy, ôm đầu, đổ người, ngất</h2><div class="grid">{cells_a}</div></html>"""


def lineup_html(rigs: list[Rig]) -> str:
    cells = "".join(
        f'<figure>{r.svg({})}<figcaption>{esc(r.char.get("name", r.id))}</figcaption></figure>' for r in rigs
    )
    return f"""<!doctype html><html lang="vi"><meta charset="utf-8">
<style>body{{margin:0;padding:20px;background:#2a2018;color:#eadfce;font:14px system-ui,sans-serif}}
.row{{display:flex;gap:12px;align-items:flex-end}} figure{{margin:0;text-align:center;background:#3a2d22;border-radius:10px;padding:8px}}
svg{{width:230px;height:460px;display:block}} figcaption{{font-size:13px}}</style>
<div class="row">{cells}</div></html>"""


def render_png(html_path: Path, png_path: Path, width: int) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": 800}, device_scale_factor=2)
        page.goto(html_path.resolve().as_uri())
        page.screenshot(path=str(png_path), full_page=True)
        browser.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Sinh rig SVG + pose sheet từ bible.json.")
    ap.add_argument("--bible", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True, help="thư mục xuất rig, ví dụ projects/<slug>/assets/rig")
    ap.add_argument("--library", type=Path, default=DEFAULT_LIBRARY, help="thư mục library dùng chung")
    ap.add_argument("--only", help="chỉ build các id này, cách nhau bằng dấu phẩy")
    ap.add_argument("--no-sheet", action="store_true")
    ap.add_argument("--script", type=Path, help="script.json để khớp id/giọng nhân vật (khuyến nghị)")
    ap.add_argument("--no-check", action="store_true", help="bỏ kiểm tràn khung và khớp script")
    args = ap.parse_args()

    bible = json.loads(args.bible.read_text(encoding="utf-8-sig"))
    style = bible.get("style", {})
    refs = style.get("palette_ref") or ["base"]
    palette = load_palette(args.library, refs, style.get("palette", {}))
    cat_file = args.library / "rigs" / "archetypes.json"
    catalog = json.loads(cat_file.read_text(encoding="utf-8")) if cat_file.exists() else {}
    vocab = bible.get("emotion_vocab") or list(EMOTIONS)
    unknown = [e for e in vocab if e not in EMOTIONS]
    if unknown:
        print(f"LỖI: emotion_vocab có giá trị rig chưa hỗ trợ: {unknown}", file=sys.stderr)
        return 1

    only = set(args.only.split(",")) if args.only else None
    try:
        chars = resolve_extends(bible.get("characters", []))
    except ValueError as e:
        print(f"LỖI: {e}", file=sys.stderr)
        return 1
    rigs = [Rig(c, palette, catalog) for c in chars if c.get("rig") and (not only or c["id"] in only)]
    if not rigs:
        print("Không có nhân vật nào có khối 'rig' trong bible.", file=sys.stderr)
        return 1

    checks: list[str] = []
    if not args.no_check:
        for rig in rigs:
            checks += bounds_errors(rig)
        if args.script:
            checks += script_errors(rigs, args.script)
        if checks:
            for e in checks:
                print(f"✗ {e}", file=sys.stderr)
            print(f"LỖI: {len(checks)} vấn đề — chưa ghi file. Sửa bible/script hoặc dùng --no-check.", file=sys.stderr)
            return 1

    args.out.mkdir(parents=True, exist_ok=True)
    sheets = args.out / "sheets"
    if not args.no_sheet:
        sheets.mkdir(exist_ok=True)

    report = []
    bad = False
    for rig in rigs:
        svg_path = args.out / Path(rig.p.get("file", f"{rig.id}.svg")).name
        svg_path.write_text(rig.svg({}), encoding="utf-8")
        if rig.missing:
            print(f"LỖI: {rig.id}: token màu không có trong palette {refs}: {sorted(rig.missing)}", file=sys.stderr)
            bad = True
        side = {
            "id": rig.id, "svg": svg_path.name, "viewBox": [0, 0, VB_W, VB_H],
            "floor": {"x": CX, "y": FLOOR}, "scale": rig.scale,
            "embed": "nested-svg-only", "pivots": rig.pivots(),
            "archetype": rig.p.get("archetype"), "outfit": rig.p.get("outfit"),
            "states": {
                "emotion": list(EMOTIONS), "mouth": ["auto", "closed", "half", "open", "round"],
                "pose": list(POSES), "stance": list(STANCES), "gaze": list(GAZE),
                "blink": [0, 1], "khan": ["on", "off"], "view": list(VIEWS),
            },
        }
        svg_path.with_suffix(".rig.json").write_text(json.dumps(side, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        entry = {"id": rig.id, "svg": str(svg_path), "bytes": svg_path.stat().st_size}
        if not args.no_sheet:
            html_path = sheets / f"{rig.id}.html"
            html_path.write_text(sheet_html(rig, vocab), encoding="utf-8")
            png = sheets / f"{rig.id}.png"
            render_png(html_path, png, 1480)
            html_path.unlink()
            entry["sheet"] = str(png)
        report.append(entry)
    if bad:
        return 1

    if not args.no_sheet:
        lp = sheets / "lineup.html"
        lp.write_text(lineup_html(rigs), encoding="utf-8")
        render_png(lp, sheets / "lineup.png", 258 * len(rigs) + 60)
        lp.unlink()

    print(json.dumps({"status": "ok", "palette": refs, "checked": not args.no_check, "script_matched": bool(args.script and not args.no_check), "rigs": report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
