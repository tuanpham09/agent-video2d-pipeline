# Design: Đứa Đứng Đầu Sau Lúc Tắt Nắng

**Trạng thái:** Draft, chờ người dùng review file thiết kế trước khi scaffold.

## 1. Brief đã chốt

- Nguồn tham khảo: YouTube `3FleNiLDpig`, kênh Dạ Hành Dị Tạp.
- Project slug dự kiến: `rong-ran-len-may-nguoi-dung-dau`.
- Dạng: truyện ma Việt chuyển thể, bản dài 20–30 phút.
- Khung hình: 16:9, 1920×1080.
- Ngôn ngữ: tiếng Việt.
- Quy trình: làm demo 30–40 giây, chạy gate, gửi người dùng duyệt; chỉ sau khi duyệt mới làm full.
- Chỉ dùng asset có sẵn trong `library/`; không tạo asset mới nếu chưa chứng minh library không có mẫu dùng được.

## 2. QA nguồn và ranh giới chuyển thể

Transcript đã lấy được ở dạng tiếng Việt tự động: 765 snippet, khoảng 35:10, không có caption thủ công. Nội dung nguồn xoay quanh một luật chơi trẻ con, một người đứng đầu hàng bất thường và hậu quả quay lại nhiều năm sau. Transcript có thể có lỗi nhận dạng tiếng; không dùng nguyên văn làm script.

Bản chuyển thể phải thay đổi có chủ đích:

- tên nhân vật, quan hệ gia đình và địa danh;
- vật neo của lời nguyền và luật chơi;
- thứ tự tiết lộ, điểm nhìn và cấu trúc hồi tưởng;
- câu chữ, hội thoại, mô tả và nhịp cảnh;
- cách kết thúc demo và cách mở khóa nguyên nhân ở bản full.

Không giữ nguyên chuỗi cảnh, tên riêng, quan hệ, câu thoại hoặc cách kể của nguồn. Trước khi chốt script, chạy `originality_check.py` trên bản rewrite và lưu kết quả trong `PROJECT.md`. Bản demo chỉ dùng làm bản chuyển thể nội bộ; quyền xuất bản/nguồn tham khảo phải được ghi rõ trong `source/permission.md`.

## 3. Hướng kể chuyện

Working title: **Đứa Đứng Đầu Sau Lúc Tắt Nắng**.

Người kể là một người cha trở về căn nhà cũ sau nhiều năm, khi con gái nhỏ bắt đầu lặp lại một trò chơi mà anh tưởng chỉ là ký ức làng quê. Luật cũ không được giải thích ngay; khán giả chỉ thấy các dấu hiệu vật lý: hàng người đứt tay, tóc ướt xuất hiện trong bóng tối, một vật bị khóa, và tiếng gõ ở cổng. Bản full mở rộng nguyên nhân qua ba lớp thời gian: hiện tại, tuổi thơ của người cha, và bí mật của thế hệ trước.

Nhịp mục tiêu:

1. **Móc câu:** luật chơi bị phá đúng lúc ánh sáng tắt; kết bằng dấu hiệu có người thứ năm.
2. **Đời sống hiện tại:** người cha, con gái và căn nhà cũ; một vật gia truyền trở thành cầu nối.
3. **Hồi ức tuổi thơ:** thay đổi người chứng kiến và lý do họ giấu chuyện.
4. **Điều tra trong làng:** bờ sông, sân nhà, gian thờ và dấu vết của một lần mất tích.
5. **Đối đầu:** luật chơi quay lại với đứa trẻ hiện tại; người cha phải chọn giữa mở cổng và phá luật.
6. **Kết:** giải thích vừa đủ, còn lại một tín hiệu âm thanh/hình ảnh để giữ dư âm; không sao chép cú kết của nguồn.

## 4. Nhân vật và asset

Ưu tiên archetype/outfit hiện có, khóa id sau khi build rig và duyệt pose sheet:

- người cha/người kể: `adult_m` + `nau_song`;
- con gái: `child` + `plain_light`;
- bà/người giữ luật cũ: `elder_f` + `ao_the_indigo`;
- thực thể đứng đầu hàng: `spirit_shadow`, chỉ dùng khi cần silhouette siêu nhiên.

Bối cảnh ưu tiên từ library: `toan_canh_lang`, `village_yard_night`, `bo_song`, `bui_tre_chuoi`, `san_nha`, `gian_tho_dem`, `phong_ngu`, `nha_co_nha_tho_ho`, `nha_hoang`.

Đạo cụ ưu tiên: `clay_jar`, `oil_lamp`, `candle`, `ancestral_altar`, `bamboo_tray`, `mourning_cloth`, `smartphone`. Nếu bible cần vật mới, phải ghi lý do không dùng được asset hiện có trong `PROJECT.md`, rồi làm đúng quy trình library.

## 5. Demo 30–40 giây

Demo chỉ chứng minh hook, phong cách hình và nhịp âm thanh; không triển khai full cốt truyện.

- 8–10 shot, xen wide/medium/close/macro.
- Mở ở sân làng lúc ánh sáng tắt; một nhóm trẻ chơi nhưng không lộ rõ mặt thực thể.
- Cắt về hiện tại: người cha nghe con gái đọc lại luật chơi trong phòng ngủ.
- Một đạo cụ trong nhà đổi state theo beat; tiếng gõ thứ nhất và thứ hai có SFX.
- Kết demo ở khoảng 30–40 giây ngay trước lần gõ tiếp theo, tạo cliffhanger mới.
- Mỗi beat nhìn thấy có `set`/`move`/`look`/`react`; beat vật lý có SFX.

Demo phải có manifest/timing thật, rig lồng `<svg>`, cảnh từ library, và được kiểm bằng snapshot từng shot. Không render full trước khi người dùng duyệt demo.

## 6. Pipeline và cổng nghiệm thu

1. Scaffold project riêng, lưu transcript/meta/cover vào `projects/rong-ran-len-may-nguoi-dung-dau/source/`.
2. Viết `source/qa.md`, `source/permission.md`, `script/brief.md` và rewrite plan.
3. Viết `script/script.md`, `script/script.json`, `bible.json`, packaging nháp; chạy `originality_check.py`.
4. Dùng `library.py use`, chạy `build_rig.py`, mở pose sheet và lineup để kiểm tra bằng mắt.
5. Sinh voice demo bằng VieNeu-TTS; `check_audio.py` và `check_sync.py` phải có bằng chứng thật.
6. Viết `shotlist.demo.json`, dựng bằng `build_video.py`, chạy `check_shots.py`, `check_motion.py`, `check_sync.py`, `hyperframes lint` và `hyperframes check --json`.
7. Render snapshot/preview demo, mở ảnh ở cỡ dùng thật và ghi lỗi đã sửa trong `PROJECT.md`.
8. Gửi demo cho người dùng duyệt. Chỉ khi được duyệt mới mở rộng 20–30 phút, chạy lại gate theo từng scene và render delivery.

## 7. Tiêu chí thành công

- Demo 30–40 giây có hook rõ, không dùng nguyên văn hay chuỗi cảnh của nguồn.
- Hình 16:9 ổn định: chân chạm sàn, mặt không đen/trống, camera không cắt chủ thể, đạo cụ đúng slot/state.
- Gate demo: `check_rules.py` 0 lỗi, `check_shots.py` 0 lỗi, `check_sync.py` OK, `check_motion.py` OK, `hyperframes check --json` `ok: true`.
- Đã mở và xem snapshot từng shot; báo cáo nêu rõ ảnh đã xem, lỗi đã sửa và phần chưa kiểm.
- Full chỉ bắt đầu sau khi người dùng duyệt demo; không commit/push nếu chưa có yêu cầu riêng.

## 8. Rủi ro và cách xử lý

- Transcript tự động sai tiếng: đối chiếu các đoạn then chốt và viết lại từ ý, không sửa tay file sinh.
- Tương đồng với nguồn: đổi cấu trúc trước, chạy originality gate; nếu fail thì sửa script/diff matrix.
- 20–30 phút tốn TTS/render: khóa demo trước, cache audio theo câu, mở rộng theo scene.
- Thiếu quyền xuất bản: giữ `source/permission.md` rõ trạng thái; chỉ làm bản demo/chuyển thể nội bộ cho tới khi có quyết định quyền.
