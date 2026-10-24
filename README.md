# PathFinder — AI learning roadmaps that feel easy

Pick a goal → get an AI-generated roadmap → take one clear next step → get rewarded.

## Run it (2 minutes)

```bash
npm install
cp .env.example .env     # optional: add ANTHROPIC_API_KEY for Claude-generated roadmaps
npm start
# open http://localhost:3000
```

No API key? It still works: a built-in offline generator produces the roadmap, so the demo never fails.

## What's inside

| Requirement | Where |
|---|---|
| Working prototype: goal → AI roadmap | `POST /api/roadmap` in `server.js` (Claude via Anthropic API, offline fallback in `lib/fallback.js`) |
| Guided path (steps, next action, progress) | "Up next" card + staged timeline + progress ring in `public/` |
| 60-second demo | **▶ 60-second demo** button on the home screen (guided with on-screen prompts) |
| Gamification | XP, levels, daily streaks, 6 badges, confetti, feedback after each step |
| Simplicity | One input, one next step at all times; later steps are locked so nobody gets lost |

## Project structure

```
server.js          Express server + /api/roadmap + /api/health
lib/fallback.js    Offline roadmap generator (Python / Web / Data + generic)
public/index.html  UI shell
public/styles.css  Design system (dark, glassy, responsive)
public/app.js      State, rendering, XP/streak/badge logic, confetti
```

## 60-second demo script

1. Click **▶ 60-second demo** (0:00) — a Python roadmap is generated for a total beginner.
2. The "Your first step" card appears (0:10) — a 10-minute task, nothing more.
3. Open it, tap **I did it ✓**, rate how it felt (0:30).
4. XP, streak and first badge pop with confetti (0:40). The next step is already waiting.

## Notes

- Progress is saved in `localStorage`; no accounts needed.
- The API key stays on the server and is never sent to the browser.
- To change the model: `ANTHROPIC_MODEL` in `.env`.
