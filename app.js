/**
 * app.js - 閻姿桂文字史奴比動力學藝術引擎
 * 60 FPS HTML5 Canvas Kinetic Typography Animation Engine
 */

(function () {
  'use strict';

  // Configuration
  const CONFIG = {
    totalParticles: 420,
    springK: 0.08,
    friction: 0.86,
    repelRadius: 130,
    repelForce: 24,
    autoPlayInterval: 6500, // 6.5s per pose
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
  let isScattered = false;
  let isBrushMode = false;
  let isAutoPlaying = false;
  let autoPlayTimer = null;
  let autoPlayProgress = 0;
  let autoPlayStartTime = 0;
  let currentTheme = 'classic';
  let brushParticles = [];

  // Device Tilt Offset
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
  let artworkMetaCard, artworkBadge, artworkTitle, artworkQuote;
  let poseNavRibbon, btnAutoPlay, playRingCircle, playIcon, playBtnText;
  let btnScatter, scatterText, btnExport, btnTheme, btnSound, btnBrush;
  let exportModal, exportPreviewImg, modalCloseBtn, modalDownloadBtn;

  // Particle Class
  class Particle {
    constructor(idx, char) {
      this.idx = idx;
      this.char = char; // '閻' or '姿' or '桂'
      this.x = (Math.random() - 0.5) * 800;
      this.y = (Math.random() - 0.5) * 800;
      this.vx = 0;
      this.vy = 0;
      this.tx = 0;
      this.ty = 0;
      this.role = 'body';
      this.baseColor = '#0f172a';
      this.size = 18;
      this.rot = (Math.random() - 0.5) * Math.PI;
      this.vRot = 0;
      this.scale = 1.0;
      this.idleSeed = Math.random() * 100;
      this.scatterTx = 0;
      this.scatterTy = 0;
    }

    setTarget(tx, ty, role, color, size, isMorphing = true) {
      this.tx = tx;
      this.ty = ty;
      this.role = role;
      this.baseColor = color;
      this.size = size;

      if (isMorphing) {
        // Swirling trajectory burst
        const dx = tx - this.x;
        const dy = ty - this.y;
        const dist = Math.hypot(dx, dy);
        const swirlAngle = Math.atan2(dy, dx) + (Math.sin(this.idx * 0.15) * 1.2);
        const impulse = Math.min(dist * 0.12, 16);
        this.vx += Math.cos(swirlAngle) * impulse;
        this.vy += Math.sin(swirlAngle) * impulse;
        this.vRot = (Math.random() - 0.5) * 0.35;
        this.scale = 1.35;
      }
    }

    update(time) {
      // Choose target based on scatter state
      let destX = isScattered ? this.scatterTx : this.tx;
      let destY = isScattered ? this.scatterTy : this.ty;

      // Add gentle mobile tilt
      destX += tiltX * 30;
      destY += tiltY * 30;

      // Subtle breathing motion when idle
      if (!isScattered) {
        const breath = Math.sin(time * 0.0025 + this.idleSeed) * 1.6;
        destY += breath;
      }

      // Spring physics
      const ax = (destX - this.x) * CONFIG.springK;
      const ay = (destY - this.y) * CONFIG.springK;

      this.vx = (this.vx + ax) * CONFIG.friction;
      this.vy = (this.vy + ay) * CONFIG.friction;

      // Pointer repulsion / wind
      if (pointer.isDown || pointer.x > 0) {
        const pdx = this.x - pointer.x;
        const pdy = this.y - pointer.y;
        const pdist = Math.hypot(pdx, pdy);

        if (pdist < CONFIG.repelRadius && pdist > 0) {
          const force = (1 - pdist / CONFIG.repelRadius) * CONFIG.repelForce;
          this.vx += (pdx / pdist) * force;
          this.vy += (pdy / pdist) * force;
          this.vRot += (Math.random() - 0.5) * 0.15;
          this.scale = 1.25;
        }
      }

      // Position update
      this.x += this.vx;
      this.y += this.vy;

      // Rotation damping
      this.rot += this.vRot;
      this.vRot *= 0.92;
      if (!isScattered && Math.abs(this.vRot) < 0.001) {
        this.rot *= 0.95; // settle back to horizontal
      }

      // Scale recovery
      this.scale += (1.0 - this.scale) * 0.1;
    }

    render(ctx, theme) {
      ctx.save();
      ctx.translate(this.x, this.y);
      ctx.rotate(this.rot);
      ctx.scale(this.scale, this.scale);

      // Color Adaptation by Theme
      const finalColor = getThemedColor(this.role, this.baseColor, theme);
      const fontSize = Math.round(this.size * scaleFactor);

      ctx.font = `800 ${fontSize}px "Microsoft JhengHei", "PingFang TC", sans-serif`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';

      // Neon / Glow effect for Midnight theme
      if (theme === 'midnight') {
        ctx.shadowColor = finalColor;
        ctx.shadowBlur = this.role === 'sunglasses' ? 4 : 12;
      } else if (theme === 'risograph') {
        // Risograph tiny faux ink offset
        ctx.fillStyle = finalColor;
        ctx.globalAlpha = 0.85;
      } else if (theme === 'imperial') {
        // Imperial ink bleeding
        if (this.role.includes('heart') || this.role.includes('roof') || this.role.includes('scarf')) {
          ctx.shadowColor = 'rgba(185, 28, 28, 0.4)';
          ctx.shadowBlur = 6;
        }
      }

      // White body fur outline check on light backgrounds
      if (this.baseColor === '#ffffff' && (theme === 'classic' || theme === 'risograph' || theme === 'imperial')) {
        ctx.fillStyle = theme === 'risograph' ? '#fde047' : '#e2e8f0';
        ctx.fillText(this.char, 0, 0);
        ctx.lineWidth = 1;
        ctx.strokeStyle = theme === 'classic' ? '#94a3b8' : '#64748b';
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
      this.vy += 0.08; // gravity
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

  // Theme Color Mapper
  function getThemedColor(role, baseColor, theme) {
    if (theme === 'classic') {
      return baseColor;
    }

    if (theme === 'midnight') {
      if (role === 'nose' || role === 'sunglasses') return '#38bdf8';
      if (role === 'ear' || role.includes('ear')) return '#818cf8';
      if (role.includes('roof') || role.includes('scarf') || role.includes('heart') || role === 'sweater') return '#f43f5e';
      if (role.includes('woodstock') || role === 'sparkle') return '#facc15';
      if (role.includes('cloud') || role === 'bubble' || role === 'ball_trail') return '#06b6d4';
      if (role === 'grass') return '#10b981';
      return '#f8fafc';
    }

    if (theme === 'risograph') {
      if (role.includes('roof') || role.includes('scarf') || role.includes('heart') || role === 'sweater' || role === 'collar') {
        return '#ff2a6d'; // Risograph Fluoro Pink
      }
      if (role.includes('woodstock') || role === 'sparkle' || role === 'golf_ball') {
        return '#ffbe0b';
      }
      if (role.includes('cloud') || role === 'bubble') {
        return '#3a86ff';
      }
      if (role === 'grass') return '#06d6a0';
      return '#051937'; // Deep Ocean Indigo
    }

    if (theme === 'imperial') {
      if (role.includes('roof') || role.includes('scarf') || role.includes('heart') || role === 'sweater' || role === 'collar') {
        return '#b91c1c'; // Cinnabar Red
      }
      if (role.includes('woodstock') || role === 'sparkle' || role === 'golf_ball') {
        return '#d4af37'; // Shimmering Imperial Gold
      }
      if (role.includes('cloud') || role === 'bubble') {
        return '#a8a29e';
      }
      if (role === 'grass') return '#047857';
      return '#1c1917'; // Rich Calligraphic Ink
    }

    return baseColor;
  }

  // Init Particle System
  function initParticles() {
    particles = [];
    const CHARS = ['閻', '姿', '桂'];
    for (let i = 0; i < CONFIG.totalParticles; i++) {
      const char = CHARS[i % 3];
      const p = new Particle(i, char);
      // Pre-calculate circular cosmos scatter positions
      const scatterAngle = (i / CONFIG.totalParticles) * Math.PI * 2 * 3;
      const scatterRadius = 260 + (i % 7) * 40;
      p.scatterTx = Math.cos(scatterAngle) * scatterRadius;
      p.scatterTy = Math.sin(scatterAngle) * scatterRadius;
      particles.push(p);
    }
  }

  // Load Pose by Index
  function applyPose(poseIdx, triggerSound = true) {
    if (!window.SNOOPY_POSES || !window.SNOOPY_POSES[poseIdx]) return;
    currentPoseIndex = poseIdx;
    const pose = window.SNOOPY_POSES[poseIdx];

    // Center offset on canvas
    const cx = width / 2;
    const cy = height / 2 + 15; // slightly lower than center for visual balance

    pose.particles.forEach((item, i) => {
      if (particles[i]) {
        const tx = cx + item.x * scaleFactor;
        const ty = cy + item.y * scaleFactor;
        particles[i].setTarget(tx, ty, item.role, item.color, item.size, true);
      }
    });

    // Update Meta Display
    if (artworkBadge) artworkBadge.textContent = `ARCHIVE 0${poseIdx + 1} / 0${window.SNOOPY_POSES.length}`;
    if (artworkTitle) artworkTitle.textContent = pose.title;
    if (artworkQuote) artworkQuote.textContent = pose.quote;

    // Update Ribbon Active State
    document.querySelectorAll('.pose-chip').forEach((chip, idx) => {
      chip.classList.toggle('active', idx === poseIdx);
      if (idx === poseIdx) {
        chip.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
      }
    });

    // Sound
    if (triggerSound && window.soundEngine) {
      window.soundEngine.playMorphArpeggio();
    }
  }

  // Scatter / Deconstruct
  function toggleScatter() {
    isScattered = !isScattered;
    if (isScattered) {
      scatterText.textContent = "聚攏史奴比";
      // Scatter to random chaotic vortex
      const cx = width / 2;
      const cy = height / 2;
      particles.forEach((p, idx) => {
        const ang = (idx / CONFIG.totalParticles) * Math.PI * 2 * 4 + (Math.random() - 0.5);
        const rad = Math.min(width, height) * 0.42 * (0.4 + Math.random() * 0.8);
        p.scatterTx = cx + Math.cos(ang) * rad;
        p.scatterTy = cy + Math.sin(ang) * rad;
        p.vx += (Math.random() - 0.5) * 20;
        p.vy += (Math.random() - 0.5) * 20;
        p.vRot = (Math.random() - 0.5) * 0.6;
      });
      if (window.soundEngine) window.soundEngine.playScatterWhoosh();
    } else {
      scatterText.textContent = "解構文字";
      // Reassemble smoothly
      applyPose(currentPoseIndex, false);
      if (window.soundEngine) window.soundEngine.playMagneticSnap();
    }
  }

  // Auto-Play Cycle
  function toggleAutoPlay() {
    isAutoPlaying = !isAutoPlaying;
    btnAutoPlay.classList.toggle('active', isAutoPlaying);
    playBtnText.textContent = isAutoPlaying ? "播映中" : "巡迴播映";
    playIcon.innerHTML = isAutoPlaying
      ? '<path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>' // Pause icon
      : '<path d="M8 5v14l11-7z"/>'; // Play icon

    if (isAutoPlaying) {
      autoPlayStartTime = performance.now();
      autoPlayTimer = setInterval(nextPose, CONFIG.autoPlayInterval);
    } else {
      clearInterval(autoPlayTimer);
      autoPlayTimer = null;
      if (playRingCircle) playRingCircle.style.strokeDashoffset = '75.4';
    }
  }

  function nextPose() {
    const nextIdx = (currentPoseIndex + 1) % window.SNOOPY_POSES.length;
    applyPose(nextIdx, true);
    autoPlayStartTime = performance.now();
  }

  function prevPose() {
    const prevIdx = (currentPoseIndex - 1 + window.SNOOPY_POSES.length) % window.SNOOPY_POSES.length;
    applyPose(prevIdx, true);
    autoPlayStartTime = performance.now();
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

    // Adaptive scale factor based on screen size (standard base 540px virtual box)
    const minDim = Math.min(width, height);
    scaleFactor = Math.min(minDim / 540, 1.25);
    if (width < 450) {
      scaleFactor = (width / 500) * 0.98;
    }

    // Re-anchor target positions without heavy animation
    if (window.SNOOPY_POSES && window.SNOOPY_POSES[currentPoseIndex]) {
      const cx = width / 2;
      const cy = height / 2 + 15;
      window.SNOOPY_POSES[currentPoseIndex].particles.forEach((item, i) => {
        if (particles[i]) {
          particles[i].tx = cx + item.x * scaleFactor;
          particles[i].ty = cy + item.y * scaleFactor;
        }
      });
    }
  }

  // Pointer & Touch Events
  function setupEvents() {
    // Window Resize
    window.addEventListener('resize', handleResize);

    // Touch & Pointer on Canvas
    const onPointerDown = (e) => {
      pointer.isDown = true;
      const clientX = e.touches ? e.touches[0].clientX : e.clientX;
      const clientY = e.touches ? e.touches[0].clientY : e.clientY;
      pointer.x = clientX;
      pointer.y = clientY;
      pointer.startX = clientX;
      pointer.startY = clientY;
      pointer.startTime = performance.now();

      // Double Tap check
      const now = performance.now();
      if (now - pointer.lastTapTime < 320) {
        toggleScatter();
        pointer.lastTapTime = 0;
      } else {
        pointer.lastTapTime = now;
      }

      // If brush mode, spawn immediate character
      if (isBrushMode) {
        spawnBrushParticle(clientX, clientY);
      } else {
        // Sound pop
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

      // Swipe detection (horizontal swipe threshold 45px in under 500ms)
      if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy) * 1.5 && dt < 500) {
        if (dx < 0) {
          nextPose();
        } else {
          prevPose();
        }
      }

      // Reset pointer influence after short delay
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

    // Device Tilt (Gyroscope)
    if (window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientation', (e) => {
        if (e.gamma !== null && e.beta !== null) {
          // Normalised tilt (-1 to 1)
          tiltX = Math.max(-1, Math.min(1, e.gamma / 35));
          tiltY = Math.max(-1, Math.min(1, (e.beta - 40) / 45));
        }
      }, { passive: true });
    }

    // UI Buttons
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

  // Calligraphy Wand Particle Spawner
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

  // Populate Bottom Poses Ribbon
  function buildRibbon() {
    if (!poseNavRibbon || !window.SNOOPY_POSES) return;
    poseNavRibbon.innerHTML = '';

    window.SNOOPY_POSES.forEach((pose, idx) => {
      const chip = document.createElement('button');
      chip.className = `pose-chip ${idx === 0 ? 'active' : ''}`;
      chip.innerHTML = `<span class="chip-num">0${idx + 1}</span> <span>${pose.title}</span>`;
      chip.addEventListener('click', () => {
        applyPose(idx, true);
        if (isAutoPlaying) autoPlayStartTime = performance.now();
      });
      poseNavRibbon.appendChild(chip);
    });
  }

  // Main Render Loop (60 FPS)
  function animate(now) {
    requestAnimationFrame(animate);

    ctx.clearRect(0, 0, width, height);

    // Update & Render Particles
    for (let i = 0; i < particles.length; i++) {
      particles[i].update(now);
      particles[i].render(ctx, currentTheme);
    }

    // Update & Render Calligraphy Brush Particles
    for (let i = brushParticles.length - 1; i >= 0; i--) {
      brushParticles[i].update();
      brushParticles[i].render(ctx);
      if (brushParticles[i].alpha <= 0) {
        brushParticles.splice(i, 1);
      }
    }

    // Auto Play Progress Ring Update
    if (isAutoPlaying && playRingCircle) {
      const elapsed = now - autoPlayStartTime;
      const progress = Math.min(1, elapsed / CONFIG.autoPlayInterval);
      const circumference = 75.4; // 2 * PI * 12
      const offset = circumference * (1 - progress);
      playRingCircle.style.strokeDashoffset = offset.toFixed(1);
    }
  }

  // Export High-Res Wallpaper / Polaroid Card Modal
  function openExportModal() {
    const exportCanvas = document.createElement('canvas');
    // High-resolution 9:16 mobile wallpaper standard (1080 x 1920)
    const expW = 1080;
    const expH = 1920;
    exportCanvas.width = expW;
    exportCanvas.height = expH;
    const expCtx = exportCanvas.getContext('2d');

    const pose = window.SNOOPY_POSES[currentPoseIndex];

    // Background based on current theme
    const bgMap = {
      classic: '#fbf8f1',
      midnight: '#090d16',
      risograph: '#fdf6ec',
      imperial: '#f5efe6'
    };
    expCtx.fillStyle = bgMap[currentTheme] || '#fbf8f1';
    expCtx.fillRect(0, 0, expW, expH);

    // Elegant Outer Museum Framing
    const frameColor = currentTheme === 'midnight' ? '#1e293b' : '#e2d9cc';
    expCtx.lineWidth = 3;
    expCtx.strokeStyle = frameColor;
    expCtx.strokeRect(36, 36, expW - 72, expH - 72);
    expCtx.lineWidth = 1;
    expCtx.strokeRect(44, 44, expW - 88, expH - 88);

    // Top Museum Meta
    expCtx.fillStyle = currentTheme === 'midnight' ? '#94a3b8' : '#78716c';
    expCtx.font = '800 24px -apple-system, sans-serif';
    expCtx.textAlign = 'center';
    expCtx.fillText('YEN TZU-KUEI // KINETIC TYPOGRAPHY ART ARCHIVE', expW / 2, 120);

    // Artist Seal Stamp on Top
    expCtx.fillStyle = '#ef4444';
    expCtx.fillRect(expW / 2 - 80, 150, 160, 44);
    expCtx.fillStyle = '#ffffff';
    expCtx.font = '900 24px serif';
    expCtx.fillText('閻姿桂 印', expW / 2, 180);

    // Big Title & English Title
    expCtx.fillStyle = currentTheme === 'midnight' ? '#f8fafc' : '#1c1917';
    expCtx.font = '900 58px "Microsoft JhengHei", sans-serif';
    expCtx.fillText(`閻姿桂 × 史奴比`, expW / 2, 280);

    expCtx.fillStyle = currentTheme === 'midnight' ? '#38bdf8' : '#ef4444';
    expCtx.font = '800 42px "Microsoft JhengHei", sans-serif';
    expCtx.fillText(pose.title, expW / 2, 345);

    expCtx.fillStyle = currentTheme === 'midnight' ? '#94a3b8' : '#78716c';
    expCtx.font = '600 28px serif';
    expCtx.fillText(pose.englishTitle, expW / 2, 390);

    // Render 420 Snoopy Particles in center
    const expCx = expW / 2;
    const expCy = 940;
    const expScale = 1.95;

    // Sort particles so fills draw first
    const sortedPoseParticles = [...pose.particles].sort((a, b) => {
      const aFill = a.role.includes('fill') ? 0 : 1;
      const bFill = b.role.includes('fill') ? 0 : 1;
      return aFill - bFill;
    });

    sortedPoseParticles.forEach(p => {
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

    // Bottom Poetic Quote
    expCtx.fillStyle = currentTheme === 'midnight' ? '#e2e8f0' : '#27272a';
    expCtx.font = 'italic 700 32px serif';
    expCtx.fillText(pose.quote, expW / 2, 1620);

    // Bottom Archival Metadata & Authenticity Guarantee
    expCtx.fillStyle = currentTheme === 'midnight' ? '#64748b' : '#a8a29e';
    expCtx.font = '600 22px sans-serif';
    expCtx.fillText('420 KINETIC CHARACTERS (140 閻 / 140 姿 / 140 桂) ｜ LIMITED ART EDITION', expW / 2, 1720);
    expCtx.fillText('COLLECTED ON 2026.11 ｜ FREE PUBLIC ACCESS', expW / 2, 1760);

    // Show in Modal
    const dataURL = exportCanvas.toDataURL('image/png');
    exportPreviewImg.src = dataURL;
    exportModal.classList.add('active');

    // Setup Download Click
    modalDownloadBtn.onclick = () => {
      const a = document.createElement('a');
      a.download = `閻姿桂_史奴比藝術桌布_${pose.id}_${currentTheme}.png`;
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

    artworkMetaCard = document.getElementById('artwork-meta');
    artworkBadge = document.getElementById('artwork-badge');
    artworkTitle = document.getElementById('artwork-title');
    artworkQuote = document.getElementById('artwork-quote');
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

    // Initial Pose load
    applyPose(0, false);

    // Start 60 FPS animation loop
    requestAnimationFrame(animate);
  }

  // Boot on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
