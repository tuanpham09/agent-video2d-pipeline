# Rồng Rắn Lên Mây Video Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Tạo bản chuyển thể truyện ma tiếng Việt dài 20–30 phút ở format 16:9 từ nguồn YouTube đã QA, bắt đầu bằng demo 30–40 giây đạt toàn bộ gate và được người dùng duyệt.

**Architecture:** Một project độc lập `projects/rong-ran-len-may-nguoi-dung-dau/` chứa source, script, bible, audio, assets, video và output. Script là nguồn sự thật cho lời thoại; bible là nguồn sự thật cho nhân vật/bối cảnh/đạo cụ; shotlist là nguồn sự thật cho beat/SFX; `build_video.py` là generator duy nhất đọc các nguồn đó để sinh HyperFrames.

**Tech Stack:** Python 3.14, VieNeu-TTS v3 Turbo, `build_voiceover.py`, SVG rig/library, HyperFrames 0.9.x, FFmpeg/ffprobe, các gate `originality_check.py`, `check_rules.py`, `check_shots.py`, `check_motion.py`, `check_sync.py`.

## Global Constraints

- Project slug: `rong-ran-len-may-nguoi-dung-dau`.
- Format: 16:9, 1920×1080; tốc độ truyện ma `--speed 1.3`.
- Bản full dài 20–30 phút; demo trước dài 30–40 giây.
- Chuyển thể phải đổi tên, quan hệ, địa danh, vật neo, câu chữ, thứ tự tiết lộ và cách kết; không giữ nguyên chuỗi cảnh/câu thoại nguồn.
- Chỉ dùng asset đã có trong `library/`; asset mới phải có lý do trong `PROJECT.md` và qua quy trình library.
- Không sửa tay file sinh tự động (`audio/`, HTML HyperFrames, motion plan); sửa nguồn rồi chạy lại generator.
- Mỗi beat vật lý có SFX; mỗi shot có set/location/ánh sáng/props/characters theo bible và anchor library.
- Không làm full trước khi demo được người dùng duyệt.
- Không commit hoặc push khi người dùng chưa yêu cầu.

---

### Task 1: Scaffold project và đóng gói QA nguồn

**Files:**
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/` bằng `scaffold_project.py`.
- Copy: `D:/temp/youtube-transcript-3FleNiLDpig/d-hnh-d-tp/rng-rn-ln-my-ngi-ng-u-hng-khng-phi-tr-con/*` vào `projects/rong-ran-len-may-nguoi-dung-dau/source/`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/source/qa.md`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/source/permission.md`.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/PROJECT.md`.

**Interfaces:**
- Consumes: metadata/transcript/cover đã lấy từ video `3FleNiLDpig`.
- Produces: project có tem RULES v2, source đầy đủ và QA record để các task rewrite dùng làm nguồn duy nhất.

- [ ] **Step 1: Scaffold project**

Run:

```powershell
python .agents/skills/video-pipeline/scripts/scaffold_project.py rong-ran-len-may-nguoi-dung-dau --title "Đứa Đứng Đầu Sau Lúc Tắt Nắng" --format 16:9 --mode a --speed 1.3
```

Expected: project mới có `source/`, `script/`, `audio/`, `assets/`, `video/`, `output/` và `PROJECT.md`.

- [ ] **Step 2: Copy immutable source files**

Run:

```powershell
$src = 'D:\temp\youtube-transcript-3FleNiLDpig\d-hnh-d-tp\rng-rn-ln-my-ngi-ng-u-hng-khng-phi-tr-con'
$dst = 'projects\rong-ran-len-may-nguoi-dung-dau\source'
Copy-Item "$src\meta.json","$src\transcript-raw.json","$src\transcript-sentences.json","$src\transcript.md","$src\transcript.srt" $dst -Force
New-Item -ItemType Directory -Force "$dst\imgs" | Out-Null
Copy-Item "$src\imgs\cover.jpg" "$dst\imgs\cover.jpg" -Force
```

Expected: source có 765 transcript snippets, metadata video và cover; không chỉnh sửa transcript raw.

- [ ] **Step 3: Write source QA and permission boundary**

`source/qa.md` phải ghi: URL, title/channel, duration 2110 giây, transcript `vi` auto-generated, không có caption thủ công, các lỗi ASR đáng chú ý, claim map sơ bộ và quyết định dùng nguồn làm chất liệu chuyển thể chứ không sao chép.

`source/permission.md` phải ghi trạng thái nguồn do người dùng cung cấp, phạm vi hiện tại là bản chuyển thể/demo nội bộ, và yêu cầu xác nhận quyền trước khi xuất bản.

- [ ] **Step 4: Run source consistency check**

Run:

```powershell
python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/rong-ran-len-may-nguoi-dung-dau --phase demo
```

Expected: không có lỗi cấu trúc source/project; nếu có lỗi thì sửa `PROJECT.md` hoặc source metadata trước khi sang Task 2.

### Task 2: Viết lại kịch bản dài và originality gate

**Files:**
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/brief.md`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/rewrite_plan.md`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/diff_matrix.md`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/script.md`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/script.json`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/packaging.md`.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/PROJECT.md`.

**Interfaces:**
- Consumes: `source/transcript.md`, `source/transcript-raw.json`, `source/qa.md`.
- Produces: script JSON hợp lệ, từng line có đúng một speaker, visual 5 trường, và packaging dùng được cho bible/shotlist/audio.

- [ ] **Step 1: Build claim map and rewrite plan**

Read the entire `source/transcript.md` and record 5–9 source claims with `[HH:MM:SS]` timestamps in `brief.md`. Mark ASR-uncertain names/quotes as unusable unless independently supported by the source transcript context. Set the audience to Vietnamese listeners who enjoy rural folk horror and the promise to: “Sau video này, người xem hiểu vì sao một luật chơi trẻ con có thể trở thành lời hẹn kéo dài qua ba thế hệ.”

- [ ] **Step 2: Write the transformed story**

Use the approved six-part arc from the design spec. Replace the source’s names, family relations, location, locked object, and reveal order. Target 20–30 minutes at `--speed 1.3`; keep spoken lines short (maximum 25 words), one speaker per line, and add visual/SFX descriptions for every scene.

- [ ] **Step 3: Cast script voices**

Use `Đức Trí` at speed 1.3 for the horror narrator, `Xuân Vĩnh` for the adult male character, `Mai Anh` or the available child preset for the daughter, and `Adam` only for the supernatural/elder voice if a distinct voice is needed. Keep total voices at four or fewer.

- [ ] **Step 4: Validate script and run originality gate**

Run:

```powershell
python .agents/skills/voice-sync/scripts/build_voiceover.py --script projects/rong-ran-len-may-nguoi-dung-dau/script/script.json --out projects/rong-ran-len-may-nguoi-dung-dau/audio --dry-run
python .agents/skills/video-pipeline/scripts/originality_check.py --script projects/rong-ran-len-may-nguoi-dung-dau/script/script.json --source projects/rong-ran-len-may-nguoi-dung-dau/source/transcript.md --json
```

Expected: script schema/voice plan valid and originality gate passes its configured thresholds. If it fails, revise `script.md`, `script.json`, and `diff_matrix.md`, then rerun; never lower thresholds.

### Task 3: Bible, library lock, rigs and visual review

**Files:**
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/bible.json`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/assets/LIBRARY.lock.json` via `library.py use`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/assets/rig/` via `build_rig.py`.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/PROJECT.md`.

**Interfaces:**
- Consumes: script cast and approved library IDs.
- Produces: bible ids `nguoi_cha`, `be_lan`, `ba_huong`, `dau_hang` using `adult_m`, `child`, `elder_f`, `spirit_shadow`; locked locations/props; pose sheets ready for visual review.

- [ ] **Step 1: Query and lock existing assets**

Run:

```powershell
python .agents/skills/video-pipeline/scripts/library.py list --kind location
python .agents/skills/video-pipeline/scripts/library.py list --kind prop
python .agents/skills/video-pipeline/scripts/library.py use --project rong-ran-len-may-nguoi-dung-dau adult_m child elder_f spirit_shadow nau_song plain_light ao_the_indigo toan_canh_lang village_yard_night bo_song bui_tre_chuoi san_nha gian_tho_dem phong_ngu nha_co_nha_tho_ho nha_hoang clay_jar oil_lamp candle ancestral_altar bamboo_tray mourning_cloth smartphone
```

Expected: `assets/LIBRARY.lock.json` records versions; no asset is copied by hand.

- [ ] **Step 2: Write bible and build rigs**

Create `bible.json` with one id per character/voice, `emotion_vocab`, selected `lib` references, location and prop states. Then run:

```powershell
python .agents/skills/video-pipeline/scripts/build_rig.py --bible projects/rong-ran-len-may-nguoi-dung-dau/script/bible.json --script projects/rong-ran-len-may-nguoi-dung-dau/script/script.json --out projects/rong-ran-len-may-nguoi-dung-dau/assets/rig
```

Expected: `checked: true`, `script_matched: true`, zero overflow combinations, SVG/JSON/pose sheets for all characters.

- [ ] **Step 3: Open pose sheets and correct source**

Open `assets/rig/sheets/nguoi_cha.png`, `assets/rig/sheets/be_lan.png`, `assets/rig/sheets/ba_huong.png`, `assets/rig/sheets/dau_hang.png`, and `assets/rig/sheets/lineup.png` at the intended character size. Check silhouette, face readability, feet on baseline, no black CSS, no limb penetration, and distinct characters. If any issue appears, fix bible/library/generator source, rebuild, and inspect again. Record the image paths and observations in `PROJECT.md` before proceeding.

### Task 4: Demo script, voice and shotlist

**Files:**
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/script/shotlist.demo.json`.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/audio/` via `build_voiceover.py`.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/script/script.json` only through source rewrite if timing/text changes.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/PROJECT.md`.

**Interfaces:**
- Consumes: approved demo lines, bible, locked library assets.
- Produces: real VieNeu manifest/SRT/WAV and 8–10 shot demo with visible beats, SFX and 30–40 second duration.

- [ ] **Step 1: Select demo lines from the rewritten script**

Use the opening hook and present-day cut from the approved arc; end before the next gate knock. The selected demo must contain the narrator and child lines needed for the hook, not source transcript lines.

- [ ] **Step 2: Generate voice and timing**

Run:

```powershell
python .agents/skills/voice-sync/scripts/build_voiceover.py --script projects/rong-ran-len-may-nguoi-dung-dau/script/script.json --out projects/rong-ran-len-may-nguoi-dung-dau/audio --speed 1.3 --json
python .agents/skills/voice-sync/scripts/check_audio.py --project projects/rong-ran-len-may-nguoi-dung-dau
```

Expected: real `engine: vieneu-v3-turbo` manifest, no clipped/overlapping line, speed in the 1.2–1.3 range. If full script audio is too long for the demo, create the project’s supported demo script/input before generating; do not hand-edit manifest timings.

- [ ] **Step 3: Write demo shotlist**

Use only locked locations/props/characters. Each shot must declare `location`, `light`, `characters`, `props`, `beats`, `camera`, `size`, and SFX. Physical beats (cloth, gate, knock, prop movement) must have a cue within ±0.15 seconds. Use `set` for every visible emotion/pose/gaze/light/prop change.

- [ ] **Step 4: Run pre-build gates**

Run:

```powershell
python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/rong-ran-len-may-nguoi-dung-dau --shotlist projects/rong-ran-len-may-nguoi-dung-dau/script/shotlist.demo.json --phase demo
python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/rong-ran-len-may-nguoi-dung-dau
```

Expected: `check_shots` has 0 errors and `check_sync` reports every generated audio clip matched to the manifest.

### Task 5: Generate and inspect the 30–40 second HyperFrames demo

**Files:**
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/video/demo/` via `build_video.py` and HyperFrames.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/video/demo/motion_plan.json` via generator.
- Create: `projects/rong-ran-len-may-nguoi-dung-dau/review/` snapshots/contact sheet.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/PROJECT.md`.

**Interfaces:**
- Consumes: manifest, bible, demo shotlist, locked assets.
- Produces: generator-owned HTML, motion plan, HyperFrames check report and opened PNG snapshots for user review.

- [ ] **Step 1: Generate demo HTML**

Run:

```powershell
python .agents/skills/video-pipeline/scripts/build_video.py --project projects/rong-ran-len-may-nguoi-dung-dau --out projects/rong-ran-len-may-nguoi-dung-dau/video/demo --shots SH001,SH002,SH003,SH004,SH005,SH006,SH007,SH008,SH009,SH010
```

Expected: generated `index.html`, one composition per shot, and motion plan; no hand-written shot HTML.

- [ ] **Step 2: Run all demo gates**

Run:

```powershell
python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/rong-ran-len-may-nguoi-dung-dau --phase demo
python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/rong-ran-len-may-nguoi-dung-dau --shotlist projects/rong-ran-len-may-nguoi-dung-dau/script/shotlist.demo.json --phase demo
python .agents/skills/video-pipeline/scripts/check_motion.py --project projects/rong-ran-len-may-nguoi-dung-dau --plan projects/rong-ran-len-may-nguoi-dung-dau/video/demo/motion_plan.json --shotlist projects/rong-ran-len-may-nguoi-dung-dau/script/shotlist.demo.json
python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/rong-ran-len-may-nguoi-dung-dau --index projects/rong-ran-len-may-nguoi-dung-dau/video/demo/index.html
Push-Location projects/rong-ran-len-may-nguoi-dung-dau/video/demo
npx hyperframes lint
npx hyperframes check --json
Pop-Location
```

Expected: zero errors, `check_sync` OK, `check_motion` OK, and HyperFrames JSON has `ok: true`. Warnings must be documented and not suppressed.

- [ ] **Step 3: Render and open snapshots**

Set `$env:TEMP = 'D:\temp'; $env:TMP = 'D:\temp'` before rendering. Use HyperFrames snapshot/preview at least once per shot, open the PNGs, and inspect feet, face, camera focus, light, prop state, SFX-visible action, and continuity. Fix the source and regenerate if any visual issue appears. Write the exact image paths and observations into `PROJECT.md`.

- [ ] **Step 4: Hand off demo for user approval**

Report the demo path, actual duration, gate outputs, opened image paths, visible issues fixed, and items not checked. Stop here until the user approves the demo.

### Task 6: Expand to the 20–30 minute full video after demo approval

**Files:**
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/script/script.json`, `script/shotlist.json`, `script/script.md`.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/audio/`, `video/`, `output/` only through their generators.
- Modify: `projects/rong-ran-len-may-nguoi-dung-dau/PROJECT.md`.

**Interfaces:**
- Consumes: user-approved demo’s locked cast, rig, visual language, timing, SFX and gate evidence.
- Produces: full scene-by-scene video, final gates, delivery render and publish metadata; no silent changes to the approved demo.

- [ ] **Step 1: Extend the script and shotlist scene by scene**

Add the remaining five-part arc while preserving demo ids, character ids, rig ids and voice assignments. Run `check_shots.py --scenes S01` for the first scene, then repeat with each subsequent scene id actually present in `script/shotlist.json`; run the whole-project check before moving to the next scene.

- [ ] **Step 2: Generate full voice and run audio gates**

Run the full `build_voiceover.py` at speed 1.3, then `check_audio.py` and `check_sync.py`. Fix only `script.json`/voice map and regenerate if timing or pronunciation is wrong.

- [ ] **Step 3: Generate full video and run final gates**

Run `build_video.py` for all scenes, `check_rules.py --phase final`, `check_shots.py --phase final`, `check_motion.py`, `check_sync.py`, `hyperframes lint`, and `hyperframes check --json`. Open snapshots at every scene boundary and high point.

- [ ] **Step 4: Render delivery and record evidence**

After all gates pass and the user has approved the preview, render with HyperFrames delivery quality, verify duration and codecs with `ffprobe`, and write the final artifact path and actual measurements to `PROJECT.md`. Do not commit or push without a separate user request.
