# Video Studio — hướng dẫn cho agent

Workspace này sản xuất video YouTube / TikTok từ nguồn có sẵn hoặc từ ý tưởng: kịch bản tiếng Việt → giọng đọc VieNeu-TTS → HyperFrames → MP4.

## 0. ĐỌC TRƯỚC KHI LÀM BẤT CỨ VIỆC GÌ

**[`RULES.md`](RULES.md) là luật chung của repo, cao nhất.** Mọi agent (Claude, Codex, Cursor, agent con…), skill, subagent đều phải đọc và tuân theo. Skill, workflow, `PROJECT.md`, file hướng dẫn lồng trong project, memory mà mâu thuẫn với `RULES.md` thì `RULES.md` thắng. Chỉ chỉ thị rõ ràng của người dùng trong phiên hiện tại mới được đè luật, và phải ghi vào mục *Ngoại lệ* của `PROJECT.md` (R0.2). Agent không tự sửa `RULES.md` (R0.3).

### ⛔ Quy tắc vận hành bắt buộc (tóm tắt; chi tiết và ID ở `RULES.md`)

1. **Bắt đầu bằng `/video-pipeline`** và đọc `.agents/skills/video-pipeline/references/workflow-v2.md`. Không tự nghĩ ra quy trình riêng (R8.1).
2. **Đúng thứ tự giai đoạn**: A/B (QA nguồn → viết lại) hoặc C (ý tưởng → bible → đề cương → kịch bản) → **demo 30–40 s** → 👤 người dùng duyệt → mới làm full (R8.1).
3. **Gate phải pass bằng lệnh máy, không tự tuyên bố** (R8.2): `originality_check.py` (A/B), `check_rules.py`, `check_shots.py`, `check_sync.py`, `hyperframes lint/check`. Gate fail → sửa nguồn (script/bible/shotlist/rig) rồi chạy lại; không sửa tay file sinh tự động (R1.3), không hạ ngưỡng, không bỏ qua cảnh báo lỗi.
4. **Cập nhật `projects/<slug>/PROJECT.md` sau mỗi gate** (ngày, lệnh, kết quả). Chưa ghi = chưa xong.
5. **Một video = `projects/<slug>/`**; scaffold bằng `scaffold_project.py`. Không ghi file lạc ra root, không tạo generator/pipeline song song cho từng video (R1.1, R1.6).
6. **Chốt kịch bản trước TTS, chốt preview trước render final** (R1.5).
7. **Thiếu thông tin hoặc gate không qua được → dừng và hỏi**, nêu rõ kẹt ở bước nào (R0.4). Không bịa số liệu/quote/tên, không dùng nội dung có bản quyền khi chưa có `source/permission.md` (R7.1).
8. **Sửa quy trình thì sửa trong `workflow-v2.md` / skill tự viết** (`video-pipeline`, `script-rewrite`, `voice-sync`) và ghi trong PR; không âm thầm làm khác.
9. **Tái sử dụng trước, tạo mới sau (R2):**
   - **Tra `library/` trước** (`library.py list`); dùng lại bằng `library.py use`. Nhân vật đã khoá ở demo không đổi id/rig/giọng.
   - **Nhân vật thiếu → clone gần nhất**: chọn `archetype` + `outfit` trong `library/rigs/archetypes.json` (R2.8), hoặc `"extends": "<id gốc>"` + `rig_params` chỉ chứa phần đổi (nếu gốc ở project khác, copy mục đó vào bible mới trước). Không vẽ rig từ đầu khi chưa thử clone. Chạy `build_rig.py` rồi đưa pose sheet cho người dùng duyệt (R3.7).
   - **Đạo cụ thiếu →** dùng đạo cụ sẵn có (đổi `states`) nếu gần đúng; chỉ khi không có mới tạo mới, khai vào `bible.json` (`props` + `states`), làm đúng chuẩn library (R2.5–R2.6) và `promote` trước giai đoạn E (R2.4). Không đặt đạo cụ "tại chỗ" trong HTML của một shot.
   - **Bối cảnh:** tra `library/locations/` trước — gồm 3 cảnh vẽ tay + **22 cảnh sinh bằng code** (nghĩa địa, làng, gian thờ, bờ sông, giếng, tre chuối, nhà hoang, đồng lúa, rạp tang, núi, chùa, WC, miếu/đình, sông, cây đa, sân, bếp, phòng ngủ/khách, nhà thờ họ, cấp bốn…). Cảnh sinh bằng code thì **sửa ở nguồn** `.agents/skills/video-pipeline/scripts/bg_lib/` → `build_bg.py` → `import_bg.py` → `library.py check`/`sheet` (không sửa tay `library/locations/<id>.svg`). Thiếu bối cảnh mới thêm hàm vào `bg_lib/` (clone cảnh gần nhất). Không vẽ bối cảnh riêng trong HTML của video. Chi tiết: `HANDOFF.md`.
   - Mỗi nhân vật/đạo cụ/bối cảnh tạo mới phải ghi lý do ("không có sẵn cái nào dùng được") vào `PROJECT.md`.

Vi phạm một mục ở trên = kết quả không hợp lệ, phải làm lại từ giai đoạn bị bỏ qua.

**[`RULES.md`](RULES.md) là luật chung của repo, cao nhất.** Mọi agent, skill, subagent đều phải đọc và tuân theo. Skill, workflow, `PROJECT.md`, file hướng dẫn lồng trong project, memory mà mâu thuẫn với `RULES.md` thì `RULES.md` thắng. Chỉ chỉ thị rõ ràng của người dùng trong phiên hiện tại mới được đè luật, và phải ghi vào mục *Ngoại lệ* của `PROJECT.md` (R0.2). Agent không tự sửa `RULES.md` (R0.3).

Ba điều hay bị quên nhất:

1. **Tra `library/` trước khi tạo** nhân vật, đạo cụ, bối cảnh (R2.1). Dùng lại bằng `library.py use`; làm mới thì đạt chuẩn library rồi `promote` (R2.4).
2. **Màu chỉ là token** (R2.5); **sửa asset dùng chung tại `library/`**, không sửa bản trong project (R2.3).
3. **Gate phải sạch mới được nói "xong"** (R8.2): `check_rules.py`, `check_shots.py`, `check_sync.py`, `hyperframes check`.

### ⛔ Tay nghề (craft) — BẮT BUỘC cho mọi agent (Codex, Cursor, Claude…) khi tạo nhân vật, đạo cụ, bối cảnh, dựng video

Chỉ thị của người dùng (phiên 2026-11-22): các agent khác làm video/nhân vật/đạo cụ chưa đẹp bằng mẫu; **phải** làm theo hướng dẫn chi tiết. Đọc và làm theo [`.agents/skills/video-pipeline/references/craft-playbook.md`](.agents/skills/video-pipeline/references/craft-playbook.md) **trước** khi vẽ/sửa/dựng bất cứ thứ gì. Tóm tắt (chi tiết ở playbook):

1. **Nhìn ảnh thật rồi mới báo xong.** Render PNG → *mở ảnh xem* ở cỡ dùng thật → sửa → xem lại. Check xanh ≠ đẹp (đã từng: check 0 lỗi nhưng sheet đen, mặt đen). Không xem được ảnh → dừng, báo người dùng.
2. **Clone mẫu vàng, không vẽ từ trắng**: nhân vật = archetype+outfit/`extends`; đạo cụ/bối cảnh = copy asset library gần nhất (`candle.svg`, `house_altar_room.svg`…) rồi sửa, đạt chuẩn library ngay.
3. **Chỉ dựng bằng `build_video.py` + `shotlist.json`**; mỗi beat nhìn thấy được có `set`, beat vật lý có SFX; không viết tay HTML/GSAP từng shot.
4. **Kỹ thuật HyperFrames**: CSS không dùng `>`; glow = `radialGradient`; rig chỉ nhúng `<svg>` lồng.
5. **Báo cáo theo khung playbook §8**, bắt buộc có dòng "Ảnh đã XEM: <đường dẫn> — thấy gì, lỗi đã sửa" và "Chưa kiểm". Thiếu = báo cáo không hợp lệ.

Máy kiểm một phần (`check_rules.py`: pose sheet từng nhân vật, nhật ký gate có ảnh đã xem); phần còn lại do bạn tự giữ kỷ luật. Đề xuất đưa thành luật R10 trong `RULES.md` đang chờ người dùng duyệt: [`references/RULES-R10-proposal.md`](.agents/skills/video-pipeline/references/RULES-R10-proposal.md) (agent không tự sửa `RULES.md`, R0.3).

## 1. Bắt đầu ở đâu

Gọi skill **`/video-pipeline`** cho mọi yêu cầu làm video. Skill đó giữ thứ tự phase, checkpoint và QC. Quy trình chi tiết, checklist từng giai đoạn: `.agents/skills/video-pipeline/references/workflow-v2.md`.

- "làm video <URL>" → Chế độ A. "clone video <URL>" → Chế độ B. "làm video: <ý tưởng>" (không URL) → Chế độ C.
- A/B: QA nguồn → viết lại chống reup (`originality_check.py`). C: xác nhận ý hiểu → thể loại/nhân vật/bối cảnh → đề cương → kịch bản 10–30 phút (`--speed 1.3`).
- Cả ba: demo 30–40 s → người dùng duyệt → mới làm full. Không sang giai đoạn sau khi gate chưa pass; cập nhật `PROJECT.md` sau mỗi gate.

Viết/viết lại kịch bản: mỗi cảnh phải có `setting` (trong/ngoài, địa điểm, giờ), `cast`, `staging` (đi từ đâu tới đâu, ai cầm gì) theo [`.agents/skills/video-pipeline/references/script-continuity-guide.md`](.agents/skills/video-pipeline/references/script-continuity-guide.md); gate `check_script_logic.py --strict` trước TTS. Luật R13 (RULES.md v3) bắt buộc điều này.

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
python $L list --kind cast               # nhân vật ĐÃ DỰNG + ĐÃ DUYỆT (kèm pose sheet, giọng gợi ý): dán rig vào bible
python $L suggest --project <slug>       # gợi ý asset có sẵn hợp kịch bản + đồ còn thiếu (hoặc --text "…")
python $L show candle                   # trạng thái, slot, pivot, scale gợi ý
python $L use --project <slug> candle ancestral_altar house_altar_room   # chép có khoá phiên bản
python $L cast-add --project <slug> --char <id> --id <cast_id> --role "…" --tags a,b --keywords x,y   # đưa nhân vật đã duyệt vào kho
python $L cast-build                     # dựng lại rig + pose sheet nhóm nhân vật chung (library/rigs/cast_src) → xem ảnh → cast-add --src library --all --force
python $L cast-verify                    # sau khi đổi build_rig/archetype/token: so rig dựng lại với mẫu vàng; ĐỔI → xem ảnh so sánh, cố ý thì --update
python $L check                         # phải 0 lỗi trước khi commit library/
python $L sheet                         # render library/sheets/*.png để duyệt bằng mắt
python $L promote --project <slug> --kind prop --id <id> --file assets/props/<id>.svg --states a,b --tags x,y --desc "..."
```

Nhân vật: `build_rig.py` đọc `archetype` + `outfit` trong `bible.json` (xem `library/rigs/archetypes.json`).

## 3. Môi trường đã kiểm

| Thành phần | Trạng thái |
| --- | --- |
| Python | 3.14.5, `vieneu` 3.8.4 đã cài (25 giọng preset, mặc định `Hải Đăng`), model `VieNeu-TTS-v3-Turbo` đã cache (~2 GB) |
| Node / npm | v24.16, `hyperframes` **0.9.82 đã ghim** trong render.py/gates.py (Opt round 3 mục 0 — npx từng trôi nổi, tự cài 0.9.82 trong lúc package.json ghim 0.9.81) |
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
python .agents/skills/video-pipeline/scripts/check_script_logic.py --project projects/<slug> [--strict]   # logic kịch bản: setting/cast/staging, đi từ đâu tới đâu (trước TTS; --strict khi chốt kịch bản)
python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/<slug>
python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/<slug>
python .agents/skills/video-pipeline/scripts/check_motion.py --project projects/<slug>    # sau build_video.py (đọc video_demo/motion_plan.json)

# xem nhanh một shot (hoặc biến thể shotlist --shotlist f.json): dựng + chụp mốc beat + contact sheet → MỞ ẢNH XEM
python .agents/skills/video-pipeline/scripts/preview_shot.py --project projects/<slug> --shot SH0xx

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
