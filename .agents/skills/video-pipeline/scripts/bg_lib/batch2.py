# -*- coding: utf-8 -*-
"""Đợt 2: trường bỏ hoang, nhà hoang, cánh đồng lúa, rạp đám tang, núi, chùa."""
from __future__ import annotations

from . import register
from .core import *  # noqa: F401,F403
from .core import P, W, H


def _windows(x0, y0, cols, rows, w, h, gap, broken=()):
    out = ""
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * (w + gap), y0 + r * (h + gap)
            out += rect(x, y, w, h, "#16100c", 4)
            if (r, c) in broken:
                out += line(x, y, x + w, y + h, 3, P["wall"]) + line(x + w, y, x + w * .4, y + h, 3, P["wall"])
            else:
                out += line(x + w / 2, y, x + w / 2, y + h, 3, P["wood_d"])
    return out


@register("truong_bo_hoang", "Trường học bỏ hoang", "exterior", ["trường", "hoang", "ma"], focus=(960, 720), sky=("#6f7f89", "#bfb9a6"))
def truong_bo_hoang():
    far = sky() + hills(560, P["mount_far"], 60, 9)
    mid = ground(660, P["grass2"])
    mid += rect(360, 380, 1200, 280, P["wall_d"], 6) + poly([(330, 380), (480, 300), (1440, 300), (1590, 380)], P["roof_d"], 6)
    mid += _windows(420, 430, 6, 1, 130, 120, 60, broken={(0, 1), (0, 4)}) + _windows(420, 580, 6, 1, 130, 60, 60)
    mid += rect(900, 520, 120, 140, P["wood_d"], 5) + rect(840, 330, 240, 40, P["wall"], 4)  # cửa chính + biển
    mid += path("M 560 380 q 20 80 -10 160 M 1300 380 q -30 70 10 140", sw=5, stroke=P["leaf_d"])  # rêu loang
    mid += line(1740, 660, 1740, 380, 8, P["wood_d"]) + poly([(1740, 390), (1840, 410), (1740, 440)], P["red"], 3)  # cột cờ
    near = ground(820, P["ground"]) + grass_tufts(810, 1070, 70, P["leaf_d"])
    near += fence(80, 700, 900, 120) + fence(1220, 1840, 900, 120) + tree(180, 1000, 360, leaf=P["leaf_d"])
    return dict(far=far, mid=mid, near=near)


@register("nha_hoang", "Nhà hoang", "exterior", ["nhà", "hoang", "ma"], focus=(960, 700), sky=("#707d86", "#c4bba4"))
def nha_hoang():
    far = sky() + hills(580, P["leaf_d"], 70, 3) + tree(260, 680, 420, leaf=P["leaf_d"]) + tree(1680, 680, 400, leaf=P["leaf_d"])
    mid = ground(660, P["grass2"])
    mid += house(960, 760, 640, 300, roof_h=190, wall=P["wall_d"], roof=P["roof_d"], door=False, window=False)
    mid += rect(860, 540, 200, 220, "#0c0907", 5) + line(860, 540, 1060, 760, 3, P["wood_l"]) + line(1060, 540, 900, 760, 3, P["wood_l"])  # cửa ván mục
    mid += rect(680, 560, 110, 120, "#0c0907", 5) + line(680, 620, 790, 620, 3, P["wood_l"]) + rect(1130, 560, 110, 120, "#0c0907", 5)
    mid += path("M 760 330 l 80 60 M 1100 350 l 70 40", sw=5, stroke=P["black"], extra='opacity=".6"')  # mái thủng
    near = ground(840, P["ground"]) + grass_tufts(830, 1070, 80, P["leaf_d"])
    near += bamboo_clump(200, 1080, 600, 6) + banana(1740, 1070, 300) + fence(560, 1360, 960, 90)
    return dict(far=far, mid=mid, near=near)


@register("canh_dong_lua", "Cánh đồng lúa", "exterior", ["đồng", "lúa", "nông thôn"], focus=(960, 760), sky=("#8fb4c9", "#f0e2bb"))
def canh_dong_lua():
    far = sky() + hills(500, P["mount_far"], 70, 5) + hills(580, P["leaf_d"], 40, 1) + "".join(tree(x, 590, 150, leaf=P["leaf_d"]) for x in (400, 1200, 1500))
    rows = ""
    for i in range(16):
        y = 600 + i * i * 1.6 + i * 12
        col = P["leaf_l"] if i % 2 else P["leaf"]
        rows += rect(0, y, W, 34 + i * 3, col, 0, stroke="none")
        for x in range(0, W, 38 + i * 4):
            rows += path(f"M {x} {y + 30 + i * 3} q 4 -{22 + i * 2} 10 -{34 + i * 4}", sw=2.5 + i * .12, stroke=P["leaf_d"])
    mid = rows
    mid += path("M 960 1080 L 940 640", "none", 120, P["ground"]) + path("M 960 1080 L 940 640", "none", 100, "#8a7653", extra='opacity=".7"')  # bờ ruộng
    near = poly([(1500, 900), (1620, 780), (1700, 900)], P["wood_l"], 5) + line(1560, 900, 1560, 1000, 6) + ell(1600, 790, 110, 30, P["bamboo"], 5)  # nón lá
    near += grass_tufts(950, 1075, 40, P["leaf_d"]) + banana(140, 1070, 280)
    return dict(far=far, mid=mid, near=near)


@register("rap_dam_tang", "Rạp đám tang", "exterior", ["tang", "rạp", "ma"], focus=(960, 640), lamp=(960, 500), sky=("#7b8892", "#c8c0aa"))
def rap_dam_tang():
    far = sky() + hills(560, P["leaf_d"], 60, 4) + house(300, 700, 260, 140) + house(1620, 700, 260, 140, thatch=True)
    mid = ground(660, P["ground"])
    mid += poly([(480, 330), (960, 230), (1440, 330), (1440, 360), (480, 360)], P["cloth"], 6)  # mái bạt trắng
    mid += "".join(line(x, 360, x, 760, 12, P["wood_d"]) for x in (500, 1420))
    mid += "".join(path(f"M {x} 360 q 20 50 0 90", sw=14, stroke=P["white"]) for x in range(540, 1420, 100))  # vải rủ
    mid += rect(760, 560, 400, 200, P["wood_d"], 6) + rect(740, 520, 440, 50, P["wood"], 6)  # quan tài
    mid += rect(780, 580, 360, 20, P["gold"], 3) + ell(960, 500, 60, 20, P["white"], 4)
    mid += "".join(g(rect(x - 18, 600, 36, 100, P["white"], 3), line(x, 590, x, 540, 4)) for x in (640, 1280))  # vòng/đèn
    near = ground(860, P["ground2"]) + rect(380, 880, 1160, 30, P["cloth"], 5, 6)
    near += "".join(g(rect(x, 940, 60, 36, P["white"], 4, 4), rect(x + 8, 906, 44, 34, P["wood_l"], 3)) for x in (300, 520, 1340, 1560))  # ghế/bát hương
    return dict(far=far, mid=mid, near=near)


@register("nui", "Núi", "exterior", ["núi", "rừng", "toàn cảnh"], focus=(960, 700), moon=(420, 180), sky=("#a9c0cc", "#efe6cc"))
def nui():
    far = sky() + mountain([(0, 640), (260, 360), (520, 520), (820, 240), (1160, 560), (1500, 330), (1920, 600), (1920, 700), (0, 700)], P["mount_far"])
    mid = mountain([(0, 760), (360, 460), (700, 680), (1100, 420), (1500, 700), (1920, 520), (1920, 900), (0, 900)], P["mount"])
    mid += "".join(tree(x, 700 + (x % 60), 140 + x % 50, leaf=P["leaf_d"]) for x in range(100, 1900, 130))
    mid += fog_band(520, 220, .5)
    near = hills(900, P["leaf_d"], 90, 2) + ground(950, P["ground2"]) + grass_tufts(940, 1070, 60, P["leaf_d"])
    near += path("M 900 1080 Q 1100 900 960 780 Q 840 700 980 600", "none", 60, P["ground"], extra='opacity=".85"')
    near += tree(140, 1070, 520, leaf=P["leaf_d"]) + tree(1790, 1070, 560, leaf=P["leaf_d"])
    return dict(far=far, mid=mid, near=near)


@register("chua", "Chùa", "exterior", ["chùa", "tâm linh", "ban đêm"], focus=(960, 560), lamp=(960, 520), sky=("#9fb6c2", "#eadfc2"))
def chua():
    far = sky() + hills(560, P["mount_far"], 80, 6) + tree(240, 690, 380) + tree(1700, 690, 400)
    mid = ground(660, P["grass"]) + ground(780, P["ground"])
    # chính điện hai tầng mái cong
    mid += rect(600, 480, 720, 300, P["wall"], 6) + rect(870, 560, 180, 220, P["wood_d"], 5) + line(960, 560, 960, 780, 3, P["gold"])
    for y, hw in ((480, 480), (380, 400)):
        mid += poly([(960 - hw, y + 30), (960 - hw + 60, y - 10), (960 + hw - 60, y - 10), (960 + hw, y + 30), (960 + hw - 40, y + 50), (960 - hw + 40, y + 50)], P["tile"], 6)
        mid += path(f"M {960 - hw} {y + 30} q -30 -10 -40 -40 M {960 + hw} {y + 30} q 30 -10 40 -40", sw=8, stroke=P["roof_d"])
    mid += "".join(rect(x, 520, 26, 260, P["red"], 4) for x in (650, 760, 1134, 1244))  # cột
    mid += rect(920, 300, 80, 80, P["tile"], 5) + circ(960, 300, 22, P["gold"], 4)
    near = ground(880, P["ground2"]) + "".join(rect(940 - i * 22, 800 + i * 26, 40 + i * 44, 26, P["stone"], 4) for i in range(7))  # bậc thang
    near += rect(250, 860, 100, 160, P["stone"], 6) + poly([(240, 860), (300, 800), (360, 860)], P["stone_d"], 5)  # đèn đá
    near += rect(1570, 860, 100, 160, P["stone"], 6) + poly([(1560, 860), (1620, 800), (1680, 860)], P["stone_d"], 5)
    near += bamboo_clump(80, 1090, 560, 5)
    return dict(far=far, mid=mid, near=near)
