#!/usr/bin/env python3
"""lab-01: 词-上下文共现矩阵 -> PPMI -> 截断 SVD -> 近邻与二维投影。

对应《Speech and Language Processing》第 3 版 §5.3（共现矩阵）、§5.4（余弦）、
§5.5.3（PPMI 与计数/预测两派的关系）。

只用标准库 + numpy + matplotlib。
运行：python3 lab01_cooccurrence_ppmi_svd.py [--window 4] [--rank 20]
产物：out/*.csv, out/vectors_2d.png
"""
import argparse
import csv
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

CORPUS = [
    "a traditional cherry pie is a classic dessert",
    "strawberry rhubarb pie is a traditional dessert",
    "apple pie is often served with ice cream",
    "cherry jam and strawberry jam are sweet",
    "the pie is filled with cherry and sugar",
    "strawberry and cherry are red fruit",
    "she baked an apple pie with sugar",
    "the dessert was a cherry pie with cream",
    "add sugar and jam to the strawberry pie",
    "the cherry dessert tastes sweet with sugar",
    "computer peripherals and digital assistants are common",
    "a computer stores information on the internet",
    "digital data and computer networks carry information",
    "the information is stored as digital data on a computer",
    "the device connects to the internet and shares data",
    "digital assistants answer questions using information",
    "computer data is processed by the digital device",
    "information retrieval finds data in a computer",
    "the internet carries digital information",
    "a digital device stores data and information",
    "her laptop is a computer with digital storage",
    "the network sends information to the computer",
    "cherry and strawberry fruit grow in the garden",
    "the garden has apple and cherry trees",
    "sugar makes the strawberry jam sweet",
    "he wrote the result on a computer",
    "the result of the search is information",
    "data and result are stored in the computer",
]


def tokenize(sent):
    return sent.lower().split()


def build_vocab(docs, min_count=2):
    freq = {}
    for d in docs:
        for w in d:
            freq[w] = freq.get(w, 0) + 1
    vocab = sorted([w for w, c in freq.items() if c >= min_count])
    return vocab, freq


def cooccurrence(docs, vocab, window):
    idx = {w: i for i, w in enumerate(vocab)}
    n = len(vocab)
    mat = np.zeros((n, n), dtype=np.float64)
    for tokens in docs:
        for i, w in enumerate(tokens):
            if w not in idx:
                continue
            lo, hi = max(0, i - window), min(len(tokens), i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                c = tokens[j]
                if c in idx:
                    mat[idx[w], idx[c]] += 1.0
    return mat


def ppmi(mat, context_smoothing=1.0):
    """PPMI。分母对上下文列做 +1 平滑，避免 log(0) 与极端值。"""
    total = mat.sum()
    row = mat.sum(axis=1, keepdims=True)
    col = mat.sum(axis=0, keepdims=True) + context_smoothing
    with np.errstate(divide="ignore", invalid="ignore"):
        pmi = np.log((mat * total) / (row * col))
    pmi[mat == 0] = 0.0
    return np.maximum(pmi, 0.0)


def truncated_svd(ppmi_mat, rank):
    u, s, vt = np.linalg.svd(ppmi_mat, full_matrices=False)
    k = min(rank, len(s))
    vecs = u[:, :k] * np.sqrt(s[:k])
    # L2 归一化：单位向量下点积即余弦（§5.4）
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return vecs / norms, s, k


def cosine_matrix(vecs):
    return vecs @ vecs.T


def neighbors(vocab, vecs, word, topn=5):
    if word not in vocab:
        return []
    i = vocab.index(word)
    sims = cosine_matrix(vecs)[i]
    order = np.argsort(-sims)
    out = []
    for j in order:
        if j == i:
            continue
        out.append((vocab[j], float(sims[j])))
        if len(out) >= topn:
            break
    return out


def write_matrix(path, vocab, mat):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word"] + vocab)
        for name, row in zip(vocab, mat):
            w.writerow([name] + [f"{v:.4f}" for v in row])


def book_cosine_check():
    """§5.3 图 5.3 的三维计数（pie, data, computer），复算 §5.4 的两个余弦。"""
    counts = {
        "cherry": [442, 8, 2],
        "digital": [5, 1683, 1670],
        "information": [5, 3982, 3325],
    }
    book = {("cherry", "information"): 0.018, ("digital", "information"): 0.996}
    rows = []
    for (a, b), ref in book.items():
        va, vb = np.array(counts[a], float), np.array(counts[b], float)
        cos = float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb)))
        rows.append([a, b, f"{cos:.6f}", f"{ref:.3f}", f"{abs(cos - ref):.6f}"])
    path = os.path.join(OUT, "book_cosine_check.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word_a", "word_b", "recomputed_cosine", "book_value", "abs_diff"])
        w.writerows(rows)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", type=int, default=4)
    ap.add_argument("--rank", type=int, default=20)
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)

    docs = [tokenize(s) for s in CORPUS]
    vocab, freq = build_vocab(docs, min_count=2)

    mat = cooccurrence(docs, vocab, args.window)
    pp = ppmi(mat)
    vecs, s, k = truncated_svd(pp, args.rank)

    write_matrix(os.path.join(OUT, "cooccurrence.csv"), vocab, mat)
    write_matrix(os.path.join(OUT, "ppmi.csv"), vocab, pp)
    write_matrix(os.path.join(OUT, "word_vectors.csv"), vocab, vecs)
    with open(os.path.join(OUT, "singular_values.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["index", "singular_value", "explained_ratio"])
        for i, v in enumerate(s[:k]):
            w.writerow([i, f"{v:.4f}", f"{v ** 2 / np.sum(s ** 2):.4f}"])

    targets = ["cherry", "strawberry", "digital", "information", "sugar"]
    with open(os.path.join(OUT, "neighbors.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["target", "rank", "neighbor", "cosine"])
        for t in targets:
            for r, (nb, sc) in enumerate(neighbors(vocab, vecs, t, 5), 1):
                w.writerow([t, r, nb, f"{sc:.4f}"])

    # 窗口敏感性：同一行 cherry 在 ±1 与 ±4 下的非零维（§5.3 行动）
    sweep = {}
    for win in (1, 4):
        m = cooccurrence(docs, vocab, win)
        i = vocab.index("cherry")
        nz = {vocab[j]: int(m[i, j]) for j in range(len(vocab)) if m[i, j] > 0}
        sweep[f"window_{win}"] = nz
    with open(os.path.join(OUT, "window_sweep_cherry.json"), "w", encoding="utf-8") as f:
        json.dump(sweep, f, ensure_ascii=False, indent=2)

    # 二维投影（取 SVD 前两维）
    coords = vecs[:, :2]
    with open(os.path.join(OUT, "vectors_2d.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["word", "x", "y", "freq"])
        for name, (x, y) in zip(vocab, coords):
            w.writerow([name, f"{x:.4f}", f"{y:.4f}", freq[name]])

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 6), dpi=150)
    fruit = {"cherry", "strawberry", "apple", "pie", "sugar", "jam", "dessert", "sweet", "fruit", "cream"}
    for name, (x, y) in zip(vocab, coords):
        color = "#c0392b" if name in fruit else "#2c6fbb"
        ax.scatter(x, y, color=color, s=18)
        ax.annotate(name, (x, y), fontsize=7, xytext=(2, 2), textcoords="offset points")
    ax.set_title(f"PPMI-SVD word vectors (window=+/-{args.window}, rank={k}); red=food words")
    ax.set_xlabel("SVD dim 1")
    ax.set_ylabel("SVD dim 2")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "vectors_2d.png"))
    plt.close(fig)

    rows = book_cosine_check()

    print(f"vocab={len(vocab)}  cooccurrence_nnz={int((mat > 0).sum())}/{mat.size}")
    print(f"PPMI nonzero ratio={float((pp > 0).mean()):.3f}; rank={k}")
    print("neighbors:")
    for t in targets:
        print(" ", t, "->", ", ".join(f"{nb}({sc:.3f})" for nb, sc in neighbors(vocab, vecs, t, 5)))
    print("book cosine check:")
    for r in rows:
        print("  cos(%s,%s)=%s book=%s diff=%s" % tuple(r))
    cs = float(cosine_matrix(vecs)[vocab.index("cherry"), vocab.index("strawberry")])
    di = float(cosine_matrix(vecs)[vocab.index("digital"), vocab.index("information")])
    print(f"cos(cherry,strawberry)={cs:.4f}  cos(digital,information)={di:.4f}")
    print("window sweep (cherry):", json.dumps(sweep, ensure_ascii=False))


if __name__ == "__main__":
    main()
