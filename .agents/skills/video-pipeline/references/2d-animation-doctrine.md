# 2D Animation Production Doctrine (Quy chuẩn hoạt hình 2D sống động)

Tài liệu này lưu trữ phương pháp sản xuất video hoạt hình 2D chuyển động biểu cảm trong không gian HyperFrames, kết hợp 3 kỹ năng cốt lõi:
1. **`reverse-any-video`**: Đo đạc và tái hiện chính xác bố cục khung hình, vị trí đạo cụ và chuyển cảnh.
2. **Line boil & biểu cảm**: rung nét vẽ tay hữu cơ (Line Boil), mô phỏng 12fps (animating on twos); biểu cảm theo `emotion_vocab` của bible (11 trạng thái rig hỗ trợ, xem `library/` + `build_rig.py`). Skill `claude-animation-base` không có trong repo này — không dẫn chiếu.
3. **`hyperframes` + `media-use`**: Lập trình vector HTML/SVG, GSAP timeline theo frame chính xác, và hòa âm 4 tầng (Voice, BGM, SFX, Stinger).

---

## 1. Kiến trúc Bối cảnh & Bố cục (`reverse-any-video`)

### A. Mật độ Shot & Nhịp điệu điện ảnh dồn dập (Cinematic Multi-Shot Pacing):
* **Mật độ chuyển cảnh cao:** Trung bình **3–5 giây / shot**. Tuyệt đối không giữ khung hình tĩnh quá 6 giây để duy trì trạng thái tập trung và kích thích thị giác.
* **Quy mô 1 phút video:** Bắt buộc thiết kế **12–15 shots trở lên** cho mỗi 60–75 giây nội dung.
* **Phối hợp đa dạng cỡ cảnh:**
  1. *Establishing Wide:* Toàn cảnh đêm, rặng chuối làng quê, rạp tang, đình làng ven sông.
  2. *Medium Character Shot:* Người dẫn chuyện, nhân vật đối thoại hoặc hành động.
  3. *Close-up & Extreme Close-up:* Biểu cảm co giật mắt, ánh mắt sợ hãi lén lút, khẩu hình mấp máy, giọt mồ hôi trán.
  4. *Macro Prop Shot:* Lư hương nghi ngút khói, ngọn nến lập lòe, mâm khăn tang xô, đáy cối đồng.
  5. *Over-The-Shoulder (OTS):* Góc nhìn từ sau vai nhân vật trông ra khung cửa tối đầy hiểm họa.
  6. *Dynamic Virtual Camera:* Cú lia máy zoom-in căng thẳng hoặc pull-back lùi dần ra xa mở rộng bối cảnh (như từ bà cụ giã trầu lùi dần thấy bé Lâm ngủ trên chõng tre).

### B. Nguyên tắc 3 lớp không gian:
1. **Hậu cảnh (Background):**
   * Vách gỗ (`#241a13`), vách nứa, vách gạch rêu với các đường chỉ ghép ván mộc (`stroke-width="6"`).
   * Ô cửa sổ hoặc cửa chính mở ra bên ngoài: đêm mờ sương (`#1a2428`), bóng rặng chuối lay, bóng trăng mờ.
   * Cột trụ chống nhà bằng gỗ dày (`#1b120c`).
2. **Trung cảnh (Midground - Vùng diễn xuất chính):**
   * Bàn thờ tổ tiên / rạp tang: Bát hương, khói trầm nghi ngút, đôi nến trắng hoặc đèn dầu.
   * Chõng tre, bếp lửa bập bùng với vòng đá kê và củi khô.
   * Vị trí nhân vật: Ngồi/đứng theo quy tắc 1/3 hoặc đối xứng trung tâm có chủ đích.
3. **Tiền cảnh (Foreground):**
   * Mâm tre đan đựng các nếp khăn xô trắng thô ráp.
   * Cối đồng giã trầu với chày gỗ.
   * Vệt bóng đổ và lớp phủ tối góc (Vignette radial gradient).

---

## 2. Kỹ thuật Line Boil & Hiệu ứng vẽ tay

Thay vì nét vẽ vector kỹ thuật số phẳng lì, áp dụng bộ lọc rung nét vẽ tay hữu cơ:

```html
<!-- Bộ lọc Hand-Drawn Boil trong SVG defs -->
<filter id="hand-drawn-boil" x="-5%" y="-5%" width="110%" height="110%">
  <feTurbulence id="boil-turb" type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" seed="1" />
  <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.4" xChannelSelector="R" yChannelSelector="G" />
</filter>
```

Trong GSAP timeline, cập nhật seed của bộ lọc theo nhịp twos (khoảng mỗi 0.16 giây = ~6-12 fps):
```javascript
for (let f = 0; f < videoDuration; f += 0.16) {
  const seedVal = Math.floor(f * 6) + 1;
  tl.set("#boil-turb", { attr: { seed: seedVal } }, f);
}
```

---

## 3. Rigging & Chuyển động nhân vật (Character Motion Rig)

### A. Thân mình & Nhịp thở (Breathing Idle):
```javascript
tl.to("#character-group", {
  y: -3,
  duration: 1.6,
  repeat: -1, // Trong HyperFrames: lặp hữu hạn theo thời lượng scene
  yoyo: true,
  ease: "sine.inOut"
}, startTime);
```

### B. Chớp mắt tự nhiên (Organic Eye Blink):
Đặt mí mắt (`<rect>` cùng màu da) nằm phía trên tròng mắt với `transform-origin` tại tâm mí mắt:
```javascript
// Chớp mắt chớp nhoáng (0.08s nhắm, 0.08s mở)
[1.5, 4.2, 7.8].forEach(time => {
  tl.to(["#blink-l", "#blink-r"], { scaleY: 1, duration: 0.08, ease: "power1.in" }, time);
  tl.to(["#blink-l", "#blink-r"], { scaleY: 0, duration: 0.08, ease: "power1.out" }, time + 0.08);
});
```

### C. Đảo mắt & Liếc nhìn sợ hãi (Pupil Tracking & Dread):
```javascript
// Khi phát hiện điều lạ: đồng tử liếc sang góc tối
tl.to(["#pupil-left", "#pupil-right"], { attr: { cx: "+=6", cy: "-=3" }, duration: 0.5 }, dreadTime);
// Lông mày chau lại với góc nhọn hoảng hốt
tl.to("#eyebrow-left", { attr: { d: "M 915 346 Q 935 334 950 350" }, duration: 0.4 }, dreadTime);
```

### D. Khẩu hình nói & Quy chuẩn TransformOrigin chống bay chi tiết:
* **Khẩu hình:** rig có 4 hình miệng (`data-mouth`: closed/half/open/round) — đổi hình theo âm, không scale một hình duy nhất. (Cách `scaleY` dưới đây chỉ là phương án cũ cho SVG vẽ tay ngoài rig.) **Khẩu hình mấp máy (`scaleY`):** Luôn dùng `transformOrigin: "50% 50%"` để khẩu hình đóng mở đối xứng quanh tâm môi:
```javascript
tl.to("#mouth", {
  scaleY: 2.0,
  duration: 0.26,
  repeat: 20,
  yoyo: true,
  transformOrigin: "50% 50%" // Bắt buộc: không dùng pixel canvas tuyệt đối
}, lineStart);
```
* **Chống bay rời chi tiết SVG:**
  - *Mắt, con ngươi, miệng, ngực thở:* luôn dùng `transformOrigin: "50% 50%"` (đã cài sẵn trong rig, điều khiển bằng `data-*`).
  - *Khớp vai, cánh tay, cẳng chân:* dùng pivot trong `<id>.rig.json` (toạ độ viewBox của rig, `transform-box: view-box`) — **RULES.md R3.4 thay cho quy ước `0% 0%` cũ**. Rig chỉ được nhúng dưới dạng `<svg>` lồng nhau; không truyền px toạ độ cảnh vào `transformOrigin`.

### E. Cử động tay cầm nắm & Tương tác (Hand Actions):
* **Giã cối đồng bộ:** Cánh tay nâng lên hạ xuống (`rotation: 10` lên, `rotation: -12` đập chạm đáy cối) quanh pivot vai trong `rig.json`; chày là part `pestle` của prop `betel_mortar` (state `rest/raised/strike`), khớp chính xác từng mili-giây với tiếng gõ SFX cối đồng.
* **Đếm khăn:** Bàn tay đưa ra gắp nếp khăn tang, nhấc nhẹ lên (`y: -30`) rồi đặt xuống nếp đếm mới kèm tiếng vải sột soạt.
* **Chỉ tay:** Cánh tay vung ra chỉ về phía cửa hoặc góc tối khi giảng giải bí mật.

---

## 4. Hệ thống SFX Dày đặc & Hòa âm 4 tầng (`media-use`)

Để tạo cảm giác **hồi hộp, gay cấn và rùng rợn**, âm thanh phải phối hợp chặt chẽ 4 kênh với mật độ SFX dày đặc:

1. **Voiceover (VieNeu-TTS v3 Turbo):**
   * Người kể ma: Luôn dùng `Đức Trí` @ 1.25–1.3.
   * Nhân vật phân vai: `Thiền Tâm Đức` (Ông già/thầy pháp), `Kim Thanh` (Mẹ/Bà), `Trúc Ly` (Em gái), `Hải Đăng` (Bố), `Thiện Minh` (Thần Trùng).
2. **BGM (Nhạc nền không gian):**
   * Dải bass/cello u uất (ambient horror drone 55Hz & 82.5Hz), kết hợp tiếng côn trùng đêm và gió thổi hiu hắt.
3. **SFX Hiện trường Dày đặc (Foley & Acoustic Events - Sample-Accurate):**
   * *Sinh hoạt nông thôn:* Tiếng cối đồng giã trầu đanh gọn ("cắc cắc" 1.480Hz/2.650Hz + thụt chày 175Hz), tiếng sột soạt lật đếm dải khăn tang xô, tiếng va chạm lách cách kim loại khay đồng (2.150Hz), tiếng củi nổ tanh tách trong bếp, tiếng mái chèo bì bõm mạn thuyền.
   * *Tâm lý & Hồi hộp:* Chuỗi nhịp tim đập dồn dập (thump tần số thấp 58Hz), tiếng thở gấp khi hoảng loạn, tiếng gió lạnh rít luồn qua khe cửa gỗ.
4. **Horror Stingers & Impacts (Điểm nhấn cao trào giật gân):**
   * **Horror Jumpscare Stinger:** Kết hợp sub-bass drop 38Hz + tiếng rít chói tai 1.840Hz + tiếng nện 65Hz đúng khoảnh khắc Thần Trùng lộ diện mắt đỏ.
   * **Funeral Gong:** Tiếng chiêng tang lễ đồng thau trầm u uất (110Hz/220Hz) khi thấy 31 người đội tang.
   * **Dread Impact Slam:** Tiếng nện kim loại kinh dị giáng xuống khi hé lộ bí mật rùng rợn (chiếc đầu thứ 32).
   * **Nguyên tắc đồng bộ:** Visual keyframe (đỉnh cử động tay, va chạm, mắt mở to, rung lắc) và acoustic impulse phải trùng khớp từng mili-giây.

---

## 5. Luật kiểm duyệt HyperFrames (Checklist)

1. **Temp Storage:** Luôn chạy `$env:TEMP = 'D:\temp'; $env:TMP = 'D:\temp'` trước khi render để tránh tràn ổ C:.
2. **Không animate clip trực tiếp:** Không dùng `tl.set` hay `tl.to` vào phần tử có `class="clip"`; chỉ animate các thẻ con bên trong.
3. **Tránh xung đột CSS Transform:** Không gán `style="transform: scaleY(0)"` cố định trong CSS nếu GSAP tween cũng điều khiển `scaleY`. Thay vào đó, khởi tạo bằng `gsap.set(..., { scaleY: 0 })` ở đầu timeline.
4. **Layout Overflow:** Gán `data-layout-allow-overflow` cho thẻ `#root`, các scene và `<svg>` để vượt qua kiểm tra layout an toàn.
5. **Đồng bộ thời lượng:** Duration của composition root và các track audio lấy chính xác tuyệt đối từ `manifest.json`.
