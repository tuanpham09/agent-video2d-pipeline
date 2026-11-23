# Detector baseline — số đo ngưỡng trên file thật (Opt round 3, mục 2)

Ngưỡng mặc định trong `detect_issues.py`:
`blackdetect d=2.0 pic_th=0.98 pix_th=0.10`, `freezedetect n=0.001 d=2.0`,
`silencedetect n=-50dB d=2.0`. Đổi ngưỡng thì cập nhật file này + ghi lý do.

## Demo #3 final (29,43s, 1920×1080, 23/11)

| Detector | Kết quả |
|---|---|
| blackdetect | 0 cờ — SH003 macro tối có chủ ý KHÔNG bị cờ (tối chứ không đen thuần) |
| freezedetect | 0 cờ |
| silencedetect | 0 cờ |

## Thần Trùng full (34:01, 2040,73s, 1280×720, 23/11, chạy 2m08s)

Video này đã qua QC mắt người (PASS) nên mọi cờ trên nó đều là báo động giả
hoặc cảnh tối có chủ ý — dùng để đo tỉ lệ báo động giả, không phải để bắt bug.

| Detector | Số cờ | Phân tích |
|---|---|---|
| blackdetect | 1 (1453,49–1456,62s, 3,13s) | Cảnh tối có chủ ý: frame ở 1455s mean luma 19,6, max 255 (có điểm sáng — không phải đen toàn bộ). Cần map shot + `dark_ok` để miễn. |
| freezedetect | 98 (2,0–4,7s, TB 2,67s; ≥4s: 6 cờ, dài nhất 4,7s) | **Báo động giả hàng loạt.** Phong cách 2D này có nhiều đoạn tĩnh thật 2–4s (cảnh SVG đứng yên, không tween) — video QC-pass vẫn bị cờ 98 lần. Ngưỡng d=2,0/n=0,001 KHÔNG dùng được để fail build; vòng này detector chỉ REPORT. Muốn bớt ồn: `--freeze-d 5` → 0 cờ trên video này, nhưng sẽ bỏ lọt stall ngắn (shot chỉ 2–6s). Hướng đúng cho vòng sau: freeze theo shot — chỉ cờ khi cả cửa sổ shot đứng yên mà shot đó có beat/move. |
| silencedetect | 1 (2037,95–2040,73s, 2,78s) | Đuôi video: giọng hết trước khi hình hết ~2,8s — bình thường. Detector đã miễn đuôi câm (end ≥ duration − 0,5s). |

**Lưu ý về map shot:** 99/100 cờ trên bản full có `shots: []` — KHÔNG phải lỗi
detector: project `than-trung-chiec-khan-tang-thu-32` trong repo chỉ có
manifest/shotlist của S01 (13 shot, 46,3s), còn bản full 34 phút được dựng bằng
pipeline beat riêng, không có manifest/shotlist khớp. Map shot chỉ có ý nghĩa
khi video được dựng bằng pipeline này (demo #3/#4). Muốn đo tỉ lệ báo động
giả có map shot thì chạy detector trên demo #4 final.

## Kiểm chứng âm tính (file tổng hợp từ demo #3 final, 23/11)

| File giả | Detector phải cờ |
|---|---|
| đen 10–13s (drawbox) | đen 10,00–13,03s → SH003, SH004 ✓ (kèm cờ đứng hình — frame đen giống hệt nhau, đúng bản chất) |
| câm 10–13s (volume=0) | câm 9,75–13,01s → SH003, SH004 ✓ |
| đứng hình 10–13s (trim+loop 1 frame) | đứng hình 10,00–13,00s → SH003, SH004 ✓ |

## Bẫy đã gặp khi làm detector

- Log ffmpeg KHÔNG có khoảng trắng sau dấu hai chấm ở blackdetect
  (`black_start:10`), còn silencedetect thì có (`silence_start: 9.75`) và dùng
  dấu `|` trước duration. Regex đầu tiên giả định 1 dòng + khoảng trắng đều
  → miss hết cả 3 file giả. Parse start/end/duration riêng rồi ghép theo thứ
  tự mới đúng.
- Tổng hợp file đứng hình bằng `select` chỉ DROP frame (thành jump-cut, không
  phải freeze). Muốn freeze thật: `trim` 1 frame + `loop` + `concat`.
