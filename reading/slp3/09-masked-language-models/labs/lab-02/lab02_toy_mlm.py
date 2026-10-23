"""lab-02: 玩具掩码语言模型（位置无关词袋双塔）
在模板生成的小语料上做 15% 掩码，用「上下文词袋向量 · 词向量」打分，
训练后报告 top-1 / top-5 命中率与损失曲线，并与一元频率基线对照。

运行: python3 lab02_toy_mlm.py
"""
import csv
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(7)

# ---------- 语料：名词分类 + 动词按类选择，使上下文真的有信息 ----------
ANIMATE = ["cat", "dog", "student"]
VEHICLE = ["car", "engine"]
NATURE = ["river", "canyon"]
OBJECT = ["book"]
NOUN_CLASS = {}
for w in ANIMATE:
    NOUN_CLASS[w] = "animate"
for w in VEHICLE:
    NOUN_CLASS[w] = "vehicle"
for w in NATURE:
    NOUN_CLASS[w] = "nature"
for w in OBJECT:
    NOUN_CLASS[w] = "object"

VERB_BY_CLASS = {
    "animate": ["sees", "likes", "watches"],
    "vehicle": ["carries", "opens", "finds"],
    "nature": ["carries", "opens", "finds"],
    "object": ["carries", "opens", "finds"],
}
DET = ["the", "a"]
ADJ = ["red", "small", "old", "bright", "quiet"]
PREP = ["in", "near", "under", "beside"]
NOUNS = list(NOUN_CLASS)


def make_sentence():
    tpl = rng.integers(5)
    n1 = NOUNS[rng.integers(len(NOUNS))]
    n2 = NOUNS[rng.integers(len(NOUNS))]
    v = VERB_BY_CLASS[NOUN_CLASS[n1]][rng.integers(3)]
    if tpl == 0:
        s = [DET[rng.integers(2)], ADJ[rng.integers(len(ADJ))], n1, v,
             DET[rng.integers(2)], n2, "."]
    elif tpl == 1:
        s = [DET[rng.integers(2)], n1, v,
             DET[rng.integers(2)], ADJ[rng.integers(len(ADJ))], n2, "."]
    elif tpl == 2:
        s = [DET[rng.integers(2)], ADJ[rng.integers(len(ADJ))], n1,
             PREP[rng.integers(len(PREP))], DET[rng.integers(2)], n2, "."]
    elif tpl == 3:
        s = [DET[rng.integers(2)], n1,
             PREP[rng.integers(len(PREP))], DET[rng.integers(2)],
             ADJ[rng.integers(len(ADJ))], n2, "."]
    else:
        s = [DET[rng.integers(2)], n1, v,
             PREP[rng.integers(len(PREP))], DET[rng.integers(2)], n2, "."]
    return s



train_raw = [make_sentence() for _ in range(4000)]
dev_raw = [make_sentence() for _ in range(1000)]
vocab = sorted({w for s in train_raw + dev_raw for w in s})
w2i = {w: i for i, w in enumerate(vocab)}
i2w = {i: w for w, i in w2i.items()}
V = len(vocab)
train = np.array([[w2i[w] for w in s] for s in train_raw], dtype=np.int64)
dev = np.array([[w2i[w] for w in s] for s in dev_raw], dtype=np.int64)
print(f"训练 {train.shape[0]} 句 × {train.shape[1]} 词，词表 {V}")

# ---------- 掩码：每句抽一个位置（约 1/7 = 14.3%） ----------
def mask_batch(seqs):
    ctxs, targets, poses = [], [], []
    for s in seqs:
        pos = rng.integers(len(s))
        ctx = np.delete(s, pos)
        ctxs.append(ctx)
        targets.append(s[pos])
        poses.append(pos)
    return ctxs, np.array(targets), np.array(poses)


train_ctx, train_y, train_pos = mask_batch(train)
dev_ctx, dev_y, dev_pos = mask_batch(dev)

# ---------- 模型：上下文 = 未掩码词向量均值；logits = E @ ctx + b ----------
D = 48
E = rng.normal(0, 0.1, size=(V, D))
P = rng.normal(0, 0.1, size=(train.shape[1], D))
b = np.zeros(V)
mE, vE = np.zeros_like(E), np.zeros_like(E)
mP, vP = np.zeros_like(P), np.zeros_like(P)
mb, vb = np.zeros_like(b), np.zeros_like(b)
lr, beta1, beta2, eps = 0.05, 0.9, 0.999, 1e-8
step = 0


def forward(ctx_ids, pos):
    ctx = E[ctx_ids].mean(axis=0) + P[pos]
    logits = E @ ctx + b
    logits -= logits.max()
    p = np.exp(logits)
    p /= p.sum()
    return ctx, p


def loss_and_grad(ctx_ids, pos, target):
    ctx, p = forward(ctx_ids, pos)
    loss = -np.log(max(p[target], 1e-12))
    dlogits = p.copy()
    dlogits[target] -= 1.0
    grad_E = np.outer(dlogits, ctx)
    grad_b = dlogits
    dctx = E.T @ dlogits / len(ctx_ids)
    np.add.at(grad_E, ctx_ids, dctx)
    return loss, grad_E, grad_b, dctx, p


def adam(grad, m, v, name):
    global step
    m = beta1 * m + (1 - beta1) * grad
    v = beta2 * v + (1 - beta2) * grad * grad
    mhat = m / (1 - beta1 ** (step + 1))
    vhat = v / (1 - beta2 ** (step + 1))
    return m, v, -lr * mhat / (np.sqrt(vhat) + eps)


def evaluate(ctxs, ys, poses):
    losses, hit1, hit5 = [], 0, 0
    ranks = []
    for ctx_ids, y, pos in zip(ctxs, ys, poses):
        ctx, p = forward(ctx_ids, pos)
        losses.append(-np.log(max(p[y], 1e-12)))
        order = np.argsort(-p)
        rank = int(np.where(order == y)[0][0])
        ranks.append(rank)
        hit1 += rank == 0
        hit5 += rank < 5
    return float(np.mean(losses)), hit1 / len(ys), hit5 / len(ys), np.array(ranks)


rows = []
batch = 256
epochs = 300
for ep in range(epochs):
    order = rng.permutation(len(train_y))
    tot = 0.0
    for start in range(0, len(order), batch):
        idx = order[start:start + batch]
        gE = np.zeros_like(E)
        gP = np.zeros_like(P)
        gb = np.zeros_like(b)
        for j in idx:
            loss, ge, gbv, gctx, _ = loss_and_grad(train_ctx[j], int(train_pos[j]), int(train_y[j]))
            gE += ge
            gP[int(train_pos[j])] += gctx
            gb += gbv
            tot += loss
        gE /= len(idx)
        gP /= len(idx)
        gb /= len(idx)
        step += 1
        mE, vE, updE = adam(gE, mE, vE, "E")
        mP, vP, updP = adam(gP, mP, vP, "P")
        mb, vb, updb = adam(gb, mb, vb, "b")
        E += updE
        P += updP
        b += updb
    if ep % 10 == 0 or ep == epochs - 1:
        tr_loss = tot / len(order)
        dv_loss, dv1, dv5, _ = evaluate(dev_ctx, dev_y, dev_pos)
        rows.append({"epoch": ep, "train_loss": tr_loss, "dev_loss": dv_loss,
                     "dev_top1": dv1, "dev_top5": dv5})
        print(f"epoch {ep:3d} train={tr_loss:.3f} dev={dv_loss:.3f} top1={dv1:.3f} top5={dv5:.3f}")

dv_loss, dv1, dv5, ranks = evaluate(dev_ctx, dev_y, dev_pos)

# ---------- 基线：一元频率 ----------
freq = np.bincount(train.ravel(), minlength=V).astype(float)
freq /= freq.sum()
order = np.argsort(-freq)
uni1 = np.mean([order[0] == y for y in dev_y])
uni5 = np.mean([y in order[:5] for y in dev_y])
uni_loss = float(np.mean([-np.log(max(freq[y], 1e-12)) for y in dev_y]))

with open(os.path.join(OUT, "loss.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT, "metrics.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["model", "loss", "top1", "top5"])
    w.writerow(["toy_mlm_bow", dv_loss, dv1, dv5])
    w.writerow(["unigram_baseline", uni_loss, uni1, uni5])

# ---------- 样例预测 ----------
examples = []
for i in range(min(12, len(dev_y))):
    ctx, p = forward(dev_ctx[i], dev_pos[i])
    top = np.argsort(-p)[:3]
    examples.append({
        "context": " ".join(i2w[int(x)] for x in dev_ctx[i]),
        "target": i2w[int(dev_y[i])],
        "top1": i2w[int(top[0])], "top2": i2w[int(top[1])], "top3": i2w[int(top[2])],
        "p_target": float(p[dev_y[i]]),
    })
with open(os.path.join(OUT, "predictions.json"), "w", encoding="utf-8") as f:
    json.dump(examples, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT, "rank_hist.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["rank", "count"])
    for r in range(10):
        w.writerow([r, int(np.sum(ranks == r))])
    w.writerow([">=10", int(np.sum(ranks >= 10))])

print(f"\n玩具 MLM: loss={dv_loss:.3f} top1={dv1:.3f} top5={dv5:.3f}")
print(f"一元基线: loss={uni_loss:.3f} top1={uni1:.3f} top5={uni5:.3f}")

# ---------- 图 ----------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
ep = [r["epoch"] for r in rows]
axes[0].plot(ep, [r["train_loss"] for r in rows], label="训练损失")
axes[0].plot(ep, [r["dev_loss"] for r in rows], label="验证损失")
axes[0].set_xlabel("epoch"); axes[0].set_ylabel("交叉熵"); axes[0].set_title("玩具 MLM 损失")
axes[0].legend()

axes[1].bar(["top-1", "top-5"], [dv1, dv5], color=["#4C72B0", "#55A868"], label="玩具 MLM")
axes[1].plot([-0.2, 0.2], [uni1, uni1], "r--", lw=1, label="一元 top-1")
axes[1].plot([0.8, 1.2], [uni5, uni5], "k:", lw=1, label="一元 top-5")
axes[1].set_ylim(0, 1.0); axes[1].set_ylabel("命中率"); axes[1].set_title("掩码词预测命中率")
axes[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "loss_and_topk.png"), dpi=150)
print("产物已写入", OUT)
