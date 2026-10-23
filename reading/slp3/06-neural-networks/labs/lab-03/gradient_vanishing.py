#!/usr/bin/env python3
"""Lab-03：激活函数与梯度消失——逐层测量反向传播的梯度范数。

对应《Speech and Language Processing》第 6 章 §6.1（饱和与梯度消失）
与 §6.6.4（链式法则逐层回传）。
网络：2 → 24 × 6 隐藏层 → 1，sigmoid 输出，BCE 损失，全批量梯度下降。
数据：两条交错的月牙（two moons），可构造、无需外部依赖。
输出：
  out/gradient_norms.csv   各激活函数、各层的初始/最终梯度范数
  out/summary.json         测试准确率、梯度衰减比、是否低于 1e-6
  out/gradient_norms.png   梯度范数随层深变化（对数纵轴）
  out/decision_boundary.png 三种激活函数学到的边界
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

SEED = 3
N_HIDDEN = 24
N_LAYERS = 10
EPOCHS = 2500
LR = 0.08
ACTIVATIONS = ("sigmoid", "tanh", "relu")


def make_moons(n, noise=0.12, seed=SEED):
    rng = np.random.default_rng(seed)
    n0 = n // 2
    n1 = n - n0
    t0 = rng.uniform(0, np.pi, n0)
    t1 = rng.uniform(0, np.pi, n1)
    x0 = np.c_[np.cos(t0), np.sin(t0)] + rng.normal(0, noise, (n0, 2))
    x1 = np.c_[1 - np.cos(t1), -np.sin(t1) - 0.5] + rng.normal(0, noise, (n1, 2))
    x = np.vstack([x0, x1])
    y = np.r_[np.zeros(n0), np.ones(n1)].reshape(-1, 1)
    perm = rng.permutation(n)
    return x[perm], y[perm]


def act_forward(name, z):
    if name == "sigmoid":
        return 1.0 / (1.0 + np.exp(-z))
    if name == "tanh":
        return np.tanh(z)
    return np.maximum(z, 0.0)


def act_backward(name, z, a):
    if name == "sigmoid":
        return a * (1.0 - a)
    if name == "tanh":
        return 1.0 - a ** 2
    return (z > 0.0).astype(z.dtype)


def init_net(name, d_in=2, hidden=N_HIDDEN, layers=N_LAYERS, seed=SEED):
    rng = np.random.default_rng(seed)
    params, grads_shape = [], []
    prev = d_in
    for _ in range(layers):
        scale = np.sqrt(2.0 / prev) if name == "relu" else np.sqrt(1.0 / prev)
        params.append({
            "w": rng.normal(0.0, scale, size=(prev, hidden)),
            "b": np.zeros((1, hidden)),
        })
        prev = hidden
    params.append({"w": rng.normal(0.0, np.sqrt(1.0 / prev), size=(prev, 1)), "b": np.zeros((1, 1))})
    return params


def forward(name, params, x):
    zs, acts = [], []
    a = x
    for layer in params[:-1]:
        z = a @ layer["w"] + layer["b"]
        a = act_forward(name, z)
        zs.append(z)
        acts.append(a)
    out = params[-1]
    z_out = a @ out["w"] + out["b"]
    y_hat = 1.0 / (1.0 + np.exp(-z_out))
    return y_hat, zs, acts


def backward(name, params, zs, acts, x, y, y_hat):
    m = y.shape[0]
    grads = [dict() for _ in params]
    dz = (y_hat - y) / m
    grads[-1]["w"] = acts[-1].T @ dz
    grads[-1]["b"] = dz.sum(axis=0, keepdims=True)
    da = dz @ params[-1]["w"].T
    for i in range(len(params) - 2, -1, -1):
        dz = da * act_backward(name, zs[i], acts[i])
        inp = x if i == 0 else acts[i - 1]
        grads[i]["w"] = inp.T @ dz
        grads[i]["b"] = dz.sum(axis=0, keepdims=True)
        da = dz @ params[i]["w"].T
    return grads


def layer_norms(grads):
    return [float(np.linalg.norm(g["w"])) for g in grads[:-1]]


def train(name, x, y, x_test, y_test):
    params = init_net(name)
    y_hat0, zs0, acts0 = forward(name, params, x)
    g0 = backward(name, params, zs0, acts0, x, y, y_hat0)
    norms_init = layer_norms(g0)

    losses = []
    for _ in range(EPOCHS):
        y_hat, zs, acts = forward(name, params, x)
        loss = float(-np.mean(y * np.log(y_hat + 1e-12) + (1 - y) * np.log(1 - y_hat + 1e-12)))
        losses.append(loss)
        grads = backward(name, params, zs, acts, x, y, y_hat)
        for p, g in zip(params, grads):
            p["w"] -= LR * g["w"]
            p["b"] -= LR * g["b"]

    y_hat, zs, acts = forward(name, params, x)
    gf = backward(name, params, zs, acts, x, y, y_hat)
    norms_final = layer_norms(gf)
    test_hat, _, _ = forward(name, params, x_test)
    acc = float(((test_hat >= 0.5).astype(float) == y_test).mean())
    return params, norms_init, norms_final, acc, losses[-1]


def plot_norms(rows):
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    for ax, key, title in ((axes[0], "grad_norm_init", "at initialization"),
                           (axes[1], "grad_norm_final", "after training")):
        for name, color in (("sigmoid", "#c0392b"), ("tanh", "#2980b9"), ("relu", "#27ae60")):
            sub = [r for r in rows if r["activation"] == name]
            xs = [r["layer"] for r in sub]
            ys = [max(r[key], 1e-16) for r in sub]
            ax.plot(xs, ys, marker="o", label=name, color=color)
        ax.set_yscale("log")
        ax.set_xlabel("hidden layer (1 = closest to input)")
        ax.set_title(title)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("||dL/dW||_F")
    axes[0].axhline(1e-6, color="gray", linestyle=":", linewidth=1, label="1e-6")
    axes[0].legend(fontsize=8)
    fig.suptitle(f"Gradient norm by depth (2-{N_HIDDEN}x{N_LAYERS}-1, BCE)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "gradient_norms.png"), dpi=160)
    plt.close(fig)


def plot_boundaries(results, x, y):
    lo = x.min(axis=0) - 0.3
    hi = x.max(axis=0) + 0.3
    gx, gy = np.meshgrid(np.linspace(lo[0], hi[0], 220), np.linspace(lo[1], hi[1], 220))
    pts = np.c_[gx.ravel(), gy.ravel()]
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 3.8), sharey=True)
    for ax, name in zip(axes, ACTIVATIONS):
        y_hat, _, _ = forward(name, results[name]["params"], pts)
        zz = y_hat.reshape(gx.shape)
        ax.contourf(gx, gy, zz, levels=np.linspace(0, 1, 15), cmap="RdBu_r", alpha=0.8)
        ax.contour(gx, gy, zz, levels=[0.5], colors="k", linewidths=1.2)
        ax.scatter(x[y.ravel() == 0, 0], x[y.ravel() == 0, 1], s=9, c="#1f3b73")
        ax.scatter(x[y.ravel() == 1, 0], x[y.ravel() == 1, 1], s=9, c="#b03a2e")
        ax.set_title(f"{name} (acc={results[name]['acc']:.3f})")
        ax.set_xlabel("x1")
    axes[0].set_ylabel("x2")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "decision_boundary.png"), dpi=160)
    plt.close(fig)


def main():
    x, y = make_moons(320)
    x_test, y_test = make_moons(320, seed=SEED + 100)
    rows, results, summary = [], {}, {}
    for name in ACTIVATIONS:
        params, n_init, n_final, acc, loss = train(name, x, y, x_test, y_test)
        results[name] = {"params": params, "acc": acc}
        for i, (a, b) in enumerate(zip(n_init, n_final), start=1):
            rows.append({
                "activation": name,
                "layer": i,
                "grad_norm_init": a,
                "grad_norm_final": b,
                "decay_ratio": a / max(b, 1e-16),
            })
        summary[name] = {
            "test_accuracy": acc,
            "final_train_loss": loss,
            "grad_norm_init_by_layer": n_init,
            "grad_norm_final_by_layer": n_final,
            "init_min_grad_norm": min(n_init),
            "layers_below_1e-6_init": int(sum(1 for v in n_init if v < 1e-6)),
        }

    with open(os.path.join(OUT, "gradient_norms.csv"), "w", encoding="utf-8") as f:
        f.write("activation,layer,grad_norm_init,grad_norm_final,decay_ratio\n")
        for r in rows:
            f.write(f"{r['activation']},{r['layer']},{r['grad_norm_init']:.10e},"
                    f"{r['grad_norm_final']:.10e},{r['decay_ratio']:.6e}\n")

    with open(os.path.join(OUT, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({
            "architecture": f"2-{N_HIDDEN}x{N_LAYERS}-1",
            "epochs": EPOCHS,
            "learning_rate": LR,
            "seed": SEED,
            "by_activation": summary,
        }, f, ensure_ascii=False, indent=2)

    plot_norms(rows)
    plot_boundaries(results, x, y)
    print(json.dumps({k: {
        "accuracy": v["test_accuracy"],
        "init_norms": [f"{z:.2e}" for z in v["grad_norm_init_by_layer"]],
        "below_1e-6": v["layers_below_1e-6_init"],
    } for k, v in summary.items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
