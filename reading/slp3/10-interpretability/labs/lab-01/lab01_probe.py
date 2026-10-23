#!/usr/bin/env python3
"""lab-01: 线性探针 + 各向异性检查（合成数据）

构造带隐藏属性的「上下文嵌入」：每个样本属于 4 个属性（词性/时态/语义类/实体），
5 个层依次增强不同属性的信号，并共享一个很强的公共方向（模拟各向异性）。
然后在每一层训练线性探针，报告准确率、随机标签基线与维度截断曲线。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

RNG = np.random.default_rng(20261020)
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

D = 64
N = 4000
N_LAYERS = 5
ATTRS = {
    "pos": 2,
    "tense": 2,
    "sem": 5,
    "entity": 6,
}
# 每层对各属性的信号强度：模拟「浅层句法、中层语义、高层话语」
STRENGTH = {
    0: {"pos": 1.55, "tense": 0.15, "sem": 0.10, "entity": 0.05},
    1: {"pos": 1.20, "tense": 1.55, "sem": 0.20, "entity": 0.10},
    2: {"pos": 0.80, "tense": 0.70, "sem": 1.60, "entity": 0.30},
    3: {"pos": 0.60, "tense": 0.50, "sem": 1.20, "entity": 1.60},
    4: {"pos": 0.50, "tense": 0.40, "sem": 1.00, "entity": 1.30},
}
COMMON_NORM = 10.0
NOISE = 0.4
SPLIT = 0.7


def unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def make_prototypes() -> tuple[np.ndarray, dict[str, np.ndarray]]:
    common = unit(RNG.normal(size=D)) * COMMON_NORM
    protos: dict[str, np.ndarray] = {}
    for name, k in ATTRS.items():
        p = RNG.normal(size=(k, D))
        p -= np.outer(p @ common, common) / (common @ common)
        p /= np.linalg.norm(p, axis=1, keepdims=True)
        protos[name] = p
    return common, protos


def make_data(common: np.ndarray, protos: dict[str, np.ndarray]):
    labels = {name: RNG.integers(0, k, size=N) for name, k in ATTRS.items()}
    noise = RNG.normal(scale=NOISE, size=(N_LAYERS, N, D))
    layers = np.zeros((N_LAYERS, N, D), dtype=np.float64)
    for li in range(N_LAYERS):
        h = np.repeat(common[None, :], N, axis=0).copy()
        for name, k in ATTRS.items():
            h += STRENGTH[li][name] * protos[name][labels[name]]
        h += noise[li]
        layers[li] = h
    return layers, labels


def standardize(train: np.ndarray, test: np.ndarray):
    mu = train.mean(axis=0, keepdims=True)
    sd = train.std(axis=0, keepdims=True) + 1e-8
    return (train - mu) / sd, (test - mu) / sd


def train_probe(X: np.ndarray, y: np.ndarray, n_classes: int, epochs: int = 500, lr: float = 0.05, l2: float = 1e-3):
    n, d = X.shape
    W = np.zeros((d, n_classes))
    b = np.zeros(n_classes)
    Y = np.eye(n_classes)[y]
    mW = np.zeros_like(W); vW = np.zeros_like(W)
    mb = np.zeros_like(b); vb = np.zeros_like(b)
    beta1, beta2, eps = 0.9, 0.999, 1e-8
    for t in range(1, epochs + 1):
        logits = X @ W + b
        logits -= logits.max(axis=1, keepdims=True)
        P = np.exp(logits)
        P /= P.sum(axis=1, keepdims=True)
        G = (P - Y) / n
        gW = X.T @ G + l2 * W
        gb = G.sum(axis=0)
        for param, grad, m, v in ((W, gW, mW, vW), (b, gb, mb, vb)):
            m *= beta1
            m += (1 - beta1) * grad
            v *= beta2
            v += (1 - beta2) * grad * grad
            mhat = m / (1 - beta1 ** t)
            vhat = v / (1 - beta2 ** t)
            param -= lr * mhat / (np.sqrt(vhat) + eps)
    return W, b


def accuracy(X, y, W, b):
    pred = np.argmax(X @ W + b, axis=1)
    return float((pred == y).mean())


def mean_pairwise_cosine(X: np.ndarray, n: int = 400) -> tuple[float, float]:
    idx = RNG.choice(len(X), size=n, replace=False)
    Z = X[idx]
    Z = Z / np.linalg.norm(Z, axis=1, keepdims=True)
    C = Z @ Z.T
    iu = np.triu_indices(n, k=1)
    vals = C[iu]
    return float(vals.mean()), float(np.percentile(vals, 95))


def main() -> None:
    common, protos = make_prototypes()
    layers, labels = make_data(common, protos)

    n_train = int(N * SPLIT)
    idx = RNG.permutation(N)
    tr, te = idx[:n_train], idx[n_train:]

    rows = []
    for li in range(N_LAYERS):
        X = layers[li]
        Xtr_raw, Xte_raw = X[tr], X[te]
        Xtr_z, Xte_z = standardize(Xtr_raw, Xte_raw)
        for name, k in ATTRS.items():
            ytr, yte = labels[name][tr], labels[name][te]
            chance = 1.0 / k
            for feat, (Xtr, Xte) in (("raw", (Xtr_raw, Xte_raw)), ("zscore", (Xtr_z, Xte_z))):
                W, b = train_probe(Xtr, ytr, k)
                acc = accuracy(Xte, yte, W, b)
                # 随机标签基线：同容量、同数据，只打乱训练标签；3 次取平均降方差
                accs = []
                for _ in range(5):
                    Wc, bc = train_probe(Xtr, RNG.permutation(ytr), k)
                    accs.append(accuracy(Xte, yte, Wc, bc))
                acc_c = float(np.mean(accs))
                rows.append({
                    "layer": li, "attribute": name, "feature": feat,
                    "n_classes": k, "chance": round(chance, 4),
                    "accuracy": round(acc, 4),
                    "random_label_accuracy": round(acc_c, 4),
                })

    with open(OUT / "probe_by_layer.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # 维度截断：在 layer 2 的 sem 属性上，按训练集类均值方差选 top-k 维
    li, name = 2, "sem"
    Xtr_raw, Xte_raw = layers[li][tr], layers[li][te]
    Xtr, Xte = standardize(Xtr_raw, Xte_raw)
    ytr, yte = labels[name][tr], labels[name][te]
    kcls = ATTRS[name]
    means = np.stack([Xtr[ytr == c].mean(axis=0) for c in range(kcls)])
    between = means.var(axis=0)
    order = np.argsort(between)[::-1]
    dim_rows = []
    for k in (1, 2, 4, 8, 16, 32, 64):
        sel = order[:k]
        W, b = train_probe(Xtr[:, sel], ytr, kcls)
        acc = accuracy(Xte[:, sel], yte, W, b)
        accs = []
        for _ in range(5):
            Wr, br = train_probe(Xtr[:, sel], RNG.permutation(ytr), kcls)
            accs.append(accuracy(Xte[:, sel], yte, Wr, br))
        acc_r = float(np.mean(accs))
        dim_rows.append({"k_dims": k, "accuracy": round(acc, 4),
                         "random_label_accuracy": round(acc_r, 4)})

    with open(OUT / "dim_sweep.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dim_rows[0]))
        w.writeheader()
        w.writerows(dim_rows)

    cos_rows = []
    for li in range(N_LAYERS):
        raw = layers[li]
        z = (raw - raw.mean(axis=0)) / (raw.std(axis=0) + 1e-8)
        for cond, X in (("raw", raw), ("zscore", z)):
            mu, p95 = mean_pairwise_cosine(X)
            cos_rows.append({"layer": li, "condition": cond,
                             "mean_cosine": round(mu, 4), "p95_cosine": round(p95, 4)})
    with open(OUT / "cosine_stats.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(cos_rows[0]))
        w.writeheader()
        w.writerows(cos_rows)

    # 图：左=各属性准确率随层变化；右=维度截断曲线
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    colors = {"pos": "#1f77b4", "tense": "#d62728", "sem": "#2ca02c", "entity": "#9467bd"}
    for name, k in ATTRS.items():
        ys = [r["accuracy"] for r in rows if r["attribute"] == name and r["feature"] == "raw"]
        axes[0].plot(range(N_LAYERS), ys, marker="o", label=name, color=colors[name])
        axes[0].axhline(1 / k, color=colors[name], ls=":", lw=1, alpha=0.7)
    axes[0].set_xticks(range(N_LAYERS))
    axes[0].set_xlabel("层（0=嵌入输出，4=最后一层）")
    axes[0].set_ylabel("探针测试准确率")
    axes[0].set_ylim(0, 1.02)
    axes[0].set_title("各属性在不同层的可解码性（虚线=随机水平）")
    axes[0].legend(fontsize=9)
    axes[0].grid(alpha=0.25)

    axes[1].plot([r["k_dims"] for r in dim_rows], [r["accuracy"] for r in dim_rows],
                 marker="o", color="#ff7f0e", label="真实标签")
    axes[1].plot([r["k_dims"] for r in dim_rows], [r["random_label_accuracy"] for r in dim_rows],
                 marker="s", ls="--", color="#7f7f7f", label="随机标签")
    axes[1].set_xscale("log", base=2)
    axes[1].set_xlabel("保留维度数 k（按类间方差排序）")
    axes[1].set_ylabel("准确率")
    axes[1].set_ylim(0, 1.02)
    axes[1].set_title("layer 2 / sem：维度截断与随机标签基线")
    axes[1].legend(fontsize=9)
    axes[1].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT / "probe_results.png", dpi=150)

    summary = {
        "n_samples": N, "n_layers": N_LAYERS, "dim": D,
        "cosine_raw_layer4": [r for r in cos_rows if r["layer"] == 4 and r["condition"] == "raw"][0],
        "cosine_zscore_layer4": [r for r in cos_rows if r["layer"] == 4 and r["condition"] == "zscore"][0],
        "best_layer_by_attr": {},
        "max_random_label_acc": max(r["random_label_accuracy"] for r in rows),
    }
    for name in ATTRS:
        cand = [r for r in rows if r["attribute"] == name and r["feature"] == "raw"]
        best = max(cand, key=lambda r: r["accuracy"])
        summary["best_layer_by_attr"][name] = {"layer": best["layer"], "accuracy": best["accuracy"]}
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    for r in rows:
        print(f"L{r['layer']} {r['attribute']:6s} {r['feature']:6s} "
              f"acc={r['accuracy']:.3f} rand={r['random_label_accuracy']:.3f}")
    print("cos layer4 raw/zscore:",
          summary["cosine_raw_layer4"]["mean_cosine"],
          summary["cosine_zscore_layer4"]["mean_cosine"])
    print("best layers:", summary["best_layer_by_attr"])


if __name__ == "__main__":
    main()
