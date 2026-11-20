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

Cả hai chế độ đều bắt đầu bằng **Giai đoạn A (QA)** rồi **Giai đoạn B (Viết lại)**. Chế độ B dùng `/style-sampling` và số đo từ `/reverse-any-video` (chỉ để **đo** nhịp/cỡ cảnh/màu, ghi vào `source/style_sheet.md`), tuyệt đối không dựng lại khung hình hay nhân vật của nguồn.

Đoạn thay cho phần "Bắt đầu ở đâu" trong `AGENTS.md`:

```markdown
## Bắt đầu ở đâu
Gọi `/video-pipeline` và đọc `references/workflow-v2.md`.
- "làm video <URL>"  → Chế độ A. "clone video <URL>" → Chế độ B.
- Luôn chạy Giai đoạn A (QA nguồn) → B (viết lại, chống reup) → C (demo 30–40 s) → 👤 duyệt → D (full).
- Không sang giai đoạn sau khi gate chưa pass. Cập nhật `PROJECT.md` sau mỗi gate.
- Không xuất bản bản dựng lại khung hình/nhân vật của nguồn (`reverse-any-video` chỉ để đo).
```

## 3. Sơ đồ

```
A QA nguồn ─► B Viết lại ─► 👤 duyệt script ─► C DEMO 30–40 s ─► 👤 duyệt demo ─► D FULL ─► E Đóng gói
              (originality)                    C1 bible  C2 shotlist  C3 voice
                                               C4 sfx    C5 dựng     C6 QC
```

## 4. Giai đoạn A — QA nguồn (`source/qa.md`)

Đầu vào: URL. Đầu ra: `source/{meta.json,transcript.md}` + `source/qa.md` với quyết định **PROCEED / CẦN XIN PHÉP / DỪNG**.

- [ ] Lấy transcript + metadata (kênh, ngày, độ dài, mô tả).
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

### C1. Bible & rig (`script/bible.json`, `assets/rig|props|bg/`)

```json
{
  "emotion_vocab": ["calm","focused","worried","afraid","shocked","dread","sad","grief","angry","suspicious","relieved"],
  "style": {"line": "hand-drawn boil 6fps", "palette": {"skin_a": "#cf9063", "wall": "#241a13"}},
  "characters": [{
    "id": "ba_noi", "name": "Bà nội", "voice": "Kim Thanh",
    "design": "áo bà ba nâu, búi tóc bạc, 89 tuổi, lưng còng",
    "rig": "assets/rig/ba_noi.svg",
    "mouth_shapes": ["closed","half","open","round"],
    "idle": {"breath_s": 3.4, "blink_s": [2.5, 5.5]}
  }],
  "locations": [{"id": "loc_gian_tho", "layers": ["far","mid","near"], "light_states": ["candle_warm","dark","red_flash"]}],
  "props": [{"id": "khan_xo", "states": ["folded","counted","missing"], "locations": ["loc_gian_tho"]}]
}
```
- [ ] Mỗi nhân vật: 1 file rig SVG, nhóm có tên (đầu, mắt, mí, đồng tử, mày, 4 hình miệng, thân, vai/tay có pivot). **Màu lấy từ bible, không gõ lại hex trong generator.**
- [ ] Tấm **pose sheet** mỗi nhân vật (đứng/ngồi × 5 cảm xúc chính) render ra ảnh để duyệt trước khi dựng shot.
- [ ] Mỗi địa điểm: 3 lớp (xa/giữa/gần) + các trạng thái ánh sáng; đạo cụ có file riêng + các trạng thái (bàn thờ, khăn, cối, gương…).
- [ ] Giọng: nhân vật xuất hiện chung một cảnh phải khác giọng; vai phụ chỉ dùng chung giọng khi không bao giờ cùng cảnh.
- [ ] `emotion_vocab` thay cho "31 sắc thái" (xóa các tham chiếu `claude-animation-base` hoặc thêm skill đó vào repo).

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
- [ ] Shot 1,0–6,0 s; trung bình 3–5 s; line > 5 s tách ≥ 2 shot (đổi cỡ cảnh/góc).
- [ ] Nhân vật nói phải xuất hiện trong ít nhất một shot của line đó với `mouth: true`. Người kể (narrator) → cutaway/insert/establishing.
- [ ] Không 3 shot liền cùng cỡ cảnh + camera; ≤ 50% shot cùng một cỡ cảnh.
- [ ] Đạo cụ chỉ đổi trạng thái theo thứ tự `states` (lùi trạng thái phải ghi `reset: true`); hướng nhìn (eye-line) nhất quán giữa các shot liền kề.
- [ ] Ánh sáng thuộc `light_states` của địa điểm.

### C3. Giọng (`/voice-sync` — giữ nguyên)
- [ ] `build_voiceover.py --dry-run` rồi chạy thật trên `script.demo.json`; nghe `voiceover.wav`.
- [ ] `check_sync.py` OK; tên riêng đọc đúng (sửa phiên âm trong `script.json`, không sửa wav).

### C4. SFX theo cue (`audio/sfx_cues` suy ra từ shotlist)
- [ ] Mỗi beat `physical: true` có SFX cue trong ±0,15 s; `t` tính **theo đầu shot** (không dùng giây tuyệt đối) → đổi lời không làm lệch.
- [ ] Nguồn SFX: file có trong `sfx/` hoặc recipe tổng hợp lưu thành file (`src` hoặc `synth:<tên>`); không gộp mọi thứ vào một wav lớn.
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
python .agents/skills/video-pipeline/scripts/originality_check.py --script projects/<slug>/script/script.json --source projects/<slug>/source/transcript-sentences.json
python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/<slug> --scenes S01,S02
python .agents/skills/video-pipeline/scripts/check_sync.py  --project projects/<slug>
cd projects/<slug>/video && npx hyperframes lint && npx hyperframes check --json
```
- [ ] Cả bốn lệnh pass (`check_shots` bỏ qua cảnh ngoài lát cắt nhờ `--scenes`).
- [ ] Xem snapshot **từng shot** (không chỉ từng scene): nhân vật cùng màu/tỉ lệ/trang phục; đạo cụ đúng trạng thái; bối cảnh không đổi vô cớ.
- [ ] Nghe riêng 3 lớp: chỉ giọng; giọng + BGM; mix đủ. Không SFX nào che lời.
- [ ] Mỗi câu thoại ngắn: tua khung hình, có chuyển động/biểu cảm riêng tại câu đó.
- [ ] Tiếng Việt không lỗi dấu, caption không đè nhân vật.
- [ ] Ghi vào `PROJECT.md`: ngày, kết quả 4 lệnh, đường dẫn demo, thời lượng thật.

### 👤 Cổng duyệt demo
Người dùng duyệt từng mục: ① nhân vật (pose sheet + trong demo) ② diễn xuất ③ SFX & mix ④ bối cảnh/đạo cụ ⑤ nhịp shot ⑥ giọng. Mục chưa đạt → sửa **bible/rig/recipe** rồi dựng lại demo, không vá riêng trong HTML.
**Khi duyệt: khóa** bible, giọng + tốc độ, thông số mix, style, danh sách cue SFX. Ghi vào `PROJECT.md` mục "Đã khóa ở demo". Thay đổi sau đó cần yêu cầu thay đổi rõ ràng.

## 7. Giai đoạn D — Full

Chỉ bắt đầu khi 👤 duyệt demo.

- [ ] Mở rộng `script.json`, bible (nhân vật/địa điểm/đạo cụ mới nếu có, kèm pose sheet) — nhân vật đã khóa không đổi.
- [ ] Voice full (cache theo câu) → `check_sync.py`.
- [ ] Shotlist **theo scene**, sau mỗi scene chạy `check_shots.py --scenes Sxx` rồi mới sang scene kế. Dùng `--project` không kèm `--scenes` ở cuối để kiểm toàn bộ.
- [ ] Mỗi scene: render snapshot, 1 lần xem nhanh trước khi gộp. Cứ 5 scene kiểm một lượt **liên tục** (trạng thái đạo cụ, trang phục, ánh sáng, vị trí nhân vật khi cắt giữa các scene).
- [ ] Bản full dùng chính generator và rig đã dùng ở demo (không viết generator mới cho từng scene).
- [ ] Hòa âm full: dùng lại thông số đã khóa; stinger dành cho các điểm ngoặt thật.
- [ ] QC cuối: bốn lệnh ở C6 (không `--scenes`), duration video = `manifest.duration` ± 0,1 s, xem snapshot mọi shot đầu/cuối scene, nghe lại các cảnh cao trào.
- [ ] Render (`--quality delivery`); đặt biến thư mục tạm theo hệ điều hành đang dùng.
- [ ] Ghi vào `PROJECT.md`: kết quả lệnh, đường dẫn `output/final.mp4`.

## 8. Giai đoạn E — Đóng gói
Theo `references/packaging.md`. Thêm:
- [ ] `originality_check.py` chạy lại trên bản script cuối.
- [ ] Mô tả/credit đúng với `qa.md` (nguồn tham khảo, giấy phép nếu có).
- [ ] Lưu bài học vào `PROJECT.md`.

## 9. Việc cần sửa trong repo để workflow này chạy trơn

| Việc | Ghi chú |
| --- | --- |
| Cập nhật `scaffold_project.py` | sinh thêm `source/qa.md`, `script/{rewrite_plan.md,diff_matrix.md,bible.json,shotlist.json}`, `PROJECT.md` theo giai đoạn A–E |
| Cập nhật `PROJECT.md` template | checkbox theo giai đoạn + ô "Đã khóa ở demo" |
| Viết `build_video.py` dựng từ dữ liệu | chưa có; gom 5 generator hiện tại thành một |
| Tạo rig/prop/bg cho các nhân vật chính | tách từ SVG trong generator hiện có |
| Thêm kho SFX còn thiếu + recipe | xem C4 |
| Xóa/thay `claude-animation-base` trong 4 file | xem Phát hiện #7 |
| Sửa luật giọng (≤ 4 giọng long-form) | cho khớp thực tế hoặc giảm số nhân vật |
| `sfx/README.md`: đổi link `file:///d:/...` thành đường dẫn tương đối; `AGENTS.md`: ghi cả lệnh đặt thư mục tạm cho Linux/macOS | |
| `projects/reverse-than-trung-1m/` | giữ làm tư liệu đo, đừng xuất bản |

## 10. Giới hạn của bản này
- `originality_check.py` chỉ đo văn bản; không thay cho việc người duyệt `diff_matrix.md`.
- `check_shots.py` kiểm *cấu trúc* (phủ line, beat, tham chiếu bible, SFX có mặt đúng giờ); chất lượng diễn xuất vẫn phải xem bằng mắt ở C6.
- Chưa render HyperFrames trong lần cải tiến này; hai script đã chạy thử trên dữ liệu thật của repo và trên bộ dữ liệu mẫu có lỗi cài sẵn.
