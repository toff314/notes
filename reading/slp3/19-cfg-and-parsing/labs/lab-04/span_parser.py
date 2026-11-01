#!/usr/bin/env python3
"""lab-04：跨度打分 + CKY 解码 vs 贪心解码（§19.7）。

不依赖任何神经库：用 225 维离散特征 + 结构化感知机（structured perceptron）训练
一个「跨度 (i,j) 是不是标签 l 的成分」打分器，再用两种解码比较：

  CKY    —— 对切分点做 max，得到全局最高分的树（保证合法）；
  greedy —— 每个跨度独立取 argmax，分数 > 0 才留下，最后检查能否拼成覆盖全句的树
             （对应 §19.7「贪心方法不保证能产生一棵树」）。

数据：由 L1X 文法随机采样并二叉化得到树库，金标准树自带，故可算 exact match。
产出（out/）：dataset.csv、metrics.json、test_pred.json（供 lab-05 计算 PARSEVAL）、
              model.json、failures.txt
"""
import csv
import json
import os
import random
import sys
import zlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import cfgkit as K  # noqa: E402

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

RULES = K.L1_RULES + [("NP", ("NP", "PP"))]
POS = sorted(set(K.LEXICON.values()))
INTERNAL = ["S", "NP", "VP", "PP", "Nominal", "X"]
LAB = {l: i for i, l in enumerate(INTERNAL + POS)}
L = len(LAB)
UNARY = [(a, r[0]) for a, r in RULES if len(r) == 1]
D = 1 + 8 + 160 + 8 + 48
rng = random.Random(19)


# ---------------------------------------------------------------- 采样与二叉化
def sample(sym, depth):
    if sym in POS:
        return (sym, [(rng.choice([w for w, p in K.LEXICON.items() if p == sym]),)])
    cands = [r for a, r in RULES if a == sym]
    if depth >= 6:
        cands = sorted(cands, key=len)[:2]
    return (sym, [sample(s, depth + 1) for s in rng.choice(cands)])


def words_of(t):
    if len(t[1]) == 1 and len(t[1][0]) == 1:
        return [t[1][0][0]]
    out = []
    for k in t[1]:
        out += words_of(k)
    return out


def binarize(t):
    """左折叠成二叉；X 是二元化引入的哑节点（与 §19.6.1 同一套做法）。"""
    sym, kids = t
    if len(kids) == 1 and len(kids[0]) == 1:
        return t
    kids = [binarize(k) for k in kids]
    if len(kids) <= 2:
        return (sym, kids)
    node = kids[-2:]
    for k in reversed(kids[:-2]):
        node = [k, ("X", node)]
    return (sym, node)


def gold_spans(t, i=0, acc=None):
    """返回 {(i,j): {label,...}}；一元链条会让同一个跨度带上两个标签。"""
    if acc is None:
        acc = {}
    sym, kids = t
    if len(kids) == 1 and len(kids[0]) == 1:
        acc.setdefault((i, i + 1), set()).add(sym)
        return i + 1, acc
    cur = i
    for k in kids:
        cur, acc = gold_spans(k, cur, acc)
    acc.setdefault((i, cur), set()).add(sym)
    return cur, acc


def make_data(n, lo=4, hi=11):
    data = []
    while len(data) < n:
        t = binarize(sample("S", 0))
        w = words_of(t)
        if lo <= len(w) <= hi:
            data.append((w, t, gold_spans(t)[1]))
    return data


TRAIN = make_data(1200)
TEST = make_data(200)


# ---------------------------------------------------------------- 特征
def feats(words, i, j):
    n = len(words)
    v = np.zeros(D)
    v[0] = 1.0
    v[min(j - i, 8)] = 1.0                       # 长度 1..8，9 起合并
    base = 9
    for slot, idx in enumerate((i, j - 1, min(i + 1, n - 1), max(j - 2, 0))):
        v[base + slot * 40 + zlib.crc32(words[idx].encode()) % 40] = 1.0
    base2 = 169
    for w in words[i:j]:                          # 跨度内可能出现哪些词类
        for t in K.POS_OF.get(w, ()):
            v[base2 + K.POS_IDX[t]] = 1.0
    base3 = 177
    for w in words[i:j]:                          # 跨度内词袋
        v[base3 + zlib.crc32(w.encode()) % 48] += 0.5
    return v


# ---------------------------------------------------------------- 解码器
def decode(words, W, use_unary=True):
    n = len(words)
    S = {}
    for i in range(n):
        for j in range(i + 1, n + 1):
            S[(i, j)] = feats(words, i, j) @ W.T      # 长度 L 的分数向量
    best, arg = {}, {}

    def close(nb, na, i, j):
        if not use_unary:
            return
        for _ in range(3):
            for a, b in UNARY:
                if b in nb and nb[b] + S[(i, j)][LAB[a]] > nb.get(a, -1e18):
                    nb[a] = nb[b] + S[(i, j)][LAB[a]]
                    na[a] = ("unary", b)

    for i in range(n):
        nb = {p: float(S[(i, i + 1)][LAB[p]]) for p in POS}
        na = {p: ("lex",) for p in POS}
        close(nb, na, i, i + 1)
        best[(i, i + 1)], arg[(i, i + 1)] = nb, na

    for span in range(2, n + 1):
        for i in range(0, n - span + 1):
            j = i + span
            root, rarg = -1e18, None
            for k in range(i + 1, j):
                if (i, k) not in best or (k, j) not in best:
                    continue
                lb, rb = best[(i, k)], best[(k, j)]
                ln, rn = list(lb), list(rb)
                M = np.array([lb[x] for x in ln])[:, None] + np.array([rb[y] for y in rn])[None, :]
                idx = int(np.argmax(M))
                if float(M.flat[idx]) > root:
                    root = float(M.flat[idx])
                    rarg = (k, ln[idx // len(rn)], rn[idx % len(rn)])
            if rarg is None:
                continue
            sv = S[(i, j)]
            nb = {l: root + float(sv[LAB[l]]) for l in INTERNAL}
            na = {l: ("split",) + rarg for l in INTERNAL}
            close(nb, na, i, j)
            best[(i, j)], arg[(i, j)] = nb, na

    if (0, n) not in best:
        return None
    root_label = max(best[(0, n)], key=best[(0, n)].get)
    return build(arg, 0, n, root_label)


def build(arg, i, j, lab):
    a = arg[(i, j)][lab]
    if a[0] == "lex":
        return (lab, [("<w>",)])
    if a[0] == "unary":
        return (lab, [build(arg, i, j, a[1])])
    _, k, lc, rc = a
    return (lab, [build(arg, i, k, lc), build(arg, k, j, rc)])


def tree_spans(t, i=0, acc=None):
    if acc is None:
        acc = {}
    sym, kids = t
    if len(kids) == 1 and len(kids[0]) == 1:
        acc.setdefault((i, i + 1), set()).add(sym)
        return i + 1, acc
    if len(kids) == 1:                       # 一元
        cur, acc = tree_spans(kids[0], i, acc)
        acc.setdefault((i, cur), set()).add(sym)
        return cur, acc
    cur = i
    for k in kids:
        cur, acc = tree_spans(k, cur, acc)
    acc.setdefault((i, cur), set()).add(sym)
    return cur, acc


def brack(t, words, i=0):
    lab, kids = t
    if len(kids) == 1 and kids[0][0] == "<w>":
        return "(%s %s)" % (lab, words[i]), i + 1
    parts, cur = [], i
    for k in kids:
        s, cur = brack(k, words, cur)
        parts.append(s)
    return "(%s %s)" % (lab, " ".join(parts)), cur


def greedy(words, W, thr=0.0):
    n = len(words)
    chosen = {}
    for i in range(n):
        for j in range(i + 1, n + 1):
            sv = feats(words, i, j) @ W.T
            labs = POS if j - i == 1 else INTERNAL
            l = max(labs, key=lambda x: sv[LAB[x]])
            if sv[LAB[l]] > thr:
                chosen.setdefault((i, j), set()).add(l)
    ok = {}

    def valid(i, j):
        if (i, j) not in chosen:
            return False
        if j - i == 1:
            return True
        if (i, j) in ok:
            return ok[(i, j)]
        ok[(i, j)] = False
        r = any(valid(i, k) and valid(k, j) for k in range(i + 1, j))
        ok[(i, j)] = r
        return r

    if not valid(0, n):
        return None, chosen
    return recover(chosen, 0, n), chosen


def recover(chosen, i, j):
    if j - i == 1:
        return (sorted(chosen[(i, j)])[0], [("<w>",)])
    for k in range(i + 1, j):
        if (i, k) in chosen and (k, j) in chosen and usable(chosen, i, k) and usable(chosen, k, j):
            return (sorted(chosen[(i, j)])[0], [recover(chosen, i, k), recover(chosen, k, j)])
    return (sorted(chosen[(i, j)])[0], [("<w>",)] * 0 or [("{unreachable}", [("<w>",)])])


def usable(chosen, i, j):
    if j - i == 1:
        return True
    return any((i, k) in chosen and (k, j) in chosen and usable(chosen, i, k) and usable(chosen, k, j)
               for k in range(i + 1, j))


# ---------------------------------------------------------------- 感知机训练
W = np.zeros((L, D))


def train(epochs=8):
    for ep in range(epochs):
        rng.shuffle(TRAIN)
        bad = 0
        for words, tree, gold in TRAIN:
            pred = decode(words, W)
            ps = tree_spans(pred)[1] if pred else {}
            if ps == gold:
                continue
            bad += 1
            for (i, j), labs in gold.items():
                f = feats(words, i, j)
                for l in labs:
                    W[LAB[l]] += f
            for (i, j), labs in ps.items():
                f = feats(words, i, j)
                for l in labs:
                    W[LAB[l]] -= f
        print("epoch %d  训练集错误 %d/%d" % (ep + 1, bad, len(TRAIN)))


train()
train_acc = sum(1 for w, t, g in TRAIN if (lambda p: p is not None and tree_spans(p)[1] == g)(decode(w, W))) / len(TRAIN)

# ---------------------------------------------------------------- 测试
em_c = em_g = valid_g = 0
records, fails = [], []
for words, tree, gold in TEST:
    pc = decode(words, W)
    pg, chosen = greedy(words, W)
    sc = tree_spans(pc)[1] if pc else {}
    sg = tree_spans(pg)[1] if pg else {}
    em_c += int(sc == gold)
    em_g += int(sg == gold)
    valid_g += int(pg is not None)
    records.append({"words": words,
                    "gold": K.bracket(tree),
                    "cky": brack(pc, words)[0] if pc else "",
                    "greedy": brack(pg, words)[0] if pg else "",
                    "cky_spans": sorted("%d-%d:%s" % (i, j, l) for (i, j), ls in sc.items() for l in ls),
                    "gold_spans": sorted("%d-%d:%s" % (i, j, l) for (i, j), ls in gold.items() for l in ls),
                    "greedy_spans": sorted("%d-%d:%s" % (i, j, l) for (i, j), ls in sg.items() for l in ls)})
    if pg is None and len(fails) < 5:
        fails.append(" ".join(words) + "\n  gold: " + K.bracket(tree))

n = len(TEST)
metrics = {
    "train_sentences": len(TRAIN),
    "test_sentences": n,
    "train_exact_match": round(train_acc, 4),
    "exact_match_cky": round(em_c / n, 4),
    "exact_match_greedy": round(em_g / n, 4),
    "greedy_valid_tree_rate": round(valid_g / n, 4),
    "avg_gold_spans": round(sum(len(l) for _, _, g in TEST for l in g.values()) / n, 2),
}
json.dump(metrics, open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
json.dump(records, open(os.path.join(OUT, "test_pred.json"), "w", encoding="utf-8"),
          ensure_ascii=False)
json.dump({"D": D, "labels": INTERNAL + POS, "algo": "structured perceptron",
           "epochs": 8, "note": "固定随机种子 19；重跑本脚本即可复现"}, 
          open(os.path.join(OUT, "model.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "dataset.csv"), "w", newline="", encoding="utf-8") as f:
    wr = csv.writer(f)
    wr.writerow(["split", "n_sentences", "min_len", "max_len", "mean_len"])
    for name, d in (("train", TRAIN), ("test", TEST)):
        ls = [len(w) for w, _, _ in d]
        wr.writerow([name, len(d), min(ls), max(ls), round(sum(ls) / len(ls), 2)])
open(os.path.join(OUT, "failures.txt"), "w", encoding="utf-8").write("\n\n".join(fails) or "（无）")

print(json.dumps(metrics, ensure_ascii=False, indent=2))
for f_ in fails:
    print("\n贪心拼不成树的例子：\n" + f_)
