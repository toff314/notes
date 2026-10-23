#!/usr/bin/env python3
"""Lab-02: DPO 的 beta 曲线（三部分）。

A. 固定一组玩具 log-prob，扫描 beta，画 DPO 损失、隐式奖励差、有效梯度。
B. 按式 8.7 的 KL 约束目标求闭式最优策略（两个候选、固定真实奖励），
   看 beta 如何决定"离参考策略多远"，以及最优点的 DPO 损失为何不随 beta 变。
C. 反过来只用 DPO 损失做梯度下降（单个偏好对），看 beta 是"KL 预算"还是"优化步长"。
"""
import json
import os

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def log_softmax(z):
    z = z - np.max(z)
    return z - np.log(np.sum(np.exp(z)))


def softmax(z):
    return np.exp(log_softmax(z))


# ---------- A. 固定 margin 的 beta 曲线 ----------
LOG_PI_W, LOG_PI_L = -1.2, -1.5
LOG_REF_W, LOG_REF_L = -2.0, -1.9
MARGIN = (LOG_PI_W - LOG_REF_W) - (LOG_PI_L - LOG_REF_L)  # 0.4

betas = np.logspace(-3, 1, 400)
loss_curve = -np.log(sigmoid(betas * MARGIN))
implied_gap = betas * MARGIN
effective_grad = betas * sigmoid(-betas * MARGIN)
peak = int(np.argmax(effective_grad))

# ---------- B. KL 约束目标的闭式最优策略 ----------
REF = np.array([0.5, 0.0])          # 参考 logits
R_TRUE = np.array([1.0, 0.0])       # 真实奖励：胜者高 1
beta_opt = np.array([0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0])


def optimal_policy(beta):
    logits = np.log(softmax(REF)) + R_TRUE / beta
    return softmax(logits)


def kl(p, q):
    return float(np.sum(p * np.log(p / q)))


p_ref = softmax(REF)
opt_rows = []
for b in beta_opt:
    p = optimal_policy(b)
    implicit_gap = b * ((np.log(p[0]) - np.log(p_ref[0])) - (np.log(p[1]) - np.log(p_ref[1])))
    dpo_at_opt = -np.log(sigmoid(implicit_gap))
    opt_rows.append({
        "beta": float(b),
        "p_winner": float(p[0]),
        "p_loser": float(p[1]),
        "kl_to_ref": kl(p, p_ref),
        "implicit_reward_gap": float(implicit_gap),
        "dpo_loss_at_optimum": float(dpo_at_opt),
    })

# ---------- C. 直接优化 DPO 损失：beta 是预算还是步长？ ----------
REF4 = np.array([1.0, 0.5, 0.0, -0.5])
WIN, LOSE = 0, 1


def dpo_loss(z, beta):
    lp, lr = log_softmax(z), log_softmax(REF4)
    delta = (lp[WIN] - lr[WIN]) - (lp[LOSE] - lr[LOSE])
    return float(-np.log(sigmoid(beta * delta)))


def kl4(z):
    return kl(softmax(z), softmax(REF4))


def grad_numeric(z, beta, eps=1e-4):
    g = np.zeros_like(z)
    for i in range(len(z)):
        zp, zm = z.copy(), z.copy()
        zp[i] += eps
        zm[i] -= eps
        g[i] = (dpo_loss(zp, beta) - dpo_loss(zm, beta)) / (2 * eps)
    return g


def run_dpo(beta, steps):
    z = REF4.copy()
    m = np.zeros_like(z)
    v = np.zeros_like(z)
    traj = []
    for t in range(1, steps + 1):
        g = grad_numeric(z, beta)
        m = 0.9 * m + 0.1 * g
        v = 0.999 * v + 0.001 * g * g
        mh = m / (1 - 0.9 ** t)
        vh = v / (1 - 0.999 ** t)
        z -= 0.05 * mh / (np.sqrt(vh) + 1e-8)
        if t % 25 == 0:
            traj.append((t, float(softmax(z)[WIN]), kl4(z), dpo_loss(z, beta)))
    p = softmax(z)
    return {
        "p_winner": float(p[WIN]),
        "p_loser": float(p[LOSE]),
        "kl_to_ref": kl4(z),
        "final_loss": dpo_loss(z, beta),
    }, traj


beta_gd = [0.01, 0.1, 1.0]
gd_short, gd_long = {}, {}
trajectories = {}
for b in beta_gd:
    gd_short[f"{b:g}"], _ = run_dpo(b, 600)
    gd_long[f"{b:g}"], trajectories[f"{b:g}"] = run_dpo(b, 6000)

report = {
    "A_fixed_margin": {
        "log_ratio_margin": MARGIN,
        "beta_0.01": {
            "dpo_loss": float(-np.log(sigmoid(0.01 * MARGIN))),
            "implicit_reward_gap": float(0.01 * MARGIN),
            "effective_gradient": float(0.01 * sigmoid(-0.01 * MARGIN)),
        },
        "beta_0.1": {
            "dpo_loss": float(-np.log(sigmoid(0.1 * MARGIN))),
            "implicit_reward_gap": float(0.1 * MARGIN),
            "effective_gradient": float(0.1 * sigmoid(-0.1 * MARGIN)),
        },
        "effective_gradient_peak": {"beta": float(betas[peak]), "value": float(effective_grad[peak])},
    },
    "B_kl_regularized_optimum": opt_rows,
    "C_dpo_gradient_descent": {"600_steps": gd_short, "6000_steps": gd_long},
}

with open(os.path.join(OUT, "metrics.json"), "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "beta_curve.csv"), "w", encoding="utf-8") as f:
    f.write("beta,dpo_loss,implied_reward_gap,effective_grad\n")
    for row in zip(betas, loss_curve, implied_gap, effective_grad):
        f.write(f"{row[0]:.6f},{row[1]:.8f},{row[2]:.8f},{row[3]:.8f}\n")

with open(os.path.join(OUT, "beta_optimum.csv"), "w", encoding="utf-8") as f:
    f.write("beta,p_winner,kl_to_ref,implicit_reward_gap,dpo_loss_at_optimum\n")
    for r in opt_rows:
        f.write(f"{r['beta']:.4f},{r['p_winner']:.6f},{r['kl_to_ref']:.6f},"
                f"{r['implicit_reward_gap']:.6f},{r['dpo_loss_at_optimum']:.6f}\n")

# ---------- 图 1：固定 margin 的 beta 曲线 ----------
fig, ax1 = plt.subplots(figsize=(7.2, 4.4))
ax1.semilogx(betas, loss_curve, color="tab:blue", lw=2, label="DPO loss")
ax1.set_xlabel(r"$\beta$")
ax1.set_ylabel("DPO loss", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.grid(alpha=0.3, which="both")
ax2 = ax1.twinx()
ax2.semilogx(betas, effective_grad, color="tab:red", lw=2, ls="--", label="effective gradient")
ax2.set_ylabel(r"$\beta\,\sigma(-\beta m)$  (effective grad)", color="tab:red")
ax2.tick_params(axis="y", labelcolor="tab:red")
ax1.axvspan(0.01, 0.1, color="green", alpha=0.10)
ax1.set_title(r"Fixed margin $m=0.4$: loss falls, learning signal peaks at $\beta\approx3.2$")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "beta_curve.png"), dpi=150)
plt.close(fig)

# ---------- 图 2：KL 约束最优策略随 beta 变化 ----------
fig, ax1 = plt.subplots(figsize=(7.2, 4.4))
ax1.semilogx(beta_opt, [r["p_winner"] for r in opt_rows], marker="o", color="tab:blue")
ax1.set_xlabel(r"$\beta$")
ax1.set_ylabel("optimal $p(winner)$", color="tab:blue")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.grid(alpha=0.3, which="both")
ax2 = ax1.twinx()
ax2.semilogx(beta_opt, [r["kl_to_ref"] for r in opt_rows], marker="s", ls="--", color="tab:purple")
ax2.set_ylabel(r"$D_{KL}(\pi^*\,\|\,\pi_{ref})$", color="tab:purple")
ax2.tick_params(axis="y", labelcolor="tab:purple")
ax1.set_title(r"Closed-form optimum of Eq. 8.7 with true reward gap 1")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "kl_optimum.png"), dpi=150)
plt.close(fig)

# ---------- 图 3：直接优化 DPO，KL 轨迹 ----------
fig, ax = plt.subplots(figsize=(7.2, 4.4))
for b in beta_gd:
    traj = trajectories[f"{b:g}"]
    ax.plot([t for t, *_ in traj], [k for _, _, k, _ in traj], label=fr"$\beta={b:g}$", lw=2)
ax.set_xscale("log")
ax.set_xlabel("gradient step")
ax.set_ylabel(r"$D_{KL}(\pi_\theta\,\|\,\pi_{ref})$")
ax.set_title("DPO on one separable pair: beta changes the speed, not the endpoint")
ax.grid(alpha=0.3, which="both")
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(OUT, "kl_trajectory.png"), dpi=150)
plt.close(fig)

print(json.dumps(report, ensure_ascii=False, indent=2))
