# HANDOFF — thư viện bối cảnh dùng chung (cập nhật mỗi commit)

Nhánh: `claude/workflow-v2` (PR #1). Agent tiếp theo: đọc file này + `AGENTS.md` (rule bắt buộc) trước.

## Mục tiêu
Bộ bối cảnh 2D đa dạng, tái sử dụng cho mọi video: `assets/library/bg/<id>.svg` + `catalog.json`.
Rule: **dùng sẵn trước, thiếu mới tạo** (AGENTS.md điều 9). Bối cảnh mới → thêm hàm vào `bg_lib/`, chạy lại `build_bg.py`, clone từ cảnh gần nhất.

## Cách dùng
- Build: `python .agents/skills/video-pipeline/scripts/build_bg.py [--only id1,id2] [--no-sheet]` → SVG + `catalog.json` + `assets/library/bg/sheets/contact.png` (cần playwright+chromium; xem contact.png để duyệt).
- SVG: viewBox 1920×1080, 3 lớp `.layer.far|mid|near` (parallax). Ánh sáng: `data-light` trên `<svg>` = `day|dusk|night|dark|red_flash` (ngoài trời) hoặc `day|candle_warm|dark|red_flash` (trong nhà). Cắt dọc 9:16: viewBox `656 0 608 1080`; tiêu điểm trong dải giữa.
- Mã nguồn: `scripts/bg_lib/{core.py (primitive+CSS), batch*.py (bối cảnh), sheet.py}`; đăng ký bằng `@register(id, tên, kind, tags, focus=...)`.

## Danh sách mục tiêu & trạng thái
Xong (đợt 1, `batch1.py`): nghia_dia, toan_canh_lang, gian_tho_dem, bo_song, gieng_lang, bui_tre_chuoi
Xong (đợt 2, `batch2.py`): truong_bo_hoang, nha_hoang, canh_dong_lua, rap_dam_tang, nui, chua
Còn lại (đợt 3+ → `batch3.py`…, nhớ `from . import batchN` trong `bg_lib/__init__.py`; commit sau mỗi đợt): nha_ve_sinh, mieu_dinh, song, cay_da, san_nha, nha_bep, phong_ngu, phong_khach, nha_co_nha_tho_ho, nha_cap_bon
(`toan_canh_lang` dùng cho cả "Toàn cảnh làng/ngôi làng".)

## Việc còn lại khác
- PR #1: đã sửa 19 review thread (chưa resolve thread nào trên GitHub); chưa có CI chạy gate.
- Chưa kiểm bối cảnh trong HyperFrames thật; chưa nhúng bối cảnh vào `bible.json` `locations` (cần map id thư viện → `light_states` từ catalog).
- Chưa test các trạng thái ánh sáng bằng ảnh cho từng cảnh (chỉ test light mặc định `day`).
