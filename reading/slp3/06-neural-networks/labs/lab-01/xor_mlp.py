#!/usr/bin/env python3
"""Lab-01：从零实现单隐藏层前馈网络（numpy 手写前向/反向），在 XOR 上训练。

对应《Speech and Language Processing》第 6 章 §6.1–§6.3、§6.6。
输出：
  out/loss_history.csv      每次迭代的损失
  out/gradient_check.json   有限差分梯度校验
  out/summary.json          最终损失、预测、准确率
  out/loss_curve.png        损失曲线
  out/decision_boundary.png 决策边界
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

SEED = 7
N_HIDDEN = 8
EPOCHS = 4000
LR = 0.5

X = np.array([[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]])
Y = np.array([[0.0], [1.0], [1.0], [0.0]])


def init_params(seed=SEED, n_hidden=N_HIDDEN):
    rng = np.random.default_rng(seed)
    w1 = rng.normal(0.0, np.sqrt(2.0 / 2.0), size=(2, n_hidden))
    b1 = rng.normal(0.0, 0.01, size=(1, n_hidden))
    w2 = rng.normal(0.0, np.sqrt(1.0 / n_hidden), size=(n_hidden, 1))
    b2 = rng.normal(0.0, 0.01, size=(1, 1))
    return {"w1": w1, "b1": b1, "w2": w2, "b2": b2}


def forward(params, x):
    z1 = x @ params["w1"] + params["b1"]
    a1 = np.maximum(z1, 0.0)
    z2 = a1 @ params["w2"] + params["b2"]
    y_hat = 1.0 / (1.0 + np.exp(-z2))
    cache = {"x": x, "z1": z1, "a1": a1, "z2": z2, "y_hat": y_hat}
    return y_hat, cache


def bce(y_hat, y):
    eps = 1e-12
    return float(-np.mean(y * np.log(y_hat + eps) + (1.0 - y) * np.log(1.0 - y_hat + eps)))


def backward(params, cache, y):
    x, z1, a1, y_hat = cache["x"], cache["z1"], cache["a1"], cache["y_hat"]
    m = x.shape[0]
    dz2 = (y_hat - y) / m
    dw2 = a1.T @ dz2
    db2 = dz2.sum(axis=0, keepdims=True)
    da1 = dz2 @ params["w2"].T
    dz1 = da1 * (z1 > 0.0)
    dw1 = x.T @ dz1
    db1 = dz1.sum(axis=0, keepdims=True)
    return {"w1": dw1, "b1": db1, "w2": dw2, "b2": db2}


def loss_of(params):
    y_hat, _ = forward(params, X)
    return bce(y_hat, Y)


def numerical_grad(params, key, idx, eps=1e-6):
    orig = params[key][idx]
    params[key][idx] = orig + eps
    plus = loss_of(params)
    params[key][idx] = orig - eps
    minus = loss_of(params)
    params[key][idx] = orig
    return (plus - minus) / (2.0 * eps)


def check_gradients(params, grads):
    """按解析梯度的绝对值挑 6 个非退化参数做中心差分校验。

    梯度接近 0 的参数不适合算相对误差（分母趋零会放大噪声），因此
    先排序再选点，并在结果里保留解析梯度大小供读者判断。
    """
    candidates = []
    for key in ("w1", "b1", "w2", "b2"):
        arr = grads[key]
        for idx in np.ndindex(arr.shape):
            candidates.append((abs(float(arr[idx])), key, idx))
    candidates.sort(reverse=True, key=lambda t: t[0])

    rows = []
    for _, key, idx in candidates[:6]:
        num = numerical_grad(params, key, idx)
        ana = float(grads[key][idx])
        denom = max(1e-12, abs(num) + abs(ana))
        rows.append({
            "param": f"{key}[{idx[0]},{idx[1]}]",
            "numerical": num,
            "analytic": ana,
            "abs_diff": abs(num - ana),
            "rel_error": abs(num - ana) / denom,
        })
    return rows


def train():
    params = init_params()
    losses = []
    for epoch in range(EPOCHS + 1):
        y_hat, cache = forward(params, X)
        loss = bce(y_hat, Y)
        losses.append((epoch, loss))
        if epoch == EPOCHS:
            break
        grads = backward(params, cache, Y)
        for key in params:
            params[key] -= LR * grads[key]
    return params, losses


def make_plots(params, losses):
    epochs = [e for e, _ in losses]
    vals = [v for _, v in losses]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(epochs, vals, color="#c0392b", linewidth=1.6)
    ax.set_yscale("log")
    ax.set_xlabel("epoch")
    ax.set_ylabel("binary cross-entropy (log scale)")
    ax.set_title("XOR training loss (2-8-1, ReLU hidden, sigmoid output)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "loss_curve.png"), dpi=160)
    plt.close(fig)

    grid = np.linspace(-0.25, 1.25, 220)
    gx, gy = np.meshgrid(grid, grid)
    pts = np.c_[gx.ravel(), gy.ravel()]
    probs, _ = forward(params, pts)
    probs = probs.reshape(gx.shape)

    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    cf = ax.contourf(gx, gy, probs, levels=np.linspace(0, 1, 21), cmap="RdBu_r", alpha=0.85)
    ax.contour(gx, gy, probs, levels=[0.5], colors="k", linewidths=1.4)
    ax.scatter(X[Y.ravel() == 0, 0], X[Y.ravel() == 0, 1], s=90, c="#1f3b73", edgecolors="w", label="label 0")
    ax.scatter(X[Y.ravel() == 1, 0], X[Y.ravel() == 1, 1], s=90, c="#b03a2e", edgecolors="w", label="label 1")
    ax.set_xlabel("x1")
    ax.set_ylabel("x2")
    ax.set_title("Learned decision boundary")
    ax.legend(loc="upper right", fontsize=9)
    fig.colorbar(cf, ax=ax, label="P(y=1)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "decision_boundary.png"), dpi=160)
    plt.close(fig)


def main():
    init = init_params()
    init_hat, init_cache = forward(init, X)
    init_rows = check_gradients(init, backward(init, init_cache, Y))

    params, losses = train()
    y_hat, cache = forward(params, X)
    grads = backward(params, cache, Y)
    rows = check_gradients(params, grads)
    preds = (y_hat >= 0.5).astype(int).ravel()
    acc = float((preds == Y.ravel()).mean())

    with open(os.path.join(OUT, "loss_history.csv"), "w", encoding="utf-8") as f:
        f.write("epoch,loss\n")
        for e, v in losses:
            f.write(f"{e},{v:.10f}\n")

    with open(os.path.join(OUT, "gradient_check.json"), "w", encoding="utf-8") as f:
        json.dump({
            "at_initialization": init_rows,
            "after_training": rows,
            "max_rel_error_initial": max(r["rel_error"] for r in init_rows),
            "max_rel_error_after_training": max(r["rel_error"] for r in rows),
            "epsilon": 1e-6,
            "note": "central finite difference vs analytic backprop",
        }, f, ensure_ascii=False, indent=2)

    summary = {
        "seed": SEED,
        "architecture": "2-8-1 (ReLU hidden, sigmoid output)",
        "epochs": EPOCHS,
        "learning_rate": LR,
        "initial_loss": losses[0][1],
        "final_loss": losses[-1][1],
        "final_probabilities": [round(float(v), 6) for v in y_hat.ravel()],
        "predictions": preds.tolist(),
        "targets": Y.ravel().astype(int).tolist(),
        "accuracy": acc,
        "max_grad_rel_error_initial": max(r["rel_error"] for r in init_rows),
        "max_grad_rel_error_after_training": max(r["rel_error"] for r in rows),
    }
    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    make_plots(params, losses)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("\nProbes:")
    for r in rows:
        print(f"  {r['param']:12s} num={r['numerical']:+.8f} ana={r['analytic']:+.8f} rel={r['rel_error']:.2e}")


if __name__ == "__main__":
    main()
