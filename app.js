/**
 * app.js - 閻姿桂文字史奴比高精度動力學藝術引擎
 * 支援從散落到組合成圖案的緩慢演進動畫 (Slow Progressive Evolution Animation)
 */

(function () {
  'use strict';

  const CONFIG = {
    totalParticles: 480, // Strictly 160 閻, 160 姿, 160 桂
    baseEvolutionDuration: 4500, // 4.5 seconds for 1.0x slow evolution
    springK: 0.12,
    friction: 0.84,
    repelRadius: 130,
    repelForce: 24,
    themes: ['classic', 'midnight', 'risograph', 'imperial'],
    themeNames: {
      classic: '經典花生報紙',
      midnight: '賽博深空霓虹',
      risograph: '日系雙色孔版',
      imperial: '宮廷金箔水墨'
    }
  };

  // State
  let canvas, ctx;
  let width = 0, height = 0, dpr = 1;
  let scaleFactor = 1;
  let currentPoseIndex = 0;
  let particles = [];
  let isBrushMode = false;
  let isAutoPlaying = false;
  let autoPlayTimer = null;
  let currentTheme = 'classic';
  let brushParticles = [];

  // Evolution Animation State
  let evolutionProgress = 1.0; // 0.0 to 1.0
  let isEvolutionPlaying = true;
  let evolutionSpeed = 1.0; // 0.5x, 1.0x, 2.0x
  let lastFrameTime = performance.now();

  // Mobile Device Tilt
  let tiltX = 0, tiltY = 0;

  // Pointer & Gesture
  const pointer = {
    x: -9999,
    y: -9999,
    isDown: false,
    startX: 0,
    startY: 0,
    startTime: 0,
    lastTapTime: 0
  };

  // DOM Elements
  let artworkBadge, artworkTitle, artworkQuote;
  let evolutionStatus, evolutionScrubber, btnEvoPlay, evoPlayIcon, btnEvoReplay;
  let speedPillButtons = [];
  let poseNavRibbon, btnAutoPlay, playRingCircle, playIcon, playBtnText;
  let btnScatter, scatterText, btnExport, btnTheme, btnSound, btnBrush;
  let exportModal, exportPreviewImg, modalCloseBtn, modalDownloadBtn;

  // Particle Class
  class Particle {
    constructor(idx, char) {
      this.idx = idx;
      this.char = char; // '閻' or '姿' or '桂'
      this.x = 0;
      this.y = 0;
      this.vx = 0;
      this.vy = 0;

      // Evolution origins & targets
      this.originX = 0;
      this.originY = 0;
      this.originRot = 0;
      this.swirlDist = 0;
      this.swirlAng = 0;

      this.tx = 0;
      this.ty = 0;
      this.role = 'outline';
      this.baseColor = '#0f172a';
      this.size = 15;

      this.rot = 0;
      this.vRot = 0;
      this.scale = 1.0;
      this.stagger = 0; // Delay ratio in [0, 0.45]
      this.idleSeed = Math.random() * 100;
      this.hasArrived = false;
    }

    randomizeScatter(width, height) {
      const cx = width / 2;
      const cy = height / 2;
      // Scatter broadly across viewport with beautiful celestial distribution
      const angle = (this.idx / CONFIG.totalParticles) * Math.PI * 2 * 3.5 + Math.random() * 0.5;
      const dist = Math.min(width, height) * (0.35 + Math.random() * 0.7);
      this.originX = cx + Math.cos(angle) * dist;
      this.originY = cy + Math.sin(angle) * dist;
      this.originRot = (Math.random() - 0.5) * Math.PI * 2.5;

      // Swirl arc parameters
      this.swirlDist = (Math.random() - 0.5) * 160;
      this.swirlAng = angle + Math.PI / 2;

      this.x = this.originX;
      this.y = this.originY;
      this.rot = this.originRot;
      this.vx = (Math.random() - 0.5) * 4;
      this.vy = (Math.random() - 0.5) * 4;
      this.hasArrived = false;
    }

    setTarget(tx, ty, role, color, size, randomizeOrigin = false) {
      this.tx = tx;
      this.ty = ty;
      this.role = role;
      this.baseColor = color;
      this.size = size;

      // Compute staggered arrival delay
      // Head & core body arrive first (stagger 0.0 ~ 0.15)
      // Features (nose, eye, ear, collar, spot) arrive middle (0.15 ~ 0.28)
      // External props (roof, scarf, Woodstock, heart, club, clouds) arrive last (0.28 ~ 0.42)
      if (role === 'head' || role === 'body' || role === 'back' || role === 'outline') {
        this.stagger = (this.idx % 60) / 60 * 0.15;
      } else if (role === 'ear' || role === 'nose' || role === 'eye' || role === 'collar' || role === 'spot' || role === 'sunglasses') {
        this.stagger = 0.14 + (this.idx % 50) / 50 * 0.14;
      } else {
        this.stagger = 0.26 + (this.idx % 70) / 70 * 0.16;
      }

      if (randomizeOrigin) {
        this.randomizeScatter(width, height);
      }
    }

    update(time, evolutionT) {
      // Individual progress [0, 1] based on stagger
      const localT = Math.max(0, Math.min(1, (evolutionT - this.stagger) / (1 - this.stagger)));

      // Cubic ease-out curve for gentle, graceful arrival
      const ease = localT < 1 ? 1 - Math.pow(1 - localT, 3) : 1;

      // Curved arc trajectory from origin to target
      const arcDisplacement = Math.sin(localT * Math.PI) * this.swirlDist;
      const pathX = this.originX + (this.tx - this.originX) * ease + Math.cos(this.swirlAng) * arcDisplacement;
      const pathY = this.originY + (this.ty - this.originY) * ease + Math.sin(this.swirlAng) * arcDisplacement;

      // Add gentle mobile device tilt
      let destX = pathX + tiltX * 25 * ease;
      let destY = pathY + tiltY * 25 * ease;

      // Subtle breathing motion when settled
      if (localT >= 0.99) {
        destY += Math.sin(time * 0.0028 + this.idleSeed) * 1.5;
        if (!this.hasArrived) {
          this.hasArrived = true;
          this.scale = 1.35; // tiny elastic pulse
        }
      } else {
        this.hasArrived = false;
      }

      // Spring physics towards current trajectory waypoint
      const ax = (destX - this.x) * CONFIG.springK;
      const ay = (destY - this.y) * CONFIG.springK;

      this.vx = (this.vx + ax) * CONFIG.friction;
      this.vy = (this.vy + ay) * CONFIG.friction;

      // Pointer wind / touch repulsion
      if (pointer.isDown || pointer.x > 0) {
        const pdx = this.x - pointer.x;
        const pdy = this.y - pointer.y;
        const pdist = Math.hypot(pdx, pdy);

        if (pdist < CONFIG.repelRadius && pdist > 0) {
          const force = (1 - pdist / CONFIG.repelRadius) * CONFIG.repelForce;
          this.vx += (pdx / pdist) * force;
          this.vy += (pdy / pdist) * force;
          this.vRot += (Math.random() - 0.5) * 0.15;
          this.scale = 1.3;
        }
      }

      this.x += this.vx;
      this.y += this.vy;

      // Target rotation eases to 0 as ease -> 1
      const targetRot = this.originRot * (1 - ease);
      this.rot += (targetRot - this.rot) * 0.1 + this.vRot;
      this.vRot *= 0.9;

      // Scale recovery
      this.scale += (1.0 - this.scale) * 0.12;

      // Alpha: starts soft, becomes solid
      this.alpha = 0.35 + 0.65 * ease;
    }

    render(ctx, theme) {
      ctx.save();
      ctx.globalAlpha = Math.max(0, Math.min(1, this.alpha));
      ctx.translate(this.x, this.y);
      ctx.rotate(this.rot);
      ctx.scale(this.scale, this.scale);

      const finalColor = getThemedColor(this.role, this.baseColor, theme);
      const fontSize = Math.round(this.size * scaleFactor);

      ctx.font = `800 ${fontSize}px "Microsoft JhengHei", "PingFang TC", sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      if (theme === 'midnight') {
        ctx.shadowColor = finalColor;
        ctx.shadowBlur = (this.role === 'nose' || this.role === 'sunglasses') ? 4 : 10;
      } else if (theme === 'risograph') {
        ctx.fillStyle = finalColor;
        ctx.globalAlpha = 0.9;
      } else if (theme === 'imperial') {
        if (this.role.includes('roof') || this.role.includes('scarf') || this.role.includes('heart') || this.role === 'collar') {
          ctx.shadowColor = 'rgba(185, 28, 28, 0.4)';
          ctx.shadowBlur = 5;
        }
      }

      if (this.baseColor === '#ffffff' && (theme === 'classic' || theme === 'risograph' || theme === 'imperial')) {
        ctx.fillStyle = theme === 'risograph' ? '#fde047' : '#e2e8f0';
        ctx.fillText(this.char, 0, 0);
        ctx.lineWidth = 1;
        ctx.strokeStyle = '#94a3b8';
        ctx.strokeText(this.char, 0, 0);
      } else {
        ctx.fillStyle = finalColor;
        ctx.fillText(this.char, 0, 0);
      }

      ctx.restore();
    }
  }

  // Brush particle for calligraphy wand mode
  class BrushParticle {
    constructor(x, y, char, color) {
      this.x = x;
      this.y = y;
      this.char = char;
      this.color = color;
      this.vx = (Math.random() - 0.5) * 2;
      this.vy = -Math.random() * 2 - 1;
      this.rot = (Math.random() - 0.5) * 0.5;
      this.vRot = (Math.random() - 0.5) * 0.05;
      this.alpha = 1.0;
      this.size = Math.random() * 12 + 14;
    }
    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.vy += 0.08;
      this.rot += this.vRot;
      this.alpha -= 0.015;
    }
    render(ctx) {
      if (this.alpha <= 0) return;
      ctx.save();
      ctx.globalAlpha = Math.max(0, this.alpha);
      ctx.translate(this.x, this.y);
      ctx.rotate(this.rot);
      ctx.font = `800 ${this.size * scaleFactor}px "Microsoft JhengHei", sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = this.color;
      ctx.fillText(this.char, 0, 0);
      ctx.restore();
    }
  }

  // Theme color mapping
  function getThemedColor(role, baseColor, theme) {
    if (theme === 'classic') return baseColor;

    if (theme === 'midnight') {
      if (role === 'nose' || role === 'sunglasses') return '#38bdf8';
      if (role === 'ear') return '#818cf8';
      if (role.includes('roof') || role.includes('scarf') || role.includes('heart') || role === 'sweater' || role === 'collar') return '#f43f5e';
      if (role.includes('woodstock') || role === 'sparkle') return '#facc15';
      if (role.includes('cloud') || role === 'zzz' || role === 'trail') return '#06b6d4';
      if (role === 'grass') return '#10b981';
      return '#f8fafc';
    }

    if (theme === 'risograph') {
      if (role.includes('roof') || role.includes('scarf') || role.includes('heart') || role === 'sweater' || role === 'collar') return '#ff2a6d';
      if (role.includes('woodstock') || role === 'sparkle' || role === 'ball') return '#ffbe0b';
      if (role.includes('cloud') || role === 'zzz') return '#3a86ff';
      if (role === 'grass') return '#06d6a0';
      return '#051937';
    }

    if (theme === 'imperial') {
      if (role.includes('roof') || role.includes('scarf') || role.includes('heart') || role === 'sweater' || role === 'collar') return '#b91c1c';
      if (role.includes('woodstock') || role === 'sparkle' || role === 'ball') return '#d4af37';
      if (role.includes('cloud') || role === 'zzz') return '#a8a29e';
      if (role === 'grass') return '#047857';
      return '#1c1917';
    }

    return baseColor;
  }

  // Init Particles
  function initParticles() {
    particles = [];
    const CHARS = ['閻', '姿', '桂'];
    for (let i = 0; i < CONFIG.totalParticles; i++) {
      const char = CHARS[i % 3];
      particles.push(new Particle(i, char));
    }
  }

  // Apply Pose and trigger Slow Progressive Evolution
  function applyPose(poseIdx, startFromScatter = true, triggerSound = true) {
    if (!window.SNOOPY_POSES || !window.SNOOPY_POSES[poseIdx]) return;
    currentPoseIndex = poseIdx;
    const pose = window.SNOOPY_POSES[poseIdx];

    const cx = width / 2;
    // Perfectly centered in the unobstructed canvas between top header and bottom dock
    const cy = (height - 135 + 70) / 2;
    const pts = pose.particles || pose.points;

    pts.forEach((item, i) => {
      if (particles[i]) {
        const tx = cx + item.x * scaleFactor;
        const ty = cy + item.y * scaleFactor;
        particles[i].setTarget(tx, ty, item.role, item.color, item.size, startFromScatter);
      }
    });

    if (startFromScatter) {
      evolutionProgress = 0.0;
      isEvolutionPlaying = true;
      updateEvolutionUI();
    }

    // Update Meta Display
    if (artworkBadge) artworkBadge.textContent = `ARCHIVE 0${poseIdx + 1} / 0${window.SNOOPY_POSES.length}`;
    if (artworkTitle) artworkTitle.textContent = pose.title;
    if (artworkQuote) artworkQuote.textContent = pose.quote;

    // Update Ribbon
    document.querySelectorAll('.pose-chip').forEach((chip, idx) => {
      chip.classList.toggle('active', idx === poseIdx);
      if (idx === poseIdx) {
        chip.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    });

    if (triggerSound && window.soundEngine) {
      window.soundEngine.playMorphArpeggio();
    }
  }

  // Evolution Controller UI updater
  function updateEvolutionUI() {
    const pct = Math.round(evolutionProgress * 100);
    if (evolutionScrubber) evolutionScrubber.value = pct;
    if (evolutionStatus) {
      if (pct >= 100) {
        evolutionStatus.textContent = '✨ 史奴比完整組裝 100%';
      } else if (pct <= 0) {
        evolutionStatus.textContent = '🌌 散落星雲 0%';
      } else {
        evolutionStatus.textContent = `🌱 緩慢演進組裝中 ${pct}%`;
      }
    }
    if (evoPlayIcon) {
      evoPlayIcon.innerHTML = isEvolutionPlaying
        ? '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>' // Pause
        : '<path d="M8 5v14l11-7z"/>'; // Play
    }
  }

  // Scatter & Reassemble Toggle
  function toggleScatter() {
    if (evolutionProgress >= 0.95) {
      // Scatter to 0
      evolutionProgress = 0.0;
      isEvolutionPlaying = false;
      particles.forEach(p => p.randomizeScatter(width, height));
      updateEvolutionUI();
      if (scatterText) scatterText.textContent = "組裝文字";
      if (window.soundEngine) window.soundEngine.playScatterWhoosh();
    } else {
      // Fast forward to 1.0
      evolutionProgress = 1.0;
      isEvolutionPlaying = false;
      updateEvolutionUI();
      if (scatterText) scatterText.textContent = "散落文字";
      if (window.soundEngine) window.soundEngine.playMagneticSnap();
    }
  }

  // Auto-Play Cycle
  function toggleAutoPlay() {
    isAutoPlaying = !isAutoPlaying;
    btnAutoPlay.classList.toggle('active', isAutoPlaying);
    playBtnText.textContent = isAutoPlaying ? "播映中" : "巡迴播映";
    playIcon.innerHTML = isAutoPlaying
      ? '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>'
      : '<path d="M8 5v14l11-7z"/>';

    if (isAutoPlaying) {
      autoPlayTimer = setInterval(nextPose, 8000); // 8s per pose for complete evolution
    } else {
      clearInterval(autoPlayTimer);
      autoPlayTimer = null;
      if (playRingCircle) playRingCircle.style.strokeDashoffset = '75.4';
    }
  }

  function nextPose() {
    const nextIdx = (currentPoseIndex + 1) % window.SNOOPY_POSES.length;
    applyPose(nextIdx, true, true);
  }

  function prevPose() {
    const prevIdx = (currentPoseIndex - 1 + window.SNOOPY_POSES.length) % window.SNOOPY_POSES.length;
    applyPose(prevIdx, true, true);
  }

  // Theme Cycler
  function cycleTheme() {
    const currIdx = CONFIG.themes.indexOf(currentTheme);
    const nextIdx = (currIdx + 1) % CONFIG.themes.length;
    currentTheme = CONFIG.themes[nextIdx];
    document.documentElement.setAttribute('data-theme', currentTheme);
    if (window.soundEngine) window.soundEngine.playBell(1046.5);
  }

  // Resize Handler
  function handleResize() {
    width = window.innerWidth;
    height = window.innerHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2.5);

    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    ctx.scale(dpr, dpr);

    const availW = Math.max(280, width - 40);
    const availH = Math.max(280, height - 210);
    scaleFactor = Math.min(availW / 530, availH / 530, 1.2);

    if (window.SNOOPY_POSES && window.SNOOPY_POSES[currentPoseIndex]) {
      const cx = width / 2;
      const cy = (height - 135 + 70) / 2;
      const pts = window.SNOOPY_POSES[currentPoseIndex].particles || window.SNOOPY_POSES[currentPoseIndex].points;
      pts.forEach((item, i) => {
        if (particles[i]) {
          particles[i].tx = cx + item.x * scaleFactor;
          particles[i].ty = cy + item.y * scaleFactor;
        }
      });
    }
  }

  // Pointer & Touch Events
  function setupEvents() {
    window.addEventListener('resize', handleResize);

    // Touch & Pointer
    const onPointerDown = (e) => {
      pointer.isDown = true;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      pointer.x = clientX;
      pointer.y = clientY;
      pointer.startX = clientX;
      pointer.startY = clientY;
      pointer.startTime = performance.now();

      const now = performance.now();
      if (now - pointer.lastTapTime < 320) {
        toggleScatter();
        pointer.lastTapTime = 0;
      } else {
        pointer.lastTapTime = now;
      }

      if (isBrushMode) {
        spawnBrushParticle(clientX, clientY);
      } else {
        if (window.soundEngine) window.soundEngine.playPop(1.1);
      }
    };

    const onPointerMove = (e) => {
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      pointer.x = clientX;
      pointer.y = clientY;

      if (pointer.isDown && isBrushMode) {
        spawnBrushParticle(clientX, clientY);
      }
    };

    const onPointerUp = (e) => {
      pointer.isDown = false;
      const dx = pointer.x - pointer.startX;
      const dy = pointer.y - pointer.startY;
      const dt = performance.now() - pointer.startTime;

      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5 && dt < 500) {
        if (dx < 0) nextPose();
        else prevPose();
      }

      setTimeout(() => {
        if (!pointer.isDown) {
          pointer.x = -9999;
          pointer.y = -9999;
        }
      }, 150);
    };

    canvas.addEventListener('mousedown', onPointerDown);
    window.addEventListener('mousemove', onPointerMove);
    window.addEventListener('mouseup', onPointerUp);

    canvas.addEventListener('touchstart', onPointerDown, { passive: true });
    window.addEventListener('touchmove', onPointerMove, { passive: true });
    window.addEventListener('touchend', onPointerUp, { passive: true });

    // Gyroscope Tilt
    if (window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientation', (e) => {
        if (e.gamma !== null && e.beta !== null) {
          tiltX = Math.max(-1, Math.min(1, e.gamma / 35));
          tiltY = Math.max(-1, Math.min(1, (e.beta - 40) / 45));
        }
      }, { passive: true });
    }

    // Evolution Scrubber drag
    if (evolutionScrubber) {
      evolutionScrubber.addEventListener('input', (e) => {
        evolutionProgress = parseFloat(e.target.value) / 100.0;
        isEvolutionPlaying = false;
        updateEvolutionUI();
      });
    }

    // Evolution Play/Pause toggle
    if (btnEvoPlay) {
      btnEvoPlay.addEventListener('click', () => {
        if (evolutionProgress >= 1.0) {
          // Restart from 0
          applyPose(currentPoseIndex, true, true);
        } else {
          isEvolutionPlaying = !isEvolutionPlaying;
          updateEvolutionUI();
        }
      });
    }

    // Evolution Replay from scatter
    if (btnEvoReplay) {
      btnEvoReplay.addEventListener('click', () => {
        applyPose(currentPoseIndex, true, true);
      });
    }

    // Evolution Speed Pills
    speedPillButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        speedPillButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        evolutionSpeed = parseFloat(btn.dataset.speed || 1.0);
        if (window.soundEngine) window.soundEngine.playBell(900 * evolutionSpeed);
      });
    });

    // Toolbar buttons
    btnScatter.addEventListener('click', toggleScatter);
    btnAutoPlay.addEventListener('click', toggleAutoPlay);
    btnTheme.addEventListener('click', cycleTheme);

    btnBrush.addEventListener('click', () => {
      isBrushMode = !isBrushMode;
      document.body.classList.toggle('brush-mode-active', isBrushMode);
      btnBrush.classList.toggle('primary', isBrushMode);
      if (window.soundEngine) window.soundEngine.playBell(1200);
    });

    btnSound.addEventListener('click', () => {
      if (window.soundEngine) {
        const isMuted = window.soundEngine.toggleMute();
        const soundBars = btnSound.querySelector('.sound-bars');
        if (soundBars) soundBars.classList.toggle('active', !isMuted);
      }
    });

    btnExport.addEventListener('click', openExportModal);
    modalCloseBtn.addEventListener('click', closeExportModal);
    exportModal.addEventListener('click', (e) => {
      if (e.target === exportModal) closeExportModal();
    });
  }

  function spawnBrushParticle(x, y) {
    const CHARS = ['閻', '姿', '桂'];
    const char = CHARS[Math.floor(Math.random() * CHARS.length)];
    const colors = currentTheme === 'midnight'
      ? ['#38bdf8', '#c084fc', '#f43f5e', '#facc15']
      : ['#ef4444', '#f59e0b', '#3b82f6', '#10b981', '#1c1917'];
    const color = colors[Math.floor(Math.random() * colors.length)];
    brushParticles.push(new BrushParticle(x, y, char, color));
    if (brushParticles.length > 80) brushParticles.shift();
  }

  function buildRibbon() {
    if (!poseNavRibbon || !window.SNOOPY_POSES) return;
    poseNavRibbon.innerHTML = '';

    window.SNOOPY_POSES.forEach((pose, idx) => {
      const chip = document.createElement('button');
      chip.className = `pose-chip ${idx === 0 ? 'active' : ''}`;
      chip.innerHTML = `<span class="chip-num">0${idx + 1}</span> <span>${pose.title}</span>`;
      chip.addEventListener('click', () => {
        applyPose(idx, true, true);
      });
      poseNavRibbon.appendChild(chip);
    });
  }

  // Main Render Loop (60 FPS)
  function animate(now) {
    requestAnimationFrame(animate);

    const delta = now - lastFrameTime;
    lastFrameTime = now;

    // Slow Progressive Evolution advancement
    if (isEvolutionPlaying && evolutionProgress < 1.0) {
      const step = (delta / CONFIG.baseEvolutionDuration) * evolutionSpeed;
      evolutionProgress = Math.min(1.0, evolutionProgress + step);
      updateEvolutionUI();

      if (evolutionProgress >= 1.0) {
        if (scatterText) scatterText.textContent = "散落文字";
        if (window.soundEngine) window.soundEngine.playBell(1046.5);
      }
    }

    ctx.clearRect(0, 0, width, height);

    // Update & Render Particles with progressive evolution
    for (let i = 0; i < particles.length; i++) {
      particles[i].update(now, evolutionProgress);
      particles[i].render(ctx, currentTheme);
    }

    // Brush particles
    for (let i = brushParticles.length - 1; i >= 0; i--) {
      brushParticles[i].update();
      brushParticles[i].render(ctx);
      if (brushParticles[i].alpha <= 0) brushParticles.splice(i, 1);
    }
  }

  // Export High-Res Wallpaper / Polaroid Card Modal
  function openExportModal() {
    const exportCanvas = document.createElement('canvas');
    const expW = 1080;
    const expH = 1920;
    exportCanvas.width = expW;
    exportCanvas.height = expH;
    const expCtx = exportCanvas.getContext('2d');

    const pose = window.SNOOPY_POSES[currentPoseIndex];

    const bgMap = {
      classic: '#fbf8f1',
      midnight: '#090d16',
      risograph: '#fdf6ec',
      imperial: '#f5efe6'
    };
    expCtx.fillStyle = bgMap[currentTheme] || '#fbf8f1';
    expCtx.fillRect(0, 0, expW, expH);

    // Museum Framing
    const frameColor = currentTheme === 'midnight' ? '#1e293b' : '#e2d9cc';
    expCtx.lineWidth = 3;
    expCtx.strokeStyle = frameColor;
    expCtx.strokeRect(36, 36, expW - 72, expH - 72);
    expCtx.lineWidth = 1;
    expCtx.strokeRect(44, 44, expW - 88, expH - 88);

    // Header metadata
    expCtx.fillStyle = currentTheme === 'midnight' ? '#94a3b8' : '#78716c';
    expCtx.font = '800 24px -apple-system, sans-serif';
    expCtx.textAlign = 'center';
    expCtx.fillText('YEN TZU-KUEI // KINETIC TYPOGRAPHY ART ARCHIVE', expW / 2, 120);

    // Artist Seal Stamp
    expCtx.fillStyle = '#ef4444';
    expCtx.fillRect(expW / 2 - 80, 150, 160, 44);
    expCtx.fillStyle = '#ffffff';
    expCtx.font = '900 24px serif';
    expCtx.fillText('閻姿桂 印', expW / 2, 180);

    // Titles
    expCtx.fillStyle = currentTheme === 'midnight' ? '#f8fafc' : '#1c1917';
    expCtx.font = '900 58px "Microsoft JhengHei", sans-serif';
    expCtx.fillText(`閻姿桂 × 史奴比`, expW / 2, 280);

    expCtx.fillStyle = currentTheme === 'midnight' ? '#38bdf8' : '#ef4444';
    expCtx.font = '800 42px "Microsoft JhengHei", sans-serif';
    expCtx.fillText(pose.title, expW / 2, 345);

    expCtx.fillStyle = currentTheme === 'midnight' ? '#94a3b8' : '#78716c';
    expCtx.font = '600 28px serif';
    expCtx.fillText(pose.englishTitle, expW / 2, 390);

    // Render 480 Snoopy Particles in center
    const expCx = expW / 2;
    const expCy = 940;
    const expScale = 1.95;
    const pts = pose.particles || pose.points;

    pts.forEach(p => {
      const px = expCx + p.x * expScale;
      const py = expCy + p.y * expScale;
      const pColor = getThemedColor(p.role, p.color, currentTheme);
      const pSize = Math.round(p.size * expScale * 0.95);

      expCtx.save();
      expCtx.translate(px, py);
      expCtx.font = `800 ${pSize}px "Microsoft JhengHei", sans-serif`;
      expCtx.textAlign = 'center';
      expCtx.textBaseline = 'middle';

      if (currentTheme === 'midnight') {
        expCtx.shadowColor = pColor;
        expCtx.shadowBlur = 14;
      }

      if (p.color === '#ffffff' && currentTheme !== 'midnight') {
        expCtx.fillStyle = currentTheme === 'risograph' ? '#fde047' : '#e2e8f0';
        expCtx.fillText(p.char, 0, 0);
        expCtx.lineWidth = 2;
        expCtx.strokeStyle = '#94a3b8';
        expCtx.strokeText(p.char, 0, 0);
      } else {
        expCtx.fillStyle = pColor;
        expCtx.fillText(p.char, 0, 0);
      }
      expCtx.restore();
    });

    // Bottom Quote
    expCtx.fillStyle = currentTheme === 'midnight' ? '#e2e8f0' : '#27272a';
    expCtx.font = 'italic 700 32px serif';
    expCtx.fillText(pose.quote, expW / 2, 1620);

    expCtx.fillStyle = currentTheme === 'midnight' ? '#64748b' : '#a8a29e';
    expCtx.font = '600 22px sans-serif';
    expCtx.fillText('480 KINETIC CHARACTERS (160 閻 / 160 姿 / 160 桂) ｜ LIMITED ART EDITION', expW / 2, 1720);
    expCtx.fillText('COLLECTED ON 2026.11 ｜ FREE PUBLIC ACCESS', expW / 2, 1760);

    const dataURL = exportCanvas.toDataURL('image/png');
    exportPreviewImg.src = dataURL;
    exportModal.classList.add('active');

    modalDownloadBtn.onclick = () => {
      const a = document.createElement('a');
      a.download = `閻姿桂_史奴比高精度桌布_${pose.id}_${currentTheme}.png`;
      a.href = dataURL;
      a.click();
    };

    if (window.soundEngine) window.soundEngine.playBell(1318.5);
  }

  function closeExportModal() {
    exportModal.classList.remove('active');
  }

  // Initialization
  function init() {
    canvas = document.getElementById('canvas-stage');
    ctx = canvas.getContext('2d');

    artworkBadge = document.getElementById('artwork-badge');
    artworkTitle = document.getElementById('artwork-title');
    artworkQuote = document.getElementById('artwork-quote');

    evolutionStatus = document.getElementById('evolution-status');
    evolutionScrubber = document.getElementById('evolution-scrubber');
    btnEvoPlay = document.getElementById('btn-evo-play');
    evoPlayIcon = document.getElementById('evo-play-icon');
    btnEvoReplay = document.getElementById('btn-evo-replay');
    speedPillButtons = document.querySelectorAll('.speed-pill');

    poseNavRibbon = document.getElementById('pose-nav');
    btnAutoPlay = document.getElementById('btn-autoplay');
    playRingCircle = document.getElementById('play-ring-circle');
    playIcon = document.getElementById('play-icon');
    playBtnText = document.getElementById('play-btn-text');
    btnScatter = document.getElementById('btn-scatter');
    scatterText = document.getElementById('scatter-text');
    btnExport = document.getElementById('btn-export');
    btnTheme = document.getElementById('btn-theme');
    btnSound = document.getElementById('btn-sound');
    btnBrush = document.getElementById('btn-brush');
    exportModal = document.getElementById('export-modal');
    exportPreviewImg = document.getElementById('export-preview-img');
    modalCloseBtn = document.getElementById('modal-close');
    modalDownloadBtn = document.getElementById('modal-download-btn');

    handleResize();
    initParticles();
    buildRibbon();
    setupEvents();

    // Start with Pose 0 in slow progressive evolution!
    applyPose(0, true, false);

    requestAnimationFrame(animate);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
