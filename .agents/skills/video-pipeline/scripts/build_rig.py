#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh rig SVG nhân vật + pose sheet từ script/bible.json.

Mỗi nhân vật trong bible có khối "rig" (tham số), màu lấy từ style.palette.
Một rig = một file SVG tự chứa, nhóm có tên + CSS điều khiển bằng thuộc tính:

  <g class="rig rig-<id>" data-emotion="calm" data-mouth="auto" data-pose="idle"
                          data-stance="stand" data-gaze="center" data-blink="0" data-khan="on">

  data-emotion  emotion_vocab của bible (calm, focused, worried, afraid, shocked,
                dread, sad, grief, angry, suspicious, relieved)
  data-mouth    auto | closed | half | open | round   (auto = theo cảm xúc)
  data-pose     idle | clasp | point-l | reach-l | raise-both
  data-stance   stand | sit
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
  thêm --no-sheet để bỏ pose sheet (cần playwright + chromium).
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

# brow rot: dương = đầu mày phía trong nhướn lên; mc: >0 cười, <0 mếu
EMOTIONS = {
    "calm": dict(byl=0, byr=0, br=0, lid=0.0, ps=1.0, es=1.0, shade=0.0, tear=0, mouth="closed", mc=0.9, gx=0),
    "focused": dict(byl=2, byr=2, br=-7, lid=0.18, ps=1.0, es=1.0, shade=0.0, tear=0, mouth="closed", mc=0.15, gx=0),
    "worried": dict(byl=-3, byr=-3, br=14, lid=0.08, ps=0.95, es=1.0, shade=0.0, tear=0, mouth="closed", mc=-0.9, gx=0),
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
}

GAZE = {"center": (0, 0), "left": (-5, 0), "right": (5, 0), "up": (0, -4), "down": (0, 4)}

DEFAULT_PALETTE = {
    "skin": "#cf9063", "skin_old": "#c48a5d", "ink": "#1f140b", "eye_white": "#fffdf7",
    "pupil": "#1b120c", "mouth_dark": "#4a1a14", "shoe": "#120d09",
    "hair_black": "#1b120c", "hair_white": "#eae4db", "brow_white": "#8d857a",
    "robe_mourning": "#e6e0d3", "robe_mourning_dark": "#cfc8b8",
    "robe_brown": "#584333", "robe_brown_dark": "#483424",
    "robe_indigo": "#2b2f45", "robe_indigo_dark": "#20233a", "khan_white": "#f4f1ea",
    "scar": "#e6b99a", "cloud": "#c9d6d8", "shadow_body": "#07070a", "shadow_ink": "#000000",
    "shadow_eye": "#ffffff", "shadow_pupil": "#d01010", "shadow_line": "#e8e4db",
}


def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


class Rig:
    """Một nhân vật + palette đã giải quyết."""

    def __init__(self, char: dict, palette: dict):
        self.char = char
        self.id = char["id"]
        p = dict(char["rig"])
        self.p = p
        self.pal = {**DEFAULT_PALETTE, **palette}
        self.shadow = bool(p.get("shadow"))

    def c(self, key: str | None, fallback: str = "ink") -> str:
        if key is None:
            return "none"
        return self.pal.get(key, key if key.startswith("#") else self.pal[fallback])

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
        x0 = CX - 90 if x0 is None else x0
        x1 = CX + 90 if x1 is None else x1
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
        for x in (CX - 36, CX + 12):
            out.append(f'<rect x="{x}" y="470" width="24" height="98" rx="10" fill="{pants}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<ellipse cx="{x + 12}" cy="572" rx="23" ry="11" fill="{shoe}" stroke="{ink}" stroke-width="3"/>')
        out.append("</g>")
        return "".join(out)

    def lap(self) -> str:
        ink = self.c("shadow_ink" if self.shadow else "ink")
        col = self.c("shadow_body" if self.shadow else self.p.get("pants", "robe_mourning_dark"))
        return (f'<ellipse class="lap" cx="{CX}" cy="500" rx="{self.body_w * 0.95:g}" ry="30" '
                f'fill="{col}" stroke="{ink}" stroke-width="6"/>')

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
        out = [f'<g class="head" transform="translate(0 {hy:g})">']

        hair_style = p.get("hair", "short")
        hat = p.get("hat")
        if hair_style in ("bun",) and not hat:
            out.append(f'<ellipse cx="{CX}" cy="205" rx="62" ry="66" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
            out.append(f'<circle class="bun" cx="{CX}" cy="132" r="24" fill="{hair}" stroke="{ink}" stroke-width="5"/>')
        # tai
        for dx in (-58, 58):
            out.append(f'<circle cx="{CX + dx}" cy="226" r="10" fill="{skin}" stroke="{ink}" stroke-width="4"/>')
        # mặt
        out.append(f'<ellipse class="face" cx="{CX}" cy="215" rx="58" ry="62" fill="{skin}" stroke="{ink}" stroke-width="6"/>')
        # tóc trước
        if hair_style in ("short", "bun") and not hat:
            out.append(
                f'<path class="hair-front" d="M {CX - 60} 206 Q {CX - 64} 148 {CX} 146 Q {CX + 64} 148 {CX + 60} 206 '
                f'Q {CX + 42} 176 {CX} 174 Q {CX - 42} 176 {CX - 60} 206 Z" fill="{hair}" stroke="{ink}" stroke-width="5" stroke-linejoin="round"/>')
        # nếp nhăn
        wr = int(p.get("wrinkles", 0))
        if wr >= 1:
            w = f'stroke="{ink}" stroke-width="2.6" stroke-linecap="round" fill="none" opacity="0.5"'
            out.append(f'<path d="M {CX - 30} 190 Q {CX} 184 {CX + 30} 190" {w}/>')
            out.append(f'<path d="M {CX - 52} 232 l 8 3 M {CX - 52} 241 l 8 -2 M {CX + 52} 232 l -8 3 M {CX + 52} 241 l -8 -2" {w}/>')
        if wr >= 2:
            out.append(f'<path d="M {CX - 26} 178 Q {CX} 172 {CX + 26} 178 M {CX - 32} 248 Q {CX - 26} 262 {CX - 18} 268 M {CX + 32} 248 Q {CX + 26} 262 {CX + 18} 268" {w}/>')
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
            out.append(f'<path class="scar" d="M {sx - 4} 190 L {sx + 6} 206" stroke="{self.c("scar")}" stroke-width="3.4" stroke-linecap="round"/>')
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
                       f'fill="{self.c("hair_white")}" stroke="{ink}" stroke-width="4" stroke-linejoin="round"/>')
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
            f"{r} .eye{{transform:scale(var(--es,1))}}",
            f"{r} .pupil{{transform:translate(var(--gx,0px),var(--gy,0px)) scale(var(--ps,1))}}",
            f"{r} .brow-r{{transform:translateY(calc(var(--byr,0) * 1px)) rotate(calc(var(--br,0) * -1deg))}}",
            f"{r} .brow-l{{transform:translateY(calc(var(--byl,0) * 1px)) rotate(calc(var(--br,0) * 1deg))}}",
            f"{r} .shade{{opacity:var(--shade,0)}}",
            f"{r} .tears{{opacity:var(--tear,0)}}",
            f"{r} .m-closed{{transform:scaleY(var(--mc,.9))}}",
            f"{r} .mouth>*{{display:none}}",
            f"{r}[data-blink='1']{{--lid:1}}",
            f"{r}[data-khan='off'] .acc-khan{{display:none}}",
            f"{r} .lap{{display:none}}",
            f"{r}[data-stance='sit'] .lap{{display:inline}}",
            f"{r}[data-stance='sit'] .legs{{display:none}}",
            f"{r}[data-stance='sit'] .body{{transform:translateY(56px)}}",
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
        for g, (gx, gy) in GAZE.items():
            if g != "center":
                lines.append(f"{r}[data-gaze='{g}']{{--gx:{gx}px;--gy:{gy}px}}")
        for name, ((ul, fl), (ur, fr)) in POSES.items():
            sel = f"{r}[data-pose='{name}']"
            lines.append(f"{sel} .arm-l{{transform:rotate({ul}deg)}}")
            lines.append(f"{sel} .fore-l{{transform:rotate({fl}deg)}}")
            lines.append(f"{sel} .arm-r{{transform:rotate({ur}deg)}}")
            lines.append(f"{sel} .fore-r{{transform:rotate({fr}deg)}}")
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
            "data-blink": str(state.get("blink", 0)),
            "data-khan": state.get("khan", self.p.get("khan_default", "on")),
        }
        a = " ".join(f'{k}="{v}"' for k, v in attrs.items())
        return (
            f'<g class="rig rig-{self.id}" {a}>'
            f'<ellipse class="floor-shadow" cx="{CX}" cy="578" rx="{self.body_w * 0.9:g}" ry="9" fill="#000" opacity="0.28"/>'
            f'<g class="scale" transform="translate({CX} {FLOOR}) scale({s:g}) translate({-CX} {-FLOOR})">'
            f'<g class="body">{self.legs()}{self.lap()}{self.torso()}{self.arm("r")}{self.arm("l")}{self.head()}</g>'
            f'</g></g>'
        )

    def svg(self, state: dict | None = None, viewbox: str | None = None, standalone: bool = True) -> str:
        vb = viewbox or f"0 0 {VB_W} {VB_H}"
        title = esc(f"{self.char.get('name', self.id)} ({self.id})")
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" role="img" aria-label="{title}">'
            f'<title>{title}</title><style>{self.css()}</style>{self.inner(state or {})}</svg>'
        )


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
    poses = [("idle", {}), ("clasp", {"emotion": "worried"}), ("point-l", {"emotion": "focused"}),
             ("reach-l", {"emotion": "afraid"}), ("raise-both", {"emotion": "shocked"}),
             ("sit", {"stance": "sit", "emotion": "calm"})]
    cells_p = "".join(
        f'<figure class="tall">{rig.svg({"pose": "idle" if n == "sit" else n, **st})}<figcaption>{n}</figcaption></figure>'
        for n, st in poses
    )
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
<h2>Hình miệng</h2><div class="grid">{cells_m}</div>
<h2>Tư thế</h2><div class="grid">{cells_p}</div></html>"""


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
    ap.add_argument("--only", help="chỉ build các id này, cách nhau bằng dấu phẩy")
    ap.add_argument("--no-sheet", action="store_true")
    args = ap.parse_args()

    bible = json.loads(args.bible.read_text(encoding="utf-8-sig"))
    palette = bible.get("style", {}).get("palette", {})
    vocab = bible.get("emotion_vocab") or list(EMOTIONS)
    unknown = [e for e in vocab if e not in EMOTIONS]
    if unknown:
        print(f"LỖI: emotion_vocab có giá trị rig chưa hỗ trợ: {unknown}", file=sys.stderr)
        return 1

    only = set(args.only.split(",")) if args.only else None
    rigs = [Rig(c, palette) for c in bible.get("characters", []) if c.get("rig") and (not only or c["id"] in only)]
    if not rigs:
        print("Không có nhân vật nào có khối 'rig' trong bible.", file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    sheets = args.out / "sheets"
    if not args.no_sheet:
        sheets.mkdir(exist_ok=True)

    report = []
    for rig in rigs:
        svg_path = args.out / Path(rig.p.get("file", f"{rig.id}.svg")).name
        svg_path.write_text(rig.svg({}), encoding="utf-8")
        entry = {"id": rig.id, "svg": str(svg_path), "bytes": svg_path.stat().st_size}
        if not args.no_sheet:
            html_path = sheets / f"{rig.id}.html"
            html_path.write_text(sheet_html(rig, vocab), encoding="utf-8")
            png = sheets / f"{rig.id}.png"
            render_png(html_path, png, 1480)
            html_path.unlink()
            entry["sheet"] = str(png)
        report.append(entry)

    if not args.no_sheet:
        lp = sheets / "lineup.html"
        lp.write_text(lineup_html(rigs), encoding="utf-8")
        render_png(lp, sheets / "lineup.png", 258 * len(rigs) + 60)
        lp.unlink()

    print(json.dumps({"status": "ok", "rigs": report}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
