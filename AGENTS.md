# Video Studio — hướng dẫn cho agent

Workspace này sản xuất video YouTube / TikTok từ nguồn có sẵn hoặc từ ý tưởng: kịch bản tiếng Việt → giọng đọc VieNeu-TTS → HyperFrames → MP4.

## 0. ĐỌC TRƯỚC KHI LÀM BẤT CỨ VIỆC GÌ

**[`RULES.md`](RULES.md) là luật chung của repo, cao nhất.** Mọi agent, skill, subagent đều phải đọc và tuân theo. Skill, workflow, `PROJECT.md`, file hướng dẫn lồng trong project, memory mà mâu thuẫn với `RULES.md` thì `RULES.md` thắng. Chỉ chỉ thị rõ ràng của người dùng trong phiên hiện tại mới được đè luật, và phải ghi vào mục *Ngoại lệ* của `PROJECT.md` (R0.2). Agent không tự sửa `RULES.md` (R0.3).

Ba điều hay bị quên nhất:

1. **Tra `library/` trước khi tạo** nhân vật, đạo cụ, bối cảnh (R2.1). Dùng lại bằng `library.py use`; làm mới thì đạt chuẩn library rồi `promote` (R2.4).
2. **Màu chỉ là token** (R2.5); **sửa asset dùng chung tại `library/`**, không sửa bản trong project (R2.3).
3. **Gate phải sạch mới được nói "xong"** (R8.2): `check_rules.py`, `check_shots.py`, `check_sync.py`, `hyperframes check`.

## 1. Bắt đầu ở đâu

Gọi skill **`/video-pipeline`** cho mọi yêu cầu làm video. Skill đó giữ thứ tự phase, checkpoint và QC. Quy trình chi tiết, checklist từng giai đoạn: `.agents/skills/video-pipeline/references/workflow-v2.md`.

- "làm video <URL>" → Chế độ A. "clone video <URL>" → Chế độ B. "làm video: <ý tưởng>" (không URL) → Chế độ C.
- A/B: QA nguồn → viết lại chống reup (`originality_check.py`). C: xác nhận ý hiểu → thể loại/nhân vật/bối cảnh → đề cương → kịch bản 10–30 phút (`--speed 1.3`).
- Cả ba: demo 30–40 s → người dùng duyệt → mới làm full. Không sang giai đoạn sau khi gate chưa pass; cập nhật `PROJECT.md` sau mỗi gate.

Chuỗi skill:

1. `/baoyu-youtube-transcript` — lấy transcript, metadata, cover.
2. `/script-rewrite` — viết lại kịch bản + `script.json` + packaging.
3. `/voice-sync` + `/vieneu-tts` — đọc từng câu, sinh `manifest.json` + SRT.
4. `/hyperframes` (+ `-cli`, `-registry`, `captions-overlay`, `media-use`) — dựng và render.
5. `/video-pipeline` → `references/packaging.md` — đóng gói xuất bản.
6. `/short-editing` — chỉ khi có bản ghi talking-head cần cắt ghép nhanh; không trộn với HyperFrames.

## 2. Thư viện dùng chung `library/`

Rig, đạo cụ, bối cảnh, palette làm một lần, dùng cho mọi project. Chi tiết: `library/README.md`.

```bash
L=.agents/skills/video-pipeline/scripts/library.py
python $L list                          # tất cả: archetype, outfit, prop, location, palette
python $L list --kind prop --tag altar  # lọc
python $L show candle                   # trạng thái, slot, pivot, scale gợi ý
python $L use --project <slug> candle ancestral_altar house_altar_room   # chép có khoá phiên bản
python $L check                         # phải 0 lỗi trước khi commit library/
python $L sheet                         # render library/sheets/*.png để duyệt bằng mắt
python $L promote --project <slug> --kind prop --id <id> --file assets/props/<id>.svg --states a,b --tags x,y --desc "..."
```

Nhân vật: `build_rig.py` đọc `archetype` + `outfit` trong `bible.json` (xem `library/rigs/archetypes.json`).

## 3. Môi trường đã kiểm

| Thành phần | Trạng thái |
| --- | --- |
| Python | 3.14.5, `vieneu` 3.8.4 đã cài (25 giọng preset, mặc định `Hải Đăng`), model `VieNeu-TTS-v3-Turbo` đã cache (~2 GB) |
| Node / npm | v24.16, `npx hyperframes` 0.9.66 chạy được |
| FFmpeg / ffprobe | 8.1.1 |
| yt-dlp | có (fallback transcript) |
| bun | không cài global; dùng `npx -y bun` (script transcript cần) |
| Playwright + Chromium | cần cho `build_rig.py` / `library.py sheet` (pose sheet, contact sheet) |

## 4. Lệnh thường dùng

```bash
# 1. khung project (ghi tem "Luật áp dụng: RULES.md vN" vào PROJECT.md)
python .agents/skills/video-pipeline/scripts/scaffold_project.py "slug" --title "Tựa" --format 9:16 --mode a|b|c

# 2. transcript
npx -y bun .agents/skills/baoyu-youtube-transcript/scripts/main.ts "<URL>" --languages vi,en --chapters --speakers

# 3. kiểm kịch bản không cần model
python .agents/skills/voice-sync/scripts/build_voiceover.py --script projects/<slug>/script/script.json --out projects/<slug>/audio --dry-run

# 4. đọc thoại + timing (mặc định --speed 1.25; dải 1.2–1.3)
python .agents/skills/voice-sync/scripts/build_voiceover.py --script projects/<slug>/script/script.json --out projects/<slug>/audio

# 5. bible → rig + pose sheet; chốt thư viện cho project
python .agents/skills/video-pipeline/scripts/build_rig.py --bible projects/<slug>/script/bible.json --out projects/<slug>/assets/rig
python .agents/skills/video-pipeline/scripts/library.py use --project <slug> <id>...

# 6. HyperFrames
npx hyperframes init projects/<slug>/video --skip-skills --non-interactive --resolution portrait
python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/<slug> --fix   # thêm dòng trỏ RULES.md vào AGENTS/CLAUDE lồng
cd projects/<slug>/video && npx hyperframes lint && npx hyperframes check --json

# 7. các gate (đều phải sạch)
python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/<slug> [--phase demo|full|final]
python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/<slug>
python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/<slug>

# 8. render
cd projects/<slug>/video && npx hyperframes render --quality delivery -o ../output/final.mp4
```

## 5. Skill tự viết (khác skill cài từ marketplace)

| Skill | Vai trò |
| --- | --- |
| `video-pipeline` | Orchestrator + layout + QC + packaging + các script: scaffold, build_rig, library, check_rules/shots/sync, originality_check |
| `script-rewrite` | Chuẩn kịch bản tiếng Việt, schema `script.json`, luật viết cho TTS |
| `voice-sync` | `build_voiceover.py`: nhiều giọng, cache, manifest, SRT |

Sửa 3 skill này khi quy trình đổi; đừng sửa skill marketplace (cập nhật sẽ ghi đè). Đổi **luật** thì chỉ người dùng quyết định (R0.3).
