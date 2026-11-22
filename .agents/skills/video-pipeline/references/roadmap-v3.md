# Roadmap v3 — nhân vật tương tác, giọng VieNeu chính xác, quy trình đồng bộ, release bộ skill

Trạng thái: **ĐỀ XUẤT, chờ người dùng duyệt** (2026-11-22). Luật mới (R10–R12) chỉ có hiệu lực khi người dùng duyệt và dán vào `RULES.md` (R0.3).

## 0. Hiện trạng đo được (không phải ước đoán)

| Hạng mục | Thực tế trong repo |
| --- | --- |
| Độ dài shot theo audio | **Có**: `build_video.py::shot_window` lấy `start/duration` từ `manifest.json`; shot kết thúc ở mốc đầu shot kế |
| Timing giọng | Chỉ mức **câu** (`start`, `duration`, `gap_after`). Không có mốc từ/âm tiết → beat đặt tay (`t`), "ba mươi hai" là ước lượng |
| Khẩu hình | Chia đều theo số từ trong câu, không theo biên độ thật |
| Giọng thật | `audio/voiceover.wav` và `audio/lines/*.wav` chưa có trong repo; `voice_map.json` của project đang `{}`; chưa nghe thử lần nào |
| Hội thoại | Manifest tuần tự, không có chồng lời/ngắt lời; không có `listener` |
| Tương tác nhân vật | Chỉ 1 nhân vật được đổi trạng thái trong beat ở 9/13 shot; SH007 không beat; SH008/SH012 người thứ hai đứng im; **không có** di chuyển/quay người/đưa đồ |
| Đồng bộ quy trình giữa agent | Dựa vào việc agent đọc `AGENTS.md`/playbook; máy chỉ kiểm vài điều (`check_rules` CRAFT). Không có trạng thái phase, không chặn nhảy bước |
| Release | Chưa có phiên bản, CHANGELOG, đóng gói, test tự động ngoài `gates.yml` |

## P0 — Hợp đồng dữ liệu & luật (làm trước, nhỏ, mở khoá mọi thứ)

1. **JSON Schema** cho `script.json`, `bible.json`, `shotlist.json`, `manifest.json` (`schemas/*.schema.json`, có `schema_version`). `vp validate` chạy cả bốn.
2. **Đề xuất luật** (chờ duyệt): R10 craft (đã có `RULES-R10-proposal.md`), **R11 tương tác** (mọi nhân vật trong shot đều có hành vi; không dịch chuyển tức thời; người nghe phản ứng), **R12 giọng** (beat neo theo từ; kiểm âm thanh bằng máy trước khi dựng).
3. Quy ước `listener`, `role` (speaker/listener/bystander), `blocking` (vị trí & hướng mặt) trong shotlist.

## P1 — Giọng VieNeu-TTS chính xác (cần máy có model)

| # | Việc | Kết quả kiểm được |
| --- | --- | --- |
| 1a | Chốt `voice_map` cho từng nhân vật (Hải Đăng mặc định; truyện ma: Đức Trí 1.3 — R6.3); chạy thật `build_voiceover.py` | có `audio/lines/*.wav`, manifest thật; nghe mẫu từng giọng |
| 1b | **Mốc từ/âm tiết** (`words[]` với `start/end`): phân bổ theo số âm tiết (tiếng Việt đơn âm) + hiệu chỉnh theo dấu câu và đường biên độ; tuỳ chọn căn chỉnh bằng ASR (whisper) khi cần | manifest có `words`; sai lệch < 0,1 s trên 20 câu đối chiếu ASR |
| 1c | **Beat neo theo từ**: `at_word: {line, text|index}` thay cho `t` số; generator đổi ra giây từ manifest | "ba mươi hai" trúng từ, không còn ước lượng |
| 1d | **Khẩu hình theo biên độ** (closed/half/open/round theo ngưỡng năng lượng) thay cho chia đều | mở miệng trùng tiếng, im thì ngậm |
| 1e | **Hội thoại nhiều người**: `gap` âm cho chồng/ngắt lời, track giọng theo nhân vật (để duck BGM/SFX), chuẩn hoá âm lượng mỗi giọng (≈ −16 LUFS) | `check_audio.py` |
| 1f | **Phát âm**: từ điển đọc (số, viết tắt, tên riêng, từ cổ), vòng kiểm "TTS → ASR → so khớp" gắn cờ câu đọc sai và đọc lại | báo cáo WER theo câu |
| 1g | `check_audio.py`: tổng thời lượng ≈ tổng line+gap, không lặng > ngưỡng, không clip, speed trong 1.2–1.3, đúng giọng theo `voice_map` | gate máy |

Rủi ro: môi trường đám mây của phiên này chưa kiểm có chạy được VieNeu hay không (model ~2 GB); nếu không, 1a/1b/1d phải chạy trên máy của bạn, mình viết và test phần logic bằng wav giả.

## P2 — Nhân vật tương tác với nhau

**Dữ liệu (shotlist):** beat có thêm các thao tác — `move {char,to,dur,walk}`, `face {char,target}`, `look {char,target}` (gaze tự tính theo vị trí tương đối), `react {char,preset: nod|flinch|step_back|lean_in}`, `reach {char,target}`, `hand_over {from,to,prop}` (đạo cụ chuyển sang tay người nhận). Mỗi `line` khai `listener`.

**Rig (thêm, không phá — R2.3):** pose `walk` (chu kỳ bước + bob), `turn` (lật hướng), `nod`, `flinch`, `lean`, `reach-r`/`point-r`, `hold` (cầm đạo cụ). Build lại, **pose sheet duyệt bằng mắt** (R3.7) trước khi dùng.

**Generator (`build_video.py`):**
- Tween vị trí giữa anchor `L/C/R` (đi bộ có bước, lật hướng khi quay).
- **Người nghe tự động**: nếu shot không khai, tự quay mắt về người nói theo vị trí, thở lệch pha, gật nhẹ ở chỗ ngắt câu (lấy từ `pauses` của manifest), biểu cảm phản ứng theo cảm xúc người nói; beat tường minh luôn thắng mặc định.
- Dàn cảnh hai người: `two_shot`, `over_shoulder`, shot–reverse-shot; giữ trục 180° (người ở L luôn ở L trong cùng cảnh trừ khi có `move`).

**Gate (`check_shots.py`, mới):** E7 shot ≥ 2 nhân vật → mỗi người có ≥ 1 hành vi (beat `set/move/look/react` hoặc người nghe tự động bật); E8 mỗi line có `listener` (trừ người kể); E9 không dịch chuyển tức thời trong cùng cảnh (đổi vị trí phải có `move`); W cảnh có ≥ 2 nhân vật mà > 50% shot chỉ thấy 1 người.

**Làm lại demo S01** (SH007/008/012 + thêm 1–2 shot hai người), chụp snapshot, render nháp để bạn duyệt.

## P3 — Đồng bộ logic cho mọi agent: một CLI, một trạng thái

- **`vp` (một CLI duy nhất)**: `vp status` (đang ở phase nào, thiếu gì), `vp next` (bước kế + lệnh + checklist), `vp gate <phase>` (chạy toàn bộ check của phase, ghi `.pipeline-state.json` và nhật ký vào `PROJECT.md`), `vp doctor` (kiểm môi trường).
- **Khoá phase**: `check_rules` fail nếu nhảy bước (dựng trước khi pose sheet được duyệt; TTS trước khi `script.locked`; full trước khi demo được duyệt; đóng gói khi gate chưa sạch).
- **Bản ghi duyệt** `approvals.json`: pose sheet / demo / kịch bản. Chỉ ghi khi có câu xác nhận của người dùng (agent không tự tick).
- **Scaffolder tạo mới theo khuôn**: `vp new-char | new-prop | new-location` sinh từ mẫu vàng (`library/_templates/`), tự chạy check + sheet + in checklist mắt; chặn "vẽ từ trắng".
- **QA hình tự động (bổ trợ, không thay mắt)**: `check_visual.py` phát hiện ảnh/mặt đen, người nổi so với `floor_y`, vật ra ngoài khung, shot gần trùng shot trước; xuất contact sheet vào `output/review/`. Agent không có khả năng xem ảnh vẫn có tín hiệu, nhưng R10.2 vẫn bắt dừng và báo.
- **Test chung nhiều agent**: dự án fixture nhỏ (2 nhân vật, 1 bối cảnh, 3 shot) + bài kiểm "agent exam": cho agent khác (Codex…) làm theo `vp next` rồi chấm bằng gate + checklist ảnh.

## P4 — Release bộ skill chuẩn

1. **Bộ skill tự viết**, mỗi skill có `SKILL.md` chuẩn (frontmatter, mô tả khi nào dùng), `references/`, `scripts/`, `VERSION`, `CHANGELOG.md` (semver): `video-pipeline` (điều phối), `script-rewrite`, `voice-sync`, và tách thêm `character-rig`, `asset-library` (đạo cụ + bối cảnh), `video-build` (generator + shotlist).
2. **Skill từ marketplace** (hyperframes, vieneu-tts, edge-tts…): khoá phiên bản + nguồn trong `skills.lock.json`, không sửa.
3. **`lint_skills.py`**: frontmatter hợp lệ, link nội bộ sống, script chạy được `--help`, không đường dẫn tuyệt đối, tên/lệnh trong tài liệu khớp code.
4. **Tests + CI**: pytest cho library/rig/shot/audio/generator trên fixture; `gates.yml` mở rộng; workflow release theo tag `v*` → tạo `video2d-skills-vX.Y.Z.zip` + checksum.
5. **Tài liệu**: README quickstart (cài, `vp doctor`, làm video đầu tiên), sơ đồ phase, bảng luật → công cụ kiểm.
6. **Điều kiện release (DoD)**: (a) demo S01 viết lại có tương tác, giọng thật, gate sạch, bạn duyệt; (b) một project thứ hai chế độ C chạy hết qua `vp`; (c) một agent khác làm fixture đạt checklist; (d) CI xanh, PR #1 hết review thread mở; (e) `RULES.md` v2 được bạn duyệt.

## Thứ tự & mốc

| Mốc | Nội dung | Phụ thuộc |
| --- | --- | --- |
| M1 | P0 + lõi P3 (`vp status/next/gate`, state, schema) | bạn duyệt R10–R12 |
| M2 | P1b–1d (mốc từ, beat neo từ, khẩu hình) trên wav thật hoặc wav giả để test | máy có VieNeu cho bản thật |
| M3 | P2 (rig mới + pose sheet duyệt, generator, gate, làm lại S01) | M2 (nhịp phản ứng dùng `pauses`) |
| M4 | P1a/1e/1f/1g (giọng thật, hội thoại chồng, ASR kiểm) + P3 phần còn lại | máy có VieNeu |
| M5 | P4 release | M1–M4 |

## Quyết định cần người dùng

1. Duyệt (hay sửa) R10 + đề xuất R11/R12 → nâng `RULES.md` lên v2.
2. VieNeu chạy ở đâu: máy của bạn (mình chuẩn bị lệnh + dữ liệu) hay thử cài ngay trong phiên này?
3. Có chấp nhận `whisper` (ASR) làm công cụ kiểm phát âm/căn chỉnh không (thêm phụ thuộc, nhưng chính xác hơn)?
4. Định dạng release: zip trong GitHub Release, hay dạng plugin/skill pack cho từng agent?
