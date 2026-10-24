// Offline roadmap generator: keeps the demo working with no API key / no internet.
const TOPICS = {
  python: {
    name: "Python",
    stages: [
      ["Get Started", "Run your first program with confidence.", [
        ["Install & say hello", "Install Python and print your first line in a REPL.", 10, "build"],
        ["Variables & types", "Create 5 variables and print them with f-strings.", 15, "learn"],
        ["Input & output", "Write a script that asks your name and greets you.", 15, "practice"],
        ["Mini win: tip calculator", "Build a bill + tip calculator in under 15 lines.", 20, "build"]]],
      ["Control Flow", "Make programs decide and repeat.", [
        ["If / else logic", "Write a number-guessing hint using if / elif / else.", 15, "learn"],
        ["Loops", "Print a multiplication table with a for loop.", 15, "practice"],
        ["Lists & dicts", "Store 5 movies with ratings in a dictionary.", 20, "learn"],
        ["Mini win: quiz game", "Build a 3-question quiz that keeps score.", 25, "build"]]],
      ["Functions & Files", "Organise code and work with real data.", [
        ["Write functions", "Refactor your quiz into 2 reusable functions.", 20, "learn"],
        ["Read a file", "Read a .txt file and count its words.", 15, "practice"],
        ["Use a library", "Fetch a random joke from a public API with requests.", 20, "learn"],
        ["Reflect", "Write 3 lines on what felt hard and what clicked.", 5, "reflect"]]],
      ["Build & Share", "Ship something you are proud of.", [
        ["Pick a project", "Choose one idea: expense tracker, to-do CLI, or quiz bot.", 10, "reflect"],
        ["Build the core", "Implement the smallest working version.", 45, "build"],
        ["Polish & test", "Add input checks and try to break it.", 25, "practice"],
        ["Share it", "Push to GitHub and write a 3-line README.", 20, "build"]]],
    ],
  },
  web: {
    name: "Web Development",
    stages: [
      ["See the Web", "Understand what a page is made of.", [
        ["Inspect any site", "Open DevTools and change a heading on a live site.", 10, "learn"],
        ["Your first HTML", "Build a page with a heading, image and link.", 15, "build"],
        ["Style with CSS", "Add colour, spacing and a font to your page.", 20, "practice"],
        ["Mini win: profile card", "Make a centred profile card with your photo.", 25, "build"]]],
      ["Layout", "Arrange things so they look professional.", [
        ["Flexbox basics", "Align 3 cards in a row with flexbox.", 20, "learn"],
        ["Grid basics", "Build a 3x2 photo grid with CSS grid.", 20, "practice"],
        ["Responsive design", "Make your layout stack on phones.", 20, "learn"],
        ["Mini win: landing page", "Build a hero + features landing page.", 30, "build"]]],
      ["Make it Interactive", "Add behaviour with JavaScript.", [
        ["JS in the browser", "Make a button change text on click.", 15, "learn"],
        ["DOM updates", "Build a to-do list that adds and removes items.", 25, "practice"],
        ["Fetch an API", "Show live data from a public API on your page.", 25, "learn"],
        ["Reflect", "Note one bug you fixed and how you found it.", 5, "reflect"]]],
      ["Ship It", "Put your work on the internet.", [
        ["Choose a project", "Pick a portfolio, weather app, or quiz site.", 10, "reflect"],
        ["Build version one", "Ship the smallest working version.", 45, "build"],
        ["Polish", "Fix spacing, add hover effects, test on mobile.", 25, "practice"],
        ["Deploy", "Publish it free on GitHub Pages or Netlify.", 20, "build"]]],
    ],
  },
  data: {
    name: "Data Science",
    stages: [
      ["Think in Data", "Get comfortable with data and questions.", [
        ["Spot the question", "Open any CSV and write 3 questions it could answer.", 10, "reflect"],
        ["Load with pandas", "Load a CSV and print its first 5 rows.", 15, "build"],
        ["Clean basics", "Find and fill or drop missing values.", 20, "practice"],
        ["Mini win: summary", "Compute mean, median and top 5 of a column.", 20, "build"]]],
      ["See the Story", "Turn numbers into visuals.", [
        ["First chart", "Plot a bar chart with matplotlib.", 15, "learn"],
        ["Compare groups", "Use groupby to compare two categories.", 20, "practice"],
        ["Correlations", "Create a heatmap and read one insight.", 20, "learn"],
        ["Mini win: dashboard", "Make a 3-chart summary of one dataset.", 30, "build"]]],
      ["Predict", "Build your first model.", [
        ["Train / test split", "Split data and explain why in one sentence.", 15, "learn"],
        ["Linear regression", "Fit a model and read its score.", 25, "practice"],
        ["Classification", "Train a decision tree on the Iris dataset.", 25, "learn"],
        ["Reflect", "Write what your model gets wrong and why.", 10, "reflect"]]],
      ["Share Insight", "Communicate what you found.", [
        ["Choose a dataset", "Pick a topic you care about from Kaggle.", 10, "reflect"],
        ["Analyse", "Answer 3 questions with charts.", 45, "build"],
        ["Model it", "Add one simple prediction.", 30, "practice"],
        ["Publish", "Write a short notebook story and share it.", 25, "build"]]],
    ],
  },
};

const GENERIC_STAGES = (s) => [
  ["Orient", `See the whole map of ${s} before you walk it.`, [
    [`What is ${s}?`, `Spend a few minutes reading a beginner overview of ${s}.`, 10, "learn"],
    ["Define your why", `Write one sentence: what will you do with ${s}?`, 5, "reflect"],
    ["Pick your tools", `List the 3 tools or materials you need to start ${s}.`, 10, "learn"],
    ["Mini win", `Complete the tiniest possible exercise in ${s}.`, 15, "practice"]]],
  ["Foundations", `Learn the core ideas everything else in ${s} builds on.`, [
    ["Core concept one", `Learn the first essential concept of ${s} and explain it aloud.`, 20, "learn"],
    ["Core concept two", `Learn the second essential concept and connect it to the first.`, 20, "learn"],
    ["Guided practice", `Follow one tutorial for ${s} end to end.`, 25, "practice"],
    ["Quick recall", `Without notes, write down what you remember.`, 10, "reflect"]]],
  ["Practice", `Move from watching to doing in ${s}.`, [
    ["Repeat with variation", `Redo your tutorial, changing one thing.`, 25, "practice"],
    ["Fix a mistake", `Find a common beginner mistake in ${s} and correct it.`, 20, "practice"],
    ["Learn from an expert", `Study one real example of excellent ${s} work.`, 20, "learn"],
    ["Mini project", `Build something small but complete in ${s}.`, 30, "build"]]],
  ["Show It", `Create proof of what you can do with ${s}.`, [
    ["Choose a project", `Pick a project that would make you proud.`, 10, "reflect"],
    ["Build version one", `Make the smallest working version.`, 45, "build"],
    ["Get feedback", `Show it to one person and note their reaction.`, 15, "reflect"],
    ["Share it", `Publish or present your work and celebrate.`, 20, "build"]]],
];

function pick(skill) {
  const k = skill.toLowerCase();
  if (/python|pandas|scripting/.test(k)) return TOPICS.python;
  if (/web|html|css|javascript|react|frontend|website/.test(k)) return TOPICS.web;
  if (/data|machine learning|\bml\b|\bai\b|analytics/.test(k)) return TOPICS.data;
  return null;
}

function fallbackRoadmap({ skill, level, minutes }) {
  const t = pick(skill);
  const name = t ? t.name : skill.replace(/\b\w/g, (c) => c.toUpperCase());
  let stages = t ? t.stages : GENERIC_STAGES(skill);

  // Respect the learner's level: skip the first stage for non-beginners.
  if (level === "intermediate") stages = stages.slice(1);
  else if (level === "some" && t) stages = stages.slice(0, 4);

  const cap = minutes;
  const out = stages.map(([title, goal, steps]) => ({
    title,
    goal,
    steps: steps.map(([stitle, action, mins, type]) => ({
      title: stitle,
      action,
      minutes: Math.min(mins, Math.max(5, Math.round(cap * 1.25))),
      type,
      hint: HINTS[type],
    })),
  }));
  const totalMin = out.flatMap((s) => s.steps).reduce((a, s) => a + s.minutes, 0);
  return {
    skill: name,
    tagline: `${out.length} stages. One small step at a time.`,
    totalWeeks: Math.max(1, Math.ceil(totalMin / (cap * 5))),
    stages: out,
  };
}

const HINTS = {
  learn: "Don't try to memorise — aim to explain it back in your own words.",
  practice: "Getting it wrong is the point. Retry once before looking anything up.",
  build: "Smaller is better. Finish something tiny rather than start something huge.",
  reflect: "Two honest sentences beat a perfect paragraph.",
};

module.exports = { fallbackRoadmap };
