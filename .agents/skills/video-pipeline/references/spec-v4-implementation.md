# Spec v4 — triển khai P0 / lõi P4 / P1 (để agent khác thực hiện)

Nguồn lý do và nghiên cứu: [`research-v4-report.md`](research-v4-report.md). Tài liệu này là **đặc tả làm được ngay**, chia thành mốc nhỏ, mỗi mốc có tiêu chí chấp nhận chạy bằng lệnh. Nhãn: **[ĐÃ CÓ]** / **[LÀM]** / **[CHƯA KIỂM]**.

## 0. Ràng buộc bắt buộc

1. Đọc `CLAUDE.md` → `RULES.md` (v2) → `AGENTS.md` trước. **Không sửa `RULES.md`** (R0.3). Muốn đổi luật: ghi đề xuất vào `HANDOFF-opencode.md` mục "Đề xuất luật".
2. **Chỉ thêm, không đổi hành vi cũ.** Không sửa dữ liệu trong `projects/*/script|audio|assets`. Không sinh lại rig/sheet. Gate cũ (`check_rules/shots/sync/audio`, `validate_schemas`) giữ nguyên kết quả trên project mẫu.
3. Python **chuẩn thư viện** + `jsonschema` (đã dùng). Tương thích Python 3.12 (CI) và 3.14 (máy dev). Đường dẫn bằng `pathlib`; chạy được trên Windows/PowerShell (người dùng dùng `D:\`). `sys.stdout.reconfigure(encoding="utf-8")` như các script hiện có. Thông báo tiếng Việt.
4. Mọi tính năng có test trong `scripts/tests/` và chạy được **không cần VieNeu, không cần Chromium** (dùng bản sao tạm của project như `test_roadmap_v3.py`). Test phải chạy ở CI (`gates.yml`).
5. Không tuyên bố "xong" khi chưa chạy lệnh trong mục "Chấp nhận". Báo cáo ghi lệnh + kết quả thật + mục **Chưa kiểm**.
6. Không dùng code từ repo bên ngoài (đặc biệt OpenMontage AGPL, Spine/Remotion license tuỳ chỉnh). Chỉ học ý tưởng.
7. File sinh ra trong `.pipeline/` là **dữ liệu sinh tự động** (như R1.3): không sửa tay, không commit `cache/`.

## 1. Quyết định ĐÃ CHỐT (người dùng yêu cầu làm theo khuyến nghị, 2026-11-23; ưu tiên: độ chính xác, đồng bộ, tốc độ ổn định)

Hướng đã chốt cho cả 4 câu. **Vẫn còn cổng riêng, không bỏ:** câu 2 phải có người dùng duyệt ảnh sau lần thử một nhân vật trước khi nhân rộng; câu 4 cần wav thật từ máy người dùng, cổng đo 20 câu, và hỏi pháp lý trước khi dùng cho sản phẩm thương mại.

| Câu hỏi | Quyết định | Vì sao (theo ưu tiên) |
| --- | --- | --- |
| Migration | Thêm `.pipeline/` + `vp` bọc script cũ, chạy **song song** luồng cũ. Chuyển luồng chính chỉ khi `vp gate` cho **kết luận trùng gate cũ** trên mọi project hiện có (tiêu chí cắt chuyển); roll-back = xoá `.pipeline/` | Không đổi kết quả đang đúng (chính xác); không có thời điểm "đứt" (ổn định) |
| Quay người / 3/4 | **Không vẽ tay từng nhân vật, không xấp xỉ mắt.** Sinh `three_quarter` **theo tham số từ chính rig** trong `build_rig.py` (cùng bible → cùng khuôn mặt, nhất quán), đổi bằng `data-view` (hoán slot, ý từ Spine skin/attachment), cú quay = hoán view + `scaleX` ngắn. **Làm thử một nhân vật, người dùng duyệt view sheet rồi mới nhân rộng** (M5) | Nhất quán nhân vật do cùng nguồn tham số; chi phí render bằng 0 (chỉ đổi thuộc tính) nên tốc độ ổn định. Đây là suy luận từ kiến trúc, **chưa thấy ai làm cho SVG** [CHƯA KIỂM] — vì vậy bắt buộc thử + duyệt ảnh (R10.2) |
| Bộ cache/khoá | **Tự viết tối giản, không `doit`.** Cache = thư mục theo hash, ghi tệp tạm rồi `os.replace` (nguyên tử); khoá = tệp `O_EXCL` có hạn dùng (chạy được Windows). SQLite (có sẵn trong thư viện chuẩn) chỉ thêm khi ≥ 2 worker/agent song song thật (P5) | Key của ta là tổ hợp nhiều trường (§3 M2.1) nên `doit` (md5 theo tệp) không thay thế được; mỗi shot độc lập nên không cần bộ lập lịch DAG; ít phụ thuộc = ít biến động tốc độ |
| ASR/MFA tiếng Việt | **Chấp nhận có điều kiện (M4):** (1) kiểm trước xem VieNeu có trả mốc/độ dài âm tiết gốc không (rẻ nhất, chính xác nhất nếu có); (2) nếu không: **căn chỉnh cưỡng bức** văn bản đã biết bằng MFA `vietnamese_mfa` (đây là forced alignment, không phải nhận dạng); (3) luôn có đường lui bằng đường biên độ RMS. Aligner đứng sau giao diện trung lập `manifest.words[]` để đổi được; **cổng chấp nhận đo thật** trên 20 câu có mốc tay (sai lệch < 0,1 s) trước khi dùng cho dựng. Quyết định dùng cho sản phẩm thương mại chỉ sau khi hỏi pháp lý về dữ liệu huấn luyện (có VIVOS CC BY-NC-SA); **không** dùng model căn chỉnh vi của whisperX (phi thương mại) | Mốc từ thật là thứ quyết định đồng bộ môi/beat (R12.2); ước tính theo ký tự là nguồn lệch lớn nhất hiện nay |

Nghĩa của "tốc độ ổn định" trong spec: thời gian dựng/render **dự đoán được** (cache tất định, render độc lập theo shot, không phụ thuộc mạng/provider) — đo ở M1.5 và M2. Tốc độ đọc giọng giữ cố định theo R6.3.

## 2. Mốc M1 — `vp` + trạng thái + hash (P0)

### M1.1 Thư viện băm `scripts/hashing.py`
- `sha_file(path) -> str`, `sha_json(obj) -> str` (JSON chuẩn tắc: `sort_keys=True, ensure_ascii=False, separators=(",", ":")`), `sha_parts(*strs) -> str` (nối bằng `\0`).
- Không phụ thuộc thời gian/đường dẫn tuyệt đối. Chuẩn hoá `\r\n`→`\n` khi băm file văn bản (`sha_text_file`).
- **Chấp nhận:** hai lần chạy cho cùng kết quả; đổi CRLF↔LF không đổi hash; test `test_hashing.py`.

### M1.2 Trạng thái `scripts/pipeline_state.py`
File: `projects/<slug>/.pipeline/state.json` (schema `schemas/pipeline_state.schema.json`, `x-schema-version: 1`):
```json
{"schema_version": 1, "project": "<slug>", "rules_version": 2,
 "gates": {"check_rules:demo": {"ok": true, "at": "ISO-8601", "cmd": "…", "head": "<git sha|null>", "inputs": "<sha>"}},
 "approvals": {"script": null, "pose_sheet": null, "demo": {"note": "người dùng nói gì", "at": "ISO-8601"}}}
```
- Kèm `events.jsonl` (chỉ thêm, mỗi dòng một JSON: `{ts, actor, op, detail}`).
- API: `load(proj)`, `save(proj, state)` (ghi nguyên tử: ghi tệp tạm rồi `os.replace`), `record_gate(...)`, `approve(name, note)` (**bắt buộc `--note` trích lời người dùng**; agent không tự duyệt).
- Gate coi là **hết hạn** nếu `inputs` (hash của các file đầu vào của gate) đổi.
- **Chấp nhận:** ghi/đọc khứ hồi; ghi đồng thời hai tiến trình không hỏng file (test bằng `multiprocessing`); `state.json` qua schema.

### M1.3 CLI `scripts/vp.py`
Lệnh (gọi **subprocess** các script hiện có, không viết lại logic; `--project projects/<slug>`):

| Lệnh | Việc | Mã thoát |
| --- | --- | --- |
| `vp doctor` | kiểm môi trường: Python, `jsonschema`, `numpy`, `soundfile`, Node, `npx hyperframes --version`, `ffmpeg`, Playwright/Chromium; mỗi mục OK/CẢNH BÁO/LỖI + cách sửa | 1 nếu có LỖI |
| `vp validate` | chạy `validate_schemas.py` | theo lệnh gốc |
| `vp status` | phase hiện tại (suy từ file + state), gate đã qua/hết hạn/thiếu, duyệt còn thiếu | 0 |
| `vp next` | bước kế tiếp + lệnh cụ thể + trỏ tới mục checklist trong `workflow-v2.md` (bảng `STEPS` trong code, có test mỗi bước trỏ đúng tiêu đề tồn tại) | 0 |
| `vp gate <demo\|full\|final>` | chạy chuỗi gate của phase (`check_rules --phase`, `check_shots`, `check_sync`, `validate_schemas`, + `check_audio` khi phase ≥ full), ghi `state.json`, **in tổng hợp** | 1 nếu có gate fail |
| `vp approve <script\|pose_sheet\|demo> --note "<lời người dùng>"` | ghi duyệt | 0 |
| `vp hash shot <SHxxx>` | in cách tính `shot_key` (M2) | 0 |

**Khoá phase (chỉ trong `vp`, không đổi `check_rules`):**
- `vp gate full` từ chối nếu thiếu `approvals.demo`.
- `vp gate demo` từ chối nếu rig của nhân vật dùng trong shotlist chưa có `approvals.pose_sheet` (R3.7).
- `vp gate final` từ chối nếu gate `full` hết hạn.
- Từ chối = in lý do + mã thoát 1; không ghi state "ok".

**Chấp nhận (chạy thật):**
```
python .agents/skills/video-pipeline/scripts/vp.py doctor
python .agents/skills/video-pipeline/scripts/vp.py status   --project projects/than-trung-chiec-khan-tang-thu-32
python .agents/skills/video-pipeline/scripts/vp.py gate demo --project projects/than-trung-chiec-khan-tang-thu-32
python .agents/skills/video-pipeline/scripts/tests/test_vp.py          # mã thoát 0
```
`vp gate demo` trên project mẫu cho **cùng kết luận** như chạy riêng từng gate (so khớp mã thoát từng cái). Dự kiến `check_audio` FAIL ở phase full khi chưa có wav — đúng, không "sửa" cho qua.

### M1.4 CI
Mở rộng `.github/workflows/gates.yml`: chạy `test_roadmap_v3.py`, `test_hashing.py`, `test_vp.py`, `vp validate`, `vp doctor --ci` (CI chỉ yêu cầu Python + jsonschema; thiếu Chromium/Node không làm fail khi `--ci`).

### M1.5 Benchmark nền (tuỳ chọn, chỉ nơi có Chromium)
`vp bench render --scenes S01` chạy `hyperframes render` ở `--workers 1` và `--workers auto`, ghi `.pipeline/bench.json`: giây tường, giây/phút phim, RAM đỉnh nếu đo được. **Không** commit file này. Nếu môi trường không có Chromium: in "chưa đo", thoát 0. Báo cáo phải nêu rõ có/không có số đo.

## 3. Mốc M2 — cache theo shot (lõi P4)

Chưa render; chỉ lập kế hoạch và ghi receipt giả định. Render thật là bước sau khi người dùng duyệt.

### M2.1 `shot_key`
`shot_key = sha_parts(...)` theo đúng thứ tự:
1. sha **HTML đã biên dịch của shot** (`video*/compositions/<SHxxx>.html`, sau chuẩn hoá EOL).
2. `sha_json` mục shotlist của shot.
3. `sha_json` các mục bible mà shot tham chiếu (nhân vật, đạo cụ, location) + giá trị palette token liên quan.
4. sha của `<id>.rig.json` + `<id>.svg` cho từng nhân vật trong shot; sha asset trong `LIBRARY.lock.json` mà shot dùng.
5. Thời gian **tương đối trong shot** (độ dài shot; offset beat theo giây đã quy từ `word` nếu có) — **không** dùng `start` tuyệt đối của timeline.
6. Profile render: fps, width, height, tỉ lệ, codec, crf/bitrate, pixel format, `hyperframes --version`, `ffmpeg -version` (dòng đầu), tên/phiên bản Chromium nếu đọc được.

**Giả thuyết [CHƯA KIỂM] phải được test xác nhận:** HTML của shot dùng thời gian tương đối, nên dịch `start` của các câu trước không đổi HTML của shot sau. Nếu test cho thấy HTML chứa thời gian tuyệt đối → **dừng, báo** (R0.4) thay vì "làm gần đúng"; khi đó sửa generator để xuất thời gian tương đối là một tác vụ riêng cần người dùng duyệt.

### M2.2 `vp plan --project … [--profile default]`
- Với mỗi shot: tính `shot_key`, đối chiếu `.pipeline/cache/<key>/receipt.json`; in bảng `SHxxx | HIT/MISS | lý do` (`vp cache why SHxxx` in trường nào đổi so với receipt gần nhất).
- Chưa có render ⇒ mọi shot MISS; vẫn phải in đúng.
- `receipt.json`: `{shot, key, profile, files:{mp4: sha}, made_at, tool_versions}`.

### M2.3 Bảng vô hiệu hoá (test bắt buộc, trên fixture 3 shot từ project mẫu)
| Sửa | Mong đợi (`vp plan` sau khi giả lập receipt cho tất cả shot) |
| --- | --- |
| đổi `do` của một beat ở SH008 | chỉ SH008 MISS |
| đổi `rig_params` của `host` | mọi shot có `host` MISS, shot khác HIT |
| đổi giá trị một palette token | mọi shot MISS |
| đổi `fps` trong profile | mọi shot MISS |
| đổi `duration` của một câu thoại ở shot trước | **chỉ** shot chứa câu đó MISS |
| đổi BGM/SFX file | **không shot nào MISS** (âm trộn riêng) |

## 4. Mốc M3 — trạng thái thế giới + gate liên tục (P1)

### M3.1 `scripts/world_state.py`
- Replay beat của các shot theo thứ tự ra `.pipeline/world/after_<SHxxx>.json` theo mô hình trong `research-v4-report.md` §D (nhân vật: `anchor, stance, pose, emotion, gaze, holding`; đạo cụ: `state, location, held_by`; cảnh: `location, light`).
- Beat ghi trường: `set` ghi trường nêu tên; `move` ghi `anchor`; `look` ghi `gaze`; `react` không ghi (chỉ hiệu ứng); `hand_over` chuyển `holding`/`held_by`.
- Cắt cảnh (đổi `location`) reset `anchor`, `light`; **không** reset `holding` và `state` đạo cụ.
- Replay tất định: cùng shotlist ⇒ cùng JSON (so bằng `sha_json`).

### M3.2 `scripts/check_continuity.py`
Lỗi (E) / cảnh báo (W):
- **E1** `hand_over` mà người cho không `holding` đạo cụ đó.
- **E2** nhân vật đổi anchor cùng location không có `move` (R11.4).
- **E3** đạo cụ đổi `state` không có beat `set prop:<key>` (R4.3).
- **E4** nhân vật dùng đạo cụ không ở anchor/không đang cầm (khi shot khai `props` kèm `held_by`).
- **W1** nhảy `emotion` giữa hai shot liên tiếp không có beat.
- Kết quả trên **S01 thật phải là OK** (dữ liệu hiện hành đã đúng) — nếu có lỗi, báo cáo từng lỗi, **không** sửa dữ liệu để qua.
- Tích hợp vào `vp gate demo|full` như một gate.

### M3.3 Test
Fixture lỗi giả (bản sao tạm): người cho không cầm → E1; đổi anchor không move → E2; cốc đặt xuống rồi shot sau xuất hiện trên tay → E4; cắt cảnh giữ `holding`.

## 4b. Mốc M4 — Aligner mốc từ (P3, cần wav thật từ máy người dùng)

Hướng đã chốt (mục 1). Chỉ bắt đầu khi đã có `audio/lines/*.wav` thật từ máy người dùng.
1. **M4.1 Thăm dò nguồn gốc:** kiểm VieNeu có trả mốc/độ dài âm tiết không (đọc API/mã nguồn của `vieneu`, ghi kết quả). Có ⇒ dùng, bỏ M4.2.
2. **M4.2 `voice-sync/scripts/align.py`:** forced alignment văn bản biết trước → ghi `words[]` (`{start,end}` tương đối trong câu) vào manifest qua `build_voiceover.py` (không sửa tay manifest, R1.2). Aligner chọn bằng `--aligner mfa|none`; `none` = ước tính hiện tại.
3. **M4.3 Cổng chính xác:** `check_alignment.py`: tổng khoảng từ = độ dài wav (± 0,05 s), mốc đơn điệu, không từ dài 0, và so với **20 câu có mốc đánh dấu tay** (`tests/fixtures/align_gold.json`) — sai lệch trung bình < 0,1 s; không đạt ⇒ không bật.
4. **M4.4 Miệng theo biên độ:** từ RMS từng khung trong khoảng từ, lượng tử closed/half/open/round, giữ tối thiểu; dùng làm đường lui khi không có `words[]` thật.
5. Báo cáo ghi rõ mốc là **thật hay ước tính** (R12.2).

## 4c. Mốc M5 — Thử `three_quarter` (P2, thử nghiệm)

1. Một nhân vật (`host`), thêm `data-view="front|three_quarter"` do `build_rig.py` sinh từ tham số có sẵn; sheet có hàng view.
2. Beat `turn {char, to:view, dur}` trong generator = hoán `data-view` + `scaleX` ngắn; `check_shots` kiểm giá trị `view` hợp lệ; `world_state` ghi `facing/view` (M3).
3. **Cổng:** xem ảnh sheet + một snapshot cảnh hai người đối mặt (R10.2); người dùng duyệt trước khi áp cho nhân vật khác. Không đạt ⇒ ghi lý do, không nhân rộng.

## 5. Không làm (ngoài phạm vi)
Render phân tán; clip chuyển động đầy đủ (P2 phần còn lại); thay đổi `RULES.md`; sửa dữ liệu project; thêm phụ thuộc nặng. (Render thật chỉ ở M1.5 benchmark, khi có Chromium.)

## 6. Cách báo cáo (R8.3, R10.7)
Mỗi mốc: danh sách file đổi, **lệnh đã chạy + mã thoát + đoạn kết quả**, test đã thêm, và mục **Chưa kiểm** (ví dụ: chưa chạy Windows, chưa đo render). Cập nhật `projects/<slug>/PROJECT.md` (nhật ký gate) và `HANDOFF-opencode.md` (trạng thái từng mốc) sau mỗi mốc; commit theo mốc, nội dung commit nêu "chưa làm".
