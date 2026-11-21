# library/ — kho dùng chung cho mọi project

Nhân vật (khuôn người + trang phục), đạo cụ, bối cảnh và bảng màu làm **một lần**, dùng cho mọi video sau.
Luật: `RULES.md` mục **R2** (tra trước → dùng lại bằng `use` → sửa tại nguồn → làm mới thì đạt chuẩn rồi `promote`).

```
library/
  index.json            registry: id, file, trạng thái, tag, anchor/slot/part, scene_s, version, sha256
  palettes/             base.json (token dùng chung) · folk-horror-vn.json (đồ tang, áo the, bóng ma…)
  rigs/archetypes.json  khuôn người (adult_m/f, elder_m/f, teen, child, spirit_shadow) + trang phục (outfit)
  props/<id>.svg        đạo cụ, trạng thái bằng data-state
  locations/<id>.svg    bối cảnh 1920×1080, 3 lớp, ánh sáng bằng data-light
  sheets/               ảnh contact sheet để duyệt bằng mắt (props.png, locations.png)
```

Công cụ: `.agents/skills/video-pipeline/scripts/library.py` (`list`, `show`, `use`, `lock-check`, `check`, `reindex`, `sheet`, `promote`).

## Đang có

| Loại | id |
| --- | --- |
| Archetype | `adult_m`, `adult_f`, `elder_m`, `elder_f`, `teen`, `child`, `spirit_shadow` |
| Outfit | `mourning`, `ao_the_indigo`, `nau_song`, `plain_light` |
| Đạo cụ | `candle`, `oil_lamp`, `incense_burner`, `ancestral_altar`, `clay_jar`, `betel_mortar`, `bamboo_bed`, `bamboo_tray`, `mourning_cloth`, `smartphone` |
| Bối cảnh | `house_altar_room`, `village_yard_night`, `veranda_night` |
| Palette | `base`, `folk-horror-vn` |

`teen` và `child` (đầu to qua `head_scale`) đã dựng thử và nhìn ổn trong lineup, nhưng chưa có pose sheet nào được người dùng duyệt; xem lại khi dùng lần đầu. 5 nhân vật chính của project mẫu có pose sheet ở `projects/than-trung-chiec-khan-tang-thu-32/assets/rig/sheets/`.

## Cách dùng trong một project

```bash
L=.agents/skills/video-pipeline/scripts/library.py
python $L list --tag altar                    # 1. tra
python $L show ancestral_altar                # 2. xem slot/pivot/scene_s
# 3. gán vào script/bible.json: nhân vật rig.archetype + rig.outfit; bối cảnh/đạo cụ có "lib": "<id>"
python $L use --project <slug> ancestral_altar candle house_altar_room   # 4. chốt phiên bản
python .agents/skills/video-pipeline/scripts/build_rig.py --bible projects/<slug>/script/bible.json --out projects/<slug>/assets/rig
python .agents/skills/video-pipeline/scripts/check_rules.py --project projects/<slug>
```

## Quy ước ghép cảnh

- **Bối cảnh** `1920×1080`. `stand.L|C|R` = chỗ chân nhân vật `{x, y, s}`; `slots` = chỗ đặt đạo cụ; `crop_9x16` = tâm cửa sổ 608×1080 cho video dọc.
- **Nhân vật** (rig 520×600, chân ở `(260,580)`): nhúng bằng `<svg x="X-260·s" y="Y-580·s" width="520·s" height="600·s" viewBox="0 0 520 600">…` — **luôn là `<svg>` lồng nhau** vì pivot tay dùng `transform-box: view-box` (RULES R3.4).
- **Đạo cụ** gốc toạ độ giữa-đáy: `<svg x="X-W·k/2" y="Y-H·k" width="W·k" height="H·k" viewBox="0 0 W H">` với `k = scene_s` (hoặc tuỳ cận cảnh). Đạo cụ con của prop cha (nến trên bàn thờ) đặt theo `slots` của cha, nhân theo tỉ lệ của cha.
- **Màu**: asset chỉ dùng `var(--pal-<token>)`. Cảnh/file nhúng phải khai báo các biến này (từ palette của project); `library.py use` nhúng sẵn `<style data-palette>` vào bản chép trong project.
- **Trạng thái**: đổi `data-state` (đạo cụ), `data-light` (bối cảnh) hoặc `data-emotion|mouth|pose|stance|gaze|blink|khan` (rig). Phần động (`parts` trong index: ngọn lửa, khói, chày, vải…) có pivot ghi sẵn.

## Thêm / sửa asset

- **Thêm** (asset mới, dùng lại được): làm đúng chuẩn dưới đây → `library.py promote ...` → `library.py sheet` → xem ảnh → commit `library/`.
- **Sửa** asset đang có: sửa file trong `library/`, chỉ được *thêm* state/part/slot/anchor (không đổi tên/xoá); `reindex` (tự tăng version) → `check` → `sheet`. Project cũ vẫn dùng bản đã khoá cho đến khi `use` lại.
- **Chuẩn file** (`library.py check` kiểm): một SVG tự chứa; `data-lib-id` + `data-lib-kind` ở thẻ `<svg>`; không hex/rgb/tên màu; không `<text>`, `<script>`, ảnh/URL ngoài; `id` nội bộ có tiền tố riêng; state trong CSS = state trong index; mỗi `part` có class tương ứng; bối cảnh có `layer-far/mid/near`; mọi anchor nằm trong khung.
