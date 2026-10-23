#!/usr/bin/env python3
"""lab-01: 从零实现二分类逻辑回归（sigmoid + 交叉熵 + 批量梯度下降）。

对应 actions.md 第 1、2 条：
  1) 在 22 条可解释的影评特征上训练，画损失曲线与决策边界，导出权重；
  2) 复现书中 §4.6.3 的单步梯度更新，并用数值梯度校验解析梯度。

运行：
    python3 logreg_binary.py
产物写入 ./out/：loss_curve.png, decision_boundary.png, weights.json,
gradient_step.json, training_log.csv
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

# 20 条迷你影评：x1 = 正向词典词数, x2 = 负向词典词数, y = 1 正面 / 0 负面
DOCS = [
    ("ab", "great fun and lovely acting", 3, 0, 1),
    ("ac", "wonderful story, I love it", 2, 0, 1),
    ("ad", "nice visuals but a dull plot", 3, 1, 1),
    ("ae", "excellent and enjoyable", 4, 1, 1),
    ("af", "good enough", 2, 1, 1),
    ("ag", "lovely little film", 1, 0, 1),
    ("ah", "great cast, weak ending", 3, 2, 1),
    ("ai", "superb and smart", 4, 0, 1),
    ("aj", "pleasant surprise", 2, 0, 1),
    ("ak", "fine, though uneven", 3, 1, 1),
    ("al", "boring and awful", 0, 2, 0),
    ("am", "dull, painfully slow", 1, 3, 0),
    ("an", "terrible script", 0, 3, 0),
    ("ao", "awful and pointless", 1, 2, 0),
    ("ap", "bad acting, bad pacing", 2, 3, 0),
    ("aq", "not good at all", 0, 1, 0),
    ("ar", "ridiculously tedious", 1, 4, 0),
    ("as", "ugly and dull", 2, 2, 0),
    ("at", "boring waste of time", 0, 2, 0),
    ("au", "weak and awful", 1, 3, 0),
    # 两条故意歧义的样本，避免完全可分导致权重无限增大
    ("av", "great acting, awful story", 1, 2, 1),
    ("aw", "dull start, lovely ending", 2, 1, 0),
]

X = np.array([[d[2], d[3]] for d in DOCS], dtype=float)
y = np.array([d[4] for d in DOCS], dtype=float)


def sigmoid(z):
    # 数值稳定写法：避免 exp 溢出
    z = np.asarray(z, dtype=float)
    out = np.empty_like(z)
    pos = z >= 0
    out[pos] = 1.0 / (1.0 + np.exp(-z[pos]))
    ez = np.exp(z[~pos])
    out[~pos] = ez / (1.0 + ez)
    return out


def linear_scores(X, w, b):
    return X @ np.asarray(w, dtype=float) + float(b)


def cross_entropy(y, y_hat):
    y = np.asarray(y, dtype=float)
    y_hat = np.clip(np.asarray(y_hat, dtype=float), 1e-12, 1 - 1e-12)
    return float(-np.mean(y * np.log(y_hat) + (1 - y) * np.log(1 - y_hat)))


def gradients(X, y, w, b):
    """交叉熵对 w、b 的解析梯度（书中式 4.26/4.28 的批平均版本）。"""
    err = sigmoid(linear_scores(X, w, b)) - y
    m = X.shape[0]
    return (X.T @ err) / m, float(np.mean(err))


def train(X, y, lr=0.5, epochs=600):
    w = np.zeros(X.shape[1], dtype=float)
    b = 0.0
    history = []
    for epoch in range(1, epochs + 1):
        loss = cross_entropy(y, sigmoid(linear_scores(X, w, b)))
        gw, gb = gradients(X, y, w, b)
        w -= lr * gw
        b -= lr * gb
        acc = float(np.mean((sigmoid(linear_scores(X, w, b)) > 0.5) == y))
        history.append((epoch, loss, acc, w[0], w[1], b))
    return w, b, history


def numerical_gradient_check():
    """复现 §4.6.3：x=[3,2], y=1, 初始 w=b=0，学习率 0.1。"""
    x = np.array([[3.0, 2.0]])
    yy = np.array([1.0])
    w = np.zeros(2)
    b = 0.0
    loss0 = cross_entropy(yy, sigmoid(linear_scores(x, w, b)))
    gw, gb = gradients(x, yy, w, b)
    lr = 0.1
    w1 = w - lr * gw
    b1 = b - lr * gb

    # 数值梯度：中心差分
    eps = 1e-6
    num = []
    for j in range(2):
        wp = w.copy()
        wm = w.copy()
        wp[j] += eps
        wm[j] -= eps
        lp = cross_entropy(yy, sigmoid(linear_scores(x, wp, b)))
        lm = cross_entropy(yy, sigmoid(linear_scores(x, wm, b)))
        num.append((lp - lm) / (2 * eps))
    lp = cross_entropy(yy, sigmoid(linear_scores(x, w, b + eps)))
    lm = cross_entropy(yy, sigmoid(linear_scores(x, w, b - eps)))
    num_b = (lp - lm) / (2 * eps)
    rel = [abs(gw[j] - num[j]) / max(1e-12, abs(num[j])) for j in range(2)]
    rel_b = abs(gb - num_b) / max(1e-12, abs(num_b))

    return {
        "input": {"x": x.tolist()[0], "y": int(yy[0])},
        "loss_at_init": loss0,
        "analytic_grad": {"w": gw.tolist(), "b": gb},
        "numerical_grad": {"w": num, "b": num_b},
        "relative_error": {"w": rel, "b": rel_b},
        "after_one_step": {
            "w": w1.tolist(),
            "b": b1,
            "loss": cross_entropy(yy, sigmoid(linear_scores(x, w1, b1))),
        },
        "book_expected": {"w": [0.15, 0.1], "b": 0.05},
    }


def main():
    w, b, history = train(X, y, lr=0.5, epochs=600)
    final_loss = history[-1][1]
    y_hat = sigmoid(linear_scores(X, w, b))
    acc = float(np.mean((y_hat > 0.5) == y))

    with open(os.path.join(OUT, "training_log.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "loss", "train_accuracy", "w_pos", "w_neg", "bias"])
        writer.writerows(history)

    weights = {
        "features": ["count(positive lexicon words)", "count(negative lexicon words)"],
        "w": w.tolist(),
        "b": b,
        "final_train_loss": final_loss,
        "train_accuracy": acc,
        "epochs": len(history),
        "learning_rate": 0.5,
        "predictions": [
            {"doc": d[0], "x": [d[2], d[3]], "y": d[4], "p_positive": float(p)}
            for d, p in zip(DOCS, y_hat)
        ],
    }
    with open(os.path.join(OUT, "weights.json"), "w", encoding="utf-8") as f:
        json.dump(weights, f, ensure_ascii=False, indent=2)

    step = numerical_gradient_check()
    with open(os.path.join(OUT, "gradient_step.json"), "w", encoding="utf-8") as f:
        json.dump(step, f, ensure_ascii=False, indent=2)

    # 损失曲线
    epochs = [h[0] for h in history]
    losses = [h[1] for h in history]
    fig, ax = plt.subplots(figsize=(6, 4), dpi=140)
    ax.plot(epochs, losses, color="#1f5fa8", linewidth=2)
    ax.set_xlabel("训练轮次")
    ax.set_ylabel("二分类交叉熵（批平均）")
    ax.set_title("lab-01 训练损失（批量 GD，学习率 0.5）")
    ax.grid(alpha=0.3)
    ax.annotate(
        f"最终 {final_loss:.4f}",
        xy=(epochs[-1], losses[-1]),
        xytext=(-110, 30),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#333333"},
    )
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "loss_curve.png"))
    plt.close(fig)

    # 决策边界
    fig, ax = plt.subplots(figsize=(6, 4.6), dpi=140)
    for label, color, marker in ((1, "#1f5fa8", "o"), (0, "#c0392b", "s")):
        mask = y == label
        ax.scatter(X[mask, 0], X[mask, 1], c=color, marker=marker, s=55,
                   edgecolor="white", linewidth=0.8,
                   label="正面" if label == 1 else "负面")
    xs = np.linspace(-0.5, 5.0, 200)
    if abs(w[1]) > 1e-9:
        ys = -(w[0] * xs + b) / w[1]
        ax.plot(xs, ys, color="#2c3e50", linewidth=2, label="决策边界 p=0.5")
    ax.set_xlim(-0.5, 5.0)
    ax.set_ylim(-0.5, 5.0)
    ax.set_xlabel("x1：正向词典词数")
    ax.set_ylabel("x2：负向词典词数")
    ax.set_title(f"lab-01 决策边界（训练准确率 {acc:.2f}）")
    ax.legend(loc="upper right", fontsize=8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "decision_boundary.png"))
    plt.close(fig)

    print("=== lab-01 ===")
    print(f"documents: {len(DOCS)}  features: {X.shape[1]}")
    print(f"learned weights: w={np.round(w, 4).tolist()}  b={round(b, 4)}")
    print(f"final train loss: {final_loss:.4f}  train accuracy: {acc:.3f}")
    print("gradient step (book §4.6.3):")
    print(json.dumps(step, ensure_ascii=False, indent=2))
    print("outputs:", sorted(os.listdir(OUT)))


if __name__ == "__main__":
    main()
