#!/usr/bin/env python3
"""lab-05 编码器-解码器与点积注意力（§14.7、§14.8）。

任务：把输入符号序列倒序输出（长度 3–8 训练，评估时也测 10、12 的未见长度）。
对照：
  fixed —— 解码器每一步都吃同一个上下文向量（编码器最后隐状态），即 §14.7 的瓶颈；
  attn  —— 每一步用点积注意力从全部编码器隐状态里加权取上下文 c_t，即 §14.8。
指标：逐位完全正确率（exact match），按长度分桶；外加一张注意力权重热图。
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from minigrad import T, Adam, add, backward, div, exp, matmul, mul, softmax_ce, tanh

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

SYM = [1, 2, 3, 4, 5]
PAD, BOS, EOS = 0, 6, 7
N_IN = 8
D = 24
MAX_LEN = 10


def onehot(i):
    v = np.zeros(N_IN)
    v[i] = 1.0
    return v


def dot(a, b):
    out = T(float(a.data @ b.data), (a, b))

    def bwd():
        a.grad += out.grad * b.data
        b.grad += out.grad * a.data
    out._b = bwd
    return out


class EncDec:
    def __init__(self, mode, seed=0):
        assert mode in ("fixed", "attn")
        self.mode = mode
        rng = np.random.default_rng(seed)
        self.p = {
            "We": T(rng.normal(0, 0.3, (D, N_IN))), "Ue": T(rng.normal(0, 0.1, (D, D))),
            "be": T(np.zeros(D)),
            "Wp": T(rng.normal(0, 0.3, (D, N_IN))), "Wc": T(rng.normal(0, 0.3, (D, D))),
            "Ud": T(rng.normal(0, 0.1, (D, D))), "bd": T(np.zeros(D)),
            "Vo": T(rng.normal(0, 0.3, (N_IN, D))), "c": T(np.zeros(N_IN)),
        }

    def encode(self, src):
        h = T(np.zeros(D))
        hs = []
        for s in src:
            h = tanh(add(add(matmul(self.p["Ue"], h), matmul(self.p["We"], onehot(s))), self.p["be"]))
            hs.append(h)
        return hs

    def context(self, h_prev, hs):
        if self.mode == "fixed":
            return hs[-1], None
        scores = [dot(h_prev, hi) for hi in hs]
        mx = max(s.data for s in scores)
        es = [exp(add(s, -mx)) for s in scores]
        z = es[0]
        for e in es[1:]:
            z = add(z, e)
        alphas = [div(e, z) for e in es]
        ctx = mul(alphas[0], hs[0])
        for a, hi in zip(alphas[1:], hs[1:]):
            ctx = add(ctx, mul(a, hi))
        return ctx, np.array([float(a.data) for a in alphas])

    def forward(self, src, tgt_in, tgt_out):
        hs = self.encode(src)
        h = hs[-1]
        losses, attns, preds = [], [], []
        for t, (xi, yi) in enumerate(zip(tgt_in, tgt_out)):
            ctx, alpha = self.context(h, hs)
            x = add(add(matmul(self.p["Wp"], onehot(xi)), matmul(self.p["Wc"], ctx)), self.p["bd"])
            h = tanh(add(matmul(self.p["Ud"], h), x))
            y = add(matmul(self.p["Vo"], h), self.p["c"])
            losses.append(softmax_ce(y, yi))
            preds.append(np.argmax(y.data))
            if alpha is not None:
                attns.append(alpha)
        loss = losses[0]
        for l in losses[1:]:
            loss = add(loss, l)
        return div(loss, float(len(losses))), attns, preds

    def greedy(self, src, max_steps=None):
        hs = self.encode(src)
        h = hs[-1]
        out, attns = [], []
        xi = BOS
        for _ in range(max_steps or len(src) + 2):
            ctx, alpha = self.context(h, hs)
            x = add(add(matmul(self.p["Wp"], onehot(xi)), matmul(self.p["Wc"], ctx)), self.p["bd"])
            h = tanh(add(matmul(self.p["Ud"], h), x))
            y = add(matmul(self.p["Vo"], h), self.p["c"])
            xi = int(np.argmax(y.data))
            if alpha is not None:
                attns.append(alpha)
            if xi == EOS:
                break
            out.append(xi)
        return out, attns


def make_pair(rng, L):
    src = [int(s) for s in rng.choice(SYM, size=L)]
    return src, list(reversed(src))


def train(mode, steps=600, bs=6, lr=0.01, seed=0):
    m = EncDec(mode, seed)
    opt = Adam(m.p, lr=lr)
    rng = np.random.default_rng(seed + 7)
    curve = []
    for s in range(steps):
        tot = 0.0
        for _ in range(bs):
            L = int(rng.integers(3, 9))
            src, tgt = make_pair(rng, L)
            tin = [BOS] + tgt[:-1]
            loss, _, _ = m.forward(src, tin, tgt)
            backward(loss)
            tot += float(loss.data)
        opt.step()
        if (s + 1) % 25 == 0:
            curve.append((s + 1, tot / bs))
    return m, curve


def evaluate(m, lengths=(3, 5, 8, 10, 12), n=40, seed=123):
    rng = np.random.default_rng(seed)
    res = {}
    for L in lengths:
        ok = 0
        for _ in range(n):
            src, tgt = make_pair(rng, L)
            pred, _ = m.greedy(src, max_steps=L + 2)
            ok += int(pred == tgt)
        res[L] = ok / n
    return res


if __name__ == "__main__":
    summary, curves, accs = {}, {}, {}
    for mode in ("fixed", "attn"):
        m, curve = train(mode)
        acc = evaluate(m)
        curves[mode], accs[mode] = curve, acc
        summary[mode] = {"acc_by_len": acc}
        print(f"{mode}: " + " ".join(f"L={k}:{v:.2f}" for k, v in acc.items()), flush=True)

        if mode == "attn":
            # 注意力热图：固定一条长度 6 的样例
            rng = np.random.default_rng(2024)
            src, tgt = make_pair(rng, 6)
            pred, attn = m.greedy(src, max_steps=6)
            with open(os.path.join(OUT, "attention_weights.csv"), "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["decoder_step", "src_pos", "src_symbol", "alpha"])
                for t, row in enumerate(attn):
                    for i, a in enumerate(row):
                        w.writerow([t, i, src[i], f"{a:.6f}"])
            summary["attn"]["example"] = {"src": src, "tgt": tgt, "pred": pred,
                                          "attention": [list(map(float, r)) for r in attn]}
            plt.figure(figsize=(4.6, 3.6))
            plt.imshow(np.array(attn), cmap="viridis", aspect="auto")
            plt.xlabel("encoder position")
            plt.ylabel("decoder step")
            plt.title("dot-product attention")
            plt.colorbar()
            plt.tight_layout()
            plt.savefig(os.path.join(OUT, "fig_attention_heatmap.png"), dpi=130)
            plt.close()

    with open(os.path.join(OUT, "accuracy_by_length.csv"), "w") as f:
        f.write("length,fixed,attn\n")
        for L in accs["fixed"]:
            f.write(f"{L},{accs['fixed'][L]:.4f},{accs['attn'][L]:.4f}\n")

    with open(os.path.join(OUT, "training_curve.csv"), "w") as f:
        f.write("mode,step,loss\n")
        for mode, c in curves.items():
            for s, l in c:
                f.write(f"{mode},{s},{l:.6f}\n")

    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.4))
    for mode, c in curves.items():
        ax[0].plot([s for s, _ in c], [l for _, l in c], label=mode)
    ax[0].set_xlabel("step")
    ax[0].set_ylabel("training loss")
    ax[0].legend()
    ax[0].set_title("encoder-decoder training")
    for mode, acc in accs.items():
        ax[1].plot(list(acc.keys()), list(acc.values()), "o-", label=mode)
    ax[1].set_xlabel("sequence length (10,12 unseen)")
    ax[1].set_ylabel("exact match")
    ax[1].set_ylim(0, 1.05)
    ax[1].legend()
    ax[1].set_title("reversal accuracy")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_encdec.png"), dpi=120)
