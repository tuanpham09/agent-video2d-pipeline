import os

html_code = '''<!doctype html>
<html lang="vi" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,600;0,700;0,800;0,900;1,700&family=Cinzel:wght@700;900&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {
        --font-sub: 'Be Vietnam Pro', sans-serif;
        --font-title: 'Cinzel', serif;
      }
      * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
      }
      html, body {
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #0d0805;
        font-family: var(--font-sub);
      }
      #root {
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #0f0a06;
      }
      .scene-container {
        position: absolute;
        top: 0;
        left: 0;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
      }
      svg {
        display: block;
        width: 100%;
        height: 100%;
      }
      /* Top Series Badge */
      .top-badge {
        position: absolute;
        top: 36px;
        left: 60px;
        display: flex;
        align-items: center;
        gap: 16px;
        z-index: 90;
        pointer-events: none;
      }
      .badge-tag {
        background: #8b0000;
        color: #fff;
        font-size: 14px;
        font-weight: 800;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        padding: 6px 14px;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.6);
      }
      .badge-title {
        color: #e0d0b8;
        font-family: var(--font-title);
        font-size: 20px;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        text-shadow: 0 2px 6px rgba(0,0,0,0.8);
      }
      /* Subtitles Container */
      .caption-track {
        position: absolute;
        bottom: 50px;
        left: 0;
        width: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 100;
        pointer-events: none;
      }
      .caption-box {
        max-width: 1560px;
        padding: 12px 36px;
        color: #ffffff;
        font-size: 38px;
        font-weight: 700;
        line-height: 1.45;
        text-align: center;
        letter-spacing: -0.01em;
        text-shadow: 0 4px 14px rgba(0,0,0,0.95), 0 2px 4px #000000;
        -webkit-text-stroke: 1.5px #000000;
        paint-order: stroke fill;
      }
      .vignette {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        background: radial-gradient(circle at 50% 50%, transparent 55%, rgba(5,3,2,0.8) 100%);
      }
      .paper-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        opacity: 0.07;
        mix-blend-mode: overlay;
        background-image: repeating-linear-gradient(45deg, #000 0, #000 2px, transparent 2px, transparent 4px);
      }
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="60.5"
      data-width="1920"
      data-height="1080"
      data-layout-allow-overflow
    >
      <!-- Audio Tracks -->
      <audio id="audio-bgm" src="assets/audio/bgm_60s.wav" class="clip" data-start="0" data-duration="60.5" data-track-index="1"></audio>
      <audio id="audio-sfx" src="assets/audio/sfx_60s.wav" class="clip" data-start="0" data-duration="60.5" data-track-index="2"></audio>
      
      <!-- Voice Lines (Đức Trí @ 1.25, 48kHz) -->
      <!-- Scene 1 Lines -->
      <audio id="v-s01-l01" src="assets/audio/S01_L01.wav" class="clip" data-start="0.0" data-duration="5.85" data-track-index="3"></audio>
      <audio id="v-s01-l02" src="assets/audio/S01_L02.wav" class="clip" data-start="6.13" data-duration="1.54" data-track-index="3"></audio>
      <audio id="v-s01-l03" src="assets/audio/S01_L03.wav" class="clip" data-start="7.94" data-duration="3.02" data-track-index="3"></audio>
      <audio id="v-s01-l04" src="assets/audio/S01_L04.wav" class="clip" data-start="11.24" data-duration="3.09" data-track-index="3"></audio>
      <audio id="v-s01-l05a" src="assets/audio/S01_L05a.wav" class="clip" data-start="14.61" data-duration="3.39" data-track-index="3"></audio>
      <audio id="v-s01-l05b" src="assets/audio/S01_L05b.wav" class="clip" data-start="18.26" data-duration="3.77" data-track-index="3"></audio>
      <audio id="v-s01-l06" src="assets/audio/S01_L06.wav" class="clip" data-start="22.33" data-duration="1.67" data-track-index="3"></audio>
      <audio id="v-s01-l07" src="assets/audio/S01_L07.wav" class="clip" data-start="24.28" data-duration="4.38" data-track-index="3"></audio>
      <audio id="v-s01-l08" src="assets/audio/S01_L08.wav" class="clip" data-start="28.93" data-duration="3.27" data-track-index="3"></audio>
      <audio id="v-s01-l09a" src="assets/audio/S01_L09a.wav" class="clip" data-start="32.48" data-duration="1.92" data-track-index="3"></audio>
      <audio id="v-s01-l09b" src="assets/audio/S01_L09b.wav" class="clip" data-start="34.65" data-duration="3.46" data-track-index="3"></audio>
      <audio id="v-s01-l10" src="assets/audio/S01_L10.wav" class="clip" data-start="38.41" data-duration="3.33" data-track-index="3"></audio>
      <audio id="v-s01-l11" src="assets/audio/S01_L11.wav" class="clip" data-start="42.02" data-duration="4.31" data-track-index="3"></audio>
      <!-- Scene 2 Lines -->
      <audio id="v-s02-l01" src="assets/audio/S02_L01.wav" class="clip" data-start="46.82" data-duration="4.14" data-track-index="3"></audio>
      <audio id="v-s02-l02" src="assets/audio/S02_L02.wav" class="clip" data-start="51.24" data-duration="3.58" data-track-index="3"></audio>
      <audio id="v-s02-l03" src="assets/audio/S02_L03.wav" class="clip" data-start="55.10" data-duration="1.43" data-track-index="3"></audio>
      <audio id="v-s02-l04" src="assets/audio/S02_L04.wav" class="clip" data-start="56.81" data-duration="3.26" data-track-index="3"></audio>

      <!-- Global Filter Defs (Line Boil & Hand-drawn Filter) -->
      <svg style="position: absolute; width: 0; height: 0;" aria-hidden="true">
        <defs>
          <filter id="hand-drawn-boil" x="-5%" y="-5%" width="110%" height="110%">
            <feTurbulence id="boil-turb" type="fractalNoise" baseFrequency="0.04" numOctaves="3" result="noise" seed="1" />
            <feDisplacementMap in="SourceGraphic" in2="noise" scale="2.4" xChannelSelector="R" yChannelSelector="G" />
          </filter>
        </defs>
      </svg>

      <!-- Top Header Badge -->
      <div class="top-badge" data-layout-ignore>
        <div class="badge-tag" data-layout-ignore>Truyện Ma Kinh Dị</div>
        <div class="badge-title" data-layout-ignore>Thần Trùng: Chiếc Khăn Tang Thứ 32</div>
      </div>

      <!-- ======================================================== -->
      <!-- SHOT 1: THE ELDER EXPLAINING IN MOURNING HOUSE (0.0s - 6.13s) -->
      <!-- ======================================================== -->
      <div id="shot1" class="clip scene-container" data-start="0" data-duration="6.13" data-track-index="0" data-layout-allow-overflow>
        <svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" filter="url(#hand-drawn-boil)" data-layout-allow-overflow>
          <defs>
            <linearGradient id="s1-wall-grad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#3d2c1d" />
              <stop offset="100%" stop-color="#241a11" />
            </linearGradient>
            <radialGradient id="lamp-light-s1" cx="68%" cy="55%" r="55%">
              <stop offset="0%" stop-color="#ffb703" stop-opacity="0.38" />
              <stop offset="40%" stop-color="#e85d04" stop-opacity="0.18" />
              <stop offset="100%" stop-color="#000000" stop-opacity="0" />
            </radialGradient>
          </defs>

          <!-- Wall Background -->
          <rect width="1920" height="1080" fill="url(#s1-wall-grad)" />
          
          <!-- Wooden Wall Planks & Pillar -->
          <g stroke="#18110b" stroke-width="6">
            <line x1="0" y1="200" x2="1920" y2="200" />
            <line x1="0" y1="400" x2="1920" y2="400" />
            <line x1="0" y1="600" x2="1920" y2="600" />
            <line x1="0" y1="780" x2="1920" y2="780" stroke-width="12" />
            <rect x="180" y="0" width="32" height="1080" fill="#1b120a" />
            <rect x="1700" y="0" width="32" height="1080" fill="#1b120a" />
          </g>

          <!-- Doorway on Left leading to Misty Night Courtyard -->
          <g id="s1-door">
            <rect x="220" y="60" width="380" height="720" fill="#120c07" stroke="#0a0604" stroke-width="12" />
            <rect x="240" y="80" width="340" height="680" fill="#1a2428" />
            <!-- Banana leaf silhouettes in night mist -->
            <path d="M 240 260 Q 320 200 400 240 Q 340 300 240 290 Z" fill="#11181c" />
            <path d="M 240 360 Q 360 300 420 380 Q 330 420 240 400 Z" fill="#11181c" />
            <line x1="240" y1="520" x2="580" y2="520" stroke="#121a1d" stroke-width="6" />
          </g>

          <!-- Ancestral Altar Table on Right -->
          <g id="s1-altar">
            <rect x="1200" y="520" width="460" height="260" rx="4" fill="#321e11" stroke="#0f0905" stroke-width="8" />
            <rect x="1220" y="780" width="30" height="200" fill="#24150b" stroke="#0f0905" stroke-width="7" />
            <rect x="1610" y="780" width="30" height="200" fill="#24150b" stroke="#0f0905" stroke-width="7" />
            <!-- Incense Burner & Rising Smoke -->
            <ellipse cx="1430" cy="510" rx="36" ry="16" fill="#8c7355" stroke="#0f0905" stroke-width="6" />
            <line x1="1425" y1="500" x2="1420" y2="420" stroke="#8b0000" stroke-width="4" />
            <line x1="1435" y1="500" x2="1440" y2="415" stroke="#8b0000" stroke-width="4" />
            <path d="M 1420 420 Q 1410 380 1435 340 Q 1460 300 1445 250" stroke="#d0c8b8" stroke-width="3" fill="none" opacity="0.6" />
            
            <!-- White Candles with Flames -->
            <rect x="1270" y="440" width="16" height="70" fill="#eae4d8" stroke="#0f0905" stroke-width="4" />
            <ellipse id="s1-candle-flame-1" cx="1278" cy="430" rx="8" ry="16" fill="#ffb703" style="transform-origin: 1278px 430px;" />
            <rect x="1580" y="440" width="16" height="70" fill="#eae4d8" stroke="#0f0905" stroke-width="4" />
            <ellipse id="s1-candle-flame-2" cx="1588" cy="430" rx="8" ry="16" fill="#ffb703" style="transform-origin: 1588px 430px;" />
          </g>

          <!-- Floor -->
          <rect x="0" y="780" width="1920" height="300" fill="#1b120a" />

          <!-- Dynamic Candle Light Glow in Room -->
          <rect id="s1-lamp-light" x="600" y="200" width="1200" height="880" fill="url(#lamp-light-s1)" pointer-events="none" />

          <!-- ELDER NARRATOR (Ông Cửu) -->
          <g id="s1-elder-group" style="transform-origin: 880px 750px;">
            <ellipse cx="880" cy="760" rx="90" ry="42" fill="#1f1812" stroke="#0f0905" stroke-width="8" />
            <ellipse cx="830" cy="800" rx="24" ry="14" fill="#0f0905" />
            <ellipse cx="930" cy="800" rx="24" ry="14" fill="#0f0905" />

            <path d="M 800 520 Q 880 500 960 520 L 975 740 L 785 740 Z" fill="#422e1e" stroke="#0f0905" stroke-width="8" stroke-linejoin="round" />
            <path d="M 805 535 Q 770 610 805 680" stroke="#422e1e" stroke-width="38" fill="none" stroke-linecap="round" />
            <circle cx="805" cy="690" r="18" fill="#a57a52" stroke="#0f0905" stroke-width="6" />

            <g id="s1-elder-hand" style="transform-origin: 955px 535px;">
              <path d="M 955 535 Q 1020 600 1005 645" stroke="#422e1e" stroke-width="38" fill="none" stroke-linecap="round" />
              <circle cx="1005" cy="650" r="18" fill="#a57a52" stroke="#0f0905" stroke-width="6" />
              <path d="M 1015 645 L 1055 635" stroke="#a57a52" stroke-width="10" stroke-linecap="round" />
            </g>

            <g id="s1-elder-head" style="transform-origin: 880px 420px;">
              <circle cx="880" cy="315" r="34" fill="#e2ded4" stroke="#0f0905" stroke-width="8" />
              <path d="M 800 410 C 790 320 830 320 880 320 C 930 320 970 320 960 410 C 945 365 920 355 880 355 C 840 355 815 365 800 410 Z" fill="#e2ded4" stroke="#0f0905" stroke-width="8" />
              <ellipse cx="880" cy="425" rx="78" ry="74" fill="#a57a52" stroke="#0f0905" stroke-width="8" />
              <path d="M 845 470 C 850 560 910 560 915 470 Z" fill="#e2ded4" stroke="#0f0905" stroke-width="6" />

              <path d="M 840 365 Q 880 358 920 365" stroke="#66462c" stroke-width="3.5" fill="none" stroke-linecap="round" />
              <path d="M 845 378 Q 880 372 915 378" stroke="#66462c" stroke-width="3.5" fill="none" stroke-linecap="round" />

              <path id="s1-elder-brow-l" d="M 830 395 Q 852 386 870 398" stroke="#48382c" stroke-width="6" fill="none" stroke-linecap="round" />
              <path id="s1-elder-brow-r" d="M 890 398 Q 908 386 930 395" stroke="#48382c" stroke-width="6" fill="none" stroke-linecap="round" />

              <circle cx="850" cy="425" r="18" fill="#ffffff" stroke="#0f0905" stroke-width="5" />
              <circle cx="850" cy="425" r="8.5" fill="#0f0905" />
              <circle cx="853" cy="422" r="3" fill="#ffffff" />
              <rect id="s1-elder-blink-l" x="830" y="405" width="40" height="40" fill="#a57a52" stroke="#0f0905" stroke-width="5" style="transform-origin: 850px 405px;" />

              <circle cx="910" cy="425" r="18" fill="#ffffff" stroke="#0f0905" stroke-width="5" />
              <circle cx="910" cy="425" r="8.5" fill="#0f0905" />
              <circle cx="913" cy="422" r="3" fill="#ffffff" />
              <rect id="s1-elder-blink-r" x="890" y="405" width="40" height="40" fill="#a57a52" stroke="#0f0905" stroke-width="5" style="transform-origin: 910px 405px;" />

              <path id="s1-elder-mouth" d="M 866 466 Q 880 472 894 466" stroke="#0f0905" stroke-width="5" fill="none" stroke-linecap="round" />
            </g>
          </g>
        </svg>

        <div class="caption-track">
          <div class="caption-box">Ở quê tôi, nhà nào có tang, việc đầu tiên không phải là mời thầy, cũng chưa phải là báo họ hàng.</div>
        </div>
      </div>


      <!-- ======================================================== -->
      <!-- SHOT 2: CLOSE-UP COUNTING HEADBANDS (6.13s - 24.28s) -->
      <!-- ======================================================== -->
      <div id="shot2" class="clip scene-container" data-start="6.13" data-duration="18.15" data-track-index="0" data-layout-allow-overflow>
        <svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" filter="url(#hand-drawn-boil)" data-layout-allow-overflow>
          <defs>
            <radialGradient id="shot2-altar-glow" cx="50%" cy="40%" r="65%">
              <stop offset="0%" stop-color="#ff9f1c" stop-opacity="0.32" />
              <stop offset="50%" stop-color="#803400" stop-opacity="0.14" />
              <stop offset="100%" stop-color="#0a0604" stop-opacity="0" />
            </radialGradient>
            <linearGradient id="cloth-white" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#ffffff" />
              <stop offset="70%" stop-color="#eae6dd" />
              <stop offset="100%" stop-color="#cfc9bd" />
            </linearGradient>
            <linearGradient id="bamboo-tray" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#694d2d" />
              <stop offset="50%" stop-color="#a07a4a" />
              <stop offset="100%" stop-color="#5a4024" />
            </linearGradient>
          </defs>

          <rect width="1920" height="1080" fill="#18110b" />
          
          <!-- Background Mourners in White Headbands Kneeling in Shadows -->
          <g id="s2-background-mourners" opacity="0.45">
            <ellipse cx="280" cy="560" rx="70" ry="35" fill="#0d0906" />
            <circle cx="280" cy="420" r="45" fill="#694b32" />
            <rect x="235" y="395" width="90" height="20" rx="3" fill="#eae4d8" />
            
            <ellipse cx="1640" cy="560" rx="70" ry="35" fill="#0d0906" />
            <circle cx="1640" cy="420" r="45" fill="#694b32" />
            <rect x="1595" y="395" width="90" height="20" rx="3" fill="#eae4d8" />
          </g>

          <rect id="s2-ambient-glow" x="200" y="100" width="1520" height="980" fill="url(#shot2-altar-glow)" pointer-events="none" />

          <!-- High Altar Table Surface -->
          <rect x="0" y="700" width="1920" height="380" fill="#24170d" stroke="#0e0704" stroke-width="10" />
          <line x1="0" y1="710" x2="1920" y2="710" stroke="#3d2716" stroke-width="6" />

          <!-- BAMBOO TRAY OF HEADBANDS -->
          <g id="s2-tray-group" style="transform-origin: 960px 820px;">
            <ellipse cx="960" cy="830" rx="320" ry="90" fill="url(#bamboo-tray)" stroke="#0e0704" stroke-width="9" />
            <ellipse cx="960" cy="820" rx="300" ry="78" fill="#4d351d" stroke="#0e0704" stroke-width="6" />

            <rect x="740" y="750" width="440" height="42" rx="10" fill="url(#cloth-white)" stroke="#0e0704" stroke-width="6" />
            <rect x="760" y="720" width="400" height="40" rx="10" fill="url(#cloth-white)" stroke="#0e0704" stroke-width="6" />
            <rect x="780" y="690" width="360" height="38" rx="9" fill="url(#cloth-white)" stroke="#0e0704" stroke-width="6" />

            <g id="s2-counted-headband" style="transform-origin: 960px 680px;">
              <rect x="800" y="660" width="320" height="36" rx="9" fill="#ffffff" stroke="#0e0704" stroke-width="7" />
              <line x1="800" y1="662" x2="780" y2="678" stroke="#dcd5c7" stroke-width="4" />
              <line x1="1120" y1="662" x2="1140" y2="678" stroke="#dcd5c7" stroke-width="4" />
            </g>
          </g>

          <!-- THE MOTHER COUNTING TENSELY -->
          <g id="s2-mother-counting" style="transform-origin: 960px 520px;">
            <path d="M 760 480 Q 960 460 1160 480 L 1220 720 L 700 720 Z" fill="#2d2218" stroke="#0e0704" stroke-width="9" stroke-linejoin="round" />
            <path d="M 780 490 Q 720 590 760 670" stroke="#2d2218" stroke-width="42" fill="none" stroke-linecap="round" />
            <circle cx="760" cy="680" r="20" fill="#b88a62" stroke="#0e0704" stroke-width="6" />

            <g id="s2-counting-hand" style="transform-origin: 1140px 490px;">
              <path d="M 1140 490 Q 1080 580 990 645" stroke="#2d2218" stroke-width="42" fill="none" stroke-linecap="round" />
              <circle cx="985" cy="650" r="22" fill="#b88a62" stroke="#0e0704" stroke-width="6" />
              <path d="M 975 645 L 945 658" stroke="#b88a62" stroke-width="10" stroke-linecap="round" />
              <path d="M 985 640 L 955 648" stroke="#b88a62" stroke-width="9" stroke-linecap="round" />
            </g>

            <g id="s2-mother-head" style="transform-origin: 960px 360px;">
              <ellipse cx="960" cy="340" rx="85" ry="80" fill="#140e09" stroke="#0e0704" stroke-width="8" />
              <ellipse cx="960" cy="365" rx="76" ry="72" fill="#b88a62" stroke="#0e0704" stroke-width="8" />
              
              <rect x="880" y="325" width="160" height="34" rx="4" fill="#ffffff" stroke="#0e0704" stroke-width="7" />
              <path d="M 880 340 L 850 370" stroke="#ffffff" stroke-width="12" stroke-linecap="round" />

              <path id="s2-mother-brow-l" d="M 915 350 Q 935 340 950 354" stroke="#140e09" stroke-width="5" fill="none" stroke-linecap="round" />
              <path id="s2-mother-brow-r" d="M 970 354 Q 985 340 1005 350" stroke="#140e09" stroke-width="5" fill="none" stroke-linecap="round" />

              <circle cx="932" cy="372" r="17" fill="#ffffff" stroke="#0e0704" stroke-width="5" />
              <circle id="s2-mother-pupil-l" cx="934" cy="377" r="8" fill="#0e0704" />
              <circle cx="936" cy="374" r="2.5" fill="#ffffff" />
              <rect id="s2-mother-blink-l" x="912" y="352" width="40" height="40" fill="#b88a62" stroke="#0e0704" stroke-width="5" style="transform-origin: 932px 352px;" />

              <circle cx="988" cy="372" r="17" fill="#ffffff" stroke="#0e0704" stroke-width="5" />
              <circle id="s2-mother-pupil-r" cx="990" cy="377" r="8" fill="#0e0704" />
              <circle cx="992" cy="374" r="2.5" fill="#ffffff" />
              <rect id="s2-mother-blink-r" x="968" y="352" width="40" height="40" fill="#b88a62" stroke="#0e0704" stroke-width="5" style="transform-origin: 988px 352px;" />

              <path id="s2-mother-mouth" d="M 948 412 Q 960 416 972 412" stroke="#0e0704" stroke-width="4.5" fill="none" stroke-linecap="round" />
            </g>
          </g>

          <!-- SUDDEN GHOST SPECTER AT 22.3s ("Họ gọi kẻ ấy là thần trùng") -->
          <g id="s2-specter" opacity="0" style="transform-origin: 1420px 320px;">
            <path d="M 1370 420 C 1350 240 1510 240 1490 420 C 1530 560 1330 560 1370 420 Z" fill="#060403" />
            <rect x="1395" y="300" width="90" height="22" rx="4" fill="#eae4d8" opacity="0.85" />
            <circle cx="1420" cy="335" r="4" fill="#ffffff" />
            <circle cx="1460" cy="335" r="4" fill="#ffffff" />
          </g>
        </svg>

        <div class="caption-track">
          <div id="sub-shot2" class="caption-box">Việc đầu tiên là đếm khăn.</div>
        </div>
      </div>


      <!-- ======================================================== -->
      <!-- SHOT 3: THE 32ND HEADBAND AT DAWN (24.28s - 38.41s) -->
      <!-- ======================================================== -->
      <div id="shot3" class="clip scene-container" data-start="24.28" data-duration="14.13" data-track-index="0" data-layout-allow-overflow>
        <svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" filter="url(#hand-drawn-boil)" data-layout-allow-overflow>
          <defs>
            <radialGradient id="dawn-fog" cx="50%" cy="30%" r="70%">
              <stop offset="0%" stop-color="#4a3b32" stop-opacity="0.4" />
              <stop offset="60%" stop-color="#1e1510" stop-opacity="0.8" />
              <stop offset="100%" stop-color="#0a0604" stop-opacity="1" />
            </radialGradient>
          </defs>

          <rect width="1920" height="1080" fill="url(#dawn-fog)" />

          <!-- Background Mourners (Crowd of 31 mourners in silhouettes) -->
          <g id="mourners-crowd" opacity="0.6">
            <!-- Row of Kneeling Mourners -->
            <g fill="#18110b" stroke="#0a0604" stroke-width="4">
              <ellipse cx="250" cy="740" rx="60" ry="30" />
              <circle cx="250" cy="640" r="38" fill="#5c432d" />
              <rect x="215" y="618" width="70" height="16" rx="3" fill="#ffffff" />

              <ellipse cx="420" cy="740" rx="60" ry="30" />
              <circle cx="420" cy="640" r="38" fill="#5c432d" />
              <rect x="385" y="618" width="70" height="16" rx="3" fill="#ffffff" />

              <ellipse cx="590" cy="740" rx="60" ry="30" />
              <circle cx="590" cy="640" r="38" fill="#5c432d" />
              <rect x="555" y="618" width="70" height="16" rx="3" fill="#ffffff" />

              <ellipse cx="1330" cy="740" rx="60" ry="30" />
              <circle cx="1330" cy="640" r="38" fill="#5c432d" />
              <rect x="1295" y="618" width="70" height="16" rx="3" fill="#ffffff" />

              <ellipse cx="1500" cy="740" rx="60" ry="30" />
              <circle cx="1500" cy="640" r="38" fill="#5c432d" />
              <rect x="1465" y="618" width="70" height="16" rx="3" fill="#ffffff" />

              <ellipse cx="1670" cy="740" rx="60" ry="30" />
              <circle cx="1670" cy="640" r="38" fill="#5c432d" />
              <rect x="1635" y="618" width="70" height="16" rx="3" fill="#ffffff" />
            </g>
          </g>

          <!-- High Altar in Background Center -->
          <rect x="760" y="460" width="400" height="240" fill="#291a10" stroke="#0a0604" stroke-width="8" />
          <ellipse cx="960" cy="450" rx="40" ry="16" fill="#80684c" stroke="#0a0604" stroke-width="6" />
          <line x1="955" y1="440" x2="950" y2="350" stroke="#8b0000" stroke-width="4" />
          <line x1="965" y1="440" x2="970" y2="345" stroke="#8b0000" stroke-width="4" />

          <!-- Floor -->
          <rect x="0" y="740" width="1920" height="340" fill="#140d08" />

          <!-- THE MOTHER STANDING IN SHOCK AT 28.9s (32 cái đầu) -->
          <g id="s3-mother-shocked" style="transform-origin: 960px 620px;">
            <!-- White Mourning Robe -->
            <path d="M 880 500 Q 960 480 1040 500 L 1060 840 L 860 840 Z" fill="#eae6dd" stroke="#0a0604" stroke-width="8" stroke-linejoin="round" />
            <!-- Hands touching mouth in terror -->
            <path d="M 885 520 Q 840 600 930 550" stroke="#eae6dd" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="935" cy="540" r="16" fill="#b88a62" stroke="#0a0604" stroke-width="5" />
            <path d="M 1035 520 Q 1080 600 990 550" stroke="#eae6dd" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="985" cy="540" r="16" fill="#b88a62" stroke="#0a0604" stroke-width="5" />

            <!-- Head -->
            <g id="s3-mother-head" style="transform-origin: 960px 420px;">
              <ellipse cx="960" cy="410" rx="72" ry="70" fill="#140e09" stroke="#0a0604" stroke-width="8" />
              <ellipse cx="960" cy="425" rx="66" ry="64" fill="#b88a62" stroke="#0a0604" stroke-width="8" />
              <rect x="895" y="385" width="130" height="30" rx="4" fill="#ffffff" stroke="#0a0604" stroke-width="6" />

              <!-- Horrified Wide Eyes -->
              <circle cx="936" cy="428" r="18" fill="#ffffff" stroke="#0a0604" stroke-width="5" />
              <circle id="s3-pupil-l" cx="936" cy="428" r="7" fill="#0a0604" />
              <circle cx="938" cy="425" r="2.5" fill="#ffffff" />
              <rect id="s3-blink-l" x="916" y="408" width="40" height="40" fill="#b88a62" stroke="#0a0604" stroke-width="5" style="transform-origin: 936px 408px;" />

              <circle cx="984" cy="428" r="18" fill="#ffffff" stroke="#0a0604" stroke-width="5" />
              <circle id="s3-pupil-r" cx="984" cy="428" r="7" fill="#0a0604" />
              <circle cx="986" cy="425" r="2.5" fill="#ffffff" />
              <rect id="s3-blink-r" x="964" y="408" width="40" height="40" fill="#b88a62" stroke="#0a0604" stroke-width="5" style="transform-origin: 984px 408px;" />

              <!-- Trembling Open Mouth (Há hốc bàng hoàng) -->
              <ellipse id="s3-mouth" cx="960" cy="465" rx="10" ry="14" fill="#0a0604" stroke="#0a0604" stroke-width="3" />
            </g>
          </g>

          <!-- THE 32ND GHOST ENTITY STANDING IN THE BACKGROUND RIGHT (Chiếc khăn tang thứ 32) -->
          <g id="s3-ghost-32" style="transform-origin: 1220px 480px;">
            <path d="M 1180 520 C 1170 340 1270 340 1260 520 L 1275 750 L 1165 750 Z" fill="#cfc9bd" stroke="#0a0604" stroke-width="7" />
            <!-- White Mourning Headband on Ghost Head -->
            <rect x="1195" y="380" width="70" height="20" rx="3" fill="#ffffff" stroke="#0a0604" stroke-width="6" />
            <!-- Hollow Black Faceless Void -->
            <ellipse cx="1220" cy="420" rx="28" ry="34" fill="#0c0805" />
            <circle cx="1212" cy="415" r="3" fill="#ffffff" />
            <circle cx="1228" cy="415" r="3" fill="#ffffff" />
          </g>
        </svg>

        <div class="caption-track">
          <div id="sub-shot3" class="caption-box">Tháng bảy âm lịch năm ngoái, bà nội tôi mất, nhà tôi phát ba mươi mốt chiếc khăn.</div>
        </div>
      </div>


      <!-- ======================================================== -->
      <!-- SHOT 4: NARRATOR ĐỖ VĂN LÂM IN CLOSE-UP (38.41s - 46.82s) -->
      <!-- ======================================================== -->
      <div id="shot4" class="clip scene-container" data-start="38.41" data-duration="8.41" data-track-index="0" data-layout-allow-overflow>
        <svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" filter="url(#hand-drawn-boil)" data-layout-allow-overflow>
          <defs>
            <radialGradient id="narrator-spotlight" cx="50%" cy="45%" r="60%">
              <stop offset="0%" stop-color="#3d2c1f" stop-opacity="0.8" />
              <stop offset="65%" stop-color="#160f0a" stop-opacity="0.95" />
              <stop offset="100%" stop-color="#0a0604" stop-opacity="1" />
            </radialGradient>
          </defs>

          <rect width="1920" height="1080" fill="url(#narrator-spotlight)" />

          <!-- NARRATOR LÂM (31 tuổi, chàng trai nhìn thẳng vào khán giả) -->
          <g id="narrator-lam-group" style="transform-origin: 960px 650px;">
            <!-- Dark Navy Rural/Modern Shirt -->
            <path d="M 780 620 Q 960 590 1140 620 L 1180 1080 L 740 1080 Z" fill="#243038" stroke="#0a0604" stroke-width="10" stroke-linejoin="round" />
            
            <!-- Head & Face -->
            <g id="narrator-lam-head" style="transform-origin: 960px 480px;">
              <!-- Modern neat black hair -->
              <path d="M 870 460 C 865 340 1055 340 1050 460 C 1030 400 990 380 960 380 C 930 380 890 400 870 460 Z" fill="#140e09" stroke="#0a0604" stroke-width="9" stroke-linejoin="round" />
              <ellipse cx="960" cy="485" rx="90" ry="86" fill="#ba8c63" stroke="#0a0604" stroke-width="9" />

              <!-- Determined Eyebrows -->
              <path id="lam-brow-l" d="M 905 445 Q 930 435 950 445" stroke="#140e09" stroke-width="6" fill="none" stroke-linecap="round" />
              <path id="lam-brow-r" d="M 970 445 Q 990 435 1015 445" stroke="#140e09" stroke-width="6" fill="none" stroke-linecap="round" />

              <!-- Sincere, Intense Eyes looking directly at camera -->
              <circle cx="925" cy="480" r="20" fill="#ffffff" stroke="#0a0604" stroke-width="6" />
              <circle cx="925" cy="480" r="9.5" fill="#0a0604" />
              <circle cx="928" cy="477" r="3.5" fill="#ffffff" />
              <rect id="lam-blink-l" x="900" y="455" width="50" height="50" fill="#ba8c63" stroke="#0a0604" stroke-width="5" style="transform-origin: 925px 455px;" />

              <circle cx="995" cy="480" r="20" fill="#ffffff" stroke="#0a0604" stroke-width="6" />
              <circle cx="995" cy="480" r="9.5" fill="#0a0604" />
              <circle cx="998" cy="477" r="3.5" fill="#ffffff" />
              <rect id="lam-blink-r" x="970" y="455" width="50" height="50" fill="#ba8c63" stroke="#0a0604" stroke-width="5" style="transform-origin: 995px 455px;" />

              <!-- Speaking Mouth -->
              <path id="lam-mouth" d="M 942 536 Q 960 545 978 536" stroke="#0a0604" stroke-width="5.5" fill="none" stroke-linecap="round" />
            </g>
          </g>
        </svg>

        <div class="caption-track">
          <div id="sub-shot4" class="caption-box">Hôm nay tôi kể hết, kể cả phần chưa kể với ai bao giờ.</div>
        </div>
      </div>


      <!-- ======================================================== -->
      <!-- SHOT 5: CHILDHOOD MEMORY AT DOORSTEP (46.82s - 60.5s) -->
      <!-- ======================================================== -->
      <div id="shot5" class="clip scene-container" data-start="46.82" data-duration="13.68" data-track-index="0" data-layout-allow-overflow>
        <svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" filter="url(#hand-drawn-boil)" data-layout-allow-overflow>
          <defs>
            <linearGradient id="afternoon-sky" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#e8cfa6" />
              <stop offset="100%" stop-color="#b89e72" />
            </linearGradient>
            <linearGradient id="afternoon-yard" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#737d57" />
              <stop offset="100%" stop-color="#555c3e" />
            </linearGradient>
            <linearGradient id="s5-wall" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#523d2b" />
              <stop offset="100%" stop-color="#3b2b1d" />
            </linearGradient>
            <linearGradient id="bronze-c5" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#805d2c" />
              <stop offset="35%" stop-color="#caa25f" />
              <stop offset="70%" stop-color="#e0bb7b" />
              <stop offset="100%" stop-color="#6d4d21" />
            </linearGradient>
          </defs>

          <!-- Rustic Wooden House Wall in Afternoon Sun -->
          <rect width="1920" height="1080" fill="url(#s5-wall)" />
          
          <line x1="0" y1="220" x2="1920" y2="220" stroke="#251a10" stroke-width="5" opacity="0.75" />
          <line x1="0" y1="440" x2="1920" y2="440" stroke="#251a10" stroke-width="5" opacity="0.75" />
          <line x1="0" y1="660" x2="1920" y2="660" stroke="#251a10" stroke-width="5" opacity="0.75" />
          
          <rect x="0" y="780" width="1920" height="300" fill="#291d13" />
          <line x1="0" y1="780" x2="1920" y2="780" stroke="#140e09" stroke-width="8" />

          <!-- DOORWAY ON RIGHT LEADING TO AFTERNOON YARD -->
          <g id="s5-doorway">
            <rect x="1170" y="30" width="480" height="750" fill="#24170d" stroke="#120a05" stroke-width="12" />
            <rect x="1200" y="60" width="420" height="420" fill="url(#afternoon-sky)" />
            <rect x="1200" y="480" width="420" height="270" fill="url(#afternoon-yard)" />
            <line x1="1200" y1="480" x2="1620" y2="480" stroke="#3d442c" stroke-width="5" />
            <!-- Door Step (Bậc cửa gỗ cao) -->
            <rect x="1130" y="710" width="560" height="95" rx="4" fill="#5c3f25" stroke="#120a05" stroke-width="9" />
            <line x1="1135" y1="718" x2="1685" y2="718" stroke="#7a5534" stroke-width="4" />
          </g>

          <!-- LEFT: BAMBOO DAYBED (Chõng tre) WITH YOUNG LÂM ASLEEP -->
          <g id="s5-daybed">
            <rect x="90" y="600" width="28" height="180" rx="4" fill="#3a2717" stroke="#120a05" stroke-width="7" />
            <rect x="710" y="600" width="28" height="180" rx="4" fill="#3a2717" stroke="#120a05" stroke-width="7" />
            <rect x="40" y="520" width="740" height="90" rx="8" fill="#8c6c42" stroke="#120a05" stroke-width="9" />
            
            <g stroke="#5c4324" stroke-width="4">
              <line x1="100" y1="525" x2="100" y2="605" /><line x1="160" y1="525" x2="160" y2="605" />
              <line x1="220" y1="525" x2="220" y2="605" /><line x1="280" y1="525" x2="280" y2="605" />
              <line x1="340" y1="525" x2="340" y2="605" /><line x1="400" y1="525" x2="400" y2="605" />
              <line x1="460" y1="525" x2="460" y2="605" /><line x1="520" y1="525" x2="520" y2="605" />
              <line x1="580" y1="525" x2="580" y2="605" /><line x1="640" y1="525" x2="640" y2="605" />
              <line x1="700" y1="525" x2="700" y2="605" />
            </g>

            <!-- Young Lâm sleeping on bamboo daybed -->
            <g id="s5-young-lam" style="transform-origin: 480px 520px;">
              <ellipse cx="400" cy="510" rx="60" ry="55" fill="#c49770" stroke="#120a05" stroke-width="7" />
              <path d="M 335 520 Q 330 440 400 440 Q 470 440 465 520 C 455 490 440 475 400 475 C 360 475 345 490 335 520 Z" fill="#18120d" stroke="#120a05" stroke-width="7" />
              <path d="M 370 512 Q 382 524 394 512" stroke="#18120d" stroke-width="6" fill="none" stroke-linecap="round" />
              <path d="M 408 512 Q 420 524 432 512" stroke="#18120d" stroke-width="6" fill="none" stroke-linecap="round" />
              <path d="M 395 536 Q 402 542 410 536" stroke="#18120d" stroke-width="4" fill="none" stroke-linecap="round" />
              
              <rect x="460" y="468" width="120" height="90" rx="16" fill="#8ea583" stroke="#120a05" stroke-width="8" />
              <path d="M 460 525 Q 520 540 575 532" stroke="#8ea583" stroke-width="26" fill="none" stroke-linecap="round" />
              <circle cx="585" cy="532" r="14" fill="#c49770" stroke="#120a05" stroke-width="5" />
              <rect x="580" y="485" width="70" height="52" fill="#3a2a1c" stroke="#120a05" stroke-width="7" />
              <rect x="650" y="480" width="36" height="60" rx="14" fill="#140e09" stroke="#120a05" stroke-width="6" />
            </g>
          </g>

          <!-- RIGHT: GRANDMOTHER POUNDING BETEL (Bà cụ giã trầu) -->
          <g id="s5-grandma">
            <ellipse cx="1275" cy="650" rx="65" ry="32" fill="#24170d" stroke="#120a05" stroke-width="7" />
            <ellipse cx="1245" cy="710" rx="22" ry="12" fill="#120a05" />
            <ellipse cx="1305" cy="710" rx="22" ry="12" fill="#120a05" />

            <path d="M 1215 440 Q 1275 430 1335 440 L 1350 620 L 1200 620 Z" fill="#4a3424" stroke="#120a05" stroke-width="8" stroke-linejoin="round" />
            <path d="M 1215 450 Q 1180 515 1205 575" stroke="#4a3424" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="1205" cy="585" r="16" fill="#ba8c63" stroke="#120a05" stroke-width="5" />

            <g id="s5-grandma-head" style="transform-origin: 1275px 400px;">
              <circle cx="1195" cy="350" r="14" fill="#ba8c63" stroke="#120a05" stroke-width="6" />
              <circle cx="1355" cy="350" r="14" fill="#ba8c63" stroke="#120a05" stroke-width="6" />
              <ellipse cx="1275" cy="355" rx="75" ry="72" fill="#ba8c63" stroke="#120a05" stroke-width="8" />
              
              <circle cx="1275" cy="245" r="32" fill="#eae5dc" stroke="#120a05" stroke-width="8" />
              <path d="M 1200 340 C 1195 260 1230 250 1275 250 C 1320 250 1355 260 1350 340 C 1335 305 1310 290 1275 290 C 1240 290 1215 305 1200 340 Z" fill="#eae5dc" stroke="#120a05" stroke-width="8" />

              <path d="M 1228 322 Q 1244 314 1260 322" stroke="#63574c" stroke-width="5" fill="none" stroke-linecap="round" />
              <path d="M 1290 322 Q 1306 314 1322 322" stroke="#63574c" stroke-width="5" fill="none" stroke-linecap="round" />

              <circle cx="1245" cy="355" r="19" fill="#ffffff" stroke="#120a05" stroke-width="5" />
              <circle cx="1245" cy="355" r="9" fill="#120a05" />
              <circle cx="1248" cy="352" r="3.5" fill="#ffffff" />
              <rect id="s5-grandma-blink-l" x="1224" y="334" width="42" height="42" fill="#ba8c63" stroke="#120a05" stroke-width="5" style="transform-origin: 1245px 335px;" />

              <circle cx="1305" cy="355" r="19" fill="#ffffff" stroke="#120a05" stroke-width="5" />
              <circle cx="1305" cy="355" r="9" fill="#120a05" />
              <circle cx="1308" cy="352" r="3.5" fill="#ffffff" />
              <rect id="s5-grandma-blink-r" x="1284" y="334" width="42" height="42" fill="#ba8c63" stroke="#120a05" stroke-width="5" style="transform-origin: 1305px 335px;" />

              <path d="M 1262 396 Q 1275 408 1288 396" stroke="#120a05" stroke-width="5" fill="none" stroke-linecap="round" />
              <path d="M 1234 378 Q 1245 385 1256 378" stroke="#8a6140" stroke-width="3" fill="none" stroke-linecap="round" />
              <path d="M 1294 378 Q 1305 385 1316 378" stroke="#8a6140" stroke-width="3" fill="none" stroke-linecap="round" />
            </g>

            <!-- Mortar on Doorstep -->
            <g id="s5-mortar">
              <path d="M 1370 660 L 1380 720 Q 1425 735 1470 720 L 1480 660 Z" fill="url(#bronze-c5)" stroke="#120a05" stroke-width="7" />
              <ellipse cx="1425" cy="660" rx="55" ry="16" fill="#523916" stroke="#120a05" stroke-width="6" />
              <ellipse cx="1425" cy="722" rx="42" ry="10" fill="#3b270c" stroke="#120a05" stroke-width="5" />
            </g>

            <!-- Pounding Pestle Arm -->
            <g id="s5-pounding-arm" style="transform-origin: 1330px 460px;">
              <path d="M 1330 455 Q 1385 520 1375 565" stroke="#4a3424" stroke-width="36" fill="none" stroke-linecap="round" />
              <circle cx="1375" cy="570" r="18" fill="#ba8c63" stroke="#120a05" stroke-width="6" />
              <rect x="1366" y="525" width="20" height="150" rx="9" fill="url(#bronze-c5)" stroke="#120a05" stroke-width="6" transform="rotate(-6 1375 570)" />
            </g>
          </g>
        </svg>

        <div class="caption-track">
          <div id="sub-shot5" class="caption-box">Tôi tên Đỗ Văn Lâm, ba mươi mốt tuổi, làm kỹ sư cầu đường ở Sài Gòn.</div>
        </div>
      </div>

      <!-- Overlays -->
      <div class="paper-overlay"></div>
      <div class="vignette"></div>
    </div>

    <!-- GSAP Master Animation Timeline -->
    <script>
      const tl = gsap.timeline({ paused: true });

      // Initialize all blinking eyelid scales to 0
      gsap.set(["#s1-elder-blink-l", "#s1-elder-blink-r", "#s2-mother-blink-l", "#s2-mother-blink-r", "#s3-blink-l", "#s3-blink-r", "#lam-blink-l", "#lam-blink-r", "#s5-grandma-blink-l", "#s5-grandma-blink-r"], { scaleY: 0 });

      // -------------------------------------------------------------
      // SHOT 1: THE ELDER SPEAKING (0.0s - 6.13s)
      // -------------------------------------------------------------
      for (let t = 0.0; t < 6.13; t += 0.2) {
        const sY = 0.88 + Math.sin(t * 15) * 0.16;
        const skew = Math.cos(t * 11) * 7;
        tl.to(["#s1-candle-flame-1", "#s1-candle-flame-2"], { scaleY: sY, skewX: skew, duration: 0.2, ease: "sine.inOut" }, t);
        tl.to("#s1-lamp-light", { opacity: 0.8 + Math.sin(t * 18) * 0.2, duration: 0.2, ease: "sine.inOut" }, t);
      }

      tl.to("#s1-elder-head", { y: -3, rotation: 1.2, duration: 1.8, repeat: 3, yoyo: true, ease: "sine.inOut" }, 0);
      tl.to("#s1-elder-hand", { rotation: -8, y: -15, duration: 1.2, ease: "power2.out" }, 1.0);
      tl.to("#s1-elder-hand", { rotation: 2, y: 4, duration: 1.4, ease: "sine.inOut" }, 3.0);
      tl.to("#s1-elder-hand", { rotation: 0, y: 0, duration: 0.8, ease: "power1.inOut" }, 4.8);

      [1.6, 4.2].forEach(time => {
        tl.to(["#s1-elder-blink-l", "#s1-elder-blink-r"], { scaleY: 1, duration: 0.08, ease: "power1.in" }, time);
        tl.to(["#s1-elder-blink-l", "#s1-elder-blink-r"], { scaleY: 0, duration: 0.08, ease: "power1.out" }, time + 0.08);
      });

      for (let t = 0.4; t < 5.6; t += 0.24) {
        tl.to("#s1-elder-mouth", { attr: { d: "M 864 466 Q 880 482 896 466" }, duration: 0.11, ease: "sine.inOut" }, t);
        tl.to("#s1-elder-mouth", { attr: { d: "M 866 466 Q 880 472 894 466" }, duration: 0.11, ease: "sine.inOut" }, t + 0.11);
      }

      // -------------------------------------------------------------
      // SHOT 2: CLOSE-UP COUNTING HEADBANDS (6.13s - 24.28s)
      // -------------------------------------------------------------
      tl.set("#sub-shot2", { textContent: "Việc đầu tiên là đếm khăn." }, 6.13);
      tl.set("#sub-shot2", { textContent: "Con cháu bao nhiêu người thì phát bấy nhiêu chiếc khăn xô." }, 7.94);
      tl.set("#sub-shot2", { textContent: "Phát xong phải đếm lại, không được thừa cũng không được thiếu." }, 11.24);
      tl.set("#sub-shot2", { textContent: "Người già bảo nếu đếm đầu người đội khăn mà ra nhiều hơn số" }, 14.61);
      tl.set("#sub-shot2", { textContent: "khăn đã phát thì trong đám tang ấy có một kẻ không phải người nhà." }, 18.26);
      tl.set("#sub-shot2", { textContent: "Họ gọi kẻ ấy là thần trùng." }, 22.33);

      tl.to("#s2-mother-counting", { y: -3, duration: 1.6, repeat: 11, yoyo: true, ease: "sine.inOut" }, 6.13);

      // Counting motion pulses
      [6.8, 8.8, 10.4, 12.0, 16.0, 19.5].forEach(time => {
        tl.to("#s2-counting-hand", { y: -30, x: -15, rotation: -7, duration: 0.4, ease: "power1.out" }, time);
        tl.to("#s2-counted-headband", { y: -18, rotation: -2, duration: 0.4, ease: "power1.out" }, time);
        tl.to("#s2-counting-hand", { y: 0, x: 0, rotation: 0, duration: 0.35, ease: "power2.in" }, time + 0.4);
        tl.to("#s2-counted-headband", { y: 0, rotation: 0, duration: 0.35, ease: "power2.in" }, time + 0.4);
      });

      [7.6, 10.8, 15.2, 19.8].forEach(time => {
        tl.to(["#s2-mother-blink-l", "#s2-mother-blink-r"], { scaleY: 1, duration: 0.08, ease: "power1.in" }, time);
        tl.to(["#s2-mother-blink-l", "#s2-mother-blink-r"], { scaleY: 0, duration: 0.08, ease: "power1.out" }, time + 0.08);
      });

      for (let t = 6.2; t < 22.0; t += 0.25) {
        tl.to("#s2-ambient-glow", { opacity: 0.75 + Math.sin(t * 14) * 0.25, duration: 0.25, ease: "sine.inOut" }, t);
      }

      // 22.33s: "Họ gọi kẻ ấy là thần trùng." -> Dim light, ghost looms
      tl.to("#s2-ambient-glow", { opacity: 0.3, duration: 1.2, ease: "power2.in", overwrite: "auto" }, 22.3);
      tl.to("#s2-specter", { opacity: 0.9, y: -20, duration: 1.5, ease: "power2.out" }, 22.4);
      tl.to(["#s2-mother-pupil-l", "#s2-mother-pupil-r"], { attr: { cx: "+=6", cy: "-=3" }, duration: 0.4 }, 22.8);

      // -------------------------------------------------------------
      // SHOT 3: 32ND HEADBAND AT DAWN (24.28s - 38.41s)
      // -------------------------------------------------------------
      tl.set("#sub-shot3", { textContent: "Tháng bảy âm lịch năm ngoái, bà nội tôi mất, nhà tôi phát ba mươi mốt chiếc khăn." }, 24.28);
      tl.set("#sub-shot3", { textContent: "Sáng hôm sau, mẹ tôi đếm được ba mươi hai cái đầu." }, 28.93);
      tl.set("#sub-shot3", { textContent: "Chuyện ấy tôi đã kể với nhiều người," }, 32.48);
      tl.set("#sub-shot3", { textContent: "ai nghe xong cũng hỏi một câu, thế rốt cuộc người thừa ra là ai?" }, 34.65);

      // 28.93s: Mother reacts in shock
      tl.to("#s3-mother-shocked", { scale: 1.05, duration: 0.3, ease: "back.out(2)" }, 28.93);
      tl.to("#s3-mouth", { attr: { ry: 20 }, duration: 0.3 }, 28.93);
      tl.to(["#s3-pupil-l", "#s3-pupil-r"], { attr: { cx: "+=7" }, duration: 0.5 }, 29.2);

      [26.0, 31.5, 36.0].forEach(time => {
        tl.to(["#s3-blink-l", "#s3-blink-r"], { scaleY: 1, duration: 0.08, ease: "power1.in" }, time);
        tl.to(["#s3-blink-l", "#s3-blink-r"], { scaleY: 0, duration: 0.08, ease: "power1.out" }, time + 0.08);
      });

      // -------------------------------------------------------------
      // SHOT 4: NARRATOR ĐỖ VĂN LÂM (38.41s - 46.82s)
      // -------------------------------------------------------------
      tl.set("#sub-shot4", { textContent: "Hôm nay tôi kể hết, kể cả phần chưa kể với ai bao giờ." }, 38.41);
      tl.set("#sub-shot4", { textContent: "Bạn nghe cho hết nhé, vì câu trả lời chính tôi cũng phải đến tận cuối mới biết." }, 42.02);

      tl.to("#narrator-lam-head", { y: -3, duration: 1.8, repeat: 4, yoyo: true, ease: "sine.inOut" }, 38.41);

      // Speaking mouth flap for Lâm
      for (let t = 38.6; t < 46.2; t += 0.22) {
        tl.to("#lam-mouth", { attr: { d: "M 940 536 Q 960 556 980 536" }, duration: 0.1, ease: "sine.inOut" }, t);
        tl.to("#lam-mouth", { attr: { d: "M 942 536 Q 960 545 978 536" }, duration: 0.1, ease: "sine.inOut" }, t + 0.1);
      }

      [40.2, 44.0].forEach(time => {
        tl.to(["#lam-blink-l", "#lam-blink-r"], { scaleY: 1, duration: 0.08, ease: "power1.in" }, time);
        tl.to(["#lam-blink-l", "#lam-blink-r"], { scaleY: 0, duration: 0.08, ease: "power1.out" }, time + 0.08);
      });

      // -------------------------------------------------------------
      // SHOT 5: CHILDHOOD MEMORY AT DOORSTEP (46.82s - 60.5s)
      // -------------------------------------------------------------
      tl.set("#sub-shot5", { textContent: "Tôi tên Đỗ Văn Lâm, ba mươi mốt tuổi, làm kỹ sư cầu đường ở Sài Gòn." }, 46.82);
      tl.set("#sub-shot5", { textContent: "Quê tôi ở một làng ven sông Luộc, tên làng cho tôi xin giấu." }, 51.24);
      tl.set("#sub-shot5", { textContent: "Tôi là cháu đích tôn." }, 55.10);
      tl.set("#sub-shot5", { textContent: "Bố mẹ tôi có hai anh em, tôi và em gái tôi là Ngân." }, 56.81);

      // Young Lâm breathing on daybed
      tl.to("#s5-young-lam", { scaleY: 1.04, y: -3, duration: 1.8, repeat: 7, yoyo: true, ease: "sine.inOut" }, 46.82);

      // Grandma pounding betel pestle (cốc... cốc...)
      for (let t = 48.0; t < 60.0; t += 0.65) {
        tl.to("#s5-pounding-arm", { y: -42, rotation: -8, duration: 0.32, ease: "power1.out" }, t);
        tl.to("#s5-pounding-arm", { y: 0, rotation: 0, duration: 0.22, ease: "power2.in" }, t + 0.32);
      }

      tl.to("#s5-grandma-head", { y: 4, rotation: 1.5, duration: 1.6, repeat: 8, yoyo: true, ease: "sine.inOut" }, 47.0);

      [49.0, 53.5, 57.5].forEach(time => {
        tl.to(["#s5-grandma-blink-l", "#s5-grandma-blink-r"], { scaleY: 1, duration: 0.08, ease: "power1.in" }, time);
        tl.to(["#s5-grandma-blink-l", "#s5-grandma-blink-r"], { scaleY: 0, duration: 0.08, ease: "power1.out" }, time + 0.08);
      });

      // Line boil animation driver across all 60.5s (animating on twos ~6fps)
      for (let f = 0; f < 60.5; f += 0.16) {
        const seedVal = Math.floor(f * 6) + 1;
        tl.set("#boil-turb", { attr: { seed: seedVal } }, f);
      }

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''

with open('projects/than-trung-chiec-khan-tang-thu-32/preview_1min/index.html', 'w', encoding='utf-8') as f:
    f.write(html_code)

print("Generated preview_1min/index.html successfully!")
