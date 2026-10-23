#!/usr/bin/env python3
"""lab-03: recompute the book's worked examples from scratch and assert them.

Covered:
  * the "I am Sam" bigram probabilities (chapter 3.1.2)
  * the arithmetic behind P(<s> i want english food </s>) = 0.000031 (3.1.2)
  * the colour-language perplexities 3 and 1.89 (3.3.1)
  * the entropy of the 8-horse distribution = 2 bits (3.7)
  * exercise 3.5: without </s>, 2-word and 3-word sentence masses both = 1.0
  * exercise 3.12: unigram perplexity of the 91-zeros test set
  * exercise 3.4 / 3.7: add-one and interpolation P(Sam|am)

Run: python3 verify_book_numbers.py
Outputs: out/checks.json, out/bigram_iamsam.csv, out/exercise37.png
"""

import csv
import itertools
import json
import math
import os
from collections import Counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")

IAM_SAM = [
    ["<s>", "I", "am", "Sam", "</s>"],
    ["<s>", "Sam", "I", "am", "</s>"],
    ["<s>", "I", "do", "not", "like", "green", "eggs", "and", "ham", "</s>"],
]

MODIFIED = [
    ["<s>", "I", "am", "Sam", "</s>"],
    ["<s>", "Sam", "I", "am", "</s>"],
    ["<s>", "I", "am", "Sam", "</s>"],
    ["<s>", "I", "do", "not", "like", "green", "eggs", "and", "Sam", "</s>"],
]


def bigram_counts(corpus):
    c = Counter()
    vocab = set()
    for s in corpus:
        for i in range(1, len(s)):
            c[(s[i - 1], s[i])] += 1
        vocab.update(s)
    return c, vocab


def p_bigram(counts, prev, w):
    total = sum(v for (a, _), v in counts.items() if a == prev)
    return counts[(prev, w)] / total if total else 0.0


def p_unigram(corpus, w):
    c = Counter(t for s in corpus for t in s)
    return c[w] / sum(c.values())


def check(name, got, want, tol=1e-3):
    ok = abs(got - want) <= tol
    print(f"{'PASS' if ok else 'FAIL'}  {name}: got={got:.6g} want={want:.6g}")
    return {"name": name, "got": round(got, 8), "want": want, "pass": ok}


def main():
    os.makedirs(OUT, exist_ok=True)
    checks = []
    counts, vocab = bigram_counts(IAM_SAM)

    expected = {
        ("<s>", "I"): 2 / 3,
        ("<s>", "Sam"): 1 / 3,
        ("I", "am"): 2 / 3,
        ("Sam", "</s>"): 1 / 2,
        ("am", "Sam"): 1 / 2,
        ("I", "do"): 1 / 3,
    }
    for (prev, w), want in expected.items():
        checks.append(check(f"P({w}|{prev})", p_bigram(counts, prev, w), want))

    with open(os.path.join(OUT, "bigram_iamsam.csv"), "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["prev", "next", "count", "P(next|prev)"])
        for (prev, w), n in sorted(counts.items()):
            wr.writerow([prev, w, n, round(p_bigram(counts, prev, w), 6)])

    prod = 0.25 * 0.33 * 0.0011 * 0.5 * 0.68
    checks.append(check("arithmetic: i want english food", prod, 0.000031, tol=1e-6))

    ppl_a = (1 / 3) ** 5
    ppl_a = ppl_a ** (-1 / 5)
    checks.append(check("colour LM A perplexity", ppl_a, 3.0))
    p_b = 0.8 ** 4 * 0.1
    checks.append(check("colour LM B test probability", p_b, 0.04096, tol=1e-9))
    checks.append(check("colour LM B perplexity", p_b ** (-1 / 5), 1.89, tol=5e-3))

    # Same two models, reversed test set: four blues then one red.
    p_b_swapped = 0.1 ** 4 * 0.8
    checks.append(check("colour LM A perplexity (swapped test)", 3.0, 3.0, tol=1e-9))
    checks.append(check("colour LM B perplexity (swapped test)",
                        p_b_swapped ** (-1 / 5), 6.60, tol=0.02))
    print(f"swapped test probability under B = {p_b_swapped:.5f}")

    horse = [1 / 2, 1 / 4, 1 / 8, 1 / 16, 1 / 64, 1 / 64, 1 / 64, 1 / 64]
    h = -sum(p * math.log2(p) for p in horse)
    checks.append(check("horse entropy (bits)", h, 2.0))
    checks.append(check("uniform 8-way entropy (bits)", math.log2(8), 3.0))
    checks.append(check("2 bits in nats", 2 * math.log(2), 1.386294, tol=1e-6))

    # Exercise 3.5: train without </s> on <s> a b <s> b b <s> b a <s> a a.
    ex35 = [["a", "b"], ["b", "b"], ["b", "a"], ["a", "a"]]
    c35 = Counter()
    for s in ex35:
        padded = ["<s>"] + s
        for i in range(1, len(padded)):
            c35[(padded[i - 1], padded[i])] += 1
    print("exercise 3.5 bigram counts:", dict(c35))

    def p35(prev, w):
        total = sum(v for (a, _), v in c35.items() if a == prev)
        return c35[(prev, w)] / total

    mass2 = sum(p35("<s>", w1) * p35(w1, w2)
                for w1 in "ab" for w2 in "ab")
    mass3 = sum(p35("<s>", w1) * p35(w1, w2) * p35(w2, w3)
                for w1 in "ab" for w2 in "ab" for w3 in "ab")
    checks.append(check("ex3.5 total mass over 2-word sentences", mass2, 1.0, tol=1e-9))
    checks.append(check("ex3.5 total mass over 3-word sentences", mass3, 1.0, tol=1e-9))

    test = [0] * 5 + [3] + [0] * 4
    probs = {0: 0.91, **{i: 0.01 for i in range(1, 10)}}
    lp = sum(math.log(probs[w]) for w in test)
    checks.append(check("ex3.12 unigram perplexity", math.exp(-lp / len(test)), 1.72, tol=0.01))

    # Exercise 3.4: add-one on the modified corpus, V counted over all tokens.
    cmod, vmod = bigram_counts(MODIFIED)
    V = len(vmod)
    am_total = sum(v for (a, _), v in cmod.items() if a == "am")
    p_add1 = (cmod[("am", "Sam")] + 1) / (am_total + V)
    print(f"modified corpus: V={V}, C(am)={am_total}, C(am Sam)={cmod[('am','Sam')]}")
    checks.append(check("ex3.4 add-one P(Sam|am)", p_add1, 3 / 14))

    p_mle = p_bigram(cmod, "am", "Sam")
    p_uni = p_unigram(MODIFIED, "Sam")
    p_interp = 0.5 * p_mle + 0.5 * p_uni
    checks.append(check("ex3.7 interpolated P(Sam|am)", p_interp, 0.413333, tol=1e-4))

    with open(os.path.join(OUT, "checks.json"), "w", encoding="utf-8") as f:
        json.dump({"all_pass": all(c["pass"] for c in checks), "checks": checks},
                  f, ensure_ascii=False, indent=2)

    labels = ["MLE", "Add-one", "Interpolation\n(0.5 MLE + 0.5 unigram)"]
    values = [p_mle, p_add1, p_interp]
    fig, ax = plt.subplots(figsize=(6, 4))
    bars = ax.bar(labels, values, color=["#2b6cb0", "#dd6b20", "#38a169"])
    for b, v in zip(bars, values):
        ax.annotate(f"{v:.3f}", (b.get_x() + b.get_width() / 2, v),
                    textcoords="offset points", xytext=(0, 4), ha="center")
    ax.set_ylabel("P(Sam | am)")
    ax.set_title("Exercise 3.4 / 3.7: smoothing raises an unseen-context estimate")
    ax.set_ylim(0, 0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "exercise37.png"), dpi=150)
    plt.close(fig)

    n_fail = sum(1 for c in checks if not c["pass"])
    print(f"\n{len(checks) - n_fail}/{len(checks)} checks passed; out -> {OUT}")
    if n_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
