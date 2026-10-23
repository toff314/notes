"""lab-01: BERT 掩码策略模拟
统计 15% 选中、80/10/10 替换下的实际比例，并用双向 bigram 上下文模型
衡量被选中词元的可预测性（区分「真上下文预测」与「原词仍在输入里的泄漏」）。

运行: python3 lab01_mask_policy.py
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
rng = np.random.default_rng(20261020)

# ---------- 1. 构造有结构的玩具语料（模板生成，便于度量上下文可预测性） ----------
DET = ["the", "a"]
ADJ = ["red", "small", "old", "bright", "quiet"]
NOUN = ["cat", "dog", "car", "book", "river", "canyon", "engine", "student"]
VERB = ["sees", "likes", "finds", "carries", "opens", "watches"]
PREP = ["in", "near", "under", "beside"]
PUNCT = ["."]

TEMPLATES = [
    ["DET", "ADJ", "NOUN", "VERB", "DET", "NOUN", "PUNCT"],
    ["DET", "NOUN", "VERB", "DET", "ADJ", "NOUN", "PUNCT"],
    ["DET", "ADJ", "NOUN", "PREP", "DET", "NOUN", "PUNCT"],
    ["DET", "NOUN", "PREP", "DET", "ADJ", "NOUN", "PUNCT"],
    ["DET", "NOUN", "VERB", "PREP", "DET", "NOUN", "PUNCT"],
]
SLOTS = {"DET": DET, "ADJ": ADJ, "NOUN": NOUN, "VERB": VERB, "PREP": PREP, "PUNCT": PUNCT}


def make_corpus(n=6000):
    sents = []
    for _ in range(n):
        tpl = TEMPLATES[rng.integers(len(TEMPLATES))]
        sents.append([SLOTS[s][rng.integers(len(SLOTS[s]))] for s in tpl])
    return sents


corpus = make_corpus()
vocab = sorted({w for s in corpus for w in s})
w2i = {w: i for i, w in enumerate(vocab)}
ids = np.array([[w2i[w] for w in s] for s in corpus], dtype=np.int64)
V = len(vocab)
MASK_ID = V  # 单独编号，只用于展示，不参与 bigram 统计
print(f"语料: {len(corpus)} 句, 词表 {V}, 总词元 {ids.size}")

# ---------- 2. 三种掩码策略 ----------
POLICIES = {
    "BERT 80/10/10": (0.8, 0.1, 0.1),
    "全掩码 100/0/0": (1.0, 0.0, 0.0),
    "不掩码 0/50/50": (0.0, 0.5, 0.5),
}


def apply_policy(seqs, p_mask, p_rand, p_keep, rate=0.15):
    out = seqs.copy()
    selected = np.zeros_like(seqs, dtype=bool)
    stats = {"selected": 0, "masked": 0, "random": 0, "kept": 0, "random_hit": 0}
    for i in range(seqs.shape[0]):
        L = seqs.shape[1]
        # BERT 原实现按 token 独立以 15% 概率选中（此处用伯努利抽样，
        # 避免短句 round 造成的选中率偏移）
        idx = np.flatnonzero(rng.random(L) < rate)
        k = len(idx)
        selected[i, idx] = True
        u = rng.random(k)
        m_idx = idx[u < p_mask]
        r_idx = idx[(u >= p_mask) & (u < p_mask + p_rand)]
        out[i, m_idx] = MASK_ID
        if len(r_idx):
            # 按一元分布抽随机词（这里用语料经验分布）
            rand_words = rng.choice(V, size=len(r_idx), p=unigram_p)
            out[i, r_idx] = rand_words
            stats["random_hit"] += int(np.sum(rand_words == seqs[i, r_idx]))
        stats["selected"] += k
        stats["masked"] += len(m_idx)
        stats["random"] += len(r_idx)
        stats["kept"] += k - len(m_idx) - len(r_idx)
    return out, selected, stats


flat = ids.ravel()
counts = np.bincount(flat, minlength=V).astype(float)
unigram_p = counts / counts.sum()

# ---------- 3. 双向 bigram 上下文模型（加一平滑） ----------
bigram = np.zeros((V, V), dtype=np.float64)
for s in ids:
    for a, b in zip(s[:-1], s[1:]):
        bigram[a, b] += 1
left_tot = bigram.sum(axis=1, keepdims=True) + V
right_tot = bigram.sum(axis=0, keepdims=True) + V
log_left = np.log((bigram + 1.0) / left_tot)          # P(next | prev)
log_right = np.log((bigram + 1.0) / right_tot)        # P(prev | next)


def context_scores(seq, pos):
    """位置无关的左右上下文打分：log P(w|prev) + log P(w|next)。"""
    prev = seq[pos - 1] if pos > 0 else None
    nxt = seq[pos + 1] if pos + 1 < len(seq) else None
    if prev == MASK_ID:
        prev = None
    if nxt == MASK_ID:
        nxt = None
    score = np.zeros(V)
    if prev is not None:
        score += log_left[prev]
    if nxt is not None:
        score += log_right[:, nxt]
    return score


def topk_hit(scores, target, k):
    order = np.argsort(-scores)[:k]
    return int(target in order)


rows_stats, rows_pred, sample_rows = [], [], []
for name, (pm, pr, pk) in POLICIES.items():
    out, selected, st = apply_policy(ids, pm, pr, pk)
    total = ids.size
    sel = st["selected"]
    leak = 0
    hit1 = hit5 = evaluated = 0
    for i in range(ids.shape[0]):
        for pos in np.flatnonzero(selected[i]):
            target = int(ids[i, pos])
            # 直接泄漏：目标词仍原样留在被选位置
            if out[i, pos] == target:
                leak += 1
                continue
            sc = context_scores(out[i], pos)
            hit1 += topk_hit(sc, target, 1)
            hit5 += topk_hit(sc, target, 5)
            evaluated += 1
            if name == "BERT 80/10/10" and len(sample_rows) < 12:
                top = np.argsort(-sc)[:3]
                sample_rows.append({
                    "position": int(pos), "target": vocab[target],
                    "top1": vocab[top[0]], "top2": vocab[top[1]], "top3": vocab[top[2]],
                    "in_input": int(out[i, pos] == target),
                })
    rows_stats.append({
        "policy": name,
        "selected_rate": sel / total,
        "mask_share": st["masked"] / sel,
        "random_share": st["random"] / sel,
        "keep_share": st["kept"] / sel,
        "input_mask_rate": st["masked"] / total,
        "leak_rate": leak / sel,
        "random_collision": st["random_hit"] / max(st["random"], 1),
    })
    rows_pred.append({
        "policy": name, "evaluated": evaluated,
        "top1": hit1 / max(evaluated, 1), "top5": hit5 / max(evaluated, 1),
    })

print("\n掩码比例（选中后）")
for r in rows_stats:
    print(f"  {r['policy']}: mask={r['mask_share']:.3f} random={r['random_share']:.3f} "
          f"keep={r['keep_share']:.3f} | 占全文 mask={r['input_mask_rate']:.4f} "
          f"泄漏={r['leak_rate']:.3f}")

print("\n双向 bigram 可预测性（仅统计目标已移出输入的位置）")
for r in rows_pred:
    print(f"  {r['policy']}: n={r['evaluated']} top1={r['top1']:.3f} top5={r['top5']:.3f}")

with open(os.path.join(OUT, "masking_stats.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_stats[0]))
    w.writeheader(); w.writerows(rows_stats)
with open(os.path.join(OUT, "predictability.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows_pred[0]))
    w.writeheader(); w.writerows(rows_pred)
with open(os.path.join(OUT, "samples.json"), "w", encoding="utf-8") as f:
    json.dump(sample_rows, f, ensure_ascii=False, indent=2)

# ---------- 4. 图 ----------
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
labels = [r["policy"] for r in rows_stats]
x = np.arange(len(labels))
wdt = 0.25
axes[0].bar(x - wdt, [r["mask_share"] for r in rows_stats], wdt, label="[MASK]")
axes[0].bar(x, [r["random_share"] for r in rows_stats], wdt, label="随机词")
axes[0].bar(x + wdt, [r["keep_share"] for r in rows_stats], wdt, label="保持原词")
axes[0].axhline(0.8, ls="--", lw=1, color="gray")
axes[0].axhline(0.1, ls=":", lw=1, color="gray")
axes[0].set_xticks(x); axes[0].set_xticklabels(labels, fontsize=9)
axes[0].set_ylabel("占被选中词元的比例"); axes[0].set_title("选中后的处理方式")
axes[0].legend(fontsize=8)

axes[1].bar(x - wdt / 2, [r["top1"] for r in rows_pred], wdt, label="top-1")
axes[1].bar(x + wdt / 2, [r["top5"] for r in rows_pred], wdt, label="top-5")
axes[1].set_xticks(x); axes[1].set_xticklabels(labels, fontsize=9)
axes[1].set_ylim(0, 1.0); axes[1].set_ylabel("命中率")
axes[1].set_title("双向 bigram 上下文预测")
axes[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "masking_rates.png"), dpi=150)
print("\n产物已写入", OUT)
