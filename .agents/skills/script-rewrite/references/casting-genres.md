# Preset giọng theo thể loại

Chọn thể loại → lấy cast + tốc độ bên dưới → đo lại bằng `--dry-run` trước khi đọc thật.
Mọi con số giọng (F0, từ/giây) lấy từ bộ mẫu `test/audio/` (vieneu 3.8.4, mỗi giọng một lần
đọc, temperature 0.8). Tai người vẫn là trọng tài cuối.

## Bảng nhanh

| Thể loại | Người kể | Nhân vật | Tốc độ | Ghi chú |
| --- | --- | --- | --- | --- |
| **Truyện ma / kinh dị** | **`Đức Trí` (luôn dùng)**, `Thiền Tâm Đức` (phương án phụ) | `Xuân Vĩnh`, `Adam` (vai ma) | **1.3** | Chốt 11/2026 — xem mục dưới, 4 giọng rất gần quãng |
| **Đời sống gay cấn / gây tò mò** | **`Hải Đăng` (đề xuất)**, `Thiện Minh` (tông lạnh) | `Ngọc Huyền`, `Thùy Dung`, `Quang Sơn` | **1.3** | Demo + số đo: `test/audio/doi-song/NGHE-THU.md` |
| Kể chuyện đời thường / documentary | `Thiện Minh`, `Thái Sơn`, `Thanh Bình` | `Ngọc Huyền`, `Thục Đoan`, `Quang Sơn` | 1.2–1.25 | Ưu tiên khác vùng cho nhân vật |
| Explainer / short công nghệ | `Hải Đăng`, `Quốc Tuấn` | `Trúc Ly`, `Thùy Dung` | 1.25 | Nhịp nhanh, câu ≤ 12 từ |
| Tài liệu / video dài | `Minh Đức`, `Đoan Trang` | `Ngọc Linh`, `Thái Sơn` | 1.2 | Ưu tiên rõ chữ hơn cảm xúc |
| Audiobook / đọc truyện | `Kim Thanh`, `Đức Trí`, `Mỹ Duyên` | `Quỳnh Anh`, `Thục Đoan` | 1.2–1.3 | Model đọc gốc đã chậm, đừng đẩy 1.3 nếu nghe lê |
| Hài / meme | `Adam bựa` | `Trúc Ly`, `Quốc Tuấn` | 1.25–1.3 | Không dùng `Adam bựa` làm narrator nghiêm túc |

Ngân sách từ: đừng tin bảng 90–150 từ/45–60 s. Model đọc nhanh hơn dự tính — luôn chốt bằng
`duration` trong `manifest.json` sau `--dry-run`.

## Truyện ma / kinh dị

**Cast đã chốt (11/2026):**

```json
"characters": [
  { "id": "narrator", "name": "Người kể", "role": "narrator", "voice": "Đức Trí", "temperature": 0.75 },
  { "id": "ong_tu",   "name": "Ông Tư",   "role": "character", "voice": "Xuân Vĩnh",     "temperature": 0.75 }
]
```

```bash
--speed 1.3
```

**Vì sao chốt `Đức Trí`:** đã nghe thử 4 bản render cùng một kịch bản 141 từ và chọn bằng tai —
`Đức Trí` @1.3 hay nhất cho truyện ma (**11/2026**). Số đo khớp với lựa chọn đó: 4,01 từ/giây,
chậm vừa, đủ khoảng thở, giữ được không khí mà không lê.

| Giọng | F0 | Từ/giây gốc | Từ/giây @1.3 | Vai |
| --- | --- | --- | --- | --- |
| `Đức Trí` | 100,9 Hz | 2,89 | **4,01** | **Người kể — luôn dùng**, mọi độ dài video |
| `Thiền Tâm Đức` | 99,7 Hz | 2,98 | 3,94 | Phương án phụ khi cần chậm/tĩnh hơn; cũng được chọn khi nghe thử |
| `Thiện Minh` | 108,8 Hz | 4,28 | 5,52 | Chỉ hook 10–15 s / cao trào; dẫn cả bài sẽ hụt không khí |
| `Xuân Vĩnh` | 109,7 Hz | 4,06 | ~5,3 | Nhân vật nam trầm ấm (ông Tư, người lạ, giọng nói trong nhà) |

Cùng một kịch bản 141 từ: `Đức Trí` @1.3 ra **36,8 s**, `Thiền Tâm Đức` **37,2 s**,
`Thiện Minh` **31,4 s**. Nếu target 45–60 s mà dùng Thiện Minh, phải viết dài hơn ~40% hoặc
hạ speed.

**Cảnh báo trùng giọng:** bốn giọng trên nằm trong 99–110 Hz. `Thiện Minh` ↔ `Xuân Vĩnh`
lệch **0,1 st** — đối thoại so le sẽ không phân biệt được ai nói. Cách xử lý:

1. Mỗi lượt thoại ≥ 2 câu, có tag dẫn trong caption ("Ông Tư nói…").
2. Hậu kỳ giọng nhân vật: reverb ngắn + hạ 1–2 dB + low-pass nhẹ.
3. Cần tách rõ tuyệt đối: narrator lệch quãng hơn (`Minh Đức` 161 Hz, lệch 6,5 st) hoặc
   `Adam` (93 Hz) cho vai ma.

**Giới hạn pipeline:** `build_voiceover.py` chỉ có **một** `--speed` cho mọi line. Ở 1.3,
nhân vật `Xuân Vĩnh` đọc ~5,3 từ/giây — nhanh hơn người kể. Muốn nhân vật chậm hơn kiểu rùng
rợn: render riêng line nhân vật ở 1.15 rồi ghép, hoặc thêm `speed` theo nhân vật vào
`build_voiceover.py`.

## Đời sống gay cấn / gây tò mò

Thể loại: chuyện đời thực, tình huống căng, kết mở; nhịp nhanh hơn documentary nhưng không
giật gân kiểu truyện ma.

**Cast đề xuất (11/2026, chờ nghe chốt):**

```json
"characters": [
  { "id": "narrator", "name": "Người kể", "role": "narrator", "voice": "Hải Đăng", "temperature": 0.75 }
]
```

```bash
--speed 1.3
```

| Giọng | Tổng (163 từ) | Từ/giây | F0 | Nhấp nhô | Vai |
| --- | --- | --- | --- | --- | --- |
| `Hải Đăng` | 34,3 s | 4,76 | 154 Hz | 8,8 st | **Đề xuất chính** — tự nhiên, đời thường, đáng tin |
| `Thiện Minh` | 35,5 s | 4,59 | 111 Hz | 9,2 st | Tông lạnh/điện ảnh; cách `Đức Trí` chỉ 1,7 st |
| `Thanh Bình` | 34,7 s | 4,70 | 177 Hz | 9,3 st | Documentary, biểu cảm rộng, lặng 39% |
| `Minh Triết` | 34,1 s | 4,78 | 150 Hz | 6,9 st | Tin tức, đáng tin nhưng phẳng |
| `Quốc Tuấn` | 34,9 s | 4,67 | 157 Hz | 9,0 st | Short 30–45 s, dồn dập |
| `Ngọc Linh` | 37,0 s | 4,41 | 201 Hz | 7,1 st | Phương án nữ |

**Vì sao `Hải Đăng`:** thể này cần giọng đời thường chứ không phải giọng đọc truyện. `Hải Đăng`
tự nhiên, nhịp nhanh (4,76 từ/giây), vẫn đủ nhấp nhô (8,8 st) để câu ngắn có sức nặng; và cách
giọng kể ma `Đức Trí` **7,3 st** nên hai thể loại không lẫn chất giọng trên cùng kênh.

**Cảnh báo:** nếu người kể là `Hải Đăng`, đừng chọn `Minh Đức` (161 Hz) hay `Quốc Tuấn`
(157 Hz) làm giọng nhân vật — lệch dưới 2 st. Dùng `Ngọc Huyền` (216 Hz), `Thùy Dung`
(210 Hz) hoặc `Quang Sơn` (139 Hz, miền Trung).

Bản render đầy đủ 6 giọng + reel 3:35: `test/audio/doi-song/NGHE-THU.md`.

## Quy tắc chọn nhiều giọng

- Short: tối đa 3 giọng. Long-form: tối đa 4.
- Cùng giới + cùng vùng: cần lệch **≥ 4–5 st** mới đủ tách. Dưới 3 st gần như không phân biệt.
- Cặp đo được là dễ lẫn: `Hải Đăng` ↔ `Minh Đức` ↔ `Quốc Tuấn`; `Trúc Ly` ↔ `Đoan Trang`;
  `Thiện Minh` ↔ `Phạm Tuyên` ↔ `Xuân Vĩnh`.
- Ưu tiên khác **giới** trước, rồi khác **vùng**, cuối cùng mới khác phong cách.

## Khi nào cập nhật file này

Đổi giọng/ tốc độ sau khi nghe thử → ghi lại số đo mới và ngày đo. Bộ mẫu đầy đủ:
`test/audio/CHON-GIONG.md` (25 giọng, reel 1.0× và 1.25×), `test/audio/truyen-ma/NGHE-THU.md`
(4 bản truyện ma ở 1.3×), `test/audio/doi-song/NGHE-THU.md` (6 giọng đời sống gay cấn ở 1.3×).
