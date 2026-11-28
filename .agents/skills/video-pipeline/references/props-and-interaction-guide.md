# Hướng dẫn đạo cụ và tương tác nhân vật ↔ đạo cụ (cho agent dựng video)

Đọc cùng `shotlist-guide.md` (cấu trúc shot, beat, macro) và `craft-playbook.md` (cách *tạo* đạo cụ mới). File này chỉ nói về **dùng** đạo cụ trong shot. Luật gốc: R4.1–R4.3, R6.1, R11.5, R10.6. Mục nào đã chạy thật ghi **[đã kiểm]**, chưa chạy ghi **[chưa kiểm]**.

---

## 1. Nguyên tắc

1. **Dùng đạo cụ trong kho trước** (`library.py list --kind prop`, `library.py suggest --project <slug>`); thiếu mới tạo (R2.1, R2.4).
2. Trong `shotlist.json` đạo cụ gọi theo **id trong bible** (`nen`, `ban_tho`, `bat_huong`…), không phải id thư viện (`candle`, `ancestral_altar`…). Bible nối hai tên qua `lib`.
3. Đặt đạo cụ bằng anchor/slot (`"at": "ban_tho.candle-l"`, `"stand:L"` + `dx`/`dy`), không toạ độ tuỳ ý (R4.2). Hai đạo cụ cùng id phải khác `key`; beat gọi đạo cụ bằng `key` (`nen-r`).
4. **Trạng thái đạo cụ chỉ đổi bằng beat** (`set: {"prop:<key>": "<state>"}`), cùng một location giữ nguyên bố cục (R4.3).
5. **Đổi state là đổi tức thì, không có chuyển mờ** [đã kiểm: generator ghi `tl.set(... data-state ...)`]. Muốn cảm giác "lụi dần": đi qua state trung gian (`lit → low → out`) cách nhau 0,5–1 s, không nhảy thẳng.
6. Phần động trong một state (ngọn lửa, khói, glow) do CSS của asset tự chạy; agent không điều khiển riêng.

---

## 2. Danh mục đạo cụ trong kho (10 mục, đã xem `library/sheets/props.png`)

| id thư viện | State | Slot / phần động | Dùng vào việc gì |
| --- | --- | --- | --- |
| `candle` (nến) | `lit` · `low` · `out` | phần động: ngọn lửa, glow, khói. `out` có sợi khói | Thắp/lụi/tắt nến; ánh sáng ấm; điềm gở khi nến tự tắt |
| `oil_lamp` (đèn dầu) | `lit` · `low` · `out` | như nến. **Có điểm nắm `grip`** → cầm được | Đèn xách đi trong tối; tắt khi ma tới |
| `incense_burner` (bát hương) | `burning` · `spent` | khói | `burning` = đang thắp; `spent` = tàn |
| `ancestral_altar` (tủ thờ + di ảnh) | `normal` · `covered` · `blank` | **slot**: `candle-l`, `candle-r`, `incense` | Nền cho cảnh thờ; `covered` = phủ vải trắng; `blank` = di ảnh trống/tối (điềm lạ) |
| `clay_jar` (hũ sành) | `sealed` · `open` · `cracked` | vải bịt đỏ | Hũ nhốt/giấu thứ gì: bịt kín → bật nắp → nứt |
| `betel_mortar` (cối giã trầu) | `rest` · `raised` · `strike` | chày xoay quanh đáy chày; **đồng bộ SFX cối** | Giã trầu: `raised` rồi `strike` đúng nhịp tiếng đập |
| `bamboo_bed` (chõng tre) | `bare` · `mat` · `blanket` | không | Nơi nằm/ngủ; `blanket` = có người/chăn nằm |
| `bamboo_tray` (mâm tre) | `empty` · `cloths` · `scattered` | **có `grip`** (hai mép) → `hand_over` được | Mâm khăn xô/trầu cau; `scattered` = đồ rơi vãi |
| `mourning_cloth` (khăn tang) | `folded` · `spread` · `torn` | không | Khăn tang gấp / trải ra / rách |
| `smartphone` (điện thoại) | `off` · `ringing` · `call` · `ended` | glow | Cuộc gọi video: đổ chuông → nghe → kết thúc (không có chữ) |

Tra thông tin mới nhất: `python .agents/skills/video-pipeline/scripts/library.py show <id>` (state, slot, pivot, `scene_s`). Danh mục này chép từ `library/index.json` ngày 2026-11-26; nếu lệch, `index.json` thắng.

---

## 3. Đạo cụ trong một shot

```json
"props": [
  {"id": "ban_tho",  "state": "normal",  "at": "altar"},
  {"id": "nen",      "state": "lit",     "at": "ban_tho.candle-l"},
  {"id": "nen",      "state": "lit",     "at": "ban_tho.candle-r", "key": "nen-r"},
  {"id": "bat_huong","state": "burning", "at": "ban_tho.incense"},
  {"id": "mam_tre",  "state": "cloths",  "at": "stand:L", "dx": -260}
]
```
- Slot của bàn thờ: `ban_tho.candle-l`, `ban_tho.candle-r`, `ban_tho.incense`. Đạo cụ đặt vào slot đi theo bàn thờ.
- Chân người không được đè đạo cụ (gate E10). `focus: "prop:<id>"` hoặc `"slot:<tên>"` phải trỏ tới thứ có thật trong shot (E11).
- Cỡ cảnh `macro` + `kind: insert` + `focus: "prop:<id>"` là cách chuẩn để cho khán giả nhìn rõ đạo cụ (ví dụ SH003 mâm khăn).

---

## 4. Tương tác: nhân vật làm gì với đạo cụ

| Việc trong kịch bản | Cách làm | SFX (R6.1) |
| --- | --- | --- |
| Nến/đèn lụi, tắt, bát hương tàn | `set: {"prop:<key>": "low"}` rồi `"out"` (hoặc `spent`) ở đúng từ/giây; nhân vật phản ứng bằng `set` cảm xúc hoặc `macro giat_minh` cùng thời điểm | Nếu beat `physical: true` thì **phải** có SFX ±0,15 s |
| Điện thoại reo rồi nghe | `set: {"prop:dien_thoai": "ringing"}` → `"call"` → `"ended"` | `ui_clicks/phone/phone-ring-classic.wav` hoặc `phone-ring-modern.wav` |
| Chạm/nhấc khăn trên mâm | `macro cham_khan` (đã gồm SFX vải) | tự thêm |
| Với tay chạm một đạo cụ ở độ cao tay (bàn thờ, bàn) | `reach` tới `{"prop": "<key>"}` | foley (mục 5) |
| Đưa mâm/đèn cho người khác | `hand_over` (chỉ đạo cụ có `grip` bám tay đẹp: `bamboo_tray`, `oil_lamp`) | foley chạm gỗ/vải |
| Giã trầu | `betel_mortar`: `raised` → `strike`, mỗi `strike` một tiếng đập | `impacts_hits/impacts/impact-*.wav` hoặc tiếng kim loại; khớp ±0,15 s |
| Mở hũ, hũ nứt | `clay_jar`: `sealed` → `open` / `cracked` ở beat có phản ứng (giật mình) | `impact-*` nhẹ/nặng; chưa có tiếng vỡ gốm (mục 5) |
| Phủ vải di ảnh, di ảnh trống | `ban_tho`: `covered` / `blank` | foley vải; stinger nếu là cao trào |
| Người nằm trên chõng | đổi `bamboo_bed` sang `blanket` + nhân vật `stance: lie` | foley vải |

Hai ràng buộc để đạo cụ và người khớp nhau:
- Đổi state và phản ứng của người đặt **cùng một beat** (hoặc cách ≤ 0,3 s), không để nến tắt mà không ai phản ứng.
- Cao trào: đổi `light` + stinger + state đạo cụ cùng một thời điểm (`shotlist-guide.md` mục 4).

---

## 5. SFX cho đạo cụ: kho có gì, thiếu gì

Có sẵn (`sfx/`, tra danh sách đầy đủ ở `sfx/catalog.json`):
- Chạm/trượt: `ambience/foley/foley-{fabric,wood,paper,card,glass,plastic}-{touch,slide}.wav`
- Đồ vật: `ambience/everyday-props/props-{drip,splash,page-turn,book-close,box-open,zip,doorbell,shop-bell,scissors,tape}.wav`
- Điện thoại: `ui_clicks/phone/phone-ring-classic.wav`, `phone-ring-modern.wav`, `phone-keypad.wav`
- Va đập: `impacts_hits/impacts/impact-{light,medium,heavy,deep}-{soft,firm,hard}.wav`, `cinematic-hits/*`, `booms-and-bass/*`

**Không có** (đã tìm theo từ khoá): tiếng quẹt diêm/thổi nến/lửa, tiếng gốm vỡ, tiếng đồ gỗ nặng đổ. Dùng âm gần nhất và **ghi rõ trong báo cáo** đó là âm thay thế; không giả vờ đúng loại. Cần âm thật → báo người dùng.

**SFX mặc định theo đạo cụ:** mỗi đạo cụ trong `library/index.json` có trường `sfx` (`touch` = âm chạm khi `reach`/`hand_over`; `state.<tên>` = âm khi đổi sang state đó; `substitute: true` = âm thay thế, không đúng loại). Khi beat vật lý thiếu SFX, `check_shots` (E6) in sẵn dòng gợi ý `{"t": …, "src": "sfx/…"}` để dán vào `sfx[]`; **không tự thêm**, agent vẫn chọn/duyệt và ghi âm thay thế vào báo cáo.

---

## 6. Ví dụ đã chạy thật [đã kiểm: 2026-11-26]

Bản sao shot SH008 của project mẫu (không commit): mẹ với tay chạm cây nến phải, nến `lit → low → out`, chị đổi sang `afraid`:

```json
"characters": [{"id": "host", "at": "C", ...}, {"id": "me", "at": "L", ...}],
"beats": [
 {"line_id": "S01_L07", "t": 0.8, "physical": true, "do": "mẹ với tay tới cây nến phải",
  "reach": {"char": "me", "to": {"prop": "nen-r"}, "dur": 0.6, "hold": 1.4}},
 {"line_id": "S01_L07", "t": 1.5, "physical": true, "do": "nến lụi dần", "set": {"prop:nen-r": "low"}},
 {"line_id": "S01_L07", "t": 2.3, "physical": true, "do": "nến tắt",
  "set": {"prop:nen-r": "out", "host": {"emotion": "afraid"}}}
],
"sfx": [
 {"t": 0.9, "src": "sfx/ambience/foley/foley-fabric-touch.wav"},
 {"t": 1.5, "src": "sfx/ambience/foley/foley-paper-touch.wav"},
 {"t": 2.3, "src": "sfx/ambience/everyday-props/props-drip.wav"}
]
```
Kết quả: `check_shots` không báo lỗi cho shot; `build_video --shots SH008` dựng được; snapshot (0,5 / 1,3 / 2,0 / 3,0 s) thấy tay với tới nến, ngọn lửa nhỏ lại ở `low`, nến `out` có sợi khói.

Hai lỗi gặp khi thử, đừng lặp lại:
- Beat `physical: true` cho việc đổi state mà không có SFX → `check_shots` E6 ("chưa có SFX trong ±0.15s"). Mỗi beat vật lý một SFX.
- `reach` tới nến bàn thờ **trượt đích** khi người đứng ở `C` (166 px) hoặc `R` (444 px); chỉ đạt khi người đứng gần bàn thờ (`L` trong `loc_gian_tho`). Quy tắc: muốn chạm đạo cụ nào, **đặt người sát đạo cụ đó** từ đầu shot hoặc `move` lại gần trước; vị trí `at` còn quyết định trục hai người (R11.4), nên đổi chỗ thì cân nhắc đổi cả người kia.
- Hết `hold`, tay hạ xuống: đặt đổi state **trong** khoảng `t + dur … t + dur + hold`.

---

## 7. Chưa kiểm / chưa có (nói thẳng)

- **[đã kiểm trong mp4 draft 2026-11-26, 46 s, khung trích từ chính file mp4]** `smartphone` (`off → ringing → call`, đặt ở `stand:R` trên sàn; glow đổi rõ, nhân vật quay sang nhìn), `candle` (`lit → low → out` có khói), `reach` tới nến, `hand_over` mâm tre giữa hai người (xem `shotlist-guide.md` mục 3.4 về hai cách dùng đúng). Điện thoại nằm sàn nên nhân vật **không thể "bắt máy" bằng tay** (reach tới sàn trượt đích): chỉ diễn bằng nét mặt + state.
- **[chưa kiểm]** `clay_jar`, `betel_mortar`, `bamboo_bed`, `ancestral_altar` (`covered`/`blank`) chỉ xem ở `library/sheets/props.png`; chưa đặt vào shot thật hay render. `hand_over` đèn dầu chưa thử; điểm nắm `oil_lamp` chỉ ước lượng từ hình.
- **[chưa kiểm]** giọng đọc: bản dựng thử không có `audio/voiceover.wav` (file sinh, không commit) nên video chỉ có SFX; khớp SFX với hình ±0,15 s mới được kiểm bằng gate, chưa nghe.
- Không có chuyển mờ giữa các state, không có tween di chuyển đạo cụ (trừ `hand_over`); đạo cụ muốn "bay"/"rơi" cần mở rộng generator (R10.6), không vá riêng một video.
- `reach` chỉ với tới đích ở độ cao tay khi người đứng/ngồi nhìn thẳng (xem `shotlist-guide.md` mục 3.3, 7).
- `check_motion.py` chỉ kiểm thao tác tường minh từ beat (xem `shotlist-guide.md` mục 7), không thấy hiệu ứng đổi state đạo cụ ngoài việc đếm là "beat vật lý có prop".
- Chưa có đạo cụ cho: lửa/diêm, bát cơm cúng, hương nhang cầm tay, cuốc/xẻng, quan tài, dây/chuỗi. Cần thì tạo theo `craft-playbook.md` mục 3 rồi `promote`.

---

## 8. Quy trình ngắn khi shot có đạo cụ

1. `library.py suggest` / `list --kind prop` → chọn đạo cụ, khai vào bible (`lib`) và `props[]` của shot, mỗi đạo cụ có anchor/slot.
2. Viết beat: mỗi lần đổi state hoặc chạm đạo cụ là một beat có `set`/`reach`/`macro`, `physical: true` nếu có tiếng, kèm `sfx`.
3. `check_shots.py` (E6, E10, E11, E12, E14) → `preview_shot.py --shot <id>` (dựng + chụp mốc beat, gồm cả mốc ngay sau beat vật lý) → **mở contact sheet xem**.
4. Báo cáo theo `craft-playbook.md` mục 8, có "Ảnh đã XEM" và "Chưa kiểm".

SFX, hiệu ứng, góc quay: xem [`sfx-effects-camera-guide.md`](sfx-effects-camera-guide.md).
