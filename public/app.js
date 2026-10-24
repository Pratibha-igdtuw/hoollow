/* PathFinder — front-end logic (vanilla JS, no build step) */
(() => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const KEY = "pathfinder_v1";

  const BADGES = [
    { id: "first", ic: "🚀", t: "First Step", d: "Finish 1 step", test: (s, p) => p.doneCount >= 1 },
    { id: "stage", ic: "🏁", t: "Stage Clear", d: "Finish a stage", test: (s, p) => p.stagesDone >= 1 },
    { id: "streak", ic: "🔥", t: "On Fire", d: "3-day streak", test: (s) => s.streak >= 3 },
    { id: "half", ic: "⛰️", t: "Halfway", d: "50% complete", test: (s, p) => p.pct >= 50 },
    { id: "lvl", ic: "⚡", t: "Level Up", d: "Reach level 2", test: (s) => level(s.xp) >= 2 },
    { id: "done", ic: "🏆", t: "Finisher", d: "Complete the path", test: (s, p) => p.pct === 100 },
  ];

  const blank = () => ({ roadmap: null, source: "", done: {}, xp: 0, streak: 0, lastDay: "", badges: [], profile: null });
  let S = load();
  let current = null; // step being viewed in modal
  let demo = false;
  let timerId = null;

  function load() {
    try { return { ...blank(), ...JSON.parse(localStorage.getItem(KEY) || "{}") }; } catch { return blank(); }
  }
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch {} }
  const level = (xp) => Math.floor(xp / 100) + 1;
  const today = () => new Date().toLocaleDateString("en-CA");
  const yesterday = () => { const d = new Date(); d.setDate(d.getDate() - 1); return d.toLocaleDateString("en-CA"); };

  /* ---------- helpers ---------- */
  function show(id) {
    $$(".view").forEach((v) => v.classList.toggle("active", v.id === id));
    window.scrollTo({ top: 0, behavior: "smooth" });
    $("#hud").hidden = !(S.roadmap && id === "path");
  }
  let toastTimer;
  function toast(msg, ms = 2600) {
    const t = $("#toast");
    t.textContent = msg;
    t.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => t.classList.remove("show"), ms);
  }
  const allSteps = () => (S.roadmap ? S.roadmap.stages.flatMap((st, si) => st.steps.map((x) => ({ ...x, stageIdx: si, stage: st.title }))) : []);
  const xpFor = (m) => 10 + Math.round(m / 2);

  function progress() {
    const steps = allSteps();
    const doneCount = steps.filter((x) => S.done[x.id]).length;
    const pct = steps.length ? Math.round((doneCount / steps.length) * 100) : 0;
    const stagesDone = S.roadmap ? S.roadmap.stages.filter((st) => st.steps.every((x) => S.done[x.id])).length : 0;
    const active = steps.find((x) => !S.done[x.id]) || null;
    return { steps, doneCount, pct, stagesDone, active };
  }

  /* ---------- form wiring ---------- */
  const form = { level: "beginner", minutes: 20 };
  $$(".seg").forEach((seg) =>
    seg.addEventListener("click", (e) => {
      const b = e.target.closest("button");
      if (!b) return;
      $$("button", seg).forEach((x) => x.classList.toggle("on", x === b));
      form[seg.dataset.name] = seg.dataset.name === "minutes" ? Number(b.dataset.v) : b.dataset.v;
    })
  );
  $("#suggest").addEventListener("click", (e) => {
    const b = e.target.closest(".pill");
    if (!b) return;
    $("#skill").value = b.dataset.skill;
    $("#skill").focus();
  });
  $("#form").addEventListener("submit", (e) => {
    e.preventDefault();
    generate($("#skill").value.trim());
  });
  $("#demo").addEventListener("click", () => {
    demo = true;
    $("#skill").value = "Python";
    form.level = "beginner";
    form.minutes = 10;
    generate("Python");
  });
  $("#restart").addEventListener("click", () => {
    if (!confirm("Start a new goal? Your current progress will be cleared.")) return;
    S = blank(); save(); show("home");
  });
  $("#brand").addEventListener("click", (e) => { e.preventDefault(); show(S.roadmap ? "path" : "home"); });

  /* ---------- generate ---------- */
  const LOAD_LINES = ["Finding the smallest first step", "Sequencing what to learn next", "Matching steps to your daily time", "Adding quick wins along the way"];
  async function generate(skill) {
    const err = $("#err");
    err.hidden = true;
    if (skill.length < 2) { err.textContent = "Tell us what you want to learn."; err.hidden = false; return; }
    $("#loadTitle").textContent = `Mapping your ${skill} path…`;
    show("loading");
    let i = 0;
    const iv = setInterval(() => { $("#loadSub").textContent = LOAD_LINES[++i % LOAD_LINES.length]; }, 700);
    const started = Date.now();
    try {
      const res = await fetch("/api/roadmap", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ skill, level: form.level, minutes: form.minutes }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong");
      const wait = Math.max(0, 1500 - (Date.now() - started)); // keep the loader visible long enough to feel intentional
      await new Promise((r) => setTimeout(r, wait));
      S = { ...blank(), roadmap: data.roadmap, source: data.source, profile: { skill, ...form }, streak: S.streak, lastDay: S.lastDay, badges: [], xp: 0 };
      save();
      render();
      show("path");
      if (demo) runDemoCoach();
    } catch (e) {
      demo = false;
      show("home");
      err.textContent = e.message || "Could not build your roadmap. Is the server running?";
      err.hidden = false;
    } finally {
      clearInterval(iv);
    }
  }

  /* ---------- render ---------- */
  function render() {
    if (!S.roadmap) return;
    const p = progress();
    const rm = S.roadmap;
    $("#pTitle").textContent = rm.skill;
    $("#pTag").textContent = `${rm.tagline} · ~${rm.totalWeeks} week${rm.totalWeeks > 1 ? "s" : ""} at ${S.profile?.minutes || 20} min/day`;
    $("#pSource").textContent = S.source === "claude" ? "Your roadmap · generated by Claude" : "Your roadmap";

    // ring
    $("#ringFg").style.strokeDashoffset = 326.7 * (1 - p.pct / 100);
    $("#pPct").textContent = p.pct + "%";

    // HUD + XP bar
    const lvl = level(S.xp);
    $("#hudStreak").textContent = S.streak;
    $("#hudXp").textContent = S.xp;
    $("#hudLvl").textContent = lvl;
    $("#xLvl").textContent = lvl;
    $("#xNow").textContent = S.xp % 100;
    $("#xFill").style.width = S.xp % 100 + "%";
    $("#hud").hidden = false;

    // next card
    const n = $("#next");
    if (p.active) {
      const a = p.active;
      n.innerHTML = `
        <p class="eyebrow">${p.doneCount === 0 ? "Your first step" : "Up next"} · ${esc(a.stage)}</p>
        <h3>${esc(a.title)}</h3>
        <p>${esc(a.action)}</p>
        <div class="cta-row">
          <button class="btn primary" id="startBtn">Start this step →</button>
        </div>
        <div class="meta" style="margin-top:18px">
          <span class="tag">${esc(a.type)}</span><span class="tag">${a.minutes} min</span><span class="tag xp">+${xpFor(a.minutes)} XP</span>
        </div>`;
      $("#startBtn").addEventListener("click", () => openStep(a));
    } else {
      n.innerHTML = `
        <p class="eyebrow">Path complete</p>
        <h3>You did it. 🏆</h3>
        <p>You finished every step of your ${esc(rm.skill)} roadmap. Pick your next goal and keep the momentum going.</p>
        <button class="btn primary" id="again">Choose a new goal</button>`;
      $("#again").addEventListener("click", () => { S = { ...blank(), streak: S.streak, lastDay: S.lastDay }; save(); show("home"); });
    }

    // timeline
    const tl = $("#timeline");
    tl.innerHTML = "";
    let reached = false;
    rm.stages.forEach((st, si) => {
      const doneN = st.steps.filter((x) => S.done[x.id]).length;
      const stageDone = doneN === st.steps.length;
      const isCurrent = !stageDone && !reached;
      if (isCurrent) reached = true;
      const locked = !stageDone && !isCurrent;
      const el = document.createElement("div");
      el.className = `stage ${stageDone ? "done" : ""} ${isCurrent ? "current open" : ""} ${locked ? "locked" : ""}`;
      el.innerHTML = `
        <button class="stage-h" aria-expanded="${isCurrent}">
          <span class="num">0${si + 1}</span>
          <span class="t"><b>${esc(st.title)}</b><span>${esc(st.goal)}</span></span>
          <span class="cnt">${stageDone ? "✓ done" : `${doneN}/${st.steps.length}`}</span>
        </button>
        <div class="steps"></div>`;
      const box = $(".steps", el);
      st.steps.forEach((x) => {
        const isDone = !!S.done[x.id];
        const isActive = p.active && p.active.id === x.id;
        const b = document.createElement("button");
        b.className = `step ${isDone ? "done" : ""} ${isActive ? "active" : ""}`;
        b.disabled = !isActive;
        b.innerHTML = `
          <span class="dot">${isDone ? "✓" : ""}</span>
          <span class="s-t"><b>${esc(x.title)}</b><small>${esc(x.action)}</small></span>
          <span class="mins">${x.minutes}m</span>`;
        if (isActive) b.addEventListener("click", () => openStep(x));
        box.appendChild(b);
      });
      $(".stage-h", el).addEventListener("click", () => el.classList.toggle("open"));
      tl.appendChild(el);
    });

    // badges
    $("#badges").innerHTML = BADGES.map(
      (b) => `<div class="badge ${S.badges.includes(b.id) ? "got" : ""}"><div class="ic">${b.ic}</div><b>${b.t}</b><small>${b.d}</small></div>`
    ).join("");
  }
  function esc(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

  /* ---------- step modal ---------- */
  function openStep(step) {
    current = step;
    $("#mMeta").textContent = `${step.stage} · ${step.type} · ${step.minutes} min`;
    $("#mTitle").textContent = step.title;
    $("#mAction").textContent = step.action;
    $("#mHint").textContent = "💡 " + (step.hint || "Keep it small and just begin.");
    $("#mFeedback").hidden = true;
    $("#mActions").hidden = false;
    $("#mTimerText").hidden = true;
    $("#mTimer").textContent = "Start timer";
    stopTimer();
    $("#modal").hidden = false;
    document.body.style.overflow = "hidden";
  }
  function closeModal() {
    $("#modal").hidden = true;
    document.body.style.overflow = "";
    stopTimer();
    $("#mDone").classList.remove("spot");
  }
  $("#mClose").addEventListener("click", closeModal);
  $("#modal").addEventListener("click", (e) => { if (e.target.id === "modal") closeModal(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("#modal").hidden) closeModal(); });

  $("#mDone").addEventListener("click", () => {
    $("#mActions").hidden = true;
    $("#mTimerText").hidden = true;
    $("#mFeedback").hidden = false;
    stopTimer();
  });
  $("#mFeedback").addEventListener("click", (e) => {
    const b = e.target.closest("button[data-f]");
    if (b && current) completeStep(current, b.dataset.f);
  });

  /* timer */
  function stopTimer() { clearInterval(timerId); timerId = null; }
  $("#mTimer").addEventListener("click", () => {
    if (timerId) { stopTimer(); $("#mTimer").textContent = "Resume timer"; return; }
    let left = (current?.minutes || 10) * 60;
    const tick = () => {
      const m = String(Math.floor(left / 60)).padStart(2, "0");
      const s = String(left % 60).padStart(2, "0");
      $("#mTimerText").textContent = `${m}:${s}`;
      if (left-- <= 0) { stopTimer(); toast("Time's up — nicely done! Tap “I did it”."); }
    };
    $("#mTimerText").hidden = false;
    $("#mTimer").textContent = "Pause timer";
    tick();
    timerId = setInterval(tick, 1000);
  });

  /* ---------- completion + rewards ---------- */
  function completeStep(step, feel) {
    if (S.done[step.id]) return;
    S.done[step.id] = true;
    const prevLvl = level(S.xp);
    const gain = xpFor(step.minutes) + (feel === "hard" ? 5 : 0); // bonus for pushing through
    S.xp += gain;

    // streak
    const t = today();
    if (S.lastDay !== t) {
      S.streak = S.lastDay === yesterday() ? S.streak + 1 : 1;
      S.lastDay = t;
    }

    const p = progress();
    const newly = BADGES.filter((b) => !S.badges.includes(b.id) && b.test(S, p));
    S.badges.push(...newly.map((b) => b.id));
    save();
    closeModal();
    render();

    ["hudXp", "hudStreak", "hudLvl"].forEach((id) => { const c = $("#" + id).parentElement; c.classList.remove("bump"); void c.offsetWidth; c.classList.add("bump"); });

    const reply = { easy: "Easy! Moving you right along.", ok: "Right on pace.", hard: "Tough ones count double — nice grit." }[feel];
    const stageJustDone = step && S.roadmap.stages.some((st) => st.steps.some((x) => x.id === step.id) && st.steps.every((x) => S.done[x.id]));
    const lvlUp = level(S.xp) > prevLvl;

    toast(`+${gain} XP · ${reply}`);
    burst(stageJustDone || lvlUp || p.pct === 100 ? 220 : 70);
    let delay = 2700;
    if (lvlUp) setTimeout(() => toast(`⚡ Level ${level(S.xp)} unlocked!`), delay), (delay += 2700);
    if (stageJustDone && p.pct < 100) setTimeout(() => toast("🏁 Stage cleared!"), delay), (delay += 2700);
    newly.forEach((b) => { setTimeout(() => toast(`${b.ic} Badge: ${b.t}`), delay); delay += 2700; });
    if (p.pct === 100) setTimeout(() => burst(400), 600);

    if (demo) {
      demo = false;
      setTimeout(() => toast("That's the loop: pick a goal → roadmap → one step → reward. 🎉", 4200), delay);
    }
    // gently pull the next step into view
    setTimeout(() => $("#next").scrollIntoView({ behavior: "smooth", block: "center" }), 350);
  }

  /* ---------- 60-second guided demo ---------- */
  function runDemoCoach() {
    toast("① Your AI roadmap is ready — here's the very first step", 3200);
    const btn = $("#startBtn");
    if (btn) btn.classList.add("spot");
    setTimeout(() => {
      const p = progress();
      if (!p.active || !demo) return;
      toast("② Open the step. Do it. Then tap “I did it”.", 3200);
      openStep(p.active);
      $("#mDone").classList.add("spot");
    }, 3400);
  }

  /* ---------- confetti ---------- */
  const cv = $("#confetti");
  const cx = cv.getContext("2d");
  let parts = [];
  let raf = 0;
  function fit() { cv.width = innerWidth * devicePixelRatio; cv.height = innerHeight * devicePixelRatio; }
  addEventListener("resize", fit); fit();
  function burst(n) {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const colors = ["#c6ff3d", "#7c5cff", "#7fffd4", "#ffffff", "#ffb020"];
    const W = cv.width, H = cv.height;
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI - Math.PI; // upward fan
      const v = (6 + Math.random() * 12) * devicePixelRatio;
      parts.push({ x: W / 2, y: H * 0.7, vx: Math.cos(a) * v * 0.9, vy: Math.sin(a) * v - 4, w: (5 + Math.random() * 6) * devicePixelRatio, h: (3 + Math.random() * 5) * devicePixelRatio, r: Math.random() * 6, vr: (Math.random() - 0.5) * 0.4, c: colors[(Math.random() * colors.length) | 0], life: 1 });
    }
    if (!raf) raf = requestAnimationFrame(loop);
  }
  function loop() {
    cx.clearRect(0, 0, cv.width, cv.height);
    parts = parts.filter((p) => p.life > 0 && p.y < cv.height + 40);
    for (const p of parts) {
      p.vy += 0.38 * devicePixelRatio; p.vx *= 0.99; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.life -= 0.007;
      cx.save(); cx.translate(p.x, p.y); cx.rotate(p.r); cx.globalAlpha = Math.max(0, p.life); cx.fillStyle = p.c; cx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); cx.restore();
    }
    raf = parts.length ? requestAnimationFrame(loop) : 0;
  }

  /* ---------- boot ---------- */
  if (S.roadmap) { render(); show("path"); } else show("home");
})();
