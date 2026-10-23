#!/usr/bin/env python3
"""lab-03: 在真实英文语料上比较上下文窗口大小对近邻的影响。

语料：本章英文原文（从 05-embeddings.dual.md 的英文对照行抽取，只读）。
方法：词-上下文共现 -> PPMI -> 截断 SVD -> 余弦近邻（§5.3、§5.4、§5.5.3）。
问题：书中 §5.7 说短窗偏句法/可替换、长窗偏主题，这在 1 万词的技术语料上成立吗？

运行：python3 lab03_window_size_compare.py
产物：out/window_compare.csv, out/overlap.csv, out/vocab_stats.json, out/window_space.png
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
TARGETS = ["word", "words", "meaning", "vector", "context", "embedding",
           "similar", "language", "corpus", "semantic", "king", "queen"]


def load_english(path):
    """抽取 dual md 中以 '> ' 开头的英文行（中文行含大量汉字，直接被 ASCII 比例过滤）。"""
    sents = []
    for ln in open(path, encoding="utf-8"):
        if not ln.startswith("> "):
            continue
        t = ln[2:].strip()
        if not t or t.startswith(("`", "释义", "*", ">", "http")):
            continue
        if "释义" in t:
            continue
        ascii_ratio = sum(c.isascii() for c in t) / max(1, len(t))
        if ascii_ratio > 0.9 and len(t.split()) >= 4:
            toks = re.findall(r"[A-Za-z]+", t.lower())
            if len(toks) >= 3:
                sents.append(toks)
    return sents


def build_vocab(sents, min_count=3, max_vocab=4000):
    freq = Counter(w for s in sents for w in s)
    kept = [w for w, c in freq.most_common(max_vocab) if c >= min_count]
    return sorted(kept), freq


def cooccurrence(sents, vocab, window):
    idx = {w: i for i, w in enumerate(vocab)}
    n = len(vocab)
    mat = np.zeros((n, n), dtype=np.float64)
    for tokens in sents:
        ids = [idx[w] for w in tokens if w in idx]
        for i, wi in enumerate(ids):
            lo, hi = max(0, i - window), min(len(ids), i + window + 1)
            for j in range(lo, hi):
                if j != i:
                    mat[wi, ids[j]] += 1.0
    return mat


def ppmi(mat, smoothing=1.0):
    total = mat.sum()
    row = mat.sum(axis=1, keepdims=True)
    col = mat.sum(axis=0, keepdims=True) + smoothing
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((mat * total) / (row * col))
    pmi[mat == 0] = 0.0
    return np.maximum(pmi, 0.0)


def svd_vectors(mat, rank=50):
    u, s, _ = np.linalg.svd(mat, full_matrices=False)
    k = min(rank, len(s))
    v = u[:, :k] * np.sqrt(s[:k])
    n = np.linalg.norm(v, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return v / n, s, k


def neighbors(vocab, vecs, word, topn=8, cache={}):
    if word not in vocab:
        return []
    i = vocab.index(word)
    sims = vecs @ vecs[i]
    order = np.argsort(-sims)
    out = []
    for j in order:
        if j == i:
            continue
        out.append((vocab[j], float(sims[j])))
        if len(out) >= topn:
            break
    return out


def jaccard(a, b):
    sa, sb = set(a), set(b)
    return len(sa & sb) / max(1, len(sa | sb))


def main():
    os.makedirs(OUT, exist_ok=True)
    sents = load_english(DUAL)
    vocab, freq = build_vocab(sents)
    n_tokens = sum(len(s) for s in sents)
    print(f"sentences={len(sents)} tokens={n_tokens} vocab={len(vocab)}")

    results = {}
    stats = {"sentences": len(sents), "tokens": n_tokens, "vocab": len(vocab), "windows": {}}
    for win in (2, 5, 10):
        mat = cooccurrence(sents, vocab, win)
        pp = ppmi(mat)
        vecs, s, k = svd_vectors(pp)
        results[win] = {"vecs": vecs, "pp": pp, "k": k}
        stats["windows"][str(win)] = {
            "nnz_ratio": round(float((mat > 0).mean()), 4),
            "ppmi_nonzero_ratio": round(float((pp > 0).mean()), 4),
            "rank": k,
            "top1_variance_ratio": round(float(s[0] ** 2 / np.sum(s ** 2)), 4),
        }
        print(f"window=+/-{win}: nnz={float((mat>0).mean()):.3f} rank={k}")

    with open(os.path.join(OUT, "window_compare.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target", "window", "rank", "neighbor", "cosine"])
        for t in TARGETS:
            if t not in vocab:
                continue
            for win, r in results.items():
                for rank, (nb, sc) in enumerate(neighbors(vocab, r["vecs"], t, 8), 1):
                    w.writerow([t, win, rank, nb, f"{sc:.4f}"])

    with open(os.path.join(OUT, "overlap.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target", "jaccard_w2_vs_w5", "jaccard_w5_vs_w10", "top10_w2", "top10_w5"])
        for t in TARGETS:
            if t not in vocab:
                continue
            a = [x for x, _ in neighbors(vocab, results[2]["vecs"], t, 10)]
            b = [x for x, _ in neighbors(vocab, results[5]["vecs"], t, 10)]
            c = [x for x, _ in neighbors(vocab, results[10]["vecs"], t, 10)]
            w.writerow([t, f"{jaccard(a, b):.3f}", f"{jaccard(b, c):.3f}",
                        "|".join(a), "|".join(b)])

    with open(os.path.join(OUT, "vocab_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    show = [w for w in ["word", "words", "meaning", "vector", "context", "embedding",
                        "similar", "language", "corpus", "semantic", "king", "queen",
                        "model", "representation", "semantics", "vector", "dot", "cosine"]
            if w in vocab]
    show = list(dict.fromkeys(show))
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), dpi=150)
    for ax, win in zip(axes, (2, 5)):
        vecs = results[win]["vecs"]
        sub = np.array([vecs[vocab.index(w)] for w in show])
        u, s, vt = np.linalg.svd(sub - sub.mean(axis=0), full_matrices=False)
        xy = (sub - sub.mean(axis=0)) @ vt[:2].T
        for name, (x, y) in zip(show, xy):
            ax.scatter(x, y, color="#2c6fbb", s=16)
            ax.annotate(name, (x, y), fontsize=7, xytext=(2, 2), textcoords="offset points")
        ax.set_title(f"PPMI-SVD on chapter text, window=+/-{win}")
        ax.set_xlabel("dim 1"); ax.set_ylabel("dim 2")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "window_space.png"))
    plt.close(fig)

    print("\nneighbors by window (top 6):")
    for t in ["word", "meaning", "context", "king"]:
        if t not in vocab:
            continue
        for win in (2, 5):
            nb = ", ".join(f"{x}({s:.3f})" for x, s in neighbors(vocab, results[win]["vecs"], t, 6))
            print(f"  [{t}] w={win}: {nb}")
    print("\noverlap@10 (Jaccard):")
    for t in TARGETS:
        if t not in vocab:
            continue
        a = [x for x, _ in neighbors(vocab, results[2]["vecs"], t, 10)]
        b = [x for x, _ in neighbors(vocab, results[5]["vecs"], t, 10)]
        print(f"  {t}: {jaccard(a, b):.3f}")


if __name__ == "__main__":
    main()
