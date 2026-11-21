# Video Studio — YouTube → kịch bản → giọng đọc → video

Workspace này đã được cài sẵn bộ skill cho quy trình:

```
Transcript YouTube  →  Viết lại kịch bản  →  VieNeu-TTS (nhiều nhân vật)  →  HyperFrames (HTML → video)  →  MP4 + phụ đề + đóng gói
```

## Luật chung & thư viện dùng chung

- **[`RULES.md`](RULES.md)** — luật cấp cao nhất của repo (mỗi luật có ID `R0`–`R9`). Mọi agent/skill phải tuân theo; `AGENTS.md` và `CLAUDE.md` đều trỏ về đây. Kiểm bằng `check_rules.py`.
- **[`library/`](library/README.md)** — rig (archetype + outfit), đạo cụ, bối cảnh, palette dùng lại cho mọi project. Quy trình: tra (`library.py list`) → dùng lại (`library.py use`) → làm mới thì đạt chuẩn rồi `promote`.

## Đã cài gì

### Skill tự viết cho dự án (`.agents/skills/`)

| Skill | Việc |
| --- | --- |
| **video-pipeline** | Điều phối các phase, cấu trúc thư mục, QC, đóng gói; kèm `scaffold_project.py`, `build_rig.py`, `library.py`, `check_rules.py`, `check_shots.py`, `check_sync.py`, `originality_check.py` |
| **script-rewrite** | Chuẩn viết kịch bản tiếng Việt giữ chân người xem, schema `script.json`, luật viết cho TTS, ví dụ đầy đủ |
| **voice-sync** | `build_voiceover.py`: đọc cả kịch bản bằng nhiều giọng (mặc định 1.25×), cache theo câu, xuất `manifest.json` + `captions.srt` + audio từng scene |

### Skill cài từ marketplace

| Skill | Nguồn | Vai trò |
| --- | --- | --- |
| `vieneu-tts` | `phuongdev89/my-agent-skills` | VieNeu-TTS v3 Turbo: 25 giọng preset Bắc/Trung/Nam (kèm `list_voices.py`), clone 3–8 s, 3 tag cảm xúc, đọc 1.25× |
| `hyperframes` | `heygen-com/hyperframes` | Dựng video bằng HTML, timeline GSAP, render frame-by-frame |
| `hyperframes-cli` | `heygen-com/hyperframes` | `npx hyperframes init/check/preview/render/timeline` |
| `hyperframes-registry` | `heygen-com/hyperframes` | ~450 block dựng sẵn (title, transition, chart, caption...) |
| `captions-overlay` | `heygen-com/hyperframes` | Quy tắc đặt phụ đề lên hình |
| `media-use` | `heygen-com/hyperframes` | Nhạc, SFX, ảnh, logo, voice, treatment footage |
| `style-sampling` | `heygen-com/hyperframes` | Làm tập mới theo style đã chứng minh |
| `reverse-any-video` | `heygen-com/hyperframes` | Dựng lại video mẫu thành project sửa được |
| `baoyu-youtube-transcript` | `jimliu/baoyu-skills` | Lấy transcript, chapter, speaker, cover |
| `edge-tts` | `aahl/skills` | TTS dự phòng (Microsoft Edge voices) |
| `long-form-youtube` | `yaxeen/storytelling-skills` | Khung kịch bản 6–25 phút, chống tụt retention |
| `storytelling-hooks` | `yaxeen/storytelling-skills` | Hook 2 giây, 6 đòn bẩy tâm lý |
| `retention-audit` | `yaxeen/storytelling-skills` | Đọc retention graph, tìm chỗ rớt |
| `titles-and-thumbnails` | `yaxeen/storytelling-skills` | Title + thumbnail ăn click |
| `short-editing` | `melvynx/video-agent-skills` | Cắt talking-head thành short có caption, nhạc, SRT (pipeline riêng) |

Skill thiết kế đã có sẵn trên máy vẫn dùng được để art-direction scene: `design-taste-frontend`, `high-end-visual-design`, `minimalist-ui`, `ui-ux-pro-max`, `brandkit`, `imagegen-frontend-web`.

## Quy trình 1 video

```bash
# 0) khung project
python .agents/skills/video-pipeline/scripts/scaffold_project.py "ai-agent-tu-lam-viec" \
  --title "AI agent tự làm việc 8 tiếng" --format 9:16

# 1) transcript
npx -y bun .agents/skills/baoyu-youtube-transcript/scripts/main.ts "<URL>" --languages vi,en --chapters --speakers

# 2) viết script/script.json theo /script-rewrite, rồi kiểm nhanh (không cần model)
python .agents/skills/voice-sync/scripts/build_voiceover.py \
  --script projects/ai-agent-tu-lam-viec/script/script.json \
  --out projects/ai-agent-tu-lam-viec/audio --dry-run

# 3) đọc thoại + sinh timing + phụ đề (mặc định --speed 1.25, dải 1.2–1.3)
python .agents/skills/voice-sync/scripts/build_voiceover.py \
  --script projects/ai-agent-tu-lam-viec/script/script.json \
  --out projects/ai-agent-tu-lam-viec/audio

# 4) dựng HyperFrames
npx hyperframes init projects/ai-agent-tu-lam-viec/video --skip-skills --non-interactive --resolution portrait
cd projects/ai-agent-tu-lam-viec/video
npx hyperframes lint
npx hyperframes check --json

# 5) kiểm audio khớp hình
python ../../../.agents/skills/video-pipeline/scripts/check_sync.py --project ..

# 6) render
npx hyperframes render --quality delivery -o ../output/final.mp4
```

Hoặc chỉ cần nói với agent: **"làm video từ link này"** — `/video-pipeline` sẽ dẫn toàn bộ chuỗi.

## Cấu trúc một video

```
projects/<slug>/
├── PROJECT.md        # checklist 7 phase
├── source/           # transcript, metadata, cover
├── script/           # brief.md, script.md, script.json, packaging.md
├── audio/            # lines/, scenes/, voiceover.wav, manifest.json, captions.srt
├── assets/           # ảnh, logo, nhạc, sfx, font
├── video/            # project HyperFrames (index.html + compositions/)
└── output/           # final.mp4, thumbnail, publish.md
```

`audio/manifest.json` chứa `start`/`duration` tuyệt đối của từng câu — HyperFrames đọc đúng file này nên lời và hình không lệch.

## Môi trường (đã kiểm tra)

- Python 3.14.5, `vieneu` đã cài, model v3 Turbo đã cache (~2 GB) → đọc offline.
- Node 24.16, `npx hyperframes` 0.9.66, FFmpeg 8.1.1, yt-dlp, `npx bun`.
- Test thật đã chạy: tạo project → 2 câu thoại 2 giọng → `manifest.json` + SRT → `check_sync.py` pass/fail đúng → `hyperframes init` + `check` báo `ok: true`.

## Lưu ý

- Skill chạy với toàn quyền agent. `vieneu-tts` (8 lượt cài) và nhóm `storytelling-skills` (dưới 1K) ít người dùng — đã đọc nội dung, không có lệnh lạ, nhưng nên biết.
- HyperFrames gửi telemetry khi dùng CLI; tài khoản chỉ cần cho tính năng cloud, render local miễn phí.
- Font tiếng Việt: kiểm tra dấu trên snapshot trước khi render; nếu thiếu, thêm `@font-face` từ `assets/fonts/`.
- Giọng clone cần file mẫu 3–8 s sạch (một người, không nhạc). Sai tên riêng thì sửa phiên âm trong `script.json`, đừng sửa file wav.
- Đổi lời sau khi đã dựng: sửa `script.json` → chạy lại `build_voiceover.py` (cache giữ câu không đổi) → `check_sync.py` → sửa các `data-start` bị lệch.

## Việc nên làm tiếp

1. Thử một video 30–45 s từ link YouTube thật để chốt giọng và phong cách hình.
2. Nếu có giọng thật/KOC: đặt file mẫu vào `projects/<slug>/assets/voices/` và khai báo `ref_audio`.
3. Chốt template HyperFrames riêng (font, màu, caption) rồi lưu thành một project mẫu để tái sử dụng.
