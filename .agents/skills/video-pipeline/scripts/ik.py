"""ik.py — IK giải tích 2 khúc cho tay nhân vật (vai → khuỷu → bàn tay).

Quy ước khớp với build_rig.py: tay buông xuống = (0, +1) trong toạ độ viewBox rig (y xuống);
CSS rotate(θ) đưa (0,1) → (-sin θ, cos θ). `.arm-*` xoay quanh vai θ1; `.fore-*` lồng bên trong,
xoay quanh khuỷu một góc TƯƠNG ĐỐI φ = θ2 − θ1. Độ dài khúc lấy từ hằng số rig (SHOULDER_Y/ELBOW_Y/462).

Chỉ dùng cho nhân vật đứng/ngồi nhìn chính diện (stance stand|sit, view front): kneel/lie/3-4 làm lệch hệ trục.
"""
from __future__ import annotations

import math

L1 = 388 - 318        # cánh trên: vai → khuỷu (SHOULDER_Y → ELBOW_Y)
L2 = 462 - 388        # cẳng tay: khuỷu → tâm bàn tay


def _ang(vx: float, vy: float) -> float:
    return math.degrees(math.atan2(-vx, vy))


def fk(shoulder, up_deg: float, fore_rel_deg: float, l1: float = L1, l2: float = L2):
    """(khuỷu, bàn tay) theo góc — để kiểm IK và vẽ kiểm thử."""
    t1 = math.radians(up_deg)
    t2 = math.radians(up_deg + fore_rel_deg)
    e = (shoulder[0] - l1 * math.sin(t1), shoulder[1] + l1 * math.cos(t1))
    h = (e[0] - l2 * math.sin(t2), e[1] + l2 * math.cos(t2))
    return e, h


def solve_arm(shoulder, target, side: str = "l", l1: float = L1, l2: float = L2):
    """-> (up_deg, fore_rel_deg, reached: bool). `reached`=False khi đích xa quá tầm (tay duỗi thẳng hướng về đích).

    Khuỷu luôn gập ra ngoài/xuống (tự nhiên): chọn nghiệm có khuỷu thấp hơn, hoà thì lệch ra phía vai của `side`.
    """
    dx, dy = target[0] - shoulder[0], target[1] - shoulder[1]
    d = math.hypot(dx, dy)
    reached = True
    lo, hi = abs(l1 - l2) + 1e-3, l1 + l2 - 1e-3
    if d > hi:
        d, reached = hi, False
    d = max(d, lo)
    tt = _ang(dx, dy)
    beta = math.degrees(math.acos(max(-1.0, min(1.0, (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)))))
    best = None
    for sgn in (1, -1):
        up = tt + sgn * beta
        e, h = fk(shoulder, up, 0.0, l1, l2)
        # điểm phạt: khuỷu cao hơn vai là xấu; ưu tiên khuỷu thấp, rồi ra ngoài
        out = (e[0] - shoulder[0]) * (1 if side == "l" else -1)   # arm-l nằm bên +x của thân (xem build_rig.shoulder)
        score = (round(e[1]), out)   # y xuống: e[1] lớn = khuỷu thấp
        if best is None or score > best[0]:
            best = (score, up)
    up = best[1]
    e, _ = fk(shoulder, up, 0.0, l1, l2)
    t2 = _ang(shoulder[0] + dx - e[0], shoulder[1] + dy - e[1]) if reached else up
    fore = (t2 - up + 180) % 360 - 180
    return round(up, 2), round(fore, 2), reached
