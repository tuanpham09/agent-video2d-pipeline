# HANDOFF — trạng thái làm việc (cập nhật mỗi commit)

Phiên sau (hoặc agent khác): đọc file này + `RULES.md` + `AGENTS.md` là làm tiếp được, không cần lịch sử chat. File duy nhất — đã gộp `references/handoff.md` cũ và HANDOFF bối cảnh của phiên song song.
Nhánh: `claude/workflow-v2` (PR #1). Người dùng nói tiếng Việt; trả lời bằng tiếng Việt.

## Yêu cầu gốc của người dùng
Đánh giá và cải tiến workflow làm video 2D của repo: nhân vật đồng bộ, SFX hợp, mỗi câu thoại ngắn có shot diễn, bối cảnh/đạo cụ đồng bộ, diễn xuất tự nhiên.
Cách làm việc: "làm video <URL>" / "clone video <URL>" → QA → viết lại chống reup → demo 30–40 s → duyệt → full; mỗi giai đoạn có checklist. Có thêm Chế độ C (từ ý tưởng → kịch bản 10–30 phút, speed 1.3).
Yêu cầu mới nhất: **rig, đạo cụ, bối cảnh phải dùng lại được cho project sau; bắt agent tuân theo luật chung ở cấp cao nhất** → `RULES.md` + `library/`.
Người dùng muốn: làm đến đâu commit đến đó, kèm handoff (file này).

## Lượt 2026-11-22 (plan v3, M1–M3 một phần)
- RULES.md v2: R10 (tay nghề), R11 (tương tác), R12 (giọng). Ngoại lệ ghi ở PROJECT.md của cả hai project. Tem `Luật áp dụng: RULES.md v2` đã cập nhật.
- Generator: `timing_lib.py` (mốc từ, beat `word`), `build_video.py` (move/look/react, người nghe tự quay mắt và gật), `check_shots.py` (E7, E8).
- `voice-sync/scripts/check_audio.py` (gate giọng, đã test với wav giả).
- S01: SH008 và SH012 thêm beat tường minh. Gate S01 OK. hyperframes check ok. Snapshot đã xem: `projects/than-trung-chiec-khan-tang-thu-32/review/`.
- Test: `python .agents/skills/video-pipeline/scripts/tests/test_roadmap_v3.py` → 25/25.
- **Việc của người dùng**: chạy `build_voiceover.py` trên máy có VieNeu (cần `audio/lines/*.wav`, `voiceover.wav`, `manifest.json`), rồi `check_audio.py`. Sau đó báo lại để mình chỉnh beat theo giọng thật.
- **Còn lại theo thứ tự**: rig pose walk/turn (cần pose sheet duyệt); schema; CLI `vp`; khẩu hình theo biên độ; mốc từ ASR (chỉ khi cần); release skill.

## Fix PR #1 — nhánh `claude/fix-pr1-gaps` (2026-11-23, từ `origin/claude/workflow-v2`)
Tuấn duyệt plan cải tiến, fix 4 mục (2, 3, 4, 5). KHÔNG merge, KHÔNG mở PR mới. Demo kiểm chứng: `projects/demo-15s-than-trung/` (không commit, 4 line, 13,97s → 14,42s sau khi đọc lại giọng).
- **Fix 2 — tốc độ riêng từng nhân vật (`build_voiceover.py`):** thứ tự ưu tiên line.speed > characters[].speed (hoặc voice_map) > `--speed` chung; cache key + manifest ghi tốc độ thật từng line/nhân vật; schema script/manifest thêm `speed` (1.0–2.0). Kiểm chứng: voice demo chạy lại 1 pass (71s, trước đây 2 pass + `merge_voice.py`): host Đức Trí 1.3, ông Bảy 1.2; `check_audio` OK; `validate_schemas` OK.
- **Fix 3 — `check_shots.py` E9/E10:** E9 (lỗi) pose/emotion/stance/gaze trong characters[] và beat `set` phải có trong `.rig.json`; beat `move` cần walk-a/walk-b; thiếu file rig → chỉ cảnh báo. E10 (lỗi) chân nhân vật (điểm stand) không được nằm trong khung đạo cụ (cùng quy tắc `Stage.resolve`/`add_prop`, dung sai dọc 10px); `at` không giải được cũng là lỗi. **Bắt được lỗi thật:** SH008 project mẫu có host đứng đè lên mâm tre — đã sửa shotlist mẫu (mâm sang stand:L dx=-260 như bản demo). Test: 2 case phủ định E9/E10 mới; toàn bộ `test_roadmap_v3.py` qua.
- **Fix 4 — render nháp (`render.py` mới):** mặc định `--quality draft` + 15 fps (ra `output/draft-<thời gian>.mp4`); `--delivery` mới render `--quality delivery` (ra `output/final.mp4`). Đo thật demo 15s (VM 1,5 CPU): draft 15fps 70,6s vs delivery 30fps 134,9s — nhanh ~48%. Riêng draft 30fps chỉ nhanh ~15% (nút cổ chai là Chrome chụp frame, không phải encode). Docs: workflow-v2.md (C6 + D) + video-pipeline SKILL.md Bước 5.
- **Fix 5 — `check_sync.py` vs `build_video.py`:** `check_sync` chấp nhận layout 1 track giọng duy nhất (`<audio id="voice">`: src tồn tại, data-start=0, data-duration khớp phần được phủ, file .wav dài đúng) và chỉ kiểm các line được phủ bởi shot trong index (dựng từng phần không đòi root dài bằng toàn bộ manifest); layout clip-riêng vẫn kiểm nghiêm như cũ; tag SFX (`sfx-*`) không còn báo cảnh báo thừa. `build_video`: dựng đủ thì root data-duration lấy từ manifest (R9.4, gồm tail); dựng từng phần giữ thời lượng cửa sổ shot. Kiểm chứng: demo PASS; `video_demo` mẫu rebuild với voice S01 (13 line, build 2m36s) PASS cả với manifest S01 lẫn manifest đầy đủ (đã scope) — **nhưng bản rebuild KHÔNG commit** (diff 14 file, timing các shot lệch do VieNeu đọc lại ngẫu nhiên) nên đã restore `video_demo/` về HEAD; voiceover.wav S01 đã xóa khỏi `audio/` thật (tránh file cũ gây nhầm cho lần dựng full sau), chỉ giữ `audio/lines/*.wav` làm cache (gitignored).
- Test: `test_roadmap_v3.py` TẤT CẢ QUA (thêm `test_check_sync`, 6 case); `library.py check` 35 asset 0 lỗi; `check_rules --phase demo`: mẫu 0 lỗi/5 cảnh báo (màu cứng generator preview cũ), demo 0/0; demo gates: check_shots OK, check_sync OK, hyperframes check ok:true, lint 0 lỗi/5 cảnh báo (tween chồng, cũ).
- **Chưa làm / lưu ý:** demo `output/final.mp4` (13,97s) vẫn từ manifest cũ — render lại mới khớp voice 14,42s. `validate_schemas` trên demo vẫn FAIL bible/shotlist thiếu `meta`/`scope` (file của demo, có từ trước, không thuộc phạm vi fix). Toàn bộ project mẫu (không `--scenes`) vẫn FAIL `check_shots` ~402 lỗi cũ — chỉ S01 là lát cắt được gate. Test cần `soundfile`/`jsonschema`/`numpy` — không có sẵn trên VM, dùng venv riêng `/tmp/test-venv` (tạo lại mỗi phiên vì /tmp bị dọn).

## Plan v3 (đề xuất, chờ duyệt): `references/roadmap-v3.md` — nhân vật tương tác, giọng VieNeu chính xác (mốc từ), `vp` CLI đồng bộ agent, release skill. Phát hiện: shot đã theo độ dài audio nhưng chỉ 1 nhân vật diễn/shot, không có di chuyển.

## Yêu cầu mới (2026-11-22): agent khác phải làm đẹp như mẫu
- Đã viết `.agents/skills/video-pipeline/references/craft-playbook.md` (bắt buộc: nhìn ảnh thật, clone mẫu vàng, chỉ dựng bằng `build_video.py`, lỗi kỹ thuật đã biết, khung báo cáo) và trỏ tới từ `AGENTS.md` (mục "Tay nghề"), `SKILL.md`, `workflow-v2.md`.
- `check_rules.py` kiểm thêm (CRAFT): pose sheet mỗi nhân vật; nhật ký gate nêu snapshot/ảnh đã xem. Đã test âm tính.
- **Chờ người dùng duyệt**: nâng thành luật R10 trong `RULES.md` (v2). Agent không tự sửa RULES.md (R0.3) — nội dung sẵn ở `references/RULES-R10-proposal.md`; duyệt thì dán vào, nâng version, cập nhật tem trong PROJECT.md các project.

## Đã xong (đã commit & push)
- Workflow v2 (`references/workflow-v2.md`): 3 chế độ A/B/C, giai đoạn A–E, checklist, cổng 👤.
- Gate: `originality_check.py`, `check_shots.py`, `check_sync.py`, `check_rules.py`, `library.py check`; `scaffold_project.py --mode a|b|c`.
- `RULES.md` (R0–R9) + `CLAUDE.md` (import RULES+AGENTS) + `AGENTS.md` (mục 0: luật + 9 quy tắc vận hành bắt buộc, gộp từ hai phiên).
- `library/`: palette (`base`, `folk-horror-vn`, `scenery-vn`), `rigs/archetypes.json` (7 archetype, 4 outfit), 10 đạo cụ, **25 bối cảnh** (3 vẽ tay + 22 sinh bằng code nhập qua `import_bg.py`), `index.json`, `sheets/*.png`. Công cụ `library.py` (list/show/use/lock-check/check/reindex/sheet/promote).
- `build_rig.py`: archetype + outfit + `extends` (clone nhân vật), kiểm giải tích tràn khung và khớp `--script`, pose sheet, xuất `<id>.rig.json`. Đã kiểm: 5 rig của project mẫu tái tạo giống hệt bản đã commit; `extends` + `--script` chạy.
- Bối cảnh sinh bằng code: `scripts/bg_lib/` + `build_bg.py` (nguồn) → `import_bg.py` → `library/locations/`. Đã xem `library/sheets/locations.png`: 22 cảnh × 6 trạng thái ánh sáng (`day|dawn|night|dark|red_flash|warm`) render đúng màu.
- Project mẫu `projects/than-trung-chiec-khan-tang-thu-32`: 5 rig nhân vật chính, bible (3 bối cảnh + 10 đạo cụ gán `lib`), `assets/LIBRARY.lock.json`. `check_rules.py` (demo, final) = OK, 5 cảnh báo generator preview cũ.

## Đã kiểm thật / chưa kiểm
- Đã kiểm: `library.py check` 0 lỗi (35 asset) + thử phá (hex, token lạ, thiếu part/layer, state lệch); `promote`; ghép thử một cảnh trong Chromium (bối cảnh + bàn thờ + nến/bát hương + 2 rig lồng `<svg>`); sheet bối cảnh sau khi sửa lỗi "ảnh đen" (sheet từng chỉ nạp palette `base` → token `bg_*` không có giá trị; đã sửa: nạp mọi palette asset dùng).
- **Chưa kiểm:** animation thật trong HyperFrames/GSAP; render video; TTS; `teen`/`child` chưa duyệt pose sheet; `slots` đạo cụ của 22 cảnh còn trống. Anchor (`bg_lib/anchors.py`): phiên song song đã ghép `host` kiểm cả 22 cảnh; mình tự ghép lại `host` ở giữa khung 9:16 cho 5 cảnh (nghia_dia, gian_tho_dem, nha_bep, nui, chua) → chân chạm đất, tỉ lệ hợp lý. Vị trí L/R nằm ngoài khung 9:16 (chỉ dùng cho 16:9), chưa xem.
- Thiết kế nhân vật/đạo cụ ngoài nguồn là **đề xuất** của agent, chưa người dùng duyệt. **`RULES.md` do agent soạn — cần người dùng duyệt/sửa** (agent không tự sửa nữa: R0.3).

## Bối cảnh — quy trình & việc dở của phiên song song
- Sửa/thêm cảnh: `.agents/skills/video-pipeline/scripts/bg_lib/{core.py,batch1-4.py,creep.py,sheet.py}` (`@register(id, tên, kind, tags, focus=...)`) → `python .agents/skills/video-pipeline/scripts/build_bg.py [--only id]` → `python .agents/skills/video-pipeline/scripts/import_bg.py` → `library.py check` → `library.py sheet` → xem ảnh → commit. Không sửa tay `library/locations/<id>.svg` của nhóm này.
- Đợt cảnh: 1 `batch1.py` (nghia_dia, toan_canh_lang, gian_tho_dem, bo_song, gieng_lang, bui_tre_chuoi); 2 `batch2.py` (truong_bo_hoang, nha_hoang, canh_dong_lua, rap_dam_tang, nui, chua); 3 `batch3.py` (nha_ve_sinh, mieu_dinh, song, cay_da, san_nha, nha_bep); 4 `batch4.py` (phong_ngu, phong_khach, nha_co_nha_tho_ho, nha_cap_bon).
- Nâng cấp truyện ma: [x] B1+B2 (`data-mood="creepy"`, ánh sáng chiều sâu, vùng sáng nến/đèn); [x] B3 lớp `.creep` cho 22 cảnh (`bg_lib/creep.py`, `CREEP[id]() -> {far,mid,near}`; duyệt bằng `assets/library/bg/sheets/creepy.png`; cầu sáng `lamp` ngoài trời chỉ ở cảnh khai `lamp=`); [x] B4 sửa cảnh yếu (nha_hoang đổ nát thật, truong_bo_hoang mái thủng/bảng rơi, nha_ve_sinh ván mục + cửa hé, canh_dong_lua chòi canh + cọc cờ, `banana()` có thân + cuống lá); [x] B5a xem khung 9:16 + neo chân: mốc đứng nay ở `bg_lib/anchors.py` (floor_y, s, cx, dx; `import_bg.py` đọc đây; đã ghép nhân vật `host` kiểm cả 22 cảnh, `anchors_reviewed=true`; số cũ suy từ `focus` sai vì focus là điểm nhìn, không phải mặt đất); [ ] B5b thử trong HyperFrames (chưa). **Sau mỗi bước phải chạy lại `import_bg.py` để `library/` cập nhật.** Phiên song song có thể còn đang làm B3–B4 trên nhánh này: `git fetch` + merge trước khi sửa `bg_lib/`.
- Bối cảnh nên thêm khi cần: cầu / đường làng đêm, hành lang bệnh viện / trạm xá, chợ quê, hầm / hang, rừng sâu, ao / đầm sen, cổng làng, nhà tập thể, gác mái, quán nước đầu làng.
- Trùng chức năng: `house_altar_room`≈`gian_tho_dem`, `village_yard_night`≈`san_nha`, `veranda_night`≈`nha_cap_bon`. Chưa hợp nhất (project mẫu dùng bản vẽ tay).

## Việc tiếp theo (theo thứ tự)
1. (xong phần neo chân/9:16) Còn `slots` đạo cụ của 22 cảnh (đang `{}`) và thử animation trong HyperFrames.
2. **Demo S01 (0–34,4 s) đã dựng bằng `build_video.py`** → `projects/than-trung-chiec-khan-tang-thu-32/video_demo/` (file sinh; chạy lại: `python .agents/skills/video-pipeline/scripts/build_video.py --project projects/<slug> --until SH010`). Đã kiểm: `check_shots --scenes S01` OK; `hyperframes lint` 0/0; `hyperframes check --json` `ok: true` (layout/contrast/audio 0 lỗi, craft 1 cảnh báo chưa đọc); snapshot 10 điểm — cảnh, đạo cụ, ánh sáng, camera, biểu cảm/pose đúng. **Chưa làm:** render mp4 (`hyperframes render`); giọng (`audio/voiceover.wav` không commit → dựng KHÔNG có tiếng; cần chạy `build_voiceover.py` ở máy có VieNeu); nghe thử SFX; khẩu hình (chỉ có khi `characters[].mouth: true`, demo dùng người kể nên chưa dùng); khớp thời điểm "ba mươi hai" với từ thật (đang ước theo tỉ lệ, chưa có word-timing); khung 9:16 (generator mới ra 16:9); captions; BGM/ambience (kho `sfx/` chưa có gió/dế/lửa). Cần người dùng 👤 duyệt demo trước khi làm full (R8.1).
   - Bẫy HyperFrames đã gặp: scoper CSS **bỏ cả khối `<style>`** nếu có combinator `>` → mặt đen. Đã sửa `build_rig.py` (`.mouth *`) và `library.py check` giờ báo lỗi nếu asset có `>` trong CSS.
   - Debug nhanh: `npx hyperframes preview --foreground --no-open --port N <dir>` rồi Playwright mở `http://localhost:N/api/projects/<tên thư mục>/preview` để đo computed style trong runtime thật. Đừng `page.evaluate` trả về object GSAP (serialize treo).
   - Chưa có: shotlist cho scene S02–S20 (chỉ S01 có).
3. Mở rộng library: nhân vật phụ (bố, chú, em gái, bé Na, Vy), đạo cụ (gương đồng, quan tài, nhang đèn, quạt, áo tang…), outfit; mỗi cái qua `promote` + `sheet` + commit.
4. SFX: bổ sung kho còn thiếu + recipe (workflow-v2 C4); sửa `sfx/README.md` (link `file:///d:/...`).
5. Chạy thử Chế độ C với một ý tưởng người dùng đưa.
6. Dọn legacy: generator `preview_*` có hàng trăm hex (chỉ cảnh báo); project `ma-thoi-den-thanh-co-tinh-tuyet` chưa có bible (R1.4, cần quyết định); PR #1: đã có CI (`.github/workflows/gates.yml`); review thread đã sửa thì resolve, còn mở 2 thread cần người dùng quyết (dung sai SFX ±0,15 s vs 'mili-giây'; pivot `0% 0%` vs pivot viewBox của R3.4).

## Lưu ý kỹ thuật
- `RULES.md`: agent không tự sửa (R0.3). Nếu cần đổi, đề xuất cho người dùng.
- Stop hook của môi trường hay báo "unpushed commit / no remote branch" sai: kiểm bằng `git ls-remote origin claude/workflow-v2` so với `git rev-parse HEAD` rồi mới tin.
- Môi trường: Playwright + Chromium có sẵn (`build_rig.py`, `library.py sheet`). Render thật dùng `npx hyperframes` (chưa chạy trong phiên này).
- Trailer commit: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>` và `Claude-Session: https://claude.ai/code/session_01GcMrUmq793eUS1ikpo24kJ`.
