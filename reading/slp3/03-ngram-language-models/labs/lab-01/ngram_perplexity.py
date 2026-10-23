#!/usr/bin/env python3
"""lab-01: train unigram/bigram/trigram/4-gram LMs on a toy corpus.

Reports test-set perplexity (add-k smoothing with k=0.1 for every order, so
that orders are comparable) and how perplexity changes with training size.
Writes out/metrics.csv, out/ppl_by_n.png, out/ppl_vs_train_size.png and
out/samples.json.

Run: python3 ngram_perplexity.py
"""

import csv
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

sys.dont_write_bytecode = True

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared_corpus import build_corpus  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
K = 0.1


def make_vocab(train, min_count=2):
    c = Counter(w for s in train for w in s)
    vocab = {w for w, n in c.items() if n >= min_count}
    vocab.update({"<s>", "</s>", "<unk>"})
    return vocab


def map_oov(sents, vocab):
    return [[w if w in vocab else "<unk>" for w in s] for s in sents]


class NgramLM:
    def __init__(self, order, vocab):
        self.order = order
        self.vocab = vocab
        self.V = len(vocab)
        self.ctx = defaultdict(Counter)
        self.ctx_total = Counter()

    def train(self, sents):
        for s in sents:
            padded = ["<s>"] * (self.order - 1) + s
            for i in range(self.order - 1, len(padded)):
                w = padded[i]
                context = tuple(padded[i - self.order + 1:i]) if self.order > 1 else ()
                self.ctx[context][w] += 1
                self.ctx_total[context] += 1
        return self

    def prob(self, context, w, k=K):
        context = tuple(context)
        c = self.ctx[context][w]
        total = self.ctx_total[context]
        return (c + k) / (total + k * self.V)

    def logprob_sentence(self, sent, k=K):
        padded = ["<s>"] * (self.order - 1) + sent
        total = 0.0
        for i in range(self.order - 1, len(padded)):
            w = padded[i]
            context = tuple(padded[i - self.order + 1:i]) if self.order > 1 else ()
            total += math.log(self.prob(context, w, k))
        return total


def evaluate(lm, sents, k=K):
    logp, n = 0.0, 0
    for s in sents:
        logp += lm.logprob_sentence(s, k)
        n += len(s)  # includes </s>, excludes the artificial <s> padding
    return math.exp(-logp / n), n


def sample_sentence(lm, rng, max_len=30, k=1e-4):
    """Sample one sentence from the LM (chapter 3.4's cumulative method).

    A tiny k keeps every candidate non-zero while staying close to the MLE
    counts; sampling with k=0.1 would mostly produce uniform noise.
    """
    context = ["<s>"] * (lm.order - 1)
    out = []
    candidates = sorted(lm.vocab - {"<s>"})
    for _ in range(max_len):
        ctx = tuple(context) if lm.order > 1 else ()
        weights = [lm.prob(ctx, w, k) for w in candidates]
        w = rng.choices(candidates, weights=weights, k=1)[0]
        out.append(w)
        if w == "</s>":
            break
        if lm.order > 1:
            context = (context + [w])[-(lm.order - 1):]
    return " ".join(out)


def main():
    os.makedirs(OUT, exist_ok=True)
    train, dev, test = build_corpus()
    vocab = make_vocab(train)
    train_m, dev_m, test_m = map_oov(train, vocab), map_oov(dev, vocab), map_oov(test, vocab)

    train_tokens = sum(len(s) for s in train_m)
    test_tokens = sum(len(s) for s in test_m)
    oov = sum(1 for s in test for w in s if w not in vocab)
    oov_rate = oov / test_tokens

    rows, lms = [], {}
    for order in (1, 2, 3, 4):
        lm = NgramLM(order, vocab).train(train_m)
        ppl, n = evaluate(lm, test_m)
        lms[order] = lm
        rows.append({
            "model": f"{order}-gram", "n": order, "train_frac": 1.0,
            "train_tokens": train_tokens, "test_tokens": n,
            "oov_rate": round(oov_rate, 4), "perplexity": round(ppl, 2),
            "distinct_contexts": len(lm.ctx),
        })
        print(f"[full train] {order}-gram  ppl={ppl:8.2f}  contexts={len(lm.ctx)}")

    # Train-size sweep for bigram and trigram.
    fractions = (0.25, 0.5, 0.75, 1.0)
    for order in (2, 3):
        for frac in fractions:
            cut = max(1, int(len(train_m) * frac))
            sub = train_m[:cut]
            lm = NgramLM(order, vocab).train(sub)
            ppl, n = evaluate(lm, test_m)
            rows.append({
                "model": f"{order}-gram", "n": order, "train_frac": frac,
                "train_tokens": sum(len(s) for s in sub), "test_tokens": n,
                "oov_rate": round(oov_rate, 4), "perplexity": round(ppl, 2),
                "distinct_contexts": len(lm.ctx),
            })
            print(f"[train {frac:.0%}] {order}-gram  ppl={ppl:8.2f}")

    with open(os.path.join(OUT, "metrics.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # Chart 1: perplexity vs n (full training set).
    full = [r for r in rows if r["train_frac"] == 1.0]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([r["n"] for r in full], [r["perplexity"] for r in full],
            marker="o", color="#2b6cb0")
    for r in full:
        ax.annotate(f'{r["perplexity"]:.1f}', (r["n"], r["perplexity"]),
                    textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9)
    ax.set_yscale("log")
    ax.set_xticks([1, 2, 3, 4])
    ax.set_xlabel("n-gram order n")
    ax.set_ylabel("test perplexity (log scale)")
    ax.set_title("Perplexity vs. order (add-k, k=0.1)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "ppl_by_n.png"), dpi=150)
    plt.close(fig)

    # Chart 2: perplexity vs training-set size.
    fig, ax = plt.subplots(figsize=(6, 4))
    for order, color in ((2, "#2b6cb0"), (3, "#c05621")):
        order_rows = sorted([r for r in rows if r["n"] == order],
                            key=lambda r: r["train_frac"])
        xs = [r["train_tokens"] for r in order_rows]
        ys = [r["perplexity"] for r in order_rows]
        ax.plot(xs, ys, marker="o", label=f"{order}-gram", color=color)
    ax.set_xlabel("training tokens")
    ax.set_ylabel("test perplexity")
    ax.set_title("Perplexity vs. training size (add-k, k=0.1)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "ppl_vs_train_size.png"), dpi=150)
    plt.close(fig)

    # Sample sentence probabilities from the trigram model.
    tri = lms[3]
    samples = []
    for s in test_m[:5]:
        lp = tri.logprob_sentence(s)
        samples.append({
            "sentence": " ".join(s),
            "tokens_scored": len(s),
            "logprob": round(lp, 4),
            "prob": float(f"{math.exp(lp):.3e}"),
            "perplexity": round(math.exp(-lp / len(s)), 2),
        })
    with open(os.path.join(OUT, "samples.json"), "w", encoding="utf-8") as f:
        json.dump({"k": K, "oov_rate": round(oov_rate, 4), "samples": samples},
                  f, ensure_ascii=False, indent=2)
    for s in samples:
        print(f'  ppl={s["perplexity"]:7.2f}  p={s["prob"]:.2e}  {s["sentence"][:70]}')

    rng = random.Random(11)
    with open(os.path.join(OUT, "samples_generated.txt"), "w", encoding="utf-8") as f:
        for order in (1, 2, 3, 4):
            f.write(f"# {order}-gram samples (5)\n")
            print(f"  [{order}-gram]")
            for _ in range(5):
                s = sample_sentence(lms[order], rng)
                f.write(s + "\n")
                print(f"    {s[:80]}")

    print(f"\nOOV rate on test: {oov_rate:.2%}  |  vocab={len(vocab)}  |  out -> {OUT}")


if __name__ == "__main__":
    main()
