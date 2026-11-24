# `script.json` — schema cho pipeline

File này là hợp đồng giữa bước viết kịch bản và bước đọc thoại. `voice-sync` đọc đúng các field dưới; field lạ bị bỏ qua nhưng đừng lạm dụng.

## Cấu trúc

```json
{
  "meta": {
    "project": "slug-project",
    "title": "Tựa video",
    "format": "9:16",
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "language": "vi"
  },
  "characters": [
    {
      "id": "host",
      "name": "Người dẫn",
      "role": "narrator",
      "voice": "Hải Đăng",
      "temperature": 0.8,
      "denoise": true
    }
  ],
  "scenes": [
    {
      "id": "S01",
      "title": "Hook",
      "goal": "khiến người xem dừng lại",
      "visual": "mô tả hình cho HyperFrames",
      "pause_after": 0.3,
      "lines": [
        {
          "id": "S01_L01",
          "speaker": "host",
          "text": "Lời thoại, có thể chèn [cười].",
          "delivery": "hào hứng, hơi nhanh",
          "emphasis": ["từ khoá"],
          "pause_after": 0.2,
          "on_screen": "Chữ ngắn hiện trên hình (tuỳ chọn)"
        }
      ]
    }
  ]
}
```

## Field

### `meta`
| Field | Bắt buộc | Ý nghĩa |
| --- | --- | --- |
| `project` | ✓ | slug, khớp tên thư mục |
| `title` | ✓ | tựa làm việc, dùng cho log và packaging |
| `format` | ✓ | `9:16` \| `16:9` \| `1:1` |
| `width`, `height` | – | suy ra từ `format` nếu thiếu |
| `fps` | – | mặc định 30 |
| `language` | – | mặc định `vi` |

### `characters[]`
| Field | Bắt buộc | Ý nghĩa |
| --- | --- | --- |
| `id` | ✓ | khoá để line tham chiếu, không dấu, không space |
| `name` | ✓ | tên hiển thị |
| `role` | – | `narrator` \| `guest` \| `character` |
| `voice` | ✓* | tên giọng preset của VieNeu (`Hải Đăng`, `Đoan Trang`, `Mai Anh`, `Ngọc Huyền`, `Thái Sơn`, `Mỹ Duyên`, ...). Alias cũ (`Minh Quân`, `Anh Khôi`, `Mạnh Dũng`) vẫn chạy nhưng tự đổi về tên chuẩn |
| `ref_audio` | ✓* | đường dẫn tương đối tới project cho clone giọng (3–8 s). Có `ref_audio` thì bỏ qua `voice` |
| `temperature` | – | 0.6–1.0; thấp = ổn định, cao = biểu cảm. Mặc định 0.8 |
| `speed` | – | tốc độ đọc riêng của nhân vật (atempo, 1.0–2.0; khuyến nghị 1.2–1.3). Thắng `--speed` chung của `build_voiceover.py`. Luật giọng hiện hành (Tuấn 23/11): giọng kể Đức Trí 1.3, nhân vật miền Bắc 1.2, miền Nam 1.0 |
| `denoise` | – | mặc định `true` cho `ref_audio` |

\* cần đúng một trong `voice` / `ref_audio`.

### `scenes[]`
| Field | Bắt buộc | Ý nghĩa |
| --- | --- | --- |
| `id` | ✓ | `S01`, `S02`, ... duy nhất |
| `title` | – | tên beat/chương |
| `goal` | – | mục tiêu cảm xúc của scene |
| `visual` | ✓ | mô tả chi tiết quang cảnh & hành động (xem mục Quy chuẩn Visual bên dưới) |
| `pause_after` | – | khoảng lặng sau scene (giây), mặc định 0.35 |
| `lines` | ✓ | ≥ 1 line |

#### Quy chuẩn trường `visual` (Bắt buộc 5 thành phần):
Mỗi `visual` phải là chuỗi mô tả rõ ràng (hoặc object JSON gồm các khóa):
- **`environment` (Quang cảnh):** Chất liệu tường/sàn, ô cửa mở ra đâu, các đạo cụ có mặt (bàn thờ, nến, cối, giường, bếp lửa...).
- **`framing` (Bố cục):** Toàn cảnh / trung cảnh / cận cảnh, vị trí ngồi/đứng của các nhân vật trong khung hình.
- **`action_rig` (Cử động):** Tay làm gì, mắt nhìn đâu, hướng quay mặt, nhịp thở, cử động giã/lật/chỉ.
- **`lighting` (Ánh sáng):** Nguồn sáng (nến, lửa, đèn dầu), hướng rọi sáng, thời điểm hạ tối / bóng ma trồi lên.
- **`sfx` (Âm thanh đi kèm):** Cues tiếng động (tiếng cối giã, tiếng sột soạt lật vải, gió hú, sub-bass stinger).

### `lines[]`
| Field | Bắt buộc | Ý nghĩa |
| --- | --- | --- |
| `id` | ✓ | duy nhất toàn file, quy ước `S01_L01` |
| `speaker` | ✓ | `characters[].id` |
| `text` | ✓ | lời thoại tiếng Việt, có thể chứa tag cảm xúc |
| `delivery` | – | ghi chú diễn xuất cho người đọc/duyệt, TTS bỏ qua |
| `emphasis` | – | từ khoá cần nhấn trên hình/caption |
| `pause_after` | – | khoảng lặng sau line (giây), mặc định 0.18 |
| `speed` | – | tốc độ đọc riêng của line (atempo, 1.0–2.0). Thắng `speed` của nhân vật |
| `on_screen` | – | chữ hiển thị thay cho caption nếu khác lời đọc |

## Luật kiểm

`build_voiceover.py` từ chối chạy nếu:
- `scenes` rỗng; scene không có `lines`; line id trùng.
- `speaker` không có trong `characters`.
- line rỗng hoặc chỉ có tag cảm xúc.
- character không có `voice` lẫn `ref_audio`, hoặc `ref_audio` không tồn tại.

Cảnh báo (không chặn):
- line > 25 từ → nên cắt.
- scene > 25 line → nên chia beat.
- text chứa ký tự dễ đọc sai: `%`, `&`, `+`, `=`, `/`, `#`, viết tắt tiếng Anh.

## Quy ước đặt id

- Scene: `S01`, `S02`, ...
- Line: `S01_L01`, `S01_L02`, ...
- Không đổi id sau khi đã dựng HyperFrames; đổi id = đổi `data-start`/caption ref. Nếu buộc phải đổi, chạy lại `build_voiceover.py` + `check_sync.py`.
