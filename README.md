# PathFinder (Python / Flask) — AI learning roadmaps that feel easy

Pick a goal → get an AI-generated roadmap → take one clear next step → get rewarded.

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

Then open **http://localhost:3000** in your browser.

Optional: copy `.env.example` to `.env` and add `ANTHROPIC_API_KEY` to have Claude generate the roadmaps.
Without a key, the built-in offline generator is used, so the demo always works.

## Structure

```
app.py             Flask server: /api/roadmap, /api/health, serves the UI
lib/fallback.py    Offline roadmap generator (Python / Web / Data + generic)
static/index.html  UI
static/styles.css  Design system
static/app.js      Progress, XP, streaks, badges, confetti
```

## 60-second demo

Click **▶ 60-second demo** on the home screen: roadmap → first step → "I did it" → XP, streak, badge, confetti.
