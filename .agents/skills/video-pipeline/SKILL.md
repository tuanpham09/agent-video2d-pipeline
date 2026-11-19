---
name: video-pipeline
description: Orchestrate the full YouTube-to-video pipeline for this workspace - fetch a YouTube transcript, rewrite it into a retention-optimized Vietnamese script, cast characters and generate synced voiceovers with VieNeu-TTS v3 Turbo, build the film as HTML in HyperFrames, render and package it for YouTube/TikTok. Use when the user gives a YouTube URL, an idea, or says "làm video", "dựng video", "video từ kênh này", "làm short", "làm video dài".
---

# Video Pipeline (YouTube → kịch bản → VieNeu → HyperFrames → MP4)

Một video = một project riêng trong `projects/<slug>/`. Không viết file rác ra root, không trộn asset giữa các video.

## Nguyên tắc vàng

1. **Một nguồn sự thật cho thời lượng:** `audio/manifest.json`. Mọi `data-start` / `data-duration` trong HyperFrames lấy từ đó, không đoán.
2. **Chốt kịch bản trước khi đọc thoại.** TTS rất tốn thời gian; sửa chữ sau khi đã render giọng là làm lại từ đầu.
3. **Chốt preview trước khi render.** `npx hyperframes preview` + snapshot, đưa người dùng xem, rồi mới `render`.
4. **Không tự bịa số liệu, quote, tên riêng** trong kịch bản. Mọi chi tiết lấy từ transcript, mô tả video, hoặc nguồn người dùng đưa.
5. **Tiếng Việt là ngôn ngữ chính.** Câu ngắn, dễ đọc thành tiếng; không viết câu chỉ đẹp trên giấy.
6. **Báo cáo bằng bằng chứng:** đường dẫn file, duration thật, kết quả `check`, không nói "xong" khi chưa kiểm.

## Bản đồ phase

| Phase | Việc | Skill / lệnh |
| --- | --- | --- |
| 0 | Chốt brief: URL/ý tưởng, format, thời lượng, kênh đích, giọng | hỏi tối đa 3 câu |
| 1 | Lấy transcript + metadata + cover | `/baoyu-youtube-transcript` |
| 2 | Viết lại kịch bản + title/thumbnail/description | `/script-rewrite` (+ `/long-form-youtube`, `/storytelling-hooks`, `/titles-and-thumbnails`) |
| 3 | Cast giọng, đọc từng line, đo thời lượng, sinh SRT | `/vieneu-tts` + `/voice-sync` |
| 4 | Dựng film HTML, scene theo beat, audio + caption khớp manifest | `/hyperframes`, `/hyperframes-cli`, `/captions-overlay`, `/hyperframes-registry`, `/media-use` |
| 5 | Check → snapshot → preview → render → QC | `/hyperframes-cli` |
| 6 | Đóng gói upload + lưu bài học | `references/packaging.md` |
| ✎ | Có bản ghi hình talking-head cần cắt ghép nhanh | `/short-editing` (pipeline riêng, không trộn với HyperFrames) |

Skill hỗ trợ thiết kế khung hình: `/design-taste-frontend`, `/high-end-visual-design`, `/minimalist-ui`, `/ui-ux-pro-max`, `/brandkit`, `/imagegen-frontend-web` — dùng khi cần art direction cho scene, không dùng để thay HyperFrames.

## Bước 0 — Brief (chỉ hỏi khi thiếu)

Mặc định nếu người dùng không nói:
- Format: `9:16` (1080×1920) cho TikTok/Shorts; `16:9` (1920×1080) cho video dài YouTube.
- Thời lượng: short 35–60 s; long-form 8–15 phút.
- Giọng: nam `Hải Đăng` (mặc định) hoặc nữ `Đoan Trang`; đa nhân vật thì mỗi nhân vật một giọng.
- Tốc độ đọc: `--speed 1.25` (mặc định của `build_voiceover.py`, dải 1.2–1.3).
- Thể loại **truyện ma / kinh dị**: `Đức Trí` @1.3 (**luôn dùng**), `Thiền Tâm Đức`
  (phương án phụ), `Thiện Minh` (hook), nhân vật `Xuân Vĩnh` — chi tiết + cảnh báo trùng quãng:
  `/script-rewrite` → `references/casting-genres.md`.

Cần hỏi: (1) video dài hay short, (2) kênh đích, (3) có nhân vật/giọng riêng cần clone không.

## Bước 1 — Transcript

```bash
npx -y bun .agents/skills/baoyu-youtube-transcript/scripts/main.ts "<URL>" --languages vi,en --chapters --speakers
```

- Không có tiếng Việt → lấy bản gốc rồi dịch khi viết lại, ghi rõ trong `script/brief.md`.
- Lưu `meta.json`, `transcript.md` vào `source/`. Giữ timestamp để đối chiếu khi kịch bản hoá.
- Video không có caption: tải audio bằng `yt-dlp` rồi `npx hyperframes transcribe` (xem `/media-use`), hoặc dừng và báo người dùng.

## Bước 2 — Kịch bản

Tạo project trước, rồi viết:

```bash
python .agents/skills/video-pipeline/scripts/scaffold_project.py "<slug>" --title "<tựa nháp>" --format 9:16
```

Theo `/script-rewrite`, kết quả bắt buộc:
- `script/brief.md` — người xem mục tiêu, promise, góc tiếp cận, nguồn.
- `script/script.md` — bản đọc cho người.
- `script/script.json` — bản máy đọc (schema: `/script-rewrite` `references/script-schema.md`).
- `script/packaging.md` — title, thumbnail concept, description, hashtags.

**Checkpoint:** đưa `script.md` + packaging cho người dùng duyệt (trừ khi họ nói "không cần hỏi").

## Bước 3 — Giọng đọc đồng bộ

```bash
python .agents/skills/voice-sync/scripts/build_voiceover.py \
  --script "projects/<slug>/script/script.json" \
  --out "projects/<slug>/audio"
```

Sinh ra:
- `audio/lines/*.wav` — từng câu, đúng giọng từng nhân vật, tag cảm xúc.
- `audio/voiceover.wav` — bản ghép đủ khoảng nghỉ, để nghe duyệt.
- `audio/manifest.json` — start/duration tuyệt đối của từng line + scene + tổng.
- `audio/captions.srt` — phụ đề theo đúng timing.

Nghe `voiceover.wav` (hoặc nhờ người dùng nghe) trước khi dựng hình. Sai giọng/sai phát âm → sửa `script.json` hoặc `audio/voice_map.json` rồi chạy lại (cache tự bỏ qua câu không đổi).

## Bước 4 — Dựng HyperFrames (Quy chuẩn hoạt hình 2D chuyển động)

```bash
npx hyperframes init projects/<slug>/video --skip-skills --non-interactive --resolution landscape
```

`--resolution`: `portrait` cho 9:16 (Shorts/TikTok), `landscape` cho 16:9 (YouTube dài).

### Quy chuẩn sản xuất hoạt hình 2D sống động (Bộ 3 kỹ năng kết hợp):
Khi làm video hoạt hình hoặc kể chuyện (truyện ma, explainer, drama), **không dựng slide ảnh tĩnh**. Bắt buộc phối hợp 3 kỹ năng:

1. **`reverse-any-video` — Đo đạc bố cục & Framing:**
   * Bố cục rõ ràng tiền cảnh – trung cảnh – hậu cảnh: Vách nhà, sàn gỗ, bàn thờ, mâm đan, chõng tre, cửa mở ra vườn sương đêm...
   * Góc máy có chủ đích: Toàn cảnh thiết lập bối cảnh, chuyển cảnh cắt sắc bén (hard cut) vào cận cảnh hành động chính (đếm khăn, giã trầu...).

2. **`claude-animation-base` — Vẽ tay hữu cơ, Line Boil & 31 Biểu cảm:**
   * **Hiệu ứng rung nét vẽ tay (Line Boil):** Tích hợp SVG filter `<feTurbulence type="fractalNoise">` + `<feDisplacementMap scale="2.4">` thay đổi seed theo nhịp 6–12fps (`animating on twos`), tạo cảm giác vẽ tay sống động thay vì nét vector phẳng đơ.
   * **Rig cử động nhân vật (Character Motion Rig):**
     * Thở tự nhiên: Ngực và thân sways nhẹ nhàng theo trục Y (`yoyo: true`).
     * Mắt chớp hữu cơ: Eyelid scaleY từ 0 -> 1 -> 0 sau mỗi 2–4 giây.
     * Đồng tử mắt linh hoạt: Liếc nhìn đạo cụ, nhìn lửa, liếc sang góc tối khi sợ hãi.
     * Khẩu hình nói: Miệng đóng mở đồng bộ với âm tiết của từng line thoại.
     * Cử động tay chân: Cầm chày giã cối nhịp nhàng, tay lật đếm từng nếp khăn, tay vung chỉ hướng cửa.
   * **Yếu tố kịch tính & Kinh dị:** Ánh sáng đèn/nến đột ngột hạ tối, thực thể ma quái từ từ trồi lên từ góc tối.

3. **`hyperframes` + `media-use` — Động cơ dựng & Hòa âm 4 tầng:**
   * **Tầng 1 (Giọng đọc):** VieNeu-TTS v3 Turbo phân vai đa nhân vật, khớp tuyệt đối theo `data-start` và `data-duration` của `manifest.json`.
   * **Tầng 2 (Nhạc nền BGM):** Dải ambient horror drone kết hợp tiếng gió và tiếng côn trùng đêm thanh vắng.
   * **Tầng 3 (SFX hiện trường):** Tiếng cối giã "cốc... cốc...", tiếng sột soạt lật đếm vải (`cloth_rustle.wav`), tiếng ngọn lửa cháy lách tách.
   * **Tầng 4 (Stinger):** Tiếng sub-bass giáng mạnh đúng thời điểm cao trào/bước ngoặt.
   * Chi tiết tham khảo toàn diện: Xem tài liệu **[references/2d-animation-doctrine.md](references/2d-animation-doctrine.md)**.

## Bước 5 — Kiểm và render

```bash
cd projects/<slug>/video
npx hyperframes lint
npx hyperframes check --json
python ../../../.agents/skills/video-pipeline/scripts/check_sync.py --project ../
npx hyperframes preview --background
npx hyperframes render --quality delivery -o ../output/final.mp4
```

QC bắt buộc: duration video = `manifest.duration` ±0.1 s; không có clip vượt `data-duration`; ảnh snapshot từng scene đã xem; tiếng Việt không lỗi dấu; caption không đè UI.

## Bước 6 — Đóng gói

Theo `references/packaging.md`: title ≤ 60 ký tự (Shorts) / ≤ 70 (long-form), description 3 dòng đầu chứa từ khoá, chapters cho video dài, 3–5 hashtag, caption TikTok, pinned comment. Lưu `output/publish.md`.

## Cấu trúc project

```
projects/<slug>/
├── PROJECT.md            # trạng thái từng phase
├── source/               # transcript, meta, cover gốc
├── script/               # brief.md, script.md, script.json, packaging.md
├── audio/
│   ├── voice_map.json    # override giọng (tuỳ chọn)
│   ├── lines/            # từng câu .wav
│   ├── voiceover.wav
│   ├── captions.srt
│   └── manifest.json
├── assets/               # ảnh, logo, nhạc, sfx, font dùng chung
├── video/                # project HyperFrames
└── output/               # final.mp4, thumbnail, publish.md
```

## Khi có sự cố

| Triệu chứng | Xử lý |
| --- | --- |
| `ModuleNotFoundError: vieneu` | `pip install vieneu` (CPU/ONNX) hoặc `pip install "vieneu[cuda]"` |
| Giọng đọc sai tên riêng | Viết phiên âm trong `script.json` (vd `ChatGPT` → `chát-gi-pi-ti`), không sửa file wav |
| Timing lệch sau khi sửa lời | Chạy lại `build_voiceover.py` rồi `check_sync.py`, không sửa tay manifest |
| HyperFrames báo clip vượt duration | Tăng `data-duration` của root theo manifest, không cắt audio |
| Render ra file 0 byte | Xem log, `npx hyperframes doctor --json`, kiểm Chrome/FFmpeg |
| Video dài > 10 phút render lâu | `HYPERFRAMES_RENDER_DETACHED=1`, theo dõi log, không chặn session |
