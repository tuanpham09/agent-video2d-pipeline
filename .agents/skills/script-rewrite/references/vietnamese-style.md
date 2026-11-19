# Viết tiếng Việt cho TTS (VieNeu-TTS v3 Turbo)

Mục tiêu: máy đọc đúng ngay lần đầu, người nghe hiểu ngay lần đầu. Mọi thứ dưới đây áp dụng cho `text` trong `script.json`.

## Câu và nhịp

- Một câu = một hơi thở. 10–18 từ là chuẩn; > 25 từ thì cắt.
- Dùng dấu phẩy để tạo nhịp thở ngắn, dấu chấm để kết ý. Không dùng dấu `;`, `—`, `...` liên tục.
- Tránh câu bị động nặng: "được thực hiện bởi" → "do ... làm".
- Tránh chuỗi danh từ: "quy trình tối ưu hoá hiệu suất vận hành hệ thống" → "cách làm hệ thống chạy nhanh hơn".
- Không viết hoa giữa câu để nhấn mạnh; TTS có thể đọc khác. Dùng tag cảm xúc hoặc tách câu.

## Số, ngày, tiền

| Viết trong script | Máy đọc |
| --- | --- |
| `1.200.000 đồng` | "một triệu hai trăm nghìn đồng" |
| `40%` | "bốn mươi phần trăm" |
| `2026` | "hai nghìn không trăm hai mươi sáu" (năm) |
| `3-5 ngày` | viết `3 đến 5 ngày` |
| `2x` | viết `gấp đôi` |
| `1/3` | viết `một phần ba` |

Quy tắc: **viết số bằng chữ khi số đó quan trọng cho việc nghe**, giữ số khi đó là dữ liệu để nhìn trên hình. Nếu line vừa đọc vừa hiện số, đặt số thật vào `on_screen` và số bằng chữ vào `text`.

## Đơn vị và ký hiệu

- `km/h` → `ki-lô-mét trên giờ`; `GB` → `gi-ga-bai`; `MB` → `mê-ga-bai`; `TB` → `tê-ra-bai`.
- `$100` → `một trăm đô-la`; `€` → `ơ-rô`; `¥` → `yên`.
- `+`, `&`, `=`, `/`, `#`, `@` không bao giờ để trong `text`; viết thành "cộng", "và", "bằng", "trên", "thăng", "a-còng".
- `AI`, `API`, `GPU` đọc được như từ tiếng Anh — chấp nhận. Từ viết tắt lạ thì phiên âm.

## Tên riêng và từ tiếng Anh

- Tên thương hiệu quen: giữ nguyên (`Google`, `YouTube`, `TikTok`, `iPhone`).
- Tên khó đọc / ít gặp: phiên âm bằng tiếng Việt trong `text`, giữ tên gốc trong `on_screen`.
  - `ChatGPT` → `chát-gi-pi-ti`
  - `Nvidia` → `en-vi-đi-a`
  - `Claude` → `clót`
  - `GPT-5` → `gi-pi-ti năm`
- Tên người Việt: viết đủ dấu, đúng chính tả. Sai dấu = sai tên.
- Không dùng emoji trong `text`.

## Từ ngữ

- Ưu tiên từ người nói hằng ngày. Hán-Việt chỉ dùng khi đã quen: "trải nghiệm" ổn, "hệ quy chiếu" không.
- Đại từ nhất quán: "mình" (gần gũi) hoặc "tôi" (trang trọng) — không trộn trong một video.
- Xưng hô với người xem: "bạn" hoặc "mọi người", chọn một.
- Không dùng từ thô, chửi, miệt thị — kể cả khi bản gốc có.
- Tránh từ đa nghĩa khi nói: "pin" (battery) vs "pin" (ghim) → nói rõ "viên pin".

## Tag cảm xúc

- **Chỉ có 3 tag**: `[cười]`, `[thở dài]`, `[hắng giọng]`. Không có tag cho buồn, vui, ngạc
  nhiên, tức giận — viết `[ngạc nhiên]` thì TTS **đọc luôn chữ "ngạc nhiên"**.
- Chỉ dùng khi cảm xúc thật sự đổi hướng câu; 1 tag mỗi 4–5 câu là tối đa.
- Đặt sau chữ, trước dấu câu: `"… hay thật đấy [cười]."` Không đặt tag ở đầu câu hỏi tu từ,
  dễ thành giả.
- Cảm xúc khác tag → dùng câu ngắn + từ mang sắc thái + dấu câu (`?`, `!`, `…`), hoặc tách
  line để lấy khoảng lặng. Chi tiết: `/vieneu-tts` → `references/emotions.md`.
- Tag **không** xuất hiện trong caption/SRT — pipeline tự bỏ.

## Giọng vùng miền

- Giọng Bắc (`Hải Đăng`, `Đoan Trang`, `Ngọc Huyền`, `Mai Anh`): dùng từ chuẩn Bắc, tránh "dzậy", "hổng".
- Giọng Nam (`Thái Sơn`, `Mỹ Duyên`, `Thùy Dung`): có thể dùng "nè", "dzậy", "hông" ở mức vừa; viết đúng chính tả, để TTS tự nhấn giọng.
- Không trộn phương ngữ trong cùng một nhân vật.

## Câu dẫn hình (không đọc)

`visual` và `on_screen` là chữ cho hình, không đưa vào TTS:
- `on_screen` ≤ 8 từ, không dấu chấm cuối, không viết tắt.
- `visual` mô tả **hành động** của hình ("counter chạy từ 0 lên 40% rồi đóng dấu"), không mô tả cảm xúc ("đẹp, sang").
- Không lặp y nguyên lời đọc trong `on_screen`; hình phải cộng thêm thông tin.

## Checklist nhanh trước khi build voice

- [ ] Không còn `%`, `&`, `+`, `#`, `/`, `...`, emoji trong `text`.
- [ ] Số quan trọng đã viết bằng chữ.
- [ ] Tên riêng khó đọc đã phiên âm.
- [ ] Không câu nào > 25 từ.
- [ ] Tag cảm xúc ≤ 1 mỗi 4–5 câu.
- [ ] Đọc to 3 line đầu: không hụt hơi, không sai dấu.
