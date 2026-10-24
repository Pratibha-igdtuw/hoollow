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

from lib.content import SKILLS, attach_problems, catalog, fallback_roadmap, sheet as leetcode_sheet

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
        attach_problems(dsa["roadmap"])  # older saved DSA paths get the LeetCode sheet too
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
Steps must fit the learner's daily time. Tailor depth to their level. Be specific and practical. No filler."""


def extract_json(text):
    a, b = text.find("{"), text.rfind("}")
    if a == -1 or b == -1:
        raise ValueError("No JSON in model output")
    return json.loads(text[a:b + 1])


def claude_roadmap(name, level, minutes):
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 3500,
        "system": SYSTEM,
        "messages": [{"role": "user", "content":
                      f"Skill: {name}\nCurrent level: {level}\nTime per day: {minutes} minutes"}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body,
        headers={
            "content-type": "application/json",
            "x-api-key": os.environ["ANTHROPIC_API_KEY"],
            "anthropic-version": "2023-06-01",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as res:
        data = json.load(res)
    return extract_json("".join(c.get("text", "") for c in data["content"]))


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
    level = p.get("level") if p.get("level") in ("beginner", "some", "intermediate") else "beginner"
    try:
        minutes = int(p.get("minutes", 20))
    except (TypeError, ValueError):
        minutes = 20
    if minutes not in (10, 20, 45):
        minutes = 20

    source, rm = "offline", None
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            rm = claude_roadmap(SKILLS[key]["name"], level, minutes)
            if len(rm.get("stages") or []) < 2:
                raise ValueError("Too few stages")
            source = "claude"
        except Exception as e:  # network error, bad JSON, API error -> offline generator
            print("Claude failed, using offline generator:", e)
            rm = None
    if rm is None:
        rm = fallback_roadmap(key, level, minutes)
    rm = normalise(rm)
    if key == "dsa":
        attach_problems(rm)
    return jsonify(source=source, roadmap=rm)


@app.get("/api/sheet")
def get_sheet():
    return jsonify(leetcode_sheet())


@app.get("/api/health")
def health():
    return jsonify(ok=True, ai=bool(os.getenv("ANTHROPIC_API_KEY")))


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


init_db()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    print(f"PathFinder running -> http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
