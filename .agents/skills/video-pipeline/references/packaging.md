# Đóng gói xuất bản (YouTube / TikTok)

Viết `output/publish.md` với đúng các mục dưới. Không bịa số liệu, không hứa điều video không làm.

## YouTube long-form

- **Title** ≤ 70 ký tự, từ khoá chính nằm trong 3 từ đầu, không ALL CAPS, không clickbait sai sự thật.
- **Thumbnail**: 1 ý, 2–4 từ chữ to, mặt/đối tượng rõ ở 1/3 trái, tương phản cao, đọc được ở 120 px. Ghi concept + prompt ảnh (nếu cần) vào `output/thumbnail.md`.
- **Description**:
  - 2 dòng đầu (≈150 ký tự) bán nội dung + từ khoá, vì phần còn lại bị cắt.
  - 1 đoạn tóm tắt 3–5 câu.
  - Chapters `00:00` theo đúng mốc scene trong manifest (chỉ khi ≥ 3 chương, mỗi chương ≥ 10 s).
  - Link nguồn tham khảo, credit nhạc/footage.
  - 3–5 hashtag cuối.
- **Tags**: 8–12 cụm, gồm biến thể người xem thật sự gõ.
- **End screen**: 1 CTA + 1 video kế tiếp, 15 s cuối.
- **Pinned comment**: 1 câu hỏi mở để kéo thảo luận.

## TikTok / Shorts / Reels

- **Hook 2 giây đầu**: chữ trên hình + lời nói phải khác nhau, không lặp.
- **Caption**: 125 ký tự đầu tự đứng một mình; 1 CTA duy nhất.
- **Hashtag**: 3–5, đúng chủ đề; không `#fyp #viral`.
- **Cover**: chọn khung có chữ hook đọc được, không để mặt bị cắt.
- **Âm thanh**: -14 LUFS, true peak ≤ -1 dBTP; thoại luôn trên nhạc 6–10 dB.
- **An toàn khung**: chữ nằm trong 80% title-safe; tránh 250 px trên (UI TikTok) và 320 px dưới (caption/CTA).

## Checklist trước khi giao

- [ ] Tên file `output/final.mp4` đúng format (1080×1920 hoặc 1920×1080), H.264 + AAC.
- [ ] Duration khớp manifest; `ffprobe` xác nhận.
- [ ] `publish.md` có title, description, hashtag, cover, CTA.
- [ ] `output/thumbnail.jpg/png` tồn tại nếu là YouTube.
- [ ] Không còn watermark, logo lạ, hay chữ tiếng Anh sót trong hình.
- [ ] Đã ghi 1 dòng "bài học" vào `PROJECT.md` (điều gì hiệu quả, điều gì phải làm lại).
