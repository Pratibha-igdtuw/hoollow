# PathFinder — learn technology, one clear level at a time

Intro page → sign in → choose a tech skill → get an AI roadmap → play it as a level map with stars, XP, streaks and badges.

## Run it (Windows)

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open **http://localhost:3000** (not the Live Server port).
Mac/Linux: use `source venv/bin/activate` instead of the activate line above.

Optional: copy `.env.example` to `.env` and add `ANTHROPIC_API_KEY` so Claude writes each roadmap.
Without a key, hand-written offline roadmaps are used, so the demo always works.

## The flow

1. **Intro page** — what PathFinder is, how it works, the skills, a preview of the level map.
2. **Sign in / Create account** — real accounts (SQLite, hashed passwords). Progress is saved per user.
3. **Skills** — 9 tech skills: Python, Java, DSA, Web Development, SQL, Data Science, Machine Learning, Cybersecurity, Cloud & DevOps.
4. **Level map** — 4 worlds x 4 levels. Only the next level is open. The last level in each world is a crowned milestone project.
5. **Play a level** — read the step, do it, rate how it went (1 to 3 stars), earn XP, keep your streak, unlock badges.

## 60-second demo

Click **Watch the 60-second demo** on the intro page (or on the sign-in page). It signs in as a ready-made demo account,
builds a Python roadmap, and a small guide walks you through your first level.
Demo account: `demo@pathfinder.app` / `demo1234`.

## Structure

```
app.py               Flask server: auth, saved progress, catalog, roadmap API
lib/content.py       Tech skill catalog + offline roadmaps
static/index.html    App shell
static/css/styles.css  Design system (calm paper-and-sage palette)
static/js/app.js     Router, views, level map, gamification, confetti
pathfinder.db        Created on first run (SQLite)
```

## Notes

- The API key stays on the server.
- Fonts load from Google Fonts; offline, the page falls back to system fonts.
