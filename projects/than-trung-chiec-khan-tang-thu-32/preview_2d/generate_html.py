html_content = '''<!doctype html>
<html lang="vi" data-resolution="landscape">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:ital,wght@0,600;0,700;0,800;0,900;1,700&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      :root {
        --font-sub: 'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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
        background: #000;
        font-family: var(--font-sub);
      }
      #root {
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #120c08;
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
      /* Subtitles */
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
        max-width: 1600px;
        padding: 12px 32px;
        color: #ffffff;
        font-size: 42px;
        font-weight: 700;
        line-height: 1.45;
        text-align: center;
        letter-spacing: -0.01em;
        text-shadow: 0 4px 12px rgba(0,0,0,0.9), 0 2px 4px #000000;
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
        background: radial-gradient(circle at 50% 50%, transparent 60%, rgba(0,0,0,0.7) 100%);
      }
    </style>
  </head>
  <body>
    <div
      id="root"
      data-composition-id="main"
      data-start="0"
      data-duration="16.0"
      data-width="1920"
      data-height="1080"
      data-layout-allow-overflow
    >
      <!-- Audio Elements -->
      <audio id="audio-line1" src="assets/audio/line1.wav" class="clip" data-start="0.4" data-duration="6.0" data-track-index="1"></audio>
      <audio id="audio-line2" src="assets/audio/line2.wav" class="clip" data-start="7.8" data-duration="7.68" data-track-index="1"></audio>

      <!-- SCENE 1: Grandmother at Doorstep (0.0s - 7.5s) -->
      <div id="scene1" class="clip scene-container" data-start="0" data-duration="7.5" data-track-index="0" data-layout-allow-overflow>
        <svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" data-layout-allow-overflow>
          <defs>
            <linearGradient id="wall-grad" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#4e3926" />
              <stop offset="100%" stop-color="#342517" />
            </linearGradient>
            <linearGradient id="door-sky" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#dedabe" />
              <stop offset="100%" stop-color="#b8b598" />
            </linearGradient>
            <linearGradient id="door-yard" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#6e7855" />
              <stop offset="100%" stop-color="#555d40" />
            </linearGradient>
            <linearGradient id="bronze" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stop-color="#805d2c" />
              <stop offset="35%" stop-color="#caa25f" />
              <stop offset="70%" stop-color="#e0bb7b" />
              <stop offset="100%" stop-color="#6d4d21" />
            </linearGradient>
          </defs>

          <!-- Wall Background -->
          <rect width="1920" height="1080" fill="url(#wall-grad)" />
          
          <!-- Wooden Wall Planks Horizontal Seams -->
          <line x1="0" y1="220" x2="1920" y2="220" stroke="#251a10" stroke-width="5" opacity="0.75" />
          <line x1="0" y1="440" x2="1920" y2="440" stroke="#251a10" stroke-width="5" opacity="0.75" />
          <line x1="0" y1="660" x2="1920" y2="660" stroke="#251a10" stroke-width="5" opacity="0.75" />
          
          <!-- Wooden Floor / Baseboard -->
          <rect x="0" y="780" width="1920" height="300" fill="#291d13" />
          <line x1="0" y1="780" x2="1920" y2="780" stroke="#140e09" stroke-width="8" />

          <!-- DOORWAY ON RIGHT (Matching Screenshot 1) -->
          <g id="doorway">
            <rect x="1170" y="30" width="480" height="750" fill="#24170d" stroke="#120a05" stroke-width="12" />
            <rect x="1200" y="60" width="420" height="420" fill="url(#door-sky)" />
            <rect x="1200" y="480" width="420" height="270" fill="url(#door-yard)" />
            <line x1="1200" y1="480" x2="1620" y2="480" stroke="#3d442c" stroke-width="5" />
            <rect x="1130" y="710" width="560" height="95" rx="4" fill="#5c3f25" stroke="#120a05" stroke-width="9" />
            <line x1="1135" y1="718" x2="1685" y2="718" stroke="#7a5534" stroke-width="4" />
          </g>

          <!-- LEFT: BAMBOO DAYBED (Chõng tre) WITH GIRL LYING DOWN -->
          <g id="daybed-group">
            <rect x="90" y="600" width="28" height="180" rx="4" fill="#3a2717" stroke="#120a05" stroke-width="7" />
            <rect x="710" y="600" width="28" height="180" rx="4" fill="#3a2717" stroke="#120a05" stroke-width="7" />
            <rect x="40" y="520" width="740" height="90" rx="8" fill="#8c6c42" stroke="#120a05" stroke-width="9" />
            <g stroke="#5c4324" stroke-width="4">
              <line x1="100" y1="525" x2="100" y2="605" />
              <line x1="160" y1="525" x2="160" y2="605" />
              <line x1="220" y1="525" x2="220" y2="605" />
              <line x1="280" y1="525" x2="280" y2="605" />
              <line x1="340" y1="525" x2="340" y2="605" />
              <line x1="400" y1="525" x2="400" y2="605" />
              <line x1="460" y1="525" x2="460" y2="605" />
              <line x1="520" y1="525" x2="520" y2="605" />
              <line x1="580" y1="525" x2="580" y2="605" />
              <line x1="640" y1="525" x2="640" y2="605" />
              <line x1="700" y1="525" x2="700" y2="605" />
            </g>

            <!-- Girl Lying Down (Bé gái nằm trên chõng tre) -->
            <g id="girl-sleeping" style="transform-origin: 480px 520px;">
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
          <g id="grandma-group">
            <ellipse cx="1275" cy="650" rx="65" ry="32" fill="#24170d" stroke="#120a05" stroke-width="7" />
            <ellipse cx="1245" cy="710" rx="22" ry="12" fill="#120a05" />
            <ellipse cx="1305" cy="710" rx="22" ry="12" fill="#120a05" />

            <path d="M 1215 440 Q 1275 430 1335 440 L 1350 620 L 1200 620 Z" fill="#4a3424" stroke="#120a05" stroke-width="8" stroke-linejoin="round" />
            
            <path d="M 1215 450 Q 1180 515 1205 575" stroke="#4a3424" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="1205" cy="585" r="16" fill="#ba8c63" stroke="#120a05" stroke-width="5" />

            <!-- Head & Face -->
            <g id="grandma-head" style="transform-origin: 1275px 400px;">
              <circle cx="1195" cy="350" r="14" fill="#ba8c63" stroke="#120a05" stroke-width="6" />
              <circle cx="1355" cy="350" r="14" fill="#ba8c63" stroke="#120a05" stroke-width="6" />
              <ellipse cx="1275" cy="355" rx="75" ry="72" fill="#ba8c63" stroke="#120a05" stroke-width="8" />
              
              <circle cx="1275" cy="245" r="32" fill="#eae5dc" stroke="#120a05" stroke-width="8" />
              <path d="M 1200 340 C 1195 260 1230 250 1275 250 C 1320 250 1355 260 1350 340 C 1335 305 1310 290 1275 290 C 1240 290 1215 305 1200 340 Z" fill="#eae5dc" stroke="#120a05" stroke-width="8" />

              <path d="M 1228 322 Q 1244 314 1260 322" stroke="#63574c" stroke-width="5" fill="none" stroke-linecap="round" />
              <path d="M 1290 322 Q 1306 314 1322 322" stroke="#63574c" stroke-width="5" fill="none" stroke-linecap="round" />

              <!-- Left Eye -->
              <g id="grandma-eye-left">
                <circle cx="1245" cy="355" r="19" fill="#ffffff" stroke="#120a05" stroke-width="5" />
                <circle class="pupil-left" cx="1245" cy="355" r="9" fill="#120a05" />
                <circle cx="1248" cy="352" r="3.5" fill="#ffffff" />
                <rect id="grandma-blink-left" x="1224" y="334" width="42" height="42" fill="#ba8c63" stroke="#120a05" stroke-width="5" style="transform-origin: 1245px 335px;" />
              </g>

              <!-- Right Eye -->
              <g id="grandma-eye-right">
                <circle cx="1305" cy="355" r="19" fill="#ffffff" stroke="#120a05" stroke-width="5" />
                <circle class="pupil-right" cx="1305" cy="355" r="9" fill="#120a05" />
                <circle cx="1308" cy="352" r="3.5" fill="#ffffff" />
                <rect id="grandma-blink-right" x="1284" y="334" width="42" height="42" fill="#ba8c63" stroke="#120a05" stroke-width="5" style="transform-origin: 1305px 335px;" />
              </g>

              <path id="grandma-mouth" d="M 1262 396 Q 1275 408 1288 396" stroke="#120a05" stroke-width="5" fill="none" stroke-linecap="round" />
              <path d="M 1234 378 Q 1245 385 1256 378" stroke="#8a6140" stroke-width="3" fill="none" stroke-linecap="round" />
              <path d="M 1294 378 Q 1305 385 1316 378" stroke="#8a6140" stroke-width="3" fill="none" stroke-linecap="round" />
            </g>

            <!-- Mortar on Floor -->
            <g id="betel-mortar">
              <path d="M 1370 660 L 1380 720 Q 1425 735 1470 720 L 1480 660 Z" fill="url(#bronze)" stroke="#120a05" stroke-width="7" />
              <ellipse cx="1425" cy="660" rx="55" ry="16" fill="#523916" stroke="#120a05" stroke-width="6" />
              <ellipse cx="1425" cy="722" rx="42" ry="10" fill="#3b270c" stroke="#120a05" stroke-width="5" />
            </g>

            <!-- Animated Right Arm Pounding Pestle -->
            <g id="pounding-arm-group" style="transform-origin: 1330px 460px;">
              <path d="M 1330 455 Q 1385 520 1375 565" stroke="#4a3424" stroke-width="36" fill="none" stroke-linecap="round" />
              <circle cx="1375" cy="570" r="18" fill="#ba8c63" stroke="#120a05" stroke-width="6" />
              <rect x="1366" y="525" width="20" height="150" rx="9" fill="url(#bronze)" stroke="#120a05" stroke-width="6" transform="rotate(-6 1375 570)" />
            </g>
          </g>
        </svg>

        <!-- Subtitle 1 -->
        <div class="caption-track">
          <div class="caption-box">Chiều nào bà cũng ngồi ở bậc cửa, giã trầu trong cái cối đồng bé bằng nắm tay.</div>
        </div>
      </div>


      <!-- SCENE 2: Family around Campfire (7.5s - 16.0s) -->
      <div id="scene2" class="clip scene-container" data-start="7.5" data-duration="8.5" data-track-index="0" data-layout-allow-overflow>
        <svg viewBox="0 0 1920 1080" xmlns="http://www.w3.org/2000/svg" data-layout-allow-overflow>
          <defs>
            <radialGradient id="fire-glow-light" cx="50%" cy="75%" r="65%">
              <stop offset="0%" stop-color="#ff9900" stop-opacity="0.45" />
              <stop offset="35%" stop-color="#ff5500" stop-opacity="0.25" />
              <stop offset="70%" stop-color="#3a1c0b" stop-opacity="0.1" />
              <stop offset="100%" stop-color="#120c08" stop-opacity="0" />
            </radialGradient>
            <linearGradient id="flame-outer-grad" x1="0%" y1="100%" x2="0%" y2="0%">
              <stop offset="0%" stop-color="#d00000" />
              <stop offset="60%" stop-color="#f48c06" />
              <stop offset="100%" stop-color="#faa307" stop-opacity="0.8" />
            </linearGradient>
            <linearGradient id="flame-mid-grad" x1="0%" y1="100%" x2="0%" y2="0%">
              <stop offset="0%" stop-color="#ffba08" />
              <stop offset="70%" stop-color="#ffe49e" />
              <stop offset="100%" stop-color="#ffffff" />
            </linearGradient>
          </defs>

          <!-- Wooden Plank Hut Interior Background -->
          <rect width="1920" height="1080" fill="#241a13" />

          <!-- Wooden Wall Slat Lines -->
          <g stroke="#160f0a" stroke-width="6">
            <line x1="0" y1="180" x2="1920" y2="180" />
            <line x1="0" y1="360" x2="1920" y2="360" />
            <line x1="0" y1="540" x2="1920" y2="540" />
            <line x1="0" y1="720" x2="1920" y2="720" stroke-width="10" />
            <rect x="260" y="0" width="36" height="1080" fill="#1b120c" />
            <rect x="1624" y="0" width="36" height="1080" fill="#1b120c" />
          </g>

          <!-- Center Maroon Curtain (Rèm đỏ) -->
          <rect x="740" y="50" width="440" height="490" fill="#581617" stroke="#160f0a" stroke-width="10" />
          <line x1="960" y1="50" x2="960" y2="540" stroke="#160f0a" stroke-width="8" />

          <!-- EERIE GHOSTLY SHADOW (Appears at climax in background) -->
          <g id="ghost-shadow" opacity="0" style="transform-origin: 960px 240px;">
            <path d="M 920 280 C 910 160 1010 160 1000 280 C 1030 380 890 380 920 280 Z" fill="#080504" />
            <circle cx="945" cy="225" r="5" fill="#ffffff" />
            <circle cx="975" cy="225" r="5" fill="#ffffff" />
          </g>

          <!-- Floor -->
          <rect x="0" y="720" width="1920" height="360" fill="#19110a" />

          <!-- DYNAMIC FIRE GLOW OVERLAY -->
          <rect id="fire-ambient-light" x="200" y="200" width="1520" height="880" fill="url(#fire-glow-light)" pointer-events="none" />

          <!-- ================= 3 CHARACTERS SITTING AROUND FIRE ================= -->
          
          <!-- 1. LEFT: THE MOTHER (Người Mẹ) -->
          <g id="mother-char" style="transform-origin: 580px 720px;">
            <ellipse cx="580" cy="740" rx="80" ry="40" fill="#201711" stroke="#120a05" stroke-width="7" />
            <ellipse cx="530" cy="775" rx="20" ry="12" fill="#120a05" />
            <ellipse cx="610" cy="775" rx="20" ry="12" fill="#120a05" />

            <path d="M 515 540 Q 580 525 645 540 L 660 720 L 500 720 Z" fill="#eae6dc" stroke="#120a05" stroke-width="8" stroke-linejoin="round" />
            <path d="M 520 550 Q 485 620 520 680" stroke="#eae6dc" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="520" cy="690" r="16" fill="#ba8c63" stroke="#120a05" stroke-width="5" />
            <path d="M 640 550 Q 675 620 640 680" stroke="#eae6dc" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="640" cy="690" r="16" fill="#ba8c63" stroke="#120a05" stroke-width="5" />

            <g id="mother-head" style="transform-origin: 580px 480px;">
              <path d="M 500 480 C 490 380 670 380 660 480 L 675 620 C 670 650 630 650 625 610 L 620 500 L 540 500 L 535 610 C 530 650 490 650 485 620 Z" fill="#18120d" stroke="#120a05" stroke-width="8" stroke-linejoin="round" />
              <ellipse cx="580" cy="460" rx="72" ry="70" fill="#ba8c63" stroke="#120a05" stroke-width="8" />
              <path d="M 515 440 C 520 390 560 395 580 435 C 600 395 640 390 645 440 C 630 420 600 415 580 425 C 560 415 530 420 515 440 Z" fill="#18120d" stroke="#120a05" stroke-width="6" />

              <path d="M 538 430 Q 552 422 566 430" stroke="#18120d" stroke-width="5" fill="none" stroke-linecap="round" />
              <path d="M 594 430 Q 608 422 622 430" stroke="#18120d" stroke-width="5" fill="none" stroke-linecap="round" />

              <circle cx="552" cy="460" r="18" fill="#ffffff" stroke="#120a05" stroke-width="5" />
              <circle class="mother-pupil" cx="557" cy="460" r="8.5" fill="#120a05" />
              <circle cx="559" cy="457" r="3" fill="#ffffff" />
              <rect id="mother-blink-left" x="532" y="440" width="40" height="40" fill="#ba8c63" stroke="#120a05" stroke-width="5" style="transform-origin: 552px 440px;" />

              <circle cx="608" cy="460" r="18" fill="#ffffff" stroke="#120a05" stroke-width="5" />
              <circle class="mother-pupil" cx="613" cy="460" r="8.5" fill="#120a05" />
              <circle cx="615" cy="457" r="3" fill="#ffffff" />
              <rect id="mother-blink-right" x="588" y="440" width="40" height="40" fill="#ba8c63" stroke="#120a05" stroke-width="5" style="transform-origin: 608px 440px;" />

              <path d="M 570 496 Q 580 504 590 496" stroke="#120a05" stroke-width="4.5" fill="none" stroke-linecap="round" />
            </g>
          </g>


          <!-- 2. RIGHT: THE FATHER (Người Bố đeo kính tròn) -->
          <g id="father-char" style="transform-origin: 1340px 720px;">
            <ellipse cx="1340" cy="740" rx="80" ry="40" fill="#201711" stroke="#120a05" stroke-width="7" />
            <ellipse cx="1290" cy="775" rx="20" ry="12" fill="#120a05" />
            <ellipse cx="1370" cy="775" rx="20" ry="12" fill="#120a05" />

            <path d="M 1275 540 Q 1340 525 1405 540 L 1420 720 L 1260 720 Z" fill="#5c3c26" stroke="#120a05" stroke-width="8" stroke-linejoin="round" />
            <path d="M 1280 550 Q 1245 620 1280 680" stroke="#5c3c26" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="1280" cy="690" r="16" fill="#ba8c63" stroke="#120a05" stroke-width="5" />
            <path d="M 1400 550 Q 1435 620 1400 680" stroke="#5c3c26" stroke-width="36" fill="none" stroke-linecap="round" />
            <circle cx="1400" cy="690" r="16" fill="#ba8c63" stroke="#120a05" stroke-width="5" />

            <g id="father-head" style="transform-origin: 1340px 480px;">
              <path d="M 1260 450 C 1255 375 1425 375 1420 450 C 1410 410 1370 400 1340 400 C 1310 400 1270 410 1260 450 Z" fill="#18120d" stroke="#120a05" stroke-width="8" stroke-linejoin="round" />
              <ellipse cx="1340" cy="460" rx="72" ry="70" fill="#ba8c63" stroke="#120a05" stroke-width="8" />

              <path d="M 1298 428 Q 1312 420 1326 428" stroke="#18120d" stroke-width="5" fill="none" stroke-linecap="round" />
              <path d="M 1354 428 Q 1368 420 1382 428" stroke="#18120d" stroke-width="5" fill="none" stroke-linecap="round" />

              <circle cx="1312" cy="460" r="23" fill="none" stroke="#120a05" stroke-width="6" />
              <circle cx="1312" cy="460" r="17" fill="#ffffff" />
              <circle class="father-pupil" cx="1312" cy="460" r="8" fill="#120a05" />
              <circle cx="1314" cy="457" r="3" fill="#ffffff" />
              <rect id="father-blink-left" x="1292" y="440" width="40" height="40" fill="#ba8c63" stroke="#120a05" stroke-width="4" style="transform-origin: 1312px 440px;" />

              <circle cx="1368" cy="460" r="23" fill="none" stroke="#120a05" stroke-width="6" />
              <circle cx="1368" cy="460" r="17" fill="#ffffff" />
              <circle class="father-pupil" cx="1368" cy="460" r="8" fill="#120a05" />
              <circle cx="1370" cy="457" r="3" fill="#ffffff" />
              <rect id="father-blink-right" x="1348" y="440" width="40" height="40" fill="#ba8c63" stroke="#120a05" stroke-width="4" style="transform-origin: 1368px 440px;" />
              
              <line x1="1335" y1="460" x2="1345" y2="460" stroke="#120a05" stroke-width="6" />
              <path d="M 1330 498 Q 1340 505 1350 498" stroke="#120a05" stroke-width="4.5" fill="none" stroke-linecap="round" />
            </g>
          </g>


          <!-- 3. CENTER: THE BOY (Bé trai ngồi sau đống lửa) -->
          <g id="boy-char" style="transform-origin: 960px 720px;">
            <path d="M 910 590 Q 960 580 1010 590 L 1020 730 L 900 730 Z" fill="#908a96" stroke="#120a05" stroke-width="7" stroke-linejoin="round" />
            
            <g id="boy-head" style="transform-origin: 960px 530px;">
              <path d="M 900 520 C 895 445 1025 445 1020 520 C 1005 480 985 470 960 470 C 935 470 915 480 900 520 Z" fill="#18120d" stroke="#120a05" stroke-width="7" stroke-linejoin="round" />
              <ellipse cx="960" cy="530" rx="60" ry="58" fill="#c99e77" stroke="#120a05" stroke-width="7" />

              <path d="M 926 502 Q 938 495 950 502" stroke="#18120d" stroke-width="4.5" fill="none" stroke-linecap="round" />
              <path d="M 970 502 Q 982 495 994 502" stroke="#18120d" stroke-width="4.5" fill="none" stroke-linecap="round" />

              <circle cx="940" cy="530" r="16" fill="#ffffff" stroke="#120a05" stroke-width="4.5" />
              <circle id="boy-pupil-left" cx="940" cy="530" r="7.5" fill="#120a05" />
              <circle cx="942" cy="527" r="2.5" fill="#ffffff" />
              <rect id="boy-blink-left" x="922" y="514" width="36" height="36" fill="#c99e77" stroke="#120a05" stroke-width="4" style="transform-origin: 940px 514px;" />

              <circle cx="980" cy="530" r="16" fill="#ffffff" stroke="#120a05" stroke-width="4.5" />
              <circle id="boy-pupil-right" cx="980" cy="530" r="7.5" fill="#120a05" />
              <circle cx="982" cy="527" r="2.5" fill="#ffffff" />
              <rect id="boy-blink-right" x="962" y="514" width="36" height="36" fill="#c99e77" stroke="#120a05" stroke-width="4" style="transform-origin: 980px 514px;" />

              <path id="boy-mouth" d="M 952 562 Q 960 568 968 562" stroke="#120a05" stroke-width="4" fill="none" stroke-linecap="round" />
            </g>
          </g>


          <!-- ================= CENTER CAMPFIRE (Bếp Lửa) ================= -->
          <g id="campfire-group" style="transform-origin: 960px 790px;">
            <g stroke="#140d07" stroke-width="5">
              <ellipse cx="890" cy="800" rx="24" ry="14" fill="#695e52" />
              <ellipse cx="925" cy="815" rx="26" ry="15" fill="#52483d" />
              <ellipse cx="965" cy="820" rx="30" ry="16" fill="#756b5f" />
              <ellipse cx="1005" cy="812" rx="26" ry="15" fill="#5a5045" />
              <ellipse cx="1035" cy="795" rx="24" ry="14" fill="#6b6054" />
              <ellipse cx="920" cy="780" rx="22" ry="12" fill="#443b31" />
              <ellipse cx="960" cy="775" rx="25" ry="13" fill="#383027" />
              <ellipse cx="1000" cy="780" rx="22" ry="12" fill="#443b31" />
            </g>

            <g stroke="#140d07" stroke-width="5">
              <rect x="910" y="785" width="105" height="18" rx="6" fill="#3b2413" transform="rotate(-18 960 790)" />
              <rect x="910" y="785" width="105" height="18" rx="6" fill="#4a2e19" transform="rotate(22 960 790)" />
            </g>

            <g id="flames">
              <path id="flame-outer" d="M 930 790 C 905 730 920 660 960 620 C 1000 660 1015 730 990 790 Z" fill="url(#flame-outer-grad)" opacity="0.9" style="transform-origin: 960px 790px;" />
              <path id="flame-mid" d="M 940 790 C 925 745 935 690 960 655 C 985 690 995 745 980 790 Z" fill="url(#flame-mid-grad)" opacity="0.95" style="transform-origin: 960px 790px;" />
              <ellipse id="flame-core" cx="960" cy="765" rx="22" ry="32" fill="#ffffff" opacity="0.85" style="transform-origin: 960px 765px;" />
            </g>
          </g>
        </svg>

        <!-- Subtitle 2 -->
        <div class="caption-track">
          <div class="caption-box">Đến đêm, cả nhà lại quây quần bên bếp lửa. Nhưng câu chuyện bà kể đêm nay... lại khiến ai nấy đều lạnh gáy.</div>
        </div>
      </div>

      <!-- Vignette Overlay -->
      <div class="vignette"></div>
    </div>

    <!-- GSAP Master Animation Timeline -->
    <script>
      const tl = gsap.timeline({ paused: true });

      // Initialize all blinking eyelid scales to 0
      gsap.set(["#grandma-blink-left", "#grandma-blink-right", "#mother-blink-left", "#mother-blink-right", "#father-blink-left", "#father-blink-right", "#boy-blink-left", "#boy-blink-right"], { scaleY: 0 });

      // ----------------- SCENE 1 ANIMATIONS (0.0s - 7.5s) -----------------
      // Girl sleeping gentle breathing
      tl.to("#girl-sleeping", {
        scaleY: 1.04,
        y: -3,
        duration: 1.8,
        repeat: 3,
        yoyo: true,
        ease: "sine.inOut"
      }, 0);

      // Grandma pounding betel pestle (cốc... cốc...)
      for (let t = 0.2; t < 6.8; t += 0.65) {
        tl.to("#pounding-arm-group", {
          y: -42,
          rotation: -8,
          duration: 0.32,
          ease: "power1.out"
        }, t);
        tl.to("#pounding-arm-group", {
          y: 0,
          rotation: 0,
          duration: 0.22,
          ease: "power2.in"
        }, t + 0.32);
      }

      // Grandma gentle head nod & breathing
      tl.to("#grandma-head", {
        y: 4,
        rotation: 1.5,
        duration: 1.6,
        repeat: 3,
        yoyo: true,
        ease: "sine.inOut"
      }, 0.2);

      // Grandma eye blinks
      [1.4, 3.8, 5.6].forEach(time => {
        tl.to(["#grandma-blink-left", "#grandma-blink-right"], {
          scaleY: 1,
          duration: 0.08,
          ease: "power1.in"
        }, time);
        tl.to(["#grandma-blink-left", "#grandma-blink-right"], {
          scaleY: 0,
          duration: 0.08,
          ease: "power1.out"
        }, time + 0.08);
      });

      // Grandma mouth flap when speaking (0.4s to 6.2s)
      for (let t = 0.5; t < 5.8; t += 0.26) {
        tl.to("#grandma-mouth", {
          attr: { d: "M 1260 396 Q 1275 418 1290 396" },
          duration: 0.12,
          ease: "sine.inOut"
        }, t);
        tl.to("#grandma-mouth", {
          attr: { d: "M 1262 396 Q 1275 404 1288 396" },
          duration: 0.12,
          ease: "sine.inOut"
        }, t + 0.12);
      }

      // ----------------- SCENE 2 ANIMATIONS (7.5s - 16.0s) -----------------
      // Campfire flame flickering (dynamic organic morphing)
      for (let t = 7.5; t < 16.0; t += 0.2) {
        const sX = 0.92 + Math.sin(t * 14) * 0.12;
        const sY = 0.9 + Math.cos(t * 11) * 0.15;
        const skew = Math.sin(t * 9) * 6;
        tl.to("#flame-outer", {
          scaleX: sX,
          scaleY: sY,
          skewX: skew,
          duration: 0.2,
          ease: "sine.inOut"
        }, t);
        tl.to("#flame-mid", {
          scaleX: 1 / sX,
          scaleY: sY * 1.05,
          duration: 0.2,
          ease: "sine.inOut"
        }, t);
        tl.to("#fire-ambient-light", {
          opacity: 0.75 + Math.sin(t * 17) * 0.25,
          duration: 0.2,
          ease: "sine.inOut"
        }, t);
      }

      // Mother, Boy, Father gentle idle breathing
      tl.to(["#mother-char", "#father-char", "#boy-char"], {
        y: -4,
        duration: 1.6,
        repeat: 4,
        yoyo: true,
        ease: "sine.inOut"
      }, 7.5);

      // Boy eye blinking
      [8.6, 11.2, 13.8].forEach(time => {
        tl.to(["#boy-blink-left", "#boy-blink-right"], {
          scaleY: 1,
          duration: 0.08,
          ease: "power1.in"
        }, time);
        tl.to(["#boy-blink-left", "#boy-blink-right"], {
          scaleY: 0,
          duration: 0.08,
          ease: "power1.out"
        }, time + 0.08);
      });

      // Mother eye blinking
      [9.2, 12.4].forEach(time => {
        tl.to(["#mother-blink-left", "#mother-blink-right"], {
          scaleY: 1,
          duration: 0.08,
          ease: "power1.in"
        }, time);
        tl.to(["#mother-blink-left", "#mother-blink-right"], {
          scaleY: 0,
          duration: 0.08,
          ease: "power1.out"
        }, time + 0.08);
      });

      // Father eye blinking
      [9.8, 13.0].forEach(time => {
        tl.to(["#father-blink-left", "#father-blink-right"], {
          scaleY: 1,
          duration: 0.08,
          ease: "power1.in"
        }, time);
        tl.to(["#father-blink-left", "#father-blink-right"], {
          scaleY: 0,
          duration: 0.08,
          ease: "power1.out"
        }, time + 0.08);
      });

      // SPOOKY HORROR CLIMAX (12.0s - 15.5s)
      tl.to("#fire-ambient-light", { opacity: 0.35, duration: 1.2, ease: "power2.in" }, 12.0);
      tl.to("#ghost-shadow", { opacity: 0.9, y: -20, duration: 1.8, ease: "power2.out" }, 12.2);
      tl.to("#boy-head", { rotation: -4, y: -6, duration: 0.6, ease: "power1.out" }, 12.6);
      tl.to(["#boy-pupil-left", "#boy-pupil-right"], { attr: { r: 5 }, duration: 0.4 }, 12.8);
      tl.to("#boy-mouth", { attr: { d: "M 952 566 Q 960 558 968 566" }, duration: 0.4 }, 12.8);

      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
'''

with open('projects/than-trung-chiec-khan-tang-thu-32/preview_2d/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Updated preview_2d/index.html successfully!")
