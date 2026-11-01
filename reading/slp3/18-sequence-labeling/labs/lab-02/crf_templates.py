#!/usr/bin/env python3
"""lab-02: 手写线性链 CRF（numpy + SGD + 前向-后向 + 维特比），对比「有/无词形特征」。

模板: <y,x> 发射、<y_prev,y> 转移、<y,shape(x)> 词形。
测试句含未登录词 Zorbly（仅词形 Xx 可见），用来检验模板是否救得回来。
"""
import itertools
import json
import math
import os
from collections import Counter, defaultdict

import numpy as np

TAGS = ["DT", "JJ", "NN", "NNP", "VB"]
TRAIN = [
    ("the dog barks", "DT NN VB"),
    ("a cat sleeps", "DT NN VB"),
    ("the big dog barks", "DT JJ NN VB"),
    ("the cat sees a dog", "DT NN VB DT NN"),
    ("a big cat sleeps", "DT JJ NN VB"),
    ("Maria bought a car", "NNP VB DT NN"),
    ("John reads the book", "NNP VB DT NN"),
]
TESTS = [("Zorbly bought a car", "NNP VB DT NN"),
         ("Zorbly", "NNP")]  # 第二句剥掉上下文，只看词形先验
L2, LR, EPOCHS = 1e-3, 0.08, 400


def shape(w):
    if w.isdigit():
        return "d"
    if w.islower():
        return "x"
    if w[0].isupper() and w[1:].islower():
        return "Xx"
    return "X"


def feats(w, i):
    """位置 i 的词可触发的特征 key（不含标签）"""
    return [("E", w), ("S", shape(w))]


def sent_feats(sent, with_shape):
    words, tags = sent[0].split(), sent[1].split()
    node = []
    for i, w in enumerate(words):
        fs = [("E", w)] + ([("S", shape(w))] if with_shape else [])
        node.append(fs)
    edge = [("<s>", t) for t in TAGS]  # 占位，真实边由 (prev,y) 拼
    return words, tags, node, edge


def build_space(data, with_shape):
    """特征空间：训练集上所有 (节点特征×标签) 与 (边特征)"""
    keys = set()
    for sent in data:
        words, tags, node, _ = sent_feats(sent, with_shape)
        for i, w in enumerate(words):
            for f in node[i]:
                for y in TAGS:
                    keys.add((f, y))
        for i in range(len(words)):
            prevs = ["<s>"] if i == 0 else TAGS
            for p in prevs:
                for y in TAGS:
                    keys.add((("T", p, y), None))
    return {k: 0.0 for k in sorted(keys, key=str)}


def unary(w, node_i, y):
    return sum(w.get((f, y), 0.0) for f in node_i)


def trans(w, p, y):
    return w.get((("T", p, y), None), 0.0)


def lse(x):
    m = max(x)
    return m + math.log(sum(math.exp(v - m) for v in x))


def forward_backward(w, node, tags):
    T, n = len(node), len(TAGS)
    U = [[unary(w, node[i], y) for y in TAGS] for i in range(T)]
    A = [[trans(w, p, y) for y in TAGS] for p in TAGS]
    al = [[0.0] * n for _ in range(T)]
    be = [[0.0] * n for _ in range(T)]
    al[0] = U[0][:]
    for i in range(1, T):
        for y in range(n):
            al[i][y] = lse([al[i - 1][p] + A[p][y] for p in range(n)]) + U[i][y]
    for i in range(T - 2, -1, -1):
        for p in range(n):
            be[i][p] = lse([A[p][y] + U[i + 1][y] + be[i + 1][y] for y in range(n)])
    logZ = lse(al[T - 1])
    marg = [[math.exp(al[i][y] + be[i][y] - logZ) for y in range(n)] for i in range(T)]
    xi = {}
    for i in range(1, T):
        for p in range(n):
            for y in range(n):
                xi[(i, p, y)] = math.exp(al[i - 1][p] + A[p][y] + U[i][y] + be[i][y] - logZ)
    return logZ, U, A, marg, xi


def viterbi(w, node, start=None, tags=None):
    """start: 起始权重（相当于 <s> 的转移）；tags: 标签集，缺省用本 lab 的 5 标签集"""
    tags = tags or TAGS
    T, n = len(node), len(tags)
    U = [[unary(w, node[i], y) for y in tags] for i in range(T)]
    A = [[trans(w, p, y) for y in tags] for p in tags]
    V = [[0.0] * n for _ in range(T)]
    bp = [[0] * n for _ in range(T)]
    V[0] = [U[0][y] + (start[y] if start is not None else 0.0) for y in range(n)]
    for i in range(1, T):
        for y in range(n):
            cand = [V[i - 1][p] + A[p][y] for p in range(n)]
            p = int(np.argmax(cand))
            V[i][y], bp[i][y] = cand[p] + U[i][y], p
    y = int(np.argmax(V[T - 1]))
    path = [y]
    for i in range(T - 1, 0, -1):
        y = bp[i][y]
        path.append(y)
    return [tags[k] for k in path[::-1]], max(V[-1])


def train(with_shape):
    w = build_space(TRAIN, with_shape)
    hist = []
    for ep in range(EPOCHS):
        grad = defaultdict(float)
        nll = 0.0
        for sent in TRAIN:
            words, tags, node, _ = sent_feats(sent, with_shape)
            logZ, U, A, marg, xi = forward_backward(w, node, tags)
            gold = [TAGS.index(t) for t in tags]
            nll += logZ - sum(U[i][gold[i]] for i in range(len(gold)))
            nll -= sum(A[gold[i - 1]][gold[i]] for i in range(1, len(gold)))
            for i in range(len(words)):
                for f in node[i]:
                    for y in range(len(TAGS)):
                        grad[(f, TAGS[y])] += (1.0 if gold[i] == y else 0.0) - marg[i][y]
            for i in range(1, len(words)):
                for p in range(len(TAGS)):
                    for y in range(len(TAGS)):
                        emp = 1.0 if (gold[i - 1] == p and gold[i] == y) else 0.0
                        grad[(("T", TAGS[p], TAGS[y]), None)] += emp - xi[(i, p, y)]
        for k in list(w):
            w[k] += LR * (grad[k] / len(TRAIN) - L2 * w[k])
        hist.append(nll / len(TRAIN))
    return w, hist


# ---- HMM 当作 CRF 的特例：log 转移/发射直接当权重 ----
H_TAGS = ["NNP", "MD", "VB", "JJ", "NN", "RB", "DT"]
H_WORDS = ["Janet", "will", "back", "the", "bill"]
H_PI = [0.2767, 0.0006, 0.0031, 0.0453, 0.0449, 0.0510, 0.2026]
H_A = [[0.3777, 0.0110, 0.0009, 0.0084, 0.0584, 0.0090, 0.0025],
       [0.0008, 0.0002, 0.7968, 0.0005, 0.0008, 0.1698, 0.0041],
       [0.0322, 0.0005, 0.0050, 0.0837, 0.0615, 0.0514, 0.2231],
       [0.0366, 0.0004, 0.0001, 0.0733, 0.4509, 0.0036, 0.0036],
       [0.0096, 0.0176, 0.0014, 0.0086, 0.1216, 0.0177, 0.0068],
       [0.0068, 0.0102, 0.1011, 0.1012, 0.0120, 0.0728, 0.0479],
       [0.1147, 0.0021, 0.0002, 0.2157, 0.4744, 0.0102, 0.0017]]
H_B = [[0.000032, 0, 0, 0.000048, 0], [0, 0.308431, 0, 0, 0],
       [0, 0.000028, 0.000672, 0, 0.000028], [0, 0, 0.000340, 0, 0],
       [0, 0.000200, 0.000223, 0, 0.002337], [0, 0, 0.010446, 0, 0],
       [0, 0, 0, 0.506099, 0]]


def _lg(x):
    return math.log(x) if x > 0 else float("-inf")


def hmm_viterbi_direct():
    n, T = len(H_TAGS), len(H_WORDS)
    V = [[float("-inf")] * n for _ in range(T)]
    bp = [[0] * n for _ in range(T)]
    V[0] = [_lg(H_PI[j]) + _lg(H_B[j][0]) for j in range(n)]
    for t in range(1, T):
        for j in range(n):
            cand = [V[t - 1][i] + _lg(H_A[i][j]) for i in range(n)]
            i = int(np.argmax(cand))
            V[t][j], bp[t][j] = cand[i] + _lg(H_B[j][t]), i
    j = int(np.argmax(V[T - 1]))
    path = [j]
    for t in range(T - 1, 0, -1):
        j = bp[t][j]; path.append(j)
    return [H_TAGS[k] for k in path[::-1]], max(V[-1])


def hmm_as_crf():
    """同一张 A/B 表写成权重字典，交给 lab-02 的通用维特比"""
    w = {}
    for i, p in enumerate(H_TAGS):
        for j, y in enumerate(H_TAGS):
            w[(("T", p, y), None)] = _lg(H_A[i][j])
    for j, y in enumerate(H_TAGS):
        for k, word in enumerate(H_WORDS):
            w[(("E", word), y)] = _lg(H_B[j][k])
    node = [[("E", word)] for word in H_WORDS]
    path, score = viterbi(w, node, start=[_lg(p) for p in H_PI], tags=H_TAGS)
    return path, score


def main():
    os.makedirs("out", exist_ok=True)
    report = {"feature_space_size": len(build_space(TRAIN, True))}
    for with_shape in (True, False):
        name = "with_shape" if with_shape else "no_shape"
        w, hist = train(with_shape)
        cases = []
        for test in TESTS:
            words, gold, node, _ = sent_feats(test, with_shape)
            path, score = viterbi(w, node)
            cases.append({"sent": test[0], "gold": gold, "decoded": path,
                          "correct": path == gold, "score": round(float(score), 4)})
        report[name] = {
            "epoch_nll_first_last": [round(hist[0], 4), round(hist[-1], 4)],
            "cases": cases,
            "correct_all": all(c["correct"] for c in cases),
            "top_weights": sorted(
                ((f"{k[0]}=>{k[1]}", round(v, 3)) for k, v in w.items() if abs(v) > 0.5),
                key=lambda x: -abs(x[1]))[:8],
            "shape_weights": sorted(
                ((k[0][1] + "/" + str(k[1]), round(v, 3)) for k, v in w.items()
                 if k[0][0] == "S"),
                key=lambda x: -abs(x[1]))[:6],
        }
    p1, s1 = hmm_viterbi_direct()
    p2, s2 = hmm_as_crf()
    report["hmm_equals_crf"] = {"hmm_path": p1, "crf_path": p2, "paths_equal": p1 == p2,
                                "score_diff": float(abs(s1 - s2))}
    print("HMM 当 CRF 用:", p1, p2, "score_diff=", f"{abs(s1 - s2):.2e}")
    # 同一模型下 HMM 式打分与 CRF 打分共用解码器：这里直接展示 U/A 的来源不同
    with open("out/decode.json", "w") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    with open("out/weights.csv", "w") as f:
        f.write("template,arg,tag,weight\n")
        for k, v in sorted(train(True)[0].items(), key=lambda x: -abs(x[1]))[:20]:
            f.write(f"{k[0][0]},\"{k[0][1:]}\",{k[1]},{v:.4f}\n")
    for k, v in report.items():
        if not isinstance(v, dict) or "cases" not in v:
            continue
        print(k, "nll", v["epoch_nll_first_last"], "all_ok", v["correct_all"])
        for c in v["cases"]:
            print("   ", f"{c['sent']:<20}", " ".join(c["decoded"]), "ok=", c["correct"])


if __name__ == "__main__":
    main()
