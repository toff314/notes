#!/usr/bin/env python3
"""lab-02 从零实现 BPTT：解析梯度 vs 有限差分，并用教师强制 / 自由运行对照训练字符级 RNN 语言模型。

对应 actions.md 第 2 条；对应书中 §14.1.2（BPTT）、§14.2.2（自监督 + 教师强制）。
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

# 手写小语料：8 句同构句 × 4，字符级；句式重复，便于小模型学到结构
SENTS = [
    "the flights the airline was canceling were full .",
    "the flights the airline was canceling were late .",
    "the flights the airline was canceling were full again .",
    "the flights the airline was delaying were full .",
    "the trains the company was canceling were late .",
    "the trains the company was delaying were full .",
    "the buses the city was canceling were late .",
    "the buses the city was delaying were full .",
]
TEXT = " ".join(SENTS * 4)
VOCAB = sorted(set(TEXT))
stoi = {c: i for i, c in enumerate(VOCAB)}
V = len(VOCAB)
DATA = np.array([stoi[c] for c in TEXT])


def softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


class CharRNN:
    """h_t = tanh(U h_{t-1} + W e_t + b), y_t = softmax(V h_t + c)"""

    def __init__(self, d_h=24, d_e=16, seed=0):
        rng = np.random.default_rng(seed)
        self.d_h, self.d_e, self.V = d_h, d_e, V
        self.E = rng.normal(0, 0.3, (d_e, V))
        self.W = rng.normal(0, 0.3, (d_h, d_e))
        self.U = rng.normal(0, 0.3, (d_h, d_h))
        self.Vm = rng.normal(0, 0.3, (V, d_h))
        self.b = np.zeros(d_h)
        self.c = np.zeros(V)
        self.params = ["E", "W", "U", "Vm", "b", "c"]

    def forward(self, xs, h_prev=None):
        h = np.zeros(self.d_h) if h_prev is None else h_prev
        cache = []
        for x in xs:
            e = self.E[:, x]
            a = self.U @ h + self.W @ e + self.b
            h_new = np.tanh(a)
            z = self.Vm @ h_new + self.c
            p = softmax(z)
            cache.append((x, h, e, h_new, p))
            h = h_new
        return h, cache

    def loss_and_grads(self, xs, ys, h_prev=None):
        h, cache = self.forward(xs, h_prev)
        loss = 0.0
        for (x, h_old, e, h_new, p), y in zip(cache, ys):
            loss -= np.log(max(p[y], 1e-12))
        grads = {k: np.zeros_like(getattr(self, k)) for k in self.params}
        dh_next = np.zeros(self.d_h)
        for (x, h_old, e, h_new, p), y in reversed(list(zip(cache, ys))):
            dz = p.copy()
            dz[y] -= 1.0
            grads["Vm"] += np.outer(dz, h_new)
            grads["c"] += dz
            dh = self.Vm.T @ dz + dh_next
            da = dh * (1 - h_new ** 2)
            grads["U"] += np.outer(da, h_old)
            grads["W"] += np.outer(da, e)
            grads["b"] += da
            grads["E"][:, x] += self.W.T @ da
            dh_next = self.U.T @ da
        for k in grads:
            grads[k] /= len(xs)  # 与 loss 的平均口径保持一致
        return loss / len(xs), grads

    def step(self, grads, lr, clip=1.0):
        for k in self.params:
            g = np.clip(grads[k], -clip, clip)
            getattr(self, k)[...] -= lr * g


def batches(data, bptt=20):
    for i in range(0, len(data) - bptt - 1, bptt):
        yield data[i:i + bptt], data[i + 1:i + bptt + 1]


# ---------- 1) 解析梯度 vs 有限差分（小模型，seq len 4） ----------
small = CharRNN(d_h=3, d_e=4, seed=3)
xs = DATA[:4]
ys = DATA[1:5]
loss0, g = small.loss_and_grads(xs, ys)

eps = 1e-5
max_abs, max_rel, checked, big = 0.0, 0.0, 0, 0
rng = np.random.default_rng(0)
for k in small.params:
    arr = getattr(small, k)
    idxs = [tuple(int(rng.integers(0, s)) for s in arr.shape) for _ in range(6)]
    for idx in idxs:
        old = arr[idx]
        arr[idx] = old + eps
        lp, _ = small.loss_and_grads(xs, ys)
        arr[idx] = old - eps
        lm, _ = small.loss_and_grads(xs, ys)
        arr[idx] = old
        num = (lp - lm) / (2 * eps)
        ana = g[k][idx]
        max_abs = max(max_abs, abs(num - ana))
        if abs(ana) > 1e-3:
            big += 1
            max_rel = max(max_rel, abs(num - ana) / abs(ana))
        checked += 1

# 时间步 t=1 的误差项随回溯距离的范数（U^T 连乘）
norms = []
d = np.ones((small.d_h, 1))
for _ in range(10):
    norms.append(float(np.linalg.norm(d)))
    d = small.U.T @ d

# ---------- 2) 训练 ----------
model = CharRNN(d_h=24, d_e=16, seed=1)
LR, EPOCHS = 0.1, 120
hist = []
for ep in range(EPOCHS):
    tot, n = 0.0, 0
    for xb, yb in batches(DATA, 20):
        loss, grads = model.loss_and_grads(xb, yb)
        model.step(grads, LR)
        tot += loss * len(xb)
        n += len(xb)
    hist.append((ep + 1, tot / n))
train_loss = hist[-1][1]
train_ppl = float(np.exp(train_loss))


def eval_teacher(seq):
    tot, n = 0.0, 0
    h = None
    for x, y in zip(seq[:-1], seq[1:]):
        h, cache = model.forward([x], h)
        p = cache[-1][4]
        tot -= np.log(max(p[y], 1e-12))
        n += 1
    return tot / n


def eval_free(seq, prime=8):
    h = None
    for x in seq[:prime]:
        h, cache = model.forward([x], h)
    tot, n = 0.0, 0
    prev = seq[prime - 1]
    for y in seq[prime:]:
        h, cache = model.forward([prev], h)
        p = cache[-1][4]
        tot -= np.log(max(p[y], 1e-12))
        n += 1
        prev = int(np.argmax(p))
    return tot / n


t_loss = float(eval_teacher(list(DATA)))
f_loss = float(np.mean([eval_free(list(DATA[i:i + 60])) for i in range(0, 400, 60)]))
t_ppl, f_ppl = float(np.exp(t_loss)), float(np.exp(f_loss))

with open(os.path.join(OUT, "loss_curve.csv"), "w") as f:
    f.write("epoch,train_loss\n")
    for ep, l in hist:
        f.write(f"{ep},{l:.6f}\n")

with open(os.path.join(OUT, "grad_check.json"), "w") as f:
    json.dump({
        "loss": loss0,
        "checked_entries": checked,
        "entries_with_abs_grad_gt_1e-3": big,
        "max_abs_error": max_abs,
        "max_relative_error_on_nontrivial": max_rel,
        "hidden_error_norm_by_backtrack_step": norms,
    }, f, ensure_ascii=False, indent=2)

with open(os.path.join(OUT, "teacher_forcing.json"), "w") as f:
    json.dump({
        "teacher_forced_loss": t_loss, "teacher_forced_ppl": t_ppl,
        "free_running_loss": f_loss, "free_running_ppl": f_ppl,
        "vocab_size": V, "d_h": model.d_h, "d_e": model.d_e,
        "n_params": int(V * model.d_e + model.d_e * model.d_h + model.d_h * model.d_h + V * model.d_h + model.d_h + V),
        "first_epoch_loss": hist[0][1], "final_epoch_loss": train_loss,
    }, f, ensure_ascii=False, indent=2)

fig, ax = plt.subplots(figsize=(5.2, 3.2))
ax.plot([e for e, _ in hist], [l for _, l in hist])
ax.set_xlabel("epoch")
ax.set_ylabel("mean cross-entropy (nats/char)")
ax.set_title("char-level RNN LM training")
fig.tight_layout()
fig.savefig(os.path.join(OUT, "loss_curve.png"), dpi=120)

print(f"vocab={V} d_h={model.d_h} d_e={model.d_e} chars={len(DATA)}")
print(f"grad check: entries={checked} nontrivial={big} max_abs={max_abs:.3e} max_rel={max_rel:.3e} (loss={loss0:.6f})")
print("error norm by backtrack:", " ".join(f"{v:.4f}" for v in norms))
print(f"train loss={train_loss:.4f} ppl={train_ppl:.3f} (epoch1 {hist[0][1]:.4f})")
print(f"teacher forcing: loss={t_loss:.4f} ppl={t_ppl:.3f}")
print(f"free running   : loss={f_loss:.4f} ppl={f_ppl:.3f}")
