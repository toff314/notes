#!/usr/bin/env python3
"""lab-02：结构歧义的枚举与计数（§19.5）。

1) 「i shot an elephant in my pajamas」的全部合法分析，按 PP 挂靠的**产出式**分类；
2) 逐步追加 PP，测总分析数随 PP 个数的增长；对照一部「挂靠更自由」的变体文法 L1X；
3) 记录「数分析」（DP）与「枚举分析」（回溯展开）的耗时差。

产出（out/）：
  elephant_parses.txt   全部括号串 + 挂靠产出式
  attachment.csv        n_pp -> 分析数（L1 / L1X）、Catalan、k!、枚举耗时
  summary.json          主句统计与增长表
"""
import csv
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cfgkit as K  # noqa: E402

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# L1X：把 PP 的挂靠口子多开一个（NP -> NP PP），用来对照「文法自由度决定歧义数」
L1X_RULES = K.L1_RULES + [("NP", ("NP", "PP"))]

CNF = K.to_cnf(K.L1_RULES, K.LEXICON)[0]
CNFX = K.to_cnf(L1X_RULES, K.LEXICON)[0]


def analyze(sent, cnf):
    ws = sent.split()
    table, back = K.cky(ws, cnf, K.LEXICON)
    return ws, table, back, K.count_trees(table, back, 0, len(ws), "S")


def pp_hosts(tree, ws):
    """返回 [(跨度, 文本, 宿主产出式)]，宿主产出式形如 VP->VP-PP。"""
    res = []

    def walk(node, start, prod):
        sym, kids = node
        if len(kids) == 1 and len(kids[0]) == 1:
            return start + 1
        cur = start
        kids_span = []
        for k in kids:
            cur = walk(k, cur, "%s->%s" % (sym, "-".join(c[0] for c in kids)))
            kids_span.append(cur)
        if sym == "PP":
            res.append(("%d-%d" % (start, cur), " ".join(ws[start:cur]), prod))
        return cur

    walk(tree, 0, "ROOT")
    return res


MAIN = "i shot an elephant in my pajamas"
ws, table, back, n_parses = analyze(MAIN, CNF)
all_trees = K.trees(table, back, 0, len(ws), "S")

lines, tally = [], {}
for t in all_trees:
    t2 = K.unbinarize(t)
    hosts = pp_hosts(t2, ws)
    key = " | ".join(h[2] for h in hosts)
    tally[key] = tally.get(key, 0) + 1
    lines.append("%-22s %s" % (key, K.bracket(t2)))
with open(os.path.join(OUT, "elephant_parses.txt"), "w", encoding="utf-8") as f:
    f.write("# %s\n" % MAIN)
    f.write("# 共 %d 种分析；首列是 PP 的宿主产出式\n" % len(all_trees))
    f.write("\n".join(lines) + "\n")

BASE = "i shot an elephant".split()
PP_CHUNKS = ["in my pajamas", "near houston", "on united", "through a meal"]
rows = []
for k in range(0, len(PP_CHUNKS) + 1):
    w = BASE + " ".join(PP_CHUNKS[:k]).split()
    sent = " ".join(w)

    t0 = time.perf_counter()
    tb, bk = K.cky(w, CNF, K.LEXICON)
    cnt1 = K.count_trees(tb, bk, 0, len(w), "S")
    t_count = time.perf_counter() - t0

    tb2, bk2 = K.cky(w, CNFX, K.LEXICON)
    cnt2 = K.count_trees(tb2, bk2, 0, len(w), "S")

    t0 = time.perf_counter()
    got = K.trees(tb2, bk2, 0, len(w), "S", limit=200000)
    t_enum = time.perf_counter() - t0

    catalan = 1
    for i in range(k):
        catalan = catalan * 2 * (2 * i + 1) // (i + 2)
    fact = 1
    for i in range(1, k + 1):
        fact *= i
    rows.append({
        "n_pp": k,
        "n_words": len(w),
        "parses_L1": cnt1,
        "parses_L1X": cnt2,
        "catalan_k": catalan,
        "factorial_k": fact,
        "n_enumerated_L1X": len(got),
        "t_count_s": round(t_count, 4),
        "t_enum_s": round(t_enum, 4),
    })

with open(os.path.join(OUT, "attachment.csv"), "w", newline="", encoding="utf-8") as f:
    wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    wr.writeheader()
    wr.writerows(rows)

summary = {"sentence": MAIN, "n_parses": n_parses,
           "pp_host_productions": tally, "growth": rows}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(json.dumps({k: summary[k] for k in ("sentence", "n_parses", "pp_host_productions")},
                 ensure_ascii=False, indent=2))
print()
print("%-5s %-6s %-10s %-11s %-9s %-7s %-13s %-9s" %
      ("n_pp", "words", "parses_L1", "parses_L1X", "catalan", "k!",
       "enumerated", "t_enum(s)"))
for r in rows:
    print("%-5d %-6d %-10d %-11d %-9d %-7d %-13d %-9.4f" %
          (r["n_pp"], r["n_words"], r["parses_L1"], r["parses_L1X"],
           r["catalan_k"], r["factorial_k"], r["n_enumerated_L1X"], r["t_enum_s"]))
