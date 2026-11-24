# Demo Interaction and SFX Correction Design

## Goal

Sửa demo 30–40 giây để hành động người–người nhìn thấy được, cảnh kéo Lan ra cửa có blocking/camera tương ứng, và SFX được chọn theo hành động thật thay vì từ khóa chung.

## Root causes found

- S01_L04/SH003 phát foley.door_creak nhưng shot chỉ có Vũ, không có Lan hoặc beat move/react, và focus không trỏ về cửa.
- make_full_shotlist.py và regroup_full_shotlist.py ưu tiên từ khóa khóa, nên các câu về chìa khóa có thể nhận nhầm SFX cửa.
- prop_for() chọn trạng thái hu_dat=cracked theo vòng lặp chỉ số, không theo hành động trong câu.
- Shot hai nhân vật chủ yếu dùng set; generator có auto gaze/nod nhưng không tạo blocking hoặc hand-over tường minh cho các hành động tương tác.

## Design

1. Giữ dữ liệu gốc ở planner. Sửa semantic cue matching trong make_full_shotlist.py và dùng chung qua regroup_full_shotlist.py.
2. Chỉ gán foley.door_creak khi câu có hành động cửa rõ ràng (mở cửa, cửa tự mở, đập vào cửa, kéo ra cửa, đóng cửa, ngưỡng cửa); không gán chỉ vì khóa hoặc chìa khóa.
3. Chỉ gán hu_dat=cracked khi câu mô tả vỡ/nứt/rạn/bể/đập; câu chỉ nhắc hũ giữ trạng thái sealed hoặc open theo nội dung.
4. Với câu có chuyền/trao/đưa và có hai nhân vật, planner tạo hand_over + beat vật lý + SFX tác động; với S01_L04, planner đưa Lan vào shot, thêm move về anchor gần cửa, focus vào slot:house-door, và thêm phản ứng của Vũ.
5. Thêm regression tests cho cue cửa/chìa khóa, trạng thái hũ và shot tương tác. Rebuild demo bằng build_video.py, chạy các gate bắt buộc, xem snapshot các shot sửa và kiểm tra MP4 bằng ffprobe.

## Acceptance criteria

- SH003 có Lan, có blocking di chuyển về phía cửa, focus cửa, và door_creak nằm cùng beat hành động.
- Shot hũ cracked không có door_creak; có SFX va chạm phù hợp nếu có hành động vật lý.
- Shot có từ hai nhân vật có hành vi tường minh cho cả hai nhân vật.
- check_shots.py, check_motion.py, check_sync.py, check_rules.py, hyperframes check --json pass; snapshot sau rebuild được mở và kiểm bằng mắt.
- Chỉ demo được render lại; full chưa chạy.
