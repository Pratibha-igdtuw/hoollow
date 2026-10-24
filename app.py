"""PathFinder — Flask backend.

POST /api/roadmap  -> AI-generated learning roadmap (Claude, with offline fallback)
GET  /api/health   -> {"ok": true, "ai": bool}
Everything else is served from ./static (the UI).
"""
import json
import os
import urllib.request

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

from lib.fallback import fallback_roadmap

load_dotenv()

app = Flask(__name__, static_folder="static", static_url_path="")
MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

SYSTEM = """You are a world-class learning coach. Create a clear, motivating roadmap for a learner.
Return ONLY valid JSON (no markdown) with this exact shape:
{
  "skill": string,
  "tagline": string (max 90 chars, encouraging),
  "totalWeeks": number,
  "stages": [
    {
      "title": string (2-4 words),
      "goal": string (one sentence outcome),
      "steps": [
        { "title": string (max 6 words), "action": string (one concrete sentence starting with a verb),
          "minutes": number, "type": "learn" | "practice" | "build" | "reflect", "hint": string (a friendly tip) }
      ]
    }
  ]
}
Rules: 4 stages, 4 steps each. The very first step must be tiny (<=10 minutes) and instantly doable.
Steps must fit the learner's daily time. Tailor depth to their level. No filler."""


def extract_json(text):
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON in model output")
    return json.loads(text[start:end + 1])


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
            steps.append({**st, "id": f"t{n}", "minutes": minutes})
        stages.append({**stage, "id": f"s{si + 1}", "steps": steps})
    rm["stages"] = stages
    return rm


def claude_roadmap(skill, level, minutes, goal):
    body = json.dumps({
        "model": MODEL,
        "max_tokens": 3000,
        "system": SYSTEM,
        "messages": [{
            "role": "user",
            "content": f"Skill: {skill}\nCurrent level: {level}\nTime per day: {minutes} minutes\n"
                       f"Why they want it: {goal or 'not specified'}",
        }],
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


@app.post("/api/roadmap")
def roadmap():
    payload = request.get_json(silent=True) or {}
    skill = str(payload.get("skill", "")).strip()[:80]
    level = payload.get("level") if payload.get("level") in ("beginner", "some", "intermediate") else "beginner"
    try:
        minutes = int(payload.get("minutes", 20))
    except (TypeError, ValueError):
        minutes = 20
    if minutes not in (10, 20, 45):
        minutes = 20
    goal = str(payload.get("goal", "")).strip()[:200]
    if len(skill) < 2:
        return jsonify(error="Tell us what you want to learn."), 400

    source, rm = "offline", None
    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            rm = claude_roadmap(skill, level, minutes, goal)
            source = "claude"
        except Exception as e:  # network error, bad JSON, API error -> fall back
            print("Claude failed, using fallback:", e)
    if rm is None:
        rm = fallback_roadmap(skill, level, minutes)
    return jsonify(source=source, roadmap=normalise(rm))


@app.get("/api/health")
def health():
    return jsonify(ok=True, ai=bool(os.getenv("ANTHROPIC_API_KEY")))


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "3000"))
    print(f"PathFinder running -> http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
