"""PathFinder — Flask backend (accounts, saved progress, AI roadmaps).

Auth:      POST /api/auth/register | /login | /demo | /logout
Session:   GET  /api/me            -> {user, state}
Progress:  PUT  /api/state         -> saves the learner's progress
Content:   GET  /api/catalog       -> tech skills
           POST /api/roadmap       -> AI-generated roadmap (Claude, with offline fallback)
"""
import json
import os
import re
import sqlite3
import urllib.request

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash

from lib.quiz import clean_questions, offline_questions
from lib.content import SKILLS, attach_problems, catalog, fallback_roadmap, sheet as leetcode_sheet, topics_for, problems_for_step

load_dotenv()

BASE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE, "pathfinder.db")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")
DEMO_EMAIL, DEMO_PASSWORD = "demo@pathfinder.app", "demo1234"

app = Flask(__name__, static_folder="static", static_url_path="")
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "pathfinder-dev-secret-change-me"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=512 * 1024,
)

EMPTY_STATE = {"xp": 0, "streak": 0, "lastDay": "", "badges": [], "active": None, "paths": {}, "solved": {}}


# ---------- database ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT NOT NULL UNIQUE,
                 pw_hash TEXT NOT NULL,
                 data TEXT NOT NULL DEFAULT '{}'
               )"""
        )
        if not c.execute("SELECT 1 FROM users WHERE email=?", (DEMO_EMAIL,)).fetchone():
            c.execute(
                "INSERT INTO users (name, email, pw_hash, data) VALUES (?,?,?,?)",
                ("Demo Learner", DEMO_EMAIL, generate_password_hash(DEMO_PASSWORD), json.dumps(EMPTY_STATE)),
            )


def current_user():
    uid = session.get("uid")
    if not uid:
        return None
    return get_db().execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()


def session_payload(row):
    try:
        state = json.loads(row["data"] or "{}")
    except json.JSONDecodeError:
        state = {}
    merged = {**EMPTY_STATE, **state}
    dsa = (merged.get("paths") or {}).get("dsa")
    if isinstance(dsa, dict) and isinstance(dsa.get("roadmap"), dict):
        attach_problems(dsa["roadmap"], (dsa.get("profile") or {}).get("level", "beginner"))  # keeps problems matched to the saved level
    return {"user": {"name": row["name"], "email": row["email"]}, "state": merged}


def login_required(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(*a, **kw):
        if not current_user():
            return jsonify(error="Please sign in first."), 401
        return fn(*a, **kw)

    return wrapper


# ---------- auth ----------
@app.post("/api/auth/register")
def register():
    p = request.get_json(silent=True) or {}
    name = str(p.get("name", "")).strip()[:60]
    email = str(p.get("email", "")).strip().lower()[:120]
    password = str(p.get("password", ""))
    if len(name) < 2:
        return jsonify(error="Please enter your name."), 400
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return jsonify(error="Please enter a valid email address."), 400
    if len(password) < 6:
        return jsonify(error="Your password needs at least 6 characters."), 400
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (name, email, pw_hash, data) VALUES (?,?,?,?)",
            (name, email, generate_password_hash(password), json.dumps(EMPTY_STATE)),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify(error="An account with that email already exists."), 409
    session.clear()
    session["uid"] = cur.lastrowid
    return jsonify(session_payload(current_user()))


@app.post("/api/auth/login")
def login():
    p = request.get_json(silent=True) or {}
    email = str(p.get("email", "")).strip().lower()
    row = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row or not check_password_hash(row["pw_hash"], str(p.get("password", ""))):
        return jsonify(error="Incorrect email or password."), 401
    session.clear()
    session["uid"] = row["id"]
    return jsonify(session_payload(row))


@app.post("/api/auth/demo")
def demo():
    """Signs into the shared demo account with a fresh slate (used by the 60-second demo)."""
    db = get_db()
    db.execute("UPDATE users SET data=? WHERE email=?", (json.dumps(EMPTY_STATE), DEMO_EMAIL))
    db.commit()
    row = db.execute("SELECT * FROM users WHERE email=?", (DEMO_EMAIL,)).fetchone()
    session.clear()
    session["uid"] = row["id"]
    return jsonify(session_payload(row))


@app.post("/api/auth/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/me")
def me():
    row = current_user()
    if not row:
        return jsonify(user=None)
    return jsonify(session_payload(row))


@app.put("/api/state")
@login_required
def save_state():
    p = request.get_json(silent=True)
    if not isinstance(p, dict):
        return jsonify(error="Invalid state."), 400
    clean = {k: p[k] for k in EMPTY_STATE if k in p}
    blob = json.dumps(clean)
    if len(blob) > 300_000:
        return jsonify(error="State too large."), 413
    db = get_db()
    db.execute("UPDATE users SET data=? WHERE id=?", (blob, session["uid"]))
    db.commit()
    return jsonify(ok=True)


# ---------- content ----------
@app.get("/api/catalog")
def get_catalog():
    return jsonify(catalog())


SYSTEM = """You are a world-class technology mentor. Create a clear, calm, motivating learning roadmap
for a student learning ONE technical skill. Return ONLY valid JSON (no markdown) with this exact shape:
{
  "skill": string,
  "tagline": string (max 90 chars),
  "totalWeeks": number,
  "stages": [
    {
      "title": string (2-4 words, a "world" name),
      "goal": string (one sentence outcome),
      "steps": [
        { "title": string (max 6 words), "action": string (one concrete sentence starting with a verb),
          "minutes": number, "type": "learn" | "practice" | "build" | "reflect", "hint": string (a friendly tip) }
      ]
    }
  ]
}
Rules: exactly 4 stages with 4 steps each. The very first step must be tiny (<=10 minutes) and instantly doable.
The LAST step of every stage is a small milestone project that starts with "Milestone:".
Steps must fit the learner's daily time. Tailor depth AND difficulty to their level: for \"pro\" learners skip basics entirely and use advanced, interview-grade material; for \"beginner\" go slowly with small wins. Be specific and practical. No filler."""


def extract_json(text):
    a, b = text.find("{"), text.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("No JSON in model output")
    return json.loads(text[a:b + 1])


GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def provider():
    """Which AI is configured: 'anthropic', 'gemini' (free key from Google AI Studio) or None."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.getenv("GEMINI_API_KEY"):
        return "gemini"
    return None


def ask_gemini(system, user, max_tokens, timeout):
    base = os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com").rstrip("/")
    body = json.dumps({
        "systemInstruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": max_tokens * 2, "temperature": 0.7},
    }).encode()
    req = urllib.request.Request(
        f"{base}/v1beta/models/{GEMINI_MODEL}:generateContent",
        data=body,
        headers={"content-type": "application/json", "x-goog-api-key": os.environ["GEMINI_API_KEY"]},
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        data = json.load(res)
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


def ask_claude(system, user, max_tokens=1000, timeout=40):
    """Ask the configured AI (Claude or Gemini). Keys stay on the server, never reach the browser."""
    if provider() == "gemini":
        return ask_gemini(system, user, max_tokens, timeout)
    body = json.dumps({
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }).encode()
    req = urllib.request.Request(
        os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as res:
        data = json.load(res)
    return "".join(c.get("text", "") for c in data["content"])


def claude_roadmap(name, level, minutes, goal="", weak=(), strong=()):
    msg = f"Skill: {name}\nCurrent level: {level}\nTime per day: {minutes} minutes"
    if weak:
        msg += "\nWEAK topics (give each extra levels, start gentler, add a drill): " + "; ".join(weak)
    if strong:
        msg += "\nALREADY STRONG topics (skip them or keep one quick check): " + "; ".join(strong)
    if goal:
        msg += f"\nThe learner's own goal (tailor the worlds and milestones to it): {goal}"
    return extract_json(ask_claude(SYSTEM, msg, max_tokens=3500, timeout=45))


COACH_SYSTEM = """You are a friendly, concise tech mentor inside a gamified learning app.
The learner is on one level of a roadmap. Answer their question in at most 120 words, plain language,
with one tiny example if it helps. If they ask for the answer to a LeetCode problem, give a hint and the idea, not full code.
No markdown headings."""


def normalise(rm):
    n = 0
    stages = []
    for si, stage in enumerate(rm.get("stages") or []):
        steps = []
        for st in stage.get("steps") or []:
            n += 1
            try:
                minutes = int(st.get("minutes") or 15)
            except (TypeError, ValueError):
                minutes = 15
            typ = st.get("type") if st.get("type") in ("learn", "practice", "build", "reflect") else "learn"
            steps.append({**st, "type": typ, "id": f"t{n}", "minutes": minutes})
        stages.append({**stage, "id": f"s{si + 1}", "steps": steps})
    rm["stages"] = stages
    return rm


@app.post("/api/roadmap")
@login_required
def roadmap():
    p = request.get_json(silent=True) or {}
    key = str(p.get("skill", ""))
    if key not in SKILLS:
        return jsonify(error="Please choose one of the tech skills."), 400
    level = p.get("level") if p.get("level") in ("beginner", "some", "intermediate", "pro") else "beginner"
    try:
        minutes = int(p.get("minutes", 20))
    except (TypeError, ValueError):
        minutes = 20
    if minutes not in (10, 20, 45):
        minutes = 20

    goal = re.sub(r"\s+", " ", str(p.get("goal", ""))).strip()[:200]

    def names(v):
        v = v if isinstance(v, list) else []
        return [re.sub(r"\s+", " ", x).strip()[:80] for x in v if isinstance(x, str) and x.strip()][:30]
    weak, strong = names(p.get("weak")), names(p.get("strong"))

    source, rm = "offline", None
    if provider():
        try:
            rm = claude_roadmap(SKILLS[key]["name"], level, minutes, goal, weak, strong)
            if len(rm.get("stages") or []) < 2:
                raise ValueError("Too few stages")
            source = "claude"
        except Exception as e:  # network error, bad JSON, API error -> offline generator
            print("Claude failed, using offline generator:", e)
            rm = None
    if rm is None:
        rm = fallback_roadmap(key, level, minutes, weak, strong)
        if goal:
            rm["tagline"] = f"Your goal: {goal}"[:90]
    rm = normalise(rm)
    if key == "dsa":
        attach_problems(rm, level)
    return jsonify(source=source, roadmap=rm)


@app.post("/api/coach")
@login_required
def coach():
    p = request.get_json(silent=True) or {}
    question = str(p.get("question", "")).strip()[:400]
    if not question:
        return jsonify(error="Type a question first."), 400
    skill = str(p.get("skill", ""))[:60]
    title = str(p.get("title", ""))[:120]
    action = str(p.get("action", ""))[:300]
    hint = str(p.get("hint", ""))[:300]
    if provider():
        try:
            ans = ask_claude(COACH_SYSTEM, f"Skill: {skill}\nLevel title: {title}\nTask: {action}\nLearner question: {question}",
                             max_tokens=400, timeout=30).strip()
            if ans:
                return jsonify(answer=ans, source="claude")
        except Exception as e:
            print("Claude coach failed, using offline answer:", e)
    ans = (f"Here is a way in. {action} {hint} Break it into the smallest piece you can finish in five minutes, "
           "do that piece, then come back and ask again. (Offline coach: add a free GEMINI_API_KEY to .env for live AI answers.)")
    return jsonify(answer=ans.strip(), source="offline")


QUIZ_SYSTEM = """You write short multiple-choice quizzes for a gamified tech-learning app.
Return ONLY a JSON array (no markdown). Each item: {"topic": string, "q": string (max 200 chars), "options": [4 short strings],
"answer": number (0-3, index of the correct option), "explain": string (one sentence why)}.
Exactly one option is correct. Make wrong options plausible. Match the difficulty to the learner's level."""


@app.post("/api/quiz")
@login_required
def quiz():
    p = request.get_json(silent=True) or {}
    key = str(p.get("skill", ""))
    if key not in SKILLS:
        return jsonify(error="Unknown skill."), 400
    level = p.get("level") if p.get("level") in ("beginner", "some", "intermediate", "pro") else "beginner"
    mode = "level" if p.get("mode") == "level" else "diagnostic"
    topics = [t for w in topics_for(key, level) for t in w["topics"]]
    if mode == "level":
        title = str(p.get("title", ""))[:120]
        action = str(p.get("action", ""))[:300]
        n, ask = 3, f"Skill: {SKILLS[key]['name']}\nLearner level: {level}\nWrite 3 questions that check this lesson.\nLesson: {title}. {action}\nUse topic: {title}"
    else:
        n, ask = 6, (f"Skill: {SKILLS[key]['name']}\nLearner level: {level}\nWrite 6 diagnostic questions, one per topic, for DIFFERENT topics. "
                     f"The topic field must be copied exactly from this list: {'; '.join(topics)}")
    if provider():
        try:
            qs = clean_questions(ask_claude(QUIZ_SYSTEM, ask, max_tokens=1800, timeout=40), topics + ([str(p.get('title', ''))] if mode == "level" else []), n)
            if len(qs) >= 2:
                return jsonify(questions=qs, source="ai")
        except Exception as e:
            print("AI quiz failed:", e)
    if mode == "diagnostic":
        qs = offline_questions(key, topics, n)
        if qs:
            return jsonify(questions=qs, source="offline")
    return jsonify(error="The quiz needs the AI key for this skill. Add GEMINI_API_KEY to .env, or pick your weak topics by hand."), 503


@app.post("/api/adapt")
@login_required
def adapt():
    """Adaptive difficulty: build one extra level after a weak (1 star) or strong (3 star) result."""
    p = request.get_json(silent=True) or {}
    key = str(p.get("skill", ""))
    if key not in SKILLS:
        return jsonify(error="Unknown skill."), 400
    level = p.get("level") if p.get("level") in ("beginner", "some", "intermediate", "pro") else "beginner"
    easier = p.get("direction") != "harder"
    title = re.sub(r"^(Revisit|Challenge): ", "", str(p.get("title", ""))[:100])
    action = str(p.get("action", ""))[:300]
    if easier:
        step = {"title": f"Revisit: {title}", "type": "practice", "minutes": 15, "weak": True,
                "action": f"Go back over {title.lower()} in smaller pieces and redo one example from scratch.",
                "hint": "Slow is fine. Fix one mistake at a time."}
    else:
        step = {"title": f"Challenge: {title}", "type": "build", "minutes": 25,
                "action": f"Push {title.lower()} further with a harder problem and no notes.",
                "hint": "Time yourself, then explain your solution out loud."}
    if provider():
        try:
            txt = ask_claude("You write one concrete learning task sentence, starting with a verb, max 25 words. No markdown.",
                             f"Skill: {SKILLS[key]['name']}\nLesson just completed: {title} ({action})\nWrite a {'simpler, step by step revision' if easier else 'harder stretch'} task for it.",
                             max_tokens=120, timeout=20).strip().strip('"')
            if 8 < len(txt) < 260:
                step["action"] = txt
        except Exception as e:
            print("AI adapt failed, using template:", e)
    if key == "dsa":
        lv = level if easier else {"beginner": "some", "some": "intermediate", "intermediate": "pro"}.get(level, level)
        step["problems"] = problems_for_step({"title": title, "action": action, "weak": easier}, lv)
    return jsonify(step=step)


@app.get("/api/topics")
def get_topics():
    key = request.args.get("skill", "")
    if key not in SKILLS:
        return jsonify(error="Unknown skill."), 400
    lv = request.args.get("level", "beginner")
    return jsonify(topics_for(key, lv if lv in ("beginner", "some", "intermediate", "pro") else "beginner"))


@app.get("/api/sheet")
def get_sheet():
    lv = request.args.get("level", "beginner")
    return jsonify(leetcode_sheet(lv if lv in ("beginner", "some", "intermediate", "pro") else "beginner"))


@app.get("/api/health")
def health():
    return jsonify(ok=True, ai=bool(provider()), provider=provider(), model=GEMINI_MODEL if provider() == "gemini" else MODEL)


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


init_db()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    print(f"PathFinder running -> http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
