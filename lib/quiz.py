"""Quiz helpers: validation of AI-written questions and a small offline bank for the diagnostic quiz."""
import json
import re

# topic names match the step titles used by lib/content.py (beginner/some levels)
BANK = {
    "dsa": [
        ("Big-O in plain words", "What is the time complexity of looking up an item in an unsorted list of n items?", ["O(1)", "O(log n)", "O(n)", "O(n squared)"], 2, "You may have to check every item once, so it grows in line with n."),
        ("Arrays and two pointers", "Two pointers on a sorted array are most useful for...", ["Finding a pair with a target sum", "Sorting the array", "Deleting the array", "Hashing values"], 0, "Move one pointer from each end inward, depending on whether the sum is too small or too big."),
        ("Linked list", "What is the cost of inserting at the head of a singly linked list?", ["O(n)", "O(1)", "O(log n)", "O(n squared)"], 1, "You only change the head pointer, no shifting is needed."),
        ("Stacks", "Which structure follows last-in, first-out?", ["Queue", "Stack", "Heap", "Graph"], 1, "A stack gives back the most recently added item first."),
        ("Binary search", "Binary search needs the data to be...", ["Unique", "Sorted", "Positive", "Stored in a list only"], 1, "Each step discards half the range, which only works when the order is known."),
        ("Recursion", "Every recursive function needs...", ["A loop", "A base case", "A global variable", "A class"], 1, "Without a base case the calls never stop."),
        ("Hash maps", "Average time to look up a key in a hash map is...", ["O(1)", "O(n)", "O(log n)", "O(n log n)"], 0, "Hashing jumps straight to the bucket."),
        ("BFS and DFS", "Which traversal uses a queue to visit the nearest nodes first?", ["DFS", "BFS", "Inorder", "Binary search"], 1, "BFS explores level by level using a queue."),
    ],
    "python": [
        ("Variables and types", "What does type(3.0) return?", ["int", "float", "str", "number"], 1, "A number with a decimal point is a float."),
        ("If, elif, else", "What prints? x = 5; if x > 10: print('a') elif x > 3: print('b') else: print('c')", ["a", "b", "c", "Nothing"], 1, "The first false check is skipped, then x > 3 is true."),
        ("Loops", "How many times does range(3) loop?", ["2", "3", "4", "Forever"], 1, "range(3) gives 0, 1, 2."),
        ("Lists and dictionaries", "How do you read the value for key 'a' in a dict d?", ["d.a", "d['a']", "d(a)", "d{a}"], 1, "Dictionaries use square brackets with the key."),
        ("Write functions", "What does a function return if it has no return statement?", ["0", "''", "None", "An error"], 2, "Python returns None by default."),
        ("Read a file", "Which statement opens a file and closes it safely?", ["open(f)", "with open(f) as fh:", "read(f)", "file(f)"], 1, "The with block closes the file even if an error happens."),
    ],
    "sql": [
        ("Tables, rows and keys", "What uniquely identifies each row in a table?", ["Foreign key", "Primary key", "Index", "View"], 1, "A primary key is unique for every row."),
        ("Filter and sort", "Which clause sorts the results?", ["GROUP BY", "WHERE", "ORDER BY", "HAVING"], 2, "ORDER BY sorts the output."),
        ("Joins", "Which join keeps all rows from the left table even with no match?", ["INNER JOIN", "LEFT JOIN", "CROSS JOIN", "SELF JOIN"], 1, "LEFT JOIN keeps every left row and fills gaps with NULL."),
        ("GROUP BY", "Which function counts rows in each group?", ["SUM()", "COUNT()", "MAX()", "ROUND()"], 1, "COUNT() counts the rows."),
        ("Indexes", "What does an index mostly speed up?", ["Inserts", "Reads and lookups", "Deleting tables", "Backups"], 1, "Indexes help the database find rows without scanning the whole table."),
    ],
    "web": [
        ("Your first HTML", "Which tag makes the largest heading?", ["<h6>", "<head>", "<h1>", "<title>"], 2, "h1 is the top-level heading."),
        ("Style with CSS", "Which CSS property changes text colour?", ["font-color", "color", "text-style", "paint"], 1, "The property is simply color."),
        ("Flexbox", "Which property turns an element into a flex container?", ["display: flex", "position: flex", "flex: container", "float: flex"], 0, "display: flex enables flexbox on the children."),
        ("JavaScript in the browser", "Which keyword declares a variable that can be changed?", ["const", "let", "fixed", "static"], 1, "let can be reassigned, const cannot."),
        ("The DOM", "What does document.querySelector('.card') return?", ["All .card elements", "The first .card element", "A string", "A CSS rule"], 1, "querySelector gives the first match."),
    ],
}


def offline_questions(skill, topics, n=6):
    """Questions from the built-in bank whose topic is on the learner's topic list."""
    allowed = {t.lower() for t in topics}
    out = []
    for (topic, q, opts, ans, why) in BANK.get(skill, []):
        if topic.lower() in allowed:
            out.append({"topic": topic, "q": q, "options": opts, "answer": ans, "explain": why})
    return out[:n]


def clean_questions(raw_text, topics=None, n=6):
    """Parse the AI reply and keep only well-formed questions."""
    a, b = raw_text.find("["), raw_text.rfind("]")
    if a == -1 or b == -1:
        a2, b2 = raw_text.find("{"), raw_text.rfind("}")
        data = json.loads(raw_text[a2:b2 + 1]).get("questions", [])
    else:
        data = json.loads(raw_text[a:b + 1])
    lower = {t.lower(): t for t in (topics or [])}
    out = []
    for item in data:
        try:
            opts = [str(o)[:140] for o in item["options"]][:4]
            ans = int(item["answer"])
            if len(opts) != 4 or not 0 <= ans <= 3:
                continue
            topic = lower.get(str(item.get("topic", "")).strip().lower(), "")
            out.append({"topic": topic, "q": re.sub(r"\s+", " ", str(item["q"]))[:300], "options": opts,
                        "answer": ans, "explain": str(item.get("explain", ""))[:300]})
        except (KeyError, TypeError, ValueError):
            continue
    return out[:n]
