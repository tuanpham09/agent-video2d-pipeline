# Review kịch bản độc lập bằng agent khác

Mục đích: bắt lỗi logic, gài–mở và nhịp mà gate máy (`check_script_logic.py`, `check_script_drama.py`) không đọc được, bằng agent **không thấy lập luận của người viết**. Người viết tự review thì thiên vị: đã thử trên than-trung, ba reviewer độc lập cùng chỉ ra hai lỗi mà gate không bắt (gán sai người nói ở S19, phép đếm khăn 31/32), xem `projects/than-trung-chiec-khan-tang-thu-32/script/review/REVIEW.md`.

## Khi nào
Sau khi `check_script_logic.py --strict` và `check_script_drama.py --strict` đã 0 lỗi, **trước khi chốt kịch bản và chạy TTS** (R1.5). Viết lại lớn thì review lại.

## Cách làm
1. Dựng gói cho từng lens (gói "mù": chỉ bible, setting/cast, lời thoại; không có `visual`, `goal`, ghi chú tác giả, khối `drama`):
   ```bash
   S=.agents/skills/video-pipeline/scripts/script_review.py
   python $S packet --project projects/<slug> --lens logic     --out <scratch>/packet_logic.md
   python $S packet --project projects/<slug> --lens loops     --out <scratch>/packet_loops.md
   python $S packet --project projects/<slug> --lens retention --out <scratch>/packet_retention.md
   ```
2. Mở **mỗi lens một agent mới** (subagent, hoặc agent khác như Codex/OpenCode), chỉ đưa đường dẫn gói và đường dẫn ghi `script/review/<lens>.json`. Không đưa kèm nhận định của bạn ("tôi nghĩ phần giữa ổn"), vì agent được đưa giả thuyết sẽ có xu hướng xác nhận nó.
3. Mỗi reviewer trả JSON đúng schema (xem gói): `findings[{severity,scene,line,category,issue,why,fix}]`, `extracted_loops` (setup/payoff reviewer tự dò), `not_checked`.
4. Gộp: `python $S merge --project projects/<slug>` → `script/review/REVIEW.md` (xếp must/should/nice, đánh dấu lỗi nhiều reviewer cùng thấy).
5. Lượt đối chiếu (tuỳ chọn): `packet --with-drama` để một reviewer so khối `drama` do tác giả khai với những gì lời thoại thật sự chứa (gate không đọc nghĩa nên không bắt được plant khai ở câu không có chi tiết đó).
6. Xử lý: **mọi `must` phải sửa hoặc ghi lý do không sửa** vào `PROJECT.md`; `should` quyết từng mục; `nice` tuỳ. Sửa trong `script.json`/`bible.json` (R1.3, R1.4), chạy lại hai gate, rồi nếu sửa lớn thì review lượt 2 bằng agent **khác lượt 1**.

## Ba lens
- `logic`: ai biết gì khi nào, động cơ đủ để hành động, mốc thời gian, đạo cụ/vị trí, luật siêu nhiên nhất quán, "ai cũng ngu cùng lúc". Ưu tiên phần giữa (nguồn: ConStory, arXiv 2603.05890, lỗi dồn ở giữa).
- `loops`: tự liệt kê setup/payoff; tìm setup không trả, payoff không có setup, tiết lộ sớm, twist thiếu manh mối công bằng.
- `retention`: hook 5 câu đầu, đoạn dễ thoát, cuối cảnh có kéo đi tiếp không, đường căng, midpoint, cú doạ lặp kiểu.

## Giới hạn (nói thật)
- Reviewer là LLM: có thể báo oan hoặc sót. Đã gặp: lỗi trùng giữa các reviewer là tín hiệu mạnh hơn lỗi chỉ một người thấy; mọi `must` vẫn cần người viết đọc lại câu được trích trước khi sửa.
- Reviewer không nghe được giọng đọc, không thấy hình: không đánh giá được nhịp thật sau TTS hay diễn xuất.
- Không thay người duyệt 👤. Review không đo được "hay"; đường giữ chân thật chỉ có sau khi đăng.
- Cùng một model review ra kết quả giống nhau nhiều hơn: nếu có agent khác hãng/khác model thì dùng cho lượt 2.
