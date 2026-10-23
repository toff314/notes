#!/usr/bin/env python3
"""lab-02: 从零实现带负采样的 skip-gram（SGNS），并做梯度校验与类比实验。

对应《Speech and Language Processing》第 3 版 §5.5.1（分类器）、§5.5.2（损失、
梯度、SGD 更新）、§5.7（平行四边形类比及其失败模式）。

实现要点（与书中公式对应）：
  P(+|w,c) = sigmoid(c·w)                       (5.15)
  L = -[log σ(c_pos·w) + Σ_i log σ(-c_neg_i·w)] (5.21)
  ∂L/∂c_pos = [σ(c_pos·w) - 1] w                (5.22)
  ∂L/∂c_neg = [σ(c_neg·w)] w                    (5.23)
  ∂L/∂w     = [σ(c_pos·w)-1] c_pos + Σ_i [σ(c_neg_i·w)] c_neg_i   (5.24)

运行：python3 lab02_sgns_from_scratch.py [--epochs 12] [--dim 40]
产物：out/loss.csv, out/vectors.csv, out/neighbors.csv, out/analogies.json,
      out/analogy_accuracy.csv, out/vector_arithmetic.png
"""
import argparse
import csv
import json
import os
import random

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

TEMPLATES = [
    "the king is male and royal",
    "the king rules from the throne",
    "the king wears the crown",
    "the queen is female and royal",
    "the queen rules from the throne",
    "the queen wears the crown",
    "the prince is young and royal",
    "the prince lives in the palace",
    "the princess is young and royal",
    "the princess lives in the palace",
    "the man is male and common",
    "the man works in the market",
    "the woman is female and common",
    "the woman works in the market",
    "the boy is young and common",
    "the boy plays in the street",
    "the girl is young and common",
    "the girl plays in the street",
    "the father is male and a parent",
    "the father works at home",
    "the mother is female and a parent",
    "the mother works at home",
    "{city} is the capital of {country} and it is a city",
    "{city} has a river and a large population",
    "the capital of {country} is {city}",
    "big has degree one",
    "bigger has degree two",
    "biggest has degree three",
    "small has degree one",
    "smaller has degree two",
    "smallest has degree three",
    "cold has degree one",
    "colder has degree two",
    "coldest has degree three",
    "warm has degree one",
    "warmer has degree two",
    "warmest has degree three",
    "tall has degree one",
    "taller has degree two",
    "tallest has degree three",
]

CAPITALS = [
    ("paris", "france"), ("rome", "italy"), ("tokyo", "japan"),
    ("berlin", "germany"), ("madrid", "spain"), ("london", "england"),
]

FILLER = ["the", "a", "is", "and", "of", "it", "has"]


def make_corpus(repeats=30, seed=0):
    rng = random.Random(seed)
    sents = []
    for t in TEMPLATES:
        if "{city}" in t:
            for city, country in CAPITALS:
                s = t.format(city=city, country=country)
                for _ in range(repeats // 2):
                    sents.append(s)
        else:
            for _ in range(repeats):
                sents.append(t)
    # 少量填充句，让高频虚词也有稳定的上下文
    for _ in range(200):
        sents.append(" ".join(rng.choice(FILLER) for _ in range(rng.randint(3, 7))))
    rng.shuffle(sents)
    return [s.split() for s in sents]


def build_vocab(docs, min_count=1):
    freq = {}
    for d in docs:
        for w in d:
            freq[w] = freq.get(w, 0) + 1
    vocab = sorted([w for w, c in freq.items() if c >= min_count])
    return vocab, freq


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def loss_and_grads(w, cpos, cnegs):
    """单组 (w, c_pos, c_negs) 的损失与解析梯度，供训练和数值校验共用。"""
    sp = float(sigmoid(cpos @ w))
    sn = sigmoid(cnegs @ w)
    loss = -(np.log(max(sp, 1e-12)) + np.log(np.maximum(1 - sn, 1e-12)).sum())
    g_w = (sp - 1.0) * cpos + sn @ cnegs
    g_cpos = (sp - 1.0) * w
    g_cnegs = sn[:, None] * w[None, :]
    return loss, g_w, g_cpos, g_cnegs


def gradient_check(seed=0):
    """有限差分校验式 5.22–5.24。返回最大相对误差。"""
    rng = np.random.default_rng(seed)
    d = 4
    w = rng.normal(size=d)
    cpos = rng.normal(size=d)
    cnegs = rng.normal(size=(3, d))
    _, g_w, g_cpos, g_cnegs = loss_and_grads(w, cpos, cnegs)
    eps = 1e-6
    errs = []

    def num_grad(vec, idx, kind):
        plus = vec.copy(); minus = vec.copy()
        plus[idx] += eps; minus[idx] -= eps
        if kind == "w":
            l1 = loss_and_grads(plus, cpos, cnegs)[0]
            l2 = loss_and_grads(minus, cpos, cnegs)[0]
        elif kind == "cpos":
            l1 = loss_and_grads(w, plus, cnegs)[0]
            l2 = loss_and_grads(w, minus, cnegs)[0]
        else:
            l1 = loss_and_grads(w, cpos, plus.reshape(1, -1))[0]
            l2 = loss_and_grads(w, cpos, minus.reshape(1, -1))[0]
        return (l1 - l2) / (2 * eps)

    for i in range(d):
        errs.append(abs(num_grad(w, i, "w") - g_w[i]) / max(1e-9, abs(g_w[i])))
        errs.append(abs(num_grad(cpos, i, "cpos") - g_cpos[i]) / max(1e-9, abs(g_cpos[i])))
    for r in range(cnegs.shape[0]):
        for i in range(d):
            errs.append(abs(num_grad(cnegs[r], i, "cneg") - g_cnegs[r, i]) / max(1e-9, abs(g_cnegs[r, i])))
    return float(max(errs))


def train(docs, vocab, dim=40, window=2, k=5, alpha=0.75, lr=0.05, epochs=12, seed=0):
    rng = np.random.default_rng(seed)
    idx = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    W = rng.normal(0, 0.1, size=(V, dim))
    C = rng.normal(0, 0.1, size=(V, dim))

    freq = np.zeros(V)
    for d in docs:
        for w in d:
            freq[idx[w]] += 1
    noise = freq ** alpha
    noise = noise / noise.sum()

    loss_curve = []
    for ep in range(epochs):
        total, n = 0.0, 0
        cur_lr = lr * (1.0 - 0.7 * ep / max(1, epochs))
        for tokens in docs:
            ids = [idx[w] for w in tokens]
            for pos, wi in enumerate(ids):
                span = rng.integers(1, window + 1)
                lo, hi = max(0, pos - span), min(len(ids), pos + span + 1)
                for j in range(lo, hi):
                    if j == pos:
                        continue
                    ci = ids[j]
                    negs = rng.choice(V, size=k, p=noise)
                    negs = negs[negs != wi]
                    if len(negs) == 0:
                        continue
                    w_vec = W[wi].copy()
                    c_pos = C[ci].copy()
                    loss, g_w, g_cpos, g_cnegs = loss_and_grads(w_vec, c_pos, C[negs])
                    total += loss; n += 1
                    W[wi] -= cur_lr * g_w
                    C[ci] -= cur_lr * g_cpos
                    C[negs] -= cur_lr * g_cnegs
        loss_curve.append((ep + 1, total / max(1, n)))
    return W, C, loss_curve, idx


def final_vectors(W, C):
    v = W + C
    norms = np.linalg.norm(v, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return v / norms


def top_neighbors(vocab, vecs, word, n=6):
    i = vocab.index(word)
    sims = vecs @ vecs[i]
    order = np.argsort(-sims)
    out = []
    for j in order:
        if j == i:
            continue
        out.append((vocab[j], float(sims[j])))
        if len(out) >= n:
            break
    return out


ANALOGIES = [
    ("king", "queen", "man", "woman"),
    ("king", "queen", "prince", "princess"),
    ("king", "queen", "father", "mother"),
    ("man", "woman", "boy", "girl"),
    ("prince", "princess", "boy", "girl"),
    ("paris", "france", "rome", "italy"),
    ("paris", "france", "tokyo", "japan"),
    ("rome", "italy", "berlin", "germany"),
    ("tokyo", "japan", "madrid", "spain"),
    ("berlin", "germany", "london", "england"),
    ("big", "bigger", "small", "smaller"),
    ("big", "bigger", "cold", "colder"),
    ("cold", "colder", "warm", "warmer"),
    ("small", "smaller", "tall", "taller"),
    ("tall", "taller", "big", "bigger"),
    ("france", "paris", "italy", "rome"),
    ("japan", "tokyo", "germany", "berlin"),
    ("woman", "man", "queen", "king"),
    ("girl", "boy", "princess", "prince"),
    ("bigger", "biggest", "smaller", "smallest"),
]


def run_analogies(vocab, vecs, exclude_inputs=True):
    rows = []
    hit = input_hit = miss = 0
    for a, b, a_star, b_star in ANALOGIES:
        if not all(w in vocab for w in (a, b, a_star, b_star)):
            rows.append({"a": a, "b": b, "a_star": a_star, "expected": b_star,
                         "predicted": None, "status": "missing_vocab", "top5": []})
            miss += 1
            continue
        target = vecs[vocab.index(b)] - vecs[vocab.index(a)] + vecs[vocab.index(a_star)]
        sims = vecs @ target
        order = np.argsort(-sims)
        pred_raw = vocab[order[0]]
        excluded = {a, b, a_star}
        pred = None
        for j in order:
            if exclude_inputs and vocab[j] in excluded:
                continue
            pred = vocab[j]
            top5 = [vocab[t] for t in order[:5]]
            break
        if pred == b_star:
            status = "hit"
            hit += 1
        elif pred_raw in excluded:
            status = "returned_input"
            input_hit += 1
        else:
            status = "relation_fail"
            miss += 1
        rows.append({"a": a, "b": b, "a_star": a_star, "expected": b_star,
                     "predicted": pred, "raw_top1": pred_raw,
                     "status": status, "top5": top5[:5]})
    acc = hit / len(ANALOGIES)
    return rows, acc, hit, input_hit, miss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=12)
    ap.add_argument("--dim", type=int, default=40)
    ap.add_argument("--window", type=int, default=2)
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    docs = make_corpus()
    vocab, freq = build_vocab(docs)
    print(f"corpus: {len(docs)} sentences, {sum(len(d) for d in docs)} tokens, vocab={len(vocab)}")

    gerr = gradient_check()
    print(f"gradient check: max relative error = {gerr:.3e}")

    accs = []
    best = None
    for seed in args.seeds:
        W, C, curve, idx = train(docs, vocab, dim=args.dim, window=args.window,
                                 k=args.k, epochs=args.epochs, seed=seed)
        vecs = final_vectors(W, C)
        rows, acc, hit, input_hit, miss = run_analogies(vocab, vecs)
        accs.append(acc)
        print(f"seed={seed} analogy acc={acc:.3f} (hit={hit}, returned_input={input_hit}, miss={miss})")
        if best is None or acc > best[0]:
            best = (acc, seed, W, C, vecs, curve, rows, hit, input_hit, miss)

    acc, seed, W, C, vecs, curve, rows, hit, input_hit, miss = best
    print(f"best seed={seed}")

    with open(os.path.join(OUT, "loss.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["epoch", "mean_loss", "seed"])
        for ep, l in curve:
            w.writerow([ep, f"{l:.6f}", seed])
    with open(os.path.join(OUT, "vectors.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word"] + [f"d{i}" for i in range(args.dim)])
        for name, vec in zip(vocab, vecs):
            w.writerow([name] + [f"{x:.4f}" for x in vec])
    with open(os.path.join(OUT, "neighbors.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target", "rank", "neighbor", "cosine"])
        for t in ["king", "queen", "man", "woman", "paris", "rome", "big", "smaller"]:
            if t not in vocab:
                continue
            for r, (nb, sc) in enumerate(top_neighbors(vocab, vecs, t, 6), 1):
                w.writerow([t, r, nb, f"{sc:.4f}"])
    with open(os.path.join(OUT, "analogies.json"), "w", encoding="utf-8") as f:
        json.dump({"gradient_check_max_rel_error": gerr, "best_seed": seed,
                   "accuracy": acc, "counts": {"hit": hit, "returned_input": input_hit,
                                               "miss": miss}, "rows": rows},
                  f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT, "analogy_accuracy.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["seed", "accuracy", "n_questions"])
        for s, a in zip(args.seeds, accs):
            w.writerow([s, f"{a:.3f}", len(ANALOGIES)])
        w.writerow(["mean", f"{np.mean(accs):.3f}", len(ANALOGIES)])
        w.writerow(["range", f"{max(accs) - min(accs):.3f}", len(ANALOGIES)])

    # 二维示意图：royal/gender 四个词的平行四边形
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    show = [w for w in ["king", "queen", "man", "woman", "prince", "princess"] if w in vocab]
    sub = np.array([vecs[vocab.index(w)] for w in show])
    u, s, vt = np.linalg.svd(sub - sub.mean(axis=0), full_matrices=False)
    xy = (sub - sub.mean(axis=0)) @ vt[:2].T
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    for name, (x, y) in zip(show, xy):
        ax.scatter(x, y, color="#2c6fbb", s=30)
        ax.annotate(name, (x, y), fontsize=9, xytext=(4, 3), textcoords="offset points")
    idxs = {w: i for i, w in enumerate(show)}
    for a, b in [("man", "king"), ("woman", "queen")]:
        if a in idxs and b in idxs:
            ax.annotate("", xy=xy[idxs[b]], xytext=xy[idxs[a]],
                        arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.2))
    ax.set_title("SGNS vectors projected to 2D (royal/gender)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "vector_arithmetic.png"))
    plt.close(fig)

    print(f"analogy acc mean={np.mean(accs):.3f} range={max(accs)-min(accs):.3f}")
    for t in ["king", "queen", "paris"]:
        if t in vocab:
            print(" ", t, "->", ", ".join(f"{nb}({sc:.3f})" for nb, sc in top_neighbors(vocab, vecs, t, 6)))
    for r in rows[:6]:
        print(f"  {r['a']}:{r['b']}::{r['a_star']}:{r['expected']} -> {r['predicted']} [{r['status']}]")


if __name__ == "__main__":
    main()
