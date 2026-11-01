#!/usr/bin/env python3
"""lab-03: k-means 粒度效应 toy 实验（SLP3 §16.4.2–16.4.3）

合成 3 类「元音-like」2 维高斯（模拟 39 维倒谱被 PCA 到 2 维的 toy 版），
扫 k=2..12，记录纯度（purity）与 ARI，检验 HuBERT 直觉：
- k 等于真实类数（3）时纯度/ARI 最高
- k 过大时纯度仍可能上升但 ARI 下降（过拟合）
输出：out/k_sweep.csv、out/k_sweep_summary.json
"""
import csv, json, os
import numpy as np

rng = np.random.default_rng(42)
CENTERS = np.array([[0.0, 0.0], [3.0, 0.0], [0.0, 3.0]])
N_PER = 100
N_INIT = 5


def gen():
    X, y = [], []
    for c, mu in enumerate(CENTERS):
        X.append(rng.normal(mu, 0.6, size=(N_PER, 2)))
        y += [c] * N_PER
    return np.vstack(X), np.array(y)


def kmeans(X, k, seed):
    r = np.random.default_rng(seed)
    idx = r.choice(len(X), k, replace=False)
    C = X[idx].copy()
    for _ in range(50):
        d = ((X[:, None, :] - C[None, :, :]) ** 2).sum(-1)
        z = d.argmin(1)
        new = np.array([X[z == j].mean(0) if (z == j).any() else C[j] for j in range(k)])
        if np.allclose(new, C):
            break
        C = new
    return z, C


def purity(y, z):
    total = 0
    for j in set(z):
        mask = z == j
        if mask.sum() == 0:
            continue
        vals, cnt = np.unique(y[mask], return_counts=True)
        total += cnt.max()
    return total / len(y)


def ari(y, z):
    from itertools import combinations
    n = len(y)
    agree = sum(1 for i, j in combinations(range(n), 2)
                if (y[i] == y[j]) == (z[i] == z[j]))
    return agree / (n * (n - 1) / 2)


def main():
    os.makedirs("out", exist_ok=True)
    X, y = gen()
    rows, summary = [], []
    for k in range(2, 13):
        ps, ars, inertias = [], [], []
        for s in range(N_INIT):
            z, C = kmeans(X, k, seed=s)
            ps.append(purity(y, z))
            ars.append(ari(y, z))
            inertias.append(((X - C[z]) ** 2).sum())
        rows.append([k, round(np.mean(ps), 4), round(np.std(ps), 4),
                     round(min(ps), 4), round(max(ps), 4),
                     round(np.mean(ars), 4), round(np.mean(inertias), 1)])
        summary.append({"k": k, "purity_mean": float(np.mean(ps)),
                        "purity_range": float(max(ps) - min(ps)),
                        "ari_mean": float(np.mean(ars))})
    with open("out/k_sweep.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["k", "purity_mean", "purity_std", "purity_min", "purity_max",
                    "ari_mean", "inertia_mean"])
        w.writerows(rows)
    json.dump({"n_per_class": N_PER, "n_init": N_INIT,
               "sweep": summary},
              open("out/k_sweep_summary.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
