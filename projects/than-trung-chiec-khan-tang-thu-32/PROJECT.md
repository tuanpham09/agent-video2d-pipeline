# Thần Trùng - Chiếc Khăn Tang Thứ Ba Mươi Hai

**Luật áp dụng: RULES.md v1** (đọc `RULES.md` ở gốc repo trước mọi việc; ngoại lệ do người dùng cho phép ghi ở mục *Ngoại lệ* bên dưới)

- Slug: `than-trung-chiec-khan-tang-thu-32`
- Format: 16:9 (1920×1080 @ 30fps)
- Tạo ngày: 2026-11-19

## Trạng thái

- [ ] 0. Brief — người xem, promise, kênh đích
- [ ] 1. Transcript + metadata (`source/`)
- [ ] 2. Kịch bản (`script/script.md`, `script/script.json`) — đã duyệt
- [ ] 3. Giọng đọc (`audio/voiceover.wav`, `audio/manifest.json`) — đã nghe
- [ ] 4. Dựng HyperFrames (`video/`) — preview đã duyệt
- [ ] 5. Render + QC (`output/final.mp4`)
- [ ] 6. Đóng gói (`output/publish.md`)

## Nhật ký gate (ngày · lệnh · kết quả)

- 2026-11-22 · `check_rules.py --project projects/<slug> --phase final` · 0 lỗi, 5 cảnh báo (generator preview cũ chứa hex).
- 2026-11-22 · `library.py check` · 35 asset, 0 lỗi. `LIBRARY.lock.json` khớp.
- 2026-11-22 · `build_rig.py --bible … --script …` · 5 rig OK (kiểm giải tích tràn khung + khớp script). Pose sheet 5 nhân vật chính: **chưa người dùng duyệt**.
- 2026-11-22 · `check_shots.py --scenes S01` · OK (shotlist 13 shot phủ hết S01).
- 2026-11-22 · `build_video.py --until SH010` → `video_demo/` (34,402 s) · `hyperframes lint` 0/0; `hyperframes check --json` `ok: true`; snapshot 10 điểm đã xem.
- **Chưa làm / chưa kiểm:** giọng thật (`audio/voiceover.wav` không có trong repo → demo chưa có tiếng), nghe thử SFX, render mp4, khung 9:16, 👤 duyệt demo (R8.1). Chưa có shotlist cho S02–S20.

## Ghi chú / bài học

- Tạo mới (không có sẵn trong library): 5 nhân vật chính dùng archetype+outfit của library, ngoại hình riêng (sẹo, mắt đục, râu) khai trong `bible.json` — chưa promote vì là biến thể của project.
- HyperFrames bỏ cả khối `<style>` nếu selector có `>` (xem HANDOFF).

## Ngoại lệ so với RULES.md

- (chưa có)
