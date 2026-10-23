#!/usr/bin/env python3
"""Lab-03: best-of-N 重排的收益上限——奖励模型噪声如何吃掉采样收益。

场景：对每个提示采样 N 个候选，真实质量 z ~ N(0,1)；
奖励模型给出 r = z + eps，eps ~ N(0, sigma^2)。
按 r 取 argmax，记录被选中候选的真实质量 z_sel。
指标：E[z_sel]、选中真最优的概率、奖励高估（r_sel - z_sel）。
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

N_LIST = [1, 2, 4, 8, 16, 32, 64, 128]
SIGMAS = [0.0, 0.25, 0.5, 1.0, 2.0]
TRIALS = 4000
K = 8  # 每次批量抽样的提示数，控制内存


def simulate(n, sigma):
    z_sel, r_sel, is_best = [], [], []
    done = 0
    while done < TRIALS:
        batch = min(K, TRIALS - done)
        z = rng.normal(size=(batch, n))
        r = z + sigma * rng.normal(size=(batch, n))
        pick = np.argmax(r, axis=1)
        rows = np.arange(batch)
        z_sel.append(z[rows, pick])
        r_sel.append(r[rows, pick])
        is_best.append(z[rows, pick] == z.max(axis=1))
        done += batch
    return np.concatenate(z_sel), np.concatenate(r_sel), np.concatenate(is_best)


rows, curves = [], {}
for sigma in SIGMAS:
    curve = []
    for n in N_LIST:
        z_sel, r_sel, is_best = simulate(n, sigma)
        row = {
            "sigma": sigma,
            "N": n,
            "expected_true_quality": float(z_sel.mean()),
            "prob_select_true_best": float(is_best.mean()),
            "reward_overestimate": float((r_sel - z_sel).mean()),
        }
        rows.append(row)
        curve.append(row)
    curves[f"{sigma:g}"] = curve

# N=1 的基准（与 sigma 无关）
baseline = curves["0"][0]["expected_true_quality"]
report = {
    "baseline_expected_quality_N1": baseline,
    "rows": rows,
    "summary": {
        s: {
            "best_true_quality": max(c["expected_true_quality"] for c in curves[s]),
            "gain_vs_N1": max(c["expected_true_quality"] for c in curves[s]) - baseline,
            "true_quality_at_N128": curves[s][-1]["expected_true_quality"],
            "reward_overestimate_at_N128": curves[s][-1]["reward_overestimate"],
        }
        for s in curves
    },
}

with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "best_of_n.csv"), "w", encoding="utf-8") as f:
    f.write("sigma,N,expected_true_quality,prob_select_true_best,reward_overestimate\n")
    for r in rows:
        f.write(f"{r['sigma']:g},{r['N']},{r['expected_true_quality']:.6f},"
                f"{r['prob_select_true_best']:.6f},{r['reward_overestimate']:.6f}\n")

fig, axes = plt.subplots(1, 2, figsize=(10.2, 4.2))
colors = plt.cm.viridis(np.linspace(0.05, 0.9, len(SIGMAS)))
for color, sigma in zip(colors, SIGMAS):
    c = curves[f"{sigma:g}"]
    axes[0].plot(N_LIST, [x["expected_true_quality"] for x in c], marker="o",
                 color=color, label=fr"$\sigma={sigma:g}$")
    axes[1].plot(N_LIST, [x["prob_select_true_best"] for x in c], marker="o",
                 color=color, label=fr"$\sigma={sigma:g}$")
axes[0].set_xscale("log", base=2)
axes[0].set_xlabel("N (candidates per prompt)")
axes[0].set_ylabel("expected true quality of selected")
axes[0].set_title("Best-of-N: gain saturates with reward noise")
axes[0].grid(alpha=0.3)
axes[0].legend(fontsize=8)
axes[1].set_xscale("log", base=2)
axes[1].set_xlabel("N (candidates per prompt)")
axes[1].set_ylabel("P(selected is truly best)")
axes[1].set_title("Probability of picking the true best")
axes[1].grid(alpha=0.3)
axes[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "best_of_n.png"), dpi=150)
plt.close(fig)

print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
