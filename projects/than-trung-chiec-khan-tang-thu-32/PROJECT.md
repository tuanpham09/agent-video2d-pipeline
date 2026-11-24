# Thần Trùng - Chiếc Khăn Tang Thứ Ba Mươi Hai

**Luật áp dụng: RULES.md v2** (đọc `RULES.md` ở gốc repo trước mọi việc; ngoại lệ do người dùng cho phép ghi ở mục *Ngoại lệ* bên dưới)

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
- 2026-11-22 · **Roadmap v3, lần 1 (tương tác + gate)**: `build_video.py --scenes S01` → `video_demo/` (46,323 s, 13 shot). SH008 và SH012 thêm beat tường minh (word 9/17, 4/13) — gate E7 đã bắt đúng hai shot này trước khi sửa.
- 2026-11-22 · `check_shots.py --scenes S01` · OK (26 beat, 4 SFX). `hyperframes lint` 0/0; `hyperframes check --json` `ok: true`.
- 2026-11-22 · **Snapshot đã XEM** (`hyperframes snapshot --at 25.0,26.4,28.4,39.2,41.6`): `review/S01_v3_contact.jpg` và `review/S01_v3_SH012_39.2s.png`. Thấy: hai nhân vật cùng khung, ông nhìn sang chị, chị nhìn sang ông, nhân vật vẫn chính diện nên chưa "đối mặt" thật; tay mẹ vươn ra ở 28.4 s khá dài; nền và đèn đồng bộ.
- 2026-11-22 · `tests/test_roadmap_v3.py` · 25/25 qua (timing, E7/E8, tween move/look/react, check_audio với wav giả).
- 2026-11-22 · `check_audio.py` · FAIL đúng (chưa có `audio/lines/*.wav`, `voiceover.wav` — cần chạy VieNeu trên máy).
- Chưa kiểm: giọng thật; khẩu hình theo biên độ; đi bộ có bước chân (rig chưa có pose walk); SFX nghe thử.

- 2026-11-22 · `check_rules.py --project projects/<slug> --phase final` · 0 lỗi, 5 cảnh báo (generator preview cũ chứa hex).
- 2026-11-22 · `library.py check` · 35 asset, 0 lỗi. `LIBRARY.lock.json` khớp.
- 2026-11-22 · `build_rig.py --bible … --script …` · 5 rig OK (kiểm giải tích tràn khung + khớp script). Pose sheet 5 nhân vật chính: **chưa người dùng duyệt**.
- 2026-11-22 · `check_shots.py --scenes S01` · OK (shotlist 13 shot phủ hết S01).
- 2026-11-22 · `build_video.py --until SH010` → `video_demo/` (34,402 s) · `hyperframes lint` 0/0; `hyperframes check --json` `ok: true`; snapshot 10 điểm đã xem.
- 2026-11-24 · **M5 (góc nhìn 3/4)**: rig 5 nhân vật build lại có `data-view` (front|tq-r|tq-l). Ảnh đã XEM: `.agents/skills/video-pipeline/references/review/m5-host-3q-sheet.png` (pose sheet host) và `m5-sh008-tq-snapshot.png` (SH008, host tq-r / me tq-l, thấy hai người quay mặt vào nhau). Người dùng đã duyệt sheet host ("ổn rồi"). Lỗi nhỏ còn lại: nếp nhăn/sẹo sát mép mặt ở góc 3/4 (me, ba_noi). Shotlist thật chưa dùng `view`.
- 2026-11-24 · **Hành vi mẫu (macro)**: `library/behaviors/behaviors.json` (12 macro) + `scripts/behaviors.py`; `check_shots` thêm E9. Ảnh đã XEM: `library/sheets/behaviors.png` (trước/sau, host + me; phần chuyển động chưa xem được trên ảnh tĩnh). Chuyển 8 beat S01 sang macro (SH002 chi_tay, SH003/SH008 cham_khan, SH005 lo_lang, SH008/SH012 nghe_gat, SH012 chap_tay + nhin_sang; giữ `do` gốc). `build_video.py` dựng lại 13 shot: HTML từng shot và `index.html` giống hệt trước khi chuyển. `check_shots --scenes S01` OK; `check_rules --phase demo` 0 lỗi; `validate_schemas` 0 lỗi; `tests/test_roadmap_v3.py` qua hết. Mức tiết kiệm trên S01 (26 beat + SFX): 4149 → 3844 ký tự (−7%) giữ `do`, 3465 (−16%) nếu bỏ `do` ở beat macro; chỉ 8/26 beat có macro tương ứng. Chưa chạy `hyperframes check`, chưa xem snapshot mới (HTML đã giống hệt bản đã xem).

- 2026-11-24 · **Hành động mới (người dùng: "chưa có quỳ lạy, chạy, ngất…")**: rig thêm `stance` kneel|lay|stagger|tilt|lie (+ `-r`), `pose` run-a/run-b|cover-head|pray|prostrate; `move.gait: run`; 6 macro (`quy_xuong`, `quy_lay`, `dung_day`, `chay_toi`, `om_dau`, `ngat`); gate E10 (giá trị set ∈ rig.json, gait). Ảnh đã XEM: `references/review/actions-host-sheet.png` (pose sheet host, mục Hành động), `references/review/actions-sh008-contact.png` (snapshot SH008 thử: chạy → quỳ → ôm đầu → loạng choạng → nghiêng → nằm). Lỗi đã sửa sau khi xem: tay chạy vung chéo ngực (đổi dấu góc), nghiêng đổ tràn khung (thêm dịch ngang), váy quỳ tràn dưới sàn (kéo lên 22 px), nằm đè lên người đứng cạnh (thêm `-r`). Còn lại: người nằm vẫn dài ~480 px nên có thể đè nhân vật kề bên (ghi ở library/README); quỳ nhìn chính diện giống ngồi trên đệm; lạy là phép gần đúng (thân dẹt, hai tay chống). Shotlist thật chưa dùng hành động nào; HTML các shot thật chỉ khác ở phần nhúng rig (đã so, tween/index giống hệt). Chưa có SFX bước chân/chạy; SFX ngã/quỳ dùng `impact-deep-soft`/`impact-medium-soft` (chưa nghe thử). Pose sheet 4 nhân vật còn lại chưa xem lại.

- 2026-11-24 · **Quỳ nhìn nghiêng** (người dùng: "quỳ hiển thị hơi ngang người mới thấy rõ dáng quỳ"): thêm `kleg` (đùi chìa về phía mặt quay, cẳng chân gập sát đất, gót giày dựng) hiện khi `stance` kneel|lay và `view` tq-r|tq-l; macro `quy_xuong`/`quy_lay` có tham số `view` (mặc định tq-r), `dung_day` trả về front. Ảnh đã XEM: `references/review/kneel-side-sheet-row.png` (host kneel tq-r/tq-l/lay tq-r) và `references/review/kneel-side-sh008.png` (SH008 thử: host quỳ nghiêng quay sang me, thấy gối và gót). Đã sửa sau khi xem: lần đầu chân bị thân che hết → kéo gối/gót ra ngoài thân. Chưa kiểm: người dùng duyệt; lạy nghiêng chỉ xem ở sheet, chưa xem trong shot; 4 nhân vật còn lại chưa xem lại pose sheet.

- **Chưa làm / chưa kiểm:** giọng thật (`audio/voiceover.wav` không có trong repo → demo chưa có tiếng), nghe thử SFX, render mp4, khung 9:16, 👤 duyệt demo (R8.1). Chưa có shotlist cho S02–S20.

## Ghi chú / bài học

- Tạo mới (không có sẵn trong library): 5 nhân vật chính dùng archetype+outfit của library, ngoại hình riêng (sẹo, mắt đục, râu) khai trong `bible.json` — chưa promote vì là biến thể của project.
- HyperFrames bỏ cả khối `<style>` nếu selector có `>` (xem HANDOFF).

## Ngoại lệ so với RULES.md

- **2026-11-22 — RULES.md v1 → v2 (R0.2/R0.3).** Người dùng yêu cầu trực tiếp trong phiên: "sửa R10 và đề xuất R11/R12 để nâng RULES.md lên v2", theo plan `references/roadmap-v3.md`. Agent chỉ thực hiện theo chỉ thị đó; không tự đổi luật. Nội dung R10–R12 là đề xuất chờ người dùng xem lại.
