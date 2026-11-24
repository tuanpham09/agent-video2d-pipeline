# Doc map — file nào là nguồn sự thật

Đọc file này khi không chắc một thông tin nằm ở đâu, hoặc khi hai tài liệu nói khác nhau.

## Thứ tự đọc

| Bước | File | Trả lời câu hỏi |
| --- | --- | --- |
| 1 | `RULES.md` (gốc repo) | Được làm gì, cấm gì. Có ID để dẫn chiếu. |
| 2 | `.agents/skills/video-pipeline/references/workflow-v2.md` | Làm theo thứ tự nào, checklist gì, cổng nào, pass khi nào. |
| 3 | `.agents/skills/video-pipeline/SKILL.md` | Lệnh nào, giai đoạn nào, chế độ nào. |
| 4 | `.agents/skills/video-pipeline/references/2d-animation-doctrine.md` | Kỹ thuật diễn xuất, rig, SFX, checklist HyperFrames. |
| 5 | `library/README.md` | Chuẩn asset dùng chung, cách `use`/`promote`. |
| 6 | `HANDOFF.md` | Việc đang dở, trạng thái thực tế của phiên trước. |

## Nguồn sự thật theo loại dữ liệu

| Dữ liệu | Nguồn duy nhất | Cấm |
| --- | --- | --- |
| Thời lượng, `data-start`, `data-duration` | `projects/<slug>/audio/manifest.json` | sửa tay số trong manifest (R1.2) |
| Lời thoại, giọng, cảm xúc | `script/script.json` + `audio/voice_map.json` | sửa file wav (R1.3) |
| Nhân vật, bối cảnh, đạo cụ, `emotion_vocab` | `script/bible.json` | khai trùng lặp trong shotlist/HTML (R1.4) |
| Shot, beat, SFX cue | `script/shotlist.json` | viết tay HTML cho từng shot (R1.6) |
| Tên cue SFX → file, gain, độ dài cắt | `sfx/cues.json` | hard-code đường dẫn rải rác trong shotlist v2 |
| Kế hoạch chuyển động đã tính (ops, footstep) | `projects/<slug>/video/demo/motion_plan.json` (do `build_video.py` sinh) | sửa tay file plan (R1.3) |
| Asset dùng chung (rig/prop/bg/palette) | `library/index.json` + `library/*` | sửa bản copy trong project (R2.3) |
| Phiên bản asset đã khoá của project | `projects/<slug>/assets/LIBRARY.lock.json` | nâng cấp ngầm (R2.10) |
| Trạng thái project, ngoại lệ luật | `projects/<slug>/PROJECT.md` | ghi trạng thái chỉ trong chat (R8.1) |
| Nguồn & quyền nội dung | `source/qa.md`, `source/permission.md` | giữ cốt truyện nguồn khi chưa có phép (R7.1–R7.2) |

## Khi hai tài liệu mâu thuẫn

1. `RULES.md` thắng tất cả.
2. `workflow-v2.md` thắng `SKILL.md` và doctrine về **thứ tự, cổng, tiêu chí pass**.
3. Doctrine thắng `SKILL.md` về **kỹ thuật hình** (nhưng không được trái `RULES.md`).
4. `PROJECT.md` chỉ ghi trạng thái và ngoại lệ; không được nới luật (R0.5).
5. Nếu mâu thuẫn không giải được bằng 4 điều trên: **dừng, báo, hỏi** (R0.4). Không tự chọn bên có lợi.

## Sửa gì thì sửa ở đâu

| Muốn đổi | Sửa tại | Không sửa |
| --- | --- | --- |
| Luật | `RULES.md` — **chỉ người dùng** (R0.3) | agent, skill, project |
| Thứ tự / cổng / checklist | `workflow-v2.md` | `SKILL.md` (chỉ cập nhật bảng lệnh) |
| Lệnh, tham số CLI | `SKILL.md` + script tương ứng | tài liệu marketplace |
| Cách diễn xuất, rig, SFX | `2d-animation-doctrine.md` + `build_video.py` | HTML sinh tự động |
| Cỡ cảnh, camera, gesture, walk cycle | `build_video.py` (`SIZE_FRAMING`, `CAMERA_MOTION`, `WALK_CYCLE`) + `build_rig.py` | khai lại số trong shotlist/HTML |
| Chuẩn asset | `library/README.md` + `library.py` | `library/**/*.svg` (trừ khi sửa nguồn `bg_lib/`) |
| Trạng thái một video | `projects/<slug>/PROJECT.md` | `HANDOFF.md` (chỉ ghi việc chung) |

## Chống trôi tài liệu

`test/test_docs_consistency.py` chặn ba loại lỗi đã từng xảy ra:

1. `SKILL.md` không trỏ về `RULES.md` / `workflow-v2.md` / demo gate.
2. Doctrine chứa lại mẫu animation cũ đã bị thay.
3. Tài liệu dẫn một skill không tồn tại trong `.agents/skills/` (trừ allowlist skill cài ở cấp máy).

Chạy `python -m pytest test/test_docs_consistency.py -q` sau mỗi lần sửa tài liệu.
