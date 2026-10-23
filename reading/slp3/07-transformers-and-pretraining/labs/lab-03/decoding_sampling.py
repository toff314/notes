#!/usr/bin/env python3
"""Lab 03: greedy / temperature / top-k / top-p decoding on toy distributions."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)


def softmax(x):
    m = np.max(x)
    e = np.exp(x - m)
    return e / e.sum()


def entropy(p):
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def top_k_filter(p, k):
    out = np.zeros_like(p)
    keep = np.argsort(p)[::-1][:k]
    out[keep] = p[keep]
    return out / out.sum()


def top_p_filter(p, threshold):
    order = np.argsort(p)[::-1]
    cum = np.cumsum(p[order])
    n = int(np.searchsorted(cum, threshold) + 1)
    n = min(n, len(p))
    out = np.zeros_like(p)
    out[order[:n]] = p[order[:n]]
    return out / out.sum(), n


def decode(table, words, itos, strategy, steps=14, seed=3):
    rng = np.random.default_rng(seed)
    cur = "<bos>"
    out = []
    for _ in range(steps):
        nxt = table.get(cur)
        if not nxt:
            break
        idx = [w for w, _ in nxt]
        logits = np.log(np.array([q for _, q in nxt]))
        if strategy == "greedy":
            j = int(np.argmax(logits))
        elif strategy == "random":
            j = int(rng.choice(len(idx), p=softmax(logits)))
        elif strategy.startswith("temperature:"):
            tau = float(strategy.split(":")[1])
            j = int(rng.choice(len(idx), p=softmax(logits / tau)))
        elif strategy.startswith("top_k:"):
            k = int(strategy.split(":")[1])
            j = int(rng.choice(len(idx), p=top_k_filter(softmax(logits), k)))
        elif strategy.startswith("top_p:"):
            thr = float(strategy.split(":")[1])
            j = int(rng.choice(len(idx), p=top_p_filter(softmax(logits), thr)[0]))
        else:
            raise ValueError(strategy)
        out.append(idx[j])
        cur = idx[j]
    return " ".join(out)


def main():
    words = ["the", "cat", "dog", "sat", "on", "a", "mat", "log", ".", "and"]
    logits = np.array([2.2, 1.2, 0.8, 0.3, 0.1, -0.2, -0.5, -0.9, -1.4, -2.0])
    itos = {i: w for i, w in enumerate(words)}

    rows = []
    for tau in [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]:
        p = softmax(logits / tau)
        rows.append({
            "tau": tau,
            "max_prob": float(p.max()),
            "entropy_nats": entropy(p),
            "effective_vocab": float(np.exp(entropy(p))),
            "argmax": words[int(np.argmax(p))],
            "prob_sum": float(p.sum()),
        })

    topk_rows = []
    base = softmax(logits)
    for k in [1, 2, 3, 5, 10]:
        keep = np.argsort(base)[::-1][:k]
        mass = float(base[keep].sum())
        p = top_k_filter(base, k)
        topk_rows.append({"k": k, "mass_before_renorm": mass,
                          "support": int(np.sum(p > 0)), "entropy_nats": entropy(p)})

    topp_rows = []
    for thr in [0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]:
        order = np.argsort(base)[::-1]
        cum = np.cumsum(base[order])
        n = min(int(np.searchsorted(cum, thr) + 1), len(base))
        p, n2 = top_p_filter(base, thr)
        topp_rows.append({"p": thr, "support": n2, "mass_before_renorm": float(cum[n - 1]),
                          "entropy_nats": entropy(p)})

    table = {
        "<bos>": [("the", 0.50), ("a", 0.50)],
        "the": [("cat", 0.45), ("dog", 0.45), ("mat", 0.10)],
        "a": [("cat", 0.50), ("dog", 0.50)],
        "cat": [("sat", 0.80), ("on", 0.20)],
        "dog": [("sat", 0.80), ("on", 0.20)],
        "sat": [("on", 0.90), ("the", 0.10)],
        "on": [("the", 0.60), ("a", 0.40)],
        "mat": [(".", 0.95), ("on", 0.05)],
        "log": [(".", 0.95), ("on", 0.05)],
        ".": [("<bos>", 0.90), ("<eos>", 0.10)],
    }
    strategies = ["greedy", "random", "temperature:0.5", "temperature:1.5", "top_k:2", "top_p:0.9"]
    samples = {s: [decode(table, words, itos, s, seed=10 + i) for i in range(3)] for s in strategies}

    summary = {
        "four_word_example": {
            "words": ["all", "the", "your", "that"],
            "logits": [2.2, 1.2, 0.8, 0.1],
            "probabilities": {
                str(tau): [round(float(x), 4) for x in softmax(np.array([2.2, 1.2, 0.8, 0.1]) / tau)]
                for tau in [0.2, 1.0, 2.0]
            },
        },
        "temperature_table": rows,
        "top_k_table": topk_rows,
        "top_p_table": topp_rows,
        "samples": samples,
        "checks": {
            "all_prob_sums_one": all(abs(r["prob_sum"] - 1) < 1e-12 for r in rows),
            "tau_to_zero_approaches_greedy": rows[0]["max_prob"] > 0.999,
            "tau_above_one_flattens": rows[-1]["entropy_nats"] > rows[4]["entropy_nats"],
            "top_k_1_equals_greedy": topk_rows[0]["support"] == 1,
        },
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "samples.json").write_text(json.dumps(samples, indent=2, ensure_ascii=False), encoding="utf-8")
    with open(OUT / "decoding_metrics.csv", "w", encoding="utf-8") as f:
        f.write("tau,max_prob,entropy_nats,effective_vocab,argmax\n")
        for r in rows:
            f.write(f"{r['tau']},{r['max_prob']:.6f},{r['entropy_nats']:.6f},"
                    f"{r['effective_vocab']:.6f},{r['argmax']}\n")

    taus = [r["tau"] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    axes[0].plot(taus, [r["max_prob"] for r in rows], marker="o")
    axes[0].set_xscale("log")
    axes[0].set_xlabel("temperature tau (log scale)")
    axes[0].set_ylabel("max probability")
    axes[0].set_title("Low tau -> greedy")
    axes[0].grid(alpha=0.25)
    axes[1].plot(taus, [r["entropy_nats"] for r in rows], marker="o", color="tab:orange")
    axes[1].set_xscale("log")
    axes[1].set_xlabel("temperature tau (log scale)")
    axes[1].set_ylabel("entropy (nats)")
    axes[1].set_title("High tau -> flatter distribution")
    axes[1].grid(alpha=0.25)
    fig.suptitle("Temperature reshapes the next-token distribution")
    fig.savefig(OUT / "temperature_effect.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    grid = np.linspace(0.05, 1.0, 40)
    support = [top_p_filter(softmax(logits), x)[1] for x in grid]
    fig, ax = plt.subplots(figsize=(6.4, 3.8))
    ax.plot(grid, support, color="tab:green")
    ax.set_xlabel("cumulative probability threshold p")
    ax.set_ylabel("retained vocabulary size")
    ax.set_title("Top-p keeps a variable number of tokens")
    ax.grid(alpha=0.25)
    fig.savefig(OUT / "top_p_retained.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
