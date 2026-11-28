# RULES — luật chung của repo (cấp cao nhất)

**Phiên bản luật: 3**

> Lịch sử: **v3** (2026-11-27) — thêm R13 (kịch bản có bối cảnh và logic liền mạch). Nâng phiên bản theo chỉ thị rõ ràng của người dùng trong phiên ("Sửa RULE nếu cần thiết", R0.2, ghi ở *Ngoại lệ* của `PROJECT.md`). **v2** (2026-11-22) — thêm R10 (tay nghề), R11 (tương tác nhân vật), R12 (giọng đọc). Nâng phiên bản theo chỉ thị rõ ràng của người dùng trong phiên (R0.2, ghi ở *Ngoại lệ* của `PROJECT.md`). **v1** — R0–R9. Sửa chữ R11.5 và R11.1 (2026-11-26) theo duyệt rõ ràng của người dùng: `hand_over`/`reach` đã có trong generator; không đổi số phiên bản luật.

Mọi agent (mọi skill, subagent, phiên làm việc) phải đọc file này **trước khi làm bất cứ việc gì** trong repo.
Skill, workflow, `PROJECT.md`, ghi chú, memory mà mâu thuẫn với file này thì **file này thắng**.

Mỗi luật có ID (`R2.3`…) để dẫn chiếu trong báo cáo, review và `PROJECT.md`. Cột "Kiểm" ở cuối cho biết công cụ nào bắt vi phạm.

---

## R0. Hiệu lực

- **R0.1** Đọc `RULES.md` đầu phiên; khi `Phiên bản luật` đổi thì đọc lại. Project ghi `Luật áp dụng: RULES.md vN` trong `PROJECT.md`.
- **R0.2** Chỉ chỉ thị **rõ ràng của người dùng trong phiên hiện tại** mới được đè luật. Khi đè, ghi vào `PROJECT.md` mục *Ngoại lệ*: luật nào, vì sao, người dùng nói gì.
- **R0.3** Agent **không tự sửa** `RULES.md`. Muốn đổi luật: nêu đề xuất và chờ người dùng.
- **R0.4** Luật không làm được hoặc mâu thuẫn với thực tế: dừng, báo, hỏi. Không âm thầm bỏ qua, không "làm gần giống".
- **R0.5** File hướng dẫn trong từng project (`projects/*/**/AGENTS.md`, `CLAUDE.md`, vd do `hyperframes init` sinh ra) không được nới luật và phải mở đầu bằng dòng trỏ về file này.

## R1. Cấu trúc & nguồn sự thật

- **R1.1** Một video = `projects/<slug>/`. Không ghi asset/audio lạc ra root. Thư mục dùng chung duy nhất được phép ngoài project: `library/` (R2), `sfx/`, `.agents/`.
- **R1.2** `audio/manifest.json` là nguồn duy nhất cho `data-start` / `data-duration`. Cấm sửa tay số trong manifest.
- **R1.3** `audio/lines/*.wav`, `audio/scenes/*.wav`, `audio/voiceover.wav` là file sinh tự động. Muốn đổi lời/giọng → sửa `script/script.json` (hoặc `audio/voice_map.json`) rồi chạy lại.
- **R1.4** `script/bible.json` là nguồn duy nhất về nhân vật, bối cảnh, đạo cụ, từ vựng cảm xúc của project. Shotlist và generator chỉ tham chiếu id trong bible.
- **R1.5** Chốt kịch bản trước khi TTS. Chốt preview trước khi render final.
- **R1.6** Một generator đọc dữ liệu (manifest + bible + shotlist) dựng cảnh. Không viết tay HTML/SVG riêng cho từng shot.

## R2. Thư viện dùng chung `library/` — tra trước, tạo sau

Mục tiêu: nhân vật, đạo cụ, bối cảnh làm một lần, dùng cho mọi project sau.

- **R2.1** **Tra trước khi tạo.** Trước khi vẽ/tạo nhân vật, đạo cụ, bối cảnh, palette: chạy `library.py list` (lọc `--tag`/`--kind`). Ghi kết quả tra vào bible (`lib` của từng mục). Chỉ tạo mới khi library chưa có thứ dùng được.
- **R2.2** **Dùng lại bằng `library.py use`** (chép có khoá phiên bản vào `assets/`, ghi `assets/LIBRARY.lock.json`). Không chép tay, không vẽ lại thứ library đã có.
- **R2.3** **Sửa tại nguồn.** Lỗi/cải tiến của asset library sửa trong `library/` rồi `reindex` → `check` → `sheet`; **không** sửa bản trong project. Sửa library là thay đổi dùng chung: chỉ được **thêm** state/part/slot/anchor; không đổi tên hay xoá cái đã có. Thay đổi phá vỡ → asset mới (`<id>_v2`).
- **R2.4** **Tạo mới thì làm đúng chuẩn library ngay từ đầu** (R2.5–R2.7), và trước giai đoạn E phải `library.py promote`, hoặc đánh `"scope": "project-only"` kèm `"reason"` trong bible.
- **R2.5** **Màu chỉ là token.** Asset library dùng `var(--pal-<token>)`; bible/archetype dùng tên token. Cấm hex/rgb/hsl/tên màu trong asset library, rig params, và generator dựng cảnh. Cần màu mới → thêm token vào `library/palettes/*.json`.
- **R2.6** **Chuẩn file asset:** một SVG tự chứa; không `<text>`, `<script>`, ảnh/URL ngoài. Đạo cụ: trạng thái bằng `data-state`, gốc toạ độ = giữa-đáy, `parts` có pivot ghi trong `index.json`. Bối cảnh: 1920×1080, ánh sáng bằng `data-light`, ba lớp `layer-far/mid/near`. `id` nội bộ SVG có tiền tố riêng (không trùng giữa các asset).
- **R2.7** **Mỗi asset có mục trong `library/index.json`** (states, tags, anchors/slots/parts, `scene_s`) và xuất hiện trong `library/sheets/*.png`; người dùng duyệt bằng mắt trước khi dựa vào.
- **R2.8** **Nhân vật: archetype + outfit trước, ghi đè sau.** Khuôn người/trang phục mới có thể dùng cho nhiều project → thêm vào `library/rigs/archetypes.json`, không nhét riêng vào một bible.
- **R2.9** `library.py check` phải 0 lỗi trước mọi commit đụng `library/`. `check_rules.py` phải 0 lỗi trước cổng demo và cổng full.
- **R2.10** Project dùng bản đã khoá. Nâng cấp library trong project chỉ khi chủ ý `use` lại và xem lại pose sheet / sheet liên quan.

## R3. Nhân vật & rig

- **R3.1** Một nhân vật = một `id` trong bible = một rig = một giọng. Tên, giọng, trang phục chỉ khai báo ở bible.
- **R3.2** Rig sinh bằng `build_rig.py` từ bible; mọi shot dùng cùng file rig; chỉ đổi trạng thái qua `data-emotion|mouth|pose|stance|gaze|blink|khan`.
- **R3.3** Cảm xúc/hình miệng/tư thế/hướng nhìn chỉ dùng giá trị trong `emotion_vocab` và `<id>.rig.json`.
- **R3.4** **Pivot & nhúng rig** (thay cho luật `0% 0%` cũ): chi tiết mặt dùng `50% 50%`; khớp vai/khuỷu dùng pivot trong `<id>.rig.json` (toạ độ viewBox của rig, `transform-box: view-box`). Rig **chỉ được nhúng dưới dạng `<svg>` lồng nhau có viewBox riêng**; không chép `<g>` trần vào svg cảnh; không truyền px toạ độ cảnh vào `transformOrigin`.
- **R3.5** Trái/phải theo giải phẫu nhân vật (`l` = bên trái nhân vật = bên phải người xem).
- **R3.6** Nhân vật chung giọng không xuất hiện cùng một cảnh.
- **R3.7** Pose sheet của nhân vật được duyệt trước khi dựng shot. Đổi thiết kế → build lại + duyệt lại.
- **R3.8** `build_rig.py` phải báo 0 tổ hợp tràn khung.

## R4. Bối cảnh & đạo cụ

- **R4.1** Mỗi shot khai báo location, ánh sáng, đạo cụ + trạng thái trong shotlist; mọi id/trạng thái phải có trong bible.
- **R4.2** Đặt người/đạo cụ theo anchor của `index.json` (`stand`, `slots`) và `scene_s`; không tự đặt toạ độ tuỳ ý. Mỗi bối cảnh có đủ ba lớp xa/giữa/gần và các trạng thái ánh sáng `warm`, `dark`, `red_flash`, `dawn`.
- **R4.3** Liên tục: trạng thái đạo cụ chỉ đổi khi có beat hành động trong shotlist. Cùng một location giữ nguyên bố cục đạo cụ trừ khi kịch bản đổi.
- **R4.4** Khung 9:16 cắt cửa sổ 608×1080 theo `crop_9x16` của location; không kéo giãn.

## R5. Thoại, shot, diễn xuất

- **R5.1** Mỗi câu thoại ngắn có ít nhất một beat diễn ở shot tương ứng (biểu cảm/miệng/tư thế/đạo cụ).
- **R5.2** Không giữ khung tĩnh quá 6 s. Trung bình 3–5 s/shot; video 1 phút có 12–15 shot trở lên, đa dạng cỡ cảnh (toàn / trung / cận / qua vai / macro đạo cụ / máy chạy).
- **R5.3** Trường `visual` trong `script.json` mô tả đủ 5 thành phần: bối cảnh, bố cục nhân vật, cử động & biểu cảm (theo `emotion_vocab`), ánh sáng, SFX.
- **R5.4** Hoạt hình 2D sống (thở, chớp mắt, đảo mắt, miệng, tay, line-boil), không slide ảnh tĩnh. Chi tiết kỹ thuật: `references/2d-animation-doctrine.md`.

## R6. Âm thanh

- **R6.1** Mọi hành động vật lý có SFX; cue lệch hình tối đa ±0,15 s.
- **R6.2** Hoà âm 4 tầng: Voice, BGM, SFX, Stinger. Stinger đặt đúng khoảnh khắc cao trào.
- **R6.3** Giọng mặc định `Hải Đăng`, `--speed 1.25` (dải 1.2–1.3). **Truyện ma:** người kể luôn `Đức Trí` ở `--speed 1.3`; nhân vật nam `Xuân Vĩnh`, `Thiền Tâm Đức` là phương án phụ. Không đổi giọng kể ma trừ khi người dùng yêu cầu.

## R7. Nội dung gốc

- **R7.1** Không bịa số liệu, quote, tên riêng. Chi tiết lấy từ `source/` hoặc nguồn người dùng đưa.
- **R7.2** Chế độ A/B: qua `originality_check.py` trước khi chốt kịch bản; không giữ cốt truyện cụ thể, tên + quan hệ nhân vật, thứ tự tiết lộ, câu chữ của nguồn.
- **R7.3** `reverse-any-video` chỉ để đo nhịp/cỡ cảnh/màu; không xuất bản bản dựng lại khung hình hay nhân vật của nguồn.

## R8. Cổng, duyệt, báo cáo

- **R8.1** Làm theo `workflow-v2.md`: demo 30–40 s → người dùng duyệt → mới làm full. Không sang giai đoạn sau khi gate trước chưa pass; cập nhật `PROJECT.md` sau mỗi gate.
- **R8.2** Không tuyên bố hoàn thành trước khi: `check_sync.py` trả `OK`, `check_shots.py` 0 lỗi, `check_rules.py` 0 lỗi, `hyperframes check --json` có `ok: true`, và đã xem snapshot/preview.
- **R8.3** Báo cáo bằng bằng chứng: đường dẫn file, số đo thật, kết quả lệnh. Điều chưa kiểm phải nói rõ là chưa kiểm.
- **R8.4** Giai đoạn E (đóng gói) chỉ qua khi `check_rules.py --phase final` sạch: mọi asset mới đã `promote` hoặc có lý do `project-only` (R2.4).

## R9. Môi trường & dựng

- **R9.1** Dựng và render bằng HyperFrames; không thay bằng ffmpeg/PIL tự viết trừ khi người dùng yêu cầu.
- **R9.2** Trước khi render đặt `$env:TEMP = 'D:\temp'; $env:TMP = 'D:\temp'` để tránh tràn ổ C:.
- **R9.3** Không animate trực tiếp phần tử `class="clip"` (chỉ animate thẻ con). Không gán `transform` cố định trong CSS nếu GSAP cũng điều khiển thuộc tính đó (khởi tạo bằng `gsap.set`). Gán `data-layout-allow-overflow` cho `#root`, các scene và `<svg>`.
- **R9.4** Thời lượng composition và track audio lấy từ `manifest.json` (R1.2).


## R10. Tay nghề (craft) — bắt buộc khi tạo nhân vật, đạo cụ, bối cảnh, dựng video

Chi tiết từng bước, mẫu vàng, checklist mắt, lỗi đã biết: [`.agents/skills/video-pipeline/references/craft-playbook.md`](.agents/skills/video-pipeline/references/craft-playbook.md). Phải đọc playbook trước khi làm bất kỳ việc nào trong mục này.

- **R10.1** Làm theo `craft-playbook.md`; không tự nghĩ ra quy trình vẽ/dựng riêng; không bỏ bước nào.
- **R10.2** **Nhìn ảnh thật rồi mới báo xong.** Mọi nhân vật/đạo cụ/bối cảnh/shot mới hoặc sửa phải render ra PNG và agent mở ảnh xem ở cỡ dùng thật; lặp ít nhất một vòng sửa nếu thấy lệch. Lệnh check xanh không thay cho việc xem. Không xem được ảnh → dừng và báo người dùng (R0.4), không tuyên bố đạt.
- **R10.3** Clone mẫu vàng, không vẽ từ trắng: nhân vật theo archetype+outfit hoặc `extends`; đạo cụ/bối cảnh copy asset library gần nhất rồi sửa. Tạo mới phải đạt chuẩn library ngay (R2.4–R2.7).
- **R10.4** Mỗi nhân vật có `assets/rig/sheets/<id>.png` và được xem/duyệt trước khi dựng shot (R3.7). Đạo cụ mới có trong `library/sheets/` và đã thử ghép vào bối cảnh thật cạnh một nhân vật.
- **R10.5** Tương thích HyperFrames: CSS asset/rig không dùng combinator `>`; glow bằng `radialGradient`; rig chỉ nhúng dạng `<svg>` lồng (R3.4).
- **R10.6** Dựng shot chỉ bằng `build_video.py` từ `shotlist.json` (R1.6). Mọi beat nhìn thấy được có `set`/`move`/`look`/`react`; beat vật lý có SFX (R6.1). Thiếu tính năng → mở rộng generator, không vá riêng một video.
- **R10.7** Báo cáo theo khung playbook §8: có dòng "Ảnh đã XEM: <đường dẫn> — thấy gì, lỗi đã sửa" và "Chưa kiểm". Nhật ký gate trong `PROJECT.md` nêu snapshot/ảnh đã xem khi đã dựng video.

## R11. Tương tác nhân vật — bắt buộc khi có từ hai nhân vật trở lên trong một shot

- **R11.1** Shot có ≥ 2 nhân vật: **mỗi nhân vật** có ít nhất một hành vi tường minh (beat `set`/`move`/`look`/`react`/`reach`/`hand_over`), kể cả người nói. Với `hand_over`, cả người cho lẫn người nhận đều được tính. Shot chỉ một người nói còn người kia đứng im là không đạt (gate `check_shots` E7).
- **R11.2** Người nói hướng về người nghe khi nói; người nghe phản ứng ở điểm ngắt câu (gật). Generator tự thêm các phản ứng này; beat tường minh luôn ghi đè mặc định.
- **R11.3** Đổi vị trí trong cùng cảnh chỉ bằng `move` (đi có thời gian, không nhảy tức thời). Đổi cảnh/cắt shot là ngoại lệ hợp lệ.
- **R11.4** Giữ trục hai người: trong cùng cảnh, nhân vật ở bên nào giữ bên đó trừ khi có `move` rõ ràng.
- **R11.5** Khi đạo cụ chuyển tay, dùng beat `hand_over` kèm SFX nếu là vật lý (R6.1). `check_shots` kiểm `hand_over` chỉ nhắc nhân vật/đạo cụ có mặt trong shot (E12) và beat vật lý có SFX (E6).

## R12. Giọng đọc & đồng bộ thời gian

- **R12.1** Giọng đọc sinh bằng VieNeu-TTS v3 Turbo (`voice-sync`), chạy trên máy có model. Không coi giọng là đạt khi chưa có `audio/manifest.json` thật (`engine: vieneu-v3-turbo`) và `check_audio.py` xanh.
- **R12.2** Beat lời nói neo theo **từ** (`word`) khi có thể; không dùng số giây đoán khi đã có mốc từ thật (`words` trong manifest). Mốc ước lượng phải được ghi là ước lượng trong báo cáo.
- **R12.3** Kiểm âm thanh bằng máy trước khi dựng: `check_audio.py` (thời lượng khớp manifest, không clip, không câm, không chồng lời, mức âm lượng, tốc độ 1.2–1.3).
- **R12.4** Kiểm phát âm bằng ASR (whisper) là tuỳ chọn: chỉ dùng khi người dùng yêu cầu hoặc khi có nghi ngờ đọc sai; kết quả ghi vào báo cáo.

---

## R13. Kịch bản: bối cảnh, hành trình, logic liền mạch — bắt buộc khi viết hoặc viết lại `script.json`

Chi tiết, mô hình dữ liệu, quy trình, ví dụ: [`.agents/skills/video-pipeline/references/script-continuity-guide.md`](.agents/skills/video-pipeline/references/script-continuity-guide.md).

- **R13.1** Mọi cảnh có `setting` (`location` lấy từ `bible.locations`, `int_ext` khớp `kind` của địa điểm, `time`, `frame`, `link`), `cast` (ai có mặt) và, khi có hành động đổi vị trí/đạo cụ, `staging`. Bối cảnh chưa có trong library thì khai `pending` + lý do trong bible (R2.1), không đặt tên tại chỗ.
- **R13.2** Nhân vật đổi địa điểm giữa hai cảnh phải khai `from` (đi từ đâu tới đâu); đi giữa các địa điểm theo `bible.locations[].connects`, hoặc có `link_note` giải thích khoảng giữa.
- **R13.3** Hồi tưởng, điện thoại, giấc mơ, cắt chen khai `frame` đúng; mốc `story_time` không đi lùi trong dòng `present`; người nói (không phải narrator) phải có trong `cast` của cảnh.
- **R13.4** Đạo cụ chỉ đổi người cầm bằng `give`/`take`/`put` và chỉ đổi trạng thái trong `states` của bible; `shot.location` phải khớp địa điểm của kịch bản (cutaway/insert là ngoại lệ có cảnh báo).
- **R13.5** `check_script_logic.py --strict` phải 0 lỗi trước khi chốt kịch bản và chạy TTS (R1.5) và trước cổng demo/full. Bố trí/mốc giờ không có trong nguồn thì ghi `note: đề xuất`, không coi là sự thật của nguồn (R7.1).

---

## Luật → công cụ kiểm

| Luật | Công cụ |
| --- | --- |
| R0.1, R0.5 | `check_rules.py` (tem phiên bản luật trong PROJECT.md, dòng trỏ ở AGENTS/CLAUDE lồng nhau; `--fix` tự thêm) |
| R2.1, R2.2, R2.4, R2.10 | `check_rules.py` (mục bible có `lib` hoặc `project-only`; `LIBRARY.lock.json`; `--phase final`) |
| R2.3, R2.5–R2.9 | `library.py check` (màu, trạng thái, parts, sha, id trùng, index) |
| R3.x | `build_rig.py` (token lạ, tràn khung), `check_rules.py` (hex trong rig params/generator) |
| R4.1, R5.1, R5.2, R6.1 | `check_shots.py` |
| R1.2, R9.4 | `check_sync.py` |
| R7.2 | `originality_check.py` |
| R8.x | `workflow-v2.md` (checklist + cổng 👤) |
| R10.4, R10.7 | `check_rules.py` (CRAFT: pose sheet; nhật ký gate có ảnh đã xem) |
| R10.1–R10.3, R10.5, R10.6 | `craft-playbook.md` + `library.py check` (cấm `>`) + người duyệt |
| R11.1 | `check_shots.py` E7 |
| R12.2 | `timing_lib.py` + `check_shots.py` E8 (beat theo từ) |
| R12.1, R12.3 | `check_audio.py` (voice-sync) |
| R13.1–R13.5 | `check_script_logic.py` (SL1–SL11; `--strict` khi chốt), `check_shots.py` (E5), `gates.py`; phần đọc hiểu do người duyệt |
