# HANDOFF → OpenCode (và agent khác): triển khai Spec v4

**Việc của bạn:** thực hiện [`spec-v4-implementation.md`](.agents/skills/video-pipeline/references/spec-v4-implementation.md) theo từng mốc M1 → M2 → M3. Lý do thiết kế: [`research-v4-report.md`](.agents/skills/video-pipeline/references/research-v4-report.md). Hai file này là nguồn sự thật; nếu mâu thuẫn với trí nhớ/giả định của bạn thì file thắng. Nếu mâu thuẫn với `RULES.md` thì **`RULES.md` thắng**.

## 1. Bắt đầu

```bash
git fetch origin && git checkout -b opencode/v4-m1 origin/claude/workflow-v2   # mốc mới = nhánh mới từ nhánh trước đã xanh
```
Đọc theo thứ tự: `CLAUDE.md` → `RULES.md` (v2) → `AGENTS.md` → `references/craft-playbook.md` (chỉ cần khi động tới hình ảnh; M1–M3 không đụng) → spec → báo cáo §C–§E.

Trạng thái mốc hiện tại (cập nhật bảng này sau mỗi mốc):

| Mốc | Nội dung | Trạng thái |
| --- | --- | --- |
| M1 | `hashing.py`, `pipeline_state.py`, `vp.py` (doctor/validate/status/next/gate/approve), CI | **Chưa làm** |
| M2 | `shot_key`, `vp plan`, bảng vô hiệu hoá + test | Chưa làm (phụ thuộc M1) |
| M3 | `world_state.py`, `check_continuity.py` | Chưa làm (phụ thuộc M1) |
| M4 | Aligner mốc từ + cổng chính xác (cần wav thật) | Chờ người dùng gật + có wav |
| M5 | Thử `three_quarter` cho một nhân vật | Chờ người dùng gật; sau M3 |

Đã có sẵn (đừng làm lại): `schemas/{script,bible,shotlist,manifest}.schema.json` + `validate_schemas.py`; `timing_lib.py`; `check_shots.py` (E1–E8); `check_audio.py`; generator hỗ trợ beat `move|look|react|hand_over`; pose `walk-a/walk-b`; `tests/test_roadmap_v3.py` (31 kiểm, tất cả qua tại commit `8a56a58`).

## 2. Lệnh kiểm nền (chạy trước khi sửa, và sau mỗi bước)

```bash
python .agents/skills/video-pipeline/scripts/tests/test_roadmap_v3.py          # phải: TẤT CẢ QUA
python .agents/skills/video-pipeline/scripts/validate_schemas.py --project projects/than-trung-chiec-khan-tang-thu-32
python .agents/skills/video-pipeline/scripts/check_shots.py     --project projects/than-trung-chiec-khan-tang-thu-32 --scenes S01
python .agents/skills/video-pipeline/scripts/check_rules.py     --project projects/than-trung-chiec-khan-tang-thu-32 --phase demo
python .agents/skills/video-pipeline/scripts/library.py check
```
`check_audio.py` trên project mẫu **FAIL là bình thường** (chưa có wav; VieNeu chạy trên máy người dùng). Không "sửa cho qua".

## 3. Bẫy đã biết trong repo này

- **Không sửa file sinh tự động:** `audio/lines|scenes|voiceover.wav`, `video_demo/**`, `assets/rig/*.svg|*.rig.json|sheets/*`, `library/sheets/*`. Muốn đổi → sửa nguồn rồi chạy lại generator (R1.3).
- **HyperFrames:** CSS trong asset/rig **không dùng combinator `>`** (bộ lọc style của HyperFrames bỏ cả `<style>` nếu gặp); rig chỉ nhúng dạng `<svg>` lồng nhau; không animate trực tiếp `class="clip"`.
- **Thời gian:** `audio/manifest.json` là nguồn duy nhất cho thời lượng (R1.2); không sửa tay.
- **Màu:** chỉ token `var(--pal-<token>)`, cấm hex trong asset library/generator (R2.5).
- Biến `chars` trong `check_shots.py` là dict bible; dùng `shot_chars` cho danh sách nhân vật của shot (từng gây lỗi).
- Môi trường người dùng là Windows/PowerShell (ổ `D:\`): dùng `pathlib`, không giả định `/`; không ghi vào `C:` khi render (R9.2).
- Gọi script khác bằng `subprocess` với `sys.executable`; ép UTF-8 như các script hiện có.

## 4. Quy ước làm việc

- Commit theo mốc nhỏ, thông điệp nêu **đã làm / chưa làm**; không force push; không sửa lịch sử đã push.
- Cập nhật bảng trạng thái ở mục 1 + `projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md` (nhật ký gate: ngày, lệnh, kết quả) sau mỗi mốc.
- Báo cáo mỗi mốc có: file đổi, lệnh + mã thoát + kết quả thật, test thêm, mục **Chưa kiểm**. Không tuyên bố hoàn thành khi chưa chạy lệnh trong "Chấp nhận" của spec (R8.2, R8.3).
- Gặp điều spec không làm được hoặc mâu thuẫn thực tế (ví dụ giả thuyết thời gian tương đối ở M2.1 sai): **dừng, ghi vào mục 5, hỏi người dùng** (R0.4). Không làm gần giống.
- Không thêm phụ thuộc nặng; không dùng code từ repo ngoài (xem license ở báo cáo §B).

## 5. Câu hỏi mở / đề xuất luật (agent ghi vào đây, người dùng quyết)

Spec dùng **khuyến nghị theo ưu tiên chính xác / đồng bộ / tốc độ ổn định** (lý do ở spec §1); chờ người dùng gật hoặc đổi. **M1–M3 làm được ngay không cần câu trả lời nào ngoài câu 1 và 3 (đã là mặc định); M4–M5 chỉ làm khi người dùng gật câu 4 và 2.**
1. Migration: `.pipeline/` + `vp` song song luồng cũ; chỉ chuyển khi `vp gate` trùng kết luận gate cũ trên mọi project.
2. Quay người: `three_quarter` sinh theo tham số rig, thử một nhân vật, người dùng duyệt ảnh rồi mới nhân rộng (M5).
3. Cache/khoá: tự viết tối giản (thư mục theo hash + `os.replace` + khoá `O_EXCL`); không `doit`; SQLite chỉ khi ≥ 2 worker (P5).
4. ASR/MFA: forced alignment có điều kiện (M4): thăm dò VieNeu trước, MFA sau, đường lui biên độ; cổng đo 20 câu < 0,1 s; hỏi pháp lý trước khi dùng thương mại.

Đề xuất luật (nếu cần, **không tự sửa `RULES.md`**): _(trống)_

Điểm kẹt do agent ghi: _(trống)_

## 6. Việc của người dùng (agent không làm được)

- Chạy `build_voiceover.py` trên máy có VieNeu rồi `check_audio.py`.
- Duyệt pose sheet (R3.7), duyệt demo trước khi làm full (R8.1).
- Trả lời 4 câu ở mục 5.
