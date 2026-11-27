---
name: script-rewrite
description: Rewrite a YouTube transcript or rough source into a retention-optimized Vietnamese video script, with a machine-readable script.json, character casting for VieNeu-TTS, and title/thumbnail/description packaging. Use when the user says "sửa kịch bản", "viết lại lời cho hay", "làm video từ transcript này", "kịch bản TikTok/YouTube", or after a transcript has been downloaded.
---

# Script Rewrite — từ transcript lộn xộn thành kịch bản video

Nguyên tắc: **không tóm tắt transcript**. Tóm tắt = mất lý do người ta xem. Ta giữ chất liệu thật, đổi cách kể, thêm vòng lặp tò mò, bỏ phần lê thê.

## 0. Đọc và bóc chất liệu (bắt buộc)

Đọc hết transcript trong `source/`, ghi ra `script/brief.md`:

- **Claim map**: 5–9 ý chính, kèm `[HH:MM:SS]` nguồn.
- **Chi tiết vàng**: con số, câu chuyện, câu nói hay, mâu thuẫn, thất bại — thứ không thể bịa.
- **Điểm yếu nguồn**: chỗ lan man, sai hướng, thiếu bằng chứng. Cắt hoặc nói rõ là ý kiến.
- **Người xem mục tiêu**: một câu, cụ thể (không phải "mọi người quan tâm AI").

Không có chất liệu thật cho một ý → bỏ ý đó. Không bịa số liệu, quote, tên.

## 1. Chọn góc (angle)

Video hay = một góc nhìn, không phải bản tin tổng hợp. Chọn 1 trong:

- **Đảo ngược**: điều ai cũng tin là sai / thiếu một nửa.
- **Hành trình**: tôi đã thử X và trả giá bằng Y.
- **So sánh**: A vs B, chọn cái nào trong trường hợp nào.
- **Điều tra**: tại sao X xảy ra; lần theo dấu vết.
- **Hướng dẫn**: làm được kết quả Z trong N bước, kèm sai lầm phổ biến.

Viết một câu promise: "Sau video này, người xem sẽ ______." Câu này quyết định hook, payoff, và title.

## 2. Khung theo format

### Short (35–60 s, 9:16)

| Giây | Việc |
| --- | --- |
| 0–2 | Hook: hình + lời khác nhau, nêu kết quả hoặc mâu thuẫn. Không chào hỏi. |
| 2–8 | Stakes: vì sao đáng nghe, mở vòng lặp chính. |
| 8–45 | 2–4 beat, mỗi beat 1 ý + 1 hình thay đổi; nối bằng "nhưng", "và rồi", "điều không ai nói". |
| 45–55 | Payoff: đóng vòng lặp mở ở đầu. |
| 55–60 | 1 CTA duy nhất, không lan man. |

- 90–150 từ tiếng Việt cho 45–60 s (tính cho bản đọc gốc). Với `--speed 1.25` mặc định,
  cùng thời lượng chứa được thêm ~20% từ; chốt bằng `duration` trong `manifest.json`,
  đừng đoán. Đọc thử: 1 line ≤ 12 từ.
- Mỗi 1–2 câu phải có thứ để nhìn: số, đối tượng, UI, so sánh.

### Long-form (8–15 phút, 16:9)

Dùng `/long-form-youtube` cho khung chuẩn. Rút gọn áp dụng ở đây:

- Hook ≤ 30 s, khớp đúng title/thumbnail, mở một vòng lặp chỉ đóng ở cuối.
- 3–6 chương, mỗi chương mở vòng lặp kế trước khi đóng vòng của mình.
- Re-hook ở 40–60% thời lượng.
- Pattern interrupt 20–40 s: đổi hình, đổi giọng, câu hỏi, im lặng có chủ đích.
- Payoff đóng đúng promise; outro 1 CTA + tease video sau, ≤ 15 s.

## 3. Viết lời thoại (không viết văn)

- **Câu ngắn, một ý.** Trung bình 10–18 từ; line dài nhất 25 từ.
- **Viết như nói**, rồi đọc to. Chỗ nào phải lấy hơi giữa từ = sai nhịp, cắt câu.
- **Bỏ từ đệm vô nghĩa**: "và", "thì", "như các bạn đã biết", "hãy cùng mình tìm hiểu".
- **Cụ thể thay vì trừu tượng**: "tăng 40% sau 3 tuần" > "tăng đáng kể".
- **Một line = một nhân vật = một file audio.** Không để hai người nói trong một line.
- **Đánh dấu cảm xúc** bằng `[cười]`, `[thở dài]`, `[hắng giọng]` — đúng 3 tag này, tối đa 1 tag mỗi 4–5 câu, chỉ khi thật sự cần.
- **Số và tên riêng**: xem `references/vietnamese-style.md` để viết sao cho TTS đọc đúng.
- **Câu hỏi tu từ** dùng có liều lượng; mỗi scene 1 câu là đủ.

## 3.0. Bối cảnh, hành trình, logic liền mạch (BẮT BUỘC, làm trước 3.1)

Mỗi cảnh phải có `setting` (địa điểm của bible, trong/ngoài, thời gian, `frame`, `link` với cảnh trước), `cast` (ai có mặt, đến từ đâu) và `staging` (ai vào/ra/đưa/cầm/đổi trạng thái đạo cụ, theo thứ tự câu). Nhân vật đổi chỗ giữa hai cảnh phải khai `from` (đi từ đâu tới đâu); địa điểm nối nhau theo `bible.locations[].connects`. Hồi tưởng, điện thoại, giấc mơ khai `frame` đúng. Làm đúng quy trình trong [`video-pipeline/references/script-continuity-guide.md`](../video-pipeline/references/script-continuity-guide.md) (mô hình dữ liệu, các bước, ví dụ than-trung, mã lỗi SL1–SL11), rồi chạy:

```bash
python .agents/skills/video-pipeline/scripts/check_script_logic.py --project projects/<slug> [--strict]
```

`--strict` (cảnh thiếu `setting` là lỗi) phải 0 lỗi trước khi chốt kịch bản và chạy TTS. Trường `visual` (3.1) mô tả hình; `setting/cast/staging` là dữ liệu máy đọc được, hai bên không được mâu thuẫn.

## 3.1. Mô tả quang cảnh & thị giác (Bắt buộc cho HyperFrames dựng mượt)

**Tuyệt đối không ghi chung chung** kiểu "cảnh đêm rạp tang hiu hắt" hay "người mẹ lo âu". Để bộ phận dựng video (HyperFrames + SVG vector) tạo được chuyển động chân thực, mượt mà và nhịp điệu dồn dập, gay cấn, kịch bản phải tuân thủ 2 nguyên tắc thiết kế:

### A. Phân tách nhiều Shot dồn dập (Multi-shot Cinematic Pacing):
* **Mật độ đổi góc máy cao:** Cứ mỗi **3–5 giây** phải đổi shot hoặc thay đổi góc nhìn/lia máy (zoom in/pull back). Tuyệt đối không giữ khung hình tĩnh quá 6 giây.
* **Tỷ lệ shot:** 1 phút video phải có **từ 12–15 shots trở lên**.
* **Đa dạng cỡ cảnh:** Phải chỉ định rõ trong từng câu thoại: Establishing Wide (toàn cảnh), Medium Action (trung cảnh), Close-up (cận cảnh mắt/khẩu hình), Macro (đạo cụ), OTS (qua vai nhìn ra hiểm họa) để tạo cảm giác nghẹt thở, lôi cuốn.

### B. Mô tả đầy đủ 5 trường thông tin thị giác & SFX cho mỗi Shot:

1. **Quang cảnh & Bối cảnh (Environment & Scene):**
   * Chất liệu không gian: vách gỗ mộc, vách nứa đan, tường gạch rêu hay cột tre? Sàn gạch tàu, sàn ván hay nền đất?
   * Cửa sổ / cửa chính mở ra đâu: khoảng sân sương đêm mờ mịt, bóng rặng chuối lay trong gió, giếng nước hay ngõ tối?
   * Đạo cụ trang trí chi tiết: bàn thờ tang, lư đồng, bát hương đang tỏa khói, đôi nến trắng thắp sáng, chõng tre, cối đồng giã trầu, mâm tre đựng khăn tang xô...
2. **Bố cục & Vị trí nhân vật (Framing & Character Blocking):**
   * Cỡ cảnh: Toàn cảnh (Wide), Trung cảnh (Medium) hay Cận cảnh (Close-up)?
   * Vị trí đứng/ngồi của từng nhân vật: Ngồi bên bậc cửa bên phải, nằm trên chõng tre bên trái, quây quần quanh đống lửa ở giữa...
   * Trang phục và đặc điểm nhận dạng: Áo bà ba nâu sòng, áo trắng ngà, khăn xô thắt ngang trán, búi tóc bạc, mắt kính gọng tròn...
3. **Cử động & Biểu cảm (Action & Motion Rig):**
   * Động tác tay chân cụ thể: Tay cầm chày giã cối nhịp nhàng, tay lật đếm từng nếp khăn, tay vung ra chỉ hướng cửa, ngực phập phồng theo nhịp thở.
   * Hướng mắt & cử động mắt: Mắt nhìn chăm chú vào mâm khăn, mắt liếc sợ hãi sang góc tối, mắt chớp tự nhiên.
   * Cảm xúc biến đổi (chọn trong `emotion_vocab` của `bible.json`: calm, focused, worried, afraid, shocked, dread, sad, grief, angry, suspicious, relieved): Từ bình thản, tập trung, nghiêm nghị sang bàng hoàng, lạnh gáy.
   * Khẩu hình miệng: Miệng mở đóng đồng bộ với âm tiết của câu thoại.
4. **Nguồn sáng & Ánh sáng động (Dynamic Lighting & Mood):**
   * Nguồn sáng từ đâu: Ánh nến vàng cam lập lòe, ngọn đèn dầu hoa kỳ hay ngọn lửa bập bùng?
   * Hiệu ứng bóng đổ và chuyển biến: Vùng sáng rọi lên mặt ai, vùng tối khuất ở góc nào, khi nào ánh sáng đột ngột hạ tối để đẩy cao trào kinh dị.
5. **Hệ thống SFX chi tiết đi kèm (Suspense Foley & Cues - Bắt buộc):**
   * Tiếng cối đồng gõ đanh cộc, tiếng vải sột soạt, tiếng lách cách kim loại mâm khay, tiếng nến nổ tanh tách, tiếng gió rít qua khe cửa, chuỗi nhịp tim đập thình thịch (thump 58Hz), tiếng thở gấp lo âu, tiếng chiêng tang ma u uất, Horror Stinger (sub-bass drop 38Hz + rít chói tai) khi giật mình lộ diện quỷ dữ. Mọi cú va chạm hay cử động vật lý đều phải có SFX đi kèm.

## 4. Cast giọng

Trong `characters` của `script.json`:

| Vai | Giọng gợi ý |
| --- | --- |
| Narrator nam, tin cậy | `Hải Đăng` (mặc định), `Minh Đức` (tin tức) |
| Narrator nữ, ấm | `Đoan Trang`, `Ngọc Huyền` |
| **Truyện ma / kinh dị — người kể** | `Đức Trí` (**luôn dùng**), `Thiền Tâm Đức` (phương án phụ), `Thiện Minh` (hook/cao trào) |
| **Truyện ma / kinh dị — nhân vật** | `Xuân Vĩnh` (nam trầm ấm), `Adam` (vai ma/lớn tuổi) |
| **Đời sống gay cấn / gây tò mò** | `Hải Đăng` (đề xuất), `Thiện Minh` (tông lạnh) — xem `references/casting-genres.md` |
| Nữ trẻ, nhanh, short | `Mai Anh`, `Trúc Ly` |
| Kể chuyện nam | `Thanh Bình`, `Thiện Minh`, `Thái Sơn` |
| Kể chuyện nữ | `Ngọc Linh`, `Thục Đoan` |
| Audiobook / đọc truyện | `Quỳnh Anh`, `Kim Thanh`, `Mỹ Duyên`, `Đức Trí` |
| Nam hiện đại, công nghệ | `Adam`, `Quốc Tuấn` |
| Nam miền Nam | `Thái Sơn`, `Minh Triết`, `Adam` |
| Nữ miền Nam | `Mỹ Duyên`, `Thùy Dung`, `Kim Thanh` |
| Miền Trung | `Quang Sơn`, `Ngọc Trân` |
| Hài / meme | `Adam bựa` |
| Nhân vật thật / KOC | clone từ `ref_audio` 3–8 s |

Danh mục đầy đủ 25 giọng (vùng, giới, phong cách, alias): `/vieneu-tts` →\
`references/voices.md`, hoặc `python .agents/skills/vieneu-tts/scripts/list_voices.py`.

Preset theo thể loại (kèm tốc độ, cặp ghép, cảnh báo trùng giọng):
**[references/casting-genres.md](references/casting-genres.md)**.

Tên cũ vẫn chạy nhưng đừng viết mới: `Minh Quân` → `Hải Đăng`, `Anh Khôi` → `Thiện Minh`,
`Mạnh Dũng` → `Quốc Tuấn`. `Phương Linh` đã bị bỏ khỏi build 3.8.

Quy tắc:
- Tối đa 3 giọng cho một short, 4 cho long-form. Nhiều hơn = rối.
- Đối thoại: mỗi lượt ≥ 1 câu trọn nghĩa; không cắt qua lại từng 3 chữ.
- Giọng clone cần file sạch, 3–8 s, một người nói, không nhạc.

## 5. Ghi ra file

1. `script/script.md` — bản đọc: hook, các chương/beat có timestamp dự kiến, lời thoại, ghi chú hình.
2. `script/script.json` — đúng schema `references/script-schema.md`, là đầu vào của `voice-sync`.
3. `script/packaging.md` — title, thumbnail concept, description, hashtag (dùng `/titles-and-thumbnails`).

Ví dụ JSON đầy đủ: `examples/script.example.json`.

## 6. Tự soát trước khi đưa duyệt

- [ ] Hook có mở vòng lặp và khớp promise/title không?
- [ ] Mỗi 20–40 s (long) hoặc 1–2 s (short) có thay đổi hình/ý không?
- [ ] Có chỗ nào chỉ toàn lời, không có gì để nhìn trong > 5 s không?
- [ ] Câu nào đọc to bị hụt hơi? Cắt.
- [ ] Có số liệu/tên riêng nào chưa có nguồn trong brief không?
- [ ] Đã bỏ hết lời chào, "subscribe" giữa video, quảng cáo lộ liễu chưa?
- [ ] Từng line có đúng 1 speaker và ≤ 25 từ chưa?
- [ ] Người không biết gì về chủ đề có hiểu 30 s đầu không?

## Liên quan

- `/long-form-youtube`, `/storytelling-hooks`, `/retention-audit`, `/titles-and-thumbnails` — lý thuyết và pattern.
- `/voice-sync` — biến `script.json` thành audio + manifest.
- `/video-pipeline` — toàn bộ quy trình và thư mục.
