#!/usr/bin/env python3
"""lab-01 简单循环网络的前向推断：形状核对、参数共享、上下文影响随距离的衰减。

对应 actions.md 第 1 条；对应书中 §14.1、§14.1.1（h_t = g(U h_{t-1} + W x_t)，y_t = softmax(V h_t)）。
只用 numpy + matplotlib，离线可跑。
"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

D_IN, D_H, D_OUT, T = 6, 4, 5, 6
rng = np.random.default_rng(14)
W = rng.normal(0.0, 0.6, (D_H, D_IN))   # 输入 -> 隐藏
U = rng.normal(0.0, 0.55, (D_H, D_H))   # 上一隐藏 -> 当前隐藏
V = rng.normal(0.0, 0.6, (D_OUT, D_H))  # 隐藏 -> 输出
h0 = np.zeros(D_H)


def softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


def forward(X, h_init=None):
    """X: [T, D_IN] -> hs [T, D_H], ys [T, D_OUT]"""
    h = np.zeros(D_H) if h_init is None else h_init.copy()
    hs, ys = [], []
    for t in range(len(X)):
        h = np.tanh(U @ h + W @ X[t])
        y = softmax(V @ h)
        hs.append(h.copy())
        ys.append(y.copy())
    return np.array(hs), np.array(ys)


X = rng.normal(0.0, 1.0, (T, D_IN))
hs, ys = forward(X)

# 1) 逐时间步手写循环 vs 上面的实现（同一份代码，但显式保存中间量）
h = h0.copy()
rows = []
for t in range(T):
    a = U @ h + W @ X[t]
    h_new = np.tanh(a)
    y = softmax(V @ h_new)
    rows.append((t + 1, *h_new.tolist(), *y.tolist()))
    h = h_new
loop_h = np.array([[r[1 + i] for i in range(D_H)] for r in rows])
shape_diff = float(np.abs(loop_h - hs).max())

# 2) 参数共享：参数量与序列长度无关
n_params = D_H * D_IN + D_H * D_H + D_OUT * D_H
params_long = n_params  # 换成 T=60 仍是同一组矩阵

# 3) 上下文影响：扰动 x_1，看每个后续时刻输出分布的变化
Xp = X.copy()
Xp[0, 0] += 0.5
_, ys_p = forward(Xp)
d_y = np.linalg.norm(ys_p - ys, axis=1)
hsp, _ = forward(Xp)
d_h = np.linalg.norm(hsp - hs, axis=1)

with open(os.path.join(OUT, "influence_decay.csv"), "w") as f:
    f.write("t,delta_h_norm,delta_y_norm\n")
    for t in range(T):
        f.write(f"{t+1},{d_h[t]:.6f},{d_y[t]:.6f}\n")

with open(os.path.join(OUT, "hidden_states.csv"), "w") as f:
    f.write("t," + ",".join(f"h{i+1}" for i in range(D_H)) + "\n")
    for t in range(T):
        f.write(f"{t+1}," + ",".join(f"{v:.6f}" for v in hs[t]) + "\n")

with open(os.path.join(OUT, "output_probs.csv"), "w") as f:
    f.write("t," + ",".join(f"y{i+1}" for i in range(D_OUT)) + "\n")
    for t in range(T):
        f.write(f"{t+1}," + ",".join(f"{v:.6f}" for v in ys[t]) + "\n")

summary = {
    "dims": {"d_in": D_IN, "d_h": D_H, "d_out": D_OUT, "T": T},
    "shapes": {"W": list(W.shape), "U": list(U.shape), "V": list(V.shape), "hs": list(hs.shape), "ys": list(ys.shape)},
    "params_total": int(n_params),
    "params_total_T60": int(params_long),
    "loop_vs_vectorized_max_abs_diff": shape_diff,
    "row_sums_max_dev": float(np.abs(ys.sum(axis=1) - 1).max()),
    "influence_delta_y": [round(float(v), 6) for v in d_y],
    "influence_ratio_last_over_first": float(d_y[-1] / d_y[0]),
    "h_abs_mean": float(np.abs(hs).mean()),
    "h_tanh_saturation_ratio": float((np.abs(hs) > 0.95).mean()),
}
with open(os.path.join(OUT, "summary.json"), "w") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
ax[0].plot(range(1, T + 1), d_h, "o-", label="‖Δh_t‖")
ax[0].plot(range(1, T + 1), d_y, "s--", label="‖Δy_t‖")
ax[0].set_xlabel("时间步 t")
ax[0].set_ylabel("扰动范数")
ax[0].set_title("扰动 x_1 的传播")
ax[0].legend()
ax[1].plot(range(1, T + 1), d_y / d_y[0], "o-")
ax[1].set_yscale("log")
ax[1].set_xlabel("时间步 t")
ax[1].set_ylabel("‖Δy_t‖ / ‖Δy_1‖")
ax[1].set_title("相对影响（对数轴）")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "influence_decay.png"), dpi=120)

print(f"dims d_in={D_IN} d_h={D_H} d_out={D_OUT} T={T}")
print(f"shapes W{W.shape} U{U.shape} V{V.shape} hs{hs.shape} ys{ys.shape}")
print(f"params_total={n_params} (T=6 与 T=60 相同)")
print(f"loop_vs_vectorized_max_abs_diff={shape_diff:.3e}")
print(f"row_sums_max_dev={summary['row_sums_max_dev']:.3e}")
print("delta_y per step:", " ".join(f"{v:.5f}" for v in d_y))
print(f"delta_y ratio last/first={summary['influence_ratio_last_over_first']:.4f}")
print(f"mean|h|={summary['h_abs_mean']:.4f} tanh saturation ratio={summary['h_tanh_saturation_ratio']:.3f}")
