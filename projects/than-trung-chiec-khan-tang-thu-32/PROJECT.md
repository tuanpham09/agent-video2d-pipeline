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

- 2026-11-24 · **Chuỗi ghép sẵn + tự quay mặt**: 5 macro nhiều bước (`cau_xin` quỳ→lạy→ngẩng, `chay_roi_om_dau`, `soc_roi_ngat`, `so_roi_bo_chay`, `vai_chao`; nhịp chỉnh bằng tham số `gap`/`after`/`dur`, SFX đi theo nhịp) — tổng 23 macro. `beat.set {view: "auto"}` (và mặc định của `quy_xuong`/`quy_lay`/`cau_xin`) quay mặt về nhân vật gần nhất tại thời điểm beat (`facing_view` trong build_video.py; không tự quay lại khi người kia di chuyển; chưa hỗ trợ `characters[].view: auto`, sẽ báo lỗi rõ). Ảnh đã XEM: `references/review/combos-sh008-contact.png` (SH008 thử: host quỳ quay về me → lạy rạp → me loạng choạng rồi nằm; thấy auto-face đúng hướng tq-r). Lỗi thấy: me nằm ngang đè lên host đang quỳ (cố ý đặt gần để thử; là hạn chế dàn cảnh đã ghi). Test: `tests/test_roadmap_v3.py` qua hết (thêm 9 kiểm: nhịp + SFX từng macro, auto-face hai hướng, E10 chấp nhận view=auto); `check_shots --scenes S01`, `check_rules --phase demo`, `library.py check`, `validate_schemas`, `behaviors.py check` sạch. Sửa kèm: regex tham số macro không nhận tên có chữ số (gap2). Chưa kiểm: chưa dùng chuỗi nào trong shotlist thật; SFX chưa nghe thử; chưa chạy `hyperframes check`.

- **Chưa làm / chưa kiểm:** giọng thật (`audio/voiceover.wav` không có trong repo → demo chưa có tiếng), nghe thử SFX, render mp4, khung 9:16, 👤 duyệt demo (R8.1). Chưa có shotlist cho S02–S20.

## Ghi chú / bài học

- Tạo mới (không có sẵn trong library): 5 nhân vật chính dùng archetype+outfit của library, ngoại hình riêng (sẹo, mắt đục, râu) khai trong `bible.json` — chưa promote vì là biến thể của project.
- HyperFrames bỏ cả khối `<style>` nếu selector có `>` (xem HANDOFF).

## Ngoại lệ so với RULES.md

- **2026-11-22 — RULES.md v1 → v2 (R0.2/R0.3).** Người dùng yêu cầu trực tiếp trong phiên: "sửa R10 và đề xuất R11/R12 để nâng RULES.md lên v2", theo plan `references/roadmap-v3.md`. Agent chỉ thực hiện theo chỉ thị đó; không tự đổi luật. Nội dung R10–R12 là đề xuất chờ người dùng xem lại.

### 2026-11-25 — Merge `origin/claude/opt-round3` (fix-pr1-gaps + opt-round2 + opt-round3) vào workflow-v2
- Xung đột duy nhất: `check_shots.py`. Hai bên cùng đặt E9/E10 → **đổi số phía macro**: E12 = beat/macro chỉ nhắc nhân vật/đạo cụ có mặt trong shot (+ kiểm thư viện macro); E13 = giá trị `set` (kể cả `view`) ∈ rig.json, `move.gait` ∈ walk|run. E9 = pose có trong rig, E10 = chân đè đạo cụ, E11 = focus (của opt-round3) giữ nguyên.
- Test: sửa 2 test cho khớp (E12/E13; test E9 thêm beat `set` tường minh vì S01 đã dùng macro); 2 đoạn end-to-end cần `projects/demo-30s-than-trung` (không có trong repo) → BỎ QUA có báo.
- Đã chạy: `test_roadmap_v3.py` 102 ✓ / 0 ✗; `check_shots --scenes S01` OK; `check_sync` OK; `check_rules --phase demo` 0 lỗi; `behaviors.py check` 23 macro 0 lỗi; `library.py check` 0 lỗi; `validate_schemas` OK; `build_video --scenes S01` + `hyperframes lint` 0 lỗi/0 cảnh báo.
- Chưa kiểm: render thật (--workers/--resume/cache), thời gian/RAM, `hyperframes check`, SFX nghe thật. HTML sinh ra khác bản trước merge (do thay đổi generator của opt-round3) — chưa xem lại ảnh sau merge.

### 2026-11-25 — Prototype IK tay (beat `reach`)
- Thêm `scripts/ik.py` (IK 2 khúc), CSS rig dùng `var(--ik-*, góc pose)` (build lại 5 rig), beat `reach` trong generator/schema/check_shots (E12 kiểm prop/char; E7 tính là hành vi), macro STEP_KEYS có `reach`. Chưa đổi shotlist thật.
- Chạy: `test_roadmap_v3.py` (mục IK, tất cả qua); build SH008 bản thử trong /tmp + `hyperframes snapshot`.
- Ảnh đã XEM: `.agents/skills/video-pipeline/references/review/ik-reach-sh008-contact.jpg` — thấy host và me giơ tay chạm nhau, khuỷu gập xuống/ra ngoài, hết hold thì tay về đúng pose cũ (clasp / chỉ tay). Lỗi đã sửa: ban đầu chọn nghiệm khuỷu hất lên cao (tay vắt lên mặt) → sửa tiêu chí chọn khuỷu thấp.
- Chưa kiểm: bàn tay chạm đúng pixel đạo cụ thật; `hand_over` bằng IK; render mp4; `hyperframes check`; rig không phải host/me.

### 2026-11-25 — hand_over bằng IK, đạo cụ bám bàn tay (bước a)
- `hand_over` viết lại: IK + lấy mẫu FK 1/24 s; thêm `held`; đạo cụ vẽ trên nhân vật. **Sửa lỗi nền**: tween vị trí đạo cụ nhắm nhầm `<g>` (không có x/y) → đạo cụ chưa từng di chuyển; nay có `id="<pid>-pos"` trên `<svg>` ngoài. Test cũ chỉ kiểm chuỗi nên không bắt được.
- Test `test_roadmap_v3.py` qua (mẫu ≥20, tween --ik-*, báo lỗi đạo cụ ngoài tầm).
- Ảnh đã XEM: `.agents/skills/video-pipeline/references/review/ik-handover-sh008-contact.jpg` — mâm tre theo tay me, tới điểm gặp, host nhận và mang về tay nghỉ; hai tay thả về pose cũ. Lỗi thấy: lần đầu mâm đứng yên trên sàn (bug nhắm nhầm `<g>`) → sửa; bàn tay chồng lên giữa mâm chứ chưa nắm mép.
- Chưa kiểm: SFX khớp thời điểm trao, render mp4, `hyperframes check`, shotlist thật (chưa dùng hand_over), nhân vật khác ngoài host/me.

### 2026-11-25 — Thân nghiêng + mắt nhìn theo đạo cụ (bước b)
- Rig: thêm nhóm `.upper` (xoay theo `--lean` quanh hông); build lại 5 rig. `ik.py`: `solve_arm_leaned`, `hand_world`, `lean_for`, `gaze_px`. `reach` và `hand_over` đặt `--lean`, `--gx/--gy` rồi `clearProps`.
- Test `test_roadmap_v3.py` qua (IK có nghiêng trúng đích <1.5 px, --lean/--gx có trong HTML, rig có `.upper`); `library.py check`, `check_shots` S01, `check_rules --phase demo` sạch; build S01 + `hyperframes lint` sạch.
- Ảnh đã XEM: `references/review/ik-lean-gaze-sh008.png` (me nghiêng về phía host, đồng tử hai người liếc xuống mâm, mâm ở giữa hai tay) và `references/review/rig-upper-lineup.png` (5 rig không đổi hình sau khi thêm `.upper`). Lỗi thấy: nghiêng 9° khá kín đáo; hai tay vẫn chồng lên giữa mâm chứ chưa nắm mép.
- Chưa kiểm: render mp4, `hyperframes check`, SFX, kneel/3-4/lie với `.upper`, nhân vật ngoài host/me, shotlist thật.

### 2026-11-25 — Giới hạn khớp + điểm nắm đạo cụ (bước c)
- `ik.py`: `LIMITS`, `side_limits`, nghiệm vi phạm bị loại / kẹp; `build_video`: `_solve_checked` báo lỗi "trượt đích"; `limits` theo beat. `library/index.json`: thêm `grip` cho `bamboo_tray` (a,b) và `oil_lamp` (a) — chỉ thêm (R2.3). `hand_over`: bàn tay cầm mép đạo cụ, điểm gặp chọn để hai tay duỗi vừa phải.
- Lỗi thấy khi chạy: với điểm nắm ở mép gần người cho, điểm gặp cũ (giữa hai vai) khiến tay người cho gập sát ngực, vượt giới hạn khuỷu (trượt 52 px) → đổi sang quét điểm gặp theo độ duỗi tay.
- Test `test_roadmap_v3.py` TẤT CẢ QUA (giới hạn khớp cả hai tay, dải tuỳ biến, grip trong index); `library.py check` 0 lỗi.
- Ảnh đã XEM: `.agents/skills/video-pipeline/references/review/ik-grip-sh008-contact.jpg` — người cho cầm mép phải mâm, host cầm mép trái, mâm ở giữa hai tay, hết beat hai tay về pose cũ; mâm dừng ở hông host sau khi nhận (hơi lơ lửng trước bụng).
- Chưa kiểm: nắm đèn dầu thật (`oil_lamp`, vị trí grip a=(0.5,0.85) chỉ ước theo ảnh SVG, chưa thử trong cảnh), SFX, render mp4, `hyperframes check`, shotlist thật.

### 2026-11-25 — Chỉ mục rig + `library.py suggest`
- Thêm `keywords`/`tags` cho 10 đạo cụ, 25 bối cảnh, 11 archetype, 9 outfit; `library/rigs/cast.json` (5 nhân vật đã dựng: host, ông Cửu, mẹ, bà nội, thần trùng) + `library/sheets/cast/*.png` + `cast-lineup.png`; `library/lexicon.json`. Lệnh mới: `cast-add`, `suggest`; `list --kind cast`, `--tag` lọc được archetype/outfit/cast; `check` kiểm cast (archetype/outfit/sheet/keywords).
- Test `test_roadmap_v3.py` TẤT CẢ QUA (9 ca mới). Thử `suggest --text` với truyện KHÁC (cô gái, bà cụ, nghĩa địa, bờ sông…): gợi ý đúng 4 bối cảnh, 3 đạo cụ, cast bà cụ + bóng ma, archetype `young_adult_f`, và báo THIẾU `gương`, `búp bê`.
- Ảnh đã XEM: `library/sheets/cast/thay_cung_ong_gia.png` (pose sheet ông Cửu đủ biểu cảm/pose/góc nhìn/hành động; ảnh rất dài 3072×9768) và `library/sheets/cast-lineup.png` (5 nhân vật). Lỗi thấy khi chạy: ban đầu "mẹ" bị gợi ý `elder_f` vì câu "Chung giọng… với Bà nội" → lọc câu nhắc người khác; "tang" làm rạp đám tang vượt gian thờ ở S01 → hạ trọng số tag.
- Chưa kiểm: `suggest` trên kịch bản thứ hai thật (mới thử một đoạn văn); chất lượng với kịch bản dài hơn/khác thể loại; cast chưa có nhân vật trẻ em/thiếu niên (archetype có nhưng chưa dựng+duyệt).

### 2026-11-26 — Dựng 6 nhân vật phụ còn thiếu rig + đưa vào cast
- Tạo mới (lý do: không có cast/rig nào dùng được cho các vai này): `bo`, `chu_hai`, `chu_ut`, `ngan`, `be_na`, `vy` (clone archetype+outfit, R2.8/R10.3). `lam_that` giữ nguyên: chỉ có tiếng trong hũ, không cần rig. Tuổi/ngoại hình không có trong nguồn đều ghi là "đề xuất thiết kế" (R7.1); chỉ Na 5 tuổi và Chú Út mất sau 3 ngày là từ nguồn.
- Mở rộng library/generator (chỉ thêm, R2.3): token `hair_grey`, `brow_grey` (base.json); `build_rig.py` thêm kiểu tóc `bob`, tham số `mustache`, `beard_color`.
- `build_rig.py` → 11 rig, 0 tổ hợp tràn khung. `library.py cast-add` ×6 → cast 11 mục; `library.py check` 0 lỗi; `test_roadmap_v3.py` TẤT CẢ QUA (đổi ca test suggest sang `lam_that` vì `chu_hai` đã có rig); `check_rules --phase demo` 0 lỗi, 5 cảnh báo cũ; `check_sync` OK; `check_shots` 401 lỗi đều là "S02+ chưa có shot" (đã có từ trước, không có lỗi loại khác).
- Ảnh đã XEM: `assets/rig/sheets/lineup.png` (11 nhân vật), `bo.png`, `be_na.png`, và hàng cảm xúc calm/focused/worried của `chu_ut`, `vy`, `chu_hai`. Lỗi thấy và đã sửa: lần build đầu Bố/Chú Út/Lâm và Ngân/Vy/Mẹ có silhouette gần giống nhau → thêm tóc muối tiêu + thân rộng (Bố), ria mép (Chú Út), râu đen (Chú Hai), tóc bob (Vy); xem lại lineup thấy tách được. Một "vòng cung nổi trên đầu" trong ảnh crop hoá ra là lỗi cắt ảnh của mình, không phải lỗi rig.
- Chưa kiểm: người dùng chưa duyệt pose sheet (R3.7); chỉ xem hàng cảm xúc, chưa xem hết pose/stance/gaze của 6 người; Chú Hai (áo `plain_light`) gần màu áo tang nên khác biệt chủ yếu nhờ khăn/râu; chưa ghép vào cảnh thật cạnh nhau; chưa thử `reach`/IK với bé Na (tay ngắn).

### 2026-11-26 — 👤 Người dùng duyệt pose sheet 6 nhân vật phụ
- Người dùng: "ok duyệt" (phiên 2026-11-26) cho pose sheet `bo`, `chu_hai`, `chu_ut`, `ngan`, `be_na`, `vy` (R3.7). Phạm vi duyệt là các ảnh mình đã trình ở trên; phần chưa xem hết (pose/stance/gaze) vẫn là "chưa kiểm" của mình.
- Việc tiếp: ghép thử 11 nhân vật vào cảnh thật (rạp đám tang, gian thờ) để kiểm tỉ lệ/vị trí đứng, hoặc đưa `reach`/`hand_over` (đèn dầu) vào shotlist; chờ người dùng chọn.

### 2026-11-26 — Rà và đóng todo #14, #15, #23
- #14 walk: `build_rig.POSES/LEG_POSES` có `walk-a`/`walk-b`; pose sheet `host.png` có hàng walk (xem `walk-b`: hai chân ngược pha). Generator có `move.gait`; test "chạy: move có gait=run" qua.
- #15 quay 3/4: `VIEWS = front|tq-r|tq-l`; pose sheet có mục "GÓC NHÌN 3/4" (thân + mặt tq-r/tq-l, nhiều cảm xúc) và kneel/lay nhìn nghiêng; generator hỗ trợ `set.view` và `view: auto` (test auto-face qua). Hạn chế đã biết: lie/kneel nhìn nghiêng còn đơn giản.
- #23 macro: `library/behaviors/behaviors.json` 23 macro, `behaviors.py check` 0 lỗi, `build_video.py` bung macro (`expand_shot`), schema có `macro`, test bung/SFX/E12 qua; shotlist S01 dùng 8 beat macro. B1 (thống kê beat) không có tài liệu riêng: số liệu tính lại hôm nay trên S01 = 26 beat (`line_id` 26, `set` 9, `macro` 8, `word` 4, `edge` 2).
- Ảnh đã XEM: crop `assets/rig/sheets/host.png` (mục walk, góc 3/4, hành động quỳ/lạy/chạy/ngã). Chưa kiểm: chưa xem `walk-a`; chưa render mp4 có người đi; chưa kiểm macro trên shotlist S02+ (chưa có).

### 2026-11-26 — #22 sửa 2 lỗi nhỏ của rig (áp cho mọi nhân vật)
- Lỗi 1 (tq-l, host): chỏm tóc nhô ra ở mép trán trái do `VIEW_HAIR_DX=6` dịch tóc trước ra ngoài đầu (tóc sau không dịch). Sửa: `VIEW_HAIR_DX=0` trong `build_rig.py`.
- Lỗi 2 (tq-r worried): hai vạch ink nhỏ trên mắt vì mí `lid=0.08` chỉ che gần hết viền mắt. Sửa: `worried.lid=0.0` (cảm xúc vẫn phân biệt bằng lông mày/miệng).
- Build lại 11 rig, 0 tổ hợp tràn khung; test `test_roadmap_v3.py` qua; `check_rules --phase demo` 0 lỗi; `library.py check` 0 lỗi.
- Ảnh đã XEM: crop `assets/rig/sheets/host.png` (tq-r calm, tq-r worried, tq-l calm, tq-l afraid) trước và sau khi sửa; trước thấy chỏm tóc và vạch mí, sau không còn. Chưa kiểm: chỉ xem 4 thẻ 3/4 của host, chưa xem lại mọi cảm xúc của 10 rig còn lại sau thay đổi tóc/mí; chưa kiểm với `sit`/kneel nhìn nghiêng.

### 2026-11-26 — Viết `references/shotlist-guide.md` (hướng dẫn shot + diễn xuất cho agent khác)
- Tạo `.agents/skills/video-pipeline/references/shotlist-guide.md`: từ kịch bản đến shot, cấu trúc shot, thao tác beat (`set/look/react/move/reach/hand_over/macro`), bảng tình huống → thao tác, tiêu chí diễn xuất (tách rõ [gate] / [khuyến nghị] / [prototype]), lỗi hay gặp, giới hạn hiện tại. Trỏ tới từ `doc-map.md`, `craft-playbook.md` §5, `2d-animation-doctrine.md` §3E.
- Kiểm ví dụ: ghép các ví dụ vào BẢN SAO shotlist (scratchpad), `check_shots` không thêm lỗi mới (vẫn 401 lỗi "S02+ chưa có shot"), `build_video` dựng được SH008. Phát hiện lỗi trong ví dụ đầu của mình: `reach` tới mâm khăn nằm sàn → "trượt đích" 100–170 px (tay đứng không với tới sàn); đã đổi ví dụ sang `nen-r` (độ cao bàn thờ) và ghi thành lưu ý.
- Ảnh đã XEM: snapshot SH008 bản thử tại 25.7 s / 27.3 s / 28.4 s (contact sheet trong scratchpad, không commit). Thấy: `reach` tay với tới cây nến, thân nghiêng; `hand_over` mâm khăn bám tay giữa hai người; chân host nhấc khi đi. Lỗi thấy: tay `reach` còn giơ khi `hand_over` bắt đầu (hai thao tác của cùng người chồng thời gian), `move` bị cắt ở cuối shot → đã ghi vào mục lỗi hay gặp.
- Phát hiện: `check_motion.py` (commit d2dfe12) đọc `motion_plan.json` mà `build_video.py` ở nhánh này KHÔNG xuất → gate chưa chạy được; `doc-map.md` đã sửa dòng đó cho đúng. Chưa kiểm: không biết `build_video.py` ở máy của bạn có xuất file này không.
- Đề xuất sửa luật (CHỜ NGƯỜI DÙNG, R0.3): R11.5 đang ghi "generator chưa có thao tác `hand_over`" — nay đã có (`hand_over`, IK, đạo cụ bám tay, SFX bắt buộc theo R6.1). Đề xuất đổi thành: "Khi đạo cụ chuyển tay, dùng beat `hand_over` + SFX nếu là vật lý (R6.1); `check_shots` kiểm `hand_over` nhắc đúng nhân vật/đạo cụ trong shot (E12)." Agent không tự sửa `RULES.md`.
- Chưa kiểm: video_demo/ được dựng lại (đổi theo rig mới) nhưng chưa render mp4; guide chưa có agent khác đọc thử để xem có làm theo được không.

### 2026-11-26 — 👤 Người dùng duyệt đề xuất sửa R11.5
- Người dùng: "duyệt đề xuất sửa R11.5" (phiên 2026-11-26), sau khi agent nêu đề xuất theo R0.3. Đã sửa `RULES.md` R11.5: dùng beat `hand_over` kèm SFX nếu là vật lý; `check_shots` kiểm nhân vật/đạo cụ có mặt (E12) và SFX (E6). Số phiên bản luật giữ nguyên 2 (chỉ sửa chữ, project đang ghi `Luật áp dụng: RULES.md v2`).
- Đã kiểm: `check_rules --phase demo` chạy lại (xem dưới). Chưa kiểm: `hand_over` chưa dùng trong shotlist thật, nên luật mới chưa được gate bắt trên video thật.

### 2026-11-26 — 👤 Người dùng duyệt đề xuất sửa R11.1 ("Sửa tất cả")
- Người dùng (phiên 2026-11-26) duyệt đề xuất thêm `reach`/`hand_over` vào R11.1 cùng các bước đi kèm. Đã sửa: `RULES.md` R11.1 (+ dòng Lịch sử, giữ phiên bản luật 2); mô tả E7 và thông báo lỗi E7 trong `check_shots.py`.
- Kiểm: bản sao shotlist trong scratchpad, SH008 chỉ có `hand_over` me→host → E7 không báo lỗi; `hand_over` me→me → E7 báo host không có hành vi. `check_shots` vẫn 401 lỗi cũ (S02+ chưa có shot), `check_rules --phase demo` 0 lỗi, `test_roadmap_v3` qua.
- Chưa kiểm: `reach`/`hand_over` vẫn chưa có trong shotlist thật.

### 2026-11-26 — Nhân vật chung cho kho (todo #26, theo yêu cầu "ma da, ma, dân làng…")
- Dựng 12 nhân vật chung ở `library/rigs/cast_src/` (ma nữ, ma da, hồn nam, ma trẻ em, 6 dân làng các lứa tuổi + 2 nón lá), thêm archetype/outfit/token/tham số rig (add-only, R2.3), `cast-add --src library`, đăng ký vào `library/rigs/cast.json` (nay 23 mục). Lý do tạo mới: kho chưa có ma da/ma nữ/dân làng nón lá.
- Ảnh đã XEM: `library/rigs/cast_src/build/sheets/lineup.png` (12 nhân vật phân biệt được bằng bóng dáng và màu; ma tóc che mặt, ma da có rong rêu), pose sheet ma_da, ma_nu_ao_trang (đã sửa: một mắt đục), ma_tre_em, dan_lang_nam_non_la; lỗi đã sửa: ma nữ `cloudy_eye` đổi sang mắt hiển thị, rong rêu mảnh hơn.
- Kiểm: `build_rig` 0 tổ hợp tràn khung; `library.py check` 0 lỗi; `test_roadmap_v3` qua; `check_rules --phase demo` 0 lỗi; `suggest` bắt đúng ma da/dân làng/ông lão theo từ khoá.
- Chưa kiểm: hon_nam_do_tang, ong_lao_lang, thanh_nien_lang, co_gai_lang, be_trai_lang, thieu_nien_lang, thieu_nu_lang chỉ xem ở ảnh lineup, chưa xem từng pose sheet; chưa ghép vào cảnh thật; pose sheet của 12 nhân vật mới **chờ người dùng duyệt** (R3.7).

### 2026-11-26 — Hướng dẫn đạo cụ và tương tác (todo #27, theo yêu cầu "Có làm đi")
- Viết `references/props-and-interaction-guide.md` (danh mục 10 đạo cụ lấy từ `library/index.json`, cách đổi state, bảng việc↔thao tác↔SFX, SFX có/thiếu, ví dụ, giới hạn); thêm con trỏ ở `doc-map.md` (3c), `shotlist-guide.md`, `craft-playbook.md`.
- Kiểm ví dụ: bản sao SH008 trong scratchpad (me tại `L` với tay `nen-r`, nến `lit→low→out`, 3 SFX): `check_shots` không báo lỗi shot đó, `build_video --shots SH008` dựng được. Lỗi gặp khi thử và đã ghi vào hướng dẫn: beat vật lý đổi state thiếu SFX → E6; `reach` nến trượt đích 166 px (me ở C) / 444 px (me ở R).
- Ảnh đã XEM: `library/sheets/props.png` (mọi state của 10 đạo cụ), contact sheet snapshot SH008 thử ở 0,5/1,3/2,0/3,0/4,2 s (không commit): tay với tới nến, lửa nhỏ lại ở `low`, `out` có khói; chị đổi sang `afraid`.
- Chưa kiểm: `smartphone`, `clay_jar`, `betel_mortar`, `bamboo_bed`, `ancestral_altar` `covered`/`blank` chưa đặt vào shot thật; `hand_over` đạo cụ thật chưa render mp4; chưa có SFX quẹt diêm/thổi nến/gốm vỡ (đã ghi trong hướng dẫn).

### 2026-11-26 — Cải tiến quy trình 3 → 1 → 4 → 2 (todo #28–#31, theo "Ok làm 3 1 4 2")
- **3 `preview_shot.py`**: dựng một shot (hoặc biến thể `--shotlist`), chụp ở mốc beat (đã giải neo `word`, bung macro, thêm mốc sau beat vật lý), ra contact sheet + khung lẻ + legend. Thêm `--shotlist` cho `build_video.py` và `check_shots.py`.
- **1 E14** trong `check_shots.py`: dựng thử shot có `reach`/`hand_over` trong bộ nhớ bằng chính bộ giải IK của generator, báo "trượt đích N px". Thử: biến thể đúng (me ở `L`) không lỗi; biến thể sai (me ở `C`) báo 166 px; shotlist thật vẫn 401 lỗi cũ (S02+ chưa có shot), không thêm lỗi.
- **4 SFX theo đạo cụ**: trường `sfx` (touch + state) cho 10 đạo cụ trong `library/index.json` (add-only; `library.py check` 0 lỗi, `reindex` không đổi gì); E6 in gợi ý `{"t","src"}` khi thiếu SFX. Hầu hết là âm thay thế (`substitute: true`), chỉ điện thoại là âm đúng loại.
- **2 `motion_plan.json` v2 + `check_motion.py` viết lại**: gate cũ đòi schema (ops/footstep/gesture) của generator đời trước, generator hiện tại không có; chọn xuất plan v2 từ beat thật và viết lại gate cho khớp (M1–M3, M5–M7). Bỏ kiểm footstep và "đứng chết" vì không có dữ liệu thật. Thử: shot thử OK; `reach` hold 6 s bị báo "vượt hết shot — bị cắt"; dựng cả 13 shot demo ra scratchpad: OK (17 thao tác/46 s, 4 cỡ cảnh).
- Ảnh đã XEM: contact sheet `preview_shot` của SH008 thử (8 khung: tay với tới nến phải, nến lit→low→out có khói, chị đổi sang afraid). Lỗi thấy: không.
- Chưa kiểm: chưa chạy `preview_shot` trên shot không có beat; ngưỡng mật độ 3 thao tác/10 s của M7 là con số mình chọn (cảnh báo, không phải luật); `substitute` SFX chưa nghe thử; chưa render mp4; chưa chạy `hyperframes check` trên nhánh này.

### 2026-11-26 — Ý 6 và ý 5 (todo #32, #33, theo "Làm tiếp ý 5 6 7")
- **Ý 6**: `library.py cast-build` (dựng lại nhóm cast chung + ảnh tổng) và `cast-add --src library --all [--force]` (đăng ký/làm mới hàng loạt từ mục `cast` trong `cast_src/bible.json`). Thử: chạy `--all --force` lặp lại, `cast.json` và sheet không đổi byte nào; `library.py check` 0 lỗi.
- **Ý 5**: `library.py cast-verify` + `library/rigs/golden.json` (23 nhân vật). Ghi golden, chạy hai lần đều KHỚP (dựng ổn định). Thử đổi hằng `VIEW_HAIR_DX` 0→6 trong build_rig: 23/23 báo ĐỔI và xuất ảnh so sánh; trả lại: KHỚP. Lưu ý: lần thử đầu của mình dùng sed sai dòng nên không đổi gì (báo KHỚP là kết quả không có giá trị); đã làm lại đúng ở lần sau.
- Ảnh đã XEM: `…/scratchpad/cmp_view.png` (ảnh so sánh ma_da, hàng biểu cảm: trái mẫu cũ, phải bản dựng lại; khác biệt tóc nhỏ nhìn thấy được ở góc trước; tiêu đề bản phải thiếu dòng mô tả thiết kế — lỗi nhỏ đã ghi vào README).
- Chưa kiểm: golden chỉ so SVG, không so ảnh render; chưa thử `cast-verify` khi đổi archetype hoặc token màu.

### 2026-11-26 — Ý 7: demo đầu-cuối dùng reach / hand_over / đạo cụ mới (todo #34)
- Dựng biến thể shotlist trong scratchpad (KHÔNG sửa project): SH008 = mẹ đưa mâm cho Lâm (`hand_over`, `held: true`, t=0.02) rồi với nến phải (`reach`), nến `lit→low→out`; SH010 = điện thoại `off→ringing→call` + SFX chuông. 13 shot, 46,3 s.
- Lệnh và kết quả: `check_shots --shotlist <biến thể>`: SH008/SH010 sạch (401 lỗi còn lại là các shot S02+ chưa có, như trước); `check_motion`: OK (22 thao tác, 4,7/10 s, 4 cỡ cảnh); `hyperframes lint`: 0 lỗi, 6 cảnh báo (overlap GSAP `--gx/--gy` 0,01 s, file composition > 300 dòng); `hyperframes check --json`: `ok: true`; `hyperframes render --quality draft`: 1920×1080, 30 fps, 1390 khung, 46,33 s, 11,7 MB, 2 phút 33 s.
- Lỗi thật tìm được: (1) E14 bắt `hand_over` mâm ở sàn "xa quá tầm tay"; (2) `held: true` giữa shot làm mâm nhảy từ sàn lên tay (đã ghi cách dùng đúng ở `shotlist-guide.md` 3.4); (3) công cụ `preview_shot.py` hỏng khi chụp > 6 khung vì hyperframes tách `contact-sheet-1/2.jpg` (đã sửa).
- Ảnh đã XEM: `…/scratchpad/dp3/preview/SH008_contact.jpg` (9 khung: mâm trong tay mẹ → hai tay gặp → Lâm cầm mâm → mẹ với nến, nến thấp rồi tắt có khói); `…/scratchpad/dp_SH010/preview/SH010_contact.jpg` (điện thoại tắt → chuông có glow → cuộc gọi); `…/scratchpad/mp4_frames.png` (6 khung trích từ chính file mp4 ở 24,9–33,9 s: khớp với snapshot). Lỗi thấy: mâm lơ lửng giữa hai người ở phiên bản `held: false` (không có mặt đỡ) → đổi sang cách đưa từ đầu shot.
- Chưa kiểm: giọng đọc (không có voiceover.wav → video chỉ có SFX, chưa nghe); `check_sync` không chạy trên biến thể; chưa render chất lượng delivery; `clay_jar`, `betel_mortar`, `bamboo_bed`, `ancestral_altar covered/blank` chưa dựng; mp4 thử nằm ở scratchpad, không commit.

### 2026-11-26 — Hướng dẫn SFX, hiệu ứng, góc quay (theo "Viết mục sfx và hiệu ứng ngay, bổ thêm cả góc quay đẹp")
- Thêm `.agents/skills/video-pipeline/references/sfx-effects-camera-guide.md`; con trỏ ở doc-map (3d), shotlist-guide, craft-playbook, props-and-interaction-guide. Mỗi mục gắn nhãn độ tin cậy `[đã kiểm]` / `[đọc code]` / `[khuyến nghị]`.
- Thử góc quay (biến thể scratchpad, không sửa project): macro + push_in vào nến phải (SH008) và biến thể SH012. Phát hiện: tay nhân vật che ngọn lửa khi macro; `ots` chỉ là zoom 1,8; E11 từ chối `focus: prop:nen-r` (chỉ nhận id bible).
- Ảnh đã XEM: `…/scratchpad/cam1/preview/SH008_contact.jpg` (tay che lửa ở 2,4 s và 3,3 s, chỉ thấy khói ở 4,2 s); `…/scratchpad/cam2/preview/SH012_contact.jpg`. Lỗi thấy: các điểm trên, đã ghi vào mục 3.5 của guide.
- Chưa kiểm: chưa nghe SFX nào (chỉ có thời điểm qua E6); generator không có BGM, stinger, ducking, chuyển cảnh, rung máy; các khuyến nghị dựng phim (ba nhịp, bảng 3.3 trừ dòng thoại medium) chưa thử trong repo; chưa có nhận xét nghe của người dùng.

### 2026-11-27 — Kịch bản có bối cảnh, hành trình, logic liền mạch (theo "kịch bản đang không nói rõ nhân vật ở trong nhà hay ngoài, đi từ đâu tới đâu…")
- Nghiên cứu: Final Draft (scene heading, CONTINUOUS/LATER), Fountain/Hekaya (không có trường liên tục), SCORE (arXiv 2503.23512, theo dõi trạng thái vật), CML-Bench (arXiv 2510.06231). Chi tiết và phần đã dùng: `references/script-continuity-guide.md` §2.
- Thêm: `scripts/check_script_logic.py` (SL1–SL11), `scripts/tests/test_script_logic.py`, trường `setting/cast/staging` ở script.schema, `kind/connects/pending` ở bible.schema, check_rules cho phép `pending` (demo cảnh báo, full chặn), `gates.py` có gate `check_script_logic` (sửa cả danh sách tên in kết quả, nếu không gate fail sẽ bị ẩn), cập nhật script-rewrite SKILL §3.0, script-schema.md, workflow-v2 C1b, scaffold checklist, doc-map 3e, AGENTS.md.
- Thử trên project này: `bible.json` thêm `kind`/`connects` cho 3 địa điểm + 3 địa điểm mới (`loc_rap_tang`←rap_dam_tang, `loc_duong_que`←toan_canh_lang, `loc_cong_truong` pending); `library.py use` hai bối cảnh mới; S01–S08 gán `setting/cast/staging` (bố trí không có trong lời kể ghi `note: đề xuất`); sửa "Cửuu"→"Cửu" ở `script.json` và `script.md`.
- Lệnh và kết quả: `test_script_logic.py` qua hết (20 ca hỏng bị bắt đúng mã, 3 ca không được báo oan); `check_script_logic.py` trên project: 0 lỗi, 5 cảnh báo, 8/20 cảnh có setting; `--strict`: lỗi ở S09–S20 như dự kiến; `check_rules` demo: 0 lỗi; `--phase full`: 1 lỗi (`loc_cong_truong` pending); `validate_schemas`: 0 lỗi; `library.py check`: 0 lỗi; `test_roadmap_v3.py`: qua; `gates.py --scenes S01 --skip-hyperframes`: OK.
- Phát hiện cần người dùng quyết (chưa sửa): S07_L07–L10 là lời ông Cửu nhưng gán `host`; S08_L21 "Ông Cửu nói…" do chính ông Cửu đọc; S02 cần nhân vật Lâm nhỏ chưa có trong bible; S03 cần bối cảnh công trường chưa có trong library; mốc `story_time` là đề xuất bám lời kể.
- Ảnh đã XEM: không có (thay đổi dữ liệu và công cụ, không dựng hình).
- Chưa kiểm: S09–S20 chưa gán setting; chưa chạy quy trình từ đầu cho kịch bản mới (chế độ C); chưa đo agent khác làm theo có tốt hơn không; chưa sinh beat/shotlist từ staging; luật R13 mới là đề xuất, chưa vào RULES.md; SL9 chưa có ca test; chưa chạy `hyperframes check` (không đụng phần dựng hình).
