#!/usr/bin/env python3
"""lab-03: 稀疏自编码器（SAE）的 λ 扫描

生成「叠加」激活：A = S @ F + 噪声，其中每行只有 k=4 个真特征非零。
在过完备字典（80 > 40）上训练 ReLU SAE，扫描 L1 系数 λ，
记录重建误差、平均激活特征数 L0 与真特征恢复度。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

RNG = np.random.default_rng(11)
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

D = 64
M_TRUE = 40
M_SAE = 80
N = 4000
K = 4
NOISE = 0.01
LAMBDAS = [0.0, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
STEPS = 1000
LR = 2e-3


def make_data():
    F = RNG.normal(size=(M_TRUE, D))
    F /= np.linalg.norm(F, axis=1, keepdims=True)
    S = np.zeros((N, M_TRUE))
    for i in range(N):
        idx = RNG.choice(M_TRUE, size=K, replace=False)
        S[i, idx] = RNG.uniform(0.5, 2.0, size=K)
    A = S @ F + RNG.normal(scale=NOISE, size=(N, D))
    return A, F, S


def train_sae(Atr, lam, steps=STEPS, lr=LR, seed=0):
    rng = np.random.default_rng(seed)
    n, d = Atr.shape
    Wd = rng.normal(size=(d, M_SAE)) * 0.1
    Wd /= np.linalg.norm(Wd, axis=0, keepdims=True)
    We = Wd.T.copy() * 1.0
    be = np.zeros(M_SAE)
    bd = np.zeros(d)
    params = [We, be, Wd, bd]
    ms = [np.zeros_like(p) for p in params]
    vs = [np.zeros_like(p) for p in params]
    b1, b2, eps = 0.9, 0.999, 1e-8
    for t in range(1, steps + 1):
        pre = Atr @ Wd + be
        Z = np.maximum(pre, 0.0)
        rec = Z @ We + bd
        diff = rec - Atr
        mse = np.mean(diff ** 2)
        l1 = np.mean(Z)
        loss = mse + lam * l1
        drec = 2.0 * diff / (n * d)
        gWe = Z.T @ drec
        gbd = drec.sum(axis=0)
        dZ = drec @ We.T + lam / (n * M_SAE)
        dZ *= (pre > 0)
        gWd = Atr.T @ dZ
        gbe = dZ.sum(axis=0)
        grads = [gWe, gbe, gWd, gbd]
        for p, g, m, v in zip(params, grads, ms, vs):
            m *= b1
            m += (1 - b1) * g
            v *= b2
            v += (1 - b2) * g * g
            mh = m / (1 - b1 ** t)
            vh = v / (1 - b2 ** t)
            p -= lr * mh / (np.sqrt(vh) + eps)
        if t % 200 == 0 or t == 1:
            print(f"  λ={lam:<5} step {t:4d} loss={loss:.5f} mse={mse:.5f} L0={np.mean((Z > 1e-4).sum(1)):.2f}")
    return We, be, Wd, bd


def evaluate(A, We, be, Wd, bd, F, lam):
    pre = A @ Wd + be
    Z = np.maximum(pre, 0.0)
    rec = Z @ We + bd
    mse = float(np.mean((rec - A) ** 2))
    l0 = float(np.mean((Z > 1e-4).sum(axis=1)))
    dead = float(np.mean((Z > 1e-4).sum(axis=0) == 0))
    Dn = Wd / (np.linalg.norm(Wd, axis=0, keepdims=True) + 1e-8)
    cos = Dn.T @ F.T  # M_SAE × M_TRUE
    best = cos.max(axis=0)
    return {
        "lambda": lam,
        "mse": round(mse, 6),
        "l0": round(l0, 3),
        "dead_feature_frac": round(dead, 3),
        "mean_best_cosine": round(float(best.mean()), 4),
        "frac_cosine_gt_0.8": round(float((best > 0.8).mean()), 3),
    }


def main() -> None:
    A, F, _ = make_data()
    n_train = int(0.8 * N)
    Atr, Ate = A[:n_train], A[n_train:]

    rows = []
    for lam in LAMBDAS:
        print(f"λ={lam}")
        We, be, Wd, bd = train_sae(Atr, lam)
        rows.append(evaluate(Ate, We, be, Wd, bd, F, lam))

    with open(OUT / "sae_lambda_sweep.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    best = min(rows, key=lambda r: r["mse"])
    near_k = min([r for r in rows if r["l0"] <= K + 2],
                 key=lambda r: r["mse"])
    summary = {
        "n_samples": N, "dim": D, "true_features": M_TRUE,
        "sae_features": M_SAE, "true_l0": K,
        "min_mse_lambda": best["lambda"],
        "selection_criterion": f"在 L0 <= {K + 2} 的行中取 MSE 最小",
        "selected": near_k,
    }
    with open(OUT / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "Noto Sans CJK JP", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False

    lams = [r["lambda"] for r in rows]
    fig, axes = plt.subplots(1, 3, figsize=(14, 3.8))
    axes[0].plot(lams, [r["mse"] for r in rows], marker="o", color="#1f77b4")
    axes[0].set_xlabel("λ（L1 系数）")
    axes[0].set_ylabel("测试 MSE")
    axes[0].set_title("重建误差随 λ 上升")
    axes[0].grid(alpha=0.25)

    axes[1].plot(lams, [r["l0"] for r in rows], marker="o", color="#d62728", label="SAE 的 L0")
    axes[1].axhline(K, ls=":", color="#2ca02c", label=f"真实 k={K}")
    axes[1].set_xlabel("λ（L1 系数）")
    axes[1].set_ylabel("平均激活特征数")
    axes[1].set_title("稀疏度随 λ 上升")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=0.25)

    axes[2].plot(lams, [r["mean_best_cosine"] for r in rows], marker="o", color="#9467bd")
    axes[2].set_xlabel("λ（L1 系数）")
    axes[2].set_ylabel("真特征平均最佳余弦")
    axes[2].set_ylim(0, 1.02)
    axes[2].set_title("字典与真特征的对齐度")
    axes[2].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(OUT / "sae_lambda_sweep.png", dpi=150)

    for r in rows:
        print(r)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
