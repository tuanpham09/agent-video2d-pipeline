# Đề xuất luật R14 (CHỜ NGƯỜI DÙNG DUYỆT, R0.3: agent không tự sửa RULES.md)

Nếu duyệt: thêm vào `RULES.md` (nâng lên phiên bản 4, ghi vào *Ngoại lệ* của `PROJECT.md` theo R0.2), thêm một dòng vào bảng "Luật → công cụ kiểm".

## R14. Kịch bản kịch tính, gài mở–đóng, review độc lập — bắt buộc khi viết hoặc viết lại `script.json`

Chi tiết: [`script-drama-guide.md`](.agents/skills/video-pipeline/references/script-drama-guide.md), [`script-review-protocol.md`](.agents/skills/video-pipeline/references/script-review-protocol.md).

- **R14.1** Kịch bản có khối `drama` (`promise`, `genre`, `tension_pattern`, `motives`, `rules`, `loops`) và mỗi cảnh có `drama` (`beat`, `tension`, `turn`, `hook_out`, `causes`).
- **R14.2** Mọi setup phải được trả (payoff) hoặc là `open` (tối đa 1, làm tease); payoff không đến trước trigger; mystery có ≥2 manh mối công bằng đứng trước payoff; luật siêu nhiên có `cost`, nêu trước khi dùng.
- **R14.3** Hook: câu đầu không chào/dẫn nhập, ≤14 từ, gài vòng lặp đầu trong 6 câu đầu; không quãng >20 câu không biến cố; cảnh nào cũng có `turn` và (trừ cảnh cuối) `hook_out`.
- **R14.4** `check_script_drama.py --strict` phải 0 lỗi trước khi chốt kịch bản/chạy TTS (R1.5) và trước cổng demo/full.
- **R14.5** Trước khi chốt: review độc lập bằng ≥3 agent khác nhau (lens logic, loops, retention), không thấy lập luận người viết; mọi lỗi `must` sửa hoặc có lý do trong `PROJECT.md`; `script/review/REVIEW.md` nằm trong project.
- **R14.6** Chi tiết siêu nhiên/dân gian không có trong nguồn ghi `note: đề xuất`, không coi là sự thật của nguồn (R7.1).

Bảng kiểm: R14.1–R14.4 → `check_script_drama.py` (DR1–DR10), `gates.py`; R14.5 → `script-review-protocol.md` + người duyệt.
