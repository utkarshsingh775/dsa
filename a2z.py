#!/usr/bin/env python3
"""A2Z helper.
  python3 a2z.py next dp            -> create file for the next unsolved DP lesson
  python3 a2z.py new dp 7           -> create file for DP lesson 7
  python3 a2z.py list dp            -> list lessons with ✅ / ⬜
  python3 a2z.py sync               -> rebuild all READMEs from the files that exist
Options: --lang cpp|java|py|js|go   (default: value in .a2z-lang, else cpp)
"""
import json, sys, os, datetime, glob

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, "problems.json"), encoding="utf-8"))
EXT = {"cpp": "cpp", "java": "java", "py": "py", "python": "py", "js": "js", "go": "go"}
STUB = {
    "cpp": "#include <bits/stdc++.h>\nusing namespace std;\n\nclass Solution {\npublic:\n    \n};\n",
    "java": "import java.util.*;\n\nclass Solution {\n    \n}\n",
    "py": "from typing import *\n\n\nclass Solution:\n    pass\n",
    "js": "/**\n * \n */\nvar solve = function () {\n    \n};\n",
    "go": "package main\n\n",
}

def lang_from(args):
    if "--lang" in args:
        return EXT[args[args.index("--lang") + 1].lower()]
    f = os.path.join(ROOT, ".a2z-lang")
    return EXT[open(f).read().strip().lower()] if os.path.exists(f) else "cpp"

def topic(folder):
    for m in DATA:
        if m["folder"] == folder:
            return m
    sys.exit(f"Unknown topic '{folder}'. Topics: " + ", ".join(m["folder"] for m in DATA))

def lessons(m):
    return [(s["name"], i) for s in m["subs"] for i in s["items"]]

def solved_file(folder, stem):
    hits = glob.glob(os.path.join(ROOT, folder, stem + ".*"))
    hits = [h for h in hits if not h.endswith(".md")]
    return os.path.basename(hits[0]) if hits else None

def create(m, it, sub, ext):
    os.makedirs(os.path.join(ROOT, m["folder"]), exist_ok=True)
    existing = solved_file(m["folder"], it["f"])
    if existing:
        print(f"Already exists: {m['folder']}/{existing}")
        return
    path = os.path.join(ROOT, m["folder"], f"{it['f']}.{ext}")
    c = "#" if ext == "py" else "//"
    head = [
        f"{m['name']} · Lesson {it['L']:02d} · {it['n']}  [{it['t'] or '-'}]",
        f"Section: {sub}",
        f"Link: {it['u'] if it['k']=='LC' else 'GFG (search): ' + it['u']}",
        f"Date: {datetime.date.today()}",
        "",
        "Approach: ",
        "Time: O()   Space: O()",
    ]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(f"{c} {h}".rstrip() for h in head) + "\n\n" + STUB[ext])
    print(f"Created {m['folder']}/{it['f']}.{ext}\nOpen: {it['u']}")

def readme_topic(m):
    rows, done = [], 0
    for sub, it in lessons(m):
        f = solved_file(m["folder"], it["f"])
        done += bool(f)
        link = f"[LeetCode{' 🔒' if it['p'] else ''}]({it['u']})" if it["k"] == "LC" else f"[GFG]({it['u']})"
        sol = f"[✅ {f}]({f})" if f else f"⬜ `{it['f']}`"
        rows.append(f"| {it['L']:02d} | {it['n']} | {sub} | {it['t'] or '-'} | {link} | {sol} |")
    total = len(rows)
    txt = (f"# {m['name']}\n\n**{done} / {total} solved**\n\n"
           f"Next one: `python3 a2z.py next {m['folder']}`\n\n"
           "| # | Problem | Section | Level | Link | Solution |\n|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n")
    with open(os.path.join(ROOT, m["folder"], "README.md"), "w", encoding="utf-8") as fh:
        fh.write(txt)
    return done, total

def sync():
    rows, D, T = [], 0, 0
    for m in DATA:
        os.makedirs(os.path.join(ROOT, m["folder"]), exist_ok=True)
        d, t = readme_topic(m)
        D += d; T += t
        bar = "█" * round(d / t * 10) + "░" * (10 - round(d / t * 10))
        rows.append(f"| [{m['name']}]({m['folder']}/) | `{m['folder']}/` | {d} / {t} | {bar} |")
    tpl = open(os.path.join(ROOT, "README.template.md"), encoding="utf-8").read()
    out = tpl.replace("{{TOTAL}}", f"{D} / {T}").replace("{{TABLE}}", "\n".join(rows))
    with open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8") as fh:
        fh.write(out)
    print(f"Synced. {D} / {T} solved.")

def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    cmd = a[0]
    if cmd == "sync":
        sync(); return
    if len(a) < 2:
        sys.exit(__doc__)
    m = topic(a[1])
    if cmd == "list":
        for sub, it in lessons(m):
            f = solved_file(m["folder"], it["f"])
            print(f"{'✅' if f else '⬜'} L{it['L']:02d}  {it['n']}  [{it['t'] or '-'}]  {it['u'] if it['k']=='LC' else '(GFG)'}")
        return
    ext = lang_from(a)
    if cmd == "next":
        for sub, it in lessons(m):
            if not solved_file(m["folder"], it["f"]):
                create(m, it, sub, ext); sync(); return
        print("Topic complete 🎉"); return
    if cmd == "new":
        n = int(a[2])
        for sub, it in lessons(m):
            if it["L"] == n:
                create(m, it, sub, ext); sync(); return
        sys.exit(f"No lesson {n} in {m['folder']}")
    sys.exit(__doc__)

if __name__ == "__main__":
    main()
