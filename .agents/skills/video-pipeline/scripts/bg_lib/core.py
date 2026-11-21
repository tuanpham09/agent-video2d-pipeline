# -*- coding: utf-8 -*-
"""Primitive vẽ + khung SVG + CSS ánh sáng cho thư viện bối cảnh."""
from __future__ import annotations

W, H = 1920, 1080
HORIZON = 640
INK = "#1a120c"
LIGHTS_EXT = ["day", "dusk", "night", "dark", "red_flash"]
LIGHTS_INT = ["day", "candle_warm", "dark", "red_flash"]

P = dict(
    sky_top="#9fb7c4", sky_bot="#e8dcc4", ground="#6b5a3f", ground2="#54452f", grass="#5d6b3a", grass2="#46532c",
    wood="#6a4a2f", wood_d="#4a3220", wood_l="#8a6440", wall="#cdbf9f", wall_d="#a89a7b", roof="#5a3a2a",
    roof_d="#3e281c", tile="#7a4a38", stone="#8c8c84", stone_d="#66665f", leaf="#456b34", leaf_d="#2f4d26",
    leaf_l="#6c8e44", bamboo="#7a8f3a", bamboo_d="#566a27", water="#6f9aa5", water_d="#4e7580", mount="#6c7e86",
    mount_far="#9aabb0", red="#a23a2a", gold="#c9a24a", white="#efe9dc", black="#0d0a08", fog="#d9e0dc",
    floor="#7b5c3c", floor_d="#5c432b", cloth="#d8d0bd",
)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x, y, w, h, fill, sw=4, rx=0, stroke=INK, extra=""):
    return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def poly(pts, fill, sw=4, stroke=INK, extra=""):
    d = "M " + " L ".join(f"{x:g} {y:g}" for x, y in pts) + " Z"
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" {extra}/>'


def path(d, fill="none", sw=4, stroke=INK, extra=""):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" {extra}/>'


def ell(cx, cy, rx, ry, fill, sw=4, stroke=INK, extra=""):
    return f'<ellipse cx="{cx:g}" cy="{cy:g}" rx="{rx:g}" ry="{ry:g}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>'


def circ(cx, cy, r, fill, sw=4, stroke=INK, extra=""):
    return ell(cx, cy, r, r, fill, sw, stroke, extra)


def line(x1, y1, x2, y2, sw=4, stroke=INK, extra=""):
    return f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" {extra}/>'


def g(*parts, cls="", extra=""):
    c = f' class="{cls}"' if cls else ""
    return f"<g{c} {extra}>" + "".join(parts) + "</g>"


# ---- khối dùng chung ----------------------------------------------------------

def sky(top=None, bot=None):
    return (f'<rect class="sky" x="0" y="0" width="{W}" height="{H}" fill="url(#skyg)"/>')


def ground(y=HORIZON, color=None, h=None):
    return f'<rect x="0" y="{y}" width="{W}" height="{H - y}" fill="{color or P["ground"]}"/>'


def hills(y, color, amp=60, seed=0, step=240):
    pts = [(0, H)]
    x = -step
    i = seed
    while x <= W + step:
        pts.append((x, y - amp * (0.5 + 0.5 * ((i * 37) % 7) / 6)))
        x += step
        i += 1
    pts.append((W, H))
    d = "M " + " ".join(f"{x:g} {yy:g}" for x, yy in pts[:1])
    d = f"M 0 {H} L " + " L ".join(f"{x:g} {yy:g}" for x, yy in pts[1:-1]) + f" L {W} {H} Z"
    return f'<path d="{d}" fill="{color}" stroke="none"/>'


def mountain(pts, color, snow=False):
    return poly(pts, color, sw=3)


def tree(x, base, h, trunk=None, leaf=None, w=None):
    w = w or h * 0.12
    trunk = trunk or P["wood_d"]
    leaf = leaf or P["leaf"]
    return g(
        poly([(x - w / 2, base), (x - w / 3, base - h * 0.55), (x + w / 3, base - h * 0.55), (x + w / 2, base)], trunk, 4),
        circ(x, base - h * 0.72, h * 0.3, leaf, 4), circ(x - h * 0.2, base - h * 0.6, h * 0.2, P["leaf_d"], 4),
        circ(x + h * 0.2, base - h * 0.62, h * 0.22, P["leaf_l"], 4),
    )


def banyan(x, base, h):
    """Cây đa: thân to, tán rộng, rễ phụ rủ."""
    parts = [poly([(x - 60, base), (x - 36, base - h * 0.5), (x + 36, base - h * 0.5), (x + 60, base)], P["wood_d"], 5)]
    for dx in (-110, -70, 70, 110):
        parts.append(path(f"M {x + dx * .5:g} {base - h * .5:g} q {dx * .3:g} {h * .3:g} {dx * .2:g} {h * .5:g}", sw=7, stroke=P["wood"]))
    for cx, cy, r in ((x - 150, base - h * .75, h * .24), (x + 150, base - h * .75, h * .24), (x, base - h * .9, h * .3), (x - 60, base - h * .68, h * .2), (x + 70, base - h * .66, h * .21)):
        parts.append(circ(cx, cy, r, P["leaf"], 5))
    parts.append(circ(x - 40, base - h * .95, h * .16, P["leaf_l"], 4))
    return g(*parts)


def bamboo_clump(x, base, h, n=7):
    parts = []
    for i in range(n):
        dx = (i - n / 2) * 26
        hh = h * (0.75 + 0.25 * ((i * 53) % 5) / 4)
        sway = (i % 3 - 1) * 14
        parts.append(path(f"M {x + dx:g} {base:g} Q {x + dx + sway:g} {base - hh / 2:g} {x + dx + sway * 2:g} {base - hh:g}", sw=14, stroke=P["bamboo_d"]))
        parts.append(path(f"M {x + dx:g} {base:g} Q {x + dx + sway:g} {base - hh / 2:g} {x + dx + sway * 2:g} {base - hh:g}", sw=8, stroke=P["bamboo"]))
        for k in range(1, 5):
            yy = base - hh * k / 5
            parts.append(line(x + dx + sway * k / 5 * 1.8 - 8, yy, x + dx + sway * k / 5 * 1.8 + 8, yy, 3))
        parts.append(path(f"M {x + dx + sway * 2:g} {base - hh:g} q 40 -10 60 20 M {x + dx + sway * 2:g} {base - hh:g} q -40 -6 -58 24", sw=6, stroke=P["leaf"]))
    return g(*parts)


def banana(x, base, h):
    parts = [path(f"M {x:g} {base:g} L {x:g} {base - h:g}", sw=16, stroke=P["leaf_d"])]
    for a in (-70, -35, 0, 35, 70):
        ex, ey = x + a * 2.2, base - h + abs(a) * .5 + 20
        parts.append(poly([(x, base - h), (ex - 18, ey - 36), (ex + 30, ey), (ex - 10, ey + 50)], P["leaf_l"], 4))
    return g(*parts)


def grass_tufts(y0, y1, n, color=None, seed=1):
    parts = []
    for i in range(n):
        x = (i * 197 + seed * 53) % W
        y = y0 + ((i * 89 + seed * 31) % max(1, int(y1 - y0)))
        parts.append(path(f"M {x} {y} l -6 -16 M {x} {y} l 0 -20 M {x} {y} l 6 -16", sw=3, stroke=color or P["grass2"]))
    return g(*parts)


def tomb(x, base, s=1.0, tall=False):
    w, h = 70 * s, (120 if tall else 80) * s
    return g(
        rect(x - w / 2 - 12 * s, base - 20 * s, w + 24 * s, 20 * s, P["stone_d"], 4),
        path(f"M {x - w / 2:g} {base - 20 * s:g} L {x - w / 2:g} {base - h:g} Q {x:g} {base - h - 36 * s:g} {x + w / 2:g} {base - h:g} L {x + w / 2:g} {base - 20 * s:g} Z", P["stone"], 5),
        line(x, base - h + 10 * s, x, base - h + 40 * s, 4, P["stone_d"]), line(x - 14 * s, base - h + 24 * s, x + 14 * s, base - h + 24 * s, 4, P["stone_d"]),
    )


def house(x, base, w, h, roof_h=None, wall=None, roof=None, door=True, window=True, thatch=False):
    """Nhà mặt trước: tường + mái hình thang/dốc."""
    roof_h = roof_h or h * .5
    wall = wall or P["wall"]
    roof = roof or (P["wood_l"] if thatch else P["tile"])
    parts = [rect(x - w / 2, base - h, w, h, wall, 5)]
    parts.append(poly([(x - w / 2 - 30, base - h + 6), (x - w * .36, base - h - roof_h), (x + w * .36, base - h - roof_h), (x + w / 2 + 30, base - h + 6)], roof, 5))
    for i in range(1, 5):
        yy = base - h + 6 - roof_h * i / 5
        parts.append(line(x - w / 2 - 30 + (w * .14 + 30) * i / 5, yy, x + w / 2 + 30 - (w * .14 + 30) * i / 5, yy, 2.5, P["roof_d"]))
    if door:
        parts.append(rect(x - w * .11, base - h * .62, w * .22, h * .62, P["wood_d"], 4))
    if window:
        for dx in (-w * .34, w * .34):
            parts.append(rect(x + dx - w * .07, base - h * .68, w * .14, h * .3, P["wood_d"], 4))
            parts.append(line(x + dx, base - h * .68, x + dx, base - h * .38, 3, P["wood_l"]))
    return g(*parts)


def fence(x0, x1, base, h=70, color=None):
    parts = []
    x = x0
    while x <= x1:
        parts.append(line(x, base, x, base - h, 6, color or P["wood_d"]))
        x += 46
    parts.append(line(x0, base - h * .7, x1, base - h * .7, 5, color or P["wood_d"]))
    parts.append(line(x0, base - h * .3, x1, base - h * .3, 5, color or P["wood_d"]))
    return g(*parts)


def smoke(x, y):
    return path(f"M {x} {y} q 20 -30 0 -60 q -20 -30 10 -70", sw=14, stroke=P["fog"], extra='opacity="0.5"')


def fog_band(y, h=120, op=0.35):
    return f'<rect x="0" y="{y}" width="{W}" height="{h}" fill="url(#fogg)" opacity="{op}"/>'


def vignette():
    return f'<rect x="0" y="0" width="{W}" height="{H}" fill="url(#vig)"/>'


# ---- khung SVG ----------------------------------------------------------------

CSS = """
.tint{fill:var(--t,#000);opacity:var(--a,0);mix-blend-mode:multiply}
.glow,.moon,.lamp{display:none}
svg[data-light='day']{--a:0}
svg[data-light='dusk']{--t:#ff9a55;--a:.38}
svg[data-light='night']{--t:#1a2650;--a:.74}
svg[data-light='night'] .moon,svg[data-light='dark'] .moon{display:inline}
svg[data-light='dark']{--t:#080a12;--a:.8}
svg[data-light='candle_warm']{--t:#2a160c;--a:.58}
svg[data-light='candle_warm'] .glow,svg[data-light='dusk'] .lamp,svg[data-light='night'] .lamp{display:inline}
svg[data-light='red_flash']{--t:#ff2a1a;--a:.58}
/* chiều sâu: xa nhạt/mờ sương, gần chìm vào bóng tối */
svg[data-light='night'] .layer.near,svg[data-light='candle_warm'] .layer.near{filter:brightness(.72)}
svg[data-light='night'] .layer.far{filter:brightness(1.12) saturate(.75)}
svg[data-light='dark'] .layer.near{filter:brightness(.5)}
svg[data-light='dark'] .layer.far{filter:brightness(1.2) saturate(.6)}
/* vùng sáng: tối dần ra xa nguồn sáng */
.pool,.pool2,.mist,.grain,.vig2,.creep{display:none}
svg[data-light='candle_warm'] .pool{display:inline}
svg[data-light='night'] .pool2,svg[data-light='dark'] .pool2,svg[data-light='dusk'] .pool2{display:inline}
/* mood rợn */
svg[data-mood='creepy'] .creep,svg[data-mood='creepy'] .mist,svg[data-mood='creepy'] .vig2{display:inline}
svg[data-mood='creepy'] .grain{display:inline;opacity:.16;mix-blend-mode:overlay}
svg[data-mood='creepy'][data-light='day']{--t:#8d9a94;--a:.34}
svg[data-mood='creepy'][data-light='dusk']{--t:#c9764a;--a:.5}
svg[data-mood='creepy'][data-light='night']{--t:#141f3a;--a:.8}
"""


def wrap_svg(bid: str, spec: dict, layers: dict, light: str | None = None, mood: str = "normal") -> str:
    kind = spec["kind"]
    default = light or ("day" if kind == "exterior" else "day")
    fx, fy = spec.get("focus", [960, 700])
    defs = (
        '<defs>'
        '<linearGradient id="skyg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
        '<linearGradient id="fogg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="%s"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
        '<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".45"/></radialGradient>'
        '<radialGradient id="glowg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffd27a" stop-opacity=".95"/><stop offset=".45" stop-color="#ff9a3a" stop-opacity=".45"/><stop offset="1" stop-color="#ff7a1a" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="poolg" gradientUnits="userSpaceOnUse" cx="%d" cy="%d" r="880"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset=".3" stop-color="#000" stop-opacity=".12"/><stop offset="1" stop-color="#000" stop-opacity=".72"/></radialGradient>'
        '<radialGradient id="poolg2" gradientUnits="userSpaceOnUse" cx="%d" cy="%d" r="900"><stop offset="0" stop-color="#000" stop-opacity="0"/><stop offset=".25" stop-color="#000" stop-opacity=".1"/><stop offset="1" stop-color="#000" stop-opacity=".6"/></radialGradient>'
        '<radialGradient id="vig2g" cx=".5" cy=".5" r=".7"><stop offset=".35" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".8"/></radialGradient>'
        '<filter id="grainf" x="0" y="0" width="100%%" height="100%%"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="7"/><feColorMatrix type="saturate" values="0"/></filter>'
        '</defs>'
    ) % (spec.get("sky", (P["sky_top"], P["sky_bot"]))[0], spec.get("sky", (P["sky_top"], P["sky_bot"]))[1], P["fog"],
      fx, fy, spec.get("lamp", (fx, fy))[0], spec.get("lamp", (fx, fy))[1])
    creep = spec.get("creep_layers") or {}
    far = layers.get("far", "") + (f'<g class="creep">{creep["far"]}</g>' if creep.get("far") else "")
    mid = layers.get("mid", "") + (f'<g class="creep">{creep["mid"]}</g>' if creep.get("mid") else "")
    near = layers.get("near", "") + (f'<g class="creep">{creep["near"]}</g>' if creep.get("near") else "")
    mist = (f'<g class="mist"><rect x="0" y="{HORIZON - 60}" width="{W}" height="200" fill="url(#fogg)" opacity=".5"/>'
            f'<rect x="0" y="{HORIZON + 140}" width="{W}" height="240" fill="url(#fogg)" opacity=".38"/></g>')
    pools = (f'<rect class="pool" x="0" y="0" width="{W}" height="{H}" fill="url(#poolg)"/>'
             f'<rect class="pool2" x="0" y="0" width="{W}" height="{H}" fill="url(#poolg2)"/>')
    grain = f'<rect class="grain" x="0" y="0" width="{W}" height="{H}" filter="url(#grainf)"/>'
    vig2 = f'<rect class="vig2" x="0" y="0" width="{W}" height="{H}" fill="url(#vig2g)"/>'
    moon = f'<g class="moon"><circle cx="{spec.get("moon", (1500, 170))[0]}" cy="{spec.get("moon", (1500, 170))[1]}" r="70" fill="#f1ecd8" stroke="none"/></g>' if kind == "exterior" else ""
    glow = f'<g class="glow"><circle cx="{fx}" cy="{fy}" r="460" fill="url(#glowg)" style="mix-blend-mode:screen"/></g>'
    lamp = f'<g class="lamp"><circle cx="{spec.get("lamp", (fx, fy))[0]}" cy="{spec.get("lamp", (fx, fy))[1]}" r="170" fill="url(#glowg)" style="mix-blend-mode:screen"/></g>' if (kind == "exterior" and "lamp" in spec) else ""
    title = esc(f"{spec['name']} ({bid})")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" data-light="{default}" data-mood="{mood}" role="img" aria-label="{title}">'
        f'<title>{title}</title><style>{CSS}</style>{defs}'
        f'<g class="layer far">{far}</g>{moon}'
        f'<g class="layer mid">{mid}</g>'
        f'<g class="layer near">{near}</g>'
        f'{mist if kind == "exterior" else ""}'
        f'<rect class="tint" x="0" y="0" width="{W}" height="{H}"/>{pools}{glow}{lamp}{vignette()}{vig2}{grain}'
        f'</svg>'
    )
