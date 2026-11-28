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
| Archetype | `adult_m`, `adult_f`, `young_adult_m`, `young_adult_f`, `elder_m`, `elder_f`, `teen`, `teen_f`, `child`, `child_f`, `spirit_shadow` |
| Cast (nhân vật đã dựng) | `nam_tre_do_tang`, `thay_cung_ong_gia`, `nu_trung_nien_do_tang`, `ba_cu_nau_song`, `bong_den_mat_trang` (xem `sheets/cast-lineup.png`, từng pose sheet ở `sheets/cast/`) |
| Outfit | `mourning`, `ao_the_indigo`, `nau_song`, `plain_light` |
| Đạo cụ | `candle`, `oil_lamp`, `incense_burner`, `ancestral_altar`, `clay_jar`, `betel_mortar`, `bamboo_bed`, `bamboo_tray`, `mourning_cloth`, `smartphone` |
| Bối cảnh (vẽ tay) | `house_altar_room`, `village_yard_night`, `veranda_night` |
| Bối cảnh (sinh bằng code, 22) | `nghia_dia`, `toan_canh_lang`, `gian_tho_dem`, `bo_song`, `gieng_lang`, `bui_tre_chuoi`, `truong_bo_hoang`, `nha_hoang`, `canh_dong_lua`, `rap_dam_tang`, `nui`, `chua`, `nha_ve_sinh`, `mieu_dinh`, `song`, `cay_da`, `san_nha`, `nha_bep`, `phong_ngu`, `phong_khach`, `nha_co_nha_tho_ho`, `nha_cap_bon` |
| Palette | `base`, `folk-horror-vn`, `scenery-vn` (91 token `bg_<hex>` của 22 cảnh sinh bằng code) |

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

## Bối cảnh sinh bằng code (22 cảnh)

Nguồn: `.agents/skills/video-pipeline/scripts/bg_lib/` → `build_bg.py` ra `assets/library/bg/*.svg` → **`import_bg.py`** chuyển vào `library/locations/` đúng chuẩn R2.5–R2.7 (màu → token `bg_<hex>` trong `palettes/scenery-vn.json`, id nội bộ có tiền tố, CSS chặn phạm vi theo `data-lib-id`, ánh sáng đổi tên `candle_warm→warm`, `dusk→dawn`; giữ thêm `day`, `night`).
- Sửa cảnh: sửa `bg_lib/` → `build_bg.py` → `import_bg.py` → `library.py check` → `sheet` → xem ảnh → commit. **Không sửa tay** file trong `library/locations/` của nhóm này (lần import sau sẽ ghi đè; mục index có `"origin": "build_bg"`).
- Thêm tuỳ chọn `data-mood="creepy"` (sương, vignette, nhiễu hạt) trên thẻ `<svg>`.
- `stand` (L/C/R: `x,y,s`), `floor_y`, `crop_9x16.center` của nhóm này lấy từ `bg_lib/anchors.py` (sửa ở đó rồi `import_bg.py`; `anchors_reviewed: true`). Đã ghép nhân vật `host` kiểm ở khung 9:16; `s` nhỏ (0.55–0.6) cho cảnh toàn/xa. `slots` đạo cụ vẫn trống: đặt khi cần.
- Token đặt tên theo giá trị màu (chưa gom theo ngữ nghĩa); muốn đổi tông cả kho thì sửa giá trị trong `scenery-vn.json`.
- Ba cảnh vẽ tay và nhóm 22 cảnh có trùng chức năng (gian thờ, sân/hiên nhà); chưa hợp nhất — project mẫu đang dùng bản vẽ tay.

## Hành vi mẫu (`library/behaviors/behaviors.json`)

Macro tái dùng cho beat diễn xuất. Trong `shotlist.json`: `{"line_id":"S01_L07","word":9,"macro":"nhin_sang","args":{"char":"host","target":"me"}}`
(không cần `do`; macro tự sinh). `build_video.py` và `check_shots.py` cùng bung macro qua `scripts/behaviors.py` nên E5/E7/R6.1 vẫn kiểm đủ;
macro vật lý tự thêm SFX. Beat viết tay vẫn dùng được cùng macro. Lệnh: `python .agents/skills/video-pipeline/scripts/behaviors.py list|check`.
Thêm macro mới: chỉ thêm, không đổi tên/xoá (như R2.3); `behaviors.py check` phải 0 lỗi.
Sheet duyệt bằng mắt: `python .agents/skills/video-pipeline/scripts/behavior_sheet.py --project projects/<slug>` → `library/sheets/behaviors.png`
(trạng thái cuối của từng macro trên hai nhân vật thật; phần chuyển động xem ở snapshot shot). Gate E9 trong `check_shots.py` kiểm macro/beat chỉ nhắc nhân vật, đạo cụ có trong shot.

### Hành động thân người (rig) và macro tương ứng
`data-stance`: `stand | sit | kneel | lay | stagger[-r] | tilt[-r] | lie[-r]` (quỳ, lạy/quỳ rạp, loạng choạng, nghiêng đổ, nằm; `-r` = ngã về bên phải người xem).
`data-pose` mới: `run-a/run-b` (chạy), `cover-head` (ôm đầu), `pray` (chắp tay trước ngực), `prostrate` (chống tay khi lạy).
`move` có `gait: "run"` (nhịp chân 0,16 s, nảy 6 px). Macro: `quy_xuong`, `quy_lay`, `dung_day`, `chay_toi`, `om_dau`, `ngat` (3 khung 0,18 s + SFX ngã ở khung cuối).
Lưu ý dàn cảnh: người nằm (`lie`) dài ~480 px ở scale 1 và chân/đầu có thể đè nhân vật bên cạnh — chừa chỗ hoặc đổi `suf`/vị trí.

### Chuỗi ghép sẵn và tự quay mặt
Macro nhiều bước (nhịp chỉnh bằng tham số, SFX đi theo nhịp): `cau_xin` (quỳ → lạy → ngẩng; `gap`, `gap2`), `chay_roi_om_dau` (`dur`, `after`), `soc_roi_ngat` (`suf`), `so_roi_bo_chay` (`dur`), `vai_chao` (`gap`).
`view: "auto"` trong `beat.set` (mặc định của `quy_xuong`/`quy_lay`/`cau_xin`): quay mặt về nhân vật gần nhất tại thời điểm beat; không tự quay lại nếu người kia đi chỗ khác — khi đó ghi lại beat `set {view: auto}`.

## IK tay — beat `reach` (prototype)
Tay không còn chỉ nhảy giữa các góc pose cố định: beat `reach` cho tay với tới một điểm bằng IK giải tích 2 khúc (`scripts/ik.py`).
```json
{"line_id":"L01","t":0.3,"do":"…","reach":{"char":"host","side":"l","to":{"prop":"mam_tre"},"dur":0.6,"hold":1.2}}
```
- `to`: `{"prop":key}` | `{"char":id,"hand":"l|r"}` | `{"x","y"}` (toạ độ cảnh) | `{"rel":[dx,dy]}` (px rig, tính từ vai). `side` mặc định = phía đích.
- Cơ chế: rig đọc `--ik-ul|fl|ur|fr` (CSS var, rơi về góc pose khi không đặt); generator tween các biến này, hết `hold` thì tween về góc pose rồi `clearProps`.
- Giới hạn đã biết: chỉ stance stand|sit, view front (kneel/lie/3-4 lệch trục); đích quá tầm >25 px → generator báo lỗi; đích sát vai (<40 px) khuỷu mơ hồ; đạo cụ không tự "dính" vào tay trong beat `reach` (chỉ `hand_over` mới mang đạo cụ).

### `hand_over` bằng IK (đạo cụ bám bàn tay)
`{"hand_over":{"prop":"mam_tre","from":"me","to":"host","dur":1.4,"held":true}}` + `physical:true` + SFX (R6.1).
Người cho với tới đạo cụ → mang tới điểm gặp (giữa hai vai) → người nhận với tới → người cho thả, người nhận mang đạo cụ về tay nghỉ.
Generator lấy mẫu FK bàn tay mỗi 1/24 s và tween đạo cụ theo đúng vị trí đó. Đạo cụ luôn thẳng đứng (phần tử cảnh); được vẽ TRÊN nhân vật.
- `held:true`: đạo cụ đã ở trong tay người cho (bắt đầu từ bàn tay nghỉ). Không có → đạo cụ phải nằm trong tầm tay người cho, nếu không generator báo lỗi (đưa nhân vật lại gần bằng `move`).
- Sửa lỗi cũ: tween x,y trước đây nhắm `<g data-state>` (không có x/y) nên đạo cụ không hề di chuyển; nay nhắm `<svg id="<pid>-pos">`.

### Thân nghiêng và ánh mắt khi với tay (bước b)
- Rig có nhóm `.upper` (thân+tay+đầu) xoay quanh hông theo `--lean` (độ). IK giải trong hệ của `.upper` đang nghiêng (`ik.solve_arm_leaned`) nên bàn tay vẫn trúng đích.
- `reach`: `lean` = `"auto"` (mặc định, tối đa 9° về phía đích) | số độ | `false`; `gaze` = true (mặc định) | false — mắt liếc theo đích.
- `hand_over`: thân cả hai nghiêng dần tới điểm gặp rồi thẳng lại; mắt cả hai theo đạo cụ (12 lần/giây). Tắt bằng `"lean": false` / `"gaze": false`.
- Giới hạn: mắt chỉ liếc tối đa 5 px ngang / 4 px dọc (như `data-gaze`) — đầu không quay; nghiêng chỉ sang ngang (khung 2D chính diện không có chiều "về phía trước"); đầu nghiêng cùng thân.

### Giới hạn khớp và điểm nắm đạo cụ (bước c)
- **Giới hạn khớp** (`ik.LIMITS`, độ, phía arm-l; arm-r đối xứng): vai −165..15, khuỷu −150..100 (rộng hơn mọi pose đã duyệt). IK bỏ nghiệm vi phạm giới hạn; không còn nghiệm hợp lệ → kẹp góc và bàn tay dừng ngắn đích, generator báo lỗi "trượt đích" (>25 px rig) thay vì bẻ khớp ngược.
- Ghi đè theo beat: `"limits":{"up":[-85,4],"fore":[-50,0]}` trong `reach` / `hand_over` (ví dụ dải cầm đèn dầu).
- **Điểm nắm** (`grip` trong `library/index.json`, chỉ THÊM — R2.3): `{"a":[fx,fy],"b":[fx,fy]}` là phân số 0..1 của hộp đạo cụ; a = mép trái, b = mép phải (b mặc định = a). `bamboo_tray`: a=(0.1,0.68), b=(0.9,0.68); `oil_lamp`: a=(0.5,0.85) (phần bầu dầu). Thiếu `grip` → nắm tâm.
- `hand_over`: người cho cầm mép phía mình, người nhận cầm mép đối diện; điểm gặp được chọn để cả hai tay duỗi vừa phải (không gập sát ngực — vì giới hạn khớp chặn). `reach` tới `{"prop":…}` với tới điểm nắm a.

## Tra cứu nhanh: `suggest` và cast
- `rigs/cast.json`: **nhân vật đã dựng và đã duyệt** (rig = archetype + outfit + tham số ghi đè, giọng gợi ý, pose sheet `sheets/cast/<id>.png`, `keywords`, `tags`). `library.py list --kind cast`, `show <id>` (in sẵn đoạn `rig` để dán vào bible). Thêm bằng `cast-add` (cần pose sheet, R10.4). Chỉ thêm, không đổi tên (R2.3).
- Mọi đạo cụ, bối cảnh, archetype, outfit, cast có `keywords` (từ/cụm từ tiếng Việt hay gặp trong kịch bản) và `tags` để máy khớp.
- `library.py suggest --project <slug>` | `--text "…"` [`--json`]: đếm từ khoá trong kịch bản rồi xếp hạng — bối cảnh THEO TỪNG CẢNH (★ = đã khai trong bible), đạo cụ toàn phim, cast/archetype/outfit cho từng nhân vật (tuổi + giới tính ghi trong bible thắng điểm từ khoá), và **THIẾU**: từ vựng trong `lexicon.json` có trong kịch bản nhưng chưa asset nào khớp → cân nhắc tạo mới (R2.4).
- Giới hạn đã biết: chỉ khớp theo từ khoá (không hiểu ngữ cảnh); từ chung như "nhà", "tang", "ma" có trọng số thấp nhưng vẫn gây nhiễu — luôn xem lại trước khi gán `lib`. `lexicon.json` là danh sách do người viết nên chưa bao quát. Cast hiện chỉ gồm 5 nhân vật của một project (mới chứng minh khớp với chính project đó và với một đoạn văn thử).


### Tham số rig thêm 2026-11-26
`hair: "bob"` (tóc ngang vai), `mustache: true` (ria mép, màu tóc), `beard_color: <token>` (mặc định `hair_white`). Token mới: `hair_grey`, `brow_grey`.

### Nhân vật chung (cast generic) 2026-11-26
12 nhân vật dùng cho nhiều phim, nguồn ở `library/rigs/cast_src/bible.json` (không thuộc project nào): ma nữ áo trắng, ma da, hồn nam đồ tang, ma trẻ em, dân làng nam/nữ đội nón lá, ông lão, thanh niên, cô gái, bé trai, thiếu niên, thiếu nữ.
- Dựng lại: `build_rig.py --bible library/rigs/cast_src/bible.json --out library/rigs/cast_src/build` (thư mục `build/` bị gitignore), xem pose sheet, rồi `library.py cast-add --src library --char <id> --id <id> --role ... --tags "a,b" --keywords "x,y"`.
- Tham số rig mới: `hair: "long_loose"` (tóc xõa dài), `hair_over_face: true` (tóc rủ che nửa mặt), `weeds: true` (rong rêu bám tóc, token `algae`/`algae_dark`), `hat: "non-la"` (nón lá, token `non_la`/`non_la_dark`). Archetype `ghost_woman`, `ghost_drowned`; outfit `ao_trang_ma`, `rach_ma_da`, `nong_dan_non_la`, `ba_ba_non_la`. Token da/áo ma mới ở `palettes/folk-horror-vn.json`.
- Ảnh tổng: `library/sheets/cast-lineup-generic.png`. Tuổi/vai là đề xuất thiết kế, chưa phải nguồn kịch bản.

### SFX mặc định của đạo cụ 2026-11-26
Mỗi đạo cụ trong `index.json` có `sfx`: `{"substitute": bool, "touch": "sfx/…", "state": {"<state>": "sfx/…"}}`. `check_shots` (E6) dùng làm gợi ý khi beat vật lý thiếu SFX. `substitute: true` = âm gần nhất trong kho (chưa có tiếng diêm/gốm vỡ…); báo cáo phải nói rõ. Thêm đạo cụ mới thì khai `sfx` khi `promote` (thêm `--meta` hoặc sửa index rồi `reindex`).

### Dựng nhóm cast chung và giữ mẫu vàng 2026-11-26
- `library.py cast-build`: dựng lại rig + pose sheet từ `library/rigs/cast_src/bible.json` (0 tràn khung, R3.8) và cập nhật `library/sheets/cast-lineup-generic.png`. Mỗi nhân vật có mục `cast` (role, age, gender, tags, keywords) trong bible đó; `cast-add --src library --all [--force]` đăng ký/làm mới cả nhóm, chạy lặp lại không đổi gì.
- `library.py cast-verify`: dựng lại rig của mọi cast từ tham số trong `cast.json` và so sha256 với `library/rigs/golden.json`. Đổi `build_rig.py`/archetype/token dùng chung thường làm đổi nhiều nhân vật cùng lúc; lệnh báo nhân vật nào đổi và xuất ảnh so sánh (trái = pose sheet đã duyệt, phải = dựng lại). Xem ảnh; cố ý thì `cast-verify --update`. Đã thử: đổi một hằng số tóc ở góc nghiêng → 23/23 báo ĐỔI; trả lại → KHỚP. Golden chỉ phát hiện rig SVG đổi, không đánh giá đẹp/xấu. Ảnh so sánh chưa có phần mô tả thiết kế ở tiêu đề (bible tạm không có `design`).
