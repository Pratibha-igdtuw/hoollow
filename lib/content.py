"""Tech-only skill catalog + offline roadmap generator.

Every skill has 4 worlds (stages) x 4 levels (steps). The last level of each world is a
milestone project. Each step is (title, action, minutes, type).
"""
import math

HINTS = {
    "learn": "Don't try to memorise it. Aim to explain it back in your own words.",
    "practice": "Getting it wrong is part of it. Retry once before you look anything up.",
    "build": "Keep it small. Finish something tiny rather than start something huge.",
    "reflect": "Two honest sentences beat a perfect paragraph.",
}

SKILLS = {
    "python": {
        "name": "Python", "tag": "Py",
        "blurb": "From your first script to a real project.",
        "stages": [
            ("Getting Started", "Run your first program with confidence.", [
                ("Install and say hello", "Install Python and print your first line in the REPL.", 10, "build"),
                ("Variables and types", "Create five variables and print them with f-strings.", 15, "learn"),
                ("Input and output", "Write a script that asks for your name and greets you.", 15, "practice"),
                ("Milestone: tip calculator", "Build a bill and tip calculator in under 15 lines.", 20, "build")]),
            ("Control Flow", "Make programs decide and repeat.", [
                ("If, elif, else", "Write a number-guessing hint using conditions.", 15, "learn"),
                ("Loops", "Print a multiplication table with a for loop.", 15, "practice"),
                ("Lists and dictionaries", "Store five movies with ratings in a dictionary.", 20, "learn"),
                ("Milestone: quiz game", "Build a three-question quiz that keeps score.", 25, "build")]),
            ("Functions and Files", "Organise code and work with real data.", [
                ("Write functions", "Refactor your quiz into two reusable functions.", 20, "learn"),
                ("Read a file", "Read a text file and count its words.", 15, "practice"),
                ("Use a library", "Fetch a random joke from a public API with requests.", 20, "learn"),
                ("Milestone: word counter", "Build a tool that lists the ten most common words in a file.", 30, "build")]),
            ("Build and Share", "Ship something you are proud of.", [
                ("Pick a project", "Choose one idea: expense tracker, to-do CLI or quiz bot.", 10, "reflect"),
                ("Build the core", "Implement the smallest working version.", 45, "build"),
                ("Polish and test", "Add input checks and try to break it.", 25, "practice"),
                ("Milestone: ship it", "Push to GitHub with a three-line README.", 20, "build")]),
        ]},
    "java": {
        "name": "Java", "tag": "Jv",
        "blurb": "Object-oriented programming, done properly.",
        "stages": [
            ("Java Basics", "Write and run your first Java programs.", [
                ("Install the JDK", "Install the JDK and run Hello World from the terminal.", 10, "build"),
                ("Types and Scanner", "Read a number from the user and print its square.", 15, "learn"),
                ("Conditions and loops", "Solve FizzBuzz with a loop and if statements.", 15, "practice"),
                ("Milestone: calculator", "Build a console calculator with a menu.", 25, "build")]),
            ("Object-Oriented Thinking", "Model the real world with classes.", [
                ("Classes and objects", "Model a Student class with fields and methods.", 20, "learn"),
                ("Encapsulation", "Add constructors, private fields and getters.", 20, "learn"),
                ("Inheritance", "Create a Shape hierarchy with Circle and Rectangle.", 25, "practice"),
                ("Milestone: library system", "Build a small library with Book, Member and Library classes.", 35, "build")]),
            ("Collections and Errors", "Handle data and failures safely.", [
                ("ArrayList and HashMap", "Store and look up students by roll number.", 20, "learn"),
                ("Exceptions", "Catch bad input with try and catch.", 15, "practice"),
                ("File I/O", "Read lines from a text file and print them.", 20, "practice"),
                ("Milestone: contact book", "Build a contact book that saves to a file.", 35, "build")]),
            ("Project", "Put it all together.", [
                ("Pick a project", "Choose a bank, inventory or quiz system.", 10, "reflect"),
                ("Design the classes", "Sketch the classes and relationships on paper.", 20, "learn"),
                ("Build the core", "Implement the main flow end to end.", 45, "build"),
                ("Milestone: ship it", "Test it, tidy it and push it to GitHub.", 25, "build")]),
        ]},
    "dsa": {
        "name": "Data Structures and Algorithms", "tag": "DS",
        "blurb": "Problem solving for interviews and exams.",
        "stages": [
            ("Foundations", "Learn to measure and reason about code.", [
                ("Big-O in plain words", "Explain O(1), O(n) and O(n squared) with an example each.", 15, "learn"),
                ("Arrays and two pointers", "Reverse an array in place using two pointers.", 20, "practice"),
                ("Strings", "Check whether two strings are anagrams.", 20, "practice"),
                ("Milestone: three easy problems", "Solve three easy array problems without hints.", 30, "build")]),
            ("Linear Structures", "Stacks, queues and linked lists.", [
                ("Linked list", "Build a singly linked list from scratch.", 25, "learn"),
                ("Stacks", "Check valid parentheses with a stack.", 20, "practice"),
                ("Queues and sliding window", "Find the max sum of k consecutive elements.", 25, "practice"),
                ("Milestone: browser history", "Implement back and forward navigation with two stacks.", 30, "build")]),
            ("Searching and Recursion", "Divide problems into smaller ones.", [
                ("Binary search", "Implement binary search and explain why it is fast.", 20, "learn"),
                ("Recursion", "Write factorial and Fibonacci recursively.", 20, "practice"),
                ("Merge sort", "Sort a small list by hand, then in code.", 25, "learn"),
                ("Milestone: three medium problems", "Solve three medium problems using search or recursion.", 40, "build")]),
            ("Trees and Graphs", "Work with connected data.", [
                ("Tree traversals", "Print a binary tree in preorder, inorder and postorder.", 25, "learn"),
                ("Hash maps", "Solve Two Sum in linear time.", 20, "practice"),
                ("BFS and DFS", "Count islands on a grid using BFS or DFS.", 30, "learn"),
                ("Milestone: mock interview", "Solve two problems in 45 minutes, out loud.", 45, "build")]),
        ]},
    "web": {
        "name": "Web Development", "tag": "Web",
        "blurb": "HTML, CSS, JavaScript and shipping a real site.",
        "stages": [
            ("See the Web", "Understand what a page is made of.", [
                ("Inspect any site", "Open DevTools and change a heading on a live site.", 10, "learn"),
                ("Your first HTML", "Build a page with a heading, image and link.", 15, "build"),
                ("Style with CSS", "Add colour, spacing and a font to your page.", 20, "practice"),
                ("Milestone: profile card", "Make a centred profile card with your photo.", 25, "build")]),
            ("Layout", "Arrange things so they look professional.", [
                ("Flexbox", "Align three cards in a row with flexbox.", 20, "learn"),
                ("CSS Grid", "Build a 3 by 2 photo grid.", 20, "practice"),
                ("Responsive design", "Make your layout stack neatly on a phone.", 20, "learn"),
                ("Milestone: landing page", "Build a hero section with a features grid.", 30, "build")]),
            ("Make It Interactive", "Add behaviour with JavaScript.", [
                ("JavaScript in the browser", "Make a button change text when clicked.", 15, "learn"),
                ("The DOM", "Build a to-do list that adds and removes items.", 25, "practice"),
                ("Fetch an API", "Show live data from a public API on your page.", 25, "learn"),
                ("Milestone: quiz page", "Build an interactive quiz with a score.", 35, "build")]),
            ("Ship It", "Put your work on the internet.", [
                ("Choose a project", "Pick a portfolio, weather app or quiz site.", 10, "reflect"),
                ("Build version one", "Ship the smallest working version.", 45, "build"),
                ("Polish", "Fix spacing, add hover states, test on mobile.", 25, "practice"),
                ("Milestone: deploy", "Publish it free on GitHub Pages or Netlify.", 20, "build")]),
        ]},
    "sql": {
        "name": "SQL and Databases", "tag": "SQL",
        "blurb": "Ask better questions of your data.",
        "stages": [
            ("Reading Data", "Pull the answers out of tables.", [
                ("Tables, rows and keys", "Describe a students table: columns, rows and the primary key.", 10, "learn"),
                ("Run your first query", "Open SQLite or an online sandbox and run a SELECT.", 15, "build"),
                ("Filter and sort", "Use WHERE, ORDER BY and LIMIT on a movies table.", 15, "practice"),
                ("Milestone: five questions", "Answer five questions about a movies dataset.", 25, "build")]),
            ("Combining Data", "Join tables and summarise them.", [
                ("Joins", "Write an INNER JOIN and a LEFT JOIN and compare results.", 25, "learn"),
                ("GROUP BY", "Count orders per customer with aggregates.", 20, "practice"),
                ("Subqueries and CTEs", "Rewrite a subquery as a CTE.", 25, "learn"),
                ("Milestone: sales report", "Build a report across three related tables.", 35, "build")]),
            ("Designing Databases", "Structure data so it stays correct.", [
                ("Normalisation", "Split one messy table into clean related tables.", 20, "learn"),
                ("Constraints and keys", "Create tables with primary and foreign keys.", 20, "practice"),
                ("Safe changes", "Use a transaction to insert, update and roll back.", 20, "practice"),
                ("Milestone: library schema", "Design a schema for a library app and load sample data.", 35, "build")]),
            ("Speed and Real Use", "Make it fast and use it from code.", [
                ("Indexes", "Compare a query with and without an index using EXPLAIN.", 20, "learn"),
                ("Window functions", "Rank rows and compute a running total.", 25, "learn"),
                ("SQL from Python", "Query your database from Python with sqlite3.", 25, "practice"),
                ("Milestone: query CLI", "Build a small command-line tool that queries your database.", 40, "build")]),
        ]},
    "data": {
        "name": "Data Science", "tag": "Da",
        "blurb": "Pandas, charts and the story in the numbers.",
        "stages": [
            ("Think in Data", "Get comfortable with data and questions.", [
                ("Spot the question", "Open any CSV and write three questions it could answer.", 10, "reflect"),
                ("Load with pandas", "Load a CSV and print its first five rows.", 15, "build"),
                ("Clean the basics", "Find and handle missing values.", 20, "practice"),
                ("Milestone: summary", "Compute mean, median and the top five of a column.", 20, "build")]),
            ("See the Story", "Turn numbers into visuals.", [
                ("Your first chart", "Plot a bar chart with matplotlib.", 15, "learn"),
                ("Compare groups", "Use groupby to compare two categories.", 20, "practice"),
                ("Correlations", "Draw a heatmap and write down one insight.", 20, "learn"),
                ("Milestone: mini dashboard", "Make a three-chart summary of one dataset.", 30, "build")]),
            ("Predict", "Build your first model.", [
                ("Train and test split", "Split the data and explain why in one sentence.", 15, "learn"),
                ("Linear regression", "Fit a model and read its score.", 25, "practice"),
                ("Classification", "Train a decision tree on the Iris dataset.", 25, "learn"),
                ("Milestone: compare models", "Compare two models and say which is better and why.", 30, "build")]),
            ("Share Insight", "Communicate what you found.", [
                ("Choose a dataset", "Pick a topic you care about from Kaggle.", 10, "reflect"),
                ("Analyse it", "Answer three questions with charts.", 45, "build"),
                ("Model it", "Add one simple prediction.", 30, "practice"),
                ("Milestone: publish", "Write a short notebook story and share it.", 25, "build")]),
        ]},
    "ml": {
        "name": "Machine Learning", "tag": "ML",
        "blurb": "Train and evaluate your first models honestly.",
        "stages": [
            ("Ground Rules", "Know what you are building and why.", [
                ("What is ML", "Explain supervised and unsupervised learning with one example each.", 10, "learn"),
                ("Set up your tools", "Install Python, NumPy and pandas and run a notebook.", 15, "build"),
                ("Explore a dataset", "Identify the features and the label in a dataset.", 20, "practice"),
                ("Milestone: clean the data", "Clean the Titanic dataset ready for modelling.", 30, "build")]),
            ("First Models", "Train, predict, measure.", [
                ("Train and test split", "Split data and explain why you must.", 15, "learn"),
                ("Linear regression", "Fit a regression and read the coefficients.", 25, "practice"),
                ("Classification", "Train a logistic regression or decision tree.", 25, "practice"),
                ("Milestone: house prices", "Predict house prices and report your error.", 35, "build")]),
            ("Doing It Honestly", "Avoid fooling yourself.", [
                ("Overfitting", "Show overfitting on a deep tree and fix it with cross-validation.", 20, "learn"),
                ("Metrics", "Compute accuracy, precision and recall and say what each means.", 20, "learn"),
                ("Feature engineering", "Create two new features and test if they help.", 25, "practice"),
                ("Milestone: prove it", "Improve your model and justify it with metrics.", 40, "build")]),
            ("Beyond the Basics", "A first look at neural networks.", [
                ("Neural network intuition", "Explain neurons, layers and training in plain words.", 20, "learn"),
                ("Train on MNIST", "Train a small network on MNIST with Keras or PyTorch.", 35, "practice"),
                ("Pick a project", "Choose a dataset and a question you care about.", 10, "reflect"),
                ("Milestone: publish", "Publish a notebook that explains your results.", 45, "build")]),
        ]},
    "cyber": {
        "name": "Cybersecurity", "tag": "Sec",
        "blurb": "Understand attacks so you can defend well.",
        "stages": [
            ("Security Mindset", "Learn the vocabulary and the basics.", [
                ("CIA triad", "Explain confidentiality, integrity and availability with examples.", 15, "learn"),
                ("How the web works", "Trace a request through DNS, HTTP and TLS.", 20, "learn"),
                ("Passwords done right", "Hash a password with bcrypt and see why plain text fails.", 20, "practice"),
                ("Milestone: audit yourself", "Turn on two-factor authentication and set up a password manager.", 20, "build")]),
            ("Web Security", "Find and fix common weaknesses.", [
                ("OWASP Top 10", "Summarise five of the OWASP Top 10 in your own words.", 20, "learn"),
                ("SQL injection", "Fix an injectable query in a practice app using parameters.", 25, "practice"),
                ("Cross-site scripting", "Prevent XSS in a practice app by escaping output.", 25, "practice"),
                ("Milestone: login review", "Review a small login page against a security checklist.", 35, "build")]),
            ("Systems and Networks", "Secure the machines under your code.", [
                ("Linux permissions", "Explain file permissions and set them correctly.", 20, "learn"),
                ("Watch your own traffic", "Capture your own browser traffic in Wireshark and read it.", 25, "practice"),
                ("Least privilege", "Describe how firewalls and least privilege reduce risk.", 20, "learn"),
                ("Milestone: harden a VM", "Harden a fresh Linux VM using a checklist.", 40, "build")]),
            ("Practise Safely", "Learn in legal, safe labs.", [
                ("Set up a lab", "Create a TryHackMe or OverTheWire account.", 15, "build"),
                ("Beginner room", "Complete one beginner room end to end.", 40, "practice"),
                ("Incident response", "Learn the steps: detect, contain, recover, review.", 20, "learn"),
                ("Milestone: security report", "Write a one-page report of what you found and fixed.", 35, "build")]),
        ]},
    "cloud": {
        "name": "Cloud and DevOps", "tag": "Cl",
        "blurb": "Git, containers and shipping software.",
        "stages": [
            ("Command Line and Git", "The daily tools of every engineer.", [
                ("Terminal essentials", "Navigate, create and search files from the command line.", 15, "learn"),
                ("Git basics", "Init a repo, commit and create a branch.", 20, "practice"),
                ("GitHub", "Push a repo and open a pull request.", 20, "practice"),
                ("Milestone: first PR", "Fix a README on any open-source project with a pull request.", 25, "build")]),
            ("Containers", "Package software so it runs anywhere.", [
                ("Why Docker", "Explain images and containers in two sentences.", 10, "learn"),
                ("Run a container", "Run your first container and expose a port.", 15, "build"),
                ("Write a Dockerfile", "Write a Dockerfile for a small app.", 25, "practice"),
                ("Milestone: containerise", "Containerise a Python or Node app.", 35, "build")]),
            ("Cloud Basics", "Run things on someone else's computers.", [
                ("Cloud concepts", "Explain regions, IAM, compute and storage.", 20, "learn"),
                ("Safe account setup", "Create a free-tier account and set a billing alert first.", 15, "build"),
                ("Host a static site", "Deploy a static website to cloud storage.", 25, "practice"),
                ("Milestone: deploy a container", "Deploy your container to a managed cloud service.", 40, "build")]),
            ("Automate", "Let the machines do the repetitive work.", [
                ("CI and CD", "Explain continuous integration and delivery with an example.", 15, "learn"),
                ("GitHub Actions", "Run your tests automatically on every push.", 30, "practice"),
                ("Logs and alerts", "Read logs and set up one basic alert.", 20, "learn"),
                ("Milestone: full pipeline", "Push code and watch it test and deploy itself.", 45, "build")]),
        ]},
}


def catalog():
    return [
        {"key": k, "name": v["name"], "tag": v["tag"], "blurb": v["blurb"],
         "levels": sum(len(s[2]) for s in v["stages"])}
        for k, v in SKILLS.items()
    ]


# Advanced worlds for learners who already solve Mediums comfortably (level "pro").
SKILLS["dsa"]["pro_stages"] = [
    ("Dynamic Programming", "Spot the state and write the recurrence before any code.", [
        ("1D DP patterns", "Solve House Robber and Coin Change, writing the recurrence on paper first.", 25, "practice"),
        ("2D DP and grids", "Solve Unique Paths and Longest Common Subsequence by filling a table.", 30, "practice"),
        ("Knapsack and subsequences", "Solve Partition Equal Subset Sum and Longest Increasing Subsequence.", 35, "practice"),
        ("Milestone: five DP problems", "Solve five mixed problems, 25 minutes each, and note which pattern each one used.", 45, "build"),
    ]),
    ("Advanced Graphs", "Pick the right graph algorithm in under a minute.", [
        ("Shortest paths", "Implement Dijkstra with a heap and solve Network Delay Time.", 30, "practice"),
        ("Union find", "Build a union-find with path compression and solve Redundant Connection.", 25, "practice"),
        ("Topological sort", "Order tasks with dependencies using Kahn's algorithm and solve Course Schedule II.", 25, "practice"),
        ("Milestone: graph contest", "Solve three graph problems back to back in a 75-minute contest.", 60, "build"),
    ]),
    ("Heaps, Tries and Greedy", "Use the right structure to cut the time complexity.", [
        ("Heaps and top K", "Solve Top K problems and keep a running median with two heaps.", 30, "practice"),
        ("Tries", "Implement a prefix tree and use it for word search.", 30, "practice"),
        ("Greedy and intervals", "Solve Jump Game and interval scheduling, and prove why the greedy choice works.", 30, "practice"),
        ("Milestone: build autocomplete", "Build a small autocomplete or time-based store that handles many queries quickly.", 60, "build"),
    ]),
    ("Interview Sprint", "Perform under a clock, like a real interview.", [
        ("Timed medium problems", "Solve three Mediums, 20 minutes each, with no hints.", 60, "practice"),
        ("Hard problem teardown", "Attempt one Hard for 40 minutes, then study the best solution and rewrite it from memory.", 60, "practice"),
        ("Explain-aloud practice", "Solve a problem while explaining your thinking out loud, and record yourself.", 30, "reflect"),
        ("Milestone: full mock round", "Do a full 90-minute mock round with two problems, ideally with a friend.", 90, "build"),
    ]),
]


def _base_stages(skill, level):
    stages = skill["stages"]
    if level == "pro" and skill.get("pro_stages"):
        return skill["pro_stages"]  # advanced worlds for people who already know the basics
    if level in ("intermediate", "pro"):
        return stages[1:]  # experienced learners skip World 1
    return stages


def _is_milestone(title):
    return title.lower().startswith("milestone")


def topics_for(key, level):
    """Topics the learner can mark as weak or strong, grouped by world (milestones excluded)."""
    out = []
    for title, _goal, steps in _base_stages(SKILLS[key], level):
        out.append({"world": title, "topics": [t for (t, _a, _m, _ty) in steps if not _is_milestone(t)]})
    return out


def fallback_roadmap(key, level, minutes, weak=(), strong=()):
    """Offline roadmap. Weak topics get an extra drill level; strong topics are skipped."""
    skill = SKILLS[key]
    weak = {w.strip().lower() for w in weak}
    strong = {w.strip().lower() for w in strong} - weak
    cap = max(10, round(minutes * 1.25))
    base = _base_stages(skill, level)
    out, drills = [], 0
    for title, goal, steps in base:
        built = []
        for (t, a, m, ty) in steps:
            low = t.lower()
            if low in strong and not _is_milestone(t):
                continue
            built.append({"title": t, "action": a, "minutes": min(m, cap), "type": ty, "hint": HINTS[ty],
                          **({"weak": True} if low in weak else {})})
            if low in weak and drills < 8:
                drills += 1
                built.append({"title": f"Drill: {t}", "action": f"Redo {t.lower()} from scratch without notes, then fix every mistake you find.",
                              "minutes": min(20, cap), "type": "practice", "weak": True,
                              "hint": "Struggling here is normal. Slow and correct beats fast and wrong."})
        # a world with only its milestone left is dropped when it has no weak topic
        if len(built) == 1 and _is_milestone(built[0]["title"]) and not any(w in {x[0].lower() for x in steps} for w in weak):
            continue
        out.append({"title": title, "goal": goal, "steps": built})
    if len(out) < 2:  # never hand back a one-world path
        out = [{"title": t, "goal": g, "steps": [{"title": a, "action": b, "minutes": min(m, cap), "type": ty, "hint": HINTS[ty]} for (a, b, m, ty) in st]} for (t, g, st) in base]
    total = sum(s["minutes"] for st in out for s in st["steps"])
    focus = sorted({w for w in weak})
    nlev = sum(len(s["steps"]) for s in out)
    tag = f"{len(out)} worlds, {nlev} levels. One small step at a time."
    if weak:
        tag = f"{len(out)} worlds, {nlev} levels, with extra practice on your weak spots."
    return {"skill": skill["name"], "tagline": tag, "totalWeeks": max(1, math.ceil(total / (minutes * 5))),
            "stages": out, "focus": [w.title() for w in focus][:8]}


# ---------------------------------------------------------------------------
# LeetCode practice sheet for the DSA path (links to leetcode.com/problems/<slug>/)
# Every topic has a pool of Easy / Medium / Hard problems. The learner's level
# decides which ones are shown, so a beginner sees Easy and a pro sees Hard.
# ---------------------------------------------------------------------------
DIFF_XP = {"Easy": 5, "Medium": 10, "Hard": 20}
E, M, H = "Easy", "Medium", "Hard"


def _p(slug, title, diff):
    return {"slug": slug, "title": title, "diff": diff, "xp": DIFF_XP[diff]}


WORLD_TITLES = {
    "core": ["Foundations", "Linear Structures", "Searching and Recursion", "Trees and Graphs"],
    "pro": ["Dynamic Programming", "Advanced Graphs", "Heaps, Tries and Greedy", "Interview Sprint"],
}

# Which difficulty to pick for each of the 3 problem slots, per level.
LEVEL_MIX = {
    "beginner": [E, E, M],
    "some": [E, M, M],
    "intermediate": [M, M, H],
    "pro": [M, H, H],
}
LEVEL_LABEL = {"beginner": "Brand new", "some": "Know a little", "intermediate": "Comfortable", "pro": "Pro"}
_NEAR = {E: [E, M, H], M: [M, E, H], H: [H, M, E]}

# (key, title, track, world index, keywords that match a roadmap step, problem pool)
SHEET_TOPICS = [
    # ---- core track ----
    ("bigo", "Warm-up: Loops and Big-O", "core", 0, ["big-o", "big o"], [
        ("fizz-buzz", "Fizz Buzz", E), ("running-sum-of-1d-array", "Running Sum of 1d Array", E),
        ("subarray-sum-equals-k", "Subarray Sum Equals K", M), ("find-the-duplicate-number", "Find the Duplicate Number", M),
        ("median-of-two-sorted-arrays", "Median of Two Sorted Arrays", H), ("first-missing-positive", "First Missing Positive", H)]),
    ("arrays", "Arrays and Two Pointers", "core", 0, ["two pointer", "array"], [
        ("reverse-string", "Reverse String", E), ("valid-palindrome", "Valid Palindrome", E), ("move-zeroes", "Move Zeroes", E),
        ("two-sum-ii-input-array-is-sorted", "Two Sum II - Input Array Is Sorted", M), ("3sum", "3Sum", M),
        ("container-with-most-water", "Container With Most Water", M),
        ("trapping-rain-water", "Trapping Rain Water", H), ("candy", "Candy", H)]),
    ("strings", "Strings", "core", 0, ["string", "anagram", "palindrome"], [
        ("valid-anagram", "Valid Anagram", E), ("longest-common-prefix", "Longest Common Prefix", E), ("is-subsequence", "Is Subsequence", E),
        ("longest-palindromic-substring", "Longest Palindromic Substring", M), ("string-to-integer-atoi", "String to Integer (atoi)", M),
        ("palindromic-substrings", "Palindromic Substrings", M),
        ("minimum-window-substring", "Minimum Window Substring", H), ("edit-distance", "Edit Distance", H),
        ("regular-expression-matching", "Regular Expression Matching", H)]),
    ("arrays_ms", "Milestone: Array Problems", "core", 0, ["three easy"], [
        ("contains-duplicate", "Contains Duplicate", E), ("best-time-to-buy-and-sell-stock", "Best Time to Buy and Sell Stock", E),
        ("single-number", "Single Number", E),
        ("maximum-subarray", "Maximum Subarray", M), ("product-of-array-except-self", "Product of Array Except Self", M),
        ("maximum-product-subarray", "Maximum Product Subarray", M),
        ("shortest-subarray-with-sum-at-least-k", "Shortest Subarray with Sum at Least K", H),
        ("count-of-smaller-numbers-after-self", "Count of Smaller Numbers After Self", H)]),
    ("linked", "Linked Lists", "core", 1, ["linked list"], [
        ("reverse-linked-list", "Reverse Linked List", E), ("middle-of-the-linked-list", "Middle of the Linked List", E),
        ("merge-two-sorted-lists", "Merge Two Sorted Lists", E),
        ("remove-nth-node-from-end-of-list", "Remove Nth Node From End of List", M), ("add-two-numbers", "Add Two Numbers", M),
        ("reorder-list", "Reorder List", M),
        ("reverse-nodes-in-k-group", "Reverse Nodes in k-Group", H), ("merge-k-sorted-lists", "Merge k Sorted Lists", H)]),
    ("stack", "Stacks", "core", 1, ["stack", "parenthes"], [
        ("valid-parentheses", "Valid Parentheses", E), ("baseball-game", "Baseball Game", E),
        ("min-stack", "Min Stack", M), ("daily-temperatures", "Daily Temperatures", M),
        ("evaluate-reverse-polish-notation", "Evaluate Reverse Polish Notation", M), ("decode-string", "Decode String", M),
        ("largest-rectangle-in-histogram", "Largest Rectangle in Histogram", H), ("basic-calculator", "Basic Calculator", H)]),
    ("window", "Queues and Sliding Window", "core", 1, ["queue", "sliding window"], [
        ("maximum-average-subarray-i", "Maximum Average Subarray I", E), ("number-of-recent-calls", "Number of Recent Calls", E),
        ("longest-substring-without-repeating-characters", "Longest Substring Without Repeating Characters", M),
        ("longest-repeating-character-replacement", "Longest Repeating Character Replacement", M),
        ("permutation-in-string", "Permutation in String", M),
        ("sliding-window-maximum", "Sliding Window Maximum", H),
        ("substring-with-concatenation-of-all-words", "Substring with Concatenation of All Words", H)]),
    ("linear_ms", "Milestone: Browser History", "core", 1, ["browser history"], [
        ("implement-queue-using-stacks", "Implement Queue using Stacks", E), ("linked-list-cycle", "Linked List Cycle", E),
        ("design-browser-history", "Design Browser History", M), ("lru-cache", "LRU Cache", M),
        ("copy-list-with-random-pointer", "Copy List with Random Pointer", M),
        ("lfu-cache", "LFU Cache", H), ("all-oone-data-structure", "All O`one Data Structure", H)]),
    ("bsearch", "Binary Search", "core", 2, ["binary search"], [
        ("binary-search", "Binary Search", E), ("search-insert-position", "Search Insert Position", E), ("sqrtx", "Sqrt(x)", E),
        ("search-in-rotated-sorted-array", "Search in Rotated Sorted Array", M),
        ("find-first-and-last-position-of-element-in-sorted-array", "Find First and Last Position of Element in Sorted Array", M),
        ("search-a-2d-matrix", "Search a 2D Matrix", M),
        ("split-array-largest-sum", "Split Array Largest Sum", H), ("k-th-smallest-prime-fraction", "K-th Smallest Prime Fraction", H)]),
    ("recursion", "Recursion", "core", 2, ["recursion", "fibonacci", "factorial"], [
        ("fibonacci-number", "Fibonacci Number", E), ("climbing-stairs", "Climbing Stairs", E), ("power-of-two", "Power of Two", E),
        ("powx-n", "Pow(x, n)", M), ("generate-parentheses", "Generate Parentheses", M), ("permutations", "Permutations", M),
        ("n-queens", "N-Queens", H), ("sudoku-solver", "Sudoku Solver", H)]),
    ("sorting", "Sorting", "core", 2, ["sort"], [
        ("merge-sorted-array", "Merge Sorted Array", E), ("squares-of-a-sorted-array", "Squares of a Sorted Array", E),
        ("sort-colors", "Sort Colors", M), ("sort-an-array", "Sort an Array", M),
        ("kth-largest-element-in-an-array", "Kth Largest Element in an Array", M), ("merge-intervals", "Merge Intervals", M),
        ("count-of-range-sum", "Count of Range Sum", H), ("reverse-pairs", "Reverse Pairs", H)]),
    ("search_ms", "Milestone: Medium Problems", "core", 2, ["three medium"], [
        ("valid-perfect-square", "Valid Perfect Square", E),
        ("koko-eating-bananas", "Koko Eating Bananas", M), ("find-minimum-in-rotated-sorted-array", "Find Minimum in Rotated Sorted Array", M),
        ("subsets", "Subsets", M), ("combination-sum", "Combination Sum", M),
        ("palindrome-partitioning-ii", "Palindrome Partitioning II", H), ("word-search-ii", "Word Search II", H)]),
    ("trees", "Trees", "core", 3, ["traversal", "binary tree", "tree"], [
        ("binary-tree-inorder-traversal", "Binary Tree Inorder Traversal", E), ("maximum-depth-of-binary-tree", "Maximum Depth of Binary Tree", E),
        ("invert-binary-tree", "Invert Binary Tree", E), ("same-tree", "Same Tree", E),
        ("lowest-common-ancestor-of-a-binary-tree", "Lowest Common Ancestor of a Binary Tree", M),
        ("kth-smallest-element-in-a-bst", "Kth Smallest Element in a BST", M), ("binary-tree-right-side-view", "Binary Tree Right Side View", M),
        ("binary-tree-maximum-path-sum", "Binary Tree Maximum Path Sum", H),
        ("serialize-and-deserialize-binary-tree", "Serialize and Deserialize Binary Tree", H)]),
    ("hashing", "Hash Maps", "core", 3, ["hash"], [
        ("two-sum", "Two Sum", E), ("ransom-note", "Ransom Note", E),
        ("group-anagrams", "Group Anagrams", M), ("top-k-frequent-elements", "Top K Frequent Elements", M),
        ("longest-consecutive-sequence", "Longest Consecutive Sequence", M),
        ("longest-duplicate-substring", "Longest Duplicate Substring", H), ("max-points-on-a-line", "Max Points on a Line", H)]),
    ("graphs", "Graphs: BFS and DFS", "core", 3, ["bfs", "dfs", "graph", "island"], [
        ("flood-fill", "Flood Fill", E), ("find-if-path-exists-in-graph", "Find if Path Exists in Graph", E),
        ("number-of-islands", "Number of Islands", M), ("binary-tree-level-order-traversal", "Binary Tree Level Order Traversal", M),
        ("clone-graph", "Clone Graph", M), ("pacific-atlantic-water-flow", "Pacific Atlantic Water Flow", M),
        ("word-ladder", "Word Ladder", H), ("shortest-path-in-a-grid-with-obstacles-elimination", "Shortest Path in a Grid with Obstacles Elimination", H)]),
    ("final_ms", "Milestone: Mock Interview", "core", 3, ["mock interview"], [
        ("diameter-of-binary-tree", "Diameter of Binary Tree", E),
        ("course-schedule", "Course Schedule", M), ("validate-binary-search-tree", "Validate Binary Search Tree", M),
        ("rotting-oranges", "Rotting Oranges", M),
        ("shortest-path-visiting-all-nodes", "Shortest Path Visiting All Nodes", H), ("binary-tree-cameras", "Binary Tree Cameras", H)]),

    # ---- pro track (for learners who already solve Mediums comfortably) ----
    ("dp1", "1D Dynamic Programming", "pro", 0, ["1d dp"], [
        ("min-cost-climbing-stairs", "Min Cost Climbing Stairs", E),
        ("house-robber", "House Robber", M), ("coin-change", "Coin Change", M), ("decode-ways", "Decode Ways", M), ("word-break", "Word Break", M),
        ("burst-balloons", "Burst Balloons", H), ("longest-valid-parentheses", "Longest Valid Parentheses", H)]),
    ("dp2", "2D and Grid DP", "pro", 0, ["2d dp"], [
        ("unique-paths", "Unique Paths", M), ("unique-paths-ii", "Unique Paths II", M), ("minimum-path-sum", "Minimum Path Sum", M),
        ("longest-common-subsequence", "Longest Common Subsequence", M), ("maximal-square", "Maximal Square", M),
        ("interleaving-string", "Interleaving String", H), ("distinct-subsequences", "Distinct Subsequences", H)]),
    ("dp3", "Knapsack and Subsequences", "pro", 0, ["knapsack"], [
        ("partition-equal-subset-sum", "Partition Equal Subset Sum", M), ("longest-increasing-subsequence", "Longest Increasing Subsequence", M),
        ("target-sum", "Target Sum", M), ("coin-change-ii", "Coin Change II", M),
        ("russian-doll-envelopes", "Russian Doll Envelopes", H), ("best-time-to-buy-and-sell-stock-iv", "Best Time to Buy and Sell Stock IV", H)]),
    ("dp_ms", "Milestone: Five DP Problems", "pro", 0, ["five dp"], [
        ("perfect-squares", "Perfect Squares", M), ("longest-palindromic-subsequence", "Longest Palindromic Subsequence", M),
        ("best-time-to-buy-and-sell-stock-with-cooldown", "Best Time to Buy and Sell Stock with Cooldown", M),
        ("super-egg-drop", "Super Egg Drop", H), ("maximum-profit-in-job-scheduling", "Maximum Profit in Job Scheduling", H)]),
    ("sp", "Shortest Paths", "pro", 1, ["shortest path"], [
        ("network-delay-time", "Network Delay Time", M), ("cheapest-flights-within-k-stops", "Cheapest Flights Within K Stops", M),
        ("path-with-minimum-effort", "Path With Minimum Effort", M), ("path-with-maximum-probability", "Path with Maximum Probability", M),
        ("swim-in-rising-water", "Swim in Rising Water", H), ("reachable-nodes-in-subdivided-graph", "Reachable Nodes In Subdivided Graph", H)]),
    ("uf", "Union Find", "pro", 1, ["union find"], [
        ("number-of-provinces", "Number of Provinces", M), ("redundant-connection", "Redundant Connection", M),
        ("accounts-merge", "Accounts Merge", M), ("most-stones-removed-with-same-row-or-column", "Most Stones Removed with Same Row or Column", M),
        ("making-a-large-island", "Making A Large Island", H), ("couples-holding-hands", "Couples Holding Hands", H)]),
    ("topo", "Topological Sort", "pro", 1, ["topological"], [
        ("course-schedule-ii", "Course Schedule II", M), ("find-eventual-safe-states", "Find Eventual Safe States", M),
        ("minimum-height-trees", "Minimum Height Trees", M),
        ("parallel-courses-iii", "Parallel Courses III", H), ("sort-items-by-groups-respecting-dependencies", "Sort Items by Groups Respecting Dependencies", H)]),
    ("graph_ms", "Milestone: Graph Contest", "pro", 1, ["graph contest"], [
        ("is-graph-bipartite", "Is Graph Bipartite?", M), ("min-cost-to-connect-all-points", "Min Cost to Connect All Points", M),
        ("critical-connections-in-a-network", "Critical Connections in a Network", H), ("reconstruct-itinerary", "Reconstruct Itinerary", H)]),
    ("heap", "Heaps and Top K", "pro", 2, ["heaps and top"], [
        ("kth-largest-element-in-a-stream", "Kth Largest Element in a Stream", E), ("last-stone-weight", "Last Stone Weight", E),
        ("k-closest-points-to-origin", "K Closest Points to Origin", M), ("task-scheduler", "Task Scheduler", M),
        ("find-median-from-data-stream", "Find Median from Data Stream", H), ("sliding-window-median", "Sliding Window Median", H)]),
    ("trie", "Tries", "pro", 2, ["tries"], [
        ("implement-trie-prefix-tree", "Implement Trie (Prefix Tree)", M),
        ("design-add-and-search-words-data-structure", "Design Add and Search Words Data Structure", M), ("replace-words", "Replace Words", M),
        ("palindrome-pairs", "Palindrome Pairs", H), ("stream-of-characters", "Stream of Characters", H)]),
    ("greedy", "Greedy and Intervals", "pro", 2, ["greedy"], [
        ("jump-game", "Jump Game", M), ("jump-game-ii", "Jump Game II", M), ("gas-station", "Gas Station", M),
        ("non-overlapping-intervals", "Non-overlapping Intervals", M), ("insert-interval", "Insert Interval", M),
        ("ipo", "IPO", H), ("minimum-number-of-refueling-stops", "Minimum Number of Refueling Stops", H)]),
    ("heap_ms", "Milestone: Build Autocomplete", "pro", 2, ["autocomplete"], [
        ("design-twitter", "Design Twitter", M), ("time-based-key-value-store", "Time Based Key-Value Store", M),
        ("insert-delete-getrandom-o1", "Insert Delete GetRandom O(1)", M),
        ("maximum-frequency-stack", "Maximum Frequency Stack", H)]),
    ("sprint1", "Timed Mediums", "pro", 3, ["timed medium"], [
        ("rotate-image", "Rotate Image", M), ("spiral-matrix", "Spiral Matrix", M), ("next-permutation", "Next Permutation", M),
        ("subarray-sums-divisible-by-k", "Subarray Sums Divisible by K", M),
        ("trapping-rain-water-ii", "Trapping Rain Water II", H), ("maximal-rectangle", "Maximal Rectangle", H)]),
    ("sprint2", "Hard Problem Teardown", "pro", 3, ["hard problem teardown"], [
        ("kth-smallest-element-in-a-sorted-matrix", "Kth Smallest Element in a Sorted Matrix", M),
        ("find-k-pairs-with-smallest-sums", "Find K Pairs with Smallest Sums", M),
        ("longest-increasing-path-in-a-matrix", "Longest Increasing Path in a Matrix", H), ("the-skyline-problem", "The Skyline Problem", H),
        ("find-minimum-in-rotated-sorted-array-ii", "Find Minimum in Rotated Sorted Array II", H)]),
    ("mock", "Milestone: Full Mock Round", "pro", 3, ["full mock round"], [
        ("valid-sudoku", "Valid Sudoku", M), ("fruit-into-baskets", "Fruit Into Baskets", M),
        ("text-justification", "Text Justification", H), ("integer-to-english-words", "Integer to English Words", H)]),
]

# Well-known external sheets (opened in a new tab)
EXTERNAL_SHEETS = [
    {"name": "LeetCode Top Interview 150", "desc": "LeetCode's own study plan for interviews.", "url": "https://leetcode.com/studyplan/top-interview-150/"},
    {"name": "LeetCode 75", "desc": "A shorter plan to build core skills fast.", "url": "https://leetcode.com/studyplan/leetcode-75/"},
    {"name": "NeetCode 150", "desc": "Curated list with video explanations.", "url": "https://neetcode.io/practice"},
    {"name": "Striver's SDE Sheet", "desc": "Popular interview sheet from takeUforward.", "url": "https://takeuforward.org/interviews/strivers-sde-sheet-top-coding-interview-problems/"},
]

# Specific topics are matched before generic ones (e.g. "linked list" before "array").
_MATCH_ORDER = ["dp_ms", "dp1", "dp2", "dp3", "graph_ms", "sp", "uf", "topo", "heap_ms", "heap", "trie", "greedy",
                "sprint1", "sprint2", "mock",
                "bigo", "linear_ms", "arrays_ms", "search_ms", "final_ms", "linked", "stack", "window", "bsearch",
                "recursion", "sorting", "trees", "hashing", "graphs", "strings", "arrays"]
_TOPIC = {t[0]: t for t in SHEET_TOPICS}


def _pool(key):
    return [_p(*x) for x in _TOPIC[key][5]]


def pick_problems(key, level):
    """Choose 3 problems from the topic pool that fit the learner's level."""
    pool = _pool(key)
    chosen = []
    for want in LEVEL_MIX.get(level, LEVEL_MIX["beginner"]):
        for d in _NEAR[want]:
            hit = next((p for p in pool if p["diff"] == d and p not in chosen), None)
            if hit:
                chosen.append(hit)
                break
    return chosen


def sheet(level="beginner"):
    track = "pro" if level == "pro" else "core"
    mine = {p["slug"] for t in SHEET_TOPICS if t[2] == track for p in pick_problems(t[0], level)}
    return {
        "level": level,
        "levelLabel": LEVEL_LABEL.get(level, "Brand new"),
        "links": EXTERNAL_SHEETS,
        "topics": [
            {"key": k, "title": title, "world": w, "worldTitle": WORLD_TITLES[tr][w],
             "problems": [{**p, "forYou": p["slug"] in mine} for p in _pool(k)]}
            for (k, title, tr, w, _kw, _pool_) in SHEET_TOPICS if tr == track
        ],
    }


_EASIER = {"pro": "intermediate", "intermediate": "some", "some": "beginner", "beginner": "beginner"}


def problems_for_step(step, level="beginner"):
    if step.get("weak"):
        level = _EASIER.get(level, level)  # weak topic: start one notch gentler
    text = f"{step.get('title', '')} {step.get('action', '')}".lower()
    for key in _MATCH_ORDER:
        if any(kw in text for kw in _TOPIC[key][4]):
            return pick_problems(key, level)
    return []


def attach_problems(roadmap, level="beginner"):
    for stage in roadmap.get("stages", []):
        for st in stage.get("steps", []):
            st["problems"] = problems_for_step(st, level)
    return roadmap
