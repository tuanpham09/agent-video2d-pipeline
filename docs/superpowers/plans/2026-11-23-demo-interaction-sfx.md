# Demo Interaction and SFX Correction Implementation Plan

> Inline execution is already selected. Execute the tasks in order and verify each checkpoint before continuing.

Goal: Sửa planner/shotlist để demo thể hiện tương tác thật, cửa có hành động nhìn thấy, và SFX không bị gán sai cho hũ.

Architecture: Giữ build_video.py là generator duy nhất. Sửa planner tạo shotlist.json, thêm test cho semantic cue/state/interaction, rồi rebuild demo bằng dữ liệu nguồn và kiểm tra HyperFrames.

Tech Stack: Python 3.14, pytest, JSON shotlist, HyperFrames CLI 0.9.x, FFmpeg/ffprobe.

## Global Constraints

- Tuân thủ RULES.md v2, workflow-v2.md, R1.6/R5.1/R6.1/R8.2/R10.6/R11.1.
- Không sửa HTML sinh tự động bằng tay.
- Không đổi rig/library đã khóa; không chạy full render.
- Render PNG/snapshot và mở ảnh trước khi báo demo đạt.

### Task 1: Add failing planner regression tests

Files:
- Create: test/test_rong_ran_shotlist_planner.py

- [ ] Test cue_for("Tôi nhặt chìa khóa...") is not foley.door_creak.
- [ ] Test cue_for("cánh cửa tự mở vào trong") is foley.door_creak.
- [ ] Test prop_for(..., "chiếc hũ rỗng", ...) is not cracked.
- [ ] Test generated S01_L04 contains Lan, a move toward the door-side anchor, and focus == slot:house-door.
- [ ] Run pytest -q test/test_rong_ran_shotlist_planner.py; confirm RED because the current planner violates these assertions.

### Task 2: Implement semantic cue and prop-state fixes

Files:
- Modify: projects/rong-ran-len-may-nguoi-dung-dau/script/make_full_shotlist.py
- Modify: projects/rong-ran-len-may-nguoi-dung-dau/script/regroup_full_shotlist.py
- Test: test/test_rong_ran_shotlist_planner.py

- [ ] Make cue_for() classify explicit door actions before generic object words, exclude bare khóa/chìa khóa, and classify break/crack actions as hit.soft.
- [ ] Make prop_for() choose cracked only from break/crack words; choose open only from opening words; otherwise keep sealed.
- [ ] Add be_lan to the S01_L04 two-person shot, set focus to slot:house-door, add move and listener react, and place the door cue at the same action beat.
- [ ] Add hand_over for explicit transfer verbs when a matching prop and two characters are present.
- [ ] Run the focused test file and confirm GREEN.

### Task 3: Regenerate and gate the demo source

Files:
- Modify: projects/rong-ran-len-may-nguoi-dung-dau/script/shotlist.json
- Modify: projects/rong-ran-len-may-nguoi-dung-dau/video/demo/*
- Modify: projects/rong-ran-len-may-nguoi-dung-dau/PROJECT.md

- [ ] Run the planner/regroup command used by the project and verify shotlist.json is valid JSON.
- [ ] Run build_video.py --project ... --out .../video/demo --scenes S01.
- [ ] Run check_rules.py --phase demo, check_shots.py --scenes S01 --phase demo, check_motion.py, check_sync.py, and npx hyperframes check --json.
- [ ] Open snapshots for SH002, SH003, and SH007; verify both characters move/react, the door is framed, and the jar state/SFX match.
- [ ] Render only output/demo-v2.mp4, run ffprobe, and append exact evidence plus an “Ảnh đã XEM” line to PROJECT.md.
