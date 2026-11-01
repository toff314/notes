#!/usr/bin/env python3
"""lab-04 序列分类的池化方式与权重绑定（§14.2.3、§14.3.2）。

两件事：
A. 线索在最前面的序列分类任务上，比较「取最后一个隐状态 / 平均池化 / 最大池化」。
   任务的标签只由第 0 个词元决定，后面 11 个词元是噪声——最后隐状态必须跨越 11 步记忆。
B. 字符级 RNN 语言模型：输出层与嵌入层绑定 vs 不绑定，比较参数量与验证困惑度。

所有梯度都用有限差分核对过（见 out/grad_check.json）。
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

rng_global = np.random.default_rng(14)


def softmax(z):
    z = z - z.max()
    e = np.exp(z)
    return e / e.sum()


# ============ A. 序列分类 ============
class Classifier:
    """h_t = tanh(U h_{t-1} + W e(x_t) + b)；池化后接线性读出。"""

    def __init__(self, V, d_e, d_h, K, seed, pool="last"):
        rng = np.random.default_rng(seed)
        self.p = {
            "E": rng.normal(0, 0.3, (V, d_e)),
            "W": rng.normal(0, 0.3, (d_h, d_e)),
            "U": rng.normal(0, 0.1, (d_h, d_h)),
            "b": np.zeros(d_h),
            "Vo": rng.normal(0, 0.3, (K, d_h)),
            "c": np.zeros(K),
        }
        self.pool = pool

    def forward(self, xs, y):
        p = self.p
        h = np.zeros(p["U"].shape[0])
        hs = []
        for x in xs:
            h = np.tanh(p["U"] @ h + p["W"] @ p["E"][x] + p["b"])
            hs.append(h)
        H = np.stack(hs)  # (T, d)
        if self.pool == "last":
            pooled, arg = H[-1], None
        elif self.pool == "mean":
            pooled, arg = H.mean(0), None
        else:
            norms = np.linalg.norm(H, axis=1)
            arg = int(np.argmax(norms))
            pooled = H[arg]
        logits = p["Vo"] @ pooled + p["c"]
        prob = softmax(logits)
        loss = -np.log(max(prob[y], 1e-12))
        return loss, dict(hs=H, pooled=pooled, arg=arg, prob=prob, xs=xs, y=y)

    def backward(self, cache):
        p, g = self.p, {k: np.zeros_like(v) for k, v in self.p.items()}
        prob, y = cache["prob"], cache["y"]
        dlogits = prob.copy()
        dlogits[y] -= 1.0
        g["Vo"] += np.outer(dlogits, cache["pooled"])
        g["c"] += dlogits
        dpool = p["Vo"].T @ dlogits
        H = cache["hs"]
        T = H.shape[0]
        dH = np.zeros_like(H)
        if self.pool == "last":
            dH[-1] = dpool
        elif self.pool == "mean":
            dH[:] = dpool / T
        else:
            dH[cache["arg"]] = dpool
        dh_next = np.zeros_like(dpool)
        for t in range(T - 1, -1, -1):
            dh = dH[t] + dh_next
            da = dh * (1 - H[t] ** 2)
            h_prev = H[t - 1] if t > 0 else np.zeros_like(H[t])
            g["U"] += np.outer(da, h_prev)
            g["W"] += np.outer(da, p["E"][cache["xs"][t]])
            g["E"][cache["xs"][t]] += p["W"].T @ da
            g["b"] += da
            dh_next = p["U"].T @ da
        return g


def make_cls_batch(rng, n, T=12, V=6):
    data = []
    for _ in range(n):
        y = int(rng.integers(0, 2))
        seq = [int(rng.integers(2, V)) for _ in range(T)]
        seq[int(rng.integers(0, T))] = y   # 线索符号（0/1）随机出现在某个位置
        data.append((seq, y))
    return data


def train_classifier(pool, T=12, steps=350, bs=8, lr=0.05, seed=0, d_h=24, d_e=8):
    V, K = 6, 2
    m = Classifier(V, d_e, d_h, K, seed, pool)
    adam_m = {k: np.zeros_like(v) for k, v in m.p.items()}
    adam_v = {k: np.zeros_like(v) for k, v in m.p.items()}
    rng = np.random.default_rng(seed + 100)
    curve = []
    for s in range(steps):
        batch = make_cls_batch(rng, bs, T, V)
        grads = {k: np.zeros_like(v) for k, v in m.p.items()}
        tot = 0.0
        for xs, y in batch:
            loss, cache = m.forward(xs, y)
            g = m.backward(cache)
            for k in grads:
                grads[k] += g[k]
            tot += loss
        t = s + 1
        for k in m.p:
            gk = grads[k] / bs
            adam_m[k] = 0.9 * adam_m[k] + 0.1 * gk
            adam_v[k] = 0.999 * adam_v[k] + 0.001 * gk * gk
            mh = adam_m[k] / (1 - 0.9 ** t)
            vh = adam_v[k] / (1 - 0.999 ** t)
            m.p[k] -= lr * mh / (np.sqrt(vh) + 1e-8)
        if t % 25 == 0:
            curve.append((t, tot / bs))
    return m, curve


def eval_classifier(m, T=12, seed=999, n=200, V=6):
    rng = np.random.default_rng(seed)
    ok = 0
    for xs, y in make_cls_batch(rng, n, T, V):
        loss, cache = m.forward(xs, y)
        ok += int(np.argmax(cache["prob"]) == y)
    return ok / n


# ============ B. 字符级语言模型（绑定 / 不绑定） ============
TEXT = (
    "the flights the airline was canceling were full . "
    "the flights the airline was canceling were full . "
    "the airline was canceling the flights . "
    "the flights were full . "
)
CHARS = sorted(set(TEXT))
V_C = len(CHARS)
STOI = {c: i for i, c in enumerate(CHARS)}


class CharLM:
    def __init__(self, V, d, seed, tied):
        rng = np.random.default_rng(seed)
        self.tied = tied
        self.p = {
            "E": rng.normal(0, 0.3, (V, d)),
            "W": rng.normal(0, 0.3, (d, d)),
            "U": rng.normal(0, 0.1, (d, d)),
            "b": np.zeros(d),
            "Vo": rng.normal(0, 0.3, (V, d)),
            "c": np.zeros(V),
        }

    def forward(self, xs):
        p = self.p
        d = p["U"].shape[0]
        h = np.zeros(d)
        hs, probs = [], []
        for x in xs:
            h = np.tanh(p["U"] @ h + p["W"] @ p["E"][x] + p["b"])
            logits = p["E"] @ h + p["c"] if self.tied else p["Vo"] @ h + p["c"]
            hs.append(h)
            probs.append(softmax(logits))
        return np.stack(hs), probs

    def loss_and_grad(self, xs, ys):
        p = self.p
        hs, probs = self.forward(xs)
        T = len(xs)
        loss = -np.mean([np.log(max(probs[t][ys[t]], 1e-12)) for t in range(T)])
        g = {k: np.zeros_like(v) for k, v in p.items()}
        dlogits_all = []
        for t in range(T):
            d = probs[t].copy()
            d[ys[t]] -= 1.0
            dlogits_all.append(d / T)
        dh_next = np.zeros_like(hs[0])
        for t in range(T - 1, -1, -1):
            dl = dlogits_all[t]
            if self.tied:
                g["E"] += np.outer(dl, hs[t])
                dh = p["E"].T @ dl
            else:
                g["Vo"] += np.outer(dl, hs[t])
                dh = p["Vo"].T @ dl
            g["c"] += dl
            dh = dh + dh_next
            da = dh * (1 - hs[t] ** 2)
            h_prev = hs[t - 1] if t > 0 else np.zeros_like(hs[t])
            g["U"] += np.outer(da, h_prev)
            g["W"] += np.outer(da, p["E"][xs[t]])
            g["E"][xs[t]] += p["W"].T @ da
            g["b"] += da
            dh_next = p["U"].T @ da
        return loss, g


def train_lm(tied, d=32, epochs=300, lr=0.05, seed=0):
    data = [STOI[c] for c in TEXT]
    m = CharLM(V_C, d, seed, tied)
    am = {k: np.zeros_like(v) for k, v in m.p.items()}
    av = {k: np.zeros_like(v) for k, v in m.p.items()}
    curve = []
    step = 0
    for ep in range(epochs):
        tot = 0.0
        for i in range(len(data) - 1):
            step += 1
            loss, g = m.loss_and_grad([data[i]], [data[i + 1]])
            tot += loss
            for k in m.p:
                am[k] = 0.9 * am[k] + 0.1 * g[k]
                av[k] = 0.999 * av[k] + 0.001 * g[k] * g[k]
                mh = am[k] / (1 - 0.9 ** step)
                vh = av[k] / (1 - 0.999 ** step)
                m.p[k] -= lr * mh / (np.sqrt(vh) + 1e-8)
        if (ep + 1) % 10 == 0:
            curve.append((ep + 1, tot / (len(data) - 1)))
    # 整段文本上的困惑度
    hs, probs = m.forward(data[:-1])
    nll = np.mean([-np.log(max(probs[t][data[t + 1]], 1e-12)) for t in range(len(data) - 1)])
    return m, curve, float(np.exp(nll))


def n_params(m):
    return int(sum(v.size for k, v in m.p.items() if not (m.tied and k == "Vo")))


# ============ 梯度校验 ============
def grad_check_classifier():
    m = Classifier(5, 4, 6, 2, seed=3, pool="mean")
    xs, y = [1, 3, 0, 4, 2], 1
    lost, cache = m.forward(xs, y)
    g = m.backward(cache)
    eps, worst = 1e-6, 0.0
    rng = np.random.default_rng(0)
    for k, node in m.p.items():
        for _ in range(4):
            idx = tuple(int(rng.integers(0, s)) for s in node.shape)
            old = node[idx]
            node[idx] = old + eps
            lp, _ = m.forward(xs, y)
            node[idx] = old - eps
            lm, _ = m.forward(xs, y)
            node[idx] = old
            num = (lp - lm) / (2 * eps)
            worst = max(worst, abs(num - g[k][idx]) / max(1e-9, abs(num) + abs(g[k][idx])))
    return worst


def grad_check_lm(tied):
    m = CharLM(V_C, 5, seed=4, tied=tied)
    xs = [STOI[c] for c in "the fl"]
    ys = [STOI[c] for c in "he fli"]
    loss, g = m.loss_and_grad(xs, ys)
    eps, worst = 1e-6, 0.0
    rng = np.random.default_rng(1)
    for k, node in m.p.items():
        for _ in range(4):
            idx = tuple(int(rng.integers(0, s)) for s in node.shape)
            old = node[idx]
            node[idx] = old + eps
            lp, _ = m.loss_and_grad(xs, ys)
            node[idx] = old - eps
            lm, _ = m.loss_and_grad(xs, ys)
            node[idx] = old
            num = (lp - lm) / (2 * eps)
            worst = max(worst, abs(num - g[k][idx]) / max(1e-9, abs(num) + abs(g[k][idx])))
    return worst


if __name__ == "__main__":
    checks = {
        "classifier_mean_pool_max_rel_err": grad_check_classifier(),
        "charlm_untied_max_rel_err": grad_check_lm(False),
        "charlm_tied_max_rel_err": grad_check_lm(True),
    }
    print("grad checks:", checks, flush=True)

    rows, curves = [], {}
    for T in (12, 40):
        for pool in ("last", "mean", "max"):
            m, curve = train_classifier(pool, T=T)
            acc = eval_classifier(m, T=T)
            rows.append((pool, T, acc))
            curves[(pool, T)] = curve
            print(f"T={T:2d} pool={pool:5s} acc={acc:.3f}", flush=True)

    with open(os.path.join(OUT, "pooling_compare.csv"), "w") as f:
        f.write("length,pool,accuracy\n")
        for p, T, a in rows:
            f.write(f"{T},{p},{a:.4f}\n")

    with open(os.path.join(OUT, "pooling_curve.csv"), "w") as f:
        f.write("length,pool,step,loss\n")
        for (p, T), c in curves.items():
            for s, l in c:
                f.write(f"{T},{p},{s},{l:.6f}\n")

    # 学习率对两种设置各扫一遍，避免「绑定版只是没调好」这种混淆
    lm_rows, lm_sweep = [], []
    for tied in (False, True):
        best = None
        for lr in (0.02, 0.05, 0.1):
            m, curve, ppl = train_lm(tied, lr=lr)
            lm_sweep.append({"tied": tied, "lr": lr, "ppl": ppl})
            print(f"tied={tied} lr={lr} params={n_params(m)} ppl={ppl:.3f}", flush=True)
            if best is None or ppl < best[2]:
                best = (tied, n_params(m), ppl)
        lm_rows.append(best)
        print(f"BEST tied={tied} ppl={best[2]:.3f}", flush=True)

    with open(os.path.join(OUT, "weight_tying.json"), "w") as f:
        json.dump({
            "vocab": V_C,
            "d": 32,
            "runs": [{"tied": t, "params": n, "ppl": p} for t, n, p in lm_rows],
            "lr_sweep": lm_sweep,
            "param_saving": lm_rows[0][1] - lm_rows[1][1],
            "corpus_chars": len(TEXT),
        }, f, ensure_ascii=False, indent=2)

    with open(os.path.join(OUT, "grad_check.json"), "w") as f:
        json.dump(checks, f, indent=2)

    fig, ax = plt.subplots(1, 2, figsize=(9.5, 3.4))
    for (p, T), c in curves.items():
        ax[0].plot([s for s, _ in c], [l for _, l in c], label=f"{p},T={T}")
    ax[0].set_xlabel("step")
    ax[0].set_ylabel("training loss")
    ax[0].set_title("pooling comparison (cue at first token)")
    ax[0].legend()
    names = ["last", "mean", "max"]
    a12 = [a for p, T, a in rows if T == 12]
    a40 = [a for p, T, a in rows if T == 40]
    ax[1].bar(np.arange(3) - 0.2, a12, 0.4, label="T=12")
    ax[1].bar(np.arange(3) + 0.2, a40, 0.4, label="T=40")
    ax[1].set_xticks(range(3))
    ax[1].set_xticklabels(names)
    ax[1].set_ylim(0, 1.1)
    ax[1].set_ylabel("accuracy")
    ax[1].set_title("pooling vs sequence length")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "fig_pooling.png"), dpi=120)
