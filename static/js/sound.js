/* PathFinder sound effects — synthesised with the Web Audio API (no audio files). */
(() => {
  'use strict';
  let ctx = null, master = null, muted = false;
  try { muted = localStorage.getItem('pf-muted') === '1'; } catch { /* storage blocked */ }

  function ac() {
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      if (!AC) return null;
      ctx = new AC();
      master = ctx.createGain(); master.gain.value = 0.5;
      const comp = ctx.createDynamicsCompressor();
      master.connect(comp); comp.connect(ctx.destination);
    }
    if (ctx.state === 'suspended') ctx.resume();
    return ctx;
  }

  // one note: frequency, start offset (s), length (s), wave, volume, optional pitch slide
  function note(f, at, dur, type = 'sine', vol = 0.3, slideTo = null) {
    if (muted) return;
    const c = ac(); if (!c) return;
    const t = c.currentTime + at;
    const o = c.createOscillator(), g = c.createGain();
    o.type = type; o.frequency.setValueAtTime(f, t);
    if (slideTo) o.frequency.exponentialRampToValueAtTime(slideTo, t + dur);
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(vol, t + 0.012);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + 0.03);
  }
  function noise(at, dur, vol = 0.12, hp = 3000) {
    if (muted) return;
    const c = ac(); if (!c) return;
    const t = c.currentTime + at, n = Math.floor(c.sampleRate * dur);
    const buf = c.createBuffer(1, n, c.sampleRate), d = buf.getChannelData(0);
    for (let i = 0; i < n; i++) d[i] = (Math.random() * 2 - 1) * (1 - i / n);
    const s = c.createBufferSource(), f = c.createBiquadFilter(), g = c.createGain();
    s.buffer = buf; f.type = 'highpass'; f.frequency.value = hp; g.gain.value = vol;
    s.connect(f); f.connect(g); g.connect(master); s.start(t);
  }
  const N = { C5: 523.25, D5: 587.33, E5: 659.25, G5: 783.99, A5: 880, B5: 987.77, C6: 1046.5, E6: 1318.5, G6: 1568, C7: 2093 };

  const SFX = {
    get muted() { return muted; },
    setMuted(v) {
      muted = !!v;
      try { localStorage.setItem('pf-muted', muted ? '1' : '0'); } catch { /* ignore */ }
      if (!muted) { ac(); SFX.pop(); }
    },
    unlock() { if (!muted) ac(); },
    // soft button click
    tap() { note(620, 0, 0.07, 'triangle', 0.22, 420); },
    // candy pop, pitch rises with i (for chains of pops)
    pop(i = 0) { const f = 420 + i * 70; note(f, 0, 0.12, 'sine', 0.3, f * 1.8); noise(0, 0.03, 0.05, 5000); },
    // wrong tap on a locked level
    error() { note(190, 0, 0.14, 'square', 0.14, 130); note(150, 0.12, 0.18, 'square', 0.14, 100); },
    // rating pick
    select() { note(N.E5, 0, 0.09, 'triangle', 0.25); note(N.A5, 0.07, 0.13, 'triangle', 0.25); },
    // a star landing: n = 1..3
    star(n = 1) { const f = [N.G5, N.B5, N.E6][n - 1] || N.G5; note(f, 0, 0.35, 'triangle', 0.3); note(f * 2, 0, 0.25, 'sine', 0.1); noise(0, 0.05, 0.06, 6000); },
    // level complete jingle (more notes for more stars)
    win(stars = 1) {
      const seq = stars === 3 ? [N.C5, N.E5, N.G5, N.C6, N.E6, N.G6] : stars === 2 ? [N.C5, N.E5, N.G5, N.C6, N.E6] : [N.C5, N.E5, N.G5, N.C6];
      seq.forEach((f, i) => { note(f, i * 0.085, 0.4, 'triangle', 0.28); note(f / 2, i * 0.085, 0.4, 'sine', 0.12); });
      const end = seq.length * 0.085;
      [N.C6, N.E6, N.G6].forEach((f) => note(f, end, 0.7, 'triangle', 0.18));
    },
    // praise word whoosh
    praise() { note(300, 0, 0.3, 'sawtooth', 0.06, 1400); noise(0, 0.25, 0.05, 4000); },
    // player level up
    levelUp() { [N.G5, N.C6, N.E6, N.G6, N.C7].forEach((f, i) => { note(f, i * 0.1, 0.5, 'square', 0.1); note(f, i * 0.1, 0.5, 'triangle', 0.22); }); },
    // badge earned
    badge() { note(N.E6, 0, 0.18, 'sine', 0.3); note(N.G6, 0.1, 0.18, 'sine', 0.3); note(N.C7, 0.2, 0.6, 'sine', 0.3); noise(0.2, 0.2, 0.05, 7000); },
    // whole world cleared
    world() { [N.C5, N.G5, N.C6, N.E6, N.G6, N.C7].forEach((f, i) => { note(f, i * 0.11, 0.55, 'triangle', 0.26); }); noise(0.4, 0.6, 0.08, 4000); },
    // next level unlocked
    unlock() { note(N.G5, 0, 0.1, 'triangle', 0.25); note(N.C6, 0.09, 0.1, 'triangle', 0.25); note(N.E6, 0.18, 0.3, 'triangle', 0.28); },
    // LeetCode problem ticked off
    solve(diff = 'Easy') { const up = { Easy: 0, Medium: 1, Hard: 2 }[diff] || 0; note(N.C6, 0, 0.1, 'triangle', 0.28); note(N.E6, 0.08, 0.12, 'triangle', 0.28); if (up) note(N.G6, 0.16, 0.14, 'triangle', 0.28); if (up > 1) note(N.C7, 0.24, 0.4, 'triangle', 0.28); },
    unsolve() { note(N.E5, 0, 0.1, 'triangle', 0.2, 330); },
    // timer finished
    ding() { note(N.C7, 0, 0.9, 'sine', 0.3); note(N.G6, 0.0, 0.9, 'sine', 0.12); },
    // sheet opens
    open() { note(300, 0, 0.14, 'sine', 0.22, 700); },
    // tiny sparkle for the demo guide
    sparkle() { note(N.E6, 0, 0.1, 'sine', 0.18); note(N.C7, 0.07, 0.18, 'sine', 0.16); },
  };
  window.SFX = SFX;
})();
