require("dotenv").config();
const express = require("express");
const cors = require("cors");
const path = require("path");
const { fallbackRoadmap } = require("./lib/fallback");

const app = express();
app.use(cors());
app.use(express.json({ limit: "50kb" }));
app.use(express.static(path.join(__dirname, "public")));

const MODEL = process.env.ANTHROPIC_MODEL || "claude-sonnet-4-5";

const SYSTEM = `You are a world-class learning coach. Create a clear, motivating roadmap for a learner.
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
Steps must fit the learner's daily time. Tailor depth to their level. No filler.`;

function extractJson(text) {
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start === -1 || end === -1) throw new Error("No JSON in model output");
  return JSON.parse(text.slice(start, end + 1));
}

function normalise(rm) {
  let n = 0;
  rm.stages = (rm.stages || []).map((s, si) => ({
    ...s,
    id: `s${si + 1}`,
    steps: (s.steps || []).map((st) => ({ ...st, id: `t${++n}`, minutes: Number(st.minutes) || 15 })),
  }));
  return rm;
}

async function claudeRoadmap({ skill, level, minutes, goal }) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: MODEL,
      max_tokens: 3000,
      system: SYSTEM,
      messages: [
        {
          role: "user",
          content: `Skill: ${skill}\nCurrent level: ${level}\nTime per day: ${minutes} minutes\nWhy they want it: ${goal || "not specified"}`,
        },
      ],
    }),
  });
  if (!res.ok) throw new Error(`Anthropic API ${res.status}`);
  const data = await res.json();
  return extractJson(data.content.map((c) => c.text || "").join(""));
}

app.post("/api/roadmap", async (req, res) => {
  const skill = String(req.body.skill || "").trim().slice(0, 80);
  const level = ["beginner", "some", "intermediate"].includes(req.body.level) ? req.body.level : "beginner";
  const minutes = [10, 20, 45].includes(Number(req.body.minutes)) ? Number(req.body.minutes) : 20;
  const goal = String(req.body.goal || "").trim().slice(0, 200);
  if (skill.length < 2) return res.status(400).json({ error: "Tell us what you want to learn." });

  let source = "offline";
  let roadmap;
  if (process.env.ANTHROPIC_API_KEY) {
    try {
      roadmap = await claudeRoadmap({ skill, level, minutes, goal });
      source = "claude";
    } catch (e) {
      console.warn("Claude failed, using fallback:", e.message);
    }
  }
  if (!roadmap) roadmap = fallbackRoadmap({ skill, level, minutes });
  res.json({ source, roadmap: normalise(roadmap) });
});

app.get("/api/health", (_req, res) => res.json({ ok: true, ai: !!process.env.ANTHROPIC_API_KEY }));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`PathFinder running → http://localhost:${PORT}`));
