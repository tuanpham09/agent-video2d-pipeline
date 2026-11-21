# HANDOFF — thư viện bối cảnh dùng chung (cập nhật mỗi commit)

Nhánh: `claude/workflow-v2` (PR #1). Agent tiếp theo: đọc file này + `AGENTS.md` (rule bắt buộc) trước.

## Mục tiêu
Bộ bối cảnh 2D đa dạng, tái sử dụng cho mọi video: `assets/library/bg/<id>.svg` + `catalog.json`.
Rule: **dùng sẵn trước, thiếu mới tạo** (AGENTS.md điều 9). Bối cảnh mới → thêm hàm vào `bg_lib/`, chạy lại `build_bg.py`, clone từ cảnh gần nhất.

## Cách dùng
- Build: `python .agents/skills/video-pipeline/scripts/build_bg.py [--only id1,id2] [--no-sheet]` → SVG + `catalog.json` + `assets/library/bg/sheets/contact.png` (cần playwright+chromium; xem contact.png để duyệt).
- SVG: viewBox 1920×1080, 3 lớp `.layer.far|mid|near` (parallax). Ánh sáng: `data-light` trên `<svg>` = `day|dusk|night|dark|red_flash` (ngoài trời) hoặc `day|candle_warm|dark|red_flash` (trong nhà). Cắt dọc 9:16: viewBox `656 0 608 1080`; tiêu điểm trong dải giữa.
- Mã nguồn: `scripts/bg_lib/{core.py (primitive+CSS), batch*.py (bối cảnh), sheet.py}`; đăng ký bằng `@register(id, tên, kind, tags, focus=...)`.

## Nâng cấp truyện ma (đang làm theo 4 bước, commit mỗi bước)
- [x] B1+B2: `data-mood="creepy"` (sương dày, vignette đậm, nhiễu hạt, tint u ám) + ánh sáng có chiều sâu (xa nhạt/gần tối) + vùng sáng quanh nến/đèn (`.pool`, `.pool2`) — trong `core.py`.
- [ ] B3: lớp chi tiết rợn `.creep` cho từng cảnh — `bg_lib/creep.py` (`CREEP[id]() -> {far,mid,near}`), chỉ hiện khi `data-mood="creepy"`.
- [ ] B4: sửa cảnh yếu: nha_hoang (đổ nát thật), truong_bo_hoang, bui_tre_chuoi (lá chuối thiếu thân → sửa `banana()` trong core), nha_ve_sinh, canh_dong_lua.
- [ ] B5 (chưa làm): xem 9:16 crop + dùng thử trong HyperFrames với 1 video thật.

## Danh sách bối cảnh — XONG 22/22 (`catalog.json` là nguồn đúng)
- đợt 1 `batch1.py`: nghia_dia, toan_canh_lang, gian_tho_dem, bo_song, gieng_lang, bui_tre_chuoi
- đợt 2 `batch2.py`: truong_bo_hoang, nha_hoang, canh_dong_lua, rap_dam_tang, nui, chua
- đợt 3 `batch3.py`: nha_ve_sinh, mieu_dinh, song, cay_da, san_nha, nha_bep (helper `room_shell()` cho cảnh trong nhà)
- đợt 4 `batch4.py`: phong_ngu, phong_khach, nha_co_nha_tho_ho, nha_cap_bon
- `toan_canh_lang` dùng cho cả "Toàn cảnh làng/ngôi làng". Đã xem `sheets/contact.png` (cảnh) và `sheets/light-test.png` (ánh sáng: candle_warm, red_flash, night, dark, dusk đều chạy).

## Gợi ý bối cảnh nên thêm khi có video cần (clone từ cảnh gần nhất)
cầu / đường làng ban đêm, hành lang bệnh viện / trạm xá, chợ quê, hầm / hang, rừng sâu, ao / đầm sen, cổng làng, nhà tập thể, tầng gác mái, quán nước đầu làng.

## Việc còn lại khác
- PR #1: đã sửa 19 review thread (chưa resolve thread nào trên GitHub); chưa có CI chạy gate.
- Chưa kiểm bối cảnh trong HyperFrames thật; chưa nhúng bối cảnh vào `bible.json` `locations` (cần map id thư viện → `light_states` từ catalog).
- Ánh sáng mới test mẫu 6 cảnh (light-test.png), chưa test từng cảnh × từng trạng thái.
- Chưa có script đo tràn/validate cho bối cảnh (chỉ kiểm XML hợp lệ); focus point trong catalog là ước lượng.
- Bối cảnh ngoài trời `kind=exterior` có trăng + `lamp` glow; nến/đèn dùng `focus` — cần chỉnh `focus`/`lamp` theo từng shot nếu lệch.
