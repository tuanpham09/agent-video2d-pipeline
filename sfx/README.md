# SFX Audio Library — Kho Hiệu Ứng Âm Thanh

Kho SFX chất lượng cao (357 file audio) gồm âm thanh tiêu chuẩn 48kHz WAV chuẩn phòng thu (CC0 Public Domain) và bộ Meme / Reaction audio phổ biến nhất cho YouTube & TikTok.

Tất cả đã được phân loại theo cấu trúc chuyên nghiệp, tự động lập chỉ mục tại [`catalog.json`](file:///d:/video_youtube/sfx/catalog.json).

---

## 1. Cấu trúc & Số lượng (357 file)

| Phân mục | Số lượng | Chi tiết âm thanh |
| :--- | :--- | :--- |
| [`transitions/`](file:///d:/video_youtube/sfx/transitions) | 78 WAV | `whooshes` (fast, medium, slow, hard, soft), `reverse-whooshes`, `swipes`, `swishes-and-zips`, `appear-and-vanish`, `bounce-spin-zoom`, `shape-changes` (grow, shrink, morph) |
| [`ui_clicks/`](file:///d:/video_youtube/sfx/ui_clicks) | 120 WAV | `interface` (chuột click, toggle, nút bấm), `keyboard` (gõ phím nhanh/cơ), `notifications` (chime, chuông, message-in/out), `pops` (bóng nổ, bubble), `phone`, `writing-and-drawing` |
| [`impacts_hits/`](file:///d:/video_youtube/sfx/impacts_hits) | 48 WAV | `cinematic-hits` (trailer hit, brass hit, heavy hit), `booms-and-bass` (808 sub drop, bass rumble), `impacts` (va chạm, đấm punch, kim loại, gỗ) |
| [`risers_tension/`](file:///d:/video_youtube/sfx/risers_tension) | 39 WAV | `risers-and-fallers` (sweep đẩy cao trào), `shimmers`, `tones` (tension pad/drone rùng rợn, hồi hộp), `time` (đồng hồ tick-tock, đếm ngược) |
| [`ambience/`](file:///d:/video_youtube/sfx/ambience) | 27 WAV | `data` (glitch số, tính toán, beep máy tính), `foley` (sột soạt, bước chân), `everyday-props` (chìa khóa, mở cửa, cốc), `mechanical` |
| [`meme_funny/`](file:///d:/video_youtube/sfx/meme_funny) | 45 audio | **Viral meme SFX**: `vine-boom`, `record-scratch`, `wrong-buzzer`, `sad-trombone`, `crickets`, `air-horn`, `bruh`, `ding`, `rimshot`, `minecraft-oof`, `windows-error`, `windows-startup`, `wow`, `yeet`, v.v.<br>**Stingers**: `celebration` (tiếng vỗ tay lớn/nhỏ, pháo hoa), `money` (máy đếm tiền, keng tiền xu), `logo-stings` |

---

## 2. Tiêu chuẩn âm thanh
- **WAV:** 48 kHz, 24-bit PCM (khớp hoàn hảo với sample rate 48kHz của `VieNeu-TTS` và timeline của `HyperFrames`).
- **Loudness:** Được chuẩn hóa âm lượng đồng đều (loudness-matched), không lo clip này quá to hay quá nhỏ.
- **Bản quyền:** CC0 Public Domain & Viral Creator Assets — hoàn toàn an toàn khi đăng lên YouTube / TikTok / Facebook Reels.

---

## 3. Cách sử dụng khi làm video

### Khi viết kịch bản (`script.json`):
Trong trường `visual` của kịch bản (theo chuẩn 5 thành phần của `AGENTS.md`), bạn có thể chỉ định rõ hiệu ứng SFX muốn chèn:
```json
{
  "id": "scene_01",
  "visual": "Bối cảnh văn phòng đêm... SFX: ui_clicks/keyboard/keyboard-type-fast.wav + meme_funny/vine-boom.mp3 khi hiện lỗi",
  ...
}
```

### Đưa vào project HyperFrames:
Khi project được tạo tại `projects/<slug>/`:
- Sao chép file SFX cần dùng vào thư mục `projects/<slug>/assets/sfx/`.
- Khi bạn thêm audio vào thư mục này, chỉ cần chạy lệnh `python update_catalog.py` để cập nhật lại danh mục tự động.
