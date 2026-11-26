# Hướng dẫn viết shot và diễn xuất nhân vật (cho agent dựng video)

> Đạo cụ (danh mục state/slot, đổi state, SFX, tương tác người↔đạo cụ): xem [`props-and-interaction-guide.md`](props-and-interaction-guide.md).

Đọc sau `RULES.md` và `craft-playbook.md`. File này trả lời ba câu: **một shot được mô tả thế nào, nhân vật phải cử động thế nào, và thế nào là đạt chuẩn.**
Mọi ví dụ JSON dưới đây đã được chạy qua `check_shots.py` trên project mẫu `than-trung-chiec-khan-tang-thu-32` (xem mục 9). Luật gốc ở `RULES.md`; file này không nới luật.

> Nhãn trạng thái dùng trong file: **[gate]** = máy chặn nếu sai · **[khuyến nghị]** = chuẩn tay nghề, máy không bắt · **[prototype]** = chạy được nhưng chưa dùng trong video thật.

---

## 1. Từ kịch bản đến shot (đi theo thứ tự này)

1. **Mỗi câu thoại (`line`) phải thuộc một shot** [gate E1]. Một shot phủ 1 line hoặc vài line ngắn liền nhau. Shot không dài quá 6 s [gate E3]; nhắm 3–5 s [R5.2].
2. **Với mỗi shot, trả lời đủ 5 thành phần** trong trường `visual` của `script.json` [R5.3]: bối cảnh · bố cục nhân vật · cử động & biểu cảm (đúng từ vựng `emotion_vocab`) · ánh sáng · SFX. Thiếu một thành phần là mô tả chưa đủ để dựng.
3. **Chọn cỡ cảnh và camera** theo cảm xúc: toàn (`wide`) để thiết lập, trung (`medium`) để thoại, cận (`close`) khi cảm xúc dồn, `macro` cho đạo cụ. Không 3 shot liền cùng cỡ, một cỡ không quá ~50% [khuyến nghị, craft-playbook §5].
4. **Viết beat cho từng thay đổi nhìn thấy được** (mục 3). Beat không có `set`/`look`/`react`/`reach`/`move`/`hand_over`/`macro` thì **không ai thấy gì**.
5. **Khai đạo cụ + trạng thái ở shot, chỉ đổi qua beat** [R4.3]. Mọi id/trạng thái phải có trong `bible.json` [gate E5].
6. Chạy `check_shots.py`, dựng, **mở snapshot xem** [R10.2].

Ví dụ `visual` đủ 5 thành phần (S01_L07 của project mẫu, viết gọn):
> Gian thờ nhà (bối cảnh). Host đứng trái, mẹ đứng giữa, bàn thờ phía sau (bố cục). Host cúi đầu, mắt rơi xuống, `sad`; mẹ `grief`, chìa tay phát khăn xô (cử động & biểu cảm). Ánh sáng `warm` nến (ánh sáng). Tiếng vải sột soạt lúc mẹ chìa khăn (SFX).

---

## 2. Cấu trúc một shot

| Trường | Giá trị | Ghi chú |
| --- | --- | --- |
| `id`, `line_ids` | `SH008`, `["S01_L07"]` | `line_id` trong beat phải thuộc `line_ids` |
| `kind` | `speaker` · `cutaway` · `insert` · `establishing` | Người kể không lên hình → dùng `cutaway`/`insert`/`establishing` |
| `size` | `wide` · `medium` · `close` · `macro` | |
| `camera` | `static` · `push_in` · `pull_out` · `pan_l` · `pan_r` | `push_in` dồn cảm xúc; `pull_out` cô lập; `static` sau cú sốc |
| `focus` | `<nhân vật>` · `prop:<id>` · `slot:<tên>` | Phải trỏ tới thứ có thật trong shot [gate E11] |
| `location`, `light` | id bối cảnh; `warm` · `dark` · `red_flash` · `dawn` | Đổi ánh sáng bằng `set.light`, không chỉnh tay |
| `characters[]` | `id`, `at` (`L`/`C`/`R`), `stance`, `emotion`, `gaze`, `pose`, `view`, `mouth` | Trạng thái đầu shot. Mọi giá trị phải có trong `<id>.rig.json` [gate E9/E13]. Nhân vật nói: `mouth: true` [gate E4] |
| `props[]` | `id`, `state`, `at`, `dx`/`dy`, `key` | `at` = `altar` · `stand:L` · `<prop>.<slot>`; **không đặt toạ độ tuỳ ý** [R4.2]. Chân người không được đè đạo cụ [gate E10]. Hai đạo cụ cùng `id` phải khác `key` |
| `beats[]` | xem mục 3 | |
| `sfx[]` | `{"t":…, "src":"sfx/…wav"}` | `t` tính từ đầu shot, phải nằm trong shot |

---

## 3. Beat: khi nào và làm gì

### 3.1 Đặt thời điểm (chọn một)
- `"word": 9` — neo theo **từ thứ 9** của line (ưu tiên, R12.2). Thêm `"edge": "end"` để rơi vào cuối từ. Từ phải có thật trong line [gate E8]. Mốc từ là **ước lượng** cho tới khi có `words` thật từ VieNeu; báo cáo phải nói rõ.
- `"t": 2.4` — giây từ đầu shot. Chỉ dùng khi không có từ để neo.
- `"dt"` chỉ dùng trong `macro` (độ lệch giữa các bước).

### 3.2 Các thao tác (một beat có thể gộp nhiều thao tác)

| Thao tác | Dùng để | Ví dụ |
| --- | --- | --- |
| `set` | Đổi trạng thái: `emotion`, `pose`, `gaze`, `stance`, `view`, `light`, `prop:<key>` | `"set": {"host": {"gaze": "right"}}` |
| `look` | Nhìn về nhân vật khác; gaze tự tính theo vị trí | `"look": {"char": "host", "target": "me"}` |
| `react` | Phản xạ ngắn. `preset` chỉ có `nod` · `flinch` [gate E8] | `"react": {"char": "host", "preset": "nod"}` |
| `move` | Đổi vị trí **có thời gian** [R11.3]; `to` là `L`/`C`/`R`; `gait` `walk`/`run` | `"move": {"char": "host", "to": "R", "dur": 1.2, "gait": "walk"}` |
| `reach` | Tay với tới đích bằng IK; thân nghiêng, mắt theo đích | xem 3.3 |
| `hand_over` | Chuyển đạo cụ giữa hai người, đạo cụ bám bàn tay | xem 3.4 |
| `macro` + `args` | Hành vi mẫu có sẵn (23 macro, `behaviors.py list`) | `"macro": "nghe_gat", "args": {"char": "host"}` |

`physical: true` khi beat có tiếng động vật lý (chạm, đặt, ngã, bước). Beat vật lý **phải** có `sfx` cách ≤ 0,15 s [gate E6, R6.1]. Macro vật lý tự thêm SFX.

### 3.3 `reach` — tay với tới [prototype: chưa dùng trong shotlist thật]
```json
{"line_id": "S01_L07", "t": 1.0, "physical": true,
 "do": "host với tay về phía cây nến bên phải trên bàn thờ",
 "reach": {"char": "host", "to": {"prop": "nen-r"}, "dur": 0.6, "hold": 1.2}}
```
- `to`: `{"prop": key}` · `{"char": id, "hand": "l|r"}` · `{"x":…, "y":…}` · `{"rel": [dx, dy]}`.
- Chỉ `stance` `stand`/`sit` và `view` `front`. Đích quá xa (>25 px rig) → generator báo "trượt đích": đưa người lại gần bằng `move`.
- **Đích phải ở độ cao tay** (bàn thờ, bàn, tay người khác). Vật nằm sàn (mâm khăn `mam_tre` ở `stand:L`) **không với tới được khi đứng** (đã thử: trượt 100–170 px dù dịch lại gần); cần quỳ/cúi mà `reach` chưa hỗ trợ. Muốn lấy vật dưới sàn, dùng `macro quy_xuong` rồi đổi `set` thay vì `reach`.
- `side` bỏ trống = tay phía đích. `to.prop` dùng **`key`** của đạo cụ trong shot (`nen-r`, không phải `nen`).
- Tuỳ chọn: `lean` (`"auto"`/số độ/`false`), `gaze` (`true`/`false`), `limits` (dải khớp theo beat).

### 3.4 `hand_over` — đưa đồ [prototype]
```json
{"line_id": "S01_L07", "t": 2.4, "physical": true,
 "do": "mẹ đưa mâm khăn cho Lâm",
 "hand_over": {"prop": "mam_tre", "from": "me", "to": "host", "dur": 1.4, "held": true}}
```
Cần `sfx` cạnh beat (R6.1, R11.5). `held: true` khi đạo cụ đã nằm trong tay người cho; nếu không, đạo cụ phải nằm trong tầm tay.

### 3.5 Macro thường dùng
`nghe_gat` (người nghe gật) · `giat_minh` · `so_hai` · `lo_lang` · `nhin_sang` · `chap_tay` · `chi_tay` · `ha_tay` · `di_toi` · `chay_toi` · `quy_xuong` · `quy_lay` · `dung_day` · `om_dau` · `ngat` · `cau_xin` · `vai_chao` · `trao_do`. Danh sách đầy đủ và tham số: `python .agents/skills/video-pipeline/scripts/behaviors.py list`. Thêm macro mới chỉ được **thêm**, không đổi tên/xoá.

---

## 4. Bảng tình huống → thao tác

| Tình huống trong kịch bản | Dùng | Đừng |
| --- | --- | --- |
| Người nghe phản ứng khi người kia nói | `macro nghe_gat` ở chỗ ngắt câu (`word` + `edge: end`) | Để người nghe đứng im [gate E7] |
| Nhìn sang người khác | `look` hoặc `macro nhin_sang` | Chỉnh `gaze` tay khi đã biết đích là ai |
| Nhân vật đi chỗ khác trong cảnh | `move` (có `dur`, có `gait`) | Đổi `at` giữa hai shot trong cùng cảnh mà không có `move` [R11.3] |
| Đưa/nhận đồ | `hand_over` + SFX | Đổi `at` của đạo cụ trong `props` của shot sau |
| Chạm/nhấc/với một vật | `reach` (+ `physical` + SFX nếu có tiếng) | Chỉ đổi `pose` sang `reach-l` khi vật ở xa (tay không tới) |
| Giật mình, sợ | `macro giat_minh` / `so_hai` | Chỉ đổi `emotion` mà không có phản xạ thân |
| Quỳ, lạy | `macro quy_xuong` / `quy_lay` (nhìn nghiêng `view: auto`) | Quỳ nhìn chính diện (trông như ngồi đệm) |
| Ngất | `macro ngat` hoặc `soc_roi_ngat`, chọn `suf` để ngã AWAY khỏi người khác | Ngã đè lên người bên cạnh |
| Khoảnh khắc cao trào | đổi `light` + stinger **cùng một thời điểm** | Đổi ánh sáng và âm thanh lệch nhau |
| Người kể (không lên hình) | `cutaway`/`insert` minh hoạ lời kể | Bắt nhân vật nhép miệng lời người kể |

---

## 5. Diễn xuất: thế nào là đạt chuẩn

**Máy chặn [gate]:**
- Mọi line có shot và có ≥ 1 beat riêng (E1, E2); không shot > 6 s (E3).
- Shot ≥ 2 nhân vật: **mỗi người** có ≥ 1 hành vi tường minh (`set`/`move`/`look`/`react`/`reach`), kể cả người nói (E7, R11.1).
- Beat vật lý có SFX ±0,15 s (E6).
- Giá trị `pose`/`emotion`/`stance`/`gaze`/`view` nằm trong rig (E9, E13); beat chỉ nhắc nhân vật/đạo cụ có mặt trong shot (E12).
- Đạo cụ có `at` hợp lệ, chân không đè đạo cụ (E10); `focus` trỏ đúng (E11).

**Tay nghề [khuyến nghị]:**
- Đổi trạng thái **đúng lúc lời nói**: ánh nhìn đổi *trước* khi nhắc tới vật; biểu cảm đổi ở từ then chốt; tay với đúng lúc câu nhắc.
- Hoạt hình sống, không slide tĩnh [R5.4]: thở, chớp mắt, đảo mắt, miệng (rig tự lo). Đừng để mặt đứng yên cả shot.
- Cảm xúc phải **nhìn khác nhau ở cỡ nhỏ**; đừng đổi hai cảm xúc gần giống ở hai beat sát nhau.
- Chuyển ánh sáng theo cảm xúc: `warm` bình thường, `dark` căng, `red_flash` sốc, `dawn` giải toả.
- **Số đo gợi ý** (từ `check_motion.py`): ≥ 3 thao tác tường minh mỗi 10 s (chưa tính hơi thở/chớp/gật tự động); ≥ 3 cỡ cảnh khác nhau trong cả đoạn. Đây là ngưỡng cảnh báo của gate đó, **không** phải luật.

---

## 6. Lỗi hay gặp

| Triệu chứng | Nguyên nhân | Cách đúng |
| --- | --- | --- |
| Beat viết "nhân vật khóc" mà hình không đổi | Beat thiếu `set`/`macro` | Thêm `set` hoặc dùng macro |
| `check_shots` báo SFX thiếu | `physical: true` nhưng không có `sfx` ±0,15 s | Thêm `sfx` hoặc dùng macro vật lý |
| "trượt đích" khi `reach`/`hand_over` | Đích ngoài tầm tay, ở sàn, hoặc ngoài giới hạn khớp | Đích ở độ cao tay; `move` lại gần; đổi `limits` |
| Người nằm đè lên người bên cạnh | `lie` dài ~480 px ở scale 1 | Chừa chỗ, đổi `suf` (`''`/`-r`) hoặc vị trí |
| Quỳ trông như ngồi đệm | Quỳ nhìn chính diện | Dùng `view: tq-r`/`tq-l` hoặc `auto` |
| Beat `word` báo từ không tồn tại | Số từ vượt độ dài line | Đếm lại từ trong `script.json` |
| Một tay giơ lơ lửng khi đang đưa đồ | `reach` và `hand_over` của **cùng một nhân vật** chạy chồng thời gian (đã thấy trong snapshot thử) | Beat sau chỉ bắt đầu khi `t + dur + hold` của beat trước đã hết |
| Chuyển động bị cắt giữa chừng | `t + dur` của `move`/`reach`/`hand_over` vượt độ dài shot (gate chưa bắt) | Kiểm `t + dur` ≤ độ dài shot, hoặc tách sang shot sau |
| Hai nến giống nhau bị gộp | Hai đạo cụ cùng `id` thiếu `key` | Đặt `key` khác nhau |
| Mặt nhân vật đen trong HyperFrames | CSS có combinator `>` | Xem `craft-playbook.md` §7 |
| Dựng "xong" nhưng không có tiếng | Chưa có `voiceover.wav` | Báo "chưa có giọng"; chạy `build_voiceover.py` trên máy có VieNeu |

---

## 7. Giới hạn hiện tại (nói thẳng, đừng giả vờ đã có)

- `react` chỉ có `nod` và `flinch`.
- `reach`/`hand_over` chỉ cho `stand`/`sit` nhìn chính diện; kneel/lie/3-4 chưa hỗ trợ. Đầu không quay, mắt chỉ liếc tối đa 5 px ngang, 4 px dọc. Thân chỉ nghiêng sang ngang.
- `reach`, `hand_over` mới **thử trên snapshot**, chưa dùng trong shotlist thật, chưa render mp4; điểm nắm của `oil_lamp` chỉ ước lượng từ hình.
- Chưa có SFX bước chân/chạy tự động cho `move`.
- **`check_motion.py` (version 2) chỉ kiểm thao tác tường minh** lấy từ beat (move/reach/hand_over có độ dài; set/look/react tức thời): thao tác vượt hết shot (bị cắt), beat vật lý không có hành động thật, người trong shot ≥ 2 nhân vật không có thao tác. Nó **không** thấy hơi thở/chớp mắt/gật tự động, không kiểm SFX bước chân (generator chưa tự thêm), không đánh giá độ mượt. Chạy sau `build_video.py` ra `video_demo/motion_plan.json`.
- `quy_xuong`/`lie` nhìn nghiêng còn đơn giản.
- Cast mới có 11 nhân vật của một project; chưa dựng nhân vật thiếu niên.

---

## 8. Quy trình ngắn cho shot mới

```bash
P=projects/<slug>
python .agents/skills/video-pipeline/scripts/check_shots.py --project $P            # mọi lỗi E* (E14: reach/hand_over với tới đích; E6 kèm gợi ý SFX đạo cụ)
# thử một shot (hoặc biến thể shotlist) và XEM ảnh: ra contact sheet theo mốc beat
python .agents/skills/video-pipeline/scripts/preview_shot.py --project $P --shot SH0xx [--shotlist biến_thể.json]
python .agents/skills/video-pipeline/scripts/check_sync.py  --project $P
python .agents/skills/video-pipeline/scripts/build_video.py --project $P --until SH0xx
cd $P/video_demo && npx -y hyperframes@0.9.82 snapshot --at <giây giữa shot> ...    # rồi MỞ ẢNH XEM
```
Báo cáo theo khung `craft-playbook.md` §8, có "Ảnh đã XEM" và "Chưa kiểm".

---

## 9. Ví dụ đã kiểm

Các ví dụ ở mục 3 được ghép vào bản sao shotlist của project mẫu và chạy `check_shots.py`; kết quả và ngày kiểm ghi ở `projects/than-trung-chiec-khan-tang-thu-32/PROJECT.md` (mục "shotlist-guide"). Ví dụ `reach`/`hand_over` chỉ được kiểm bằng gate và dựng thử, **chưa** render video.
Bản thử ghép **cả năm thao tác vào một shot 4,4 s để kiểm lỗi**, không phải mẫu diễn xuất hay: ở snapshot thấy tay `reach` còn giơ khi `hand_over` bắt đầu và `move` bị cắt ở cuối shot. Khi viết shot thật, mỗi shot chỉ nên có vài thao tác, cách nhau đủ thời gian.
