# Hướng dẫn viết kịch bản có bối cảnh, hành trình và logic liền mạch

Dành cho agent viết hoặc viết lại `script/script.json` (chế độ A, B, C). Máy kiểm: `scripts/check_script_logic.py` (mã SL1–SL11). Bổ sung cho `script-rewrite/SKILL.md` §3.1 (mô tả `visual`) và `script-schema.md`. Luật tương ứng là R13 trong `RULES.md` v3 (§9).

## 1. Vấn đề cần giải quyết

Trước đây một cảnh chỉ có `visual` (đoạn văn tự do) và `lines`. Từ đó máy và người đọc không biết được:
- nhân vật đang ở trong nhà hay ngoài sân, tại địa điểm nào của bible;
- cảnh trước họ ở đâu, **đi từ đâu tới đâu**, qua cửa/lối nào, mất bao lâu;
- ai đang có mặt, ai chỉ nghe qua điện thoại, ai đang cầm đạo cụ gì;
- đạo cụ đang ở trạng thái nào và ai làm nó đổi;
- giờ trong truyện có đi xuôi không (hồi tưởng, nhảy thời gian).

Ví dụ thật trong `than-trung-chiec-khan-tang-thu-32` (đo ngày 2026-11-27 trên S01–S08): S04 "bay chuyến tối rồi thuê xe về quê" không nói Lâm ở đâu trước đó; S05 nhảy từ ngoài sân vào gian thờ giữa chừng (câu "Vào thắp hương cho bà xong") mà `visual` chỉ ghi một cảnh; S03 là cuộc gọi video nhưng bà nội và mẹ ở đâu không ghi; S02 hồi tưởng nhưng chưa đánh dấu là hồi tưởng. Đây là nguồn gốc của shot "đúng từng câu mà sai tổng thể".

## 2. Học từ đâu (đã đọc, nêu đúng phần dùng)

| Nguồn | Điều lấy |
| --- | --- |
| [Final Draft: scene heading](https://www.finaldraft.com/blog/everything-that-should-and-should-not-be-in-a-scene-heading) | Mỗi cảnh mở bằng INT/EXT + địa điểm + thời gian; địa điểm gọi đúng một tên mỗi lần; đổi địa điểm hoặc trong/ngoài thì sang cảnh mới; CONTINUOUS chỉ dùng khi di chuyển ngay lập tức, LATER khi thời gian trôi ở cùng chỗ; không nhét hồi tưởng vào tiêu đề. → `setting.int_ext/location/time`, `link: continuous\|later`, `frame: flashback` |
| [Fountain](https://fountain.io/) và [Hekaya spec](https://michaelkmalak.github.io/hekaya/docs/spec/hekaya-markup-spec) | Heading tách thành vị trí/thời gian thành phần; spec không có trường liên tục (continuity) nên phải tự thêm. → `link`, `link_note`, `story_time` |
| Script supervisor (continuity sheet) | Ghi lại ai ở đâu, cầm gì, trạng thái vật qua các cảnh. → máy mô phỏng thế giới giữa các cảnh |
| [SCORE (arXiv 2503.23512)](https://arxiv.org/pdf/2503.23512) | Theo dõi trạng thái vật chính (còn/mất/hỏng); vật đã mất mà tái xuất không lời giải thích bị đánh dấu là lỗi liền mạch. → `holding`, `give/take/put`, `set_state` kiểm theo state trong bible |
| [CML-Bench (arXiv 2510.06231)](https://arxiv.org/html/2510.06231v1) | Đo kịch bản theo ba trục: mạch hội thoại, nhất quán nhân vật, hợp lý của diễn biến; prompt có hướng dẫn theo thành phần (scene heading, action, thoại, chuyển cảnh) cải thiện độ nhất quán. → cấu trúc ép buộc từng thành phần, kiểm máy phần đo được |

Giới hạn: các nguồn trên là quy ước nghề và nghiên cứu về văn bản; mình chưa chạy thử riêng phương pháp nào của họ. Mình chỉ lấy ý tưởng cấu trúc rồi tự viết kiểm tra, và đã thử trên kịch bản thật và bộ test ở §8.

## 3. Mô hình dữ liệu

### 3.1 Trong `bible.json` — mỗi địa điểm
```json
{"id": "loc_gian_tho", "lib": "house_altar_room", "kind": "int",
 "connects": [{"to": "loc_san_dem", "via": "cửa chính"}, {"to": "loc_hien_nha", "via": "cửa hông"}]}
```
- `kind`: `int` (trong nhà) hoặc `ext`. Hiên/sân/rạp là `ext`.
- `connects`: địa điểm **kề nhau**, đi bộ được; mặc định hai chiều (`"oneway": true` để một chiều). Sơ đồ này là nguồn duy nhất để biết "đi từ A sang B được không". Thiếu liên kết thật thì thêm vào đây, không nói miệng.
- `lib` hoặc `pending`: chưa có bối cảnh trong library thì ghi `"pending": "<lý do>"` (check_rules cho qua demo, chặn từ `--phase full`); tra `library.py list --kind location` trước (R2.1).

### 3.2 Trong `script.json` — mỗi cảnh
```json
{
  "id": "S06", "title": "...",
  "setting": {
    "location": "loc_gian_tho",   // id trong bible.locations
    "int_ext": "int",              // phải khớp bible.kind
    "time": "dawn",                // day | night | dawn | dusk
    "story_time": "N2 05:00",      // mốc trong truyện: N<ngày> HH:MM
    "frame": "present",            // present | flashback | dream | phone | cutaway
    "link": "later",               // continuous | later | cut | travel
    "link_note": "…",              // bắt buộc khi travel; nên có khi from khác chỗ cũ
    "moves": [{"after": "S06_L09", "to": "loc_san_dem", "via": "cửa chính"}]   // cả nhóm đổi chỗ giữa cảnh
  },
  "cast": [
    {"id": "host", "stance": "kneel", "at": "linh cữu"},
    {"id": "ong_cuu", "start": false, "holding": ["hu_sanh"]},
    {"id": "ba_noi", "presence": "remote"}
  ],
  "staging": [
    {"after": "S06_L01", "who": "ong_cuu", "do": "enter", "from": "loc_san_dem", "via": "cửa chính"},
    {"after": "S06_L07", "who": "ong_cuu", "do": "gesture", "note": "giơ ba ngón tay"}
  ]
}
```

**`frame`**: `present` = dòng truyện chính, thay đổi "thế giới" (ai ở đâu, ai cầm gì). `flashback`, `dream`, `phone`, `cutaway` (cắt chen, teaser) vẫn kiểm staging nhưng **không đổi** thế giới; cảnh present kế tiếp được so với cảnh present liền trước, không so với cảnh hồi tưởng.

**`link`** (so với cảnh present liền trước):
- `continuous`: ngay sau đó; phải **cùng chỗ hoặc kề nhau** (bible.connects). Ai đổi chỗ phải khai `from` đúng chỗ cũ.
- `later`: cùng địa điểm, thời gian trôi (`story_time` phải lớn hơn).
- `cut`: nhảy sang nơi/thời điểm khác; ai đổi chỗ phải khai `from`.
- `travel`: đi quãng dài; bắt buộc `link_note` (bằng gì, bao lâu).

**`cast`**: ai **có mặt** trong cảnh. Người kể (`role: narrator`) không cần khai nếu chỉ lồng tiếng; nếu hiện hình thì khai như nhân vật. `presence`: `physical` (mặc định), `remote` (qua điện thoại/video, không chiếm vị trí), `voice` (chỉ nghe tiếng). `start: false` = vào giữa cảnh, phải có `staging.enter`. `from` = địa điểm nhân vật đến từ, **bắt buộc khi khác chỗ so với cảnh trước**. `holding` = đạo cụ đang cầm lúc bắt đầu cảnh. Người nói (không phải narrator) mà không có trong cast thì lỗi.

**`staging`**: hành động có hệ quả logic, sắp theo thứ tự line (`after` = line id). `do`:
`enter` (vào, kèm `from` kề + `via`), `exit` (ra, kèm `to` kề), `move`, `sit`, `stand`, `take`/`give`/`put` (kèm `prop`, `give` có `to`), `set_state` (kèm `prop` + `state`), `look`, `react`, `gesture`. Ghi `note` bằng lời cho người đọc và để sau này sinh beat.

## 4. Quy trình viết (làm theo thứ tự)

1. **Vẽ bản đồ trước khi viết**: liệt kê địa điểm trong bible (`library.py list --kind location`, tra trước), mỗi nơi ghi `kind` và `connects`. Chưa có bối cảnh → `pending` + lý do, không đặt tên tại chỗ.
2. **Lập dòng thời gian**: mỗi cảnh một `story_time` (`N1 14:50`). Câu "chiều hôm ấy", "sáng hôm sau" trong lời thoại phải khớp mốc này (tính từ chính lời của nguồn, R7.1; mốc không có trong nguồn thì ghi là đề xuất trong `note`).
3. **Mỗi lần đổi địa điểm hoặc trong/ngoài = một cảnh mới** (như scene heading). Nếu viết lại cảnh đã có id thì dùng `setting.moves` để khỏi đổi id line đã gắn với shotlist; cảnh mới thì tách hẳn.
4. **Ghi hành trình**: nhân vật nào đổi chỗ so với cảnh trước đều có `from` (đi từ đâu), `via` ở `enter/exit`, và `link_note` khi khoảng giữa dài. Một câu như "tôi vào thắp hương rồi hỏi mẹ" nghĩa là có `moves` hoặc cảnh mới, không phải chỗ để máy đoán.
5. **Đánh dấu hồi tưởng, điện thoại, giấc mơ**: `frame` đúng; người ở đầu dây kia là `presence: remote`.
6. **Theo dõi đạo cụ**: ai cầm gì từ đầu cảnh (`holding`), đổi chủ chỉ bằng `give`/`take`, đổi trạng thái chỉ bằng `set_state` trong danh sách `states` của bible. Đạo cụ nào không có trong bible thì thêm vào bible trước (R4.1).
7. **Mỗi người có mặt có hành vi**: cảnh ≥ 2 người thì mỗi người ≥ 1 mục `staging` (khớp R11.1). Ai cố ý đứng im thì ghi `role_note` nêu lý do.
8. **Chạy gate**: `python .agents/skills/video-pipeline/scripts/check_script_logic.py --project projects/<slug> [--strict]`. Lỗi thì sửa nguồn rồi chạy lại. `--strict` (cảnh thiếu `setting` là lỗi) bắt buộc trước khi chốt kịch bản và chạy TTS (R1.5); `gates.py --phase full` tự bật.
9. **Đọc lại một lượt** như người xem: câu thoại có nói trái với bối cảnh/giờ đã khai không (máy chỉ bắt phần đo được, §6).

## 5. Máy kiểm gì (mã SL)

| Mã | Bắt |
| --- | --- |
| SL1 | thiếu hoặc sai `setting` (location không có trong bible, `int_ext` ≠ `kind`, time/frame/link lạ). Thiếu: lỗi khi `--strict`, cảnh báo nếu không |
| SL2 | người nói (không phải narrator) không có trong cast |
| SL3 | `continuous` không kề nhau; `later` khác chỗ hoặc không có thời gian trôi; `travel` thiếu `link_note` |
| SL4 | đổi địa điểm giữa hai cảnh mà không khai `from`; `from` ≠ chỗ cũ khi continuous; từ xa quá mà thiếu `link_note` (cảnh báo) |
| SL5 | `enter/exit` không nối kề; hành động sau khi đã `exit`; `after` không phải line của cảnh hoặc ngược thứ tự; `start:false` thiếu `enter` |
| SL6 | `give` khi không cầm; đổi người cầm giữa cảnh không có give/take; state ngoài `states` của bible |
| SL7 | `story_time` đi lùi trong dòng present; (cảnh báo) giờ không hợp `time` |
| SL8 | `cast` không có trong bible.characters |
| SL9 | (cảnh báo) cảnh ≥ 2 người có người không có hành động; ai đó biến mất giữa hai cảnh liền nhau cùng chỗ |
| SL10 | (cảnh báo, heuristic) người kể dùng "tao/mày" (có thể là lời nhân vật khác), nhân vật tự gọi tên mình ngôi ba ("Ông Cửu nói…" do chính ông đọc), tên gõ lặp ký tự ("Cửuu") |
| SL11 | `shot.location` ≠ địa điểm hiệu lực của line trong kịch bản (cutaway/insert chỉ cảnh báo) |

Không kiểm được (cần người đọc): lời thoại có mâu thuẫn với giờ/địa điểm đã khai không, nhân vật có biết điều chưa được kể không, động cơ hợp lý, nhịp. Máy chỉ bảo đảm dữ liệu tự nhất quán, không bảo đảm truyện hay.

## 6. Ví dụ đã chạy (than-trung S01–S08)

Dòng thời gian suy ra từ chính lời kể: bà nội mất 15:40 chiều ngày 1 (S04_L03), cuộc gọi video "gần ba giờ" cùng chiều (S03_L04), Lâm bay tối rồi "gần nửa đêm" tới đầu làng (S04_L06), ông Cửu đến "lúc gà gáy" (S06_L01), "sáng hôm ấy" ra rạp (S08_L01). Gán: S03 `N1 14:50`, S04 `N1 23:30` (`link: travel`, `link_note` lấy từ S04_L05, Lâm `from: loc_cong_truong`), S05 `N1 23:50`, S06 `N2 05:00`, S07 `N2 05:30`, S08 `N2 08:00`. Các mốc ngày/giờ là **đề xuất bám lời kể**, không phải số liệu của nguồn.

Bố trí không có trong lời kể (ví dụ bố mẹ ở gian thờ trong S06–S07, lối đi sân → rạp, `loc_duong_que` dùng `toan_canh_lang`) đã ghi `note: đề xuất` để người dùng sửa. S09–S20 chưa gán `setting`: gate báo cảnh báo, `--strict` sẽ báo lỗi cho đến khi làm.

Việc gate tìm ra khi chạy thử (không phải do mình soi bằng mắt):
- thứ tự `staging` của chính mình viết ngược line (S03, S06) → SL5, đã sửa;
- "Cửuu" gõ lặp ở S06/S08 (máy báo 8 câu; tìm thấy 15 dòng trong mỗi file) → SL10, đã sửa thành "Cửu" trong `script.json` và `script.md`;
- S07_L07 đến L10: lời ông Cửu kể về bố ông ("Bố tao nhốt…", "Đám ấy bà mày mười hai tuổi…") đang gán `speaker: host`; máy bắt được L07 và L08a nhờ "tao/mày" (SL10), L09 và L10 là suy luận của mình theo mạch kể, máy không bắt. **Chưa sửa**: đổi speaker là đổi giọng đọc (TTS), cần người dùng quyết;
- S08_L21: "Ông Cửu nói, vì mày là đứa về muộn nhất…" gán `ong_cuu` nên ông tự gọi tên mình → SL10. **Chưa sửa**, cùng lý do;
- S02 hồi tưởng có cậu bé Lâm nằm trên chõng (theo `visual`) nhưng bible chưa có nhân vật Lâm nhỏ → chưa đưa vào `cast`, cần tạo nhân vật (R3) nếu muốn hiện;
- S03 cần bối cảnh công trường/lán tôn mà library chưa có → `loc_cong_truong` đang `pending`; từ `--phase full` check_rules sẽ chặn cho tới khi tạo theo chuẩn rồi promote;
- S01 hook: SH006 (cutaway) ở sân trong khi `setting` của S01 là gian thờ → SL11 cảnh báo, hợp lệ vì là cutaway.

## 7. Nối với shotlist

`shotlist.shot.location` phải bằng địa điểm hiệu lực của line đầu shot (SL11). Khi viết shotlist: lấy địa điểm, giờ (`time` → `light`), người có mặt (cast), đạo cụ đang cầm/đổi (`staging`) từ kịch bản, không nghĩ lại. Chuyển `staging` thành beat tự động chưa làm (xem §9).

## 8. Kiểm thử đã chạy

`python .agents/skills/video-pipeline/scripts/tests/test_script_logic.py`: kịch bản mini 2 cảnh; bản đúng phải sạch; 20 biến thể hỏng, mỗi biến thể phải bị bắt đúng mã (SL1–SL8, SL10, SL11; SL9 chưa có ca test), kèm 2 ca "không được báo oan" (exit rồi sang cảnh sau không cần `from`; hồi tưởng chen giữa không làm hỏng liên tục). Kết quả khi viết: qua hết. Chạy trên project thật: `check_script_logic.py --project projects/than-trung-chiec-khan-tang-thu-32`: 0 lỗi, 5 cảnh báo (liệt kê ở §6) với 8/20 cảnh có `setting`.

## 9. Chưa làm và đề xuất

- **Chưa kiểm**: S09–S20 chưa gán `setting`; chưa chạy quy trình này từ đầu cho một kịch bản mới (chế độ C); chưa đo xem agent khác (Codex, OpenCode) làm theo có ra kịch bản tốt hơn không.
- **Chưa làm**: sinh beat/`shotlist` từ `staging`; nhân vật theo dõi trang phục/vết thương/cảm xúc qua cảnh; lối đi nhiều bước (`connects` mới kiểm kề 1 bước, đi qua 2 chỗ phải khai `link_note`); kiểm bằng LLM về mâu thuẫn trong lời thoại.
- **Luật**: người dùng đã cho phép sửa luật (2026-11-27); nội dung đã vào `RULES.md` v3 thành R13.1–R13.5 (RULES.md là bản chính, guide này không lặp lại).
