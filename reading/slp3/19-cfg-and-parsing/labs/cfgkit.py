"""cfgkit — 第 19 章 lab 共用的 CFG / CNF / CKY / PARSEVAL 工具.

只依赖标准库。所有 lab 脚本都从这里取文法与算法，保证各 lab 用的是同一份实现。
文法：书中图 19.8 的 L1（含词汇规则），外加 §19.5 大象例句所需的 5 个词。
"""
from collections import defaultdict

# ---- 图 19.8 的 L1 文法（非终结符规则） ----
L1_RULES = [
    ("S", ("NP", "VP")),
    ("S", ("Aux", "NP", "VP")),
    ("S", ("VP",)),
    ("NP", ("Pronoun",)),
    ("NP", ("Proper-Noun",)),
    ("NP", ("Det", "Nominal")),
    ("Nominal", ("Noun",)),
    ("Nominal", ("Nominal", "Noun")),
    ("Nominal", ("Nominal", "PP")),
    ("VP", ("Verb",)),
    ("VP", ("Verb", "NP")),
    ("VP", ("Verb", "NP", "PP")),
    ("VP", ("Verb", "PP")),
    ("VP", ("VP", "PP")),
    ("PP", ("Preposition", "NP")),
]

# ---- 词库（L1 + §19.5 例句） ----
LEXICON = {
    "that": "Det", "this": "Det", "the": "Det", "a": "Det", "an": "Det", "my": "Det",
    "book": "Noun", "flight": "Noun", "meal": "Noun", "money": "Noun",
    "elephant": "Noun", "pajamas": "Noun", "shot": "Verb",
    "include": "Verb", "prefer": "Verb",
    "i": "Pronoun", "she": "Pronoun", "me": "Pronoun",
    "houston": "Proper-Noun", "united": "Proper-Noun",
    "does": "Aux",
    "from": "Preposition", "to": "Preposition", "on": "Preposition",
    "near": "Preposition", "through": "Preposition", "in": "Preposition",
}
# 同一个词既是 Noun 又是 Verb：book（书中图 19.8 就是这样）
LEXICON_AMBIG = dict(LEXICON)
LEXICON_AMBIG["book"] = "Noun"  # 主词性；book 作动词的情形由 AMBIG_POS 追加

AMBIG_POS = {"book": ["Noun", "Verb"]}

POS_TAGS = sorted({p for p in LEXICON.values()} | {"Proper-Noun"})


POS_OF = {}
for _w, _p in LEXICON.items():
    POS_OF.setdefault(_w, []).append(_p)
POS_IDX = {p: i for i, p in enumerate(sorted(set(LEXICON.values())))}
NONT = {a for a, _ in L1_RULES}


def pos_of(word, ambig=True):
    if ambig and word in AMBIG_POS:
        return AMBIG_POS[word]
    return [LEXICON[word]] if word in LEXICON else []


# ---------------------------------------------------------------- CNF 转换
def to_cnf(rules, lexicon, ambig=True):
    """返回 (cnf_rules, dummy_of_terminal)。消单元产生式、提终结符、二元化。"""
    nonterms = {a for a, _ in rules} | set(lexicon.values())
    term_dummy = {}

    def promote(sym):
        if sym in nonterms:
            return sym
        d = "T_" + sym
        term_dummy[d] = sym
        return d

    work = []
    for a, rhs in rules:
        work.append((a, tuple(promote(s) for s in rhs)))
    for w in lexicon:
        for p in pos_of(w, ambig):
            work.append((p, (w,)))          # 词汇规则已是 CNF 形状（A -> w）

    # 单元产生式闭包
    units = defaultdict(set)
    nonunit = []
    for a, rhs in work:
        if len(rhs) == 1 and rhs[0] in nonterms:
            units[a].add(rhs[0])
        else:
            nonunit.append((a, rhs))

    def closure(a):
        seen, stack = {a}, [a]
        while stack:
            x = stack.pop()
            for y in units[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        return seen

    out = []
    for a, rhs in nonunit:
        out.append((a, rhs))
    for a in sorted(nonterms):
        for b in closure(a):
            if b == a:
                continue
            for c, rhs in nonunit:
                if c == b:
                    out.append((a, rhs))

    # 二元化（自左向右，命名 X1, X2, ...）
    final = []
    counter = [0]

    def fresh():
        counter[0] += 1
        return "X%d" % counter[0]

    for a, rhs in out:
        if len(rhs) <= 2:
            final.append((a, rhs))
            continue
        cur = rhs
        left = a
        while len(cur) > 2:
            x = fresh()
            final.append((left, (cur[0], x)))
            cur = cur[1:]
            left = x
        final.append((left, cur))

    # 去重、去空
    seen = set()
    dedup = []
    for a, rhs in final:
        if (a, rhs) in seen:
            continue
        seen.add((a, rhs))
        dedup.append((a, rhs))
    return dedup, term_dummy


def rule_index(cnf_rules):
    """(B, C) -> [A]，以及 A -> w 的词汇表。"""
    binary = defaultdict(list)
    lexical = defaultdict(list)
    unary_term = defaultdict(list)
    for a, rhs in cnf_rules:
        if len(rhs) == 2:
            binary[(rhs[0], rhs[1])].append(a)
        elif len(rhs) == 1:
            lexical[rhs[0]].append(a)   # A -> w（w 是终结符）
    return binary, lexical


# ---------------------------------------------------------------- 通用成员判定
def accepts(words, rules, lexicon, ambig=True):
    """不要求 CNF 的自底向上图表识别（单调不动点），用于验证 CNF 转换不改变语言。

    与 cfgkit.cky 完全独立：不依赖二元化，可处理任意长度右部与单元产生式。
    """
    n = len(words)
    prods = [(a, rhs) for a, rhs in rules]
    for w in lexicon:
        for p in pos_of(w, ambig):
            prods.append((p, (w,)))

    chart = defaultdict(set)          # (i, j) -> 能导出 words[i:j] 的符号
    for i, w in enumerate(words):
        chart[(i, i + 1)].add(w)      # 终结符自身也算一个符号
        for p in pos_of(w, ambig):
            chart[(i, i + 1)].add(p)

    changed = True
    while changed:
        changed = False
        for a, rhs in prods:
            for i in range(n):
                states = {i}
                for sym in rhs:
                    nxt = set()
                    for s in states:
                        for j in range(s + 1, n + 1):
                            if sym in chart[(s, j)]:
                                nxt.add(j)
                    states = nxt
                    if not states:
                        break
                for j in states:
                    if a not in chart[(i, j)]:
                        chart[(i, j)].add(a)
                        changed = True
    return "S" in chart[(0, n)]


# ---------------------------------------------------------------- CKY
def cky(words, cnf_rules, lexicon, ambig=True, max_len=None):
    """返回 (table, back)。table[i][j] = {非终结符}；back[(i,j,A)] = [(k,B,C)]。"""
    n = len(words)
    binary, lexical = rule_index(cnf_rules)
    table = [[set() for _ in range(n + 1)] for _ in range(n + 1)]
    back = defaultdict(list)

    for i, w in enumerate(words):
        for a in lexical.get(w, ()):
            table[i][i + 1].add(a)
            back[(i, i + 1, a)].append(("lex", w))

    for span in range(2, n + 1):
        for i in range(0, n - span + 1):
            j = i + span
            for k in range(i + 1, j):
                for b in table[i][k]:
                    for c in table[k][j]:
                        for a in binary.get((b, c), ()):
                            if a not in table[i][j]:
                                table[i][j].add(a)
                            back[(i, j, a)].append((k, b, c))
    return table, back


def count_trees(table, back, i, j, sym, memo=None):
    if memo is None:
        memo = {}
    key = (i, j, sym)
    if key in memo:
        return memo[key]
    total = 0
    for item in back.get((i, j, sym), ()):
        if item[0] == "lex":
            total += 1
        else:
            k, b, c = item
            total += count_trees(table, back, i, k, b, memo) * count_trees(table, back, k, j, c, memo)
    memo[key] = total
    return total


def trees(table, back, i, j, sym, limit=10000):
    out = []
    for item in back.get((i, j, sym), ()):
        if item[0] == "lex":
            out.append((sym, [(item[1],)]))
        else:
            k, b, c = item
            for lb in trees(table, back, i, k, b, limit):
                for rc in trees(table, back, k, j, c, limit):
                    out.append((sym, [lb, rc]))
                    if len(out) >= limit:
                        return out
    return out


def bracket(tree):
    sym, kids = tree
    if len(kids) == 1 and len(kids[0]) == 1:
        return "(%s %s)" % (sym, kids[0][0])
    return "(%s %s)" % (sym, " ".join(bracket(k) for k in kids))


def unit_closure_map(rules):
    nts = {a for a, _ in rules}
    direct = defaultdict(set)
    for a, rhs in rules:
        if len(rhs) == 1 and rhs[0] in nts:
            direct[a].add(rhs[0])
    out = {}
    for a in nts:
        seen, stack = {a}, [a]
        while stack:
            x = stack.pop()
            for y in direct[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
        out[a] = seen
    return out


def unbinarize(tree, rules=None, prefix="X"):
    """删掉二元化引入的哑非终结符，并按原始文法恢复被消掉的单元产生式链。"""
    rules = L1_RULES if rules is None else rules
    closure = unit_closure_map(rules)
    orig = defaultdict(list)
    for a, rhs in rules:
        orig[tuple(rhs)].append(a)

    def is_dummy(s):
        return s.startswith(prefix) and s[len(prefix):].isdigit()

    def rec(node):
        sym, kids = node
        if len(kids) == 1 and len(kids[0]) == 1:
            return node
        newkids = []
        for k in kids:
            k2 = rec(k)
            if is_dummy(k2[0]):
                newkids.extend(k2[1])
            else:
                newkids.append(k2)
        labels = tuple(k[0] for k in newkids)
        if sym in orig.get(labels, ()):
            return (sym, newkids)
        cands = [b for b in orig.get(labels, ()) if b in closure.get(sym, {sym})]
        if cands and cands[0] != sym:
            return (sym, [(cands[0], newkids)])
        return (sym, newkids)

    return rec(tree)


# ---------------------------------------------------------------- 树工具
def spans_of(tree, i=0, include_pos=True):
    """返回 (spans, end)。spans = [(i, j, label)]。"""
    sym, kids = tree
    if len(kids) == 1 and len(kids[0]) == 1:
        return ([(i, i + 1, sym)] if include_pos else []), i + 1
    spans, cur = [], i
    for k in kids:
        s, cur = spans_of(k, cur, include_pos)
        spans.extend(s)
    if include_pos or len(kids) > 1:
        spans.append((i, cur, sym))
    return spans, cur


def words_of(tree):
    sym, kids = tree
    if len(kids) == 1 and len(kids[0]) == 1:
        return [kids[0][0]]
    out = []
    for k in kids:
        out.extend(words_of(k))
    return out


def crossing_brackets(hyp, gold):
    hs = {(i, j) for i, j, _ in spans_of(hyp, include_pos=False)[0]}
    gs = {(i, j) for i, j, _ in spans_of(gold, include_pos=False)[0]}

    def cross(a, b):
        return (a[0] < b[0] < a[1] < b[1]) or (b[0] < a[0] < b[1] < a[1])

    return sum(1 for a in hs for b in gs if cross(a, b))


def parseval(hyp, gold, include_pos=True, collapse_labels=False):
    hs = spans_of(hyp, include_pos=include_pos)[0]
    gs = spans_of(gold, include_pos=include_pos)[0]
    if collapse_labels:
        hs = [(i, j, "X") for i, j, _ in hs]
        gs = [(i, j, "X") for i, j, _ in gs]
    hs, gs = set(hs), set(gs)
    correct = len(hs & gs)
    p = correct / len(hs) if hs else 0.0
    r = correct / len(gs) if gs else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"p": p, "r": r, "f1": f, "n_hyp": len(hs), "n_gold": len(gs),
            "correct": correct, "crossing": crossing_brackets(hyp, gold)}
