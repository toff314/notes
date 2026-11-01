#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-02  手算 chrF 与 BLEU：复算书中 §13.6.2 给出的 .86 / .62

对应 actions.md 第 2 条。
书中的最小例子：REF = "witness for the past,"，HYP1 = "witness of the past,"，
HYP2 = "past witness"，chrF2,2 分别是 .86 与 .62（书里把空格去掉后按 18 个字符算）。
本脚本按 chrF 的原始定义（字符 n 元、β=2、n≤6 取平均）复算这两个数，
再做 k、β 的敏感性扫描，并用 BLEU 对照说明「短句上 BLEU 会塌成 0」。
"""
import os
from collections import Counter

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

REF = "the cat sat on the mat"
REF_W = "witness for the past,"
HYP1 = "witness of the past,"
HYP2 = "past witness"


def ngrams(s, n, keep_space=False):
    t = s if keep_space else s.replace(" ", "")
    return Counter(t[i:i + n] for i in range(len(t) - n + 1))


def f_score(pred, ref, n, beta, keep_space=False):
    P = ngrams(pred, n, keep_space)
    R = ngrams(ref, n, keep_space)
    if not P:
        return 0.0, 0.0, 0.0
    hit = sum((P & R).values())
    p = hit / sum(P.values())
    r = hit / max(sum(R.values()), 1)
    if p + r == 0:
        return p, r, 0.0
    b2 = beta ** 2
    return p, r, (1 + b2) * p * r / (b2 * p + r)


def chrf(pred, ref, max_n=6, beta=2.0, keep_space=False):
    ps, rs, fs = [], [], []
    for n in range(1, max_n + 1):
        p, r, f = f_score(pred, ref, n, beta, keep_space)
        ps.append(p); rs.append(r); fs.append(f)
    return float(np.mean(ps)), float(np.mean(rs)), float(np.mean(fs)), fs


print("=== 1) 复算书中两个 chrF2,2 值 ===")
rows = []
for name, hyp in (("HYP1", HYP1), ("HYP2", HYP2)):
    p, r, f, per_n = chrf(hyp, REF_W, beta=2.0)
    rows.append((name, hyp, p, r, f))
    print(f"{name}: chrP={p:.4f} chrR={r:.4f} chrF2={f:.4f}   逐 n 的 F: "
          + " ".join(f"{x:.3f}" for x in per_n))
print("  （书中给的是 .86 / .62；n≤6 的均值比只手算 1–2 元略低，原因见下）")

# 手算对照：只到 n=2，与书中「18 字符 / 17 二元」的算法一致
def hand(hyp, ref):
    p1, r1, _ = f_score(hyp, ref, 1, 2)
    p2, r2, _ = f_score(hyp, ref, 2, 2)
    cp, cr = (p1 + p2) / 2, (r1 + r2) / 2
    return cp, cr, 5 * cp * cr / (4 * cp + cr)


hand_rows = [hand(HYP1, REF_W), hand(HYP2, REF_W)]
for (name, hyp, p, r, f), (cp, cr, fh2) in zip(rows, hand_rows):
    print(f"  手算(仅 1–2 元) {name}: chrP={cp:.4f} chrR={cr:.4f} chrF2={fh2:.4f}")
print(f"  参考句去掉空格后长度 = {len(REF_W.replace(' ', ''))} 字符，"
      f"{len(REF_W.replace(' ', '')) - 1} 个二元 —— 与书中一致")

with open(os.path.join(OUT, "chrf_terms.csv"), "w", encoding="utf-8") as fh:
    fh.write("hyp,chrP,chrR,chrF2_n6,chrF2_hand_n12\n")
    for (name, hyp, p, r, f), (cp, cr, fh2) in zip(rows, hand_rows):
        fh.write(f"{name},{p:.4f},{r:.4f},{f:.4f},{fh2:.4f}\n")

print("\n=== 2) k 与 β 的敏感性 ===")
sweep = []
for k in range(1, 7):
    _, _, f2, _ = chrf(HYP2, REF_W, max_n=k)
    _, _, f1, _ = chrf(HYP1, REF_W, max_n=k)
    sweep.append((k, f1, f2))
    print(f"  n≤{k}: HYP1 chrF2={f1:.4f}  HYP2 chrF2={f2:.4f}")
with open(os.path.join(OUT, "chrf_k_sweep.csv"), "w", encoding="utf-8") as fh:
    fh.write("max_n,HYP1,HYP2\n")
    for k, a, b in sweep:
        fh.write(f"{k},{a:.4f},{b:.4f}\n")

print("\n  β 扫描（HYP2，n≤6）：")
for beta in (0.5, 1.0, 2.0, 3.0):
    _, _, f, _ = chrf(HYP2, REF_W, beta=beta)
    print(f"    β={beta}: chrF={f:.4f}")

print("\n=== 3) BLEU：词级 n 元精确率 + 简短惩罚 ===")


def bleu(hyp, ref, max_n=4, smooth=True):
    h, r = hyp.split(), ref.split()
    ps = []
    for n in range(1, max_n + 1):
        hc = Counter(tuple(h[i:i + n]) for i in range(len(h) - n + 1))
        rc = Counter(tuple(r[i:i + n]) for i in range(len(r) - n + 1))
        if not hc:
            ps.append(0.0); continue
        hit = sum((hc & rc).values())
        ps.append((hit + (1 if smooth else 0)) / (sum(hc.values()) + (1 if smooth else 0)))
    if min(ps) == 0:
        return 0.0, ps
    bp = 1.0 if len(h) > len(r) else float(np.exp(1 - len(r) / max(len(h), 1)))
    return float(bp * np.exp(np.mean(np.log(ps)))), ps


print("  单词对的 BLEU（REF='the cat sat on the mat'）：")
bleu_rows = []
for name, hyp in (("HYP1", "the cat sat on the mat,"), ("HYP2", "cat mat")):
    s, ps = bleu(hyp, REF)
    s0, _ = bleu(hyp, REF, smooth=False)
    bleu_rows.append((name, hyp, s, s0))
    print(f"    {name}: BLEU-4(平滑)={s:.4f}  BLEU-4(不平滑)={s0:.4f}  各 n 精确率 "
          + " ".join(f"{x:.2f}" for x in ps))

CORPUS_REF = ["the house is big", "the dog is small", "i see the house",
              "the dog sees the house", "i see a big dog"]
CORPUS_HYP = ["the house is big", "the dog is small", "i see a house",
              "the dog sees house", "i see big dog"]


def corpus_bleu(hyps, refs, max_n=4):
    num = [0] * max_n; den = [0] * max_n
    for h, r in zip(hyps, refs):
        h, r = h.split(), r.split()
        for n in range(1, max_n + 1):
            hc = Counter(tuple(h[i:i + n]) for i in range(len(h) - n + 1))
            rc = Counter(tuple(r[i:i + n]) for i in range(len(r) - n + 1))
            num[n - 1] += sum((hc & rc).values())
            den[n - 1] += sum(hc.values())
    prec = [num[i] / den[i] if den[i] else 0.0 for i in range(max_n)]
    lh = sum(len(h.split()) for h in hyps); lr = sum(len(r.split()) for r in refs)
    bp = 1.0 if lh > lr else float(np.exp(1 - lr / max(lh, 1)))
    if min(prec) == 0:
        return 0.0, prec
    return float(bp * np.exp(np.mean(np.log(prec)))), prec


print("\n  语料级 BLEU（5 句，避免单句过短把 BLEU 打成 0）：")
cb, prec = corpus_bleu(CORPUS_HYP, CORPUS_REF)
print(f"    corpus BLEU-4 = {cb:.4f}   各 n 精确率 " + " ".join(f"{x:.3f}" for x in prec))

print("\n  同一批句子上的句子级 chrF2：")
ch = [chrf(h, r)[2] for h, r in zip(CORPUS_HYP, CORPUS_REF)]
for h, r, c in zip(CORPUS_HYP, CORPUS_REF, ch):
    print(f"    {c:.3f}  {h!r} vs {r!r}")
print(f"    平均 chrF2 = {np.mean(ch):.4f}   最小 = {min(ch):.4f}")

with open(os.path.join(OUT, "bleu_compare.csv"), "w", encoding="utf-8") as fh:
    fh.write("case,bleu4_smooth,bleu4_raw\n")
    for name, hyp, s, s0 in bleu_rows:
        fh.write(f"{name},{s:.4f},{s0:.4f}\n")
    fh.write(f"corpus5,{cb:.4f},\n")
    fh.write("segment,chrf2\n")
    for h, c in zip(CORPUS_HYP, ch):
        fh.write(f'"{h}",{c:.4f}\n')

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(9.2, 3.4))
ax[0].plot([k for k, _, _ in sweep], [a for _, a, _ in sweep], "o-", label="HYP1 (of the)")
ax[0].plot([k for k, _, _ in sweep], [b for _, _, b in sweep], "s--", label="HYP2 (past witness)")
ax[0].axhline(0.86, color="gray", lw=0.8, ls=":")
ax[0].axhline(0.62, color="gray", lw=0.8, ls=":")
ax[0].set_xlabel("max n"); ax[0].set_ylabel("chrF2"); ax[0].set_title("chrF vs n-gram order")
ax[0].legend(fontsize=8)

names = ["HYP1", "HYP2"]
xx = np.arange(2)
ax[1].bar(xx - 0.2, [b for _, _, b, _ in bleu_rows], 0.4, label="BLEU-4 (smoothed)")
ax[1].bar(xx + 0.2, [chrf(HYP1, REF_W)[2], chrf(HYP2, REF_W)[2]], 0.4, label="chrF2")
ax[1].set_xticks(xx); ax[1].set_xticklabels(names)
ax[1].set_title("short segments: BLEU collapses, chrF does not")
ax[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "bleu_chrf.png"), dpi=150)

with open(os.path.join(OUT, "summary.txt"), "w", encoding="utf-8") as fh:
    for name, hyp, p, r, f in rows:
        fh.write(f"{name}: chrP={p:.4f} chrR={r:.4f} chrF2={f:.4f}\n")
    fh.write(f"corpus5 BLEU-4={cb:.4f}\n")
    fh.write(f"corpus5 mean chrF2={np.mean(ch):.4f}\n")
print("\n[done] out/ 已写 chrf_terms.csv / chrf_k_sweep.csv / bleu_compare.csv / bleu_chrf.png")
