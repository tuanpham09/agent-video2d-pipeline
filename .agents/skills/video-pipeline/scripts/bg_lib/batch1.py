# -*- coding: utf-8 -*-
"""Đợt 1: nghĩa địa, toàn cảnh làng, gian thờ đêm, bờ sông, giếng làng, bụi tre bụi chuối."""
from __future__ import annotations

from . import register
from .core import *  # noqa: F401,F403
from .core import P, W, H, HORIZON


@register("nghia_dia", "Nghĩa địa", "exterior", ["ma", "đêm", "mồ mả"], focus=(960, 760), lamp=(960, 770), sky=("#7f8f99", "#c9c3b0"))
def nghia_dia():
    far = sky() + hills(560, P["mount_far"], 50, 1) + hills(620, P["leaf_d"], 40, 4)
    far += "".join(tree(x, 640, 300 + (x % 90), leaf=P["leaf_d"]) for x in (120, 430, 1500, 1800))
    mid = ground(640, P["grass2"])
    mid += "".join(tomb(x, 700 + (i % 3) * 18, 0.9, i % 2 == 0) for i, x in enumerate((260, 520, 1400, 1660)))
    mid += fog_band(600, 160, .45)
    near = ground(800, P["ground"]) + grass_tufts(790, 1060, 40)
    near += "".join(tomb(x, 930 + (i % 2) * 20, 1.5, i % 2 == 1) for i, x in enumerate((140, 1790, 1010)))
    near += rect(930, 780, 60, 20, P["stone_d"], 4) + line(960, 760, 960, 700, 5, P["wood_d"])  # bát hương + nhang
    return dict(far=far, mid=mid, near=near)


@register("toan_canh_lang", "Toàn cảnh làng", "exterior", ["làng", "toàn cảnh", "thiết lập"], focus=(960, 700), lamp=(960, 640))
def toan_canh_lang():
    far = sky() + hills(520, P["mount_far"], 80, 2) + hills(600, P["mount"], 50, 5)
    mid = ground(620, P["grass"]) + hills(640, P["leaf"], 30, 3)
    for i, (x, w, h) in enumerate(((330, 190, 110), (640, 230, 130), (980, 260, 150), (1330, 210, 120), (1620, 190, 110))):
        mid += house(x, 700 + (i % 2) * 20, w, h, thatch=i % 2 == 0)
    mid += smoke(1000, 480) + smoke(660, 520)
    mid += banana(500, 720, 150) + bamboo_clump(1480, 730, 260, 5) + tree(180, 720, 260)
    near = ground(800, P["ground"]) + path("M 960 1080 Q 900 900 960 800 Q 1010 740 960 700", "none", 70, P["ground2"])
    near += grass_tufts(820, 1070, 50) + banana(160, 1060, 230) + banana(1780, 1070, 250)
    return dict(far=far, mid=mid, near=near)


@register("gian_tho_dem", "Gian thờ đêm", "interior", ["thờ", "nhà", "ma", "nến"], focus=(960, 560))
def gian_tho_dem():
    far = rect(0, 0, W, H, P["wall_d"], 0, stroke="none") + rect(0, 820, W, 260, P["floor"], 0, stroke="none")
    far += "".join(line(x, 0, x, 820, 3, P["wall"]) for x in range(120, W, 160))
    far += rect(120, 0, 70, 820, P["wood_d"], 5) + rect(1730, 0, 70, 820, P["wood_d"], 5)
    mid = rect(560, 540, 800, 300, P["wood"], 6) + rect(600, 500, 720, 40, P["wood_d"], 5)  # bàn thờ
    mid += rect(760, 300, 400, 200, P["wood_d"], 6) + rect(790, 330, 340, 140, P["gold"], 4)  # khám / bài vị
    mid += poly([(540, 300), (960, 220), (1380, 300), (1380, 330), (540, 330)], P["roof"], 5)  # mái khám
    mid += rect(690, 440, 20, 60, P["red"], 3) + rect(1210, 440, 20, 60, P["red"], 3)  # nến
    mid += rect(900, 470, 120, 30, P["stone_d"], 4) + line(930, 470, 930, 430, 4) + line(960, 470, 960, 425, 4) + line(990, 470, 990, 430, 4)  # bát hương
    mid += ell(820, 520, 70, 26, P["tile"], 4) + ell(1100, 520, 70, 26, P["tile"], 4)  # mâm
    near = rect(0, 900, W, 180, P["floor_d"], 0, stroke="none") + rect(0, 886, W, 14, P["wood_d"], 4)
    near += rect(300, 880, 360, 24, P["cloth"], 4, 6) + rect(1260, 880, 360, 24, P["cloth"], 4, 6)  # chiếu
    near += rect(0, 0, 90, H, P["wood_d"], 0, stroke="none") + rect(1830, 0, 90, H, P["wood_d"], 0, stroke="none")
    return dict(far=far, mid=mid, near=near)


@register("bo_song", "Bờ sông", "exterior", ["sông", "bến", "nước"], focus=(960, 760), moon=(300, 150))
def bo_song():
    far = sky() + hills(470, P["mount_far"], 60, 6) + hills(540, P["leaf_d"], 40, 2)
    mid = rect(0, 560, W, 260, P["water"], 0, stroke="none")
    mid += "".join(path(f"M {x} {600 + (i % 4) * 50} q 40 -14 80 0 t 80 0", sw=4, stroke=P["water_d"]) for i, x in enumerate(range(40, W, 210)))
    mid += fog_band(520, 120, .4)
    mid += poly([(1300, 700), (1750, 700), (1700, 740), (1350, 740)], P["wood"], 4) + line(1400, 700, 1400, 640, 6, P["wood_d"]) + poly([(1380, 640), (1500, 560), (1500, 640)], P["cloth"], 4)  # thuyền
    near = hills(840, P["grass"], 60, 3) + ground(850, P["ground"]) + grass_tufts(830, 1070, 45)
    near += bamboo_clump(220, 880, 520, 6) + rect(700, 800, 520, 24, P["wood"], 5) + "".join(line(x, 800, x, 900, 8, P["wood_d"]) for x in (730, 960, 1190))  # cầu ván
    return dict(far=far, mid=mid, near=near)


@register("gieng_lang", "Giếng làng", "exterior", ["giếng", "làng", "nước"], focus=(960, 760), lamp=(1200, 560))
def gieng_lang():
    far = sky() + hills(540, P["mount_far"], 60, 7) + house(420, 700, 260, 140, thatch=True) + house(1500, 700, 240, 130)
    far += banyan(1760, 720, 480)
    mid = ground(650, P["grass"]) + ground(760, P["ground"])
    mid += ell(960, 800, 230, 64, P["stone_d"], 6) + rect(740, 740, 440, 60, P["stone"], 6) + ell(960, 745, 220, 52, "#10161a", 6)  # miệng giếng
    mid += line(800, 740, 800, 560, 10, P["wood_d"]) + line(1120, 740, 1120, 560, 10, P["wood_d"]) + line(780, 560, 1140, 560, 12, P["wood_d"]) + line(960, 560, 960, 700, 4) + rect(942, 690, 36, 40, P["wood"], 4)  # cọc + gầu
    near = ground(900, P["ground2"]) + grass_tufts(880, 1070, 40) + ell(300, 960, 70, 26, P["wood_d"], 5) + rect(240, 900, 120, 60, P["wood"], 5)  # thùng nước
    near += banana(1700, 1070, 240)
    return dict(far=far, mid=mid, near=near)


@register("bui_tre_chuoi", "Bụi tre bụi chuối", "exterior", ["tre", "chuối", "ma", "cây cối"], focus=(960, 780), sky=("#7c8f8c", "#cdd2b8"))
def bui_tre_chuoi():
    far = sky() + hills(560, P["leaf_d"], 70, 8) + bamboo_clump(300, 720, 520, 9) + bamboo_clump(1650, 720, 560, 9)
    mid = ground(700, P["grass2"]) + banana(620, 800, 260) + banana(1320, 800, 280) + banana(960, 760, 220)
    mid += fog_band(640, 160, .4)
    near = ground(860, P["ground"]) + path("M 900 1080 Q 960 940 930 860", "none", 80, P["ground2"]) + grass_tufts(850, 1070, 55)
    near += bamboo_clump(120, 1100, 900, 5) + bamboo_clump(1820, 1100, 940, 5)
    return dict(far=far, mid=mid, near=near)
