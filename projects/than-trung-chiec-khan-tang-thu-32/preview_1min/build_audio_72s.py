import numpy as np
from scipy.io import wavfile
import os

sr = 48000
duration = 72.5
total_samples = int(sr * duration)
t = np.linspace(0, duration, total_samples, endpoint=False)

# ----------------- BGM TRACK -----------------
# Ambient Horror (0 -> 46.5s)
base_drone1 = np.sin(2 * np.pi * 55.0 * t + 0.1 * np.sin(2 * np.pi * 0.2 * t))
base_drone2 = 0.6 * np.sin(2 * np.pi * 82.4 * t)
base_drone3 = 0.3 * np.sin(2 * np.pi * 110.0 * t)
noise = np.random.normal(0, 0.05, total_samples)

# Low pass filter approximation via cumulative sum or simple moving average
# A subtle wind bed:
wind = np.zeros(total_samples)
chunk = 480
for i in range(0, total_samples - chunk, chunk):
    val = np.random.uniform(0.02, 0.08)
    wind[i:i+chunk] = val
wind = np.convolve(wind, np.ones(2400)/2400, mode='same') * np.sin(2 * np.pi * 70 * t)

horror_mix = (base_drone1 + base_drone2 + base_drone3) * 0.35 + wind * 0.4

# Nostalgic Rural Ambiance (46.5 -> 72.5s)
warm_drone1 = np.sin(2 * np.pi * 130.81 * t) # C3
warm_drone2 = 0.7 * np.sin(2 * np.pi * 196.00 * t) # G3
warm_drone3 = 0.5 * np.sin(2 * np.pi * 261.63 * t) # C4
warm_drone4 = 0.4 * np.sin(2 * np.pi * 329.63 * t) # E4
rural_mix = (warm_drone1 + warm_drone2 + warm_drone3 + warm_drone4) * 0.22

# Crossfade between horror and rural at 45.0s -> 49.0s
fade_start = 45.0
fade_end = 49.0
horror_env = np.ones(total_samples)
horror_env[t > fade_start] = np.clip(1.0 - (t[t > fade_start] - fade_start) / (fade_end - fade_start), 0.0, 1.0)

rural_env = np.zeros(total_samples)
rural_env[t > fade_start] = np.clip((t[t > fade_start] - fade_start) / (fade_end - fade_start), 0.0, 1.0)

bgm_mono = horror_mix * horror_env + rural_mix * rural_env

# Fade in and out
fade_in = np.clip(t / 2.0, 0, 1)
fade_out = np.clip((duration - t) / 2.5, 0, 1)
bgm_mono = bgm_mono * fade_in * fade_out

# Stereo panning
bgm_left = bgm_mono * 0.95 + 0.05 * np.sin(2 * np.pi * 0.1 * t) * bgm_mono
bgm_right = bgm_mono * 0.95 - 0.05 * np.sin(2 * np.pi * 0.1 * t) * bgm_mono

# Add horror stingers into BGM
# Stinger 1 at 22.32s ("Thần trùng")
stinger1_center = 22.32
idx1 = (t >= stinger1_center) & (t < stinger1_center + 4.0)
t_st1 = t[idx1] - stinger1_center
s1 = np.sin(2 * np.pi * 42.0 * t_st1) * np.exp(-t_st1 * 0.8) * 0.6
bgm_left[idx1] += s1
bgm_right[idx1] += s1

# Stinger 2 at 28.93s ("32 cái đầu")
stinger2_center = 28.93
idx2 = (t >= stinger2_center) & (t < stinger2_center + 4.5)
t_st2 = t[idx2] - stinger2_center
s2 = (np.sin(2 * np.pi * 50.0 * t_st2) + 0.4 * np.sin(2 * np.pi * 148.0 * t_st2)) * np.exp(-t_st2 * 0.7) * 0.7
bgm_left[idx2] += s2
bgm_right[idx2] += s2

# Normalize BGM to -14 LUFS approx (-18dB peak ~ 0.4 max)
max_bgm = np.max(np.abs([bgm_left, bgm_right]))
if max_bgm > 0:
    bgm_left = (bgm_left / max_bgm) * 0.35
    bgm_right = (bgm_right / max_bgm) * 0.35

bgm_stereo = np.column_stack((bgm_left, bgm_right))


# ----------------- SFX TRACK -----------------
sfx_left = np.zeros(total_samples)
sfx_right = np.zeros(total_samples)

# 1. Cloth rustle pulses (counting headbands) at 8.5s, 10.0s, 11.5s, 12.8s, 13.8s
for rustle_t in [8.5, 10.0, 11.5, 12.8, 13.8]:
    idx = (t >= rustle_t) & (t < rustle_t + 0.4)
    t_r = t[idx] - rustle_t
    rustle = np.random.normal(0, 0.08, len(t_r)) * np.sin(np.pi * t_r / 0.4)
    sfx_left[idx] += rustle
    sfx_right[idx] += rustle * 0.9

# 2. Dread impact at 28.93s
idx_dread = (t >= 28.93) & (t < 28.93 + 2.0)
t_dr = t[idx_dread] - 28.93
dread_hit = np.sin(2 * np.pi * 58.0 * t_dr) * np.exp(-t_dr * 3.5) * 0.55
sfx_left[idx_dread] += dread_hit
sfx_right[idx_dread] += dread_hit

# 3. Bronze betel mortar clacks (cối đồng giã trầu)
# From 57.0s to 71.8s every 0.70s
mortar_times = np.arange(57.2, 71.8, 0.70)
for mt in mortar_times:
    idx = (t >= mt) & (t < mt + 0.35)
    t_m = t[idx] - mt
    # Bronze metallic ping (1520Hz & 2780Hz) + wooden thump (160Hz)
    thump = np.sin(2 * np.pi * 160.0 * t_m) * np.exp(-t_m * 24.0) * 0.45
    bronze_ping = (np.sin(2 * np.pi * 1520.0 * t_m) + 0.5 * np.sin(2 * np.pi * 2780.0 * t_m)) * np.exp(-t_m * 14.0) * 0.35
    hit = thump + bronze_ping
    sfx_left[idx] += hit * 0.85
    sfx_right[idx] += hit * 1.0 # Slightly to right ear (grandma is on right)

# Normalize SFX
max_sfx = np.max(np.abs([sfx_left, sfx_right]))
if max_sfx > 0:
    sfx_left = (sfx_left / max_sfx) * 0.50
    sfx_right = (sfx_right / max_sfx) * 0.50

sfx_stereo = np.column_stack((sfx_left, sfx_right))

# Save WAV files (int16 48kHz stereo)
out_dir = "projects/than-trung-chiec-khan-tang-thu-32/preview_1min/assets/audio"
wavfile.write(os.path.join(out_dir, "bgm_72s.wav"), sr, (bgm_stereo * 32767).astype(np.int16))
wavfile.write(os.path.join(out_dir, "sfx_72s.wav"), sr, (sfx_stereo * 32767).astype(np.int16))
print("Generated bgm_72s.wav and sfx_72s.wav successfully!")
