#!/usr/bin/env python3
"""Lab 02: learned position embeddings + one Transformer block (numpy).

Char-level next-token prediction on a tiny repeated corpus.
Implements forward and backward passes by hand: RMSNorm, single-head causal
self-attention, residual stream, ReLU feed-forward, tied unembedding.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)
MASK_CACHE = {}


def softmax(x, axis=-1):
    m = np.max(x, axis=axis, keepdims=True)
    e = np.exp(x - m)
    return e / np.sum(e, axis=axis, keepdims=True)


def causal_mask(n):
    if n not in MASK_CACHE:
        MASK_CACHE[n] = np.triu(np.ones((n, n), dtype=bool), k=1)
    return MASK_CACHE[n]


def rmsnorm_forward(x, g, eps=1e-5):
    r = np.sqrt(np.mean(x * x, axis=-1, keepdims=True) + eps)
    xhat = x / r
    return xhat * g, (x, r, xhat)


def rmsnorm_backward(dy, cache, g):
    x, r, xhat = cache
    d = x.shape[-1]
    dg = np.sum(dy * xhat, axis=tuple(range(dy.ndim - 1)))
    dx = (g * dy) / r - x * np.sum(g * dy * x, axis=-1, keepdims=True) / (d * r ** 3)
    return dx, dg


def init_params(vocab, n_ctx, d, dff, seed=7):
    rng = np.random.default_rng(seed)
    p = {
        "E": rng.normal(0, 0.08, (vocab, d)),
        "P": rng.normal(0, 0.08, (n_ctx, d)),
        "Wq": rng.normal(0, 0.3, (d, d)),
        "Wk": rng.normal(0, 0.3, (d, d)),
        "Wv": rng.normal(0, 0.3, (d, d)),
        "Wo": rng.normal(0, 0.3, (d, d)),
        "g1": np.ones(d),
        "g2": np.ones(d),
        "W1": rng.normal(0, np.sqrt(2.0 / d), (d, dff)),
        "b1": np.zeros(dff),
        "W2": rng.normal(0, np.sqrt(2.0 / dff), (dff, d)),
        "b2": np.zeros(d),
    }
    return p


def forward(tokens, p):
    B, N = tokens.shape
    d = p["E"].shape[1]
    X = p["E"][tokens] + p["P"][None, :N, :]
    r1, c1 = rmsnorm_forward(X, p["g1"])
    Q, K, V = r1 @ p["Wq"], r1 @ p["Wk"], r1 @ p["Wv"]
    scores = Q @ K.transpose(0, 2, 1) / np.sqrt(d)
    scores = np.where(causal_mask(N)[None, :, :], -1e30, scores)
    A = softmax(scores, axis=-1)
    H = A @ V
    attn = H @ p["Wo"]
    T3 = X + attn
    r2, c2 = rmsnorm_forward(T3, p["g2"])
    z = r2 @ p["W1"] + p["b1"]
    f = np.maximum(z, 0.0)
    ff = f @ p["W2"] + p["b2"]
    T5 = T3 + ff
    logits = T5 @ p["E"].T
    cache = dict(tokens=tokens, X=X, c1=c1, r1=r1, Q=Q, K=K, V=V, A=A, H=H,
                 T3=T3, c2=c2, r2=r2, z=z, f=f, T5=T5, logits=logits)
    return logits, cache


def loss_and_grads(windows, p):
    tokens = windows[:, :-1]
    targets = windows[:, 1:]
    logits, c = forward(tokens, p)
    B, N, V = logits.shape
    probs = softmax(logits, axis=-1)
    picked = probs[np.arange(B)[:, None], np.arange(N)[None, :], targets]
    loss = float(-np.mean(np.log(picked + 1e-12)))

    dlogits = probs
    dlogits[np.arange(B)[:, None], np.arange(N)[None, :], targets] -= 1.0
    dlogits /= B * N

    grads = {}
    grads["E"] = dlogits.reshape(-1, V).T @ c["T5"].reshape(-1, p["E"].shape[1])
    dT5 = dlogits @ p["E"]
    dT3 = dT5.copy()
    dff = dT5
    grads["W2"] = c["f"].reshape(-1, c["f"].shape[-1]).T @ dff.reshape(-1, dff.shape[-1])
    grads["b2"] = dff.sum(axis=(0, 1))
    dz = (dff @ p["W2"].T) * (c["z"] > 0)
    grads["W1"] = c["r2"].reshape(-1, c["r2"].shape[-1]).T @ dz.reshape(-1, dz.shape[-1])
    grads["b1"] = dz.sum(axis=(0, 1))
    dr2 = dz @ p["W1"].T
    dT3_ln, grads["g2"] = rmsnorm_backward(dr2, c["c2"], p["g2"])
    dT3 += dT3_ln

    dattn = dT3
    grads["Wo"] = c["H"].reshape(-1, c["H"].shape[-1]).T @ dattn.reshape(-1, dattn.shape[-1])
    dH = dattn @ p["Wo"].T
    dA = dH @ c["V"].transpose(0, 2, 1)
    dV = c["A"].transpose(0, 2, 1) @ dH
    dscores = c["A"] * (dA - np.sum(dA * c["A"], axis=-1, keepdims=True))
    dscale = np.sqrt(p["Wq"].shape[0])
    dQ = dscores @ c["K"] / dscale
    dK = dscores.transpose(0, 2, 1) @ c["Q"] / dscale
    grads["Wq"] = c["r1"].reshape(-1, c["r1"].shape[-1]).T @ dQ.reshape(-1, dQ.shape[-1])
    grads["Wk"] = c["r1"].reshape(-1, c["r1"].shape[-1]).T @ dK.reshape(-1, dK.shape[-1])
    grads["Wv"] = c["r1"].reshape(-1, c["r1"].shape[-1]).T @ dV.reshape(-1, dV.shape[-1])
    dr1 = dQ @ p["Wq"].T + dK @ p["Wk"].T + dV @ p["Wv"].T
    dX_ln, grads["g1"] = rmsnorm_backward(dr1, c["c1"], p["g1"])
    dX = dT3 + dX_ln
    grads["P"] = dX.sum(axis=0)
    dE = grads["E"]
    np.add.at(dE, tokens.reshape(-1), dX.reshape(-1, dX.shape[-1]))
    return loss, grads


def gradient_check():
    vocab, n_ctx, d, dff = 6, 4, 4, 8
    p = init_params(vocab, n_ctx, d, dff, seed=11)
    rng = np.random.default_rng(3)
    tokens = rng.integers(0, vocab, size=(2, n_ctx))
    loss, grads = loss_and_grads(tokens, p)
    picks = [("E", (0, 0)), ("E", (3, 2)), ("P", (1, 1)), ("Wq", (2, 1)),
             ("Wk", (0, 3)), ("Wv", (1, 0)), ("Wo", (2, 2)), ("W1", (1, 3)),
             ("W2", (4, 2)), ("g1", (0,)), ("g2", (3,)), ("b1", (2,))]
    eps = 1e-6
    rows = []
    for name, idx in picks:
        old = p[name][idx]
        p[name][idx] = old + eps
        lp, _ = loss_and_grads(tokens, p)
        p[name][idx] = old - eps
        lm, _ = loss_and_grads(tokens, p)
        p[name][idx] = old
        num = (lp - lm) / (2 * eps)
        ana = grads[name][idx]
        rel = abs(num - ana) / max(1e-8, abs(num) + abs(ana))
        rows.append({"param": name, "index": list(idx), "analytic": float(ana),
                     "numeric": float(num), "rel_error": float(rel)})
    return max(r["rel_error"] for r in rows), rows


class Adam:
    def __init__(self, params, lr=0.01, b1=0.9, b2=0.999, eps=1e-8):
        self.lr, self.b1, self.b2, self.eps = lr, b1, b2, eps
        self.m = {k: np.zeros_like(v) for k, v in params.items()}
        self.v = {k: np.zeros_like(v) for k, v in params.items()}
        self.t = 0

    def step(self, params, grads):
        self.t += 1
        for k in params:
            self.m[k] = self.b1 * self.m[k] + (1 - self.b1) * grads[k]
            self.v[k] = self.b2 * self.v[k] + (1 - self.b2) * grads[k] ** 2
            mhat = self.m[k] / (1 - self.b1 ** self.t)
            vhat = self.v[k] / (1 - self.b2 ** self.t)
            params[k] -= self.lr * mhat / (np.sqrt(vhat) + self.eps)


def eval_loss(windows, p, batch=64):
    total, n = 0.0, 0
    for i in range(0, len(windows), batch):
        tok = windows[i:i + batch]
        logits, _ = forward(tok[:, :-1], p)
        probs = softmax(logits, axis=-1)
        targets = tok[:, 1:]
        picked = probs[np.arange(tok.shape[0])[:, None], np.arange(tok.shape[1] - 1)[None, :], targets]
        total += float(-np.sum(np.log(picked + 1e-12)))
        n += targets.size
    return total / n


def generate(prompt, p, stoi, itos, length=60, temperature=0.8, top_k=5, seed=5):
    rng = np.random.default_rng(seed)
    ids = [stoi[c] for c in prompt]
    n_ctx = p["P"].shape[0]
    for _ in range(length):
        ctx = np.array([ids[-n_ctx:]], dtype=np.int64)
        logits, _ = forward(ctx, p)
        u = logits[0, -1] / temperature
        if top_k:
            cut = np.sort(u)[-top_k]
            u = np.where(u < cut, -np.inf, u)
        probs = softmax(u)
        nxt = int(rng.choice(len(probs), p=probs))
        ids.append(nxt)
    return "".join(itos[i] for i in ids)


def main():
    sentences = [
        "the cat sat on the mat. ",
        "the dog sat on the log. ",
        "a cat sat on a mat. ",
        "a dog sat on a log. ",
    ]
    corpus = "".join(sentences[i % len(sentences)] for i in range(90))
    chars = sorted(set(corpus))
    stoi = {c: i for i, c in enumerate(chars)}
    itos = {i: c for c, i in stoi.items()}
    data = np.array([stoi[c] for c in corpus], dtype=np.int64)
    n_ctx, d, dff = 16, 24, 48
    starts = np.arange(len(data) - n_ctx)
    windows = np.stack([data[i:i + n_ctx + 1] for i in starts])
    split = int(0.8 * len(windows))
    train, val = windows[:split], windows[split:]

    p = init_params(len(chars), n_ctx, d, dff, seed=7)
    opt = Adam(p, lr=0.01)
    rng = np.random.default_rng(13)
    log = []
    init_train = eval_loss(train, p)
    for step in range(1, 701):
        idx = rng.integers(0, len(train), size=32)
        loss, grads = loss_and_grads(train[idx], p)
        opt.step(p, grads)
        if step % 25 == 0 or step == 1:
            log.append({"step": step, "train_loss": float(loss), "val_loss": eval_loss(val, p)})
    final_train = eval_loss(train, p)
    final_val = eval_loss(val, p)

    max_rel, grad_rows = gradient_check()
    sample = generate("the ", p, stoi, itos, length=60, temperature=0.8, top_k=5)
    sample_greedy = generate("the ", p, stoi, itos, length=40, temperature=0.01, top_k=1, seed=9)

    # Position ablation: zero / shuffle the learned position table at eval time.
    p_zero = {k: v.copy() for k, v in p.items()}
    p_zero["P"][:] = 0.0
    p_shuf = {k: v.copy() for k, v in p.items()}
    p_shuf["P"] = p_shuf["P"][rng.permutation(n_ctx)]

    with open(OUT / "training_log.csv", "w", encoding="utf-8") as f:
        f.write("step,train_loss,val_loss\n")
        for row in log:
            f.write(f"{row['step']},{row['train_loss']:.6f},{row['val_loss']:.6f}\n")
    with open(OUT / "gradient_check.csv", "w", encoding="utf-8") as f:
        f.write("param,index,analytic,numeric,rel_error\n")
        for row in grad_rows:
            f.write(f"{row['param']},\"{row['index']}\",{row['analytic']:.8e},"
                    f"{row['numeric']:.8e},{row['rel_error']:.3e}\n")

    n_params = sum(v.size for v in p.values())
    summary = {
        "config": {"vocab": len(chars), "n_ctx": n_ctx, "d": d, "dff": dff,
                   "block": "RMSNorm -> 1-head causal attention -> residual -> "
                            "RMSNorm -> ReLU FFN -> residual -> tied unembedding",
                   "params": int(n_params), "steps": 700, "batch": 32},
        "loss": {"init_train": init_train, "final_train": final_train,
                 "final_val": final_val,
                 "relative_drop": (init_train - final_train) / init_train},
        "gradient_check_max_rel_error": max_rel,
        "position_ablation_val_loss": {
            "learned": final_val,
            "zeroed": eval_loss(val, p_zero),
            "shuffled": eval_loss(val, p_shuf),
        },
        "position_embedding_row_norm_std": float(np.std(np.linalg.norm(p["P"], axis=1))),
        "samples": {"temperature_0.8_top5": sample, "greedy": sample_greedy},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    (OUT / "samples.json").write_text(json.dumps(summary["samples"], indent=2, ensure_ascii=False), encoding="utf-8")

    steps = [r["step"] for r in log]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(steps, [r["train_loss"] for r in log], label="train (batch)")
    ax.plot(steps, [r["val_loss"] for r in log], label="held-out")
    ax.set_xlabel("Adam step")
    ax.set_ylabel("cross-entropy (nats/char)")
    ax.set_title("Tiny Transformer block: next-character prediction")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.savefig(OUT / "loss_curve.png", dpi=160, bbox_inches="tight")
    plt.close(fig)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
