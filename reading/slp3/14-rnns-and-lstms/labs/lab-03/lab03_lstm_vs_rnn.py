#!/usr/bin/env python3
"""lab-03 长距离依赖：简单 RNN vs LSTM（自己写的小型自动微分引擎 + 标记-回忆任务）。

对应 actions.md 第 3 条；对应书中 §14.5（门控单元、误差反复相乘导致梯度消失）。

任务（delayed recall with marker）：
    序列 = [标记] [目标符号] [干扰符号 × (L-2)]，在最后一步输出目标符号。
    标记每次相同，所以「记住标记后面那个符号」是一个纯记忆任务，与输入分布无关。
指标：不同延迟 L 下的准确率；训练后损失对第 0 步隐状态的梯度范数（梯度流）。

用法：python3 lab03_lstm_vs_rnn.py            # 完整跑
     python3 lab03_lstm_vs_rnn.py --probe 40 300  # 只训 LSTM、lag=40，看是否学得会
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

K = 4            # 目标/干扰符号数
MARK = K         # 标记符号的 one-hot 下标
D_IN = K + 1
D_H = 32


# ---------------- 迷你自动微分（只支持本实验用到的算子） ----------------
class T:
    __slots__ = ("data", "grad", "_p", "_b")

    def __init__(self, data, _p=(), _b=None):
        self.data = np.asarray(data, dtype=np.float64)
        self.grad = np.zeros_like(self.data)
        self._p = _p
        self._b = _b if _b is not None else (lambda: None)


def _unbroadcast(g, shape):
    while g.ndim > len(shape):
        g = g.sum(axis=0)
    for i, s in enumerate(shape):
        if s == 1 and g.shape[i] != 1:
            g = g.sum(axis=i, keepdims=True)
    return g


def matmul(a, b):
    a = a if isinstance(a, T) else T(a)
    b = b if isinstance(b, T) else T(b)
    A, B = a.data, b.data
    out = T(A @ B, (a, b))

    def bwd():
        g = out.grad
        if A.ndim == 2 and B.ndim == 1:
            a.grad += np.outer(g, B)
            b.grad += A.T @ g
        elif A.ndim == 1 and B.ndim == 2:
            a.grad += B @ g
            b.grad += np.outer(A, g)
        else:
            a.grad += g @ B.T
            b.grad += A.T @ g
    out._b = bwd
    return out


def add(a, b):
    a = a if isinstance(a, T) else T(a)
    b = b if isinstance(b, T) else T(b)
    out = T(a.data + b.data, (a, b))

    def bwd():
        a.grad += _unbroadcast(out.grad, a.data.shape)
        b.grad += _unbroadcast(out.grad, b.data.shape)
    out._b = bwd
    return out


def mul(a, b):
    a = a if isinstance(a, T) else T(a)
    b = b if isinstance(b, T) else T(b)
    out = T(a.data * b.data, (a, b))

    def bwd():
        a.grad += _unbroadcast(out.grad * b.data, a.data.shape)
        b.grad += _unbroadcast(out.grad * a.data, b.data.shape)
    out._b = bwd
    return out


def tanh(a):
    out = T(np.tanh(a.data), (a,))

    def bwd():
        a.grad += out.grad * (1.0 - out.data ** 2)
    out._b = bwd
    return out


def sigmoid(a):
    out = T(1.0 / (1.0 + np.exp(-a.data)), (a,))

    def bwd():
        a.grad += out.grad * out.data * (1.0 - out.data)
    out._b = bwd
    return out


def softmax_ce(logits, y):
    z = logits.data - logits.data.max()
    p = np.exp(z) / np.exp(z).sum()
    out = T(-np.log(max(p[y], 1e-12)), (logits,))

    def bwd():
        d = p.copy()
        d[y] -= 1.0
        logits.grad += d
    out._b = bwd
    return out


def backward(out):
    topo, seen = [], set()

    def visit(n):
        if id(n) in seen:
            return
        seen.add(id(n))
        for p in n._p:
            visit(p)
        topo.append(n)

    visit(out)
    out.grad = np.ones_like(out.data)
    for n in reversed(topo):
        n._b()


class Adam:
    def __init__(self, params, lr=0.02):
        self.p, self.lr, self.t = params, lr, 0
        self.m = {k: np.zeros_like(v.data) for k, v in params.items()}
        self.v = {k: np.zeros_like(v.data) for k, v in params.items()}

    def step(self, clip=5.0):
        self.t += 1
        for k, p in self.p.items():
            g = np.clip(p.grad, -clip, clip)
            self.m[k] = 0.9 * self.m[k] + 0.1 * g
            self.v[k] = 0.999 * self.v[k] + 0.001 * g * g
            mh = self.m[k] / (1 - 0.9 ** self.t)
            vh = self.v[k] / (1 - 0.999 ** self.t)
            p.data -= self.lr * mh / (np.sqrt(vh) + 1e-8)
            p.grad = np.zeros_like(p.data)


# ---------------- 两个模型 ----------------
class SimpleRNN:
    name = "RNN"

    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        self.p = {
            "W": T(rng.normal(0, 0.3, (D_H, D_IN))), "U": T(rng.normal(0, 0.1, (D_H, D_H))),
            "b": T(np.zeros(D_H)), "Vo": T(rng.normal(0, 0.3, (K, D_H))), "c": T(np.zeros(K)),
        }

    def forward(self, xs):
        h = T(np.zeros(D_H))
        hs = [h]
        for x in xs:
            onehot = np.eye(D_IN)[x]
            a = add(add(matmul(self.p["U"], h), matmul(self.p["W"], onehot)), self.p["b"])
            h = tanh(a)
            hs.append(h)
        y = add(matmul(self.p["Vo"], h), self.p["c"])
        return y, hs


class LSTMCell:
    name = "LSTM"

    def __init__(self, seed):
        rng = np.random.default_rng(seed)
        p = {}
        for g in "fiog":
            p["W" + g] = T(rng.normal(0, 0.3, (D_H, D_IN)))
            p["U" + g] = T(rng.normal(0, 0.1, (D_H, D_H)))
            p["b" + g] = T(np.zeros(D_H))
        p["bf"].data += 1.0  # 遗忘门偏置初始化为 1，默认「记住」
        p["Vo"] = T(rng.normal(0, 0.3, (K, D_H)))
        p["c"] = T(np.zeros(K))
        self.p = p

    def _gate(self, g, h, x, act):
        z = add(add(matmul(self.p["U" + g], h), matmul(self.p["W" + g], x)), self.p["b" + g])
        return act(z)

    def forward(self, xs):
        h = T(np.zeros(D_H))
        c = T(np.zeros(D_H))
        hs = [h]
        for x in xs:
            onehot = np.eye(D_IN)[x]
            f = self._gate("f", h, onehot, sigmoid)
            i = self._gate("i", h, onehot, sigmoid)
            o = self._gate("o", h, onehot, sigmoid)
            g = self._gate("g", h, onehot, tanh)
            c = add(mul(f, c), mul(i, g))
            h = mul(o, tanh(c))
            hs.append(h)
        y = add(matmul(self.p["Vo"], h), self.p["c"])
        return y, hs


def make_batch(rng, lag, n):
    """[标记][目标][干扰 × (lag-2)]，返回 (序列, 目标)。"""
    data = []
    for _ in range(n):
        target = int(rng.integers(0, K))
        seq = [MARK, target] + [int(rng.integers(0, K)) for _ in range(lag - 2)]
        data.append((seq, target))
    return data


def train(model_cls, lag, seed, steps=300, batch=8, lr=0.03, clip=5.0):
    model = model_cls(seed)
    opt = Adam(model.p, lr=lr)
    rng = np.random.default_rng(1000 + seed)
    curve = []
    for s in range(steps):
        b = make_batch(rng, lag, batch)
        total = 0.0
        for seq, target in b:
            y, _ = model.forward(seq)
            loss = softmax_ce(y, target)
            backward(loss)
            total += loss.data
        opt.step(clip=clip)
        if (s + 1) % 30 == 0:
            curve.append((s + 1, total / batch))
    return model, curve


def accuracy(model, lag, seed=999, n=64):
    rng = np.random.default_rng(seed)
    ok = 0
    for seq, target in make_batch(rng, lag, n):
        y, _ = model.forward(seq)
        ok += int(np.argmax(y.data) == target)
    return ok / n


def grad_profile(model, lag, seed=7):
    rng = np.random.default_rng(seed)
    seq, target = make_batch(rng, lag, 1)[0]
    y, hs = model.forward(seq)
    loss = softmax_ce(y, target)
    backward(loss)
    return [float(np.linalg.norm(h.grad)) for h in hs]


def gradcheck(n_samples=4):
    """对两个模型各取若干参数元素，做中心差分核对（自动微分 vs 数值梯度）。"""
    out = {}
    seq, target = [MARK, 2, 1, 3, 0], 2
    rng = np.random.default_rng(0)
    for cls in (SimpleRNN, LSTMCell):
        m = cls(5)
        y, _ = m.forward(seq)
        loss = softmax_ce(y, target)
        backward(loss)
        eps, worst = 1e-6, 0.0
        for k, node in m.p.items():
            for _ in range(n_samples):
                idx = tuple(int(rng.integers(0, s)) for s in node.data.shape)
                old = node.data[idx]
                node.data[idx] = old + eps
                yp, _ = m.forward(seq)
                lp = softmax_ce(yp, target).data
                node.data[idx] = old - eps
                ym, _ = m.forward(seq)
                lm = softmax_ce(ym, target).data
                node.data[idx] = old
                num = (lp - lm) / (2 * eps)
                ana = node.grad[idx]
                worst = max(worst, abs(num - ana) / max(1e-12, abs(num) + abs(ana)))
        out[cls.name] = worst
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", nargs=2, type=int, default=None)
    ap.add_argument("--gradcheck", action="store_true")
    ap.add_argument("--steps", type=int, default=800)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2])
    ap.add_argument("--lags", type=int, nargs="+", default=[4, 8, 12, 20])
    args = ap.parse_args()

    if args.gradcheck:
        gc = gradcheck()
        print("gradcheck max rel err:", gc)
        with open(os.path.join(OUT, "grad_check.json"), "w") as f:
            json.dump(gc, f, indent=2)
        raise SystemExit(0)

    if args.probe:
        lag, steps = args.probe
        for cls in (SimpleRNN, LSTMCell):
            m, curve = train(cls, lag, 1, steps=steps)
            print(f"probe {cls.name} lag={lag} steps={steps} acc={accuracy(m, lag):.3f} "
                  f"loss={curve[-1][1]:.4f}")
        raise SystemExit(0)

    # 超参选择：在短延迟（lag=8）上为每个模型各选一个学习率，之后固定不变。
    LRS = [0.005, 0.01, 0.02]
    chosen = {}
    for cls in (SimpleRNN, LSTMCell):
        best_lr, best_acc = LRS[0], -1.0
        for lr in LRS:
            m, _ = train(cls, 8, 1, steps=300, lr=lr)
            a = accuracy(m, 8)
            print(f"select {cls.name:5s} lr={lr:<6} lag=8 acc={a:.3f}", flush=True)
            if a > best_acc:
                best_lr, best_acc = lr, a
        chosen[cls.name] = {"lr": best_lr, "lag8_acc": best_acc}
    print("chosen:", chosen, flush=True)

    rows, curves_long, profiles = [], [], {}
    for cls in (SimpleRNN, LSTMCell):
        for lag in args.lags:
            accs = []
            for sd in args.seeds:
                model, curve = train(cls, lag, sd, steps=args.steps, lr=chosen[cls.name]["lr"])
                accs.append(accuracy(model, lag))
                if lag == max(args.lags):
                    curves_long.append((cls.name, sd, curve))
                    profiles[cls.name] = grad_profile(model, lag)
            rows.append((cls.name, lag, float(np.mean(accs)), float(np.std(accs)), accs))
            print(f"{cls.name:5s} lag={lag:2d} acc={np.mean(accs):.3f} (seeds {accs})", flush=True)

    with open(os.path.join(OUT, "accuracy_by_lag.csv"), "w") as f:
        f.write("model,lag,acc_mean,acc_std,acc_seeds\n")
        for m, l, mu, sd, accs in rows:
            f.write(f"{m},{l},{mu:.4f},{sd:.4f},\"{'/'.join(f'{a:.3f}' for a in accs)}\"\n")

    with open(os.path.join(OUT, "grad_norm_by_step.csv"), "w") as f:
        f.write("model,step,grad_norm\n")
        for m, prof in profiles.items():
            for i, v in enumerate(prof):
                f.write(f"{m},{i},{v:.10e}\n")

    with open(os.path.join(OUT, "training_curve_longest.csv"), "w") as f:
        f.write("model,seed,step,loss\n")
        for m, sd, curve in curves_long:
            for s, l in curve:
                f.write(f"{m},{sd},{s},{l:.6f}\n")

    summary = {
        "task": "delayed recall with marker: [MARK][target][distractors x(lag-2)] -> predict target",
        "K": K, "d_h": D_H, "seeds": args.seeds, "steps": args.steps,
        "chosen_lr": chosen,
        "accuracy": {m: {l: mu for mm, l, mu, sd, a in rows if mm == m} for m in ("RNN", "LSTM")},
        "grad_norm_at_step0": {m: prof[0] for m, prof in profiles.items()},
        "grad_norm_at_last": {m: prof[-1] for m, prof in profiles.items()},
        "grad_norm_ratio_step0_over_last": {m: prof[0] / prof[-1] for m, prof in profiles.items()},
    }
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.6))
    for m in ("RNN", "LSTM"):
        sub = [(l, mu) for mm, l, mu, sd, a in rows if mm == m]
        ax[0].plot([s[0] for s in sub], [s[1] for s in sub], "o-", label=m)
    ax[0].set_xlabel("lag (steps)")
    ax[0].set_ylabel("accuracy")
    ax[0].set_ylim(0, 1.05)
    ax[0].axhline(1 / K, ls=":", c="gray", label="chance")
    ax[0].set_title("delayed recall accuracy")
    ax[0].legend()
    for m, prof in profiles.items():
        ax[1].plot(range(len(prof)), prof, "o-", ms=3, label=m)
    ax[1].set_yscale("log")
    ax[1].set_xlabel("backprop step (0 = first input)")
    ax[1].set_ylabel("||dL/dh_t||")
    ax[1].set_title("gradient flow at longest lag")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_rnn_vs_lstm.png"), dpi=120)

    print("grad norm at step0:", {m: f"{p[0]:.3e}" for m, p in profiles.items()})
    print("grad norm at last :", {m: f"{p[-1]:.3e}" for m, p in profiles.items()})
