# PLAN-REVIEW — Vòng 3 (phân tích lại plan trước khi implement)

Ngày: 2026-11-23. Nhánh: `claude/opt-round3` (từ `claude/opt-round2` @9d09022).
Nguồn: `~/workspace/github-video-pipeline-research-0500/final-report.md` (2 agent phản biện)
+ HANDOFF.md + code hiện tại (render.py, gates.py, build_video.py, build_voiceover.py,
check_shots.py). Tuấn chốt: phân tích xong thì implement luôn; mục 7 KHÔNG hoãn,
làm spike trong vòng này, xếp cuối.

## 0. Sự thật đo/kiểm chứng được trong lúc phân tích (làm căn cứ sửa plan)

- **Phiên bản hyperframes demo #3 dùng là KHÔNG XÁC ĐỊNH ĐƯỢC.** Cache npx:
  0.9.63 + 0.9.59 (17/11), 0.9.82 (22/11 22:10 UTC = 23/11 05:10 VN — cài trong
  lúc research, KHÔNG phải lúc demo #3 render 04:33–04:49). 0.9.81 KHÔNG BAO GIỜ
  có trong cache VM này dù package.json của demo-30s ghim 0.9.81. Suy ra: không
  được lấy số đo demo #3 làm "baseline cùng phiên bản" một cách mù — mọi số đo
  vòng 3 phải ghi rõ phiên bản đã ghim.
- **Pin trong repo hiện loạn:** AGENTS.md ghi 0.9.66; package.json demo-30s ghim
  0.9.81; project mẫu + preview cũ ghim 0.9.67; render.py/gates.py gọi bare `npx
  hyperframes` (trôi nổi, hiện ra 0.9.82). `npx hyperframes --version` = 0.9.82.
- **Concat: SFX là BẮT BUỘC, không phải tùy chọn.** Shot composition
  (`build_video.py:shot_html`) chỉ chứa SVG + GSAP, KHÔNG có audio. Giọng + SFX
  chỉ có trong index.html. Demo #3 có 3 cue SFX (SH001/SH006 cloth, SH003 boom);
  Thần Trùng full có 13 SFX. Concat chỉ mux giọng = final thiếu SFX (sai).
- **Concat về mặt thời gian là KHỚP CHÍNH XÁC.** `build_video.py` xếp shot nối
  tiếp nhau không chồng, không hở: shot i kết thúc đúng lúc shot i+1 bắt đầu
  (`ends[i] = wins[i+1][0]`), không có crossfade. Nối ffmpeg stream-copy là đúng
  về cấu trúc; chỉ cần gate duration + tham số từng shot.
- **Lazy-load: reorder đơn giản là ĐÚNG (đã chứng minh, không cần alias-file).**
  Cache key = SHA1(text, voice-như-ghi-trong-script, speed, temperature, ref).
  Quét cache bằng tên giọng THÔ: hit chỉ xảy ra khi key đã lưu khớp đúng tên thô
  đó — tức meta đã ghi bằng đúng tên đó (hoặc tên thô = tên chuẩn). Trường hợp
  alias ("Minh Quân"→"Hải Đăng"): quét thô sẽ MISS (key khác) → vẫn tạo Speaker
  như cũ → canonicalize → tính lại key → hit lại cache. Không có đường nào skip
  Speaker mà dùng nhầm audio. Chỉ bỏ qua `check_cast` khi tất cả đã cache — an
  toàn vì cache tồn tại ⟹ giọng đã từng qua check_cast thành công.
- **Linter: check_shots.py hiện KHÔNG kiểm `focus` chút nào** (grep 0 kết quả).
  Bug SH006 (`focus: "mam_tre"` không tiền tố) rơi về giữa khung một cách IM LẶNG
  (`focus_point` trả về W/2, H/2); `focus: "prop:<id-không-tồn-tại>"` thì
  KeyError lúc build_video (crash ở bước dựng, không phải ở gate).
- **Detector: bộ lọc ffmpeg có sẵn** (blackdetect, freezedetect, silencedetect).
  Nhưng file bug nhịp 2 Thần Trùng đen toàn bộ KHÔNG còn tồn tại trong bản final
  (đã render lại) — không có "mẫu bug thật" để test trực tiếp; phải tổng hợp
  clip test + đo tỉ lệ báo động giả trên file full 34 phút
  (`~/workspace/than-trung-video/full-video/than-trung-full.mp4`).
- **Rust CHƯA cài trên VM** (`rustc: command not found`). Spike oxframe phải tính
  thêm thời gian cài Rust toolchain + build Skia lần đầu.
- **Agent v2 đã có sẵn** (`~/workspace/muse-windows-agent/agent.py`, HTTP server
  cổng 8765, token auth, jobs nền) — v3 polling chỉ cần đổi chiều kết nối, không
  viết lại từ đầu. Queue đọc được không cần auth: repo public → Windows poll
  `raw.githubusercontent.com`.
- **gates.py docstring đang ghi sai:** "Tiết kiệm ~30s mỗi lần chạy gate" — số đo
  thật vòng 2 là ~2s lúc Chrome ấm. Sửa docstring khi đụng vào gates.py.

## 1. Quyết định sửa plan (giữ / bỏ / đổi cách làm / đổi thứ tự)

| # | Mục gốc | Quyết định | Lý do thay đổi |
|---|---------|------------|----------------|
| 0 | Ghim hyperframes (0.9.81 theo package.json) | **ĐỔI: ghim 0.9.82** trong render.py + gates.py (hằng `HYPERFRAMES_VERSION`, cờ `--hyperframes-version` để đo), cập nhật docs (AGENTS.md, workflow-v2.md). KHÔNG đụng package.json của project cũ (0.9.67) — ngoài phạm vi. | 0.9.81 chưa bao giờ cài/chạy được chứng minh trên VM này; 0.9.82 đang cài sẵn, research đã xác minh `--help` (cờ --workers, --page-side-compositing, --experimental-fast-capture) trên nó. Mọi số đo vòng 3 ghi rõ "hyperframes 0.9.82 (pinned)". |
| 5 | Lazy-load VieNeu | **GIỮ, đổi cách làm:** tách quét cache thành hàm `scan_cache()` chạy TRƯỚC khi tạo Speaker; 0 line chưa cache → bỏ qua hẳn Speaker; còn line chưa cache → tạo Speaker, canonicalize, tính lại key cho line nào đổi tên + quét lại cache lần 2. | Tránh alias-file (thừa): chứng minh ở mục 0 — quét thô là an toàn. Test mới: stub Speaker (test env không có model) — assert không khởi tạo Speaker khi all-cached; assert alias "Minh Quân"→"Hải Đăng" vẫn hit cache sau canonicalize. |
| 6 | Linter shotlist | **GIỮ, thu hẹp phạm vi:** chỉ thêm kiểm E11 cho `focus` trong check_shots.py (không làm autocomplete UI riêng). Thông báo lỗi liệt kê focus hợp lệ của shot đó (char trong shot + `prop:<id trong shot>` + `slot:<slot của location>`) — đó chính là autocomplete. | E9 đã liệt kê pose hợp lệ trong thông báo lỗi; làm đúng mẫu đó là đủ. Linter CHỈ kiểm tham chiếu, KHÔNG tự sửa focus, KHÔNG gợi ý bố cục — tránh đẩy về shot tĩnh (luật di chuyển 21/11). |
| 2 | Detector ffmpeg | **GIỮ, đổi cách kiểm chứng:** (a) clip tổng hợp (đen 2s giữa video) phải bị flag đúng khoảng; (b) chạy trên Thần Trùng full 34 phút, đo tỉ lệ báo động giả; (c) chạy trên demo #3 draft + final — phải sạch, trừ shot macro tối SH003 (đã biết, kiểm tra mapping khoảng đen → shot để loại trừ mood dark). Ngưỡng chỉnh trên file thật, không dùng mặc định ffmpeg. | Bug thật không còn file để test trực tiếp. Ngưỡng mặc định sẽ báo sai vào cảnh tối cố ý của truyện ma. |
| 3 | --workers | **GIỮ, thu hẹp:** chỉ thêm cờ `--workers` cho render chính; KHÔNG song song hóa vòng lặp `--shots` trong vòng này (ghi follow-up). Đo auto vs 2 vs 4 trên pinned 0.9.82, render delivery demo #3; thử --page-side-compositing + --experimental-fast-capture trên 1 shot trước, đối chiếu frame rồi mới tin. | Song song hóa vòng --shots là thay đổi riêng, chưa đo; giữ vòng 3 gọn. Trên VM 1,5 CPU kỳ vọng ~0 — phép đo mới là deliverable, không phải tốc độ. |
| 1 | Concat nấc 1 | **GIỮ, mở rộng thiết kế:** (a) cho phép `--shots --delivery` (hiện xung đột) → per-shot delivery mp4, tên ổn định `output/shots/<id>.mp4`; (b) concat_shots.py nối video stream-copy + mux lại giọng (voiceover.wav) + SFX (adelay theo start tuyệt đối + amix, volume 0.8 như index.html); (c) gate: duration từng shot ±0,15s + tham số video khớp nhau (codec/res/fps), fail to kèm delta từng shot. | SFX bắt buộc (mục 0). Tên file ổn định mới nối được. Khung giá trị nói thật: concat chỉ thắng khi render LẠI ÍT shot (re-render 1 shot ~25s + nối ~10s vs render full ~193s); lần build đầu không nhanh hơn (mỗi shot delivery vẫn trả phí khởi động Chrome). |
| B | gates.py bỏ Chrome khi diff chỉ .py | **GIỮ:** cờ tường minh `--auto-skip` (không bật mặc định). Dùng `git status --porcelain`: chỉ file .py/md đổi → bỏ worker hyperframes, in rõ lý do; nghi ngờ → vẫn chạy hyperframes (fail-safe). Sửa luôn docstring "~30s" sai. | Bật mặc định là rủi ro âm thầm bỏ gate; cờ tường minh + fail-safe giữ đúng tinh thần gate (R8.2). |
| 4 | v3 polling spike | **GIỮ, thu hẹp phạm vi spike:** chỉ chứng minh vòng lặp (VM đẩy job JSON vào queue repo public → agent Windows poll → chạy lệnh trong allow-list → báo kết quả về). Job spike = tải zip demo + render 1 shot + báo thời gian. Đồng bộ file (model 2GB + rigs) là thiết kế riêng, KHÔNG làm trong spike. Chuẩn bị hết phía VM (agent v3 + submitter + zip + hướng dẫn chạy); nếu Tuấn chưa chạy trong vòng này → báo rõ "đã chuẩn bị xong X, còn cần Tuấn làm Y". | Đường nối là blocker đã biết; spike chỉ cần chứng minh chiều kết nối đảo ngược chạy được. Sync 2GB model không chứng minh được bằng job thử nhỏ. |
| 7 | oxframe spike | **GIỮ THEO LỆNH TUẤN (không hoãn), xếp CUỐI, timebox.** Spike ngoài repo (`~/workspace/oxframe-spike/`). Quy tắc dừng ghi trước: build Rust/Skia >2h wall trên VM HOẶC không nhanh hơn ≥2× trên shot thật HOẶC chữ Việt vỡ dấu → DỪNG ở spike, báo rõ, không triển khai tiếp. | Xem rủi ro ở mục 2. |

## 2. Thứ tự implement đã sửa (có phụ thuộc)

1. **Mục 0 — ghim 0.9.82** (trước MỌI phép đo).
2. **Mục 5 — lazy-load** (độc lập; làm sớm để lần chạy lại đo sạch).
3. **Mục 6 — linter E11** (độc lập).
4. **Mục 2 — detector** (độc lập; cần draft demo #3 để chỉnh ngưỡng).
5. **Mục 3 — đo --workers** (sau ghim; trên demo #3, delivery).
6. **Mục 1 — concat** (sau ghim + sau khi biết workers mặc định tốt nhất; cần `--shots --delivery`).
7. **Backlog — gates.py --auto-skip** (độc lập; đo riêng, không trộn vào số đo gate demo #4).
8. **Mục 4 — v3 polling** (chuẩn bị phía VM; chạy thật cần Tuấn).
9. **Mục 7 — oxframe spike** (cuối cùng; timebox; ngoài repo).

Phụ thuộc chéo cần nhớ: đo workers (5) phải dùng phiên bản đã ghim (1); concat
(6) dùng per-shot delivery render với workers mặc định từ (5); demo #4 đo TTS
lần đầu (fresh cache) KHÔNG thấy lợi ích lazy-load — đo mục 5 bằng lần chạy lại
all-cached riêng; số đo gate demo #4 dùng gates.py mặc định (không --auto-skip).

## 3. Rủi ro từng mục (đã phân tích kĩ)

- **0 Ghim:** phiên bản demo #3 không xác định → so sánh demo #3 vs #4 mang caveat
  phiên bản. Giảm nhẹ: ghi rõ version trong mọi số đo; không tuyên bố "nhanh hơn"
  nếu chỉ khác phiên bản.
- **1 Concat:** (a) nối sai nếu shot mp4 lệch tham số — gate params bắt trước khi
  nối; (b) drift giọng ±0,1s làm mốc SFX/giọng lệch — gate duration từng shot +
  kiểm tổng duration video vs voiceover.wav, lệch >0,15s thì FAIL, không nối mò;
  (c) Chrome stall ra file shot ngắn một nửa (đã gặp ở demo #3) — gate duration
  bắt được; (d) nấc 1 không có cache tự động nên chọn nhầm shot cũ vẫn có thể xảy
  ra — giảm nhẹ bằng tên file ổn định + in rõ danh sách shot + thời gian render
  của từng file trước khi nối.
- **2 Detector:** báo động giả trên cảnh tối/lặng cố ý của truyện ma; draft 15fps
  nén tối bị nhận nhầm là đen. Giảm nhẹ: ngưỡng chỉnh trên file thật; mapping
  khoảng → shot để loại trừ mood dark; đo tỉ lệ báo động giả trên full 34 phút
  trước khi tin; detector chỉ BÁO, không tự fail build (exit 0 kèm cảnh báo)
  trong vòng này — tránh chặn nhầm pipeline.
- **3 Workers:** stall khi nhiều worker cùng seek GSAP nặng (đã có tiền lệ file
  ngắn một nửa); RAM ~256MB/worker; ép workers cao trên máy Tuấn đang dùng việc
  khác sẽ giật máy — đo trên VM chỉ để lấy số, khuyến nghị workers cho máy Tuấn
  ghi rõ "giới hạn theo lúc máy rảnh".
- **4 v3 polling:** cần Tuấn chạy agent trên máy; sync file chưa thiết kế; khác
  biệt Windows/Linux (font, đường dẫn, phiên bản hyperframes); bảo mật: chỉ lệnh
  trong allow-list, token như v2. Nếu Tuấn chưa chạy → spike ở trạng thái
  "đã chuẩn bị", không bịa kết quả đo.
- **5 Lazy-load:** rủi ro duy nhất là alias — đã chứng minh an toàn (mục 0) +
  test hồi quy bắt buộc. Không đổi hành vi khi có line chưa cache.
- **6 Linter:** E11 quá chặt sẽ chặn focus hợp lệ (vd focus char ngoài shot nhưng
  camera cố ý nhìn sang?) — kiểm chứng: focus char PHẢI trong shot (camera theo
  nhân vật trong khung); nếu có use-case focus char ngoài shot thì E11 phải là
  cảnh báo, không phải lỗi. Quyết định khi implement: tra shotlist demo #3 +
  project mẫu — nếu không có case đó, E11 là lỗi.
- **7 oxframe:** Rust chưa cài; build Skia lần đầu có thể >2h trên VM 1,5 CPU;
  oxframe-sdk ~8 sao, API đổi bất cứ lúc nào; font tiếng Việt trong Skia/resvg
  chưa kiểm chứng (vỡ dấu = fail hoàn toàn); oxframe tự kết luận nên dùng
  HyperFrames cho HTML/GSAP; kết cục "hai renderer song song" gấp đôi pipeline.
  Quy tắc dừng đã ghi ở mục 1.

## 4. Xung đột với luật đứng — đã kiểm tra

- **Luật di chuyển 21/11 (cấm shot tĩnh chỉ đứng nói):** linter E11 chỉ kiểm tham
  chiếu focus, không gợi ý bố cục tĩnh — không xung đột. Concat không đổi nội
  dung shot — không xung đột. Detector không đổi nội dung — không xung đột.
- **Luật YouTube 18/11 (mỗi video khác cấu trúc):** không mục nào sinh cấu trúc
  video — generator đã hoãn từ trước, vòng này không đụng tới.
- **RULES.md / R0.3:** không sửa RULES.md; không merge; không mở PR trong vòng
  này (theo brief gốc — LƯU Ý: Tuấn đã đổi ý ở follow-up sau, mở PR sau khi
  push; xem báo cáo cuối).
- **R8.2 (gate phải pass bằng lệnh máy):** detector vòng này chỉ báo, không thay
  gate; concat có gate duration/params riêng, fail thì dừng.

## 5. Plan đã sửa — tóm tắt thay đổi so với plan gốc

- Ghim **0.9.82** thay vì 0.9.81 (có bằng chứng cache).
- Concat **thêm mux SFX + gate duration/params + `--shots --delivery`** (SFX bắt
  buộc; plan gốc chỉ nói mux giọng).
- Detector: **đổi cách kiểm chứng** (clip tổng hợp + đo false-positive trên full
  34 phút + mapping khoảng→shot); detector **chỉ báo, không fail build** vòng này.
- Workers: **bỏ song song hóa vòng --shots** khỏi vòng này (follow-up).
- Lazy-load: **bỏ alias-file**, dùng reorder + quét lại sau canonicalize (chứng
  minh đúng, gọn hơn).
- Linter: **thu hẹp thành E11 focus** (không làm autocomplete UI riêng).
- v3 polling: **thu hẹp spike** thành chứng minh vòng lặp (không làm sync file).
- oxframe: **làm trong vòng này theo lệnh Tuấn, xếp cuối, timebox + quy tắc dừng
  ghi trước** (không hoãn).
- Thứ tự mới: 0 → 5 → 6 → 2 → 3 → 1 → backlog → 4 → 7.
