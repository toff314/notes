#!/usr/bin/env python3
"""lab-02: compare smoothing methods on the same trigram test set.

Methods: MLE (no smoothing), Laplace / add-1, add-k (k = 0.1, 0.01, 0.001),
Jelinek-Mercer linear interpolation (weights tuned on dev), stupid backoff
(lambda = 0.4, unnormalised score).

Run: python3 smoothing_compare.py
Outputs: out/metrics.csv, out/smoothing_ppl.png, out/dev_vs_test.png,
         out/lambdas.json, out/backoff_examples.json
"""

import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_corpus import build_corpus  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
SB_LAMBDA = 0.4


def make_vocab(train, min_count=2):
    c = Counter(w for s in train for w in s)
    vocab = {w for w, n in c.items() if n >= min_count}
    vocab.update({"<s>", "</s>", "<unk>"})
    return vocab


def map_oov(sents, vocab):
    return [[w if w in vocab else "<unk>" for w in s] for s in sents]


class Counts:
    def __init__(self, vocab):
        self.vocab = vocab
        self.V = len(vocab)
        self.uni = Counter()
        self.bi = Counter()
        self.tri = Counter()
        self.bi_hist = Counter()
        self.tri_hist = Counter()
        self.uni_total = 0

    def train(self, sents):
        for s in sents:
            padded = ["<s>", "<s>"] + s
            for i, w in enumerate(padded):
                self.uni[w] += 1
                self.uni_total += 1
                if i >= 1:
                    self.bi[(padded[i - 1], w)] += 1
                    self.bi_hist[padded[i - 1]] += 1
                if i >= 2:
                    self.tri[(padded[i - 2], padded[i - 1], w)] += 1
                    self.tri_hist[(padded[i - 2], padded[i - 1])] += 1
        return self


class Models:
    def __init__(self, c):
        self.c = c

    def p_uni(self, w):
        return self.c.uni[w] / self.c.uni_total if self.c.uni_total else 0.0

    def p_bi(self, prev, w):
        total = self.c.bi_hist[prev]
        return self.c.bi[(prev, w)] / total if total else 0.0

    def p_tri(self, w1, w2, w):
        total = self.c.tri_hist[(w1, w2)]
        return self.c.tri[(w1, w2, w)] / total if total else 0.0

    def p_addk(self, w1, w2, w, k):
        c = self.c.tri[(w1, w2, w)]
        total = self.c.tri_hist[(w1, w2)]
        return (c + k) / (total + k * self.c.V)

    def p_interp(self, w1, w2, w, lam):
        return (lam[0] * self.p_uni(w)
                + lam[1] * self.p_bi(w2, w)
                + lam[2] * self.p_tri(w1, w2, w))

    def score_backoff(self, w1, w2, w):
        tri = self.c.tri[(w1, w2, w)]
        if tri:
            return tri / self.c.tri_hist[(w1, w2)]
        bi = self.c.bi[(w2, w)]
        if bi:
            return SB_LAMBDA * bi / self.c.bi_hist[w2]
        return SB_LAMBDA * SB_LAMBDA * self.p_uni(w)


def positions(sents):
    """Yield (w1, w2, w) for every scored token (excluding padding <s>)."""
    for s in sents:
        padded = ["<s>", "<s>"] + s
        for i in range(2, len(padded)):
            yield padded[i - 2], padded[i - 1], padded[i]


def ppl_from_logps(logps):
    if any(x == float("-inf") for x in logps):
        return float("inf")
    return math.exp(-sum(logps) / len(logps))


def eval_model(fn, sents):
    logps = []
    for t in positions(sents):
        p = fn(*t)
        logps.append(math.log(p) if p > 0 else float("-inf"))
    return ppl_from_logps(logps)


def tune_lambdas(models, dev):
    """Grid search on the simplex, maximising dev log-likelihood (numpy)."""
    u, b, t = [], [], []
    for w1, w2, w in positions(dev):
        u.append(models.p_uni(w))
        b.append(models.p_bi(w2, w))
        t.append(models.p_tri(w1, w2, w))
    u, b, t = np.array(u), np.array(b), np.array(t)
    step = 0.05
    grid = np.arange(0, 1 + 1e-9, step)
    best = (-np.inf, None)
    for l1 in grid:
        for l2 in grid:
            l3 = 1.0 - l1 - l2
            if l3 < -1e-9:
                continue
            p = l1 * u + l2 * b + max(0.0, l3) * t
            total = float(np.log(np.maximum(p, 1e-300)).sum())
            if total > best[0]:
                best = (total, (round(float(l1), 2), round(float(l2), 2),
                                round(max(0.0, float(l3)), 2)))
    return best[1]


def main():
    os.makedirs(OUT, exist_ok=True)
    train, dev, test = build_corpus()
    vocab = make_vocab(train)
    train_m, dev_m, test_m = map_oov(train, vocab), map_oov(dev, vocab), map_oov(test, vocab)
    counts = Counts(vocab).train(train_m)
    m = Models(counts)

    lambdas = tune_lambdas(m, dev_m)
    print(f"tuned lambdas (uni, bi, tri) = {lambdas}")

    rows = []

    def add(name, ppl_dev, ppl_test, note=""):
        rows.append({"model": name, "dev_perplexity": ppl_dev,
                     "test_perplexity": ppl_test, "note": note})
        d = "inf" if math.isinf(ppl_dev) else f"{ppl_dev:.2f}"
        t = "inf" if math.isinf(ppl_test) else f"{ppl_test:.2f}"
        print(f"{name:18s} dev={d:>8s}  test={t:>8s}  {note}")

    add("MLE", eval_model(lambda a, b, w: m.p_tri(a, b, w), dev_m),
        eval_model(lambda a, b, w: m.p_tri(a, b, w), test_m),
        "unseen trigram -> zero -> infinite perplexity")
    add("Laplace (k=1)", eval_model(lambda a, b, w: m.p_addk(a, b, w, 1.0), dev_m),
        eval_model(lambda a, b, w: m.p_addk(a, b, w, 1.0), test_m), "add-one")
    for k in (0.1, 0.01, 0.001):
        add(f"Add-k (k={k})", eval_model(lambda a, b, w, k=k: m.p_addk(a, b, w, k), dev_m),
            eval_model(lambda a, b, w, k=k: m.p_addk(a, b, w, k), test_m), "add-k")
    add("Interpolation", eval_model(lambda a, b, w: m.p_interp(a, b, w, lambdas), dev_m),
        eval_model(lambda a, b, w: m.p_interp(a, b, w, lambdas), test_m),
        f"JM weights={lambdas}")

    sb_dev = ppl_from_logps([math.log(max(m.score_backoff(*t), 1e-300)) for t in positions(dev_m)])
    sb_test = ppl_from_logps([math.log(max(m.score_backoff(*t), 1e-300)) for t in positions(test_m)])
    add("Stupid backoff", sb_dev, sb_test,
        "lambda=0.4, unnormalised score; pseudo-perplexity only")

    with open(os.path.join(OUT, "metrics.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["model", "dev_perplexity", "test_perplexity", "note"])
        w.writeheader()
        for r in rows:
            out = dict(r)
            for key in ("dev_perplexity", "test_perplexity"):
                if math.isinf(out[key]):
                    out[key] = "inf"
                else:
                    out[key] = round(out[key], 4)
            w.writerow(out)

    with open(os.path.join(OUT, "lambdas.json"), "w", encoding="utf-8") as f:
        json.dump({"lambda_unigram": lambdas[0], "lambda_bigram": lambdas[1],
                   "lambda_trigram": lambdas[2],
                   "tuned_on": "dev split, step=0.05, max dev log-likelihood"}, f, indent=2)

    plot_rows = [r for r in rows if not math.isinf(r["test_perplexity"])]
    labels = [r["model"].replace(" (", "\n(") for r in plot_rows]
    values = [r["test_perplexity"] for r in plot_rows]
    colors = ["#c53030", "#dd6b20", "#d69e2e", "#38a169", "#3182ce", "#805ad5"][:len(values)]
    fig, ax = plt.subplots(figsize=(9, 4.6))
    bars = ax.bar(labels, values, color=colors)
    for b, v in zip(bars, values):
        ax.annotate(f"{v:.1f}", (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("test perplexity (log scale)")
    ax.set_title("Trigram LM: smoothing comparison (MLE = infinite, omitted)")
    ax.tick_params(axis="x", labelsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "smoothing_ppl.png"), dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.2))
    x = range(len(plot_rows))
    ax.plot(x, [r["dev_perplexity"] for r in plot_rows], marker="o", label="dev")
    ax.plot(x, [r["test_perplexity"] for r in plot_rows], marker="s", label="test")
    ax.set_xticks(list(x))
    ax.set_xticklabels([r["model"] for r in plot_rows], rotation=20, ha="right", fontsize=8)
    ax.set_yscale("log")
    ax.set_ylabel("perplexity (log scale)")
    ax.set_title("Dev vs. test perplexity per smoothing method")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "dev_vs_test.png"), dpi=150)
    plt.close(fig)

    examples = []
    for s in test_m:
        padded = ["<s>", "<s>"] + s
        for i in range(2, len(padded)):
            w1, w2, w = padded[i - 2], padded[i - 1], padded[i]
            if counts.tri[(w1, w2, w)] == 0:
                examples.append({"context": f"{w1} {w2}", "word": w,
                                 "trigram_count": 0,
                                 "bigram_count": counts.bi[(w2, w)],
                                 "backoff_score": round(m.score_backoff(w1, w2, w), 6)})
            if len(examples) >= 10:
                break
        if len(examples) >= 10:
            break
    with open(os.path.join(OUT, "backoff_examples.json"), "w", encoding="utf-8") as f:
        json.dump({"lambda": SB_LAMBDA, "examples": examples}, f, ensure_ascii=False, indent=2)

    oov = sum(1 for s in test for w in s if w not in vocab) / sum(len(s) for s in test_m)
    print(f"\nOOV rate test: {oov:.2%}")
    print(f"out -> {OUT}")


if __name__ == "__main__":
    main()
