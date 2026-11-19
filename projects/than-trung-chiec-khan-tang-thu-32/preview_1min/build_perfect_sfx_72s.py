import numpy as np
from scipy.io import wavfile
import os

sr = 48000
duration = 72.5
total_samples = int(sr * duration)
t = np.linspace(0, duration, total_samples, endpoint=False)

sfx_l = np.zeros(total_samples, dtype=np.float64)
sfx_r = np.zeros(total_samples, dtype=np.float64)

def add_sound(t_start, dur, wave_l, wave_r=None):
    if wave_r is None:
        wave_r = wave_l
    i_start = int(t_start * sr)
    n = min(len(wave_l), total_samples - i_start)
    if n > 0 and i_start < total_samples:
        sfx_l[i_start:i_start+n] += wave_l[:n]
        sfx_r[i_start:i_start+n] += wave_r[:n]

# =========================================================================
# 1. SHOT 1 (0.0s - 3.8s): NIGHT WIND RUSTLING (Tiếng gió đêm rít qua rặng chuối)
# =========================================================================
dur1 = 3.8
t1 = np.linspace(0, dur1, int(sr * dur1), endpoint=False)
noise1 = np.random.normal(0, 0.15, len(t1))
# Wind filter
wind_env = np.sin(np.pi * t1 / dur1) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.8 * t1))
wind_l = noise1 * wind_env * 0.4
wind_r = np.roll(noise1, 100) * wind_env * 0.35
add_sound(0.0, dur1, wind_l, wind_r)

# =========================================================================
# 2. SHOT 3 (6.13s - 8.5s): TEMPLE BELL / SINGING BOWL (Chuông đồng bàn thờ gia tiên)
# =========================================================================
dur_bell = 2.4
t_b = np.linspace(0, dur_bell, int(sr * dur_bell), endpoint=False)
bell_tone = (
    np.sin(2 * np.pi * 432.0 * t_b) * 0.6 +
    np.sin(2 * np.pi * 864.0 * t_b) * 0.3 +
    np.sin(2 * np.pi * 1296.0 * t_b) * 0.15
) * np.exp(-t_b * 2.2)
add_sound(6.13, dur_bell, bell_tone * 0.55, bell_tone * 0.50)

# =========================================================================
# 3. SHOT 4 & 5 (8.8s, 10.4s, 11.8s, 13.2s): CLOTH RUSTLE & TRAY CLINK (Đếm khăn)
# =========================================================================
for t_cloth in [8.8, 10.4]:
    dur_c = 0.35
    tc = np.linspace(0, dur_c, int(sr * dur_c), endpoint=False)
    cloth = np.random.normal(0, 0.12, len(tc)) * np.sin(np.pi * tc / dur_c)
    add_sound(t_cloth, dur_c, cloth * 0.45, cloth * 0.40)

for t_tray in [11.8, 13.2]:
    dur_c = 0.45
    tc = np.linspace(0, dur_c, int(sr * dur_c), endpoint=False)
    # Cloth slide
    cloth = np.random.normal(0, 0.14, len(tc)) * np.sin(np.pi * tc / dur_c)
    # Bronze tray metallic ping
    ping = np.sin(2 * np.pi * 2150.0 * tc) * np.exp(-tc * 22.0) * 0.25
    clink = cloth + ping
    add_sound(t_tray, dur_c, clink * 0.5, clink * 0.45)

# =========================================================================
# 4. SHOT 6 (15.2s, 16.2s, 17.2s, 18.2s): TENSE HEARTBEAT (Tim đập thình thịch)
# =========================================================================
for t_hb in [15.2, 16.2, 17.2, 18.2]:
    dur_hb = 0.25
    thb = np.linspace(0, dur_hb, int(sr * dur_hb), endpoint=False)
    hb = np.sin(2 * np.pi * 58.0 * thb) * np.exp(-thb * 16.0) * 0.6
    add_sound(t_hb, dur_hb, hb, hb * 0.95)

# =========================================================================
# 5. SHOT 7 (19.4s - 21.0s): GHOST WHOOSH (Gió lạnh rít khi bóng ma lướt qua)
# =========================================================================
dur_gh = 1.8
t_gh = np.linspace(0, dur_gh, int(sr * dur_gh), endpoint=False)
gh_whoosh = np.random.normal(0, 0.15, len(t_gh)) * np.sin(np.pi * t_gh / dur_gh)**2
gh_drone = np.sin(2 * np.pi * (140.0 - 40.0 * (t_gh / dur_gh)) * t_gh) * 0.4 * np.exp(-t_gh * 1.2)
add_sound(19.4, dur_gh, (gh_whoosh + gh_drone) * 0.55, (gh_whoosh + gh_drone) * 0.65)

# =========================================================================
# 6. SHOT 8 (22.33s): MASSIVE HORROR JUMPSCARE STINGER ("Thần Trùng")
# =========================================================================
dur_st8 = 2.2
t_st8 = np.linspace(0, dur_st8, int(sr * dur_st8), endpoint=False)
# Ultra deep sub-bass drop (38Hz)
sub_bass = np.sin(2 * np.pi * 38.0 * t_st8) * np.exp(-t_st8 * 1.5) * 0.85
# Discordant metallic screamer
screamer = (
    np.sin(2 * np.pi * 1840.0 * t_st8) * 0.35 +
    np.sin(2 * np.pi * 1920.0 * t_st8) * 0.35 +
    np.sin(2 * np.pi * 720.0 * t_st8) * 0.25
) * np.exp(-t_st8 * 3.5)
# Impact boom
impact = np.sin(2 * np.pi * 65.0 * t_st8) * np.exp(-t_st8 * 6.0) * 0.75
stinger8 = sub_bass + screamer + impact
add_sound(22.33, dur_st8, stinger8 * 0.9, stinger8 * 0.9)

# =========================================================================
# 7. SHOT 9 (24.28s - 27.5s): FUNERAL GONG (Tiếng chiêng tang u uất 31 người)
# =========================================================================
dur_gong = 3.2
t_gong = np.linspace(0, dur_gong, int(sr * dur_gong), endpoint=False)
gong = (
    np.sin(2 * np.pi * 110.0 * t_gong) * 0.5 +
    np.sin(2 * np.pi * 220.0 * t_gong) * 0.35 +
    np.sin(2 * np.pi * 330.0 * t_gong) * 0.15
) * np.exp(-t_gong * 1.4)
add_sound(24.28, dur_gong, gong * 0.55, gong * 0.50)

# =========================================================================
# 8. SHOT 10 (28.93s): DREAD CLIMAX SLAM (Chiếc đầu thứ 32 xuất hiện)
# =========================================================================
dur_st10 = 2.8
t_st10 = np.linspace(0, dur_st10, int(sr * dur_st10), endpoint=False)
# Massive dread impact
dread_slam = (
    np.sin(2 * np.pi * 48.0 * t_st10) * 0.8 +
    np.sin(2 * np.pi * 115.0 * t_st10) * 0.45
) * np.exp(-t_st10 * 2.2)
metallic_resonance = np.sin(2 * np.pi * 840.0 * t_st10) * np.exp(-t_st10 * 5.0) * 0.35
gasp = np.random.normal(0, 0.08, len(t_st10)) * np.exp(-t_st10 * 8.0) * 0.4
stinger10 = dread_slam + metallic_resonance + gasp
add_sound(28.93, dur_st10, stinger10 * 0.95, stinger10 * 0.95)

# =========================================================================
# 9. SHOT 12 & 13 (42.5s - 56.0s): RURAL WATER LAP & COUNTRYSIDE WIND
# =========================================================================
for t_lap in [43.2, 45.0, 47.5, 50.2, 53.0]:
    dur_lap = 0.6
    tlap = np.linspace(0, dur_lap, int(sr * dur_lap), endpoint=False)
    water_lap = np.random.normal(0, 0.06, len(tlap)) * (np.sin(np.pi * tlap / dur_lap)**3)
    water_bubble = np.sin(2 * np.pi * 320.0 * tlap) * np.exp(-tlap * 12.0) * 0.18
    add_sound(t_lap, dur_lap, (water_lap + water_bubble) * 0.4, (water_lap + water_bubble) * 0.4)

# =========================================================================
# 10. SHOT 14 (57.50s - 72.0s): BRONZE BETEL MORTAR (Tiếng cối đồng giã trầu)
# CHÍNH XÁC TỪNG NHỊP 0.80 GIÂY KHỚP 100% CỬ ĐỘNG CỦA BÀ CỤ!
# =========================================================================
mortar_hits = [
    57.50, 58.30, 59.10, 59.90, 60.70, 61.50, 62.30, 63.10,
    63.90, 64.70, 65.50, 66.30, 67.10, 67.90, 68.70, 69.50,
    70.30, 71.10, 71.90
]

for t_hit in mortar_hits:
    dur_m = 0.38
    tm = np.linspace(0, dur_m, int(sr * dur_m), endpoint=False)
    # 1. Wooden pestle impact thump (tiếng chày gỗ nén trầu)
    thump = np.sin(2 * np.pi * 175.0 * tm) * np.exp(-tm * 28.0) * 0.65
    # 2. Resonant bronze bell ping (tiếng chuông cối đồng thau)
    bronze_ping1 = np.sin(2 * np.pi * 1480.0 * tm) * np.exp(-tm * 16.0) * 0.40
    bronze_ping2 = np.sin(2 * np.pi * 2650.0 * tm) * np.exp(-tm * 22.0) * 0.22
    # Combined clack
    mortar_clack = thump + bronze_ping1 + bronze_ping2
    # Pan slightly to right (grandma is seated on the right door sill)
    add_sound(t_hit, dur_m, mortar_clack * 0.70, mortar_clack * 0.95)

# Normalization & Master Limiting
peak = max(np.max(np.abs(sfx_l)), np.max(np.abs(sfx_r)))
if peak > 0:
    sfx_l = (sfx_l / peak) * 0.65
    sfx_r = (sfx_r / peak) * 0.65

sfx_stereo = np.column_stack((sfx_l, sfx_r))

out_path = "projects/than-trung-chiec-khan-tang-thu-32/preview_1min/assets/audio/sfx_72s.wav"
wavfile.write(out_path, sr, (sfx_stereo * 32767).astype(np.int16))
print(f"Generated precision-synced SFX to {out_path} successfully!")
