#!/usr/bin/env python3
"""lab-04: 归一化与词频——原始点积为什么偏爱高频词。

两个问题（对应 §5.4）：
  1. 原始点积真的偏爱高频词吗？——比较「点积 top-10」与「余弦 top-10」。
  2. 向量长度与词频的关系有多强？——log 频次 vs L2 范数散点 + Pearson 相关
     （分别对原始计数向量与 PPMI-SVD 向量计算，看 PPMI 是否已经做了部分归一化）。
偏差审计见 lab-05。

语料：本章英文原文（05-embeddings.dual.md，只读）。
运行：python3 lab04_normalization_and_bias.py
产物：out/freq_norm.csv, out/freq_norm.png, out/freq_norm.json,
      out/dot_vs_cosine.csv, out/dot_vs_cosine.png
"""
import csv
import json
import os
import re
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DUAL = "/home/yuanwu/books/slp3/zh/md/05-embeddings.dual.md"

def load_sentences(path):
    sents = []
    for ln in open(path, encoding="utf-8"):
        if not ln.startswith("> "):
            continue
        t = ln[2:].strip()
        if not t or t.startswith(("`", "释义", "*", ">", "http")):
            continue
        if "释义" in t:
            continue
        if sum(c.isascii() for c in t) / max(1, len(t)) > 0.9 and len(t.split()) >= 4:
            toks = re.findall(r"[A-Za-z]+", t.lower())
            if len(toks) >= 3:
                sents.append(toks)
    return sents


def build(sents, window=5, min_count=3, rank=50):
    freq = Counter(w for s in sents for w in s)
    vocab = sorted([w for w, c in freq.most_common(4000) if c >= min_count])
    idx = {w: i for i, w in enumerate(vocab)}
    mat = np.zeros((len(vocab), len(vocab)))
    for toks in sents:
        ids = [idx[w] for w in toks if w in idx]
        for i, wi in enumerate(ids):
            lo, hi = max(0, i - window), min(len(ids), i + window + 1)
            for j in range(lo, hi):
                if j != i:
                    mat[wi, ids[j]] += 1
    total = mat.sum()
    row = mat.sum(axis=1, keepdims=True)
    col = mat.sum(axis=0, keepdims=True) + 1.0
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((mat * total) / (row * col))
    pmi[mat == 0] = 0.0
    pp = np.maximum(pmi, 0.0)
    u, s, _ = np.linalg.svd(pp, full_matrices=False)
    k = min(rank, len(s))
    raw = u[:, :k] * np.sqrt(s[:k])          # 未归一化：保留长度信息
    unit = raw / np.maximum(np.linalg.norm(raw, axis=1, keepdims=True), 1e-12)
    return vocab, freq, mat, raw, unit


def topk(vecs, vocab, word, k=10, exclude_self=True):
    i = vocab.index(word)
    scores = vecs @ vecs[i]
    order = np.argsort(-scores)
    out = []
    for j in order:
        if exclude_self and j == i:
            continue
        out.append((vocab[j], float(scores[j])))
        if len(out) >= k:
            break
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    sents = load_sentences(DUAL)
    vocab, freq, mat, raw, unit = build(sents)
    print(f"tokens={sum(len(s) for s in sents)} vocab={len(vocab)}")

    # 1) 频率 vs 范数
    norms = np.linalg.norm(raw, axis=1)
    logf = np.log10(np.array([freq[w] for w in vocab], dtype=float))
    r = float(np.corrcoef(logf, norms)[0, 1])
    count_norms = np.linalg.norm(mat, axis=1)
    r_count = float(np.corrcoef(logf, count_norms)[0, 1])
    with open(os.path.join(OUT, "freq_norm.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word", "count", "log10_count", "l2_norm"])
        for i, word in enumerate(vocab):
            w.writerow([word, freq[word], f"{logf[i]:.4f}", f"{norms[i]:.4f}"])
    with open(os.path.join(OUT, "freq_norm.json"), "w", encoding="utf-8") as f:
        json.dump({"pearson_logfreq_vs_norm": r,
                   "pearson_logfreq_vs_raw_count_norm": r_count,
                   "n": len(vocab),
                   "mean_norm_top50_freq": float(norms[np.argsort(-np.array([freq[w] for w in vocab]))[:50]].mean()),
                   "mean_norm_rest": float(np.delete(norms, np.argsort(-np.array([freq[w] for w in vocab]))[:50]).mean())},
                  f, ensure_ascii=False, indent=2)
    print(f"Pearson(log10 freq, ||v||_PPMI-SVD) = {r:.3f}")
    print(f"Pearson(log10 freq, ||v||_raw count) = {r_count:.3f}")

    # 2) 点积 vs 余弦 top-10
    rows = []
    for target in ["word", "meaning", "context", "king"]:
        if target not in vocab:
            continue
        dot = topk(raw, vocab, target, 10)
        cos = topk(unit, vocab, target, 10)
        overlap = len(set(x for x, _ in dot) & set(x for x, _ in cos)) / 10
        for rank, ((dw, ds), (cw, cs)) in enumerate(zip(dot, cos), 1):
            rows.append([target, rank, dw, f"{ds:.3f}", cw, f"{cs:.3f}"])
        print(f"  [{target}] dot top10 vs cosine top10 overlap={overlap:.0%}")
        print(f"      dot:    {', '.join(x for x, _ in dot[:6])}")
        print(f"      cosine: {', '.join(x for x, _ in cos[:6])}")
    with open(os.path.join(OUT, "dot_vs_cosine.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target", "rank", "dot_neighbor", "dot_score", "cosine_neighbor", "cosine_score"])
        w.writerows(rows)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5), dpi=150)
    ax.scatter(logf, norms, s=10, color="#2c6fbb", alpha=0.6)
    for word in ["the", "of", "word", "meaning", "king", "concatenate" if "concatenate" in vocab else "queen"]:
        if word in vocab:
            i = vocab.index(word)
            ax.annotate(word, (logf[i], norms[i]), fontsize=8, xytext=(3, 2), textcoords="offset points")
    ax.set_xlabel("log10 frequency")
    ax.set_ylabel("L2 norm of PPMI-SVD vector")
    ax.set_title(f"Frequency vs vector length (Pearson r={r:.2f})")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "freq_norm.png"))
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
    for target in ["word", "context"]:
        if target not in vocab:
            continue
        i = vocab.index(target)
        ax.plot(logf, unit @ unit[i], ".", ms=4, label=f"cosine to '{target}'")
        ax.plot(logf, raw @ raw[i], ".", ms=4, alpha=0.6, label=f"dot to '{target}'")
    ax.set_xlabel("log10 frequency")
    ax.set_ylabel("similarity score")
    ax.set_title("Dot product vs cosine by frequency")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "dot_vs_cosine.png"))
    plt.close(fig)

    print("done: see out/freq_norm.csv, out/freq_norm.json, out/dot_vs_cosine.csv")


if __name__ == "__main__":
    main()
