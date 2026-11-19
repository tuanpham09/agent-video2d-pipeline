# Tag cảm xúc của VieNeu-TTS v3 Turbo

Tài liệu này là **danh sách đầy đủ** các tag mà model thực sự hiểu — kiểm chứng trên
`vieneu` 3.2.3 đã cài trong máy, đối chiếu với source upstream
(`src/vieneu_utils/phonemize_text.py`) và model card Hugging Face.

## 1. Chỉ có 3 tag

| Tag tiếng Việt | Alias tiếng Anh | Alias không dấu | Token trong phoneme |
| --- | --- | --- | --- |
| `[cười]` | `[chuckle]` | `[cuoi]` | `<\|emotion_1\|>` |
| `[thở dài]` | `[sigh]` | `[tho dai]` | `<\|emotion_2\|>` |
| `[hắng giọng]` | `[clear throat]` | `[hang giong]` | `<\|emotion_3\|>` |

Đây là toàn bộ bảng map `_EMOTION_TAG_TO_K` trong phonemizer — **không có tag nào khác**.
Model card cũng ghi rõ đây là tính năng **EXPERIMENTAL**.

## 2. Tag lạ bị đọc thành chữ, không bị bỏ qua

Phonemizer chỉ thay token khi tag nằm trong bảng trên. Mọi `[...]` khác bị coi là chữ
thường: dấu ngoặc bị xoá và **nội dung được đọc lên**.

```
"Tôi [ngạc nhiên] không tin nổi."
  -> t̪ˈoj ŋˈaː6c ɲˈiɛn xˌoŋ tˈe4 tˈin nˈo4j.      # đọc "ngạc nhiên"
"Tôi [cười] không tin nổi."
  -> t̪ˈoj <|emotion_1|> xˌoŋ tˈe4 tˈin nˈo4j.       # tiếng cười chèn vào
```

Hệ quả: viết `[buồn]`, `[vui]`, `[hét]`, `[cười lớn]`, `[ngạc nhiên]`… là **lỗi nội dung**
— người nghe sẽ nghe thấy chính từ đó. `build_voiceover.py` cảnh báo các tag lạ trước khi
đọc (xem mục 6).

## 3. Vì sao chỉ có 3

Trong `configuration_v3_turbo.py` có 8 slot `emotion_0_token_id` … `emotion_7_token_id`
và tokenizer có đủ `<|emotion_0|>` … `<|emotion_7|>`. Nhưng:

- `emotion_1..3` là 3 cue **phi ngôn ngữ** được train inline trong chuỗi phoneme.
- `emotion_0` là prefix "natural" của đường v2 (`base.py` / `remote.py` truyền qua tham số
  `emotion_tag`), **không** phải cue inline của v3 Turbo.
- `emotion_4..7` tồn tại trong vocab nhưng **không có cue nào map tới** và không được tài
  liệu hoá → coi như chưa dùng. Đừng đưa `<|emotion_4|>` vào script.

`<|emotion_k|>` viết thẳng trong text sẽ đi qua phonemizer nguyên vẹn, kể cả `k` không tồn
tại (khi đó tokenizer tách thành ký tự rác). Chỉ dùng `[...]`, đừng dùng token thô.

## 4. Không có tham số `emotion` hay `style` để điều khiển cảm xúc

- `Vieneu().infer(text, ...)` trên v3 Turbo **không** nhận `emotion`. Cảm xúc chỉ đến từ
  3 tag inline + cách viết câu.
- `style="tu_nhien" | "tin_tuc" | "doc_truyen"` vẫn còn trong chữ ký hàm nhưng model card
  ghi rõ **deprecated và bị bỏ qua** trên v3 Turbo: phong cách đọc đã nằm trong reference
  (preset voice hoặc clip clone). Chọn "chất giọng" bằng **voice**, không bằng `style`.

## 5. Cách đặt tag cho tự nhiên

- Đặt ở **ranh giới mệnh đề/câu**, sau chữ và trước dấu câu: `"… hay thật đấy [cười]."`
  Dấu câu đi liền token, giống dữ liệu train.
- Không đặt ở đầu câu trừ khi muốn cue xuất hiện trước khi nói (`"[thở dài] Mình đã thử rồi."`
  — dùng được, nhưng dễ thành kịch).
- Tối đa **1 tag mỗi 4–5 câu**. Nhiều hơn thì tiếng cười/thở dài thành tiếng đệm đều đặn,
  phản tác dụng.
- Tag chỉ nằm trong `text`; `on_screen` và SRT không bao giờ chứa tag (pipeline tự bỏ).

## 6. Cảnh báo tự động trong pipeline

`voice-sync/scripts/build_voiceover.py` quét mọi `[...]` trong `text` khi validate và thêm
warning dạng:

```
S01_L03: tag không hỗ trợ [ngạc nhiên] — VieNeu chỉ hiểu [cười] [thở dài] [hắng giọng],
từ này sẽ bị đọc thành chữ.
```

Warning xuất hiện ở cả `--dry-run` và lượt chạy thật. Thấy warning thì sửa `script.json`,
đừng chạy tiếp rồi hậu kỳ.

## 7. Khi cảm xúc không phải 1 trong 3

Không có tag cho buồn, tức giận, ngạc nhiên, hào hứng. Các cách thay thế, theo thứ tự hiệu quả:

1. **Đổi câu chữ**: câu ngắn + từ mang sắc thái ("Mình đã thử. Ba lần. Vẫn hỏng.").
2. **Dấu câu**: `?`, `!`, dấu ba chấm, gạch ngang — TTS dùng để lên/xuống giọng.
3. **Chọn giọng khác**: mỗi preset đã có "character" riêng (News / Natural / Storytelling)
   — xem [voices.md](voices.md).
4. **Temperature**: 0.8 ổn định; 0.85–0.95 biểu cảm hơn nhưng dễ lè nhè — đổi theo cả
   nhân vật trong `script.json`, không đổi giữa các câu của cùng nhân vật.
5. **Ngắt line**: tách một câu dài thành 2 line cùng speaker, chèn `pause_after` — khoảng
   lặng làm cảm xúc nặng hơn là tag.
