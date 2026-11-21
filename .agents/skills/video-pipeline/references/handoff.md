# HANDOFF — trạng thái làm việc (cập nhật mỗi lần commit)

Mục đích: phiên sau (hoặc agent khác) đọc file này + `RULES.md` là làm tiếp được, không cần lịch sử chat.
Nhánh làm việc: `claude/workflow-v2`. Người dùng nói tiếng Việt; trả lời bằng tiếng Việt.

## Yêu cầu gốc của người dùng
Đánh giá và cải tiến workflow làm video 2D của repo: nhân vật đồng bộ, SFX hợp, mỗi câu thoại ngắn có shot diễn, bối cảnh/đạo cụ đồng bộ, diễn xuất tự nhiên.
Cách làm việc: "làm video <URL>" / "clone video <URL>" → QA → viết lại chống reup → demo 30–40 s → duyệt → full; mỗi giai đoạn có checklist. Có thêm Chế độ C (từ ý tưởng → kịch bản 10–30 phút, speed 1.3).
Yêu cầu mới nhất: **rig, đạo cụ, bối cảnh phải dùng lại được cho project sau; bắt agent tuân theo luật chung ở cấp cao nhất** → `RULES.md` + `library/`.
Người dùng muốn: làm đến đâu commit đến đó, kèm handoff (file này).

## Đã xong (đã commit)
- Workflow v2 (`references/workflow-v2.md`): 3 chế độ A/B/C, giai đoạn A–E, checklist, cổng 👤.
- Gate: `originality_check.py`, `check_shots.py`, `check_sync.py`, `check_rules.py`; `scaffold_project.py --mode a|b|c`.
- `RULES.md` (luật R0–R9, có ID), `CLAUDE.md` (import RULES+AGENTS), `AGENTS.md` viết lại.
- `library/`: palette (base, folk-horror-vn), `rigs/archetypes.json` (7 archetype, 4 outfit), 10 đạo cụ, 3 bối cảnh, `index.json`, `sheets/*.png`. Công cụ `library.py` (list/show/use/lock-check/check/reindex/sheet/promote).
- `build_rig.py`: rig SVG từ bible (archetype + outfit + ghi đè), pose sheet, kiểm tràn khung, xuất `<id>.rig.json`.
- Project mẫu `projects/than-trung-chiec-khan-tang-thu-32`: 5 rig nhân vật chính, bible có 3 bối cảnh + 10 đạo cụ (gán `lib`), `assets/LIBRARY.lock.json`. `check_rules.py` = OK (5 cảnh báo generator preview cũ).

## Đã kiểm thật / chưa kiểm
- Đã kiểm: `library.py check` (0 lỗi) + thử phá (hex, token lạ, thiếu part/layer, state lệch → đều bị bắt); `promote` (thành công, từ chối trùng id, từ chối asset xấu); ghép thử một cảnh trong Chromium: bối cảnh + bàn thờ + nến/bát hương vào slot + 2 rig lồng `<svg>` (tay chỉ, tay giơ đúng pivot).
- **Chưa kiểm:** animation thật trong HyperFrames/GSAP (đổi `data-*`, xoay tay bằng GSAP); render video; TTS; `teen`/`child` mới nhìn qua lineup, chưa duyệt pose sheet.
- Thiết kế nhân vật/đạo cụ ngoài nguồn là **đề xuất** của agent, chưa người dùng duyệt (sheet ở `library/sheets/`, `assets/rig/sheets/`).

## Việc tiếp theo (theo thứ tự)
1. `build_video.py`: generator đọc `manifest.json` + `bible.json` + `shotlist.json` → HTML HyperFrames. Dùng quy ước nhúng trong `workflow-v2.md` C1 và `library/README.md` (rig/prop = `<svg>` lồng; anchor `stand`/`slots`; token màu qua `library.py project_palette`). Không gõ hex (R2.5). Thử với 1 cảnh ngắn của project mẫu, chạy `hyperframes lint/check`.
2. Mở rộng library: nhân vật phụ (bố, chú, em gái, bé Na, Vy), bối cảnh (đình làng, bờ sông, phòng khách, nghĩa địa), đạo cụ (gương đồng, quan tài, nhang đèn, quạt, áo tang…), outfit; mỗi cái qua `promote` + `sheet` + commit.
3. SFX: bổ sung kho còn thiếu + recipe (workflow-v2 C4); sửa `sfx/README.md` (link `file:///d:/...`).
4. Chạy thử Chế độ C với một ý tưởng người dùng đưa.
5. Dọn legacy: generator `preview_*` có hàng trăm hex (R2.5, hiện chỉ cảnh báo); project `ma-thoi-den-thanh-co-tinh-tuyet` chưa có bible (check_rules báo lỗi — đúng luật R1.4, cần quyết định bổ sung hay coi là legacy).

## Lưu ý kỹ thuật
- `RULES.md`: agent không tự sửa (R0.3). Nếu cần đổi, đề xuất cho người dùng.
- Stop hook của môi trường hay báo "unpushed commit / no remote branch" sai: kiểm bằng `git ls-remote origin claude/workflow-v2` so với `git rev-parse HEAD` rồi mới tin.
- Môi trường: Playwright + Chromium có sẵn (`build_rig.py`, `library.py sheet`). Render thật dùng `npx hyperframes` (chưa chạy trong phiên này).
- Trailer commit: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` và `Claude-Session: https://claude.ai/code/session_01GcMrUmq793eUS1ikpo24kJ`.
