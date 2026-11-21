# -*- coding: utf-8 -*-
"""Đợt 4: phòng ngủ, phòng khách, nhà cổ / nhà thờ họ, nhà cấp bốn."""
from __future__ import annotations

from . import register
from .core import *  # noqa: F401,F403
from .core import P, W, H
from .batch3 import room_shell


@register("phong_ngu", "Phòng ngủ", "interior", ["phòng ngủ", "nhà", "đêm"], focus=(760, 620))
def phong_ngu():
    far = room_shell(P["wall_d"], 840, beams=False) + rect(1250, 200, 330, 300, "#16100c", 5) + rect(1270, 220, 290, 260, "#253546", 3) + line(1415, 220, 1415, 480, 4, P["wood_d"])
    far += rect(240, 220, 200, 260, P["wall"], 5) + circ(340, 300, 40, P["gold"], 3) + line(340, 300, 340, 270, 3) + line(340, 300, 362, 310, 3)  # tranh/đồng hồ
    mid = rect(420, 600, 760, 240, P["wood"], 6) + rect(440, 520, 720, 100, P["cloth"], 5, 16) + ell(560, 530, 90, 36, P["white"], 4) + rect(440, 560, 720, 90, P["red"], 4, 10)  # giường + chăn
    mid += rect(420, 520, 30, 320, P["wood_d"], 5) + rect(1150, 540, 30, 300, P["wood_d"], 5)
    mid += rect(1260, 620, 240, 220, P["wood"], 6) + rect(1280, 640, 200, 70, P["wood_d"], 4) + rect(1280, 720, 200, 90, P["wood_d"], 4)  # tủ
    mid += rect(1210, 600, 40, 40, P["wood_d"], 4) + rect(1195, 560, 70, 40, P["gold"], 4) + circ(1230, 548, 8, "#ffd27a", 2)  # đèn ngủ
    near = rect(0, 940, W, 140, P["floor_d"], 0, stroke="none") + rect(500, 960, 600, 60, P["cloth"], 5, 14)  # chiếu / thảm
    near += rect(0, 0, 80, H, P["wood_d"], 0, stroke="none") + rect(1840, 0, 80, H, P["wood_d"], 0, stroke="none")
    return dict(far=far, mid=mid, near=near)


@register("phong_khach", "Phòng khách", "interior", ["phòng khách", "nhà", "gia đình"], focus=(960, 640))
def phong_khach():
    far = room_shell(P["wall"], 840) + rect(760, 140, 400, 240, P["wood_d"], 6) + rect(780, 160, 360, 200, P["gold"], 4, extra='opacity=".8"')  # tranh / chữ hoành phi
    far += "".join(rect(x, 200, 140, 200, "#16100c", 5) + rect(x + 14, 214, 112, 172, "#253546", 3) for x in (240, 1540))
    mid = rect(560, 560, 800, 280, P["wood"], 6) + rect(560, 500, 800, 70, P["wood_d"], 6) + "".join(rect(x, 600, 80, 240, P["wood_d"], 5) for x in (560, 1280))  # sập / bộ sofa gỗ
    mid += rect(600, 620, 720, 60, P["cloth"], 4, 10) + rect(780, 700, 360, 70, P["tile"], 5)  # đệm + bàn trà
    mid += ell(960, 690, 70, 16, P["white"], 3) + rect(1450, 380, 120, 460, P["wood_d"], 6) + rect(330, 660, 120, 180, P["tile"], 6, 14) + path("M 390 660 q -30 -90 -50 -140 M 390 660 q 20 -90 40 -140", sw=6, stroke=P["leaf"])  # tủ + bình cắm cành
    near = rect(0, 940, W, 140, P["floor_d"], 0, stroke="none") + rect(620, 960, 680, 70, P["red"], 5, 8)
    near += rect(0, 0, 80, H, P["wood_d"], 0, stroke="none") + rect(1840, 0, 80, H, P["wood_d"], 0, stroke="none")
    return dict(far=far, mid=mid, near=near)


@register("nha_co_nha_tho_ho", "Nhà cổ / nhà thờ họ", "exterior", ["nhà cổ", "từ đường", "tâm linh", "ma"], focus=(960, 560), lamp=(960, 520), sky=("#8fa6b2", "#e2d6b8"))
def nha_co_nha_tho_ho():
    far = sky() + hills(560, P["mount_far"], 60, 4) + tree(220, 700, 440, leaf=P["leaf_d"]) + tree(1700, 700, 420, leaf=P["leaf_d"])
    mid = ground(660, P["grass"]) + ground(780, P["ground"])
    mid += rect(480, 470, 960, 310, P["wall_d"], 6) + "".join(rect(x, 480, 38, 300, P["wood_d"], 5) for x in range(520, 1420, 150))
    mid += poly([(400, 490), (540, 360), (1380, 360), (1520, 490), (1440, 520), (480, 520)], P["tile"], 6) + poly([(540, 360), (680, 280), (1240, 280), (1380, 360)], P["roof"], 6)
    mid += path("M 400 490 q -50 -10 -70 -60 M 1520 490 q 50 -10 70 -60", sw=10, stroke=P["roof_d"]) + rect(900, 232, 120, 48, P["tile"], 5) + circ(960, 214, 16, P["gold"], 3)
    mid += rect(860, 560, 200, 220, "#0e0906", 5) + rect(780, 520, 360, 34, P["gold"], 4) + "".join(g(rect(x, 600, 44, 160, P["red"], 3), line(x + 22, 600, x + 22, 760, 2, P["gold"])) for x in (690, 1190))  # câu đối
    mid += "".join(g(line(x, 420, x, 470, 3), ell(x, 490, 22, 30, P["red"], 4)) for x in (600, 760, 1160, 1320))  # đèn lồng
    near = ground(880, P["ground2"]) + "".join(rect(920 - i * 20, 800 + i * 20, 80 + i * 40, 22, P["stone"], 4) for i in range(5))
    near += rect(1440, 840, 80, 130, P["stone"], 6) + rect(400, 840, 80, 130, P["stone"], 6) + grass_tufts(950, 1070, 40, P["leaf_d"]) + bamboo_clump(1800, 1090, 600, 4)
    return dict(far=far, mid=mid, near=near)


@register("nha_cap_bon", "Nhà cấp bốn", "exterior", ["nhà cấp bốn", "nông thôn", "gia đình"], focus=(960, 700), lamp=(960, 560), sky=("#9db8c7", "#eee2c0"))
def nha_cap_bon():
    far = sky() + hills(560, P["leaf_d"], 70, 6) + tree(1700, 690, 380) + banana(240, 700, 260)
    mid = ground(650, P["grass"]) + ground(770, P["ground"])
    mid += rect(520, 500, 880, 270, "#d9cdb2", 6) + poly([(480, 510), (640, 400), (1280, 400), (1440, 510)], "#b24a36", 6)  # mái tôn/ngói đỏ
    mid += "".join(line(x, 400 + (x - 640) * 0.0, x - 30 if x < 960 else x + 30, 510, 2.5, P["roof_d"]) for x in range(700, 1280, 80))
    mid += rect(880, 580, 160, 190, P["wood_d"], 5) + line(960, 580, 960, 770, 3) + "".join(rect(x, 590, 130, 120, "#2a3b4a", 5) + line(x + 65, 590, x + 65, 710, 3) for x in (600, 1190))
    mid += rect(1420, 620, 120, 150, P["wood_l"], 5) + poly([(1410, 620), (1480, 570), (1550, 620)], P["roof_d"], 5)  # bếp phụ
    near = ground(860, P["ground2"]) + ground(880, "#8e7c58") + grass_tufts(930, 1070, 40, P["leaf_d"])
    near += "".join(line(x, 770, x, 900, 7, P["wood_d"]) for x in range(120, 480, 60)) + line(100, 810, 460, 810, 6, P["wood_d"]) + fence(1440, 1860, 950, 100)
    near += rect(560, 940, 260, 22, P["wood"], 5) + "".join(line(x, 962, x, 1030, 7, P["wood_d"]) for x in (580, 800))  # chõng
    return dict(far=far, mid=mid, near=near)
