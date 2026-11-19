# Timing contract — manifest ↔ HyperFrames

`audio/manifest.json` là nguồn duy nhất cho thời gian. Không đọc `wave`/`ffprobe` lại để đoán.

## Hình dạng manifest

```json
{
  "version": 1,
  "sample_rate": 48000,
  "speed": 1.25,
  "duration": 42.73,
  "full_audio": "audio/voiceover.wav",
  "captions": "audio/captions.srt",
  "characters": { "host": { "name": "Người dẫn", "voice": "Hải Đăng", "mode": "preset" } },
  "scenes": [
    {
      "id": "S01",
      "start": 0.0,
      "duration": 6.42,
      "audio": "audio/scenes/S01.wav",
      "lines": [
        {
          "id": "S01_L01",
          "speaker": "host",
          "text": "Câu thoại ...",
          "audio": "audio/lines/S01_L01.wav",
          "start": 0.0,
          "duration": 2.18,
          "gap_after": 0.25
        }
      ]
    }
  ]
}
```

- `start` là tuyệt đối tính từ 0 của cả video, đơn vị giây (float).
- `duration` của scene = từ line đầu đến hết line cuối (đã gồm gap giữa các line trong scene).
- `gap_after` là khoảng lặng sau line, đã được tính vào `start` của line kế tiếp.

## Audio trong HyperFrames

Mỗi line là một `<audio>` riêng, căn đúng `start`/`duration`:

```html
<audio id="S01_L01" class="clip" data-start="0" data-duration="2.18"
       data-track-kind="audio" src="../audio/lines/S01_L01.wav"></audio>
```

Quy tắc:
- Không dùng `audio/scenes/S01.wav` và `audio/lines/*.wav` cùng lúc cho một scene (double tiếng).
  Dùng line-level để caption khớp; scene-level chỉ khi không cần caption theo câu.
- Không tự cộng trừ offset bằng tay. Nếu cần nhạc nền hoặc SFX, đặt trên track khác, xem `sound.md` của `/hyperframes`.
- `data-duration` của root (thời lượng video) luôn `>= manifest.duration`; phần dư chỉ để thở, không cắt lời.

## Caption

- Nguồn: `audio/captions.srt` (đã bỏ tag cảm xúc, đã chia cue ≤ 2 dòng).
- Nếu dựng caption bằng HyperFrames component, map `start`/`end` của từng cue thành `data-start`/`data-duration` của clip caption; không chia lại theo cảm tính.
- Caption phải nằm trong vùng an toàn, không che mặt/UI; xem `/captions-overlay`.

## Kiểm tra

```bash
python .agents/skills/video-pipeline/scripts/check_sync.py --project projects/<slug>
```

Script so `manifest.duration` với `data-duration` root và từng `<audio>` với line tương ứng. Lệch > 0.05 s = fail, sửa code chứ không sửa số trong manifest.

## Đổi lời sau khi đã dựng

1. Sửa `script.json`.
2. Chạy lại `build_voiceover.py` (cache giữ nguyên câu không đổi).
3. Chạy `check_sync.py`, cập nhật các `data-start` bị đổi (thường chỉ các scene sau điểm sửa).
4. `npx hyperframes check --json`, snapshot lại scene bị ảnh hưởng.
