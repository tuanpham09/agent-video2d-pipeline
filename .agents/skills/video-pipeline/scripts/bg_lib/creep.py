# -*- coding: utf-8 -*-
"""Lớp chi tiết rợn (.creep) bật/tắt bằng data-mood="creepy". CREEP[id]() -> {far, mid, near}.
Mỗi chi tiết là hàm nhỏ dùng lại được; thêm cảnh mới = thêm 1 dòng vào CREEP."""
from __future__ import annotations

from .core import *  # noqa: F401,F403
from .core import P, W, H, INK

CREEP: dict = {}
PALE = "#e9e4d6"
EYE = "#fff3a8"


def crow(x, y, s=1.0, flip=False):
    f = -1 if flip else 1
    return path(f"M {x} {y} q {18 * s * f:g} {-16 * s:g} {40 * s * f:g} {-4 * s:g} q {-10 * s * f:g} {4 * s:g} {-16 * s * f:g} {14 * s:g} q {-14 * s * f:g} {-10 * s:g} {-24 * s * f:g} {-10 * s:g} Z", INK, 3, INK)


def flock(x, y, n=5, s=1.0):
    return g(*[crow(x + i * 46 * s, y + ((i * 37) % 5 - 2) * 14 * s, s * (0.8 + (i % 3) * .15), i % 2 == 1) for i in range(n)])


def figure(x, base, s=1.0, color="#0b0a0c", eyes=True, long_hair=False, op=1.0):
    """Bóng người đứng, đầu hơi nghiêng; mắt trắng nhỏ."""
    parts = [
        poly([(x - 34 * s, base), (x - 26 * s, base - 150 * s), (x + 26 * s, base - 150 * s), (x + 34 * s, base)], color, 0, color),
        circ(x, base - 176 * s, 24 * s, color, 0, color),
        path(f"M {x - 26 * s:g} {base - 148 * s:g} q {-20 * s:g} {70 * s:g} {-10 * s:g} {130 * s:g} M {x + 26 * s:g} {base - 148 * s:g} q {20 * s:g} {70 * s:g} {10 * s:g} {130 * s:g}", "none", 14 * s, color),
    ]
    if long_hair:
        parts.append(path(f"M {x - 22 * s:g} {base - 190 * s:g} q {-26 * s:g} {90 * s:g} {-8 * s:g} {170 * s:g} M {x + 22 * s:g} {base - 190 * s:g} q {26 * s:g} {90 * s:g} {8 * s:g} {170 * s:g}", "none", 12 * s, color))
    if eyes:
        parts.append(ell(x - 8 * s, base - 178 * s, 3.4 * s, 4.6 * s, EYE, 0, EYE) + ell(x + 8 * s, base - 178 * s, 3.4 * s, 4.6 * s, EYE, 0, EYE))
    return g(*parts, extra=f'opacity="{op}"')


def ghost(x, base, s=1.0, op=.85):
    """Hồn trắng váy dài, tóc rủ, không chân."""
    return g(
        path(f"M {x - 40 * s:g} {base:g} q {-6 * s:g} {-120 * s:g} {10 * s:g} {-160 * s:g} h {60 * s:g} q {16 * s:g} {40 * s:g} {10 * s:g} {160 * s:g} q {-20 * s:g} {-16 * s:g} {-30 * s:g} {0} q {-20 * s:g} {16 * s:g} {-40 * s:g} {0} Z", PALE, 2, "#9a9488"),
        circ(x, base - 180 * s, 24 * s, PALE, 2, "#9a9488"),
        path(f"M {x - 22 * s:g} {base - 195 * s:g} q {-24 * s:g} {110 * s:g} {-6 * s:g} {190 * s:g} M {x + 22 * s:g} {base - 195 * s:g} q {24 * s:g} {110 * s:g} {6 * s:g} {190 * s:g} M {x} {base - 204 * s:g} q {2 * s:g} {80 * s:g} {0} {160 * s:g}", "none", 7 * s, "#0b0a0c"),
        ell(x - 8 * s, base - 178 * s, 3 * s, 7 * s, "#0b0a0c", 0, "#0b0a0c") + ell(x + 8 * s, base - 178 * s, 3 * s, 7 * s, "#0b0a0c", 0, "#0b0a0c"),
        extra=f'opacity="{op}"',
    )


def dead_tree(x, base, h, flip=False):
    f = -1 if flip else 1
    d = f"M {x} {base} q {-8 * f:g} {-h * .4:g} {10 * f:g} {-h * .7:g} q {14 * f:g} {-h * .15:g} {-4 * f:g} {-h:g}"
    br = ""
    for k, (a, b, c) in enumerate(((.45, 90, -50), (.62, -110, -70), (.78, 80, -90), (.88, -60, -60))):
        y = base - h * a
        br += path(f"M {x + 6 * f:g} {y:g} q {a * 40 * f:g} {c:g} {b * f:g} {c * 1.6:g} m {-b * .5 * f:g} {c * .8:g} l {30 * f:g} {-24:g}", "none", 7 - k, INK)
    return g(path(d, "none", 22, INK), path(d, "none", 12, "#2a2018"), br)


def cobweb(x, y, s=1.0, flipx=False, flipy=False):
    fx, fy = (-1 if flipx else 1), (-1 if flipy else 1)
    parts = [line(x, y, x + 150 * s * fx, y + 6 * s * fy, 2, "#cfcabd"), line(x, y, x + 110 * s * fx, y + 110 * s * fy, 2, "#cfcabd"), line(x, y, x + 6 * s * fx, y + 150 * s * fy, 2, "#cfcabd")]
    for r in (40, 80, 120):
        parts.append(path(f"M {x + r * s * fx:g} {y + 2 * s * fy:g} Q {x + r * .55 * s * fx:g} {y + r * .55 * s * fy:g} {x + 2 * s * fx:g} {y + r * s * fy:g}", "none", 1.8, "#cfcabd"))
    return g(*parts, extra='opacity=".75"')


def eyes(x, y, s=1.0, color=EYE):
    return g(ell(x - 14 * s, y, 7 * s, 4 * s, color, 0, color), ell(x + 14 * s, y, 7 * s, 4 * s, color, 0, color),
             ell(x - 14 * s, y, 1.6 * s, 4 * s, "#000", 0, "#000"), ell(x + 14 * s, y, 1.6 * s, 4 * s, "#000", 0, "#000"))


def wisps(pts, color="#9be8d0"):
    return g(*[circ(x, y, r, color, 0, color, extra='opacity=".75"') + circ(x, y, r * 2.4, color, 0, color, extra='opacity=".18"') for x, y, r in pts])


def paper_money(x, y, n=6):
    """Vàng mã vương vãi."""
    return g(*[rect(x + i * 46, y + (i % 3) * 12, 26, 18, "#d8c46a", 2, 2, extra=f'transform="rotate({i * 23 - 40} {x + i * 46} {y})"') for i in range(n)])


def red_thread(x0, y0, x1, y1, sag=40):
    return path(f"M {x0} {y0} Q {(x0 + x1) / 2:g} {max(y0, y1) + sag:g} {x1} {y1}", "none", 4, "#b02a22")


def ribbons(x, y, n=5, h=130):
    return g(*[path(f"M {x + i * 34} {y} q {(-1) ** i * 14} {h / 2:g} {(-1) ** i * -6} {h - (i % 3) * 20}", "none", 9, "#e8e2d0") for i in range(n)])


def stain(x, y, rx=120, ry=60, op=.25):
    return ell(x, y, rx, ry, "#0a0806", 0, "#0a0806", extra=f'opacity="{op}"')


def hand(x, y, s=1.0):
    """Bàn tay trắng bám mép."""
    return g(rect(x - 12 * s, y, 24 * s, 50 * s, PALE, 2, 6, stroke="#8e887a"), *[rect(x - 14 * s + i * 8 * s, y - 28 * s + (i % 2) * 6 * s, 6 * s, 34 * s, PALE, 2, 3, stroke="#8e887a") for i in range(4)])


def window_glow(x, y, w, h):
    return rect(x, y, w, h, "#1a1408", 0, stroke="none") + rect(x + 6, y + 6, w - 12, h - 12, "#e9c15a", 0, stroke="none", extra='opacity=".55"')


def _reg(bid):
    def deco(fn):
        CREEP[bid] = fn
        return fn
    return deco


@_reg("nghia_dia")
def _():
    return dict(far=dead_tree(1500, 640, 340) + flock(320, 220, 5) + ghost(1160, 680, .55, .6),
                mid=figure(700, 690, .8, op=.85),
                near=paper_money(500, 1000, 7) + paper_money(1250, 1030, 5) + stain(960, 1000, 300, 50, .3) + eyes(1120, 900, .8))


@_reg("toan_canh_lang")
def _():
    return dict(far=flock(500, 200, 6) + dead_tree(120, 640, 360), mid=figure(960, 706, .35, eyes=False), near=paper_money(760, 1010, 4) + stain(960, 1000, 260, 40, .25))


@_reg("gian_tho_dem")
def _():
    return dict(far=cobweb(110, 70, 1.6) + cobweb(1810, 70, 1.6, flipx=True) + figure(300, 830, 1.9, op=.9),
                mid=red_thread(120, 70, 1800, 120, 80) + stain(960, 850, 420, 40, .3) + cobweb(560, 500, 1.0),
                near=paper_money(420, 960, 8) + paper_money(1180, 990, 6) + hand(1500, 880, 1.2))


@_reg("bo_song")
def _():
    return dict(far=flock(900, 180, 4) + ghost(1120, 640, .7, .7),
                mid=wisps([(560, 650, 5), (720, 700, 4), (1640, 640, 5)]) + path("M 1060 600 q 20 40 0 90 M 1180 600 q -20 40 0 90", "none", 5, "#0b0a0c"),
                near=paper_money(800, 1020, 4) + stain(960, 1000, 380, 40, .25))


@_reg("gieng_lang")
def _():
    return dict(far=dead_tree(1760, 720, 380, True) + flock(380, 190, 4),
                mid=hand(1140, 705, .9) + path("M 900 745 q -20 50 -4 110 M 940 750 q -10 60 6 120 M 980 748 q 10 55 -2 112", "none", 5, "#0b0a0c") + eyes(960, 748, .9),
                near=paper_money(1100, 1000, 5) + stain(960, 820, 300, 44, .25))


@_reg("bui_tre_chuoi")
def _():
    return dict(far=eyes(470, 600, 1.0) + eyes(1500, 640, 1.2, "#ff5a40"), mid=figure(960, 790, .8, op=.85) + eyes(700, 700, .9), near=eyes(300, 760, 1.1) + paper_money(780, 1010, 4))


@_reg("truong_bo_hoang")
def _():
    return dict(far=flock(500, 240, 5),
                mid=figure(865, 550, .62, op=.95) + eyes(485, 495, .7) + cobweb(426, 436, .5) + wisps([(1100, 620, 4)]) + stain(960, 640, 520, 18, .35),
                near=dead_tree(1790, 1000, 420, True) + paper_money(560, 1010, 4))


@_reg("nha_hoang")
def _():
    return dict(far=flock(1200, 220, 6) + dead_tree(150, 700, 460), mid=ghost(960, 760, .8, .8) + eyes(735, 620, .9) + eyes(1185, 620, .9, "#ff5a40"),
                near=dead_tree(1760, 1040, 440, True) + paper_money(640, 1020, 5))


@_reg("canh_dong_lua")
def _():
    scarecrow = g(line(700, 640, 700, 900, 10, "#2a2018"), line(610, 720, 790, 720, 10, "#2a2018"), circ(700, 680, 30, "#d8c8a0", 4), poly([(650, 660), (700, 610), (750, 660)], P["wood_l"], 4), ell(692, 682, 3, 5, "#000", 0, "#000") + ell(708, 682, 3, 5, "#000", 0, "#000"))
    return dict(far=flock(300, 180, 7) + ghost(1330, 610, .5, .55), mid=scarecrow + wisps([(1100, 700, 5), (1500, 660, 4)]), near=eyes(300, 960, 1.2, "#ff5a40"))


@_reg("rap_dam_tang")
def _():
    return dict(far=figure(1560, 700, .9, op=.8) + flock(800, 200, 4), mid=figure(960, 560, .8, color="#15110d", eyes=True) + paper_money(560, 790, 8) + paper_money(1100, 770, 6) + ribbons(520, 360, 3, 90),
                near=paper_money(400, 1020, 5) + stain(960, 1000, 500, 40, .3) + eyes(1650, 1000, 1.0))


@_reg("nui")
def _():
    return dict(far=flock(300, 160, 5) + figure(820, 280, .3, eyes=False), mid=wisps([(500, 700, 5), (860, 640, 4), (1300, 690, 5), (1580, 620, 4)]) + ghost(1200, 700, .45, .5), near=dead_tree(1790, 1080, 520, True) + eyes(300, 940, 1.1))


@_reg("chua")
def _():
    return dict(far=flock(1400, 180, 5), mid=figure(960, 780, .9, color="#050404", eyes=True) + wisps([(420, 820, 5), (1500, 830, 5)]) + paper_money(780, 800, 4),
                near=dead_tree(120, 1040, 420) + eyes(1700, 980, 1.0, "#ff5a40"))


@_reg("nha_ve_sinh")
def _():
    return dict(far=flock(300, 200, 4), mid=rect(920, 560, 40, 180, "#050403", 0, stroke="none") + eyes(940, 620, .5) + hand(976, 650, .5) + cobweb(785, 445, .6),
                near=paper_money(700, 1000, 4) + eyes(1500, 930, 1.0, "#ff5a40"))


@_reg("mieu_dinh")
def _():
    return dict(far=ribbons(240, 380, 6, 140) + flock(1100, 200, 5), mid=ghost(1480, 780, .85, .7) + red_thread(520, 470, 1400, 470, 50) + paper_money(800, 790, 5), near=eyes(300, 1000, 1.0) + stain(960, 960, 360, 40, .3))


@_reg("song")
def _():
    boat_fig = figure(1260, 560, .7, color="#0b0a0c")
    return dict(far=flock(700, 200, 5) + ghost(500, 600, .6, .6), mid=boat_fig + wisps([(600, 700, 5), (900, 760, 4), (1700, 700, 5)]), near=eyes(300, 980, 1.1))


@_reg("cay_da")
def _():
    return dict(far=flock(1100, 200, 6), mid=ribbons(900, 470, 6, 170) + red_thread(700, 520, 1220, 520, 50) + eyes(960, 700, 1.3, "#ff5a40") + figure(1500, 900, .6, op=.9),
                near=paper_money(760, 1000, 6) + stain(960, 960, 440, 40, .3))


@_reg("san_nha")
def _():
    return dict(far=flock(300, 200, 5) + dead_tree(1790, 700, 380, True), mid=figure(960, 700, .75, op=.9) + stain(960, 780, 240, 24, .35),
                near=figure(1640, 900, 1.0, op=.9) + paper_money(520, 1020, 5))


@_reg("nha_bep")
def _():
    return dict(far=figure(1545, 460, .7, op=.9) + cobweb(80, 80, 1.3), mid=eyes(590, 700, 1.0, "#ff5a40") + red_thread(260, 70, 1500, 80, 50) + cobweb(1870, 80, 1.1, flipx=True),
                near=paper_money(360, 1010, 4) + stain(900, 1000, 460, 40, .3))


@_reg("phong_ngu")
def _():
    return dict(far=figure(1415, 480, .8, color="#0a0c14", eyes=True) + cobweb(90, 70, 1.4), mid=hand(430, 840, .8) + hand(470, 845, .7) + cobweb(1830, 70, 1.4, flipx=True),
                near=stain(800, 1000, 460, 44, .35) + paper_money(900, 1030, 4))


@_reg("phong_khach")
def _():
    return dict(far=eyes(960, 260, 2.0) + cobweb(90, 70, 1.4), mid=figure(960, 700, .9, color="#0b0a0c", op=.9) + red_thread(250, 410, 1670, 410, 40) + cobweb(1830, 70, 1.4, flipx=True),
                near=paper_money(500, 1010, 5) + stain(960, 1000, 520, 40, .3))


@_reg("nha_co_nha_tho_ho")
def _():
    return dict(far=flock(1000, 160, 6) + dead_tree(120, 700, 480), mid=ghost(960, 780, .95, .85) + eyes(960, 470, 1.2, "#ff5a40"), near=paper_money(700, 1010, 7) + dead_tree(1790, 1040, 460, True))


@_reg("nha_cap_bon")
def _():
    return dict(far=flock(600, 200, 5) + dead_tree(150, 700, 420), mid=figure(665, 710, .55, color="#0a0c14") + cobweb(1190, 596, .5) + eyes(1250, 650, .6),
                near=paper_money(620, 1020, 4) + eyes(1600, 1000, 1.0, "#ff5a40"))
