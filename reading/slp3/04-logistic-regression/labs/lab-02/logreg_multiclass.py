#!/usr/bin/env python3
"""lab-02: 多项逻辑回归（softmax）+ 评估 + 超参数对比 + 配对自助检验。

对应 actions.md 第 3、4 条：
  3) 实现 softmax 多项逻辑回归，输出混淆矩阵、宏/微平均精确率·召回率·F1，
     并扫描学习率与 L2 正则强度；
  4) 按书中 §4.11.1 的配对自助检验，比较最优模型与多数类基线，输出 p 值。

运行：
    python3 logreg_multiclass.py
产物写入 ./out/：
    confusion_matrix.png, metrics.json, lr_comparison.png, lr_comparison.csv,
    reg_comparison.png, reg_comparison.csv, bootstrap.json, bootstrap_hist.png
"""
from __future__ import annotations

import csv
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

LABELS = ["positive", "negative", "neutral"]


def make_dataset(seed=7, n_per_class=(60, 60, 60)):
    """三类影评特征：x1 正向词数、x2 负向词数、x3 感叹号数。

    按类别设定泊松均值，保证类别可由特征区分，但保留重叠（有错分）。
    """
    rng = np.random.default_rng(seed)
    means = {
        "positive": (4.2, 1.0, 1.6),
        "negative": (1.0, 4.2, 0.8),
        "neutral": (2.2, 2.2, 0.2),
    }
    X_parts, y_parts = [], []
    for k, label in enumerate(LABELS):
        lam = means[label]
        n = n_per_class[k]
        block = rng.poisson(lam=lam, size=(n, 3)).astype(float)
        X_parts.append(block)
        y_parts.append(np.full(n, k, dtype=int))
    X = np.vstack(X_parts)
    y = np.concatenate(y_parts)
    idx = rng.permutation(len(y))
    return X[idx], y[idx]


def split(X, y, n_train_per_class=40, seed=11):
    rng = np.random.default_rng(seed)
    train_idx, test_idx = [], []
    for k in range(3):
        idx = np.flatnonzero(y == k)
        rng.shuffle(idx)
        train_idx.extend(idx[:n_train_per_class].tolist())
        test_idx.extend(idx[n_train_per_class:].tolist())
    rng.shuffle(train_idx)
    rng.shuffle(test_idx)
    return X[train_idx], y[train_idx], X[test_idx], y[test_idx]


def softmax(Z):
    Z = np.asarray(Z, dtype=float)
    Z = Z - Z.max(axis=1, keepdims=True)
    E = np.exp(Z)
    return E / E.sum(axis=1, keepdims=True)


def loss_fn(X, y, W, b, alpha=0.0):
    P = softmax(X @ W.T + b)
    n = len(y)
    ce = -np.mean(np.log(np.clip(P[np.arange(n), y], 1e-12, 1.0)))
    reg = 0.5 * alpha * float(np.sum(W * W))
    return float(ce + reg)


def gradients(X, y, W, b, alpha=0.0):
    n = len(y)
    P = softmax(X @ W.T + b)
    Y = np.zeros_like(P)
    Y[np.arange(n), y] = 1.0
    G = (P - Y)
    gW = (G.T @ X) / n + alpha * W
    gb = G.mean(axis=0)
    return gW, gb


def train(X, y, lr=0.1, epochs=800, alpha=0.0, seed=3):
    rng = np.random.default_rng(seed)
    K, f = 3, X.shape[1]
    W = rng.normal(0.0, 0.01, size=(K, f))
    b = np.zeros(K)
    history = []
    for epoch in range(1, epochs + 1):
        history.append(loss_fn(X, y, W, b, alpha))
        gW, gb = gradients(X, y, W, b, alpha)
        W -= lr * gW
        b -= lr * gb
    history.append(loss_fn(X, y, W, b, alpha))
    return W, b, history


def predict(X, W, b):
    return softmax(X @ W.T + b).argmax(axis=1)


def confusion(y_true, y_pred, K=3):
    cm = np.zeros((K, K), dtype=int)
    for t, p in zip(y_true, y_pred):
        cm[t, p] += 1
    return cm


def prf_per_class(cm):
    rows = []
    for k in range(cm.shape[0]):
        tp = int(cm[k, k])
        fp = int(cm[:, k].sum() - tp)
        fn = int(cm[k, :].sum() - tp)
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        rows.append({"class": LABELS[k], "precision": p, "recall": r, "f1": f1,
                     "support": int(cm[k, :].sum())})
    return rows


def macro_metrics(rows):
    return {
        "precision": float(np.mean([r["precision"] for r in rows])),
        "recall": float(np.mean([r["recall"] for r in rows])),
        "f1": float(np.mean([r["f1"] for r in rows])),
    }


def micro_metrics(cm):
    tp = int(np.trace(cm))
    total = int(cm.sum())
    fp = int(cm.sum() - tp)
    fn = fp
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": p, "recall": r, "f1": f1}


def accuracy(y_true, y_pred):
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


def paired_bootstrap(y_true, pred_a, pred_b, b=2000, seed=19):
    """§4.11.1：有放回抽测试样本，统计 δ_boot >= 2δ 的比例作为单侧 p 值。"""
    rng = np.random.default_rng(seed)
    y_true = np.asarray(y_true)
    pred_a = np.asarray(pred_a)
    pred_b = np.asarray(pred_b)
    n = len(y_true)
    delta = accuracy(y_true, pred_a) - accuracy(y_true, pred_b)
    deltas = np.empty(b)
    for i in range(b):
        idx = rng.integers(0, n, size=n)
        yt = y_true[idx]
        deltas[i] = accuracy(yt, pred_a[idx]) - accuracy(yt, pred_b[idx])
    p_value = float(np.mean(deltas >= 2 * delta))
    return {
        "observed_delta": delta,
        "b": b,
        "p_value": p_value,
        "threshold": 0.01,
        "significant_at_0.01": p_value < 0.01,
        "deltas_mean": float(deltas.mean()),
        "deltas_q95": float(np.quantile(deltas, 0.95)),
        "deltas": deltas,
    }


def plot_confusion(cm, path):
    fig, ax = plt.subplots(figsize=(5.2, 4.4), dpi=140)
    im = ax.imshow(cm, cmap="Blues")
    cn = ["正面", "负面", "中性"]
    ax.set_xticks(range(3), cn, rotation=20)
    ax.set_yticks(range(3), cn)
    ax.set_xlabel("预测类别")
    ax.set_ylabel("金标准")
    ax.set_title("lab-02 混淆矩阵（测试集）")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "#222222",
                    fontsize=12)
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    X, y = make_dataset()
    Xtr, ytr, Xte, yte = split(X, y)
    W, b, hist = train(Xtr, ytr, lr=0.1, epochs=800, alpha=0.01)
    pred = predict(Xte, W, b)
    cm = confusion(yte, pred)
    rows = prf_per_class(cm)
    metrics = {
        "n_train": int(len(ytr)),
        "n_test": int(len(yte)),
        "accuracy": accuracy(yte, pred),
        "macro": macro_metrics(rows),
        "micro": micro_metrics(cm),
        "per_class": rows,
        "confusion_matrix": cm.tolist(),
        "final_test_loss": loss_fn(Xte, yte, W, b, alpha=0.01),
        "weights": W.tolist(),
        "bias": b.tolist(),
    }
    with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)
    plot_confusion(cm, os.path.join(OUT, "confusion_matrix.png"))

    # 学习率扫描
    lr_rows = []
    for lr in [0.01, 0.05, 0.1, 0.3, 0.6, 1.0]:
        Wl, bl, hl = train(Xtr, ytr, lr=lr, epochs=800, alpha=0.01)
        pl = predict(Xte, Wl, bl)
        lr_rows.append({"lr": lr, "train_loss": hl[-1],
                        "test_loss": loss_fn(Xte, yte, Wl, bl, alpha=0.01),
                        "test_accuracy": accuracy(yte, pl),
                        "macro_f1": macro_metrics(prf_per_class(confusion(yte, pl)))["f1"]})
    with open(os.path.join(OUT, "lr_comparison.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(lr_rows[0].keys()))
        writer.writeheader()
        writer.writerows(lr_rows)

    fig, ax1 = plt.subplots(figsize=(6, 4), dpi=140)
    lrs = [r["lr"] for r in lr_rows]
    ax1.plot(lrs, [r["test_loss"] for r in lr_rows], marker="o", color="#1f5fa8",
             label="测试交叉熵")
    ax1.set_xscale("log")
    ax1.set_xlabel("学习率（对数刻度）")
    ax1.set_ylabel("测试交叉熵", color="#1f5fa8")
    ax2 = ax1.twinx()
    ax2.plot(lrs, [r["test_accuracy"] for r in lr_rows], marker="s", color="#c0392b",
             label="测试准确率")
    ax2.set_ylabel("测试准确率", color="#c0392b")
    ax1.set_title("lab-02 学习率扫描（α=0.01）")
    ax1.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "lr_comparison.png"))
    plt.close(fig)

    # L2 强度扫描
    reg_rows = []
    for alpha in [0.0, 0.001, 0.01, 0.1, 1.0]:
        Wr, br, hr = train(Xtr, ytr, lr=0.1, epochs=800, alpha=alpha)
        pr = predict(Xte, Wr, br)
        reg_rows.append({
            "alpha": alpha,
            "train_loss": hr[-1],
            "test_loss": loss_fn(Xte, yte, Wr, br, alpha=alpha),
            "test_accuracy": accuracy(yte, pr),
            "macro_f1": macro_metrics(prf_per_class(confusion(yte, pr)))["f1"],
            "weight_l2": float(np.sqrt(np.sum(Wr * Wr))),
            "weight_l1": float(np.sum(np.abs(Wr))),
        })
    with open(os.path.join(OUT, "reg_comparison.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(reg_rows[0].keys()))
        writer.writeheader()
        writer.writerows(reg_rows)

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(8.4, 3.8), dpi=140)
    alphas = [r["alpha"] for r in reg_rows]
    axl.plot(alphas, [r["test_loss"] for r in reg_rows], marker="o", color="#1f5fa8")
    axl.set_xscale("symlog", linthresh=0.001)
    axl.set_xlabel("α（L2 强度，symlog）")
    axl.set_ylabel("测试交叉熵")
    axl.set_title("损失随正则强度的变化")
    axl.grid(alpha=0.25)
    axr.plot(alphas, [r["weight_l2"] for r in reg_rows], marker="s", color="#c0392b")
    axr.set_xscale("symlog", linthresh=0.001)
    axr.set_xlabel("α（L2 强度，symlog）")
    axr.set_ylabel("权重 L2 范数")
    axr.set_title("权重范数随 α 收缩")
    axr.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "reg_comparison.png"))
    plt.close(fig)

    # 配对自助检验：L2 正则模型（alpha=0.1） vs 无正则模型（alpha=0）
    # 两者差距不大，正好用来看 §4.11.1 的 2δ 保守阈值会给出什么结论
    W_reg, b_reg, _ = train(Xtr, ytr, lr=0.1, epochs=800, alpha=0.1)
    W_plain, b_plain, _ = train(Xtr, ytr, lr=0.1, epochs=800, alpha=0.0)
    pred_reg = predict(Xte, W_reg, b_reg)
    pred_plain = predict(Xte, W_plain, b_plain)
    boot = paired_bootstrap(yte, pred_reg, pred_plain, b=2000)
    boot_out = {k: v for k, v in boot.items() if k != "deltas"}
    boot_out["model_a"] = "L2 alpha=0.1"
    boot_out["model_b"] = "no regularization"
    boot_out["model_accuracy"] = accuracy(yte, pred_reg)
    boot_out["baseline_accuracy"] = accuracy(yte, pred_plain)
    with open(os.path.join(OUT, "bootstrap.json"), "w", encoding="utf-8") as f:
        json.dump(boot_out, f, ensure_ascii=False, indent=2)

    fig, ax = plt.subplots(figsize=(5.6, 3.8), dpi=140)
    ax.hist(boot["deltas"], bins=40, color="#1f5fa8", alpha=0.85)
    ax.axvline(boot["observed_delta"], color="#c0392b", linewidth=2,
               label=f"观测 δ={boot['observed_delta']:.3f}")
    ax.axvline(2 * boot["observed_delta"], color="#2c3e50", linestyle="--",
               label="2×δ（书中阈值）")
    ax.set_xlabel("δ（α=0.1 模型 − 无正则模型）")
    ax.set_ylabel("自助样本计数")
    ax.set_title(f"lab-02 配对自助检验（b=2000，p={boot['p_value']:.4f}）")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "bootstrap_hist.png"))
    plt.close(fig)

    print("=== lab-02 ===")
    print(f"train={len(ytr)} test={len(yte)}  accuracy={metrics['accuracy']:.3f}")
    print(f"macro  P/R/F1 = {metrics['macro']['precision']:.3f} / "
          f"{metrics['macro']['recall']:.3f} / {metrics['macro']['f1']:.3f}")
    print(f"micro  P/R/F1 = {metrics['micro']['precision']:.3f} / "
          f"{metrics['micro']['recall']:.3f} / {metrics['micro']['f1']:.3f}")
    print("confusion matrix:")
    print(cm)
    print("lr sweep:")
    for r in lr_rows:
        print(f"  lr={r['lr']:<5} test_loss={r['test_loss']:.4f} acc={r['test_accuracy']:.3f}")
    print("reg sweep:")
    for r in reg_rows:
        print(f"  alpha={r['alpha']:<6} test_loss={r['test_loss']:.4f} "
              f"acc={r['test_accuracy']:.3f} ||W||2={r['weight_l2']:.3f}")
    print("bootstrap:", json.dumps(boot_out, ensure_ascii=False))
    print("outputs:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
