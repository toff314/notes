#!/usr/bin/env python3
"""Lab-01: 用 Bradley-Terry 成对损失训练奖励模型（numpy 从零实现）。

实验一（干净特征）：候选输出由 4 个有效特征描述，真实效用为线性函数；
偏好标签按 BT 概率采样。训练 r(f)=theta·f，看能否恢复真实权重、测试准确率多少。

实验二（捷径特征）：训练集里"胜者"系统性地更长（第 5 维 +1，败者 -1），
但真实效用与长度无关。测试集把该相关性反转，观察奖励模型的准确率崩塌。
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 8
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(SEED)

D = 6
TRUE_W = np.array([1.0, 0.75, 0.45, -0.25, 0.0, 0.0])


def sample_candidates(n):
    return rng.normal(size=(n, D))


def label_pairs(fa, fb):
    """按 BT(true) 采样偏好；返回 (winner, loser) 特征矩阵。"""
    delta = (fa - fb) @ TRUE_W
    p = 1.0 / (1.0 + np.exp(-delta))
    win_is_a = rng.random(len(p)) < p
    fw = np.where(win_is_a[:, None], fa, fb)
    fl = np.where(win_is_a[:, None], fb, fa)
    return fw, fl


def make_pairs(n, shortcut=None):
    fa, fb = sample_candidates(n), sample_candidates(n)
    fw, fl = label_pairs(fa, fb)
    if shortcut == "aligned":
        fw = fw.copy()
        fl = fl.copy()
        fw[:, 4] = 1.0 + 0.5 * rng.normal(size=n)
        fl[:, 4] = -1.0 + 0.5 * rng.normal(size=n)
    elif shortcut == "reversed":
        fw = fw.copy()
        fl = fl.copy()
        fw[:, 4] = -1.0 + 0.5 * rng.normal(size=n)
        fl[:, 4] = 1.0 + 0.5 * rng.normal(size=n)
    elif shortcut == "none":
        fw = fw.copy()
        fl = fl.copy()
        fw[:, 4] = 0.5 * rng.normal(size=n)
        fl[:, 4] = 0.5 * rng.normal(size=n)
    return fw, fl


def fit_bt(fw, fl, steps=4000, lr=0.15):
    """全批量梯度下降最小化 -log sigmoid(theta·(fw-fl))。"""
    diff = fw - fl
    theta = np.zeros(D)
    hist = []
    for _ in range(steps):
        s = diff @ theta
        p = 1.0 / (1.0 + np.exp(-s))
        loss = -np.mean(np.log(np.maximum(p, 1e-12)))
        grad = -np.mean((1.0 - p)[:, None] * diff, axis=0)
        theta -= lr * grad
        hist.append(float(loss))
    return theta, np.array(hist)


def accuracy(theta, fw, fl):
    return float(np.mean((fw - fl) @ theta > 0))


report = {}

# ---------- 实验一：干净特征 ----------
fw_tr, fl_tr = make_pairs(2000)
fw_te, fl_te = make_pairs(2000)
theta_clean, hist_clean = fit_bt(fw_tr, fl_tr)
report["clean"] = {
    "train_accuracy": accuracy(theta_clean, fw_tr, fl_tr),
    "test_accuracy": accuracy(theta_clean, fw_te, fl_te),
    "theta": [round(float(x), 4) for x in theta_clean],
    "true_w": [round(float(x), 4) for x in TRUE_W],
    "cosine_similarity_all_dims": float(
        np.dot(theta_clean, TRUE_W) / (np.linalg.norm(theta_clean) * np.linalg.norm(TRUE_W))
    ),
    "final_loss": float(hist_clean[-1]),
    "initial_loss": float(hist_clean[0]),
    "bayes_accuracy_estimate": float(np.mean(1.0 / (1.0 + np.exp(-np.abs((fw_te - fl_te) @ TRUE_W))))),
}

# ---------- 实验二：捷径特征 ----------
fw_sp, fl_sp = make_pairs(2000, shortcut="aligned")
fw_sp_te, fl_sp_te = make_pairs(2000, shortcut="aligned")
fw_rev, fl_rev = make_pairs(2000, shortcut="reversed")
fw_none, fl_none = make_pairs(2000, shortcut="none")
theta_sp, hist_sp = fit_bt(fw_sp, fl_sp)
report["shortcut"] = {
    "train_accuracy": accuracy(theta_sp, fw_sp, fl_sp),
    "test_accuracy_same_distribution": accuracy(theta_sp, fw_sp_te, fl_sp_te),
    "test_accuracy_reversed_shortcut": accuracy(theta_sp, fw_rev, fl_rev),
    "test_accuracy_shortcut_removed": accuracy(theta_sp, fw_none, fl_none),
    "theta": [round(float(x), 4) for x in theta_sp],
    "learned_shortcut_weight": round(float(theta_sp[4]), 4),
    "final_loss": float(hist_sp[-1]),
}

# ---------- 产物 ----------
with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "loss_history.csv"), "w", encoding="utf-8") as f:
    f.write("step,clean_loss,shortcut_loss\n")
    for i, (a, b) in enumerate(zip(hist_clean, hist_sp)):
        if i % 20 == 0:
            f.write(f"{i},{a:.8f},{b:.8f}\n")

fig, ax = plt.subplots(figsize=(6.4, 4.2))
ax.plot(hist_clean, label="clean features", lw=2)
ax.plot(hist_sp, label="with shortcut feature", lw=2, ls="--")
ax.set_xlabel("gradient step")
ax.set_ylabel(r"$-\log\sigma(r(o_w)-r(o_l))$")
ax.set_title("Bradley-Terry pairwise loss")
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "loss_curve.png"), dpi=150)
plt.close(fig)

fig, ax = plt.subplots(figsize=(7.0, 4.2))
idx = np.arange(D)
ax.bar(idx - 0.2, TRUE_W, width=0.4, label="true weights")
ax.bar(idx + 0.2, theta_clean, width=0.4, label="learned (clean)")
ax.bar(idx + 0.2, theta_sp, width=0.22, label="learned (shortcut)", color="tab:red", alpha=0.75)
ax.set_xticks(idx)
ax.set_xticklabels([f"f{i}" for i in range(D)])
ax.axvspan(3.5, 5.5, color="grey", alpha=0.08)
ax.set_ylabel("weight")
ax.set_title("Weight recovery: f4 is the spurious length cue")
ax.grid(axis="y", alpha=0.3)
ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "weight_recovery.png"), dpi=150)
plt.close(fig)

print(json.dumps(report, ensure_ascii=False, indent=2))
