#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-01  IBM Model 1 的 EM 词对齐（离线，只用 numpy + 标准库）

对应 actions.md 第 1 条；对应书中 §历史注记（IBM 模型 1–5）。
语料写死在脚本里：8 组英语-德语句对 + 人工标注的金对齐。
"""
import json
import os

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- 语料
# (英语词序列, 德语词序列, 金对齐 [(en_i, de_j), ...])
CORPUS = [
    ("the house is big".split(),        "das haus ist groß".split(),        [(0, 0), (1, 1), (2, 2), (3, 3)]),
    ("the house is small".split(),      "das haus ist klein".split(),       [(0, 0), (1, 1), (2, 2), (3, 3)]),
    ("i see the house".split(),         "ich sehe das haus".split(),        [(0, 0), (1, 1), (2, 2), (3, 3)]),
    ("i see the big house".split(),     "ich sehe das große haus".split(),  [(0, 0), (1, 1), (2, 2), (3, 4), (4, 3)]),
    ("the dog is small".split(),        "der hund ist klein".split(),       [(0, 0), (1, 1), (2, 2), (3, 3)]),
    ("i see the dog".split(),           "ich sehe den hund".split(),        [(0, 0), (1, 1), (2, 2), (3, 3)]),
    ("the dog sees the house".split(),  "der hund sieht das haus".split(),  [(0, 0), (1, 1), (2, 2), (3, 3), (4, 4)]),
    ("i see a house".split(),           "ich sehe ein haus".split(),        [(0, 0), (1, 1), (2, 2), (3, 3)]),
]

NULL = "<NULL>"


def build_vocab():
    es, fs = {NULL}, {NULL}
    for e, f, _ in CORPUS:
        es.update(e)
        fs.update(f)
    return sorted(es), sorted(fs)


E_VOCAB, F_VOCAB = build_vocab()
E_IDX = {w: i for i, w in enumerate(E_VOCAB)}
F_IDX = {w: i for i, w in enumerate(F_VOCAB)}

# 每条句子的索引表，英语侧在最前面插入 NULL
SENTS = []
for e, f, gold in CORPUS:
    ei = [0] + [E_IDX[w] for w in e]          # 0 号是 NULL
    fi = [F_IDX[w] for w in f]
    SENTS.append((ei, fi, gold))


def em(n_iter=15):
    """标准 IBM Model 1 EM：t(f|e) 初始均匀。"""
    t = np.full((len(F_VOCAB), len(E_VOCAB)), 1.0 / len(F_VOCAB))
    loglik_hist = []
    for _ in range(n_iter):
        count = np.zeros_like(t)
        total = np.zeros(len(E_VOCAB))
        ll = 0.0
        for ei, fi, _ in SENTS:
            for j in fi:
                denom = t[j, ei].sum()          # 对英语側（含 NULL）求和
                ll += np.log(denom)
                count[j, ei] += t[j, ei] / denom
                total[ei] += t[j, ei] / denom
        t = count / np.maximum(total, 1e-12)
        loglik_hist.append(ll)
    return t, loglik_hist


def viterbi_align(t, ei, fi):
    """Model 1 的 Viterbi 对齐：每个目标词取 argmax_e t(f|e)（解码时排除 NULL）。"""
    out = []
    for jj, j in enumerate(fi):
        scores = t[j, ei].copy()
        scores[0] = -1.0                 # 位置 0 是 NULL，解码时不允许对齐到它
        pos = int(np.argmax(scores))
        out.append((pos - 1, jj))        # 位置 p 对应英语词下标 p-1；jj 是德语词在句中的位置
    return out


def prf(pred, gold):
    pred, gold = set(pred), set(gold)
    if not pred or not gold:
        return 0.0, 0.0, 0.0
    hit = len(pred & gold)
    p, r = hit / len(pred), hit / len(gold)
    f1 = 0.0 if p + r == 0 else 2 * p * r / (p + r)
    return p, r, f1


t, loglik = em()
rows = []
tot_p = tot_r = tot_f = 0.0
detail = []
for k, ((e, f, gold), (ei, fi, _)) in enumerate(zip(CORPUS, SENTS)):
    links = viterbi_align(t, ei, fi)
    pred = [(i, j) for i, j in links if i != 0]      # 去掉 NULL 链接
    p, r, f1 = prf(pred, gold)
    tot_p += p
    tot_r += r
    tot_f += f1
    detail.append({
        "id": k + 1,
        "en": " ".join(e),
        "de": " ".join(f),
        "pred": [{"en": E_VOCAB[i], "de": F_VOCAB[j]} for i, j in pred],
        "gold": [{"en": e[i], "de": f[j]} for i, j in gold],
        "P": round(p, 4), "R": round(r, 4), "F1": round(f1, 4),
    })

n = len(CORPUS)
mean_p, mean_r, mean_f = tot_p / n, tot_r / n, tot_f / n

with open(os.path.join(OUT, "alignments.json"), "w", encoding="utf-8") as fh:
    json.dump({"mean_P": round(mean_p, 4), "mean_R": round(mean_r, 4),
               "mean_F1": round(mean_f, 4), "pairs": detail}, fh, ensure_ascii=False, indent=2)

# 概率表：只看非 NULL 的英语词，取每列最高的 2 个德语词
with open(os.path.join(OUT, "t_table.csv"), "w", encoding="utf-8") as fh:
    fh.write("en,de,t\n")
    for ei, w in enumerate(E_VOCAB):
        if w == NULL:
            continue
        for fj in np.argsort(-t[:, ei])[:2]:
            fh.write(f"{w},{F_VOCAB[fj]},{t[fj, ei]:.4f}\n")

with open(os.path.join(OUT, "loglik.csv"), "w", encoding="utf-8") as fh:
    fh.write("iter,loglik\n")
    for i, v in enumerate(loglik, 1):
        fh.write(f"{i},{v:.6f}\n")

# 一张热力图：第 4 句 i see the big house
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ei, fi, _ = SENTS[3]
M = t[np.ix_(fi, ei)]
fig, ax = plt.subplots(figsize=(6.4, 3.6))
im = ax.imshow(M, cmap="Blues", aspect="auto")
ax.set_xticks(range(len(ei)))
ax.set_xticklabels([E_VOCAB[i] for i in ei], rotation=30, ha="right")
ax.set_yticks(range(len(fi)))
ax.set_yticklabels([F_VOCAB[j] for j in fi])
for a in range(len(fi)):
    for b in range(len(ei)):
        ax.text(b, a, f"{M[a, b]:.2f}", ha="center", va="center", fontsize=7)
ax.set_title("IBM Model 1  t(f|e)  (sentence 4)")
fig.colorbar(im, ax=ax, shrink=0.8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "t_heatmap.png"), dpi=150)

print(f"句对数={n}  英 vocab={len(E_VOCAB)}(含 NULL)  德 vocab={len(F_VOCAB)}")
print(f"EM 迭代={len(loglik)}")
print(f"loglik: 首轮 {loglik[0]:.4f}  末轮 {loglik[-1]:.4f}  单调递增={all(b >= a - 1e-9 for a, b in zip(loglik, loglik[1:]))}")
print(f"Viterbi 对齐 宏平均  P={mean_p:.4f}  R={mean_r:.4f}  F1={mean_f:.4f}")
for d in detail:
    print(f"  #{d['id']} F1={d['F1']:.3f}  {d['en']}  ||  {d['de']}")
print("t(the→das) = %.4f   t(the→der) = %.4f   t(the→den) = %.4f"
      % (t[F_IDX['das'], E_IDX['the']], t[F_IDX['der'], E_IDX['the']], t[F_IDX['den'], E_IDX['the']]))
print("t(house→haus) = %.4f   t(see→sehe) = %.4f"
      % (t[F_IDX['haus'], E_IDX['house']], t[F_IDX['sehe'], E_IDX['see']]))
