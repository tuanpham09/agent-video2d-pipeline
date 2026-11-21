# Video Studio — hướng dẫn cho agent

Workspace này sản xuất video YouTube / TikTok từ nguồn có sẵn: transcript → kịch bản tiếng Việt → giọng đọc VieNeu-TTS → HyperFrames → MP4.

## ⛔ RULE BẮT BUỘC cho mọi agent khi làm video

Áp dụng cho **mọi agent** (Claude, Codex, Cursor, agent con…) và mọi yêu cầu liên quan đến video trong repo này. Không có ngoại lệ ngầm; chỉ người dùng mới được miễn một bước, và phải nói rõ.

1. **Bắt đầu bằng `/video-pipeline`** và đọc `.agents/skills/video-pipeline/references/workflow-v2.md` trước khi làm bất cứ việc gì. Không tự nghĩ ra quy trình riêng.
2. **Đi đúng thứ tự giai đoạn**: A/B (QA nguồn → viết lại) hoặc C (ý tưởng → bible → đề cương → kịch bản) → **demo 30–40 s** → 👤 người dùng duyệt → mới làm full. Không nhảy cóc, không làm full khi demo chưa được duyệt.
3. **Gate phải pass bằng lệnh máy, không tự tuyên bố**: `originality_check.py` (A/B), `check_shots.py`, `check_sync.py`, `hyperframes lint/check`. Gate fail → sửa nguồn (script/bible/shotlist/rig) rồi chạy lại; không sửa tay file sinh tự động, không hạ ngưỡng, không bỏ qua cảnh báo lỗi.
4. **Cập nhật `projects/<slug>/PROJECT.md` sau mỗi gate** (ngày, lệnh, kết quả). Chưa ghi = chưa xong.
5. **Một video = `projects/<slug>/`**; scaffold bằng `scaffold_project.py`. Không ghi file lạc ra root, không tạo generator/pipeline song song cho từng video.
6. **Chốt kịch bản trước TTS, chốt preview trước render final.** Giọng cho bản đầy đủ chỉ chạy sau khi demo được duyệt.
7. **Thiếu thông tin hoặc gate không đi qua được → dừng và hỏi người dùng**, nêu rõ đang kẹt ở bước nào. Không bịa số liệu/quote/tên, không dùng nội dung có bản quyền khi chưa có `source/permission.md`.
8. **Sửa quy trình thì sửa trong `workflow-v2.md` / skill tự viết** (`video-pipeline`, `script-rewrite`, `voice-sync`) và ghi trong PR; không âm thầm làm khác.

Vi phạm một mục ở trên = kết quả không hợp lệ, phải làm lại từ giai đoạn bị bỏ qua.

## Bắt đầu ở đâu

Gọi skill **`/video-pipeline`** cho mọi yêu cầu làm video. Skill đó giữ thứ tự phase, checkpoint và QC. Không dựng video bằng cách tự viết ffmpeg/PIL thay cho HyperFrames trừ khi người dùng yêu cầu.

Quy trình chi tiết, checklist từng giai đoạn và các gate: `.agents/skills/video-pipeline/references/workflow-v2.md`.

- "làm video <URL>" → Chế độ A. "clone video <URL>" → Chế độ B. "làm video: <ý tưởng>" (không URL) → Chế độ C.
- A/B: QA nguồn → viết lại chống reup (`originality_check.py`). C: xác nhận ý hiểu → thể loại/nhân vật/bối cảnh → đề cương → kịch bản 10–30 phút (`--speed 1.3`).
- Cả ba: demo 30–40 s (`check_shots.py`, `check_sync.py`) → người dùng duyệt → mới làm full. Không sang giai đoạn sau khi gate chưa pass; cập nhật `PROJECT.md` sau mỗi gate.
- `reverse-any-video` chỉ để đo nhịp/cỡ cảnh/màu; không xuất bản bản dựng lại khung hình hay nhân vật của nguồn.

Chuỗi skill:

1. `/baoyu-youtube-transcript` — lấy transcript, metadata, cover.
2. `/script-rewrite` — viết lại kịch bản + `script.json` + packaging.
3. `/voice-sync` + `/vieneu-tts` — đọc từng câu, sinh `manifest.json` + SRT.
4. `/hyperframes` (+ `-cli`, `-registry`, `captions-overlay`, `media-use`) — dựng và render.
5. `/video-pipeline` → `references/packaging.md` — đóng gói xuất bản.
6. `/short-editing` — chỉ khi có bản ghi talking-head cần cắt ghép nhanh; không trộn với HyperFrames.

## Luật cứng

- Một video = `projects/<slug>/`. Không ghi asset/audio lạc ra root.
- Giọng mặc định `Hải Đăng` (nam, Bắc); tốc độ đọc mặc định `--speed 1.25`, chỉ chỉnh trong dải 1.2–1.3.
- **Truyện ma: người kể luôn là `Đức Trí`** ở `--speed 1.3`; nhân vật nam dùng `Xuân Vĩnh`, `Thiền Tâm Đức` là phương án phụ. Không đổi giọng kể ma trừ khi người dùng yêu cầu.
- `audio/manifest.json` là nguồn duy nhất cho `data-start` / `data-duration`. Cấm sửa tay số trong manifest.
- `audio/lines/*.wav`, `audio/scenes/*.wav`, `audio/voiceover.wav` là file sinh tự động. Muốn đổi lời/giọng → sửa `script/script.json` (hoặc `audio/voice_map.json`) rồi chạy lại.
- Không bịa số liệu, quote, tên riêng. Mọi chi tiết lấy từ `source/` hoặc nguồn người dùng đưa.
- **Ưu tiên nhiều Shot & Nhịp chuyển cảnh dồn dập (Multi-shot Cinematic Pacing):** Tuyệt đối không giữ khung hình tĩnh quá 4–6 giây. Chia nhỏ kịch bản thành nhiều shot đa dạng (Toàn cảnh thiết lập bối cảnh, Trung cảnh hành động, Cận cảnh biểu cảm mắt/miệng, Góc nhìn qua vai, Cú lia máy zoom-in/pull-back). Video 1 phút phải có từ 12–15 shots trở lên để tạo cảm giác hồi hộp, gay cấn, lôi cuốn người xem liên tục.
- **Hệ thống SFX dày đặc & Cao trào (Dense Suspense Foley & SFX):** Mọi hành động vật lý (tiếng vải sột soạt, va chạm kim loại khay mâm, tiếng gõ cối đồng nhịp nhàng, bước chân, gió rít, nến nổ, tim đập thình thịch 58Hz, tiếng thở dốc, chuông tang) bắt buộc phải có SFX đi kèm. Sử dụng Horror Stingers (bass drop 38Hz, rít chói tai, dread slam) đúng thời điểm cao trào hoặc hé lộ kinh dị, đồng bộ chính xác từng mili-giây với chuyển động hình ảnh.
- **Chuẩn hóa GSAP TransformOrigin trên SVG (Chống văng lệch chi tiết):**
  - Tuyệt đối không truyền pixel canvas tuyệt đối vào `transformOrigin` của phần tử con SVG (như `transformOrigin: "962px 420px"` sẽ làm phần tử bay hàng trăm pixel).
  - Chi tiết mặt (mồm, mắt, con ngươi, ngực thở): luôn dùng `transformOrigin: "50% 50%"` để mấp máy hoặc co giãn ngay tại tâm bộ phận.
  - Khớp vai, cánh tay, cẳng chân: dùng `transformOrigin: "0% 0%"` (đỉnh trên của bounding box khớp nối) để cánh tay gắn chặt vào vai khi vung chày hoặc ra hiệu.
- **Kịch bản (`script.json` / `script.md`):** trường `visual` bắt buộc mô tả chi tiết quang cảnh 5 thành phần (quang cảnh bối cảnh, bố cục nhân vật, cử động & biểu cảm 31 sắc thái, ánh sáng động, hiệu ứng âm thanh SFX đi kèm).
- **Dựng hoạt hình 2D sống động:** tuân thủ `references/2d-animation-doctrine.md` (kết hợp `reverse-any-video` đo bố cục, `claude-animation-base` rung nét vẽ tay line-boil 12fps + cử động mắt/miệng/tay/thở, và `hyperframes` hòa âm 4 tầng: Voice, BGM, SFX, Stinger). Không làm slide ảnh tĩnh.
- **Ổ đĩa render:** Luôn đặt `$env:TEMP = 'D:\temp'; $env:TMP = 'D:\temp'` trước khi render HyperFrames để tránh tràn ổ C:.
- Không tuyên bố hoàn thành trước khi: `check_sync.py` trả `OK`, `hyperframes check --json` có `ok: true`, và đã xem snapshot/preview.
- Chốt kịch bản trước khi TTS; chốt preview trước khi render final.

## Môi trường đã kiểm

| Thành phần | Trạng thái |
| --- | --- |
| Python | 3.14.5, `vieneu` 3.8.4 đã cài (25 giọng preset, mặc định `Hải Đăng`), model `VieNeu-TTS-v3-Turbo` đã cache (~2 GB) |
| Node / npm | v24.16, `npx hyperframes` 0.9.66 chạy được |
| FFmpeg / ffprobe | 8.1.1 |
| yt-dlp | có (fallback transcript) |
| bun | không cài global; dùng `npx -y bun` (script transcript cần) |

## Lệnh thường dùng

```bash
# 1. khung project
python .agents/skills/video-pipeline/scripts/scaffold_project.py "slug" --title "Tựa" --format 9:16

# 2. transcript
npx -y bun .agents/skills/baoyu-youtube-transcript/scripts/main.ts "<URL>" --languages vi,en --chapters --speakers

# 3. kiểm kịch bản không cần model
python .agents/skills/voice-sync/scripts/build_voiceover.py --script projects/<slug>/script/script.json --out projects/<slug>/audio --dry-run

# 4. đọc thoại + timing (mặc định --speed 1.25; dải khuyến nghị 1.2–1.3)
python .agents/skills/voice-sync/scripts/build_voiceover.py --script projects/<slug>/script/script.json --out projects/<slug>/audio

# 5. HyperFrames
npx hyperframes init projects/<slug>/video --skip-skills --non-interactive --resolution portrait
cd projects/<slug>/video && npx hyperframes lint && npx hyperframes check --json

# 6. kiểm đồng bộ audio ↔ HTML
python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/<slug>

# 7. render
cd projects/<slug>/video && npx hyperframes render --quality delivery -o ../output/final.mp4
```

## Skill tự viết (khác skill cài từ marketplace)

| Skill | Vai trò |
| --- | --- |
| `video-pipeline` | Orchestrator + layout + QC + packaging + 2 script kiểm tra |
| `script-rewrite` | Chuẩn kịch bản tiếng Việt, schema `script.json`, luật viết cho TTS |
| `voice-sync` | `build_voiceover.py`: nhiều giọng, cache, manifest, SRT |

Sửa 3 skill này khi quy trình đổi; đừng sửa skill marketplace (cập nhật sẽ ghi đè).
