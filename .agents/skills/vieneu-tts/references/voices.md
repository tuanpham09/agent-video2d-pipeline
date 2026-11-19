# Danh mục giọng VieNeu-TTS v3 Turbo (vieneu 3.8.4)

`vieneu.list_preset_voices()` trả **25 giọng chuẩn**. Tên cũ được giữ làm alias
(`Minh Quân` → `Hải Đăng`) nên kịch bản cũ vẫn chạy, nhưng nên viết tên chuẩn.

- **Giọng mặc định:** `Hải Đăng` (nam, Bắc, tự nhiên).
- **⭐ = editors' pick** (10 giọng đầu, do model đánh dấu `featured`) — không phải "tốt hơn",
  chỉ là thứ tự gợi ý của tác giả model.
- **Bản 3.8 đổi tên:** `Minh Quân` → `Hải Đăng`; `Anh Khôi` → `Thiện Minh`;
  `Mạnh Dũng` → `Quốc Tuấn`. `Phương Linh` **bị bỏ** (không alias) → dùng `Đoan Trang`,
  `Ngọc Huyền` hoặc `Trúc Ly`.

Kiểm tra lại bất cứ lúc nào (script tự đọc đúng bản đang cài):

```bash
python .agents/skills/vieneu-tts/scripts/list_voices.py              # bảng nhóm theo vùng/giới/phong cách
python .agents/skills/vieneu-tts/scripts/list_voices.py --recommended
python .agents/skills/vieneu-tts/scripts/list_voices.py --json       # cho agent đọc, có alias + default
python .agents/skills/vieneu-tts/scripts/list_voices.py --markdown   # dán vào docs
```

## ⭐ Nhóm gợi ý (featured 1–10)

| # | Voice | Vùng | Giới | Phong cách | Dùng khi |
| --- | --- | --- | --- | --- | --- |
| 1 | `Adam bựa` | Bắc | Nam | Tự nhiên | Hài, meme, nội dung giải trí — không dùng cho tin cậy |
| 2 | `Trúc Ly` | Bắc | Nữ | Tự nhiên | Shorts, nội dung trẻ, giọng nữ nhẹ |
| 3 | `Thiện Minh` | Bắc | Nam | Kể chuyện | Storytelling, nội dung cảm xúc vừa (alias `Anh Khôi`) |
| 4 | `Mai Anh` | Bắc | Nữ | Tin tức | Bản tin, nội dung dứt khoát, nhịp nhanh |
| 5 | `Hải Đăng` | Bắc | Nam | Tự nhiên | **Mặc định**; podcast, explainer, review (alias `Minh Quân`) |
| 6 | `Thùy Dung` | Nam | Nữ | Tin tức | Bản tin, điểm tin, giọng nữ miền Nam |
| 7 | `Thiền Tâm Đức` | Bắc | Nam | Kể chuyện | Thiền, nội dung chậm và tĩnh |
| 8 | `Ngọc Huyền` | Bắc | Nữ | Tự nhiên | Kể chuyện nhẹ, hướng dẫn, review |
| 9 | `Quang Sơn` | Trung | Nam | Tự nhiên | Nhân vật miền Trung, phóng sự địa phương |
| 10 | `Ngọc Trân` | Trung | Nữ | Tự nhiên | Nhân vật nữ miền Trung |

## Miền Bắc — Nam (9)

| Voice | Phong cách | Dùng khi |
| --- | --- | --- |
| `Hải Đăng` | Tự nhiên | Mặc định; podcast, explainer |
| `Minh Đức` | Tin tức | Bản tin, nội dung trung tính, trang trọng |
| `Phạm Tuyên` | Tự nhiên | Giải thích, review, giọng gần gũi |
| `Quốc Tuấn` | Tự nhiên | Shorts, nội dung nhanh (alias `Mạnh Dũng`) |
| `Xuân Vĩnh` | Tự nhiên | Kể chuyện nhẹ, điểm tin; **truyện ma — giọng nhân vật nam trầm ấm** |
| `Thanh Bình` | Kể chuyện | Documentary, kể chuyện có nhịp |
| `Thiện Minh` | Kể chuyện | Storytelling cảm xúc vừa; truyện ma — hook/cao trào |
| `Thiền Tâm Đức` | Kể chuyện | Thiền, chậm, nội dung tĩnh; truyện ma — phương án phụ ở 1.3× |
| `Adam bựa` | Tự nhiên | Giọng vui, hài — dùng có chủ đích |

## Miền Bắc — Nữ (6)

| Voice | Phong cách | Dùng khi |
| --- | --- | --- |
| `Đoan Trang` | Tự nhiên | Mặc định nữ; KOC review, giọng ấm, đáng tin |
| `Ngọc Huyền` | Tự nhiên | Kể chuyện nhẹ, hướng dẫn |
| `Trúc Ly` | Tự nhiên | Shorts, nội dung trẻ |
| `Mai Anh` | Tin tức | Bản tin, nội dung nhanh, dứt khoát |
| `Ngọc Linh` | Kể chuyện | Storytelling, tài liệu |
| `Quỳnh Anh` | Đọc truyện | Audiobook, truyện dài, nội dung chữ nhiều |

## Miền Trung (2)

| Voice | Giới | Phong cách | Dùng khi |
| --- | --- | --- | --- |
| `Quang Sơn` | Nam | Tự nhiên | Nhân vật miền Trung, phóng sự địa phương |
| `Ngọc Trân` | Nữ | Tự nhiên | Nhân vật nữ miền Trung, kể chuyện nhẹ |

## Miền Nam — Nam (4)

| Voice | Phong cách | Dùng khi |
| --- | --- | --- |
| `Adam` | Tự nhiên | Giọng nam hiện đại, short, công nghệ |
| `Minh Triết` | Tin tức | Bản tin, nội dung cần độ tin cậy |
| `Thái Sơn` | Kể chuyện | Kể chuyện, documentary |
| `Đức Trí` | Đọc truyện | Truyện dài, nội dung trữ tình; truyện ma dài 8–15 phút |

## Miền Nam — Nữ (4)

| Voice | Phong cách | Dùng khi |
| --- | --- | --- |
| `Thùy Dung` | Tin tức | Bản tin, điểm tin |
| `Thục Đoan` | Kể chuyện | Storytelling, nội dung cảm xúc |
| `Kim Thanh` | Đọc truyện | Audiobook, truyện ngắn |
| `Mỹ Duyên` | Đọc truyện | Truyện, nội dung nhẹ nhàng |

## Chọn giọng theo mục đích

| Mục đích | Gợi ý |
| --- | --- |
| Short TikTok/Reels nam | `Hải Đăng`, `Quốc Tuấn`, `Adam` |
| Short TikTok/Reels nữ | `Trúc Ly`, `Mai Anh`, `Đoan Trang` |
| Explainer / video dài | `Hải Đăng`, `Đoan Trang`, `Minh Đức` |
| Kể chuyện / documentary | `Thanh Bình`, `Thiện Minh`, `Ngọc Linh`, `Thái Sơn` |
| Audiobook / đọc truyện | `Quỳnh Anh`, `Kim Thanh`, `Mỹ Duyên`, `Đức Trí` |
| Truyện ma / kinh dị | `Đức Trí` (kể chính, 1.3×), `Thiền Tâm Đức` (phụ), `Thiện Minh` (hook), `Xuân Vĩnh` (nhân vật) |
| Review / KOC | `Đoan Trang`, `Ngọc Huyền`, `Hải Đăng` |
| Hài / meme | `Adam bựa` (không dùng cho nội dung nghiêm túc) |
| Nhân vật miền Trung | `Quang Sơn`, `Ngọc Trân` |
| Nhân vật miền Nam | `Thái Sơn`, `Mỹ Duyên`, `Thùy Dung`, `Kim Thanh`, `Thục Đoan`, `Adam`, `Minh Triết`, `Đức Trí` |

## Nhiều nhân vật trong một video

- Hai giọng cùng vùng + cùng giới rất dễ lẫn. Khác vùng hoặc khác giới trước, rồi mới
  khác phong cách.
- Cặp an toàn: `Hải Đăng` (nam Bắc) + `Đoan Trang` (nữ Bắc); `Hải Đăng` + `Thùy Dung`
  (nữ Nam); `Thanh Bình` + `Ngọc Huyền`.
- Ba nhân vật trở lên: thêm `Quang Sơn`/`Ngọc Trân` (Trung) để tách kênh miền.

## Alias — dùng được nhưng đừng viết trong kịch bản mới

| Alias | Trỏ về |
| --- | --- |
| `Minh Quân`, `Minh Quân Pro` | `Hải Đăng` |
| `Anh Khôi` | `Thiện Minh` |
| `Mạnh Dũng` | `Quốc Tuấn` |

- `build_voiceover.py` tự đổi alias về tên chuẩn (in `[alias] host: 'Minh Quân' → 'Hải Đăng'`)
  trước khi đọc, nên cache và manifest luôn ổn định.
- Tên không có trong 25 giọng và không phải alias → `VoiceNotFound` kèm gợi ý gần giống.
