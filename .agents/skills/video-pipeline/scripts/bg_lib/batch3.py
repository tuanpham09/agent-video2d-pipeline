# -*- coding: utf-8 -*-
"""Đợt 3: nhà vệ sinh, miếu/đình làng, sông, cây đa, sân nhà, nhà bếp."""
from __future__ import annotations

from . import register
from .core import *  # noqa: F401,F403
from .core import P, W, H


def room_shell(wall=None, floor_y=820, beams=True):
    wall = wall or P["wall_d"]
    s = rect(0, 0, W, H, wall, 0, stroke="none") + rect(0, floor_y, W, H - floor_y, P["floor"], 0, stroke="none")
    s += line(0, floor_y, W, floor_y, 6, P["wood_d"])
    if beams:
        s += rect(0, 0, W, 70, P["wood_d"], 0, stroke="none") + "".join(rect(x, 0, 50, floor_y, P["wood_d"], 4) for x in (110, 1760))
    return s


@register("nha_ve_sinh", "Nhà vệ sinh", "exterior", ["wc", "sân sau", "ma"], focus=(960, 700), lamp=(960, 560), sky=("#7b8a92", "#c7bfa9"))
def nha_ve_sinh():
    far = sky() + hills(560, P["leaf_d"], 70, 5) + banana(300, 700, 280) + banana(1650, 700, 300)
    mid = ground(640, P["grass2"]) + ground(740, P["ground"])
    mid += rect(780, 440, 360, 300, P["wood_l"], 6) + "".join(line(x, 440, x, 740, 3, P["wood_d"]) for x in range(830, 1140, 50))
    mid += poly([(750, 450), (960, 360), (1170, 450)], P["roof_d"], 6) + rect(870, 540, 140, 200, P["wood_d"], 5) + circ(990, 650, 8, P["gold"], 3)  # cửa
    mid += rect(1180, 620, 80, 120, P["stone_d"], 5) + ell(1220, 620, 40, 12, P["water_d"], 4)  # lu nước
    mid += line(1260, 480, 1260, 740, 6, P["wood_d"]) + circ(1260, 480, 18, "#e8e1c8", 3)  # bóng đèn
    near = ground(880, P["ground2"]) + grass_tufts(870, 1070, 60, P["leaf_d"]) + bamboo_clump(140, 1090, 640, 6) + banana(1780, 1075, 300)
    near += ell(560, 980, 60, 20, P["wood_d"], 4) + rect(510, 920, 100, 60, P["wood"], 5)  # xô nước
    return dict(far=far, mid=mid, near=near)


@register("mieu_dinh", "Miếu / Đình làng", "exterior", ["miếu", "đình", "tâm linh"], focus=(960, 600), lamp=(960, 560), sky=("#9bb1bd", "#e4d9bc"))
def mieu_dinh():
    far = sky() + hills(540, P["mount_far"], 70, 4) + banyan(280, 700, 520)
    mid = ground(660, P["grass"]) + ground(770, P["ground"])
    mid += rect(520, 470, 880, 300, P["wall"], 6) + "".join(rect(x, 500, 34, 270, P["red"], 4) for x in range(560, 1400, 110))
    mid += poly([(440, 490), (560, 380), (1360, 380), (1480, 490), (1400, 520), (520, 520)], P["tile"], 6)
    mid += poly([(500, 380), (620, 290), (1300, 290), (1420, 380)], P["roof"], 6)
    mid += path("M 440 490 q -50 -10 -70 -60 M 1480 490 q 50 -10 70 -60", sw=10, stroke=P["roof_d"])
    mid += rect(880, 580, 160, 190, "#0e0906", 5) + rect(780, 540, 360, 36, P["gold"], 4) + ell(960, 600, 30, 12, P["red"], 3)  # cửa + hoành phi
    near = ground(900, P["ground2"]) + rect(860, 800, 200, 20, P["stone"], 4) + rect(820, 830, 280, 20, P["stone"], 4) + rect(780, 860, 360, 20, P["stone"], 4)
    near += rect(1480, 770, 120, 170, P["stone"], 6) + poly([(1470, 770), (1540, 710), (1610, 770)], P["stone_d"], 5)
    near += rect(300, 790, 130, 150, P["stone_d"], 6) + grass_tufts(940, 1070, 40, P["leaf_d"]) + tree(1790, 1080, 540, leaf=P["leaf_d"])
    return dict(far=far, mid=mid, near=near)


@register("song", "Sông", "exterior", ["sông", "mặt nước", "toàn cảnh", "thuyền"], focus=(960, 720), moon=(1400, 160), sky=("#a5bccb", "#efe4c6"))
def song():
    far = sky() + hills(440, P["mount_far"], 70, 3) + hills(500, P["mount"], 40, 7)
    mid = rect(0, 520, W, 560, P["water"], 0, stroke="none")
    for i in range(14):
        y = 560 + i * i * 2.4
        mid += "".join(path(f"M {x + i * 17} {y} q {30 + i * 3} -{8 + i} {60 + i * 6} 0", sw=2.5 + i * .15, stroke=P["water_d"]) for x in range(-40, W, 180 + i * 10))
    mid += fog_band(480, 100, .4)
    mid += poly([(1000, 700), (1500, 700), (1440, 760), (1060, 760)], P["wood"], 5) + poly([(1180, 700), (1260, 560), (1320, 700)], P["cloth"], 4) + line(1250, 700, 1250, 540, 7, P["wood_d"])
    near = hills(1000, P["grass"], 50, 1) + ground(1010, P["ground2"])
    near += bamboo_clump(130, 1090, 560, 5) + bamboo_clump(1800, 1090, 520, 4) + grass_tufts(1010, 1075, 40, P["leaf_d"])
    return dict(far=far, mid=mid, near=near)


@register("cay_da", "Cây đa", "exterior", ["cây đa", "đầu làng", "ma", "tâm linh"], focus=(960, 760), lamp=(960, 640), sky=("#8ca3b0", "#e2d8bb"))
def cay_da():
    far = sky() + hills(560, P["mount_far"], 60, 9) + house(300, 700, 240, 130) + house(1650, 700, 230, 130, thatch=True)
    mid = ground(650, P["grass"]) + ground(800, P["ground"])
    mid += banyan(960, 820, 760)
    mid += rect(840, 790, 240, 40, P["stone_d"], 5) + rect(870, 740, 180, 50, P["stone"], 5)  # bệ thờ gốc đa
    mid += rect(930, 700, 20, 40, P["red"], 3) + line(960, 700, 960, 650, 4)
    near = ground(900, P["ground2"]) + rect(1300, 900, 400, 24, P["wood"], 6) + line(1340, 924, 1340, 1000, 8, P["wood_d"]) + line(1660, 924, 1660, 1000, 8, P["wood_d"])  # ghế đá/ván dưới gốc
    near += grass_tufts(930, 1070, 50, P["leaf_d"]) + banana(140, 1075, 280)
    return dict(far=far, mid=mid, near=near)


@register("san_nha", "Sân nhà", "exterior", ["sân", "nhà", "gia đình"], focus=(960, 760), lamp=(960, 560), sky=("#9db8c7", "#efe3c2"))
def san_nha():
    far = sky() + hills(560, P["leaf_d"], 70, 2) + tree(240, 680, 400) + bamboo_clump(1700, 690, 420, 6)
    mid = ground(640, P["grass"]) + house(960, 700, 760, 300, roof_h=190, wall=P["wall"], thatch=False)
    mid += rect(780, 560, 120, 140, P["wood_d"], 5) + rect(1020, 560, 120, 140, P["wood_d"], 5) + rect(900, 560, 120, 140, "#120d09", 5)
    mid += rect(700, 480, 40, 40, P["gold"], 4, extra='opacity=".9"')
    near = ground(760, P["floor"]) + ground(780, "#9c8a66") + rect(0, 780, W, 18, P["stone"], 4)  # sân gạch
    near += "".join(line(x, 800, x + 20, 1080, 2.5, P["stone_d"]) for x in range(60, W, 200)) + "".join(line(0, y, W, y, 2.5, P["stone_d"]) for y in (860, 960, 1040))
    near += rect(1480, 880, 300, 20, P["wood"], 5) + "".join(line(x, 900, x, 980, 6, P["wood_d"]) for x in (1500, 1760))  # chõng tre
    near += ell(380, 960, 120, 34, P["wood_l"], 5) + ell(380, 950, 100, 22, P["bamboo"], 4)  # mẹt phơi
    near += banana(140, 1080, 300)
    return dict(far=far, mid=mid, near=near)


@register("nha_bep", "Nhà bếp", "interior", ["bếp", "nhà", "củi"], focus=(900, 640))
def nha_bep():
    far = room_shell(P["wall_d"], 840) + rect(1380, 180, 330, 280, "#16100c", 5) + rect(1400, 200, 290, 240, "#2a3b4a", 3)  # cửa sổ
    far += "".join(line(x, 180, x, 460, 4, P["wood_d"]) for x in (1480, 1580, 1670))
    mid = rect(420, 560, 640, 280, P["stone_d"], 6) + rect(480, 600, 220, 200, "#0b0806", 5) + rect(780, 600, 220, 200, "#0b0806", 5)  # bếp lò
    mid += ell(590, 590, 90, 24, P["black"], 5) + path("M 570 560 q 20 -20 0 -40", sw=8, stroke=P["fog"], extra='opacity=".6"')
    mid += rect(1120, 640, 460, 200, P["wood"], 6) + rect(1100, 620, 500, 30, P["wood_d"], 5) + ell(1250, 610, 50, 16, P["tile"], 4) + ell(1400, 610, 60, 18, P["wood_l"], 4)
    mid += "".join(line(x, 70, x, 220, 3) + ell(x, 240, 30, 22, P["bamboo"], 4) for x in (260, 340, 420))  # móc treo rổ
    mid += rect(120, 300, 220, 14, P["wood_d"], 4) + "".join(rect(140 + i * 60, 240, 44, 60, P["tile"], 4, 6) for i in range(3))  # kệ chum
    near = rect(0, 940, W, 140, P["floor_d"], 0, stroke="none") + rect(240, 900, 280, 40, P["wood_d"], 5) + "".join(line(260 + i * 60, 900, 280 + i * 60, 860, 7, P["wood_l"]) for i in range(4))  # củi
    near += ell(1500, 960, 110, 36, P["tile"], 5) + rect(1390, 900, 220, 60, P["tile"], 5, 18) + rect(0, 0, 80, H, P["wood_d"], 0, stroke="none") + rect(1840, 0, 80, H, P["wood_d"], 0, stroke="none")
    return dict(far=far, mid=mid, near=near)
