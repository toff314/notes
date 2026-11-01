#!/usr/bin/env python3
"""lab-01：把 L1 文法转成 CNF，再用 CKY 填表分析 "book the flight through houston"。

产出（out/）：
  cnf_rules.csv        转换后的 CNF 规则（含词汇规则）
  parse_table.csv      填好的上三角表（每格的非终结符集合）
  parses.txt           回溯指针枚举出的全部解析树（括号记法）
  unbinarized.txt      折叠哑节点后的树
  equiv.csv            20 个句子在「转换前/转换后」的成员判定
  summary.json         关键计数（parse 数、规则数、单元格数）
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cfgkit as K  # noqa: E402

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

SENT = "book the flight through houston".split()

cnf_rules, dummy = K.to_cnf(K.L1_RULES, K.LEXICON)
table, back = K.cky(SENT, cnf_rules, K.LEXICON)

n = len(SENT)
n_parses = K.count_trees(table, back, 0, n, "S")

# ---- 1. CNF 规则 ----
with open(os.path.join(OUT, "cnf_rules.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["lhs", "rhs", "kind"])
    for a, rhs in sorted(cnf_rules):
        kind = "binary" if len(rhs) == 2 else "lexical"
        w.writerow([a, " ".join(rhs), kind])

# ---- 2. 分析表 ----
with open(os.path.join(OUT, "parse_table.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["i", "j", "span_words", "nonterminals"])
    for i in range(n + 1):
        for j in range(i + 1, n + 1):
            w.writerow([i, j, " ".join(SENT[i:j]), "|".join(sorted(table[i][j]))])

# ---- 3. 全部解析树 ----
ts = K.trees(table, back, 0, n, "S")
with open(os.path.join(OUT, "parses.txt"), "w", encoding="utf-8") as f:
    for t in ts:
        f.write(K.bracket(t) + "\n")

# ---- 4. 折叠哑节点 ----
with open(os.path.join(OUT, "unbinarized.txt"), "w", encoding="utf-8") as f:
    for t in ts:
        f.write(K.bracket(K.unbinarize(t)) + "\n")

# ---- 5. 转换前后语言一致性（20 句） ----
tests = [
    "book the flight through houston",
    "i prefer a morning flight",
    "does houston include the meal",
    "the flight from houston to united",
    "she book the money",
    "i shot an elephant in my pajamas",
    "the meal on united",
    "near houston the flight",
    "book book book",
    "the the the",
    "flight",
    "i",
    "does",
    "from houston",
    "the flight through houston on united near a meal",
    "i prefer the flight through houston on united",
    "book that flight",
    "the money from the meal",
    "united near houston",
    "she prefer a meal in the morning",
]
rows = []
agree = 0
for s in tests:
    ws = s.split()
    before = K.accepts(ws, K.L1_RULES, K.LEXICON)
    after = K.accepts(ws, cnf_rules, K.LEXICON)
    agree += int(before == after)
    rows.append({"sentence": s, "before_cnf": before, "after_cnf": after})
with open(os.path.join(OUT, "equiv.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["sentence", "before_cnf", "after_cnf"])
    w.writeheader()
    w.writerows(rows)

# ---- 6. CNF 形状断言 ----
cnf_ok = True
lex_set = set(K.LEXICON)
for a, rhs in cnf_rules:
    if len(rhs) == 2:
        if any(s in lex_set for s in rhs):
            cnf_ok = False
    elif len(rhs) == 1:
        if rhs[0] not in lex_set:
            cnf_ok = False
    else:
        cnf_ok = False

summary = {
    "sentence": " ".join(SENT),
    "n_words": n,
    "n_cnf_rules": len(cnf_rules),
    "n_cells_filled": sum(1 for i in range(n + 1) for j in range(i + 1, n + 1)
                          if table[i][j]),
    "n_cells_total": n * (n + 1) // 2,
    "n_parses": n_parses,
    "n_parses_enumerated": len(ts),
    "cnf_ok": cnf_ok,
    "equiv_agree": "%d/%d" % (agree, len(tests)),
    "dummy_terminals": dummy,
    "root_cell": sorted(table[0][n]),
}
with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(json.dumps(summary, ensure_ascii=False, indent=2))
if n_parses != 3:
    print("!! 期望 3 种分析（书中图 19.14），实际 %d" % n_parses)
