# -*- coding: utf-8 -*-
"""Mốc đứng của 22 cảnh sinh bằng code (nguồn duy nhất; import_bg.py đọc ở đây).

floor_y = đường chân (mặt đất/sàn nơi nhân vật đứng), s = tỉ lệ rig (520×600, chân ở (260,580)),
dx = khoảng cách L/R so với C, cx = tâm khung cắt 9:16 (608×1080) và cũng là x của C.
Đã ghép nhân vật `host` vào từng cảnh ở khung 9:16 để chỉnh (B5); số nhỏ s cho cảnh toàn/xa.
"""

ANCHORS = {
    # id:               (floor_y, s,   cx,   dx)
    "nghia_dia":         (930, 0.80,  960, 380),
    "toan_canh_lang":    (960, 0.55,  960, 380),
    "gian_tho_dem":      (980, 0.85,  960, 380),
    "bo_song":           (920, 0.75,  960, 380),
    "gieng_lang":        (940, 0.80,  960, 380),
    "bui_tre_chuoi":     (960, 0.85,  960, 380),
    "truong_bo_hoang":   (940, 0.80,  960, 380),
    "nha_hoang":         (940, 0.80,  960, 380),
    "canh_dong_lua":     (980, 0.60,  960, 380),
    "rap_dam_tang":      (970, 0.80,  960, 380),
    "nui":               (980, 0.55,  960, 380),
    "chua":              (980, 0.75,  960, 380),
    "nha_ve_sinh":       (940, 0.80,  960, 380),
    "mieu_dinh":         (1010, 0.75, 960, 380),
    "song":              (1010, 0.60, 960, 380),
    "cay_da":            (960, 0.80,  960, 380),
    "san_nha":           (970, 0.80,  960, 380),
    "nha_bep":           (990, 0.85,  900, 380),
    "phong_ngu":         (990, 0.85,  760, 380),
    "phong_khach":       (1000, 0.85, 960, 380),
    "nha_co_nha_tho_ho": (1010, 0.75, 960, 380),
    "nha_cap_bon":       (990, 0.80,  960, 380),
}
