# VieNeu-TTS Skill (Vietnamese On-Device Neural TTS)

Kỹ năng tạo giọng đọc tiếng Việt **cục bộ (On-Device)**, chất lượng cao 48kHz, hỗ trợ nhân bản giọng nói (Instant Voice Cloning) và gắn tag cảm xúc trực tiếp.

Thư mục skill này hoàn toàn độc lập, có thể sao chép trực tiếp sang bất kỳ dự án AI Agent nào khác.

---

## 1. Cấu trúc Thư mục Skill

```
vieneu-tts/
├── README.md                 # Hướng dẫn chi tiết cho Developer và AI Agent
├── SKILL.md                  # Khai báo kỹ năng chuẩn cho hệ thống Agent (Antigravity/Cursor/Claude)
└── scripts/
    └── generate_voice.py     # Script CLI tự động sinh file âm thanh và đo độ dài (WAV)
```

---

## 2. Hướng dẫn Dành Riêng Cho AI Agent (Agent Protocol)

Khi nhận lệnh tạo giọng đọc qua **`vieneu-tts`**, Agent **BẮT BUỘC** thực hiện theo quy trình kiểm tra sau:

### Bước 1: Kiểm tra xem môi trường đã có thư viện `vieneu` chưa
Chạy lệnh shell:
```bash
python -c "import vieneu"
```

### Bước 2: Xử lý khi người dùng CHƯA cài đặt package (`ModuleNotFoundError`)
Nếu lệnh trên trả về lỗi chưa có module `vieneu`, Agent xử lý như sau:
1. **Nếu Agent có quyền chạy lệnh (`run_command`)**: Chủ động chạy lệnh cài đặt:
   ```bash
   # Chạy trên CPU (Rất nhẹ, tối ưu ONNX Runtime, không cần GPU):
   pip install vieneu

   # Hoặc nếu máy có GPU NVIDIA CUDA (nếu muốn tăng tốc tối đa):
   pip install "vieneu[cuda]"
   ```
2. **Nếu Agent KHÔNG có quyền tự chạy pip hoặc môi trường bị khóa**: Phải thông báo ngay cho người dùng:
   > *"Dự án chưa cài đặt thư viện `vieneu`. Bạn vui lòng mở terminal và chạy lệnh: `pip install vieneu` (hoặc `pip install vieneu[cuda]` nếu có GPU NVIDIA) rồi nhắn lại để mình tiếp tục nhé!"*

### Bước 3: Lưu ý tải Model lần đầu (First-run Cache)
- Khi chạy lần đầu tiên, thư viện `vieneu` sẽ tự động tải trọng số mô hình `pnnbao-ump/VieNeu-TTS-v3-Turbo` (~300MB) về thư mục cache Hugging Face (`~/.cache/huggingface/hub/`). Quá trình này diễn ra một lần duy nhất, sau đó hoạt động offline 100% không cần mạng.

---

## 3. Cách Sử Dụng CLI (`scripts/generate_voice.py`)

Agent hoặc Developer có thể gọi trực tiếp script từ terminal:

### A. Đọc văn bản bằng giọng dựng sẵn (Preset Voice)
```bash
python scripts/generate_voice.py \
  --text "Chào bạn! Chiếc áo này mặc lên form cực kỳ tôn dáng luôn nhé [cười]." \
  --voice "Đoan Trang" \
  --output "output_audio.wav"
```

### B. Đọc từ file kịch bản (.txt)
```bash
python scripts/generate_voice.py \
  --text-file "script.txt" \
  --voice "Hải Đăng" \
  --output "output_audio.wav"
```

### C. Nhân bản giọng nói (Instant Voice Cloning) từ audio mẫu 3–8 giây
```bash
python scripts/generate_voice.py \
  --text "Chất vải thun cotton này sờ vào mát rượi luôn mọi người ơi!" \
  --ref-audio "path/to/koc_sample_5s.wav" \
  --output "output_audio.wav"
```

### D. Liệt kê toàn bộ danh sách giọng có sẵn
```bash
python scripts/generate_voice.py --list-voices
```

---

## 4. Định dạng Đầu Ra Chuẩn (JSON Output)

Script in ra stdout kết quả JSON chuẩn giúp Agent bắt được thông số kỹ thuật:
```json
{
  "status": "success",
  "mode": "preset_voice",
  "voice": "Đoan Trang",
  "output_file": "D:\\path\\to\\output_audio.wav",
  "duration_seconds": 4.4,
  "sample_rate": 48000,
  "file_size_bytes": 422444
}
```

> [!IMPORTANT]
> **Dynamic Duration Rule**: Sử dụng giá trị `duration_seconds` thực tế từ JSON để căn chỉnh độ dài video hoặc phân cảnh. Tuyệt đối không cố định thời lượng video là 28s.

---

## 5. Danh mục Giọng Đọc Dựng Sẵn (Preset Voices)

Danh mục đầy đủ 25 giọng (Bắc / Trung / Nam, kèm alias và gợi ý chọn giọng theo nhân vật):
**[references/voices.md](references/voices.md)**. Danh sách chuẩn luôn lấy từ model đang cài:

```bash
python .agents/skills/vieneu-tts/scripts/list_voices.py
```

| Khu vực | Giọng tiêu biểu | Đặc điểm |
| :--- | :--- | :--- |
| **Miền Bắc** | `Hải Đăng` *(mặc định)*, `Đoan Trang`, `Ngọc Huyền`, `Mai Anh` | Nam/nữ Hà Nội, tự nhiên, chuẩn tin tức / podcast / KOC |
| **Miền Trung** | `Quang Sơn`, `Ngọc Trân` | Giọng miền Trung, nhẹ và chậm |
| **Miền Nam** | `Kim Thanh`, `Mỹ Duyên`, `Thái Sơn`, `Thùy Dung` | Nữ/nam Sài Gòn, truyền cảm, kể chuyện |

### Tag biểu cảm hỗ trợ:
Chỉ có **3 tag** — mọi tag khác sẽ bị đọc thành chữ:
- `[cười]` : Thêm tiếng cười nhẹ nhàng tự nhiên.
- `[thở dài]` : Thở dài nhẹ, tạo cảm giác lắng đọng.
- `[hắng giọng]` : Hắng giọng tự nhiên trước khi nói.

Chi tiết (alias tiếng Anh, cách đặt tag, vì sao không có tag buồn/vui/ngạc nhiên):
**[references/emotions.md](references/emotions.md)**.

---

## 6. Tốc độ đọc (speed)

SDK `vieneu` **không có** tham số `speed` cho v3 Turbo (chỉ `v3nano` có). Muốn đọc nhanh/chậm
thì hậu kỳ bằng ffmpeg, giữ nguyên cao độ:

```bash
ffmpeg -y -i in.wav -filter:a "atempo=1.25" -ar 48000 -ac 1 out.wav
```

Pipeline `voice-sync` làm sẵn việc này: `build_voiceover.py` mặc định `--speed 1.25` (dải
khuyến nghị **1.2–1.3**), áp `atempo` lên từng câu **trước khi đo duration**, nên
`manifest.json` / `caption` / `voiceover.wav` luôn khớp. `--speed 1.0` = giữ nguyên giọng gốc.

Đừng tăng `temperature` để "đọc nhanh hơn" — nó chỉ làm giọng lè nhè, không đổi nhịp.

