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


# Giới hạn khớp mặc định (độ) — rộng hơn mọi pose đã duyệt trong build_rig.POSES (|up| tới 150°, |fore| tới 135°).
# arm-l: vai âm = dang/giơ ra phía +x; arm-r đối xứng (đổi dấu). Ghi đè theo beat bằng "limits": {"up":[a,b],"fore":[a,b]} (độ, phía arm-l).
LIMITS = {"up": (-165.0, 15.0), "fore": (-150.0, 100.0)}


def side_limits(side: str, limits=None):
    lim = limits or LIMITS
    up, fo = lim["up"], lim["fore"]
    return ((up[0], up[1]), (fo[0], fo[1])) if side == "l" else ((-up[1], -up[0]), (-fo[1], -fo[0]))


def _wrap(a: float) -> float:
    return (a + 180) % 360 - 180


def solve_arm(shoulder, target, side: str = "l", l1: float = L1, l2: float = L2, limits=None):
    """-> (up_deg, fore_rel_deg, reached: bool). `reached`=False khi đích xa quá tầm HOẶC mọi nghiệm đều vượt giới hạn khớp
    (khi đó góc bị kẹp vào giới hạn: bàn tay dừng ở điểm gần nhất, không bẻ khớp ngược).

    Hai nghiệm khuỷu: bỏ nghiệm vi phạm giới hạn khớp; còn cả hai thì chọn khuỷu thấp hơn, hoà thì lệch ra phía vai của `side`.
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
    (u_lo, u_hi), (f_lo, f_hi) = side_limits(side, limits)
    cands = []
    for sgn in (1, -1):
        up = _wrap(tt + sgn * beta)
        e, _ = fk(shoulder, up, 0.0, l1, l2)
        t2 = _ang(shoulder[0] + dx - e[0], shoulder[1] + dy - e[1]) if reached else up
        fore = _wrap(t2 - up)
        ok_lim = u_lo - 1e-6 <= up <= u_hi + 1e-6 and f_lo - 1e-6 <= fore <= f_hi + 1e-6
        out = (e[0] - shoulder[0]) * (1 if side == "l" else -1)   # arm-l nằm bên +x của thân (xem build_rig.shoulder)
        cands.append((ok_lim, round(e[1]), out, up, fore))       # y xuống: e[1] lớn = khuỷu thấp
    feas = [c for c in cands if c[0]]
    if feas:
        _, _, _, up, fore = max(feas, key=lambda c: (c[1], c[2]))
    else:                                                          # không nghiệm nào hợp lệ: kẹp nghiệm gần giới hạn nhất
        reached = False
        _, _, _, up, fore = max(cands, key=lambda c: (c[1], c[2]))
        up, fore = min(max(up, u_lo), u_hi), min(max(fore, f_lo), f_hi)
    return round(up, 2), round(fore, 2), reached


HIP = (260.0, 470.0)        # tâm xoay thân trên (CX, HIP_Y của build_rig)
EYE = (260.0, 215.0)        # tâm mắt trong toạ độ rig (build_rig: tâm nét mặt y=215)
LEAN_MAX = 9.0              # độ nghiêng thân tối đa khi với tay


def rot_about(pt, deg: float, c=HIP):
    """Xoay điểm theo CSS rotate(deg) quanh c (y xuống: dương = thuận chiều kim đồng hồ, đỉnh thân đổ sang +x)."""
    a = math.radians(deg)
    dx, dy = pt[0] - c[0], pt[1] - c[1]
    return (c[0] + dx * math.cos(a) - dy * math.sin(a), c[1] + dx * math.sin(a) + dy * math.cos(a))


def lean_for(target, shoulder) -> float:
    """Độ nghiêng thân (độ) khi đưa tay tới `target` (toạ độ rig, thế giới): nghiêng về phía đích theo độ lệch ngang."""
    k = (target[0] - shoulder[0]) / (0.8 * (L1 + L2))
    return round(LEAN_MAX * max(-1.0, min(1.0, k)), 2)


def solve_arm_leaned(shoulder, target, side: str, lean: float, limits=None):
    """IK trong hệ của nhóm `.upper` đang nghiêng `lean` độ: đưa đích về hệ cục bộ rồi giải như thường.
    Trả (up, fore, reached) — góc áp thẳng cho .arm/.fore vì chúng nằm trong .upper."""
    return solve_arm(shoulder, rot_about(target, -lean), side, limits=limits)


def hand_world(shoulder, up: float, fore: float, lean: float):
    """Bàn tay (toạ độ rig thế giới) khi thân nghiêng `lean` độ."""
    return rot_about(fk(shoulder, up, fore)[1], lean)


def gaze_px(eye_xy, target_xy, scale: float):
    """(gx, gy) px cho --gx/--gy: ánh mắt từ `eye_xy` tới `target_xy` (toạ độ cảnh). Biên độ như GAZE của rig (5 ngang, 4 dọc)."""
    dx, dy = target_xy[0] - eye_xy[0], target_xy[1] - eye_xy[1]
    d = math.hypot(dx, dy) or 1.0
    k = min(1.0, d / (40 * scale))      # đích sát mắt thì liếc nhẹ, xa thì liếc hết cỡ
    return round(5 * dx / d * k, 2), round(4 * dy / d * k, 2)
