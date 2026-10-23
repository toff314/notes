#!/usr/bin/env python3
"""Lab 02: 在留出句上计算 unigram / bigram 困惑度，比较加一与加 k 平滑。

测试句（书中 §1.9.2 的例子）在训练前被整句剔除，避免"自己考自己"。
输出：out/perplexity.json、out/perplexity.csv、out/perplexity.png
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DEFAULT_SOURCE = Path("/home/yuanwu/books/slp3/zh/md/01-introduction.dual.md")
HOLDOUT = "so long and thanks"
TEST_SENTENCE = "so long and thanks for all the fish"
KS = [0.0001, 0.001, 0.01, 0.1, 1.0]


def load_tokens(path: Path) -> list[str]:
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.startswith("> "):
            continue
        text = raw[2:].strip()
        if not text or "释义" in text or text.startswith("`"):
            continue
        letters = sum(ch.isascii() and ch.isalpha() for ch in text)
        if len(text) > 15 and letters / len(text) > 0.55:
            lines.append(text)
    lines = [ln for ln in lines if HOLDOUT not in ln.lower()]
    text = re.sub(r"[^a-z' ]+", " ", " ".join(lines).lower())
    return text.split()


def perplexity(logprob_sum: float, n: int) -> float:
    return math.exp(-logprob_sum / n)


def unigram_pp(test, unigram, total, vocab_size, add_one: bool):
    if add_one:
        logp = [math.log((unigram.get(w, 0) + 1) / (total + vocab_size)) for w in test]
    else:
        logp = [math.log(unigram[w] / total) if unigram.get(w) else float("-inf") for w in test]
    s = sum(logp)
    return (perplexity(s, len(test)) if math.isfinite(s) else float("inf")), s


def bigram_pp(test, unigram, bigram, total, vocab_size, k: float | None):
    """k=None 表示不平滑；否则使用 add-k。"""
    if k is None:
        p0 = unigram[test[0]] / total if unigram.get(test[0]) else 0.0
        logp = [math.log(p0)] if p0 else [float("-inf")]
        for a, b in zip(test, test[1:]):
            c = bigram.get((a, b), 0)
            denom = unigram.get(a, 0)
            logp.append(math.log(c / denom) if c and denom else float("-inf"))
    else:
        denom0 = total + k * vocab_size
        logp = [math.log((unigram.get(test[0], 0) + k) / denom0)]
        for a, b in zip(test, test[1:]):
            c = bigram.get((a, b), 0)
            logp.append(math.log((c + k) / (unigram.get(a, 0) + k * vocab_size)))
    s = sum(logp)
    return (perplexity(s, len(test)) if math.isfinite(s) else float("inf")), s


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "out")
    args = ap.parse_args()

    tokens = load_tokens(args.source)
    unigram = Counter(tokens)
    bigram = Counter(zip(tokens, tokens[1:]))
    total, V = len(tokens), len(unigram)
    test = TEST_SENTENCE.split()
    oov = [w for w in test if w not in unigram]
    args.out.mkdir(parents=True, exist_ok=True)

    pp_uni_raw, s_uni_raw = unigram_pp(test, unigram, total, V, add_one=False)
    pp_uni_a1, s_uni_a1 = unigram_pp(test, unigram, total, V, add_one=True)
    pp_bi_raw, s_bi_raw = bigram_pp(test, unigram, bigram, total, V, k=None)
    results = {
        "test_sentence": TEST_SENTENCE,
        "test_tokens": len(test),
        "train_tokens": total,
        "vocab_size": V,
        "oov": oov,
        "models": {
            "unigram_unsmoothed": {"perplexity": pp_uni_raw, "logprob": s_uni_raw},
            "unigram_add1": {"perplexity": pp_uni_a1, "logprob": s_uni_a1},
            "bigram_unsmoothed": {"perplexity": pp_bi_raw, "logprob": s_bi_raw},
        },
        "bigram_add_k": {},
    }
    for k in KS:
        pp, s = bigram_pp(test, unigram, bigram, total, V, k=k)
        results["bigram_add_k"][str(k)] = {"perplexity": pp, "logprob": s}
    (args.out / "perplexity.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    with (args.out / "perplexity.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["model", "perplexity", "logprob"])
        w.writerow(["unigram_unsmoothed", pp_uni_raw, s_uni_raw])
        w.writerow(["unigram_add1", pp_uni_a1, s_uni_a1])
        w.writerow(["bigram_unsmoothed", pp_bi_raw, s_bi_raw])
        for k in KS:
            w.writerow([f"bigram_add{ k }", results["bigram_add_k"][str(k)]["perplexity"],
                        results["bigram_add_k"][str(k)]["logprob"]])

    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
    labels = ["unigram\n无平滑", "unigram\n加一", "bigram\n无平滑", "bigram\n加一"]
    finite = [1e8 if pp_uni_raw == float("inf") else pp_uni_raw, pp_uni_a1,
              1e8 if pp_bi_raw == float("inf") else pp_bi_raw,
              results["bigram_add_k"]["1.0"]["perplexity"]]
    ax1.bar(labels, finite, color=["#c0392b", "#2c7fb8", "#c0392b", "#2c7fb8"],
            label="红=含零概率（∞）　蓝=有限值")
    ax1.legend(fontsize=8, loc="upper right")
    ax1.set_yscale("log")
    ax1.set_ylabel("困惑度（对数轴，1e8 表示 ∞）")
    ax1.set_title(f'测试句："{TEST_SENTENCE}"')
    for i, v in enumerate(finite):
        ax1.text(i, v * 1.25, "∞" if v == 1e8 else f"{v:.1f}", ha="center", fontsize=8)
    ax1.set_ylim(1, 1e9)

    pps = [results["bigram_add_k"][str(k)]["perplexity"] for k in KS]
    ax2.plot(KS, pps, marker="o", color="#2c7fb8")
    ax2.set_xscale("log")
    ax2.set_yscale("log")
    ax2.set_xlabel("平滑强度 k（对数轴）")
    ax2.set_ylabel("bigram 困惑度")
    ax2.set_title("加 k 平滑：k 太小或太大都变差，最优在中间")
    for k, p in zip(KS, pps):
        ax2.annotate(f"{p:.1f}", (k, p), textcoords="offset points", xytext=(4, 6), fontsize=7)
    fig.tight_layout()
    fig.savefig(args.out / "perplexity.png", dpi=160)

    print(f"train tokens={total} V={V} test={test} oov={oov}")
    print(f"unigram raw PP={pp_uni_raw}  add1 PP={pp_uni_a1:.2f}")
    print(f"bigram  raw PP={pp_bi_raw}  add1 PP={results['bigram_add_k']['1.0']['perplexity']:.2f}")
    for k in KS:
        print(f"  k={k}: PP={results['bigram_add_k'][str(k)]['perplexity']:.2f}")


if __name__ == "__main__":
    main()
