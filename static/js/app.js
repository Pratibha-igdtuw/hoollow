/* PathFinder — single-page front end (vanilla JS, no build step) */
(() => {
  'use strict';
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const wait = (ms) => new Promise((r) => setTimeout(r, ms));
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const root = $('#root');

  /* ---------------- state ---------------- */
  const blank = () => ({ xp: 0, streak: 0, lastDay: '', badges: [], active: null, paths: {}, solved: {} });
  let ME = null, STATE = blank(), CATALOG = [], DEMO = false;
  let saveT;
  const persist = () => { clearTimeout(saveT); saveT = setTimeout(() => api('/api/state', { method: 'PUT', body: STATE }).catch(() => {}), 300); };
  const playerLevel = () => Math.floor(STATE.xp / 100) + 1;
  const dayStr = (d = new Date()) => d.toLocaleDateString('en-CA');
  const activePath = () => (STATE.active && STATE.paths[STATE.active]) || null;
  const flat = (P) => { let n = 0; return P.roadmap.stages.flatMap((st, si) => st.steps.map((s, i) => ({ ...s, world: si, stage: st, idx: n++, last: i === st.steps.length - 1 }))); };

  async function api(url, opts = {}) {
    const res = await fetch(url, {
      method: opts.method || 'GET',
      headers: { 'content-type': 'application/json' },
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    let data = {};
    try { data = await res.json(); } catch { /* empty */ }
    if (!res.ok) throw new Error(data.error || 'Something went wrong. Please try again.');
    return data;
  }

  /* ---------------- icons ---------------- */
  const STAR = 'M12 2.6l2.9 6 6.6.9-4.8 4.6 1.2 6.5L12 17.4 6.1 20.6l1.2-6.5L2.5 9.5l6.6-.9z';
  const I = {
    star: (on) => `<svg viewBox="0 0 24 24" class="st ${on ? 'on' : ''}"><path d="${STAR}"/></svg>`,
    lock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="5" y="11" width="14" height="9" rx="2.2"/><path d="M8 11V8a4 4 0 018 0v3"/></svg>',
    crown: '<svg viewBox="0 0 30 22" fill="currentColor"><path d="M2 20L0 5l7.5 6L15 1l7.5 10L30 5l-2 15z"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>',
    flame: '<svg viewBox="0 0 24 24"><path d="M12 1.5c1.2 4 6 6.4 6 11.7a6 6 0 01-12 0c0-2.4 1.2-3.6 2.4-4.8.4 1.9 1.4 2.8 2.4 3C11 8.6 10.8 5 12 1.5z" fill="#ff6a2b"/><path d="M12 12c.8 1.6 2.6 2.4 2.6 4.4a2.6 2.6 0 01-5.2 0c0-1.2.7-1.9 1.4-2.6.2.8.6 1.2 1 1.3-.1-1 .1-2.2.2-3.1z" fill="#ffd93b"/></svg>',
    bolt: '<svg viewBox="0 0 24 24"><path d="M13.5 1.5L4 13.5h6.2l-1.4 9 9.7-12.5h-6.4z" fill="#ffd93b" stroke="#c98a00" stroke-width="1.4" stroke-linejoin="round"/></svg>',
    sound: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5z" fill="currentColor"/><path d="M15.5 9a4 4 0 010 6M18 6.5a8 8 0 010 11"/></svg>',
    muted: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5z" fill="currentColor"/><path d="M16 9.5l5 5M21 9.5l-5 5"/></svg>',
    ext: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 01-1 1H5a1 1 0 01-1-1V7a1 1 0 011-1h5"/></svg>',
    level: '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" fill="#ff4fa3" stroke="#fff" stroke-width="2"/><path d="M12 5.5l1.9 4 4.4.6-3.2 3 .8 4.4-3.9-2.1-3.9 2.1.8-4.4-3.2-3 4.4-.6z" fill="#fff"/></svg>',
  };
  const LOGO = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle cx="16" cy="16" r="15" fill="#fff" stroke="#c21f78" stroke-width="1.6"/><path d="M16 16L16 1A15 15 0 0 1 28.99 8.5Z M16 16L28.99 23.5A15 15 0 0 1 16 31Z M16 16L3.01 23.5A15 15 0 0 1 3.01 8.5Z" fill="#ff4fa3"/><circle cx="16" cy="16" r="4.2" fill="#fff" stroke="#c21f78" stroke-width="1.4"/><ellipse cx="10" cy="7.5" rx="4" ry="2" fill="#fff" opacity=".75" transform="rotate(-30 10 7.5)"/></svg>';
  const logo = (href = '#/') => `<a class="logo" href="${href}">${LOGO}<span>PathFinder</span></a>`;

  /* ---------------- badges ---------------- */
  const BADGES = [
    { id: 'first', t: 'First level', d: 'Complete any level', test: (s) => s.done >= 1 },
    { id: 'three', t: 'Perfect score', d: 'Earn three stars on a level', test: (s) => s.three },
    { id: 'world', t: 'World cleared', d: 'Finish every level in a world', test: (s) => s.worlds >= 1 },
    { id: 'streak', t: 'Three-day streak', d: 'Learn three days in a row', test: (s) => STATE.streak >= 3 },
    { id: 'half', t: 'Halfway there', d: 'Reach 50% of your path', test: (s) => s.pct >= 50 },
    { id: 'coder', t: 'Problem solver', d: 'Solve 10 LeetCode problems', test: () => solvedCount() >= 10 },
    { id: 'path', t: 'Path complete', d: 'Finish an entire roadmap', test: (s) => s.full },
  ];
  function stats() {
    let done = 0, stars = 0, three = false, worlds = 0, full = false;
    Object.values(STATE.paths).forEach((P) => {
      const f = flat(P);
      f.forEach((s) => { const v = P.done[s.id]; if (v) { done++; stars += v; if (v === 3) three = true; } });
      P.roadmap.stages.forEach((st) => { if (st.steps.every((s) => P.done[s.id])) worlds++; });
      if (f.length && f.every((s) => P.done[s.id])) full = true;
    });
    const A = activePath();
    const fa = A ? flat(A) : [];
    const pct = fa.length ? Math.round((fa.filter((s) => A.done[s.id]).length / fa.length) * 100) : 0;
    return { done, stars, three, worlds, full, pct };
  }

  /* ---------------- toast, confetti ---------------- */
  let toastT;
  function toast(msg, ms = 2600) {
    const t = $('#toast');
    t.textContent = msg; t.classList.add('show');
    clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove('show'), ms);
  }
  const cv = $('#confetti'), cx = cv.getContext('2d');
  let parts = [], raf = 0;
  const fit = () => { cv.width = innerWidth * devicePixelRatio; cv.height = innerHeight * devicePixelRatio; };
  addEventListener('resize', fit); fit();
  function burst(n = 110) {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const colors = ['#ff3b4a', '#ff9a1f', '#ffd93b', '#5ed13a', '#2f9bff', '#9b5de5', '#ff4fa3'];
    for (let i = 0; i < n; i++) {
      const a = -Math.PI * (0.15 + Math.random() * 0.7), v = (7 + Math.random() * 11) * devicePixelRatio;
      parts.push({ x: cv.width / 2, y: cv.height * 0.62, vx: Math.cos(a) * v, vy: Math.sin(a) * v, w: (6 + Math.random() * 6) * devicePixelRatio, h: (4 + Math.random() * 5) * devicePixelRatio, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.35, c: colors[(Math.random() * colors.length) | 0], t: (Math.random() * 3) | 0, life: 1 });
    }
    if (!raf) raf = requestAnimationFrame(loop);
  }
  function loop() {
    cx.clearRect(0, 0, cv.width, cv.height);
    parts = parts.filter((p) => p.life > 0 && p.y < cv.height + 40);
    parts.forEach((p) => {
      p.vy += 0.36 * devicePixelRatio; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.life -= 0.008;
      cx.save(); cx.translate(p.x, p.y); cx.rotate(p.r); cx.globalAlpha = Math.max(0, p.life); cx.fillStyle = p.c;
      if (p.t === 0) { cx.beginPath(); cx.arc(0, 0, p.w * 0.6, 0, 7); cx.fill(); cx.fillStyle = 'rgba(255,255,255,.7)'; cx.beginPath(); cx.arc(-p.w * 0.2, -p.w * 0.2, p.w * 0.18, 0, 7); cx.fill(); }
      else if (p.t === 1) { cx.beginPath(); cx.ellipse(0, 0, p.w * 0.8, p.h * 0.5, 0, 0, 7); cx.fill(); cx.strokeStyle = 'rgba(255,255,255,.75)'; cx.lineWidth = p.h * 0.28; cx.beginPath(); cx.moveTo(-p.w * 0.3, -p.h * 0.5); cx.lineTo(p.w * 0.3, p.h * 0.5); cx.stroke(); }
      else { cx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); }
      cx.restore();
    });
    raf = parts.length ? requestAnimationFrame(loop) : 0;
  }

  /* ---------------- sound hooks ---------------- */
  const sfx = (name, ...a) => { try { window.SFX && window.SFX[name](...a); } catch { /* audio unavailable */ } };
  addEventListener('pointerdown', () => sfx('unlock'), { once: true });
  document.addEventListener('click', (e) => {
    const t = e.target.closest('.btn, .skill-card, .link, .top nav a, .avatar, .menu button, .tab, .logo');
    if (t && !t.matches('.node')) sfx('tap');
  });
  const soundBtn = () => `<button class="stat mute" id="mute" aria-label="${window.SFX?.muted ? 'Turn sound on' : 'Turn sound off'}" title="Sound">${window.SFX?.muted ? I.muted : I.sound}</button>`;

  /* ---------------- routing ---------------- */
  const cur = () => location.hash.replace(/^#\/?/, '') || 'intro';
  const go = (r) => { location.hash = '#/' + (r === 'intro' ? '' : r); };
  const navigate = (r) => (cur() === r ? route() : go(r));

  async function route() {
    let r = cur();
    if (!['intro', 'login', 'app', 'map'].includes(r)) r = 'intro';
    if ((r === 'app' || r === 'map') && !ME) { r = 'login'; history.replaceState(null, '', '#/login'); }
    if (r === 'login' && ME) { r = 'app'; history.replaceState(null, '', '#/app'); }
    if (r === 'map' && !activePath()) { r = 'app'; history.replaceState(null, '', '#/app'); }
    closeSheet();
    if (r !== 'map' && !DEMO) hideCoach();
    ({ intro: viewIntro, login: viewLogin, app: viewApp, map: viewMap })[r]();
    window.scrollTo(0, 0);
  }
  addEventListener('hashchange', route);

  function bindNav(scope = root) {
    $$('[data-nav]', scope).forEach((el) => el.addEventListener('click', (e) => { e.preventDefault(); navigate(el.dataset.nav); }));
    $$('[data-scroll]', scope).forEach((el) => el.addEventListener('click', (e) => { e.preventDefault(); $('#' + el.dataset.scroll)?.scrollIntoView({ behavior: 'smooth' }); }));
  }

  /* ---------------- level path drawing ---------------- */
  function drawPath(c) {
    const svg = c && c.querySelector('svg.trail');
    if (!svg) return;
    const W = c.offsetWidth, H = c.offsetHeight;
    svg.setAttribute('width', W); svg.setAttribute('height', H); svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
    const pts = $$('.node', c).map((n) => { const lv = n.parentElement; return { x: lv.offsetLeft + n.offsetLeft + n.offsetWidth / 2, y: lv.offsetTop + n.offsetTop + n.offsetHeight / 2, done: n.dataset.state === 'done' }; });
    let base = '', prog = '';
    for (let i = 1; i < pts.length; i++) {
      const a = pts[i - 1], b = pts[i], my = (a.y + b.y) / 2;
      const seg = `M${a.x},${a.y} C${a.x},${my} ${b.x},${my} ${b.x},${b.y} `;
      base += seg; if (a.done) prog += seg;
    }
    svg.innerHTML = `<path class="t-edge" d="${base}"/><path class="t-base" d="${base}"/><path class="t-prog" d="${prog}"/>`;
  }
  const redrawAll = () => $$('.levels').forEach(drawPath);
  addEventListener('resize', redrawAll);
  if (document.fonts?.ready) document.fonts.ready.then(redrawAll);

  const X = [50, 74, 50, 26];
  function previewMap() {
    const rows = [
      { x: 50, st: 'done', stars: 3, n: 1, t: 'Install and say hello' },
      { x: 74, st: 'done', stars: 2, n: 2, t: 'Variables and types' },
      { x: 50, st: 'current', stars: 0, n: 3, t: 'Input and output' },
      { x: 26, st: 'locked', stars: 0, n: 4, t: 'Milestone: tip calculator', ms: true },
    ];
    return `<div class="levels preview compact"><svg class="trail"></svg>${rows.map((r) => `
      <div class="lv ${r.ms ? 'ms' : ''}" data-st="${r.st}" data-x="${r.x >= 60 ? 'r' : 'l'}" style="--x:${r.x}%;--i:${r.n}">
        ${r.st === 'current' ? '<div class="bubble">Play</div>' : ''}
        <div class="node" data-state="${r.st}">${r.st === 'locked' ? I.lock : r.n}${r.ms ? `<i class="crown">${I.crown}</i>` : ''}</div>
        <div class="stars">${[1, 2, 3].map((n) => I.star(r.stars >= n)).join('')}</div>
        <div class="lv-t">${r.t}</div>
      </div>`).join('')}</div>`;
  }

  /* ---------------- view: intro ---------------- */
  function viewIntro() {
    root.innerHTML = `
    <div class="view-in">
      <header class="nav" id="nav"><div class="container nav-in">
        ${logo()}
        <nav class="nav-links"><a href="#" data-scroll="how">How it works</a><a href="#" data-scroll="skills">Skills</a><a href="#" data-scroll="levels">Levels</a></nav>
        <div class="nav-cta"><button class="link" data-nav="login">Sign in</button><button class="btn btn-dark btn-sm" data-nav="login">Get started</button></div>
      </div></header>

      <section class="hero"><div class="container hero-grid">
        <div>
          <p class="eyebrow">Guided learning for technology</p>
          <h1 class="display" style="margin-top:18px">Learn technology the sweet way, <em>one level at a time.</em></h1>
          <p class="lede">PathFinder turns any tech skill into a game. Choose a skill, follow your candy-bright map, earn stars and finish one small level at a time.</p>
          <div class="cta-row">
            <button class="btn btn-dark" data-nav="login">Start learning free</button>
            <button class="btn btn-ghost" id="demoBtn">Watch the 60-second demo</button>
          </div>
          <p class="hero-note">No credit card. Your first step takes about ten minutes.</p>
        </div>
        <div class="hero-card">
          <div class="hc-top"><b>Python</b><span>World 1 · Getting Started</span></div>
          ${previewMap()}
        </div>
      </div></section>

      <section class="sec alt" id="how"><div class="container">
        <div class="sec-h"><p class="eyebrow">How it works</p><h2>Three easy steps from "where do I start?" to done.</h2></div>
        <div class="how">
          <div><span class="n">1</span><h3>Choose a skill</h3><p>Pick from carefully selected technology skills, then tell us your level and how much time you have each day.</p></div>
          <div><span class="n">2</span><h3>Get your roadmap</h3><p>An AI mentor builds a clear path of worlds and levels, sized to your day. The first step is always tiny.</p></div>
          <div><span class="n">3</span><h3>Play through it</h3><p>Finish a level, rate how it went, and earn stars. The next level is always one tap away, so nobody gets lost.</p></div>
        </div>
      </div></section>

      <section class="sec" id="skills"><div class="container">
        <div class="sec-h"><p class="eyebrow">Skills</p><h2>Focused on the skills that build careers in tech.</h2><p>Every path is hand-structured into four worlds, each ending in a small project you can show.</p></div>
        <div class="skills-mini">${CATALOG.map((s) => `<div class="skill-pill"><span class="mono">${esc(s.tag)}</span><div><b>${esc(s.name)}</b><small>${s.levels} levels</small></div></div>`).join('')}</div>
      </div></section>

      <section class="sec alt" id="levels"><div class="container feature">
        <div>
          <p class="eyebrow">Made to be finished</p>
          <div class="sec-h" style="margin-bottom:0"><h2>Levels, not lectures.</h2><p>Learning sticks when progress is visible. Every step is a level on a map, with stars, XP and badges that make coming back feel natural.</p></div>
          <ul>
            <li><i>01</i><div><b>One level at a time</b><span>Only the next level is open. You always know exactly what to do.</span></div></li>
            <li><i>02</i><div><b>Up to three stars</b><span>Rate how it went honestly. Replay a level to earn more stars.</span></div></li>
            <li><i>03</i><div><b>Streaks, XP and badges</b><span>Small, steady rewards that keep you going when motivation dips.</span></div></li>
            <li><i>04</i><div><b>A project at every world</b><span>Each world ends with a milestone, marked with a crown.</span></div></li>
          </ul>
        </div>
        <div class="hero-card"><div class="hc-top"><b>Your map</b><span>Level 3 of 16</span></div>${previewMap()}</div>
      </div></section>

      <section class="sec"><div class="container"><div class="band">
        <h2>Your first step takes <em>ten minutes.</em></h2>
        <p>Create a free account, pick a skill and play your first level today.</p>
        <button class="btn btn-dark" data-nav="login">Create your free account</button>
      </div></div></section>

      <footer class="container foot"><span>${logo().replace('href="#/"', 'href="#/"')}</span><span>Built as a learning prototype · PathFinder</span></footer>
    </div>`;
    bindNav();
    $('#demoBtn').addEventListener('click', startDemo);
    const nav = $('#nav');
    const onScroll = () => nav && nav.classList.toggle('scrolled', scrollY > 8);
    addEventListener('scroll', onScroll, { passive: true }); onScroll();
    requestAnimationFrame(redrawAll);
  }

  /* ---------------- view: login ---------------- */
  function viewLogin(mode = 'signin') {
    const up = mode === 'signup';
    root.innerHTML = `
    <div class="auth view-in">
      <aside class="auth-art">
        ${logo()}
        <div><blockquote>Small steps, <em>finished</em>, beat big plans left alone.</blockquote><small>Pick up exactly where you left off, on any device.</small></div>
        <span></span>
      </aside>
      <div class="auth-form-wrap"><form class="auth-form" id="authForm" novalidate>
        <a class="back" href="#/" data-nav="intro">← Back to home</a>
        <h1>${up ? 'Create your account' : 'Welcome back'}</h1>
        <p class="sub">${up ? 'Free to start. Your progress is saved automatically.' : 'Sign in to continue your path.'}</p>
        <div class="form-err" id="err" hidden></div>
        ${up ? '<label class="field"><span>Your name</span><input name="name" autocomplete="name" required /></label>' : ''}
        <label class="field"><span>Email</span><input name="email" type="email" autocomplete="email" required /></label>
        <label class="field"><span>Password</span><input name="password" type="password" autocomplete="${up ? 'new-password' : 'current-password'}" required /></label>
        <button class="btn btn-dark" id="authBtn" type="submit">${up ? 'Create account' : 'Sign in'}</button>
        <p class="switch">${up ? 'Already have an account?' : 'New to PathFinder?'} <button type="button" class="link" id="swap">${up ? 'Sign in' : 'Create an account'}</button></p>
        <div class="demo-box"><b>Just exploring?</b> <button type="button" class="link" id="demoLogin">Try the 60-second demo</button> with a ready-made account.</div>
      </form></div>
    </div>`;
    bindNav();
    $('#swap').addEventListener('click', () => viewLogin(up ? 'signin' : 'signup'));
    $('#demoLogin').addEventListener('click', startDemo);
    $('#authForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const f = Object.fromEntries(new FormData(e.target));
      const err = $('#err'), btn = $('#authBtn');
      err.hidden = true; btn.disabled = true;
      try {
        const d = await api(up ? '/api/auth/register' : '/api/auth/login', { method: 'POST', body: f });
        ME = d.user; STATE = { ...blank(), ...d.state };
        go('app');
      } catch (ex) { err.textContent = ex.message; err.hidden = false; btn.disabled = false; }
    });
    $('input', root).focus();
  }

  /* ---------------- app shell ---------------- */
  function shell(active, body) {
    const lvl = playerLevel();
    return `
    <header class="top"><div class="container top-in">
      ${logo('#/app')}
      <nav><a href="#/app" class="${active === 'app' ? 'on' : ''}">Skills</a>${activePath() ? `<a href="#/map" class="${active === 'map' ? 'on' : ''}">My path</a>` : ''}</nav>
      <div class="stats">
        <span class="stat" id="stStreak" title="Daily streak">${I.flame}<b>${STATE.streak}</b> day${STATE.streak === 1 ? '' : 's'}</span>
        <span class="stat" id="stXp" title="Experience points">${I.bolt}<b>${STATE.xp}</b> XP</span>
        <span class="stat" id="stLvl" title="Your level">${I.level}Level <b>${lvl}</b></span>
        ${soundBtn()}
      </div>
      <div class="avatar-wrap"><button class="avatar" id="avatar" aria-label="Account menu">${esc((ME.name || '?').charAt(0).toUpperCase())}</button>
        <div class="menu" id="menu" hidden><p>${esc(ME.name)}<small>${esc(ME.email)}</small></p><button id="logout">Sign out</button></div></div>
    </div></header>
    <main class="container view-in">${body}</main>`;
  }
  function bindShell() {
    bindNav();
    $('#mute').addEventListener('click', () => { const m = $('#mute'); window.SFX.setMuted(!window.SFX.muted); m.innerHTML = window.SFX.muted ? I.muted : I.sound; m.setAttribute('aria-label', window.SFX.muted ? 'Turn sound on' : 'Turn sound off'); });
    $('#avatar').addEventListener('click', (e) => { e.stopPropagation(); $('#menu').hidden = !$('#menu').hidden; });
    document.addEventListener('click', () => { const m = $('#menu'); if (m) m.hidden = true; }, { once: true });
    $('#logout').addEventListener('click', async () => {
      try { await api('/api/auth/logout', { method: 'POST' }); } catch { /* ignore */ }
      ME = null; STATE = blank(); DEMO = false; hideCoach(); go('intro');
    });
  }
  function bump(id) { const el = $('#' + id); if (!el) return; el.classList.remove('bump'); void el.offsetWidth; el.classList.add('bump'); }

  /* ---------------- view: dashboard ---------------- */
  function greet() { const h = new Date().getHours(); return h < 5 ? 'Late night' : h < 12 ? 'Good morning' : h < 17 ? 'Good afternoon' : 'Good evening'; }
  function viewApp() {
    const A = activePath();
    const first = (ME.name || '').split(' ')[0];
    let cont = '';
    if (A) {
      const f = flat(A), d = f.filter((s) => A.done[s.id]).length, next = f.find((s) => !A.done[s.id]);
      const pct = Math.round((d / f.length) * 100);
      cont = `<div class="cont">
        <div><p class="eyebrow">Continue your path</p><h3>${esc(A.roadmap.skill)}</h3>
          <div class="progress"><i style="width:${pct}%"></i></div>
          <small>${d} of ${f.length} levels · ${next ? 'Next: ' + esc(next.title) : 'Path complete'}</small></div>
        <button class="btn btn-dark" data-nav="map">${next ? 'Continue' : 'View map'}</button></div>`;
    }
    root.innerHTML = shell('app', `
      <div class="page">
        <div class="page-h"><p class="eyebrow">${greet()}</p><h1>${esc(first)}, what will you <em>learn</em> next?</h1></div>
        ${cont}
        <h2 class="sec-t">Choose a skill</h2>
        <div class="skill-grid">${CATALOG.map((s) => {
          const has = STATE.paths[s.key];
          const p = has ? Math.round((flat(has).filter((x) => has.done[x.id]).length / flat(has).length) * 100) : 0;
          return `<button class="skill-card" data-skill="${s.key}"><span class="mono">${esc(s.tag)}</span>
            <div><h3>${esc(s.name)}</h3><p>${esc(s.blurb)}</p></div>
            <div class="foot-r"><span>${s.levels} levels</span><b>${has ? p + '% · Continue' : 'Start'}</b></div></button>`;
        }).join('')}</div>
      </div>`);
    bindShell();
    $$('.skill-card').forEach((c) => c.addEventListener('click', () => {
      const key = c.dataset.skill;
      if (STATE.paths[key]) { STATE.active = key; persist(); go('map'); } else openSetup(key);
    }));
  }

  /* ---------------- setup sheet + build ---------------- */
  function sheet(html, onClose) {
    $('#modal-root').innerHTML = `<div class="sheet-back" data-close></div><div class="sheet" role="dialog" aria-modal="true"><button class="sheet-x" data-close aria-label="Close">×</button>${html}</div>`;
    $$('[data-close]', $('#modal-root')).forEach((el) => el.addEventListener('click', () => closeSheet()));
    document.body.style.overflow = 'hidden';
    sheet.onClose = onClose;
  }
  function closeSheet() {
    if (!$('#modal-root').innerHTML) return;
    $('#modal-root').innerHTML = ''; document.body.style.overflow = '';
    clearInterval(timerId); timerId = null;
    if (sheet.onClose) { const f = sheet.onClose; sheet.onClose = null; f(); }
  }
  addEventListener('keydown', (e) => { if (e.key === 'Escape') closeSheet(); });

  function openSetup(key) {
    const s = CATALOG.find((x) => x.key === key);
    const prof = { level: 'beginner', minutes: 20 };
    sheet(`
      <p class="eyebrow">New path</p><h3>${esc(s.name)}</h3><p class="lede">${esc(s.blurb)}</p>
      <span class="field-l" style="margin-top:6px">Where are you starting from?</span>
      <div class="seg" data-k="level"><button class="on" data-v="beginner">Brand new</button><button data-v="some">Know a little</button><button data-v="intermediate">Comfortable</button></div>
      <span class="field-l">Time you can give each day</span>
      <div class="seg" data-k="minutes"><button data-v="10">10 min</button><button class="on" data-v="20">20 min</button><button data-v="45">45 min</button></div>
      <button class="btn btn-dark" id="build" style="width:100%;margin-top:6px">Build my roadmap</button>`);
    $$('.seg').forEach((seg) => seg.addEventListener('click', (e) => {
      const b = e.target.closest('button'); if (!b) return;
      $$('button', seg).forEach((x) => x.classList.toggle('on', x === b));
      prof[seg.dataset.k] = seg.dataset.k === 'minutes' ? Number(b.dataset.v) : b.dataset.v;
    }));
    $('#build').addEventListener('click', () => { closeSheet(); buildPath(key, prof); });
  }

  const LOAD = ['Choosing the right first step', 'Sequencing your worlds', 'Fitting levels to your day', 'Adding a project to each world'];
  async function buildPath(key, prof) {
    const name = CATALOG.find((c) => c.key === key).name;
    const L = document.createElement('div'); L.className = 'loader';
    L.innerHTML = `<div><div class="balls"><i></i><i></i><i></i><i></i></div><h2>Building your ${esc(name)} path</h2><p id="ls">${LOAD[0]}</p></div>`;
    document.body.appendChild(L);
    let i = 0; const iv = setInterval(() => { const p = $('#ls'); if (p) p.textContent = LOAD[++i % LOAD.length]; }, 750);
    const t0 = Date.now();
    try {
      const d = await api('/api/roadmap', { method: 'POST', body: { skill: key, ...prof } });
      await wait(Math.max(0, 1600 - (Date.now() - t0)));
      STATE.paths[key] = { roadmap: d.roadmap, source: d.source, profile: prof, done: {} };
      STATE.active = key; persist();
      navigate('map');
    } catch (e) {
      DEMO = false; hideCoach(); toast(e.message, 4000);
    } finally { clearInterval(iv); L.remove(); }
  }

  /* ---------------- view: map ---------------- */
  function viewMap() {
    const P = activePath(), rm = P.roadmap, f = flat(P);
    const next = f.find((s) => !P.done[s.id]);
    const d = f.filter((s) => P.done[s.id]).length, pct = Math.round((d / f.length) * 100);
    const starsGot = f.reduce((a, s) => a + (P.done[s.id] || 0), 0);
    const lvl = playerLevel(), into = STATE.xp % 100, S = stats();

    let levels = '';
    rm.stages.forEach((st, si) => {
      const allLocked = st.steps.every((s) => !P.done[s.id] && !(next && next.id === s.id));
      levels += `<div class="world-ban ${allLocked ? 'dim' : ''}"><div><small>World ${si + 1}</small><b>${esc(st.title)}</b></div></div>`;
      st.steps.forEach((s, i) => {
        const g = f.find((x) => x.id === s.id);
        const state = P.done[s.id] ? 'done' : next && next.id === s.id ? 'current' : 'locked';
        const stars = P.done[s.id] || 0;
        levels += `<div class="lv ${g.last ? 'ms' : ''}" data-st="${state}" data-x="${X[i % 4] >= 60 ? 'r' : 'l'}" style="--x:${X[i % 4]}%;--i:${g.idx}">
          ${state === 'current' ? '<div class="bubble">Play</div>' : ''}
          <button class="node" data-state="${state}" data-id="${s.id}" aria-label="Level ${g.idx + 1}: ${esc(s.title)}${state === 'locked' ? ' (locked)' : ''}">${state === 'locked' ? I.lock : g.idx + 1}${g.last ? `<i class="crown">${I.crown}</i>` : ''}</button>
          <div class="stars">${[1, 2, 3].map((n) => I.star(stars >= n)).join('')}</div>
          <div class="lv-t">${esc(s.title)}</div></div>`;
      });
    });

    const side = `
      <aside class="side">
        ${next ? `<div class="card up"><h4>Up next · Level ${next.idx + 1}</h4><h3>${esc(next.title)}</h3><p>${esc(next.action)}</p><button class="btn btn-dark" id="playNext">Play level</button></div>`
               : `<div class="card up"><h4>Path complete</h4><h3>You finished ${esc(rm.skill)}.</h3><p>Choose another skill and keep your streak going.</p><button class="btn btn-dark" data-nav="app">Choose a skill</button></div>`}
        <div class="card"><h4>Your progress</h4>
          <div class="facts"><div><b>${d}/${f.length}</b><span>Levels</span></div><div><b>${starsGot}</b><span>Stars</span></div><div><b>${STATE.streak}</b><span>Day streak</span></div></div>
          <div class="lvl-bar"><div><span>Level ${lvl}</span><span>${into} / 100 XP</span></div><div class="progress" style="height:8px"><i style="width:${into}%"></i></div></div></div>
        ${STATE.active === 'dsa' ? `<div class="card lc-card"><h4>LeetCode sheet</h4><h3>${solvedCount()} problems solved</h3><p>Hand-picked problems that match your worlds.</p><button class="btn btn-dark" id="openSheet">Open the sheet</button></div>` : ''}
        <div class="card"><h4>Badges</h4>${BADGES.map((b) => `<div class="badge-row ${STATE.badges.includes(b.id) ? 'got' : ''}"><i>${I.check}</i><div>${b.t}<small>${b.d}</small></div></div>`).join('')}</div>
      </aside>`;

    root.innerHTML = shell('map', `
      <div class="map-page">
        <section>
          <div class="map-head"><p class="eyebrow">${P.source === 'claude' ? 'Roadmap by Claude' : 'Your roadmap'}</p><h1>${esc(rm.skill)}</h1><p>${esc(rm.tagline)} About ${rm.totalWeeks} week${rm.totalWeeks > 1 ? 's' : ''} at ${P.profile?.minutes || 20} minutes a day.</p>
            <div class="row"><div class="progress"><i style="width:${pct}%"></i></div><span>${pct}% complete</span></div></div>
          <div class="levels" id="levels"><svg class="trail"></svg>${levels}</div>
          <div class="map-foot"><button class="link" data-nav="app">Switch skill</button><button class="link" id="reset">Restart this path</button></div>
        </section>
        ${side}
      </div>`);
    bindShell();
    requestAnimationFrame(() => { redrawAll(); });
    $$('.node').forEach((n) => n.addEventListener('click', () => {
      if (n.dataset.state === 'locked') { n.classList.remove('shake'); void n.offsetWidth; n.classList.add('shake'); toast('Finish the level before this one to unlock it.'); sfx('error'); return; }
      sfx('open'); openLevel(f.find((x) => x.id === n.dataset.id));
    }));
    $('#openSheet')?.addEventListener('click', openSheetModal);
    $('#playNext')?.addEventListener('click', () => { sfx('open'); openLevel(next); });
    $('#reset').addEventListener('click', () => {
      if (!confirm('Restart this path? Your stars for it will be cleared.')) return;
      delete STATE.paths[STATE.active]; STATE.active = Object.keys(STATE.paths)[0] || null; persist(); navigate(STATE.active ? 'map' : 'app');
    });
    if (next && d > 0) setTimeout(() => $('.node[data-state="current"]')?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 250);
    if (DEMO && d === 0) coach(1, 3, 'This is your map. The glowing level is your first step. Tap it to begin.', '.node[data-state="current"]');
  }

  /* ---------------- LeetCode sheet (DSA) ---------------- */
  let SHEET = null;
  const lcUrl = (slug) => `https://leetcode.com/problems/${slug}/`;
  const isSolved = (slug) => (STATE.solved || {})[slug] === 2;
  const solvedCount = () => Object.values(STATE.solved || {}).filter((v) => v === 2).length;
  function problemRow(p) {
    return `<div class="pr ${isSolved(p.slug) ? 'solved' : ''}">
      <label><input type="checkbox" data-slug="${esc(p.slug)}" data-diff="${esc(p.diff)}" data-xp="${p.xp}" ${isSolved(p.slug) ? 'checked' : ''} aria-label="Mark ${esc(p.title)} as solved"><i class="tick">${I.check}</i></label>
      <span class="pr-t">${esc(p.title)}</span>
      <span class="diff d-${esc(p.diff.toLowerCase())}">${esc(p.diff)}</span>
      <a class="pr-go" href="${lcUrl(p.slug)}" target="_blank" rel="noopener noreferrer" aria-label="Open ${esc(p.title)} on LeetCode">${I.ext}</a></div>`;
  }
  function bindProblems(scope, onChange) {
    $$('.pr input', scope).forEach((cb) => cb.addEventListener('change', () => {
      STATE.solved = STATE.solved || {};
      const slug = cb.dataset.slug, xp = +cb.dataset.xp, was = STATE.solved[slug];
      if (cb.checked) {
        STATE.solved[slug] = 2;
        sfx('solve', cb.dataset.diff);
        if (!was) {
          STATE.xp += xp; toast(`Solved! +${xp} XP`, 1800);
          const b = $('#stXp b'); if (b) { b.textContent = STATE.xp; bump('stXp'); }
          const fresh = BADGES.filter((x) => !STATE.badges.includes(x.id) && x.test(stats()));
          if (fresh.length) { STATE.badges.push(...fresh.map((x) => x.id)); setTimeout(() => { toast(`New badge: ${fresh[0].t}`, 2400); sfx('badge'); burst(90); }, 700); }
        }
      } else { STATE.solved[slug] = 1; sfx('unsolve'); }
      cb.closest('.pr').classList.toggle('solved', cb.checked);
      persist(); onChange && onChange();
    }));
  }
  const countIn = (el) => { const all = $$('.pr input', el); return `${all.filter((c) => c.checked).length} / ${all.length}`; };
  function levelProblems(s) {
    if (!s.problems || !s.problems.length) return '';
    return `<div class="lc"><div class="lc-h"><h4>LeetCode practice</h4><b id="lcCount">${s.problems.filter((p) => isSolved(p.slug)).length} / ${s.problems.length}</b></div>${s.problems.map(problemRow).join('')}<p class="lc-note">Optional. Solve them on LeetCode, then tick them off here for bonus XP.</p></div>`;
  }
  async function openSheetModal() {
    if (!SHEET) { try { SHEET = await api('/api/sheet'); } catch { toast('Could not load the sheet. Check your connection.'); return; } }
    const total = SHEET.topics.reduce((a, t) => a + t.problems.length, 0);
    const worlds = [...new Set(SHEET.topics.map((t) => t.world))];
    sfx('open');
    sheet(`<p class="eyebrow">DSA · Practice</p><h3>LeetCode sheet</h3>
      <p class="lede">${total} hand-picked problems, in the same order as your worlds. Tick each one when you solve it.</p>
      <div class="lc-total"><div class="progress"><i id="lcBar" style="width:0%"></i></div><b id="lcAll"></b></div>
      <div id="lcBody">${worlds.map((w) => {
        const ts = SHEET.topics.filter((t) => t.world === w);
        return `<div class="lc-world"><h5><span>World ${w + 1}</span>${esc(ts[0].worldTitle)}</h5>${ts.map((t) => `<div class="lc-topic"><h6>${esc(t.title)}</h6>${t.problems.map(problemRow).join('')}</div>`).join('')}</div>`;
      }).join('')}</div>
      <div class="lc-ext"><h5>More sheets</h5>${SHEET.links.map((l) => `<a class="ext" href="${esc(l.url)}" target="_blank" rel="noopener noreferrer"><div><b>${esc(l.name)}</b><small>${esc(l.desc)}</small></div>${I.ext}</a>`).join('')}</div>`);
    const body = $('#lcBody');
    const upd = () => { const all = $$('.pr input', body), d = all.filter((c) => c.checked).length; $('#lcAll').textContent = `${d} / ${all.length} solved`; $('#lcBar').style.width = Math.round((d / all.length) * 100) + '%'; };
    bindProblems(body, upd); upd();
  }

  /* ---------------- level sheet ---------------- */
  let timerId = null, openStepRef = null;
  const xpFor = (m) => 10 + Math.round(m / 2);
  function openLevel(s) {
    const P = activePath(), old = P.done[s.id] || 0;
    openStepRef = s;
    sheet(`
      <div id="pDo">
        <p class="eyebrow">Level ${s.idx + 1} · ${esc(s.stage.title)}</p>
        <h3>${esc(s.title)}</h3>
        <p class="lede">${esc(s.action)}</p>
        <div class="tip"><b>Tip</b>${esc(s.hint || 'Keep it small and just begin.')}</div>
        ${levelProblems(s)}
        <div class="meta-row"><span>${s.minutes} min</span><span>${cap(s.type)}</span><span>+${xpFor(s.minutes)} XP</span>${old ? `<span>Best: ${old} star${old > 1 ? 's' : ''}</span>` : ''}</div>
        <div class="row"><button class="btn btn-dark" id="bDone">I've done this</button><button class="btn btn-ghost" id="bTimer">Start ${s.minutes}-minute timer</button></div>
        <div class="timer" id="timer" hidden></div>
      </div>
      <div id="pRate" hidden>
        <p class="eyebrow">Level ${s.idx + 1}</p><h3>How did it go?</h3><p class="lede">Be honest. It only helps you.</p>
        <div class="rate">
          <button data-s="3"><span class="rs3">${[1, 2, 3].map(() => I.star(true)).join('')}</span><div><b>Nailed it</b><small>I could do it again without notes</small></div></button>
          <button data-s="2"><span class="rs3">${[1, 2, 3].map((n) => I.star(n <= 2)).join('')}</span><div><b>Got it</b><small>I understood most of it</small></div></button>
          <button data-s="1"><span class="rs3">${[1, 2, 3].map((n) => I.star(n <= 1)).join('')}</span><div><b>Still shaky</b><small>I'd like another go later</small></div></button>
        </div>
      </div>
      <div id="pRes" hidden></div>`, () => { if (DEMO && !$('.node[data-state="done"]')) { /* keep tour alive */ } });
    bindProblems($('#pDo'), () => { const c = $('#lcCount'); if (c) c.textContent = countIn($('.lc')); });
    $('#bDone').addEventListener('click', () => {
      clearInterval(timerId); timerId = null;
      $('#pDo').hidden = true; $('#pRate').hidden = false;
      if (DEMO) coach(3, 3, 'Rate how it went. Honest ratings earn stars, and stars unlock the next level.', '.rate button');
    });
    $('#bTimer').addEventListener('click', () => {
      if (timerId) { clearInterval(timerId); timerId = null; $('#bTimer').textContent = 'Resume timer'; return; }
      let left = $('#timer').dataset.left ? +$('#timer').dataset.left : s.minutes * 60;
      const tick = () => {
        $('#timer').dataset.left = left;
        $('#timer').textContent = `${String(Math.floor(left / 60)).padStart(2, '0')}:${String(left % 60).padStart(2, '0')}`;
        if (left-- <= 0) { clearInterval(timerId); timerId = null; toast('Time is up. Nicely done.'); sfx('ding'); }
      };
      $('#timer').hidden = false; $('#bTimer').textContent = 'Pause timer'; tick(); timerId = setInterval(tick, 1000);
    });
    $$('#pRate button').forEach((b) => b.addEventListener('click', () => { sfx('select'); finishLevel(s, +b.dataset.s); }));
    if (DEMO) coach(2, 3, 'Read the step, do it (or imagine you did), then tap "I\'ve done this".', '#bDone');
  }

  function finishLevel(s, stars) {
    const P = activePath(), old = P.done[s.id] || 0, first = !old;
    const prevLvl = playerLevel(), prevWorlds = stats().worlds;
    let gain = 0;
    if (stars > old) P.done[s.id] = stars;
    if (first) {
      gain = xpFor(s.minutes) + stars * 5; STATE.xp += gain;
      const t = dayStr(), y = dayStr(new Date(Date.now() - 864e5));
      if (STATE.lastDay !== t) { STATE.streak = STATE.lastDay === y ? STATE.streak + 1 : 1; STATE.lastDay = t; }
    }
    const S = stats();
    const fresh = BADGES.filter((b) => !STATE.badges.includes(b.id) && b.test(S));
    STATE.badges.push(...fresh.map((b) => b.id));
    persist();
    const lvlUp = playerLevel() > prevLvl, worldDone = S.worlds > prevWorlds, pathDone = S.full && P.roadmap.stages.every((st) => st.steps.every((x) => P.done[x.id]));
    const more = flat(P).find((x) => !P.done[x.id]);
    const lines = [];
    if (worldDone) lines.push('World cleared!');
    if (lvlUp) lines.push(`You reached level ${playerLevel()}.`);
    fresh.forEach((b) => lines.push(`New badge: ${b.t}`));
    $('#pRate').hidden = true;
    const res = $('#pRes'); res.hidden = false;
    res.innerHTML = `<div class="res">
      <div class="res-stars">${[1, 2, 3].map((n) => `<span style="--d:${0.15 + n * 0.22}s">${I.star(n <= stars)}</span>`).join('')}</div>
      <h3>${pathDone ? 'Path Complete!' : 'Level Complete!'}</h3>
      <p class="gain">${first ? `+${gain} XP` : stars > old ? 'Better score saved.' : 'Your best score stays.'}</p>
      ${lines.map((l) => `<p class="extra">${esc(l)}</p>`).join('')}
      <button class="btn btn-dark" id="bNext">${more ? 'Next level' : 'Back to map'}</button></div>`;
    praise(stars);
    sfx('win', stars); sfx('praise');
    for (let n = 1; n <= stars; n++) setTimeout(() => sfx('star', n), 150 + n * 220 + 120);
    let at = 1000;
    if (lvlUp) { setTimeout(() => sfx('levelUp'), at); at += 650; }
    if (worldDone || pathDone) { setTimeout(() => sfx('world'), at); at += 700; }
    if (fresh.length) setTimeout(() => sfx('badge'), at);
    burst(worldDone || pathDone || lvlUp ? 240 : 110);
    if (pathDone) setTimeout(() => burst(260), 700);
    $('#bNext').addEventListener('click', () => {
      closeSheet(); viewMap(); sfx('unlock');
      ['stXp', 'stStreak', 'stLvl'].forEach(bump);
      setTimeout(() => $('.node[data-state="current"]')?.scrollIntoView({ behavior: 'smooth', block: 'center' }), 200);
      setTimeout(() => { const n = $('.node[data-state="current"]'); if (n) { n.classList.add('unlock'); setTimeout(() => n.classList.remove('unlock'), 1000); } }, 450);
      if (DEMO) { DEMO = false; coach(0, 0, 'That is the whole loop: pick a skill, get a roadmap, play one level, earn stars. Your account saves it all.', null, true); }
    });
    if (DEMO) coach(0, 0, 'Stars, XP and badges appear after every level. Tap "Next level" to see your map update.', null);
  }

  /* ---------------- praise word ---------------- */
  function praise(stars) {
    const word = { 3: 'Divine!', 2: 'Delicious!', 1: 'Sweet!' }[stars] || 'Sweet!';
    const color = { 3: '#ffe14d', 2: '#ffb62e', 1: '#ff8fd0' }[stars] || '#ffe14d';
    const el = document.createElement('div');
    el.className = 'praise'; el.style.setProperty('--c', color); el.textContent = word;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1900);
  }

  /* ---------------- guided demo ---------------- */
  async function startDemo() {
    try {
      const d = await api('/api/auth/demo', { method: 'POST' });
      ME = d.user; STATE = { ...blank(), ...d.state }; DEMO = true;
      await buildPath('python', { level: 'beginner', minutes: 10 });
      if (cur() !== 'map') go('map');
    } catch (e) { toast(e.message, 3500); }
  }
  function hideCoach() { const c = $('#coach'); c.hidden = true; c.innerHTML = ''; $$('.spot').forEach((e) => e.classList.remove('spot')); }
  function coach(n, total, text, target, last) {
    const c = $('#coach'); c.hidden = false;
    c.innerHTML = `${n ? `<span class="c-n">${n} / ${total}</span>` : ''}<p>${esc(text)}</p>${last ? '<button class="btn" id="cOk">Explore</button>' : '<button id="cSkip">Skip tour</button>'}`;
    sfx('sparkle');
    $$('.spot').forEach((e) => e.classList.remove('spot'));
    if (target) $$(target).forEach((e) => e.classList.add('spot'));
    $('#cSkip')?.addEventListener('click', () => { DEMO = false; hideCoach(); });
    $('#cOk')?.addEventListener('click', hideCoach);
  }

  /* ---------------- boot ---------------- */
  (async function boot() {
    try { CATALOG = await api('/api/catalog'); } catch { CATALOG = []; }
    try {
      const d = await api('/api/me');
      if (d.user) { ME = d.user; STATE = { ...blank(), ...d.state }; }
    } catch { /* offline */ }
    route();
  })();
})();
