# Video Handoff Roadmap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hoàn thiện các hạng mục còn dở trong `HANDOFF.md` bằng một vertical slice HyperFrames có kiểm chứng trước, sau đó tổng quát hóa thành generator dùng chung, mở rộng library/SFX và đóng các gate của PR #1.

**Architecture:** Dùng `audio/manifest.json`, `script/bible.json`, `script/shotlist.json` và `library/index.json` làm bốn nguồn dữ liệu đầu vào. `build_video.py` là generator duy nhất, sinh HTML HyperFrames với SVG lồng nhau, anchor/slot từ library và timeline GSAP seek-safe; các preview cũ chỉ là dữ liệu đối chiếu trong giai đoạn chuyển tiếp. Triển khai theo vertical slice 30–40 giây trước, rồi mới migrate đủ 20 scene.

**Tech Stack:** Python 3.14 local / Python 3.12 CI, Node 24.16, `hyperframes@0.9.66` theo môi trường repo, GSAP, VieNeu-TTS audio artifacts, Playwright/Chromium, pytest.

## Global Constraints

- Đọc và tuân thủ `RULES.md`, `AGENTS.md`, `.agents/skills/video-pipeline/references/workflow-v2.md` trước mỗi task.
- Không sửa `RULES.md` trong roadmap này; chuẩn SFX giữ `±0,15 s` theo R6.1/C4.
- Pivot rig giữ chuẩn R3.4: tọa độ pivot theo viewBox, `transform-box: view-box`; không quay lại quy ước `0% 0%`.
- `audio/manifest.json` là nguồn duy nhất cho `data-start`/`data-duration`; không sửa tay audio sinh tự động.
- Không sửa tay SVG bối cảnh sinh bằng code; sửa `bg_lib` → `build_bg.py` → `import_bg.py` → `library.py check/sheet`.
- Một generator đọc dữ liệu; không tạo HTML/SVG thủ công riêng cho từng shot.
- Sau mỗi gate phải cập nhật `projects/<slug>/PROJECT.md` và `HANDOFF.md`; chưa ghi thì chưa coi là hoàn thành.
- Demo phải được người dùng duyệt trước khi mở rộng full; snapshot/preview là bằng chứng bắt buộc, không thay bằng mock hoặc spec.
- Trước mọi preview/render HyperFrames trên Windows, đặt `$env:TEMP = 'D:\temp'; $env:TMP = 'D:\temp'` theo R9.2; không dùng thư mục tạm mặc định trên ổ C:.
- Giữ nguyên thay đổi chưa commit hiện có trong `.gitignore`; không đưa chúng vào các commit của roadmap nếu chưa được người dùng yêu cầu.
- `projects/ma-thoi-den-thanh-co-tinh-tuyet` chưa có bible nên chỉ ghi nhận là deferred; không tự tạo bible hoặc bịa dữ liệu.

## Current State and File Boundaries

- `projects/than-trung-chiec-khan-tang-thu-32` là fixture chính: có bible, 20 scene, audio manifest và video HyperFrames legacy; chưa có `script/shotlist.json` chuẩn.
- `projects/.../video/shots.json` và `sfx_cues.json` chứa shot/SFX legacy; `preview_1min/*` và `preview_2d/*` không còn được xem là generator chính sau khi migration pass.
- `bg_lib/anchors.py` là nguồn anchor cho 22 bối cảnh sinh bằng code; `import_bg.py` hiện tạo `slots: {}` và thay toàn bộ entry cũ khi re-import, nên task anchor phải xử lý preserve metadata trước khi dùng lại.
- `library/index.json` dùng một danh sách `items`; location có `stand`, `floor_y`, `crop_9x16`, `slots`, còn prop có `slots` nội bộ như `ancestral_altar`.
- `.github/workflows/gates.yml` hiện có Python/library/background/rig/check_rules gates nhưng chưa chạy đầy đủ shotlist, sync và HyperFrames runtime.

### Task 0: Lock contracts and establish baseline

**Files:**
- Read-only: `RULES.md`, `AGENTS.md`, `HANDOFF.md`, `references/workflow-v2.md`, PR #1.
- Update after evidence: `HANDOFF.md`, relevant `projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md`.

**Interfaces:**
- Consumes: the two user decisions recorded in this plan: SFX tolerance `0.15` seconds and viewBox pivot.
- Produces: a baseline record containing HEAD/remote parity, dirty-file boundary, current gate results and the exact PR review disposition.

- [ ] **Step 1: Capture repository baseline**

  Run:

  ```powershell
  git status --short --branch
  git rev-parse HEAD
  git ls-remote origin refs/heads/claude/workflow-v2
  git diff --check
  ```

  Expected: HEAD equals `origin/claude/workflow-v2`; the pre-existing `.gitignore` modification is listed and remains outside roadmap commits.

- [ ] **Step 2: Run the existing static gates before changing behavior**

  ```powershell
  python .agents/skills/video-pipeline/scripts/library.py check
  python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/than-trung-chiec-khan-tang-thu-32 --phase demo
  python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/than-trung-chiec-khan-tang-thu-32 --phase final
  ```

  Record exact output, warnings and exit codes in `PROJECT.md`; do not call the project complete because the HyperFrames/shotlist gates are not yet present.

- [ ] **Step 3: Resolve the PR policy comments with evidence**

  Verify the current code against the two P1 comments. Keep `SFX_TOLERANCE = 0.15` and viewBox pivots unchanged if the implementation matches the selected contract. Reply on PR #1 with the contract references and defer/close the comments only after the current code and tests prove that behavior. If GitHub authentication is unavailable, record the exact user action in `HANDOFF.md` instead of changing policy files.

- [ ] **Step 4: Commit only roadmap baseline documentation, if it changed**

  ```powershell
  git add HANDOFF.md projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md
  ```

  Do not stage `.gitignore` in this commit.

### Task 1: Complete the 22-background anchor and slot contract

**Files:**
- Modify: `.agents/skills/video-pipeline/scripts/bg_lib/anchors.py`
- Modify: `.agents/skills/video-pipeline/scripts/import_bg.py`
- Test: `test/test_background_import.py` (create)

**Interfaces:**
- Consumes: `ANCHORS[location_id] = (floor_y, scale, crop_center, dx)` and the source SVG/catalog metadata.
- Produces: each generated location entry with `floor_y`, `stand`, `crop_9x16`, `slots`, `anchors_reviewed: true`, and preserved reviewed metadata on re-import.

Use this slot schema for all 22 generated locations:

```json
{
  "slots": {
    "ground-left": {"x": 580, "y": 930, "s": 0.80},
    "ground-center": {"x": 960, "y": 930, "s": 0.80},
    "ground-right": {"x": 1340, "y": 930, "s": 0.80}
  }
}
```

Only slots visibly supported by a scene may be populated; unsupported semantic slots remain absent. Coordinates are scene coordinates in the 1920×1080 viewBox, `s` is the prop/rig scale multiplier, and no slot may be inferred from `focus`.

- [ ] **Step 1: Add explicit source metadata for the 22 scene slot maps**

  Extend `bg_lib/anchors.py` with a `SLOTS` mapping keyed by the same 22 IDs as `ANCHORS`. Use the three ground slot names above for open scenes and add named surface slots only when a visible table/altar/bed/door/window exists. Keep all values in the source file; do not put per-scene coordinates in generated SVG or HTML.

- [ ] **Step 2: Preserve reviewed index metadata during import**

  Refactor `import_bg.py` so a re-import replaces generated fields (`file`, `size`, `layers`, `light_states`, `default_light`, `floor_y`, `stand`, `crop_9x16`, `slots`, `sha256`, `version`) while retaining reviewed user metadata (`description`, `tags`, `moods`, extra approved anchors/slots) unless the source explicitly changes it. Initialize palette tokens only when missing and do not apply `LIGHT_RENAME` twice to `default_light`.

- [ ] **Step 3: Add deterministic import tests**

  Cover: all 22 IDs have an anchor; every generated `stand` is inside the 1920×1080 bounds; crop center is within `[304, 1616]`; slot coordinates are inside the scene; re-import preserves a sentinel reviewed field; missing slot definitions do not become fabricated coordinates.

- [ ] **Step 4: Regenerate and inspect the library**

  ```powershell
  python .agents/skills/video-pipeline/scripts/build_bg.py --no-sheet
  python .agents/skills/video-pipeline/scripts/import_bg.py
  python .agents/skills/video-pipeline/scripts/library.py check
  python .agents/skills/video-pipeline/scripts/library.py sheet
  ```

  Inspect the location sheet and a 9:16 diagnostic contact sheet with `host` composited at L/C/R. Fix only `bg_lib` or importer sources, then repeat the pipeline. Do not edit `library/locations/*.svg` directly.

- [ ] **Step 5: don't Commit the background contract**

  ```powershell
  git add .agents/skills/video-pipeline/scripts/bg_lib/anchors.py .agents/skills/video-pipeline/scripts/import_bg.py test/test_background_import.py library/index.json library/locations assets/library/bg

  ```

### Task 2: Create the canonical demo shotlist from existing project data

**Files:**
- Create: `projects/than-trung-chiec-khan-tang-thu-32/script/shotlist.demo.json`
- Modify: `.agents/skills/video-pipeline/scripts/check_shots.py`
- Test: `test/test_shotlist_contract.py` (create)
- Reference only: `projects/than-trung-chiec-khan-tang-thu-32/video/shots.json`, `video/sfx_cues.json`

**Interfaces:**
- Consumes: line IDs and audio durations from `script/script.json` and `audio/manifest.json`; legacy shot/SFX metadata only as migration input.
- Produces: canonical shots with `id`, `line_ids`, `span`, `location`, `light`, `characters`, `props`, `beats`, and relative per-shot `sfx` cues.

- [ ] **Step 1: Select a 30–40 second demo slice**

  Select 8–12 existing shots covering the hook, two of the bible locations (`loc_gian_tho`, `loc_san_dem`, `loc_hien_nha`), at least two framings/cameras, two speaking characters, one physical action and one stinger. Preserve original line IDs; do not invent dialogue or alter `audio/manifest.json`.

- [ ] **Step 2: Write the canonical demo schema**

  Use this shape for every selected shot:

  ```json
  {
    "id": "S01_SHOT_002",
    "line_ids": ["S01_L02"],
    "span": [0.0, 1.752],
    "kind": "speaker",
    "size": "medium",
    "camera": "dolly_in",
    "location": "loc_gian_tho",
    "light": "warm",
    "characters": [{"id": "me", "emotion": "worried", "mouth": true}],
    "props": [{"id": "khan_xo", "state": "folded"}],
    "beats": [{"line_id": "S01_L02", "t": 0.35, "do": "mẹ nhấc khăn khỏi mâm", "physical": true}],
    "sfx": [{"cue": "foley_fabric_slide", "src": "sfx/ambience/foley/foley-fabric-slide.wav", "t": 0.35}]
  }
  ```

  `span` is relative to the line when a line is split; `beats[*].t` and `sfx[*].t` are relative to the shot. Every beat must be inside the shot duration and every physical beat must match a real file within `0.15` seconds.

- [ ] **Step 3: Make checker input explicit**

  Add `--shotlist` to `check_shots.py`, defaulting to `<project>/script/shotlist.json` and allowing the demo path. Keep `--scenes` strict: an unknown scene ID or a filter that selects no manifest scene fails instead of returning an empty success. Keep the full-run missing-line check enabled when `--scenes` is omitted.

- [ ] **Step 4: Add contract tests**

  Test missing line IDs, unknown scene filters, beats outside `[0, shot_duration]`, missing/empty SFX sources, physical beats without SFX, and a valid `±0.15 s` match. Add a regression test that `synth:<name>` is accepted only when the rendered recipe output exists.

- [ ] **Step 5: don't Commit the demo data contract**

  ```powershell
  git add projects/than-trung-chiec-khan-tang-thu-32/script/shotlist.demo.json .agents/skills/video-pipeline/scripts/check_shots.py test/test_shotlist_contract.py

  ```

### Task 3: Build the first data-driven HyperFrames vertical slice

**Files:**
- Create: `.agents/skills/video-pipeline/scripts/build_video.py`
- Modify: `projects/than-trung-chiec-khan-tang-thu-32/video/index.html` through the generator only
- Test: `test/test_build_video.py` (create)
- Update evidence: `projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md`

**Interfaces:**
- CLI: `python .agents/skills/video-pipeline/scripts/build_video.py --project projects/than-trung-chiec-khan-tang-thu-32 --shotlist script/shotlist.demo.json --out video/index.html`
- Inputs: `audio/manifest.json`, `script/bible.json`, selected shotlist, `library/index.json`, locked project assets.
- Output: deterministic HyperFrames HTML with nested `<svg>` assets, `data-start`/`data-duration` from manifest plus shot offsets, and `window.__timelines` registration.

- [ ] **Step 1: Implement input loading and validation**

  Resolve all relative paths from the repository/project root, reject missing line IDs, reject bible IDs not present in library lock data, reject invalid states/lights, and fail before writing HTML. Do not silently fall back to arbitrary coordinates or colors.

- [ ] **Step 2: Implement nested asset placement**

  Render each location at 1920×1080, place characters using `stand`, place props using location slots or prop-local slots, and embed every rig/prop as a nested `<svg>` with its own viewBox. Use palette tokens from the project/library loader; do not emit literal hex/rgb/named colors in generated composition code.

- [ ] **Step 3: Implement seek-safe motion**

  Animate child nodes rather than `.clip`, register deterministic GSAP timelines, and apply the viewBox pivot from `<id>.rig.json`. Add anticipation, mouth movement driven by measurable WAV amplitude windows, seeded blink intervals, breathing/moving hold, eye-before-head motion, and a short follow-through. Do not use a universal fixed `yoyo` loop.

- [ ] **Step 4: Implement audio and captions**

  Copy/reference only project-local audio assets, create one audio clip per manifest line, set exact `data-start` and `data-duration`, and place captions from the manifest/SRT without covering the characters. Keep voice, BGM, foley and stinger as separate layers with ducking under voice.

- [ ] **Step 5: Add generator unit tests**

  Assert deterministic output for the same inputs, manifest timing preservation, nested SVG structure, no direct `.clip` animation, no hard-coded colors, rejection of an invalid slot/light/state, and correct viewBox pivot serialization.

- [ ] **Step 6: Run the real HyperFrames demo gate**

  ```powershell
  $env:TEMP = 'D:\temp'; $env:TMP = 'D:\temp'
  python .agents/skills/video-pipeline/scripts/build_video.py --project projects/than-trung-chiec-khan-tang-thu-32 --shotlist script/shotlist.demo.json --out projects/than-trung-chiec-khan-tang-thu-32/video/index.html
  python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/than-trung-chiec-khan-tang-thu-32 --phase demo
  python .agents/skills/video-pipeline/scripts/check_shots.py --project projects/than-trung-chiec-khan-tang-thu-32 --shotlist projects/than-trung-chiec-khan-tang-thu-32/script/shotlist.demo.json --scenes S01,S02,S03
  python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/than-trung-chiec-khan-tang-thu-32
  cd projects/than-trung-chiec-khan-tang-thu-32/video
  npx --yes hyperframes@0.9.66 lint
  npx --yes hyperframes@0.9.66 check --json --snapshots
  ```

  Inspect every selected shot, the 9:16 crop diagnostic, character feet, prop slots, mouth/blink/arm motion, caption placement and the three audio mix layers. Record exact commands, duration and artifact paths in `PROJECT.md`; stop for user review here.

- [ ] **Step 7: not Commit only after demo evidence exists**

  ```powershell
  git add .agents/skills/video-pipeline/scripts/build_video.py test/test_build_video.py projects/than-trung-chiec-khan-tang-thu-32/video/index.html projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md
  ```

### Task 4: Migrate the full sample project to one generator

**Files:**
- Modify/create: `.agents/skills/video-pipeline/scripts/build_video.py`
- Create: `projects/than-trung-chiec-khan-tang-thu-32/script/shotlist.json`
- Modify: `projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md`, `HANDOFF.md`
- Archive/deprecate after parity: `preview_1min/*`, `preview_2d/*`, legacy video generator entrypoints

**Interfaces:**
- Consumes: all 417 legacy shot records and 54 SFX records after explicit mapping into the canonical schema.
- Produces: one full `script/shotlist.json`, one reproducible `build_video.py` output, and no production dependency on the legacy preview generators.

- [ ] **Step 1: Convert legacy shot/SFX data without losing traceability**

  Map `video/shots.json` shot IDs, start/duration, framing, camera, action and line IDs into canonical shots. Map `video/sfx_cues.json` to per-shot relative cues using the owning shot start; preserve the legacy ID in a non-rendering `source` field for audit. Any record that lacks a character, location, prop, beat or valid file must fail the converter and be resolved in the source data, not guessed in HTML.

- [ ] **Step 2: Add full-shotlist validation**

  Require every manifest line in the full run to appear in a shot, every spoken line to have a speaking character with `mouth: true`, every physical beat to have a matching SFX, every light to be registered by its location and every prop state to be declared by the bible.

- [ ] **Step 3: Rebuild all 20 scenes and compare parity**

  Generate the full composition, run `check_shots.py` without `--scenes`, `check_sync.py`, `check_rules.py --phase final`, `npx hyperframes lint`, `npx hyperframes check --json --snapshots`, then compare representative frames and total duration with the legacy preview. Treat visual differences as source/bible/shotlist fixes; never patch generated HTML.

- [ ] **Step 4: Deprecate legacy generators only after parity**

  Add a short migration note identifying `build_video.py` as the sole generator, move old preview generators under an explicitly marked legacy area or remove them only if their outputs and source data are preserved, and keep legacy hex warnings isolated from the new generator gate.

- [ ] **Step 5: not Commit the migration**

  ```powershell
  git add .agents/skills/video-pipeline/scripts/build_video.py projects/than-trung-chiec-khan-tang-thu-32/script/shotlist.json projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md HANDOFF.md
  ```

### Task 5: Extend CI and close the verified PR gate

**Files:**
- Modify: `.github/workflows/gates.yml`, `projects/than-trung-chiec-khan-tang-thu-32/video/package.json` if its existing `0.9.67` pin conflicts with the repo-approved `0.9.66` runtime
- Test: existing `test/` suite plus the new background/shotlist/generator tests
- Update evidence: `HANDOFF.md`, `PROJECT.md`

**Interfaces:**
- Consumes: reproducible source generators, sample project data and the pinned HyperFrames CLI.
- Produces: CI evidence for library, source/import parity, rig, rules, shots, sync and HyperFrames runtime.

- [ ] **Step 1: Add Node and HyperFrames setup**

  Pin Node 24.16-compatible setup, invoke `hyperframes@0.9.66` to match the current repo environment, and retain the existing Python 3.12 job. Reconcile the current project package pin before adding CI; do not silently upgrade the CLI. Do not use a background shell wrapper for Studio preview in CI.

- [ ] **Step 2: Add non-mutating CI checks**

  Run Python compilation, unit tests, `library.py check`, `build_bg.py --no-sheet` plus import parity, sample rig generation, `check_rules.py`, demo/full `check_shots.py`, `check_sync.py`, `hyperframes lint` and `hyperframes check --json`. Generated temporary outputs must go to runner temp or ignored artifact folders; CI must fail if tracked library output differs from source.

- [ ] **Step 3: Keep the missing-bible project explicit**

  Continue skipping `ma-thoi-den-thanh-co-tinh-tuyet` with a visible reason until a user supplies/approves its bible; do not make CI silently treat it as production-ready.

- [ ] **Step 4: Run and document the complete suite**

  ```powershell
  python -m pytest -q
  git diff --check
  ```

  Separate focused passes from stale/unrelated failures in `HANDOFF.md`; never lower a threshold or hide a failure.

- [ ] **Step 5: Not Commit CI changes and update PR evidence**

  ```powershell
  git add .github/workflows/gates.yml HANDOFF.md projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md test
  ```

### Task 6: Expand the reusable library after the demo contract is locked

**Files:**
- Modify: `library/rigs/archetypes.json`, `library/index.json`, relevant `library/palettes/*.json`
- Create/update source assets through the existing library workflow, not project-local copies
- Update: the sample bible and `PROJECT.md` only after pose/sheet review

**Interfaces:**
- Consumes: approved demo style, existing archetypes/outfits, `library.py list/show`, project usage evidence.
- Produces: reusable rigs/props/outfits with stable IDs, states, slots, pivots, palette references, sheets and SHA locks.

- [ ] **Step 1: Inventory before creation**

  Run `library.py list`/`show` for each requested character and prop. Record why no existing asset is sufficient before creating anything.

- [ ] **Step 2: Clone nearest rigs first**

  Use `extends` plus minimal `rig_params` for `bố`, `chú`, `em gái`, `bé Na`, `Vy` and future outfit variants. Use existing child/teen archetypes only after pose sheets are generated; do not ship them into the demo before user approval.

- [ ] **Step 3: Create and promote missing props**

  Add the requested mirror, coffin, incense/lighting, fan and mourning-clothing assets only when the library has no usable equivalent. Enforce palette tokens, `data-state`, bottom-center origin, internal ID prefixes and declared slots.

- [ ] **Step 4: Validate each asset batch**

  ```powershell
  python .agents/skills/video-pipeline/scripts/library.py check
  python .agents/skills/video-pipeline/scripts/library.py sheet
  ```

  Review pose/asset sheets, then `library.py promote` and refresh `LIBRARY.lock.json`. Keep each batch independently committed.

### Task 7: Complete the reusable SFX inventory and recipes

**Files:**
- Modify: `sfx/README.md`
- Create/update: the existing `sfx/` recipe/source layout and its permission/license records
- Modify: `.agents/skills/video-pipeline/scripts/check_shots.py` only for validated recipe/file resolution

**Interfaces:**
- Consumes: canonical shotlist cue names and existing CC0/owned assets.
- Produces: stable cue IDs for gong, mortar, heartbeat, firewood, footsteps, creaking door, breathing, stinger and drone, with rendered `synth:<name>` outputs where used.

- [ ] **Step 1: Inventory and license every source**

  Reuse existing `sfx/` assets first; add `source/permission.md` or equivalent provenance for every non-generated file. Replace the absolute `file:///d:/...` links in `sfx/README.md` with repository-relative links.

- [ ] **Step 2: Extract parameterized recipes**

  Move reusable recipe logic out of `build_perfect_sfx_72s.py` into the shared recipe path, keeping deterministic seed/parameters and rendering each named recipe to the project’s `audio/sfx/` output before a gate accepts it.

- [ ] **Step 3: Verify mix behavior in the demo**

  Check voice-only, voice+BGM and full mix; ensure no SFX masks speech, BGM has room tone, and stingers are limited to the demo contract. Keep the `±0.15` timing gate.

### Task 8: Run a Mode C pilot when the user supplies an idea

**Files:**
- Create one new `projects/<slug>/` only after the user supplies the idea and approves the bible/outline.
- Update that project’s `PROJECT.md`, `script/`, `audio/`, `video/` and `output/` only through the prescribed pipeline.

**Interfaces:**
- Consumes: user idea, approved concept/bible/outline, `scaffold_project.py --mode c`, VieNeu and HyperFrames.
- Produces: a 30–40 second demo that passes the C-mode gates; full production remains blocked until explicit demo approval.

- [ ] **Step 1: Stop at the missing user input**

  Do not repurpose `ma-thoi-den-thanh-co-tinh-tuyet`. Ask for the idea, audience/format and desired tone when this milestone is started.

- [ ] **Step 2: Follow C-mode order**

  Concept → bible → outline → script at speed `1.3` → demo shotlist → TTS → SFX → HyperFrames → gates. Skip `originality_check.py` for Mode C and use the source-free concept gate defined in `workflow-v2.md`.

- [ ] **Step 3: Apply the same approval gate**

  Require user review of characters, acting, SFX/mix, backgrounds/props, shot rhythm and voice before any full render.

### Task 9: Final cleanup and handoff closure

**Files:**
- Update: `HANDOFF.md`, all touched project `PROJECT.md` files, PR #1 description/comments as needed.
- Only after verified parity: legacy preview files and generated artifact policy.

- [ ] **Step 1: Separate legacy warnings from new production errors**

  Keep existing `preview_*` hex warnings documented while ensuring every new generator output is token-based. Remove or archive legacy code only after the full generator parity gate.

- [ ] **Step 2: Confirm all required gates**

  Completion requires `library.py check` clean, `check_rules.py` clean, `check_shots.py` zero errors, `check_sync.py` OK, `hyperframes lint` clean, `hyperframes check --json` with `ok: true`, and reviewed snapshots/preview. A nominal config, mock, or focused-only test is insufficient.

- [ ] **Step 3: Update HANDOFF with evidence**

  Replace each `[ ]` item only with the command, date, result and artifact path that proves it. Keep the missing-bible project and any user-review decisions explicitly marked pending.

- [ ] **Step 4: Final PR review**

  Push commits, wait for CI/Codex review to finish, resolve comments that are fixed, and leave the two contract decisions documented as accepted/rejected findings. Do not claim the PR is merge-ready while checks are pending.

## Acceptance Criteria

- The 22 generated backgrounds have source-owned anchors/slots, pass import parity and library validation, and have a reviewed 9:16 diagnostic sheet.
- The sample project has a canonical demo shotlist and a reproducible 30–40 second HyperFrames output generated by `build_video.py`.
- Demo gates pass with real artifacts: `check_rules.py`, `check_shots.py`, `check_sync.py`, `hyperframes lint`, `hyperframes check --json`, and reviewed snapshots.
- The full sample project migrates from legacy shot/SFX data to one generator without missing manifest lines, invalid states/lights, or untracked manual HTML edits.
- CI enforces the same static and runtime gates; failures remain visible and thresholds are not weakened.
- Library/SFX additions are reusable, provenance-backed, palette-token compliant and locked per project.
- Mode C is ready to run but not fabricated without a user idea; the missing-bible project remains explicitly deferred.
- `HANDOFF.md` records evidence after every gate and no completion claim is made before all required gates pass.

## Assumptions and Explicit Decisions

- Execution order is **gate-first vertical slice**.
- SFX tolerance is **±0.15 seconds**; no “millisecond” policy change is planned.
- Rig pivot is **viewBox-based per R3.4**; no `0% 0%` migration is planned.
- The existing `.gitignore` edit is unrelated local work and remains unstaged.
- The sample project’s current 16:9 format remains unchanged; the 9:16 behavior is validated through the explicit crop diagnostic and reusable anchor data.
- `ma-thoi-den-thanh-co-tinh-tuyet` is deferred until the user provides/approves its bible.
- Any ambiguity found while converting legacy shots is a source-data blocker: stop and ask, rather than inventing character, prop, timing or factual details.
