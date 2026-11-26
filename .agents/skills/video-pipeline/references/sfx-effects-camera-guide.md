# Hướng dẫn SFX, hiệu ứng và góc quay (cho agent dựng video)

Bổ sung cho `shotlist-guide.md` (cấu trúc shot, beat), `props-and-interaction-guide.md` (đạo cụ) và `craft-playbook.md` mục 5 (nhịp và ống kính). Luật gốc: R5.2, R6.1, R6.2, R10.2.

**Cách đọc độ tin cậy.** `[đã kiểm]` = đã dựng, render và xem khung hình (2026-11-26). `[đọc code]` = đọc từ `build_video.py`, chưa thử riêng. `[khuyến nghị]` = nguyên tắc dựng phim, chưa kiểm trong repo này. **Chưa ai trong repo này đã nghe SFX**: chỉ kiểm được thời điểm (±0,15 s, gate E6) và loại âm theo tên file, không kiểm được âm có hợp cảnh hay không. Nhận xét nghe của người dùng thì ghi ở mục 6.

---

## 1. SFX: nguyên tắc

1. **Mỗi hành động vật lý một âm, đúng nhịp** (R6.1): `physical: true` ⇒ có `sfx` cách ≤ 0,15 s [gate E6]. Beat vật lý thiếu SFX thì E6 in sẵn gợi ý theo đạo cụ (`library/index.json` trường `sfx`).
2. **Âm khớp chất liệu và lực**, không chỉ khớp tên hành động [khuyến nghị]:
   - gỗ chạm gỗ/bàn thờ → `foley-wood-touch/slide`; vải, khăn, áo, chăn → `foley-fabric-*`; giấy, tàn hương → `foley-paper-*`; kính, đèn → `foley-glass-*`;
   - va đập: chọn theo lực × độ cứng, `impact-{light|medium|heavy|deep}-{soft|firm|hard}` (nhẹ rơi vãi = `light-soft`; vật nặng đổ = `heavy-hard`; điềm lạ/trầm = `deep-soft`);
   - điện thoại: `ui_clicks/phone/phone-ring-modern.wav` (chuông), `phone-keypad.wav` (bắt máy/cúp);
   - nước/giọt: `ambience/everyday-props/props-drip.wav`, `props-splash.wav`.
3. **Ba nhịp cho một khoảnh khắc đáng chú ý** [khuyến nghị, chưa nghe]: *dự báo* (âm nhỏ, 0,2–0,5 s trước) → *hành động* (âm chính đúng khung hình) → *phản ứng* (nhân vật `set` cảm xúc cùng nhịp hoặc ≤ 0,3 s sau). Ví dụ nến: tay chạm (`glass-touch`) → `low` (`paper-touch`) → `out` (`drip`) + nhân vật chuyển `afraid`.
4. **Cao trào** (R6.2): stinger/âm trầm đặt đúng khoảnh khắc, cùng lúc đổi `light` và state đạo cụ. Kho có `impacts_hits/booms-and-bass`, `cinematic-hits`, `risers_tension/*` (tra `sfx/catalog.json`); **chưa thử ghép** nên chọn xong phải nghe.
5. **Đừng rải âm ở mọi beat**: khoảng lặng cũng là SFX. Beat không vật lý (nhìn, gật, đổi mắt) thì không cần âm [khuyến nghị].
6. **Kho còn thiếu**: tiếng quẹt diêm, thổi nến, lửa cháy, gốm vỡ, vật gỗ nặng đổ, bước chân (generator chưa tự thêm). Dùng âm gần nhất và **ghi "âm thay thế" trong báo cáo**; cần âm thật → hỏi người dùng. Không nhập âm ngoài `sfx/` khi chưa được phép (bản quyền, R7.1).

**Mức âm** [đọc code]: generator đặt giọng `data-volume=1`, mọi SFX `0.8` cố định; **chưa có BGM, stinger tự động, ducking hay cân bằng riêng từng âm**. Cần mix khác thì phải mở rộng generator (R10.6), không vá riêng một video. Cân bằng thật chỉ kiểm được khi nghe.

---

## 2. Hiệu ứng hình: cái có và cái chưa có

**Có** (đã thấy trong khung hình) [đã kiểm]:
- **Đổi state đạo cụ tức thì** (không chuyển mờ). Muốn mượt thì đi qua state trung gian cách 0,5–1 s: `lit → low → out` (ngọn lửa nhỏ lại rồi tắt, có sợi khói).
- **Glow/ánh sáng của đạo cụ nổi trong cảnh tối**: điện thoại `ringing` có glow xanh rõ trong `light: dark`; cùng hiệu ứng ở cảnh sáng thì mất. Chọn `light` theo cảm xúc: `warm` bình thường, `dark` căng thẳng, `red_flash` sốc, `dawn` giải toả (`craft-playbook.md` mục 5).
- **Phản ứng nhân vật cùng nhịp với hiệu ứng**: `set` cảm xúc/`gaze`/macro `giat_minh` trong cùng beat với đổi state.
- Camera chạy trong shot (mục 3).

**Chưa có** [đọc code: không có trong `build_video.py`]: chuyển cảnh mờ/trượt giữa shot (chỉ cắt cứng), rung máy, lấy nét (rack focus), làm mờ nền, hạt/bụi/mưa, nhạc nền. Cần thì **mở rộng generator**, không ghép tay vào HTML của shot (R10.6, R1.6).

---

## 3. Góc quay

### 3.1 Cỡ cảnh và độ zoom [đọc code: `ZOOM` trong `build_video.py`]
| `size` | Zoom | Dùng khi |
| --- | --- | --- |
| `wide` | 1,0 | thiết lập không gian, cô lập, nhìn hai người cùng đạo cụ |
| `medium` | 1,6 | thoại thường, hai người trong khung (đã dùng nhiều nhất) |
| `close` | 2,4 | cảm xúc dồn, mặt nhân vật |
| `macro` | 3,2 | đạo cụ/chi tiết nhỏ (nến, khăn, điện thoại) |
| `ots` | 1,8 | **chỉ là zoom 1,8 [đã kiểm]**, không có vai nhân vật phía trước nên **không phải over-the-shoulder thật**; đừng dùng để diễn tả góc qua vai |

`focus` chọn điểm ống kính nhìn vào: `<id nhân vật>`, `prop:<id bible>`, `slot:<tên>`. Với `wide`, camera chỉ nghiêng nhẹ về tiêu điểm (35% ngang, 20% dọc) chứ không dịch hết.

### 3.2 Chuyển động camera [đọc code]
`static` giữ nguyên · `push_in` zoom vào 12% suốt shot · `pull_out` lùi ra 12% · `pan_l`/`pan_r` trượt ±70 px (đơn vị khung 1920×1080). Mọi chuyển động chạy **đều suốt shot**; chưa có đường cong gia tốc, đẩy nhanh ở cuối, hay hai chuyển động nối nhau.

### 3.3 Chọn góc theo mục đích [khuyến nghị, từ `craft-playbook.md`; mục dấu ✔ đã xem lại]
| Mục đích | Cỡ + camera | Ghi chú |
| --- | --- | --- |
| Mở cảnh, cho khán giả định hướng | `wide` + `static`/`pull_out` | `pull_out` tạo cảm giác bị bỏ rơi/cô lập |
| Thoại bình thường | `medium` + `static` | ✔ hai người trong khung vẫn thấy tay và đạo cụ |
| Cảm xúc dồn, sắp tiết lộ | `close` + `push_in` | zoom chậm 12% đủ; đừng zoom quá nhanh |
| Nhấn một vật | `macro` + `static` hoặc `push_in`, `kind: insert`, `focus: prop:<id>` | xem cảnh báo che khuất bên dưới |
| Nhân vật bước vào/lộ ra | `medium` + `pan_l`/`pan_r` | dẫn mắt về phía tiết lộ |
| Sau cú sốc | `static` | để khán giả nhìn phản ứng |

### 3.4 Quy tắc nhịp ống kính (`craft-playbook.md`, nhắc lại vì hay vi phạm)
Không 3 shot liền cùng cỡ hoặc cùng camera; một cỡ không quá ~50% số shot; shot 3–5 s, không tĩnh > 6 s; xen toàn/trung/cận/macro/cutaway.

### 3.5 Lỗi góc quay đã gặp [đã kiểm]
1. **Tay/thân nhân vật che mất thứ khán giả cần thấy.** Thử `macro` + `push_in` lên cây nến phải ở SH008: khi mẹ với tay tắt nến, bàn tay che gần hết ngọn lửa ở các khung 2,4 s và 3,3 s; chỉ thấy khói ở 4,2 s. Cận cảnh vào đúng chỗ nhân vật đang tác động làm mất chính hiệu ứng. Cách xử lý: dùng `medium` để thấy cả tay lẫn nến, hoặc cắt sang `macro` **sau** khi tay rời đi (shot riêng), hoặc chọn người đứng lệch phía khác.
2. **`macro` cắt mất thân người** (zoom 3,2): chỉ thấy mặt và cánh tay giơ; ổn cho cảm xúc nhưng mất bối cảnh. Đừng dùng cho beat cần thấy `reach`/`hand_over` toàn thân.
3. **`focus` theo `key` đạo cụ bị gate E11 từ chối** (ví dụ `prop:nen-r`: "không có trong bible"); `focus` chỉ nhận id bible (`prop:nen`) nên khi có hai cây nến cùng id, tiêu điểm nằm ở giữa/cây đầu. Muốn nhắm đúng một cây thì dùng `slot:<tên>` nếu location có slot đó, hoặc nhắm nhân vật.
4. **`ots` không đúng nghĩa qua vai** (mục 3.1).

---

## 4. Quy trình khi viết SFX/góc quay cho một shot
1. Với mỗi beat vật lý, chọn một âm theo chất liệu (mục 1); lấy gợi ý từ lỗi E6 rồi **tự duyệt**, ghi âm thay thế.
2. Chọn `size`/`camera` theo bảng 3.3; kiểm tra không 3 shot liền cùng cỡ.
3. `check_shots.py` (E6, E11, E14) → `preview_shot.py --shot <id>` (chụp ở mốc beat và sau beat vật lý) → **mở contact sheet xem**: có bị che khuất không, có thấy đổi state không.
4. Báo cáo theo `craft-playbook.md` mục 8: "Ảnh đã XEM", "Chưa kiểm" (ghi rõ **chưa nghe SFX**, mix chưa cân).

---

## 5. Hiệu ứng/âm cần làm thêm trong generator (đề xuất, chưa làm)
SFX bước chân khi `move`; ducking giọng khi có SFX/stinger; BGM theo cảnh; chuyển cảnh mờ/trượt; rung máy ngắn cho cú sốc; `ots` thật (nhân vật phía trước làm khung); `focus` theo `key`. Mỗi mục cần thiết kế + thử + xem/nghe trước khi dạy agent dùng.

---

## 6. Nhận xét nghe/xem của người dùng (điền khi có)
*Chưa có.* Sau khi người dùng nghe `demo_render.mp4` hoặc video sau này, ghi tại đây: âm nào lệch nhịp/sai chất liệu, nhịp nào thừa, góc quay nào gây khó chịu; đó là kinh nghiệm đáng tin hơn mọi suy luận ở trên.
