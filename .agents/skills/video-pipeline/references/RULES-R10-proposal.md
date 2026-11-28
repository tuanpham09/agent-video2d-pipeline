# Đề xuất thêm R10 vào RULES.md (chờ người dùng duyệt — R0.3)

Căn cứ: chỉ thị của người dùng phiên 2026-11-22 — agent khác (Codex…) làm video/nhân vật/đạo cụ chưa đẹp bằng mẫu; "các agent phải bắt buộc tuân theo khi dựng video, tạo nhân vật và các đạo cụ".

Nếu duyệt: dán khối dưới vào `RULES.md` (trước mục "Luật → công cụ kiểm"), nâng `Phiên bản luật` lên 2, cập nhật tem `Luật áp dụng: RULES.md v2` trong `PROJECT.md` của từng project (`check_rules.py` sẽ cảnh báo lệch), và thêm vào bảng công cụ: `R10.4, R10.7 → check_rules.py`.

```markdown
## R10. Chất lượng & tay nghề (craft) — bắt buộc khi dựng video, tạo nhân vật, đạo cụ, bối cảnh

Chi tiết: `.agents/skills/video-pipeline/references/craft-playbook.md`. Phải đọc trước khi tạo/sửa nhân vật, đạo cụ, bối cảnh hoặc dựng video.

- **R10.1** Làm theo `craft-playbook.md`; không tự nghĩ quy trình dựng/vẽ riêng, không bỏ bước.
- **R10.2** Nhìn ảnh thật rồi mới báo xong: render PNG, agent mở ảnh xem ở cỡ dùng thật, lặp ≥ 1 vòng sửa nếu lệch. Check xanh không thay cho việc xem. Không xem được ảnh → dừng và báo người dùng (R0.4).
- **R10.3** Clone mẫu vàng, không vẽ từ trắng (archetype+outfit/`extends`; copy asset library gần nhất). Tạo mới đạt chuẩn library ngay (R2.4–R2.7).
- **R10.4** Mỗi nhân vật có `assets/rig/sheets/<id>.png` và được xem/duyệt trước khi dựng shot (R3.7). Đạo cụ mới có trong `library/sheets/` và đã thử ghép vào bối cảnh thật cạnh một nhân vật.
- **R10.5** Tương thích HyperFrames: CSS asset/rig không dùng `>`; glow bằng `radialGradient`; rig chỉ nhúng `<svg>` lồng (R3.4).
- **R10.6** Dựng shot chỉ bằng `build_video.py` từ `shotlist.json` (R1.6); beat nhìn thấy được có `set`; beat vật lý có SFX (R6.1).
- **R10.7** Báo cáo theo khung playbook §8, bắt buộc có "Ảnh đã XEM: <đường dẫn> — thấy gì, lỗi đã sửa" và "Chưa kiểm". Nhật ký gate trong `PROJECT.md` nêu snapshot/ảnh đã xem.
```
