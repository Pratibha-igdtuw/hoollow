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


def fallback_roadmap(key, level, minutes):
    skill = SKILLS[key]
    stages = skill["stages"]
    if level == "intermediate":
        stages = stages[1:]  # experienced learners skip World 1
    cap = max(10, round(minutes * 1.25))
    out = []
    for title, goal, steps in stages:
        out.append({
            "title": title,
            "goal": goal,
            "steps": [
                {"title": t, "action": a, "minutes": min(m, cap), "type": ty, "hint": HINTS[ty]}
                for (t, a, m, ty) in steps
            ],
        })
    total = sum(s["minutes"] for st in out for s in st["steps"])
    return {
        "skill": skill["name"],
        "tagline": f"{len(out)} worlds, {sum(len(s['steps']) for s in out)} levels. One small step at a time.",
        "totalWeeks": max(1, math.ceil(total / (minutes * 5))),
        "stages": out,
    }


# ---------------------------------------------------------------------------
# LeetCode practice sheet for the DSA path (links to leetcode.com/problems/<slug>/)
# ---------------------------------------------------------------------------
DIFF_XP = {"Easy": 5, "Medium": 10, "Hard": 20}


def _p(slug, title, diff):
    return {"slug": slug, "title": title, "diff": diff, "xp": DIFF_XP[diff]}


WORLD_TITLES = ["Foundations", "Linear Structures", "Searching and Recursion", "Trees and Graphs"]

# key, title, world index, keywords used to match a roadmap step, problems
SHEET_TOPICS = [
    ("bigo", "Warm-up: Loops and Big-O", 0, ["big-o", "big o"], [
        _p("fizz-buzz", "Fizz Buzz", "Easy"),
        _p("running-sum-of-1d-array", "Running Sum of 1d Array", "Easy"),
        _p("richest-customer-wealth", "Richest Customer Wealth", "Easy")]),
    ("arrays", "Arrays and Two Pointers", 0, ["two pointer", "array"], [
        _p("reverse-string", "Reverse String", "Easy"),
        _p("valid-palindrome", "Valid Palindrome", "Easy"),
        _p("two-sum-ii-input-array-is-sorted", "Two Sum II - Input Array Is Sorted", "Medium")]),
    ("strings", "Strings", 0, ["string", "anagram", "palindrome"], [
        _p("valid-anagram", "Valid Anagram", "Easy"),
        _p("longest-common-prefix", "Longest Common Prefix", "Easy"),
        _p("is-subsequence", "Is Subsequence", "Easy")]),
    ("arrays_ms", "Milestone: Easy Array Problems", 0, ["three easy"], [
        _p("contains-duplicate", "Contains Duplicate", "Easy"),
        _p("best-time-to-buy-and-sell-stock", "Best Time to Buy and Sell Stock", "Easy"),
        _p("single-number", "Single Number", "Easy")]),
    ("linked", "Linked Lists", 1, ["linked list"], [
        _p("reverse-linked-list", "Reverse Linked List", "Easy"),
        _p("middle-of-the-linked-list", "Middle of the Linked List", "Easy"),
        _p("merge-two-sorted-lists", "Merge Two Sorted Lists", "Easy")]),
    ("stack", "Stacks", 1, ["stack", "parenthes"], [
        _p("valid-parentheses", "Valid Parentheses", "Easy"),
        _p("min-stack", "Min Stack", "Medium"),
        _p("daily-temperatures", "Daily Temperatures", "Medium")]),
    ("window", "Queues and Sliding Window", 1, ["queue", "sliding window"], [
        _p("maximum-average-subarray-i", "Maximum Average Subarray I", "Easy"),
        _p("longest-substring-without-repeating-characters", "Longest Substring Without Repeating Characters", "Medium"),
        _p("sliding-window-maximum", "Sliding Window Maximum", "Hard")]),
    ("linear_ms", "Milestone: Browser History", 1, ["browser history"], [
        _p("design-browser-history", "Design Browser History", "Medium"),
        _p("implement-queue-using-stacks", "Implement Queue using Stacks", "Easy"),
        _p("linked-list-cycle", "Linked List Cycle", "Easy")]),
    ("bsearch", "Binary Search", 2, ["binary search"], [
        _p("binary-search", "Binary Search", "Easy"),
        _p("search-insert-position", "Search Insert Position", "Easy"),
        _p("search-in-rotated-sorted-array", "Search in Rotated Sorted Array", "Medium")]),
    ("recursion", "Recursion", 2, ["recursion", "fibonacci", "factorial"], [
        _p("fibonacci-number", "Fibonacci Number", "Easy"),
        _p("climbing-stairs", "Climbing Stairs", "Easy"),
        _p("powx-n", "Pow(x, n)", "Medium")]),
    ("sorting", "Sorting", 2, ["sort"], [
        _p("merge-sorted-array", "Merge Sorted Array", "Easy"),
        _p("sort-colors", "Sort Colors", "Medium"),
        _p("sort-an-array", "Sort an Array", "Medium")]),
    ("search_ms", "Milestone: Medium Problems", 2, ["three medium"], [
        _p("koko-eating-bananas", "Koko Eating Bananas", "Medium"),
        _p("find-minimum-in-rotated-sorted-array", "Find Minimum in Rotated Sorted Array", "Medium"),
        _p("subsets", "Subsets", "Medium")]),
    ("trees", "Trees", 3, ["traversal", "binary tree", "tree"], [
        _p("binary-tree-inorder-traversal", "Binary Tree Inorder Traversal", "Easy"),
        _p("maximum-depth-of-binary-tree", "Maximum Depth of Binary Tree", "Easy"),
        _p("invert-binary-tree", "Invert Binary Tree", "Easy")]),
    ("hashing", "Hash Maps", 3, ["hash"], [
        _p("two-sum", "Two Sum", "Easy"),
        _p("group-anagrams", "Group Anagrams", "Medium"),
        _p("top-k-frequent-elements", "Top K Frequent Elements", "Medium")]),
    ("graphs", "Graphs: BFS and DFS", 3, ["bfs", "dfs", "graph", "island"], [
        _p("number-of-islands", "Number of Islands", "Medium"),
        _p("flood-fill", "Flood Fill", "Easy"),
        _p("binary-tree-level-order-traversal", "Binary Tree Level Order Traversal", "Medium")]),
    ("final_ms", "Milestone: Mock Interview", 3, ["mock interview"], [
        _p("course-schedule", "Course Schedule", "Medium"),
        _p("validate-binary-search-tree", "Validate Binary Search Tree", "Medium"),
        _p("rotting-oranges", "Rotting Oranges", "Medium")]),
]

# Well-known external sheets (opened in a new tab)
EXTERNAL_SHEETS = [
    {"name": "LeetCode Top Interview 150", "desc": "LeetCode's own study plan for interviews.", "url": "https://leetcode.com/studyplan/top-interview-150/"},
    {"name": "LeetCode 75", "desc": "A shorter plan to build core skills fast.", "url": "https://leetcode.com/studyplan/leetcode-75/"},
    {"name": "NeetCode 150", "desc": "Curated list with video explanations.", "url": "https://neetcode.io/practice"},
    {"name": "Striver's SDE Sheet", "desc": "Popular interview sheet from takeUforward.", "url": "https://takeuforward.org/interviews/strivers-sde-sheet-top-coding-interview-problems/"},
]

# Match the more specific topics (milestones, linked list, ...) before generic ones (array, string).
_MATCH_ORDER = ["bigo", "linear_ms", "arrays_ms", "search_ms", "final_ms", "linked", "stack", "window", "bsearch",
                "recursion", "sorting", "trees", "hashing", "graphs", "strings", "arrays"]
_TOPIC = {t[0]: t for t in SHEET_TOPICS}


def sheet():
    return {
        "links": EXTERNAL_SHEETS,
        "topics": [
            {"key": k, "title": title, "world": w, "worldTitle": WORLD_TITLES[w], "problems": probs}
            for (k, title, w, _kw, probs) in SHEET_TOPICS
        ],
    }


def problems_for_step(step):
    text = f"{step.get('title', '')} {step.get('action', '')}".lower()
    for key in _MATCH_ORDER:
        if any(kw in text for kw in _TOPIC[key][3]):
            return _TOPIC[key][4]
    return []


def attach_problems(roadmap):
    for stage in roadmap.get("stages", []):
        for st in stage.get("steps", []):
            st["problems"] = problems_for_step(st)
    return roadmap
