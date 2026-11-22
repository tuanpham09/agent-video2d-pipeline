# Workflow v2 — Video 2D: QA → viết lại → demo 30–40 s → duyệt → full

Thay thế chuỗi "transcript → script → TTS → HyperFrames" bằng chuỗi có **cổng (gate)** ở mỗi giai đoạn. Mỗi gate có checklist và (nếu đo được) một lệnh do máy kiểm, không do agent tự tuyên bố.

## 0. Đánh giá hiện trạng (đo trên repo, 20/11/2026)

| # | Phát hiện | Bằng chứng | Hệ quả |
| - | --- | --- | --- |
| 1 | Không có bước QA nguồn / chống reup. Script mẫu gần như là transcript gốc | `originality_check.py` trên `than-trung-chiec-khan-tang-thu-32`: **398/414 line (96%)** trùng ≥ 50% cụm 4 từ, **319 line khớp nguyên câu**, giữ **12/13** tên riêng; các câu còn lại chỉ lệch nhỏ (ví dụ "32" → "ba mươi hai"). `brief.md` còn ghi "Chi tiết vàng (không bịa đặt)" — đúng cho tin tức/kiến thức, sai cho truyện hư cấu vì đó chính là phần biểu đạt riêng của tác giả | Video xuất bản sẽ là bản chép lời + cốt truyện của kênh gốc |
| 2 | Thoại ↔ hình chỉ gắn theo **scene**, không theo **line** | `script.json`: field `visual` ở cấp scene; line chỉ có `id/speaker/text/pause_after`. 18/20 scene có `visual` 63–78 ký tự (chỉ 2/20 đủ 5 thành phần như luật). `check_sync.py` chỉ so thời gian audio ↔ HTML | Không có gì ép "mỗi câu thoại có shot diễn tương ứng" |
| 3 | Bản full không phải hoạt hình 2D như doctrine | `video/index.html`: 414 thẻ `<audio>`, **0** `<svg>`, **0** `<img>`, ~20 id shot/scene cho 1.297 s thoại (≈ 65 s/shot, chuẩn là 3–5 s). Chỉ các bản preview mới có SVG (`preview_1min`: 15 thẻ `<svg>`; `preview_2d`: 3) | Mức hoạt hình 2D mới dừng ở bản preview, chưa mở rộng sang bản full |
| 4 | Nhân vật không đồng bộ theo cấu trúc | Nhân vật vẽ bằng SVG nội tuyến trong chuỗi HTML của generator Python (30–74 KB mỗi file); `#cf9063` lặp 27 lần trong `generate_14shots_html.py`; 3 generator cho preview 1 phút, 2 cho preview 2D; không có file rig/bible dùng chung | Mỗi lần sửa là một biến thể mới; nhân vật lệch giữa shot |
| 5 | SFX gắn cứng theo giây tuyệt đối, không gắn theo hành động | `build_perfect_sfx_72s.py` tổng hợp numpy rồi gộp vào **một** `sfx_72s.wav` với mốc giây cố định; kho `sfx/` (357 file) không được generator nào tham chiếu. Kho thiếu hẳn nhóm cần cho truyện dân gian/kinh dị: gong, cối giã, tim đập, củi nổ, bước chân, cửa kẹt, thở, stinger, drone (có fabric/wood slide-touch) | Đổi lời → SFX lệch; không kiểm được "hành động nào chưa có tiếng" |
| 6 | Diễn xuất trong doctrine máy móc | `2d-animation-doctrine.md`: miệng `repeat: 20, yoyo: true` nhịp cố định 0,26 s (không theo âm tiết); chớp mắt ở `[1.5, 4.2, 7.8]` cố định; thở `yoyo` đều. Không có anticipation / follow-through / hold | Dễ ra cảm giác "rối gỗ", đúng thứ cần tránh |
| 7 | Tham chiếu skill không tồn tại | `claude-animation-base` (đặc tả "31 sắc thái", line-boil, rig) xuất hiện ở `AGENTS.md`, `video-pipeline/SKILL.md`, `2d-animation-doctrine.md`, `script-rewrite/SKILL.md` nhưng không có trong repo hay `skills-lock.json` | Agent mới không biết "31 sắc thái" là gì → bịa |
| 8 | Luật tự mâu thuẫn | 12 nhân vật / 7 giọng khác nhau, trong khi `script-rewrite` giới hạn ≤ 4 giọng cho long-form; `Kim Thanh` đọc cả mẹ lẫn bà nội, `Trúc Ly` đọc cả ba vai (Ngân, bé Na, Vy), `Hải Đăng` đọc cả bố lẫn chú Hai, `Đức Trí` đọc cả người kể lẫn Lâm thật | Nghe không phân biệt được ai đang nói khi hai vai chung giọng xuất hiện cùng cảnh |
| 9 | `reverse-any-video` dựng lại **chính video nguồn** (theo mô tả skill: khớp từng frame với bản gốc) | `projects/reverse-than-trung-1m/{frames,rebuilt}`: theo tên và cấu trúc là bản reverse 1 phút của video "Thần Trùng" (chưa xác minh được video nguồn từ `meta.json`) | Dùng để đo thì được; đem xuất bản là reup khung hình |
| 10 | Hạ tầng chưa là "nguồn sự thật" | `PROJECT.md` của cả 2 project có toàn bộ checkbox trống dù đã có audio/video; `sfx/README.md` dùng link `file:///d:/video_youtube/...`; `AGENTS.md` yêu cầu `$env:TEMP` (chỉ đúng PowerShell/Windows) | Không biết project đang ở giai đoạn nào |
| 11 | Project `ma-thoi-den-thanh-co-tinh-tuyet` không có nguồn/QA | `source/` chỉ có `.gitkeep` (không transcript, không URL); `brief.md` dùng tên nhân vật Hồ Bát Nhất, Tuyền Béo và khẩu quyết từ loạt tiểu thuyết Ma Thổi Đèn (nhiều khả năng còn bản quyền) | Không chạy được `originality_check.py`; thiếu quyết định quyền sử dụng → phải qua Giai đoạn A (xin phép hoặc đổi sang nhân vật/cốt truyện gốc) |

**Giữ lại (đang tốt):** `audio/manifest.json` là nguồn thời lượng duy nhất; cache TTS theo câu; `check_sync.py`; luật "không tuyên bố xong khi chưa kiểm"; quy tắc `transformOrigin` SVG; chốt kịch bản trước TTS, chốt preview trước render.

## 1. Nguyên tắc v2

1. **Gate trước, làm sau.** Không sang giai đoạn kế khi gate chưa pass và người dùng chưa duyệt (các gate đánh dấu 👤).
2. **Một ID chạy xuyên suốt:** `line_id → shot_id → beat → sfx cue → <audio id>`. Sửa lời → mọi thứ truy ngược được.
3. **Bible trước shot.** Nhân vật, bối cảnh, đạo cụ định nghĩa một lần (`bible.json` + file rig/prop/bg), shot chỉ *tham chiếu*.
4. **Demo = lát cắt dọc của bản full**, dùng đúng nhân vật, giọng, mix, style của bản full. Cái gì khóa ở demo thì kế thừa nguyên sang full.
5. **Số liệu do script đo.** Báo cáo kèm đầu ra của lệnh, không kèm lời khẳng định.

## 2. Kích hoạt

| Bạn nói | Chế độ | Được lấy từ nguồn | Không được lấy |
| --- | --- | --- | --- |
| "làm video `<URL>`" | **A — làm mới từ chủ đề** | chủ đề, phong tục/kiến thức chung, thông tin thật (sự kiện, số liệu có nguồn) | cốt truyện cụ thể, nhân vật, tên, thứ tự tiết lộ, twist, câu chữ |
| "clone video `<URL>`" | **B — clone công thức** | cấu trúc hook→payoff, nhịp shot, tỉ lệ cỡ cảnh, bảng màu, kiểu chữ, kiểu mix SFX | cốt truyện, nhân vật, lời, khung hình |
| "làm video: `<ý tưởng sơ qua>`" (không có URL) | **C — từ ý tưởng** | toàn bộ do bạn và agent tạo ra | không dùng nhân vật/thế giới của tác phẩm có bản quyền |

Chế độ A và B đều bắt đầu bằng **Giai đoạn A (QA)** rồi **Giai đoạn B (Viết lại)**. Chế độ C bắt đầu bằng **Giai đoạn I (Ý tưởng)** ở mục 3b, rồi vào thẳng Giai đoạn C (demo). Chế độ B dùng `/style-sampling` và số đo từ `/reverse-any-video` (chỉ để **đo** nhịp/cỡ cảnh/màu, ghi vào `source/style_sheet.md`), tuyệt đối không dựng lại khung hình hay nhân vật của nguồn.

Đoạn thay cho phần "Bắt đầu ở đâu" trong `AGENTS.md`:

```markdown
## Bắt đầu ở đâu
Gọi `/video-pipeline` và đọc `references/workflow-v2.md`.
- "làm video <URL>"  → Chế độ A. "clone video <URL>" → Chế độ B. "làm video: <ý tưởng>" (không URL) → Chế độ C.
- A/B: Giai đoạn A (QA nguồn) → B (viết lại, chống reup). C: Giai đoạn I (ý tưởng → xác nhận → thể loại/nhân vật/bối cảnh → đề cương → kịch bản).
- Sau đó cả ba: C (demo 30–40 s) → 👤 duyệt → D (full).
- Không sang giai đoạn sau khi gate chưa pass. Cập nhật `PROJECT.md` sau mỗi gate.
- **Mọi giai đoạn có tạo nhân vật/đạo cụ/bối cảnh/shot** (C1–C4, D): làm theo `references/craft-playbook.md` (bắt buộc) — render PNG, *mở ảnh xem*, ghi "Ảnh đã XEM" vào báo cáo và nhật ký gate.
- Không xuất bản bản dựng lại khung hình/nhân vật của nguồn (`reverse-any-video` chỉ để đo).
```

## 3. Sơ đồ

```
A QA nguồn ─► B Viết lại ─► 👤 duyệt script ─► C DEMO 30–40 s ─► 👤 duyệt demo ─► D FULL ─► E Đóng gói
(chế độ A/B)  (originality)                    C1 bible  C2 shotlist  C3 voice
I Ý tưởng ─► 👤 ─► 👤 ─► 👤 ─► kịch bản ──────► C4 sfx    C5 dựng     C6 QC
(chế độ C)  I1    I2    I3    I5
```

## 3b. Chế độ C — Từ ý tưởng (Giai đoạn I)

Bạn nhập ý tưởng sơ qua → agent xác nhận → chốt thể loại/nhân vật/bối cảnh → đề cương → kịch bản 10–30 phút (giọng đọc `--speed 1.3`) → vào Giai đoạn C (demo). Mỗi bước 👤 phải được bạn xác nhận trước khi sang bước sau; agent không tự suy diễn tiếp.

**Độ dài kịch bản.** Ước tính từ project Thần Trùng (`Đức Trí`, 1.3×): ≈ 216 từ/phút, câu trung bình 2,8 s. Chỉ để lập kế hoạch; bản cuối chốt theo `manifest.json`.

| Thời lượng | Số từ | Số câu thoại | Chương (đề xuất) |
| --- | --- | --- | --- |
| 10 phút | ≈ 2.200 | ≈ 210 | 3–5 |
| 20 phút | ≈ 4.300 | ≈ 420 | 5–8 |
| 30 phút | ≈ 6.500 | ≈ 630 | 7–10 |

### I1. Xác nhận ý hiểu (`script/idea.md`) 👤
- [ ] Ghi lại ý tưởng gốc của bạn nguyên văn.
- [ ] Viết lại ý hiểu trong 5–7 dòng: chuyện gì xảy ra, ai là trung tâm, vì sao người xem quan tâm, cảm xúc muốn tạo.
- [ ] Ghi **promise** một câu ("Sau video này, người xem sẽ ______") và người xem mục tiêu.
- [ ] Liệt kê các chỗ agent **chưa chắc** (tối đa 3 câu hỏi) thay vì tự đoán.
- [ ] Bạn xác nhận / sửa. Chưa xác nhận → không sang I2.

### I2. Thể loại, nhân vật, bối cảnh (`script/concept.md` + `script/bible.json` bản nháp) 👤
- [ ] Thể loại + tông (kinh dị dân gian, hài, drama…), kênh đích, format (16:9 / 9:16).
- [ ] Nhân vật: tên, tuổi, nghề, quan hệ, tính cách, ngoại hình/trang phục, **giọng VieNeu** (khác nhau cho các vai cùng cảnh; theo `/script-rewrite` → `casting-genres.md`).
- [ ] Bối cảnh: địa điểm chính (tối đa 3–4 cho bản đầu), thời điểm, đạo cụ trung tâm và các trạng thái của chúng.
- [ ] Bảng cảm xúc (`emotion_vocab`) và phong cách hình (nét vẽ, bảng màu, ánh sáng chủ đạo).
- [ ] Tốc độ đọc: mặc định `--speed 1.3`; tốc độ riêng từng nhân vật khai `speed` trong `script.json` (giọng kể Đức Trí 1.3, nhân vật miền Bắc 1.2, miền Nam 1.0 — luật Tuấn 23/11; ghi vào `concept.md`).
- [ ] Bạn xác nhận / sửa. Bản bible này là gốc cho C1 của demo, không làm lại từ đầu.

### I3. Đề cương (`script/outline.md`) 👤
- [ ] Chọn thời lượng mục tiêu 10–30 phút (bảng trên) và số chương.
- [ ] Mỗi chương: mục tiêu, beat chính, điểm ngoặt/tiết lộ, vòng lặp tò mò mở – đóng, nhân vật xuất hiện, địa điểm.
- [ ] Hook ≤ 30 s khớp promise; re-hook ở 40–60%; với video > 15 phút thêm pattern interrupt cứ ~8–10 phút (đề xuất; khung chuẩn ở `/long-form-youtube`).
- [ ] Nhịp cảm xúc tổng thể (đường căng thẳng) và chỗ đặt các cao trào.
- [ ] Bạn duyệt đề cương **trước** khi viết toàn bộ lời.

### I4. Kiểm tra ý tưởng gốc (thay cho QA nguồn)
- [ ] Không dùng tên nhân vật, thế giới, khẩu quyết, cốt truyện của tác phẩm đang có bản quyền (tiểu thuyết, phim, game, kênh khác). Nếu ý tưởng bạn đưa vốn dựa trên một tác phẩm → quay về Giai đoạn A để phân loại và xin phép hoặc đổi sang nhân vật/cốt truyện gốc.
- [ ] Tập tục/truyền thuyết dân gian được dùng làm motif; cách kể và nhân vật là của riêng dự án.
- [ ] Sự thật dùng trong truyện (nếu có) có nguồn trong `brief.md`.
- [ ] Ghi kết luận vào `script/concept.md`.

### I5. Viết kịch bản đầy đủ (`script.md` + `script.json`)
Skill: `/script-rewrite` (§3 viết lời, §4 cast), `/long-form-youtube`, `/storytelling-hooks`.
- [ ] Viết theo `outline.md`; câu ≤ 25 từ, 1 line = 1 speaker, đúng 3 tag cảm xúc cho phép.
- [ ] Nhân vật và giọng đúng với `bible.json`; id line theo `S01_L01`.
- [ ] Đo thời lượng không cần model: `build_voiceover.py --script projects/<slug>/script/script.json --out projects/<slug>/audio --dry-run` rồi so với mục tiêu; lệch > 10% → cắt/thêm chương, không kéo giãn khoảng nghỉ.
- [ ] Tự soát theo `/script-rewrite` §6.
- [ ] 👤 Bạn duyệt `script.md` + `packaging.md`, sau đó mới vào Giai đoạn C (demo 30–40 s).

## 4. Giai đoạn A — QA nguồn (`source/qa.md`) — chế độ A và B

Đầu vào: URL. Đầu ra: `source/{meta.json,transcript.md,transcript-sentences.json}` + `source/qa.md` với quyết định **PROCEED / CẦN XIN PHÉP / DỪNG**.

- [ ] Lấy transcript + metadata (kênh, ngày, độ dài, mô tả). Skill transcript ghi vào cây `youtube-transcript/<kênh>/<video>/`; **copy `transcript.md`, `transcript-sentences.json`, `meta.json` sang `projects/<slug>/source/`** (hoặc dùng `--output-dir`). `originality_check.py` đọc `source/transcript-sentences.json`.
- [ ] Ghi **loại nội dung**: truyện hư cấu / kiến thức / tin tức / review / hướng dẫn.
- [ ] Ghi **tình trạng quyền**: tự do (CC, public domain) / có giấy phép / chưa rõ. Chưa rõ + truyện hư cấu → chỉ làm Chế độ A theo mục B.2, hoặc xin phép tác giả bằng văn bản (lưu vào `source/permission.md`).
- [ ] Tách **ý tưởng chung** (phong tục dân gian, motif, thể loại, sự thật có thể kiểm chứng) khỏi **biểu đạt riêng của tác giả** (cốt truyện cụ thể, tên và quan hệ nhân vật, thứ tự tiết lộ, twist, kết, chi tiết đặc trưng, câu chữ). Lập 2 danh sách.
- [ ] Với kiến thức/tin tức: đối chiếu ≥ 2 nguồn độc lập cho mọi con số và sự kiện dùng lại; ghi vào `qa.md`.
- [ ] Chấm rủi ro: THẤP (kiến thức chung) / TRUNG BÌNH (có biểu đạt riêng nhưng sẽ viết lại) / CAO (muốn giữ cốt truyện) → CAO bắt buộc có `permission.md`.
- [ ] Chế độ B: điền `source/style_sheet.md` (nhịp shot trung bình, tỉ lệ cỡ cảnh, bảng màu, font, cấu trúc hook→payoff, mật độ SFX).
- [ ] 👤 Người dùng xác nhận quyết định của `qa.md`.

## 5. Giai đoạn B — Viết lại chống reup (`script/`)

Chỉ bắt đầu khi A = PROCEED. Skill: `/script-rewrite` (+ `/storytelling-hooks`).

**B.1 Việc phải làm**
- [ ] `script/rewrite_plan.md`: giữ gì (chỉ "ý tưởng chung"), đổi gì.
- [ ] `script/diff_matrix.md`: bảng *beat gốc → beat mới → khác ở đâu* (nhân vật / bối cảnh / diễn biến / kết).
- [ ] Viết `script.md` + `script.json` từ `rewrite_plan.md`, **không mở transcript khi viết lời** (chỉ mở để kiểm thông tin thật).

**B.2 Tối thiểu để một truyện hư cấu được coi là "viết lại" (không chỉ đổi chữ)**
- [ ] Nhân vật mới: tên, quan hệ, nghề, tuổi đều khác nguồn.
- [ ] Bối cảnh mới: địa danh, thời điểm, đạo cụ trung tâm khác nguồn (giữ motif dân gian được).
- [ ] Cấu trúc kể khác: đổi ngôi kể *hoặc* thứ tự tiết lộ.
- [ ] Ít nhất 2 trong 3 điểm ngoặt chính của nguồn bị thay; **kết khác**.
- [ ] Câu chữ viết mới hoàn toàn (không dịch/diễn đạt lại từng câu).
- [ ] Muốn giữ nguyên cốt truyện/nhân vật → quay lại A: cần giấy phép.

**B.3 Gate (máy đo lời + người đo ý)**

```bash
python .agents/skills/video-pipeline/scripts/originality_check.py \
  --script projects/<slug>/script/script.json \
  --source projects/<slug>/source/transcript-sentences.json
```
Pass khi: ≤ 10% line trùng ≥ 50% cụm 4 từ, overlap trung bình ≤ 0,20; cảnh báo nếu giữ ≥ 60% tên riêng nguồn.
Script này **chỉ đo lời**. "Đổi tên + đổi từ nhưng giữ nguyên diễn biến" vẫn qua được máy → bắt buộc người duyệt `diff_matrix.md`.

- [ ] `originality_check.py` = OK.
- [ ] `diff_matrix.md` thể hiện đủ mục B.2.
- [ ] Mọi sự thật dùng lại có nguồn trong `brief.md`.
- [ ] Tự soát theo `/script-rewrite` §6 (hook, vòng lặp, câu ≤ 25 từ, 1 speaker/line).
- [ ] 👤 Duyệt `script.md` + `packaging.md`.

## 6. Giai đoạn C — Demo 30–40 s (chạy đủ pipeline trên một lát cắt)

**Chọn lát cắt** (8–12 shot): hook; ≥ 1 cặp thoại hai nhân vật khác nhau; ≥ 1 hành động vật lý có SFX; 1 cao trào/stinger; ≥ 2 góc hoặc 2 địa điểm; mọi nhân vật chính xuất hiện ≥ 1 lần. Tạo `script.demo.json` chỉ gồm các scene/line này (giữ nguyên `id` so với script full).

### C1. Bible, rig, đạo cụ, bối cảnh — **tra `library/` trước** (RULES R2, R3, R4)

Thứ tự bắt buộc:

1. **Tra thư viện (R2.1).** `library.py list [--kind prop|location|archetype|outfit] [--tag ...]`, `library.py show <id>`. Xem `library/sheets/props.png`, `locations.png` để chọn bằng mắt.
2. **Gán vào bible.** Nhân vật: `rig.archetype` + `rig.outfit` (+ ghi đè rời). Bối cảnh/đạo cụ: trường `lib` = id trong library, `states`/`light_states` ⊆ trạng thái của asset.
3. **Chốt phiên bản (R2.2).** `library.py use --project <slug> <id>...` → chép vào `assets/props|bg/` kèm palette đã nhúng, ghi `assets/LIBRARY.lock.json`.
4. **Dựng rig.** `build_rig.py --bible ... --out projects/<slug>/assets/rig` → `<id>.svg`, `<id>.rig.json` (pivot, trạng thái), `sheets/<id>.png`, `sheets/lineup.png`; tự kiểm tràn khung và token màu lạ.
5. **Thiếu gì mới tạo (R2.4).** Làm đúng chuẩn library ngay từ đầu (token màu, `data-state`/`data-light`, gốc giữa-đáy, 3 lớp, không `<text>`), thử trong project, rồi `library.py promote` ở giai đoạn E (hoặc khai `project-only` + lý do).
6. **Cổng:** `check_rules.py --project projects/<slug>` sạch; 👤 duyệt pose sheet + sheet đạo cụ/bối cảnh được dùng.

**Tái sử dụng trước (bắt buộc):** quét `projects/*/script/bible.json` và `projects/*/assets/` tìm nhân vật/đạo cụ/bối cảnh dùng được. Có sẵn → dùng lại nguyên id/rig/giọng. Thiếu nhân vật → clone nhân vật gần nhất bằng `"extends": "<id gốc>"` và `rig_params` chỉ ghi phần khác (gốc ở project khác: copy mục đó sang bible mới trước). Thiếu đạo cụ → đổi `states`/màu của đạo cụ gần nhất; chỉ tạo mới khi không có, và khai vào `bible.props` + `assets/props/`. Ghi lý do tạo mới vào `PROJECT.md`.

```json
{
  "emotion_vocab": ["calm","focused","worried","afraid","shocked","dread","sad","grief","angry","suspicious","relieved"],
  "style": {"line": "hand-drawn boil 6fps", "palette_ref": ["base", "folk-horror-vn"], "palette": {}},
  "characters": [{
    "id": "ba_noi", "name": "Bà nội", "voice": "Kim Thanh",
    "design": "89 tuổi, lưng còng, tóc bạc búi, áo nâu sồng",
    "rig": {"file": "assets/rig/ba_noi.svg", "archetype": "elder_f", "outfit": "nau_song"},
    "mouth_shapes": ["closed","half","open","round"],
    "idle": {"breath_s": 2.8, "blink_s": [3.0, 6.0], "seed": 89}
  }],
  "locations": [{"id": "loc_gian_tho", "lib": "house_altar_room", "light_states": ["warm","dark","red_flash","dawn"]}],
  "props": [
    {"id": "khan_xo", "lib": "mourning_cloth", "states": ["folded","spread","torn"], "locations": ["loc_gian_tho"]},
    {"id": "guong_dong", "scope": "project-only", "reason": "chỉ có ở truyện này; sẽ promote nếu dùng lại", "states": ["clear","fogged"], "locations": ["loc_gian_tho"]}
  ]
}
```

Quy ước (đã kiểm bằng cách ghép thử một cảnh: bối cảnh + bàn thờ + nến/bát hương vào slot + 2 nhân vật):
- **Rig:** viewBox `0 0 520 600`, chân ở `(260, 580)`; điều khiển bằng `data-emotion|mouth|pose|stance|gaze|blink|khan` trên `<g class="rig">`; `l`/`r` theo giải phẫu nhân vật. **Chỉ nhúng bằng `<svg>` lồng nhau** (`x = X - 260·s`, `y = Y - 580·s`, `width = 520·s`, `height = 600·s`); pivot tay trong `<id>.rig.json` (R3.4).
- **Đạo cụ:** gốc toạ độ = giữa-đáy; đặt tại `(X, Y)` với `scale = scene_s` trong index; trạng thái bằng `data-state`; prop có `slots` (vd bàn thờ: `candle-l`, `candle-r`, `incense`) thì đặt prop con vào đúng toạ độ slot (theo tỉ lệ của prop cha).
- **Bối cảnh:** 1920×1080; chọn vị trí đứng từ `stand` (L/C/R) và `slots` trong index (R4.2); ánh sáng bằng `data-light`; 9:16 cắt cửa sổ 608×1080 quanh `crop_9x16` (R4.4).
- **Chưa kiểm trong HyperFrames/GSAP:** ghép thử mới dùng CSS/Chromium. Kiểm animation thật (GSAP đổi `data-*`/biến CSS, xoay tay) ở demo C5 trước khi khoá.
- **Sinh rig + kiểm giải tích:** `python .agents/skills/video-pipeline/scripts/build_rig.py --bible projects/<slug>/script/bible.json --out projects/<slug>/assets/rig [--script projects/<slug>/script/script.json]` → `<id>.svg` + `<id>.rig.json` + `sheets/<id>.png` + `sheets/lineup.png`. Trước khi ghi file, script kiểm **giải tích** (không render): tay ở mọi pose × đứng/ngồi và đầu/thân có nằm trong viewBox không (có tính `scale`/`head_scale`); với `--script` thì id + giọng khớp `script.json`. Lỗi → thoát 1, không ghi gì (`--no-check` để bỏ). Không thay cho việc xem pose sheet.
- **Nhân vật mới:** chọn `archetype` + `outfit` (library) hoặc clone `"extends": "<id gốc>"` + `rig_params` chỉ phần đổi. Bible khai `"rig": {tham số}` hoặc `"rig": "assets/rig/<id>.svg"` + `"rig_params": {...}`.
- Mỗi địa điểm: 3 lớp xa/giữa/gần + trạng thái ánh sáng; đạo cụ có file riêng + trạng thái — tất cả lấy từ `library/` (R2), không vẽ tại chỗ.
- [ ] Giọng: nhân vật xuất hiện chung một cảnh phải khác giọng; vai phụ chỉ dùng chung giọng khi không bao giờ cùng cảnh.
- [ ] `emotion_vocab` thay cho "31 sắc thái" (không dẫn chiếu `claude-animation-base`).

### C2. Shotlist (`script/shotlist.json`) — mỗi câu thoại một beat diễn

```json
{"shots": [{
  "id": "SH003", "line_ids": ["S01_L03"], "kind": "speaker",
  "size": "close", "camera": "push_in",
  "location": "loc_gian_tho", "light": "candle_warm",
  "characters": [{"id": "ba_noi", "emotion": "worried", "mouth": true}],
  "props": [{"id": "khan_xo", "state": "folded"}],
  "beats": [
    {"line_id": "S01_L03", "t": 0.0, "do": "bà ngẩng lên, mắt liếc khung cửa rồi mới nói", "physical": false},
    {"line_id": "S01_L03", "t": 1.4, "do": "tay nhấc nếp khăn trên mâm", "physical": true}
  ],
  "sfx": [{"cue": "foley.cloth", "src": "sfx/ambience/foley/foley-fabric-touch.wav", "t": 1.4}]
}]}
```
Quy tắc:
- [ ] **Mỗi line ≥ 1 beat diễn riêng**, kể cả line < 1,2 s (câu ngắn được ở chung shot nhưng phải có beat riêng: liếc mắt, hít vào, đặt tay, quay đầu…).
- [ ] Shot 1,0–6,0 s; trung bình 3–5 s; line > 5 s tách ≥ 2 shot (đổi cỡ cảnh/góc). Khi một line được nhiều shot chia nhau, **mỗi shot khai `"span": [từ, đến]`** (giây, tính từ đầu line) — `check_shots.py` dùng span làm thời lượng shot và báo lỗi nếu thiếu.
- [ ] `t` của beat và SFX tính từ đầu shot và phải nằm trong `[0, thời lượng shot]`; mỗi beat phải có `do` không rỗng; shot phải có `light` thuộc `light_states` của địa điểm, và mọi prop trong bible phải khai `states`.
- [ ] Nhân vật nói phải xuất hiện trong ít nhất một shot của line đó với `mouth: true`. Người kể (narrator) → cutaway/insert/establishing.
- [ ] Không 3 shot liền cùng cỡ cảnh + camera; ≤ 50% shot cùng một cỡ cảnh.
- [ ] Đạo cụ chỉ đổi trạng thái theo thứ tự `states` (lùi trạng thái phải ghi `reset: true`); hướng nhìn (eye-line) nhất quán giữa các shot liền kề.
- [ ] Ánh sáng thuộc `light_states` của địa điểm.

### C3. Giọng (`/voice-sync` — giữ nguyên)
- [ ] `build_voiceover.py --dry-run` rồi chạy thật trên `script.demo.json`; nghe `voiceover.wav`.
- [ ] `check_sync.py` OK; tên riêng đọc đúng (sửa phiên âm trong `script.json`, không sửa wav).

### C4. SFX theo cue (`audio/sfx_cues` suy ra từ shotlist)
- [ ] Mỗi beat `physical: true` có SFX cue trong ±0,15 s; `t` tính **theo đầu shot** (không dùng giây tuyệt đối) → đổi lời không làm lệch.
- [ ] Nguồn SFX: `src` là file có thật (tương đối gốc repo hoặc project), hoặc `synth:<tên>` = recipe **đã render** ra `projects/<slug>/audio/sfx/<tên>.wav` (gate kiểm file này tồn tại; `src` rỗng bị từ chối); không gộp mọi thứ vào một wav lớn.
- [ ] 4 tầng: giọng / BGM / foley / stinger. BGM luôn có room tone liên tục; stinger ≤ 3–4 lần trong demo để còn chỗ nhấn. Hạ BGM và foley khi có thoại bằng `data-automation` (xem `media-use/references/mixing.md`), mục tiêu lời luôn nghe rõ nhất.
- [ ] Bổ sung kho còn thiếu (gong, cối giã, tim đập, củi nổ, bước chân, cửa kẹt, thở, stinger, drone) bằng recipe tham số hóa (tách từ `build_perfect_sfx_72s.py`) hoặc nguồn CC0; tên cue ổn định, ví dụ `foley.cloth`, `amb.wind_night`, `hit.gong_funeral`.

### C5. Dựng (HyperFrames, một generator đọc dữ liệu)
- [ ] Một `build_video.py` đọc `manifest.json` + `bible.json` + `shotlist.json` sinh HTML (thay các generator rời theo từng bản). Nhân vật/đạo cụ/bối cảnh được *include* từ file rig/prop/bg.
- [ ] Mọi `data-start/data-duration` lấy từ manifest + offset shot.
- [ ] Giữ luật `transformOrigin`, "không animate trực tiếp `.clip`", không CSS transform trùng GSAP.

**Diễn tự nhiên (thay các đoạn tương ứng trong doctrine):**
| Hạng mục | Cách làm |
| --- | --- |
| Nhịp một câu thoại | trước khi nói: nhìn/hít 0,15–0,3 s (anticipation); trong lúc nói: miệng + đầu/vai nhấn theo từ khóa; sau: giữ phản ứng 0,2–0,4 s (follow-through) |
| Khẩu hình | 3–4 hình miệng chọn theo **biên độ âm của wav từng line** (trích bằng script ra keyframe JSON), không `yoyo` nhịp cố định |
| Chớp mắt | khoảng cách ngẫu nhiên 2,5–5,5 s theo seed của nhân vật; chớp trước khi đổi hướng nhìn hoặc ngay sau cú sốc |
| Thở / idle | chu kỳ và biên độ riêng từng nhân vật; không `repeat: -1`; không để đứng yên tuyệt đối > 1 s (moving hold) |
| Cử động thứ cấp | tóc, vải, tay áo trễ 2–4 frame so với thân; overshoot 5–8% rồi về |
| Ease | hành động chính vào nhanh ra chậm (power2.out); va chạm có hold 2–3 frame; không dùng một ease cho mọi thứ |
| Mắt & hướng nhìn | mắt dẫn trước đầu, đầu dẫn trước thân; eye-line nhất quán qua các shot |
| Lặp | cùng một cử chỉ lặp lại phải đổi biên độ/thời lượng nhẹ |

### C6. QC demo (gate)
```bash
# chỉ chế độ A/B (có nguồn). Chế độ C không có nguồn → bỏ dòng originality_check, dùng I4 (script/concept.md) làm gate ý tưởng gốc
python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/<slug> --phase demo
python .agents/skills/video-pipeline/scripts/originality_check.py --script projects/<slug>/script/script.json --source projects/<slug>/source/transcript-sentences.json
python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/<slug> --scenes <id các scene thuộc demo, vd S01 hoặc S01,S02>   # bỏ --scenes nếu manifest demo chỉ chứa scene demo
python .agents/skills/video-pipeline/scripts/check_sync.py  --project projects/<slug>
cd projects/<slug>/video && npx hyperframes lint && npx hyperframes check --json
```
- [ ] Mọi lệnh áp dụng cho chế độ của dự án đều pass (A/B: cả năm lệnh; C: bốn lệnh còn lại). `check_shots` bỏ qua cảnh ngoài lát cắt nhờ `--scenes` (id scene sai/không có trong manifest → lỗi, không được "OK rỗng").
- [ ] Xem snapshot **từng shot** (không chỉ từng scene): nhân vật cùng màu/tỉ lệ/trang phục; đạo cụ đúng trạng thái; bối cảnh không đổi vô cớ.
- [ ] Nghe riêng 3 lớp: chỉ giọng; giọng + BGM; mix đủ. Không SFX nào che lời.
- [ ] Mỗi câu thoại ngắn: tua khung hình, có chuyển động/biểu cảm riêng tại câu đó.
- [ ] Tiếng Việt không lỗi dấu, caption không đè nhân vật.
- [ ] Ghi vào `PROJECT.md`: ngày, kết quả các lệnh gate, đường dẫn demo, thời lượng thật.
- [ ] Render demo bằng `render.py` (mặc định `--quality draft`, nhanh) để người dùng duyệt chuyển động; **không** render delivery cho bản xem thử — delivery chỉ 1 lần cuối ở giai đoạn D.

### 👤 Cổng duyệt demo
Người dùng duyệt từng mục: ① nhân vật (pose sheet + trong demo) ② diễn xuất ③ SFX & mix ④ bối cảnh/đạo cụ ⑤ nhịp shot ⑥ giọng. Mục chưa đạt → sửa **bible/rig/recipe** rồi dựng lại demo, không vá riêng trong HTML.
**Khi duyệt: khóa** bible, phiên bản library đã dùng (`assets/LIBRARY.lock.json`), giọng + tốc độ, thông số mix, style, danh sách cue SFX. Ghi vào `PROJECT.md` mục "Đã khóa ở demo". Thay đổi sau đó cần yêu cầu thay đổi rõ ràng.

## 7. Giai đoạn D — Full

Chỉ bắt đầu khi 👤 duyệt demo.

- [ ] Mở rộng `script.json`, bible (nhân vật/địa điểm/đạo cụ mới nếu có, kèm pose sheet) — nhân vật đã khóa không đổi. Mục mới cũng **tra library trước** (R2.1); sửa asset dùng chung tại `library/`, không vá bản trong project (R2.3).
- [ ] Voice full (cache theo câu) → `check_sync.py`.
- [ ] Shotlist **theo scene**, sau mỗi scene chạy `check_shots.py --scenes Sxx` rồi mới sang scene kế. Dùng `--project` không kèm `--scenes` ở cuối để kiểm toàn bộ.
- [ ] Mỗi scene: render snapshot, 1 lần xem nhanh trước khi gộp. Cứ 5 scene kiểm một lượt **liên tục** (trạng thái đạo cụ, trang phục, ánh sáng, vị trí nhân vật khi cắt giữa các scene).
- [ ] Bản full dùng chính generator và rig đã dùng ở demo (không viết generator mới cho từng scene).
- [ ] Hòa âm full: dùng lại thông số đã khóa; stinger dành cho các điểm ngoặt thật.
- [ ] QC cuối: các lệnh gate ở C6 (không `--scenes`; chế độ C bỏ `originality_check.py` và dùng quyết định I4), duration video = `manifest.duration` ± 0,1 s, xem snapshot mọi shot đầu/cuối scene, nghe lại các cảnh cao trào.
- [ ] Render nháp (`render.py`, mặc định `--quality draft` + 15 fps) để xem chuyển động, lặp bao nhiêu lần cũng được; **chỉ render `--quality delivery` 1 lần cuối** sau khi đã chốt preview; đặt biến thư mục tạm theo hệ điều hành đang dùng.
- [ ] Ghi vào `PROJECT.md`: kết quả lệnh, đường dẫn `output/final.mp4`.

## 8. Giai đoạn E — Đóng gói
Theo `references/packaging.md`. Thêm:
- [ ] Chế độ A/B: `originality_check.py` chạy lại trên bản script cuối. Chế độ C: đối chiếu lại quyết định I4 (`script/concept.md`) với script cuối (không có `--source` để so).
- [ ] **Đưa asset mới vào library (R2.4/R8.4):** mỗi rig archetype/outfit, đạo cụ, bối cảnh mới → `library.py promote` (kèm `library.py sheet`, `library.py check` sạch, commit `library/`), hoặc khai `project-only` + lý do trong bible. `check_rules.py --project projects/<slug> --phase final` sạch.
- [ ] Mô tả/credit đúng với `qa.md` (nguồn tham khảo, giấy phép nếu có).
- [ ] Lưu bài học vào `PROJECT.md`.

## 9. Việc cần sửa trong repo để workflow này chạy trơn

| Việc | Ghi chú |
| --- | --- |
| ~~Cập nhật `scaffold_project.py`~~ ✅ | sinh thêm `source/qa.md`, `script/{rewrite_plan.md,diff_matrix.md,bible.json,shotlist.json}`, `PROJECT.md` theo giai đoạn A–E |
| ~~Cập nhật `PROJECT.md` template~~ ✅ (thêm tem luật + C0 tra thư viện + promote ở E) | checkbox theo giai đoạn + ô "Đã khóa ở demo" |
| Viết `build_video.py` dựng từ dữ liệu | chưa có; gom 5 generator hiện tại thành một. Dùng quy ước nhúng ở C1 (rig/prop `<svg>` lồng, anchor trong `library/index.json`); không gõ hex (R2.5) |
| ~~Tạo rig/prop/bg dùng lại được~~ | ✅ `library/` (7 archetype, 4 outfit, 10 đạo cụ, 3 bối cảnh, 2 palette) + `library.py`, `check_rules.py`; rig 5 nhân vật chính của project mẫu. Còn thiếu: nhân vật phụ, thêm bối cảnh (đình làng, bờ sông, phòng khách…), đạo cụ (gương đồng, quan tài, nhang đèn…) — thêm dần qua `promote` |
| Thêm kho SFX còn thiếu + recipe | xem C4 |
| ~~Xóa/thay `claude-animation-base`~~ | ✅ đã thay bằng `emotion_vocab` (SKILL.md, doctrine, script-rewrite) |
| Sửa luật giọng (≤ 4 giọng long-form) | cho khớp thực tế hoặc giảm số nhân vật |
| `sfx/README.md`: đổi link `file:///d:/...` thành đường dẫn tương đối; `AGENTS.md`: ghi cả lệnh đặt thư mục tạm cho Linux/macOS | |
| `projects/reverse-than-trung-1m/` | giữ làm tư liệu đo, đừng xuất bản |

## 10. Giới hạn của bản này
- `originality_check.py` chỉ đo văn bản; không thay cho việc người duyệt `diff_matrix.md`.
- `check_shots.py` kiểm *cấu trúc* (phủ line, beat, tham chiếu bible, SFX có mặt đúng giờ); chất lượng diễn xuất vẫn phải xem bằng mắt ở C6.
- Chưa render HyperFrames trong lần cải tiến này; hai script đã chạy thử trên dữ liệu thật của repo và trên bộ dữ liệu mẫu có lỗi cài sẵn.
