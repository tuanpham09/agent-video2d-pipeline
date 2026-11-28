# Kịch bản kịch tính, giữ chân, gài mở – đóng

Bổ sung cho `script-continuity-guide.md` (liền mạch: ở đâu, đi đâu) và `script-rewrite/SKILL.md`. Continuity trả lời "có hợp lý không"; tài liệu này trả lời **"có khiến người xem không dám thoát không"**. Gate máy: `check_script_drama.py` (DR1–DR10). Phần hay/dở thật sự vẫn cần review độc lập (`script-review-protocol.md`) và người duyệt.

**Cách đọc độ tin cậy.** `[đã kiểm]` = có test chạy trong repo. `[nguồn]` = lấy từ tài liệu/paper đã đọc (ghi rõ nguồn). `[blog]` = số liệu của bài blog, tác giả không công bố phương pháp, **chưa kiểm**. `[đề xuất]` = thiết kế của repo này, chưa thử trên video thật.

---

## 1. Vấn đề

Kịch bản đúng logic vẫn có thể nhạt: mọi thứ xảy ra "vì tác giả muốn", không có thứ gì được gài rồi trả, nên người xem không có lý do chờ. Ngược lại kịch bản hấp dẫn mà hở: manh mối xuất hiện không ai nhắc lại, luật ma quái đổi giữa chừng, hung thủ lộ ra mà trước đó không có dấu vết nào. Ba lỗi hay gặp khi viết bằng agent: **setup không trả** (khẩu súng Chekhov không nổ), **payoff đến trước trigger** (tiết lộ sớm), **cú twist không có manh mối công bằng**.

## 2. Nguồn đã học và phần dùng

| Nguồn | Điều lấy | Độ tin cậy |
| --- | --- | --- |
| *Codified Foreshadowing-Payoff Text Generation*, arXiv 2601.07033 | Mỗi setup là một bộ **Foreshadow–Trigger–Payoff**: setup tạo "nợ nhân quả", payoff chỉ được xảy ra khi trigger đã xuất hiện; giữ một **danh sách nợ chưa trả** làm trạng thái tường minh; hai lỗi cần bắt: payoff **sớm** và setup **không bao giờ được trả**. Paper đo trên tóm tắt sách, tự động trích triple vẫn có thể sót/bịa. | [nguồn] → `loops[]`, DR3, DR4 |
| *Lost in Stories: Consistency Bugs in Long Story Generation*, arXiv 2603.05890 (ConStory) | Lỗi nhất quán dồn ở nhóm **thời gian & logic cốt truyện** và **sự thật/chi tiết**, hay nằm ở **giữa** truyện; đo bằng mật độ lỗi trên 10 000 từ. Bản gốc dùng LLM làm giám khảo, không phải luật tĩnh. | [nguồn] → review độc lập tập trung phần giữa |
| Horror Structure Paradigm (whatsleepsbeneath.com) | Chuỗi beat kinh dị: mở nhanh → có gì đó "lạ" → "vì sao bây giờ" (lỗi/lời nguyền/điều ước hỏng) → thảm hoạ đầu → điểm không quay lại → kế hoạch → **thất bại ở midpoint** → leo thang → đỉnh → mở/đóng; "một cú doạ khoảng mỗi 10 trang, cú lớn trong 3–5 trang đầu"; ma không nói lý lẽ thường nhưng **luật của nó phải nhất quán**. | [nguồn] → `beat`, DR6 |
| VSAText "Narrative Structure" | Mỗi beat gắn đúng một cảnh, thứ tự tăng dần, vị trí % hợp lệ (midpoint ≈ 50%); cảnh phi tuyến phải khai kỹ thuật. | [nguồn] → DR6 midpoint 35–65% |
| Bài "Hook Engineering" (dev.to) | Hook 1–3 s, không chào hỏi/dẫn nhập, mở một vòng lặp tò mò, hình đầu phải đọc được khi tắt tiếng. Các con số 68%/47%/60% **không có phương pháp công bố**. | [blog], chưa kiểm → DR2 chỉ kiểm hình thức |
| Repo `bybren-llc/story-systems-template` (skill `story-structure`) | Chỉ đọc được trang tóm tắt: ba hồi 25/50/25 và vị trí beat. Không thấy rule kiểm. | chưa dùng |

Không tìm được repo nào trên GitHub có bộ kiểm "gài – mở" cho kịch bản video tiếng Việt; phần dữ liệu và gate ở đây là thiết kế của repo (xem `[đề xuất]` bên dưới).

## 3. Mô hình dữ liệu `[đề xuất, có test]`

Khối `drama` ở gốc `script.json`, và `scene.drama` ở từng cảnh (schema: `script.schema.json`).

```jsonc
"drama": {
  "promise": "vì sao cơ biết tên người chết",       // câu hứa: hook mở, payoff đóng
  "genre": "ghost_ritual",                            // ghost_ritual | feud_curse | love_charm | mystery | other
  "tension_pattern": "escalating_peaks",              // hoặc slow_burn
  "rules":  [{"id":"R1","text":"chỉ hỏi ba câu","cost":"câu thứ tư gọi chính người hỏi",
              "plant":"S1_L03","first_use":"S2_L02","violations":["S3_L04"]}],
  "loops":  [{"id":"M1","type":"mystery","question":"ai là người trả lời?",
              "plant":"S1_L02","clues":["S2_L03","S4_L02"],"payoff":"S6_L05"},
             {"id":"O1","type":"object","plant":"S1_L05","trigger":"S4_L05","payoff":"S6_L02"}],
  "motives":[{"char":"ngan","role":"protagonist","want":"…","obstacle":"…"},
             {"char":"hung","role":"antagonist","want":"…","obstacle":"…","secret":"…"}]
}
// mỗi cảnh:
"drama": {"beat":"first_disaster","tension":6,"turn":"Hưng bỏ vòng tròn muối",
          "hook_out":"Hưng đi đâu?","causes":["S2","R1"],"turn_at":"S3_L04"}
```

- **loop** = một bộ Foreshadow–Trigger–Payoff gắn vào **line id thật**. `type`: `clue` (manh mối), `object` (đạo cụ gài), `rule`, `promise` (lời hứa/cảnh báo), `mystery` (cần ≥2 `clues`), `red_herring` (đánh lạc, vẫn phải được trả: cho thấy vì sao nó sai), `line` (câu nói gài).
- **rule** = luật của thế lực siêu nhiên/lời nguyền. Bắt buộc có `cost`: luật không có giá thì vi phạm không đáng sợ.
- **causes** = cảnh hoặc loop/rule đã gây ra cảnh này; chuỗi nhân quả là thứ khiến kịch bản không "rời rạc".
- **tension** 0–10 tự chấm cho mỗi cảnh; gate kiểm *hình dạng* đường cong, không kiểm con số có đúng cảm giác hay không.

## 4. Quy trình viết (thứ tự bắt buộc) `[đề xuất]`

1. **Promise + logline** (1–2 câu): người xem chờ biết điều gì? Chưa có câu này thì chưa viết.
2. **Motives**: ai muốn gì, bị cản bởi gì, giấu gì. Kịch tính = muốn + bị cản. Thế lực ma/lời nguyền khai `role: force`.
3. **Rules** của siêu nhiên: mỗi luật một `cost`. Quyết **trước** khi viết cảnh; ghi `note: đề xuất` nếu không có trong nguồn (R7.1: không coi là sự thật của nguồn; luật dân gian có thật thì phải có nguồn).
4. **Chuỗi nhân quả (xương sống)**: viết 8–12 mệnh đề "vì A nên B, nhưng C nên D"; mọi mối nối là "nên/nhưng", **không phải "và rồi"**. Mối nối "và rồi" = chỗ rời rạc.
5. **Loops**: từ xương sống, chọn ≥3 thứ để gài (1 mystery có ≥2 clue công bằng, 1 object, 1 promise). Quyết **payoff trước, plant sau** (viết ngược từ cái kết), sau đó mới rải plant. Mỗi plant phải trông vô hại lúc đầu (chỉ thành manh mối khi nhìn lại).
6. **Beat sheet + đường căng**: gán `beat` và `tension` cho từng cảnh, theo mẫu thể loại (mục 6). Midpoint là **thất bại của kế hoạch đầu hoặc thông tin mới nâng rủi ro**, không phải cảnh nghỉ.
7. **Hook** (cảnh 1): câu đầu ≤14 từ, vào thẳng mâu thuẫn/hình ảnh lạ, **gài vòng lặp đầu trong 6 câu đầu**, không chào. Hình đầu đọc được khi tắt tiếng.
8. **Viết lời** theo `script-rewrite/SKILL.md` §3; mỗi cảnh có `turn` (điều thay đổi) và `hook_out` (câu hỏi kéo sang cảnh sau, trừ cảnh cuối).
9. **Gate**: `check_script_logic.py --strict` **và** `check_script_drama.py --strict` phải 0 lỗi.
10. **Review độc lập** (`script-review-protocol.md`): ít nhất 3 agent khác nhau, không thấy lập luận của người viết. Sửa theo mục "phải sửa", ghi quyết định cho mục còn lại vào `PROJECT.md`.

## 5. Gate kiểm gì và không kiểm gì

| Mã | Bắt |
| --- | --- |
| DR1 | thiếu `drama`/`scene.drama`, promise/genre/pattern sai |
| DR2 | hook: chào hỏi, câu đầu >14 từ, cảnh 1 không phải `hook`, chưa gài vòng lặp trong 6 câu đầu |
| DR3 | loop trỏ line không tồn tại; payoff trước trigger/plant; plant–payoff cách <3 câu |
| DR4 | setup không bao giờ được trả (trừ tối đa 1 `open` làm tease) |
| DR5 | luật thiếu `cost`; dùng luật trước khi người xem biết; luật không ảnh hưởng gì |
| DR6 | thiếu/đa `climax`; đỉnh không phải climax; không leo thang; nhịp phẳng ≥4 cảnh; midpoint lệch |
| DR7 | cảnh thiếu `turn`/`hook_out`; quãng >20 câu không biến cố |
| DR8 | mystery <2 clue hoặc clue sau payoff |
| DR9 | cảnh thiếu `causes`; nhân quả ngược |
| DR10 | motives thiếu want/obstacle, nhân vật ∉ bible, thiếu cặp chính/đối trọng |

**Gate không kiểm được:** manh mối có *thật sự* đủ để đoán không; luật có hợp lý/đáng sợ không; twist có bất ngờ không; thoại có tự nhiên không; plant có "vô hại" không; con số `tension` có đúng cảm giác không. Gate chỉ chứng minh dữ liệu gài–mở **nhất quán với chính nó**, không chứng minh khớp với lời thoại (agent có thể khai plant ở câu không hề chứa chi tiết đó). Vì vậy bước review độc lập đọc lại lời thoại là bắt buộc: reviewer phải tự dò setup/payoff rồi mới đối chiếu với `loops`.

## 6. Ba khung thể loại `[đề xuất; luật/cốt do repo nghĩ ra, không phải sự thật dân gian]`

Mỗi khung là **xương sống nhân quả** để clone, không phải kịch bản. Tên nhân vật, luật cụ thể, kết cục phải do nguồn/người dùng quyết; phần nào tự thêm phải `note: đề xuất`.

### 6.1 Cầu cơ ở nghĩa địa (`ghost_ritual`, nhóm bạn)
Chuỗi: **thách thức** (một người cược/khích) → **nghi thức có luật** (số câu hỏi, vòng bảo vệ, phải "tiễn") → **câu trả lời đầu đúng một chi tiết chỉ người chết biết** (clue 1, nhóm cười/nể) → **một người vi phạm luật vì động cơ riêng** (rule violation; cost hiện ra) → **thảm hoạ đầu** (không giết, chỉ gây tổn hại, ví dụ mất một người trong bóng tối) → **plan thất bại ở midpoint** (tiễn cơ không được, vì luật tiễn bị phá) → **leo thang**: thứ đi theo họ về, đúng nơi họ tưởng an toàn → **reveal**: câu trả lời đầu giờ có nghĩa khác (clue 1 + clue 2 công bằng chỉ về một người **trong nhóm**) → kết: trả giá hoặc mơ hồ.
Loop mẫu: *mystery* "ai thực sự đang trả lời" (≥2 clue: tên gọi cũ, vật chỉ một người mang theo); *object* vật bị bỏ lại ở nghĩa địa → xuất hiện ở nhà; *rule* "không quay đầu khi tiễn" → vi phạm → hậu quả.
Lỗi logic hay gặp: nhóm vẫn ở lại sau cú doạ thật mà không có động cơ giữ lại (cần `obstacle` cho lý do không bỏ chạy: đồ bị mất, người bị kẹt, thách đã đặt cược).

### 6.2 Nhà A thù nhà B, mời thầy (`feud_curse`)
Chuỗi: **mối thù có gốc cụ thể** (đất, nguồn nước, hôn ước, một cái chết) → **A mời thầy** (thầy ra điều kiện/giá) → **thuật ra đòn đầu lên B** (dấu hiệu nhỏ, chỉ người trong cuộc hiểu) → **B tìm thầy khác/hoá giải; hai thầy đối đầu** → **midpoint: thuật phản lại chủ** (thuật có luật: chỉ trúng người nó nhắm *đúng tên/đúng huyết*; A đã khai sai một chi tiết) → người vô can (đứa trẻ, người dâu) bị vạ → **reveal**: gốc thù không như hai nhà tin (clue gài từ đầu: lời một người già, một vật) → kết: cái giá thật của thầy, hoặc hoá giải đòi A trả đúng thứ đã giấu.
Loop mẫu: *promise* lời thầy dặn "đến ngày X không được mở cửa"; *object* vật A giấu; *mystery* "ai thực sự hưởng lợi từ cuộc thù" (≥2 clue).
Lỗi logic hay gặp: thầy quyền năng nhưng không dùng cho việc dễ hơn (cần `cost`/giới hạn cho thầy); hai nhà sống cạnh nhau mà không ai ép hoà giải (cần lý do không hoà giải ngay từ đầu).

### 6.3 Bùa yêu (`love_charm`)
Chuỗi: **khao khát bị từ chối** (người dùng bùa có lý do hiểu được) → **cầu bùa với điều kiện/giá** → **bùa có hiệu lực; người bị bùa "yêu" nhưng thiếu một chi tiết rất người** (clue: quên một thói quen, không còn sợ thứ từng sợ) → **vui trước, rạn sau**: người dùng bùa dần thấy tình yêu "rỗng" → **midpoint: muốn gỡ thì bị đòi cái giá đã giấu** → người thứ ba nhận ra điều bất thường → **reveal**: ai là người bị bùa *trước* / giá phải trả là gì → kết: gỡ bùa, mất nhau, hoặc chấp nhận một tình yêu giả.
Loop mẫu: *rule* "bùa mất hiệu lực nếu người bị bùa nhìn thấy [X]"; *object* vật làm bùa; *mystery* "người này yêu thật hay do bùa" (≥2 clue ở thói quen cũ).
Lỗi logic hay gặp: hiệu lực bùa tuỳ tiện (lúc mạnh lúc yếu mà không có luật) → luôn khai `rules` và giá.

> Chuỗi nhân quả ở trên ngắn gọn có chủ đích: người viết phải thay bằng sự kiện cụ thể của nguồn. **Mọi chi tiết dân gian (bùa, nghi thức, tên) phải lấy từ nguồn người dùng đưa hoặc ghi `note: đề xuất`** (R7.1).

## 7. Giữ chân người xem (hình thức, `[blog]` chưa kiểm, dùng như ràng buộc nhẹ)

- Câu đầu vào thẳng mâu thuẫn/hình lạ; không chào, không "hôm nay mình kể".
- Cứ 1–2 cảnh có **một biến cố** (plant/payoff/clue/vi phạm luật/đổi thế); gate cảnh báo khi >20 câu trống.
- Cuối cảnh để lại **câu hỏi chưa đóng** (`hook_out`); đóng vòng cũ **cùng lúc mở vòng mới** (payoff của loop này là plant của loop kế).
- Mỗi cảnh đổi một thứ người xem tin (`turn`). Cảnh nào không đổi gì thì cắt hoặc gộp.
- Dài 10–30 phút: re-hook ở 40–60% (midpoint thật), kèm một cú đổi hình/đổi giọng.
- Đo thật sau khi đăng: đường giữ chân từng đoạn là dữ liệu duy nhất đáng tin; ghi vào mục 9 khi có.

## 8. Ví dụ đã chạy `[đã kiểm]`

`tests/test_script_drama.py`: kịch bản cầu cơ 7 cảnh (mini) sạch; 29 biến thể hỏng/không-báo-oan, mỗi cái bị bắt đúng mã hoặc không bị báo oan (31 dòng kết quả, 0 ca lệch). Trên `than-trung-chiec-khan-tang-thu-32`: chưa có khối `drama` (kịch bản có trước gate này): chế độ demo chỉ cảnh báo, `--strict` báo 21 lỗi DR1 (thiếu `drama` gốc và 20 cảnh). **Review độc lập đã chạy** (3 agent, 3 lens, gói mù): must=7, should=38, nice=22 (`projects/than-trung-chiec-khan-tang-thu-32/script/review/REVIEW.md`). Cả ba lens cùng thấy gán sai người nói ở S19 và phép đếm khăn 31/32 mâu thuẫn, hai lỗi mà `check_script_logic` không bắt (nó chỉ bắt được một phần dạng này ở SL10). Các lỗi này chưa sửa, chờ người dùng quyết. **Chưa gán `drama` cho project này**; việc gán nên làm sau khi review độc lập, để review không bị neo vào dữ liệu do chính người viết khai.

## 9. Chưa làm / chưa kiểm

- Chưa dùng trên một kịch bản mới viết từ đầu theo quy trình mục 4 (chế độ C).
- Các khung 6.1–6.3 chưa thử viết thành kịch bản hoàn chỉnh, chưa review bởi người.
- Con số hook (1–3 s, 14 từ, 6 câu, 20 câu trống) là ngưỡng khởi đầu, **chưa hiệu chỉnh bằng dữ liệu giữ chân thật**.
- Gate không đọc nghĩa lời thoại (mục 5).
- Chưa có nhận xét người xem; điền vào đây khi có: đoạn nào thoát, đoạn nào hỏi lại.
