# Craft playbook — làm nhân vật, đạo cụ, bối cảnh và video cho đẹp (BẮT BUỘC theo AGENTS.md; đề xuất R10 chờ duyệt)

Dành cho **mọi agent** (Codex, Cursor, Claude, agent con…). Đây là cách làm đã cho ra kết quả đẹp và chạy được ở project mẫu `than-trung-chiec-khan-tang-thu-32`. Không "sáng tạo lại" quy trình: làm theo từng bước, dùng asset mẫu làm khuôn, **nhìn ảnh thật** trước khi báo xong.

> Nguyên nhân thường gặp khiến video/asset xấu: (1) vẽ từ trắng thay vì clone khuôn đã đẹp; (2) chỉ chạy lệnh check mà **không mở ảnh ra xem**; (3) tự viết HTML/GSAP riêng cho từng shot; (4) bỏ qua tỉ lệ/anchor nên người nổi/đạo cụ lệch; (5) màu hex, glow phẳng, CSS không tương thích HyperFrames. Playbook này chặn cả năm.

---

## 0. Ba nguyên tắc không thương lượng

1. **Nhìn rồi mới nói.** Mọi asset mới/sửa và mọi shot phải được **render ra PNG và bạn phải mở ảnh đó xem** (công cụ đọc ảnh, ví dụ `Read` file `.png`/`.jpg`) trước khi viết "xong". Lệnh `check` chỉ bắt lỗi cấu trúc — nó **không** bắt được ảnh đen, mặt trống, người lơ lửng, tỉ lệ sai. (Đã từng xảy ra: `library.py check` báo 0 lỗi nhưng cả sheet đen; mặt mọi nhân vật đen trong HyperFrames.) Nếu bạn **không xem được ảnh** → dừng và báo người dùng, không được tuyên bố đạt.
2. **Clone khuôn đẹp, đừng vẽ từ trắng.** Mới → chọn asset gần nhất trong `library/` (hoặc archetype+outfit) làm gốc, chỉnh phần khác. Danh sách "mẫu vàng" ở mục 6.
3. **Một generator, một nguồn dữ liệu.** Video chỉ dựng bằng `build_video.py` từ `manifest.json` + `bible.json` + `shotlist.json`. Cấm viết tay HTML/SVG/GSAP cho từng shot. Thiếu tính năng → **mở rộng generator** (rồi chạy lại cho mọi video), không vá riêng một video.

---

## 1. Vòng lặp bắt buộc cho mọi sản phẩm hình ảnh

```
làm  →  render ra PNG  →  MỞ ẢNH XEM  →  so với mẫu vàng/checklist  →  sửa  →  render lại  →  xem lại  →  báo cáo kèm đường dẫn ảnh
```

- Lặp tối thiểu **một vòng sửa** nếu lần xem đầu thấy bất kỳ điều gì lệch (người ta hay bỏ qua vì "gần đúng").
- Xem ở **kích thước dùng thật**: nhân vật ở cỡ ~150–250 px cao (cảnh toàn) chứ không chỉ cỡ phóng to.
- Báo cáo (R8.3) ghi: file ảnh đã xem, **điều đã thấy sai và đã sửa**, điều **chưa kiểm**. Không viết "trông ổn" chung chung.

---

## 2. Nhân vật (rig)

**Quy trình** (không bỏ bước):

1. `library.py list --kind archetype` → chọn `archetype` + `outfit` gần nhất (`library/rigs/archetypes.json`). Chỉ ghi đè tham số cần đổi (sẹo, râu, mắt đục, màu áo…). Nhân vật gần một nhân vật đã có → `"extends": "<id>"` + `rig_params` chỉ phần đổi. **Khuôn mới** (hình người/trang phục chưa có) → thêm vào `archetypes.json` (R2.8), không nhét riêng vào bible.
2. Khai trong `script/bible.json`: `id` (một id = một rig = một giọng), `archetype`/`outfit`, `voice`, cảm xúc dùng.
3. `build_rig.py --bible … --out projects/<slug>/assets/rig --script projects/<slug>/script/script.json` → phải **0 tổ hợp tràn khung**, id/giọng khớp script.
4. **Mở** `assets/rig/sheets/<id>.png` (pose sheet) và `sheets/lineup.png`. Kiểm bằng mắt:
   - Đủ 11 cảm xúc (`calm focused worried afraid shocked dread sad grief angry suspicious relieved`) và **mỗi cái nhìn khác nhau** ở cỡ nhỏ; mắt/mày/miệng đọc được.
   - Pose `idle clasp point-l reach-l raise-both`, `stance stand|sit`, `gaze center|left|right|up|down`, `khan on|off`: tay không xuyên thân, không cụt, không lìa khớp.
   - **Silhouette nhận ra được** từng nhân vật khi tô đen (tóc/khăn/râu/dáng khác nhau). Hai nhân vật chính trong cùng cảnh không được trông na ná.
   - Tỉ lệ khớp archetype (`head_scale` cho trẻ). Chân ở `(260,580)`, khung rig `0 0 520 600`.
5. Đưa pose sheet cho người dùng duyệt trước khi dựng shot (R3.7). Đổi thiết kế → build lại + duyệt lại.

**Chuẩn nghệ thuật** (khớp bộ rig hiện có — giữ đồng nhất phong cách):
- Nét viền tối `--pal-ink` ~4–6 px, bo tròn (`stroke-linecap/linejoin: round`); mảng màu **phẳng**, tối đa 2–3 sắc độ mỗi vật (nền + bóng); không gradient trên người.
- Mặt: elip lớn, mắt tròn trắng + đồng tử, mày điều khiển bằng biến CSS theo cảm xúc. Mặt phải đọc được ở 1/3 kích thước.
- Màu **chỉ là token** (`library/palettes/*.json`); cần màu mới → thêm token (R2.5). Cấm hex/rgb/tên màu trong tham số rig/generator.
- Trái/phải theo giải phẫu nhân vật (`l` = trái nhân vật).

**Cấm / bẫy đã gặp:**
- ❌ CSS có combinator `>` (vd `.mouth>*`) — **bộ scoper của HyperFrames bỏ cả khối `<style>`** → mặt đen. Dùng selector hậu duệ (có dấu cách). `library.py check` bắt với asset; với rig thì tự kiểm bằng snapshot.
- ❌ Chép `<g>` trần của rig vào svg cảnh. Rig **chỉ nhúng dưới dạng `<svg>` lồng** có viewBox riêng (pivot dùng `transform-box: view-box`; R3.4).
- ❌ Đổi trạng thái bằng cách sửa đường path. Chỉ đổi `data-emotion|mouth|pose|stance|gaze|blink|khan`.

---

## 3. Đạo cụ

**Quy trình:**

1. `library.py list --kind prop --tag <từ khoá>` rồi `library.py show <id>`. Có gần đúng → dùng lại, đổi `state`. Thiếu → **copy file mẫu vàng gần nhất** (mục 6) sang `projects/<slug>/assets/props/<id>.svg`, sửa hình, **đạt chuẩn library ngay** (R2.4–R2.7), khai `props` + `states` trong bible, rồi `library.py promote …` trước giai đoạn E (hoặc `project-only` + lý do).
2. Chuẩn file (`library.py check` kiểm, nhưng bạn vẫn phải xem ảnh):
   - Một SVG tự chứa; `data-lib-id`, `data-lib-kind="prop"` ở `<svg>`; **không** `<text>`, `<script>`, ảnh/URL ngoài.
   - **Gốc toạ độ = giữa-đáy**; `viewBox` vừa khít vật (không chừa lề thừa).
   - Trạng thái bằng `data-state` trên phần tử gốc + lớp `st st-<state>`; CSS liệt kê đủ state; mỗi state phải **nhìn khác hẳn**.
   - Phần động (`parts`: ngọn lửa, khói, chày, vải…) có `class` và pivot ghi trong `index.json` (`transform-box: view-box; transform-origin: <x>px <y>px`).
   - `id` nội bộ có tiền tố riêng (`cndl-glow`…), màu = `var(--pal-<token>)`.
   - **Vùng sáng/glow = `radialGradient` có stop-opacity giảm dần**, không phải hình tròn phẳng. (Đã sửa lỗi này một lần: glow phẳng trông như đĩa dán.)
   - Có `slots` nếu có đạo cụ con (nến trên bàn thờ) và `scene_s` (tỉ lệ khi đặt vào bối cảnh 1920×1080).
3. Thêm vào `library/index.json` (states, tags, parts, slots, `scene_s`), `library.py check` → 0 lỗi, `library.py sheet`, **mở `library/sheets/props.png`**: mọi state hiện đúng, không state nào trống/chồng nhau, phần động quay quanh đúng điểm.
4. **Thử trong cảnh thật** trước khi tin: ghép vào một bối cảnh ở `slots` + một nhân vật cạnh nó, render, xem tỉ lệ (nến không to hơn bàn thờ, bát hương không chìm).

**Cấm:** hex; vẽ đạo cụ "tại chỗ" trong HTML một shot; sửa bản chép trong project thay vì sửa ở `library/` (R2.3); đổi tên/xoá state đã có (chỉ được thêm — cần phá vỡ thì `<id>_v2`).

---

## 4. Bối cảnh

- Tra `library/locations/` (3 cảnh vẽ tay + 22 cảnh sinh bằng code). Cảnh sinh bằng code **sửa ở nguồn**: `scripts/bg_lib/` → `build_bg.py` → `import_bg.py` → `library.py check` + `sheet` → commit `library/` (không sửa tay file đã import).
- Chuẩn: 1920×1080, 3 lớp `layer-far/mid/near`, trạng thái ánh sáng `warm dark red_flash dawn` (+ `day night`), anchor `stand` L/C/R `{x,y,s}`, `slots`, `crop_9x16`.
- **Anchor phải kiểm bằng cách ghép nhân vật thật vào cảnh** (khung 16:9 và crop 9:16): chân chạm sàn, đầu không chạm trần, tỉ lệ so với đồ vật hợp lý. Không tin số suy ra tự động.
- Mỗi cảnh xem đủ trạng thái ánh sáng trong `library/sheets/locations.png`.

---

## 5. Dựng video (shotlist → `build_video.py`)

**Thứ tự** (không nhảy cóc; cổng máy chạy ở mỗi bước):

1. Chốt kịch bản + giọng (`manifest.json` là nguồn thời gian — không tự ghi số).
2. Bible + `library.py use` + `build_rig.py` + **duyệt pose sheet**.
3. Viết `script/shotlist.json` (theo schema workflow-v2 C2 + trường cho generator, xem mẫu `projects/than-trung-chiec-khan-tang-thu-32/script/shotlist.json`, shot SH001–SH013). `check_shots.py --project … [--scenes …]` → 0 lỗi.
4. `build_video.py --project … [--until SHxxx]` → `hyperframes lint` → `hyperframes check --json` (`ok: true`) → `hyperframes snapshot --at <giữa mỗi shot>` → **mở contact sheet / từng frame xem** → sửa nguồn (shotlist/bible/library/generator) → dựng lại.
5. Render nháp (`hyperframes render --quality draft`) để xem chuyển động; chỉ `--quality delivery` sau khi người dùng duyệt (R8.1).

**Chuẩn viết shot** (đây là chỗ quyết định "diễn tự nhiên"). Shot có đạo cụ: đọc thêm [`props-and-interaction-guide.md`](props-and-interaction-guide.md). SFX/góc quay: [`sfx-effects-camera-guide.md`](sfx-effects-camera-guide.md). Thao tác chi tiết (`reach`, `hand_over`, `move`, macro, bảng tình huống → thao tác, lỗi hay gặp): [`shotlist-guide.md`](shotlist-guide.md).

- **Mỗi câu thoại ngắn có ≥ 1 beat diễn** ở shot tương ứng (R5.1). Beat có `t` (giây, tính từ đầu shot), `do` (mô tả), `physical` (true nếu có tiếng động vật lý), và `set` (cái generator thực sự đổi): `{"<nhân_vật>": {"emotion":…, "pose":…, "gaze":…}, "light":"dark", "prop:<key>":"<state>"}`. **Beat không có `set` thì không ai thấy** — viết `set` cho mọi beat có thể nhìn thấy.
- Diễn bằng **chuyển trạng thái đúng lúc lời nói**: ánh nhìn đổi trước khi nhắc tới vật; biểu cảm đổi ở từ then chốt; tay chỉ/với đúng chỗ câu nhắc. Đừng để mặt đứng yên suốt shot.
- Beat vật lý (nhấc khăn, đặt, gạt, đóng cửa) **phải có SFX** trong `sfx[]` cách beat ≤ 0,15 s (R6.1). Khoảnh khắc cao trào: đổi `light` + stinger ở **cùng một thời điểm** (vd đèn tối + boom lúc "ba mươi hai").
- Nhịp & ngôn ngữ ống kính: shot 3–5 s, không tĩnh > 6 s, 12–15 shot/phút; xen toàn/trung/cận/macro/cutaway; **không 3 shot liền cùng cỡ hoặc cùng camera**; một cỡ không quá ~50%. `camera`: `push_in` cho cảm xúc dồn, `pull_out` cho mở rộng/cô lập, `pan_l/pan_r` cho dẫn mắt/tiết lộ, `static` cho nhấn mạnh sau cú sốc. `focus` chỉ rõ ống kính nhìn vào đâu (`<char>`, `prop:<id>`, `slot:<tên>`).
- Người kể (không lên hình) → dùng `cutaway`/`insert`/`establishing`: cảnh minh hoạ lời kể, không bắt nhân vật nhép miệng. Nhân vật tự nói → `characters[].mouth: true` (khẩu hình theo số âm tiết).
- Đặt người/đạo cụ **theo anchor** (`at: "L|C|R"`, `"stand:C"` + `dx/dy`, tên slot, hoặc `"<prop>.<slot>"`); không toạ độ tuỳ ý. Trạng thái đạo cụ chỉ đổi qua beat (R4.3).
- Ánh sáng theo cảm xúc: `warm` bình thường, `dark` căng/đe doạ, `red_flash` sốc, `dawn` kết thúc/giải toả. Ánh sáng chuyển bằng `set.light`, không bằng chỉnh tay.

**Xem snapshot — checklist mắt** (tick từng ô cho mỗi shot, ghi vào báo cáo shot nào lỗi):
- [ ] Chân nhân vật chạm sàn; không nổi, không chìm; tỉ lệ so với đồ vật hợp lý.
- [ ] **Mặt có đủ mắt/mày/miệng** (mặt đen/trống = CSS bị loại, xem mục 2 "Cấm").
- [ ] Biểu cảm/pose/gaze đúng với `set` của beat tại thời điểm chụp.
- [ ] Camera đóng khung đúng `focus`; không cắt mất đầu/tay quan trọng; có "không khí" quanh chủ thể.
- [ ] Ánh sáng đúng trạng thái; không có vùng đen vô lý; glow mềm.
- [ ] Đạo cụ đúng state (nến sáng/tắt, bát hương…) và đúng chỗ slot.
- [ ] Không có shot nào gần giống hệt shot liền trước.

---

## 6. Mẫu vàng (clone từ đây)

| Cần làm | Mở/clone |
| --- | --- |
| Nhân vật | `library/rigs/archetypes.json` (7 archetype × 4 outfit); ví dụ khai trong `projects/than-trung-chiec-khan-tang-thu-32/script/bible.json` (host, ong_cuu, me, ba_noi, than_trung) |
| Đạo cụ có state + phần động + glow | `library/props/candle.svg`, `oil_lamp.svg`, `incense_burner.svg` |
| Đạo cụ có slot chứa vật con | `library/props/ancestral_altar.svg` (xem `slots` trong `library/index.json`) |
| Bối cảnh vẽ tay | `library/locations/house_altar_room.svg`, `village_yard_night.svg` |
| Bối cảnh sinh bằng code | `scripts/bg_lib/*` (clone cảnh gần nhất) |
| Shotlist đầy đủ | `projects/than-trung-chiec-khan-tang-thu-32/script/shotlist.json` |
| Dựng video | `.agents/skills/video-pipeline/scripts/build_video.py` |

---

## 7. Lỗi kỹ thuật đã biết (đừng giẫm lại)

| Triệu chứng | Nguyên nhân | Cách đúng |
| --- | --- | --- |
| Mặt nhân vật đen trong HyperFrames, tĩnh thì đúng | CSS có `>`; scoper bỏ cả `<style>` | Selector hậu duệ; xem snapshot |
| Sheet/contact sheet đen toàn bộ | Chỉ nạp palette `base`, token palette khác không có giá trị | Nạp mọi palette asset dùng (đã sửa trong `library.py sheet`) |
| Glow trông như đĩa phẳng | `circle` + `opacity` | `radialGradient` stop-opacity giảm dần |
| Người nổi/chìm so với sàn | Anchor suy tự động, chưa ghép thử | Ghép nhân vật thật vào cảnh, chỉnh `anchors.py` |
| `Hex` bị `check_rules` báo trong generator | Màu viết cứng | Lấy từ palette token; thêm token mới nếu cần |
| `page.evaluate` treo khi debug | Trả về object GSAP khó serialize | `return 0` cuối hàm |
| Muốn xem runtime thật | — | `hyperframes preview --foreground --no-open --port N <dir>`, mở `http://localhost:N/api/projects/<tên thư mục>/preview` bằng Playwright, đo computed style |
| Dựng "xong" nhưng không có tiếng | `audio/voiceover.wav` không commit | Báo rõ "chưa có giọng"; chạy `build_voiceover.py` ở máy có VieNeu |

---

## 8. Mẫu báo cáo bằng chứng (R8.3) — dùng nguyên khung này

```
Làm: <1 câu>
Lệnh đã chạy: <lệnh> → <kết quả thật>   (check_rules / library check / check_shots / check_sync / hyperframes check)
Ảnh đã XEM: <đường dẫn .png> — thấy: <điều cụ thể>; lỗi phát hiện và đã sửa: <…>
Chưa kiểm: <liệt kê rõ: giọng, SFX nghe thử, render delivery, 9:16, người dùng duyệt…>
Tạo mới (nếu có): <asset> — lý do không dùng lại được asset nào: <…>
```

Thiếu "Ảnh đã XEM" cho một sản phẩm hình ảnh = báo cáo không hợp lệ.
