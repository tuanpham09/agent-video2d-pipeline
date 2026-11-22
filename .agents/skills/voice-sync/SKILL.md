---
name: voice-sync
description: Generate character voiceovers from script.json with VieNeu-TTS v3 Turbo (Vietnamese, on-device, 48 kHz), per-character preset or cloned voices, emotion tags, then emit an exact timing manifest, scene mixes and SRT captions that HyperFrames can sync to. Use when the script is approved and you need audio, khi cần "tạo giọng đọc", "lồng tiếng", "đọc kịch bản", or after editing lines in script.json.
---

# Voice Sync — đọc kịch bản thành audio + timing

Biến `script/script.json` thành bộ audio đồng bộ trong một lần chạy. Không đọc từng câu bằng tay, không tự đoán `data-start`.

## Kiểm sau khi đọc (R12.3)

```bash
python .agents/skills/voice-sync/scripts/check_audio.py --project projects/<slug>
```

Phải OK trước khi dựng video. Kiểm: engine = vieneu-v3-turbo, speed 1.2–1.3, thời lượng wav khớp manifest, không clip/câm/chồng lời, tổng khớp voiceover.

## Điều kiện

- `vieneu` đã cài: `python -c "import vieneu"` (nếu thiếu: `pip install vieneu` hoặc `pip install "vieneu[cuda]"`).
- `numpy`, `soundfile` (đã có cùng vieneu).
- `script.json` hợp lệ theo `/script-rewrite` → `references/script-schema.md`.
- Lần chạy đầu sẽ tải model `pnnbao-ump/VieNeu-TTS-v3-Turbo` (~vài trăm MB) vào cache Hugging Face; sau đó offline.

## Chạy

```bash
python .agents/skills/voice-sync/scripts/build_voiceover.py \
  --script "projects/<slug>/script/script.json" \
  --out "projects/<slug>/audio"
```

Luôn chạy `--dry-run` trước nếu vừa sửa cấu trúc:

```bash
python .agents/skills/voice-sync/scripts/build_voiceover.py \
  --script "projects/<slug>/script/script.json" --out "projects/<slug>/audio" --dry-run
```

Tuỳ chọn hữu ích:

| Flag | Việc |
| --- | --- |
| `--speed 1.25` | tốc độ đọc, **mặc định 1.25×**, dải khuyến nghị 1.2–1.3 (atempo, giữ cao độ) |
| `--gap 0.18` | lặng mặc định giữa các câu (giây) |
| `--scene-gap 0.4` | lặng giữa các scene, chỗ để thở/chuyển hình |
| `--tail 0.4` | lặng cuối video |
| `--force` | đọc lại tất cả, bỏ cache |
| `--no-scenes` | không xuất audio theo scene |
| `--voice-map <file>` | đổi giọng không sửa `script.json` |

### Tốc độ đọc

- Mặc định **1.25×** — video ngắn gọn, nhịp nhanh hơn bản đọc gốc mà vẫn rõ chữ.
- Chỉnh trong dải 1.2–1.3: `1.2` cho nội dung cần nghỉ (giải thích, kể chuyện), `1.3` cho
  short nhiều năng lượng. Ngoài dải này ffmpeg vẫn chạy (1.0–2.0) nhưng dễ mất tự nhiên.
- Áp bằng `ffmpeg atempo` trên từng line **trước khi đo duration**, nên `manifest.json`,
  SRT và `voiceover.wav` luôn khớp nhau. `--speed 1.0` = giữ nguyên giọng gốc.
- Speed nằm trong cache key: đổi speed → đọc lại toàn bộ (đúng, vì file cũ sai tốc độ).
- Muốn nhanh/chậm **theo cảm xúc từng câu** thì đừng đổi speed giữa các line — cắt câu
  ngắn hơn, hoặc để `pause_after` lo nhịp.

## Đổi giọng nhanh: `voice_map.json`

Đặt ở `audio/voice_map.json` (hoặc trỏ bằng `--voice-map`):

```json
{
  "host": { "voice": "Mai Anh", "temperature": 0.9 },
  "dev": { "ref_audio": "assets/voices/linh_ref_6s.wav", "denoise": true }
}
```

Override này thắng `script.json`. Dùng để thử giọng mà không đụng kịch bản; khi đã chốt thì ghi lại vào `script.json` để người sau đọc hiểu.

## Đầu ra

```
audio/
├── lines/S01_L01.wav ...   # từng câu, đúng giọng, 48 kHz
├── scenes/S01.wav ...      # mỗi scene một bản ghép (có gap trong scene)
├── voiceover.wav           # toàn bộ, đã ghép gap + tail
├── manifest.json           # start/duration tuyệt đối từng line + scene
├── captions.srt            # phụ đề đã bỏ tag cảm xúc
└── timing.md               # bảng timing để người đọc
```

`manifest.json` là nguồn duy nhất để đặt `data-start` / `data-duration` trong HyperFrames. Chi tiết hợp đồng: `/video-pipeline` → `references/timing.md`.

## Cache

- Key = text + giọng/ref audio + temperature + engine.
- Sửa 1 câu → chỉ câu đó được đọc lại; các câu khác lấy từ cache (nhanh, và không đổi âm sắc ngẫu nhiên).
- Đổi `--force` chỉ khi nghi file hỏng hoặc đổi model.

## Chất lượng giọng

1. **Preset**: nghe thử 1 câu trước khi đọc cả kịch bản. Danh mục 25 giọng:
   `python .agents/skills/vieneu-tts/scripts/list_voices.py` (chi tiết: `/vieneu-tts` → `references/voices.md`).
   Script build kiểm tra tên giọng trước khi đọc, tự đổi alias cũ (`Minh Quân` → `Hải Đăng`)
   và báo `VoiceNotFound` kèm gợi ý nếu tên không tồn tại.
2. **Clone**: file mẫu 3–8 s, một người nói, không nhạc, không vang, cắt đúng câu. `denoise: true` mặc định.
3. **Temperature**: 0.7–0.8 ổn định cho nội dung giải thích; 0.85–0.95 cho kể chuyện/review. > 1.0 dễ lè nhè.
4. **Tag cảm xúc** chỉ đặt trong `text`, không đặt trong `on_screen`. Chỉ có 3 tag:
   `[cười]`, `[thở dài]`, `[hắng giọng]`. Tag khác (`[buồn]`, `[ngạc nhiên]`…) bị **đọc
   thành chữ** — build script cảnh báo trước khi đọc. Chi tiết: `/vieneu-tts` →
   `references/emotions.md`.
5. **Tên riêng đọc sai** → sửa phiên âm trong `text` (xem `/script-rewrite` `references/vietnamese-style.md`). Không hậu kỳ file wav.
6. **Câu quá dài** → cắt thành 2 line cùng speaker; timing và caption sẽ tự theo.

## Kiểm trước khi dựng hình

- [ ] Nghe `audio/voiceover.wav` hết một lượt: không mất chữ, không cắt đuôi câu, không đổi giọng giữa scene.
- [ ] `manifest.duration` hợp lý với format (short 35–60 s; long-form 8–15 phút).
- [ ] `captions.srt` mở được, không có `[cười]`, không quá 2 dòng/cue.
- [ ] Mọi line trong `script.json` đều có file trong `audio/lines/`.
- [ ] Sau khi dựng: `python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/<slug>` trả `OK`.

## Lỗi thường gặp

| Lỗi | Nguyên nhân / xử lý |
| --- | --- |
| `PackageNotInstalled` | Chưa `pip install vieneu` trong đúng môi trường Python đang gọi |
| `MissingRefAudio` | Đường dẫn `ref_audio` tính từ thư mục project, không phải từ `script/` |
| `VoiceNotFound` | Tên giọng không có trong model. Chạy `list_voices.py` để lấy tên chuẩn; `Anh Khôi`/`Mạnh Dũng` không có trong build này |
| `SynthesisFailed` | Xem danh sách line lỗi; thường do text chứa ký tự lạ hoặc hết RAM. Sửa rồi chạy lại (cache giữ câu đã xong) |
| Model load rất lâu lần đầu | Đang tải weights; chỉ xảy ra một lần |
| Giọng đọc đều, thiếu cảm xúc | Tăng temperature nhẹ, thêm tag cảm xúc, tách câu ngắn hơn |
| Âm lượng nhỏ/lớn bất thường | Script tự chuẩn hoá khi đỉnh > 1.0; nếu vẫn lệch, xử lý ở HyperFrames bằng `normalize-audio` |
| Windows console lỗi font | Script đã ép UTF-8; nếu vẫn lỗi, chạy trong Windows Terminal |

## Liên quan

- `/vieneu-tts` — chi tiết model, preset voices, cloning, SDK.
- `/script-rewrite` — nguồn `script.json` và luật viết cho TTS.
- `/video-pipeline` — thứ tự phase và QC toàn bộ.
- `/hyperframes` — đặt audio/caption vào composition.
