#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""lab-03  束搜索 vs 贪心解码，以及长度归一化会怎样改变选择

对应 actions.md 第 3 条；对应 §13.4 图 13.7 的搜索树。
书中给出的三个锚点数：第一步 yes 的局部概率 .5、ok 的先验 .4、
以及 ok ok EOS 的总概率 .4×.7×1.0。本脚本据此重建一棵玩具树
（其余分支书中图里没有在抽取文本中给出，按「让贪心走错」的最小设定补齐），
然后跑贪心 / 束宽 k=2,3 的束搜索，并对长度归一化做翻转率实验。
"""
import json
import os

import numpy as np

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)
EPS = 1e-12

# ---------------------------------------------------------------- 玩具搜索树
# key = 已生成的前缀（tuple），value = {下一个词: 概率}
TREE = {
    (): {"ok": 0.40, "yes": 0.50, "the": 0.05, "EOS": 0.05},
    ("ok",): {"ok": 0.70, "yes": 0.10, "the": 0.10, "EOS": 0.10},
    ("ok", "ok"): {"EOS": 1.00},
    ("yes",): {"yes": 0.40, "ok": 0.30, "EOS": 0.20, "the": 0.10},
    ("yes", "yes"): {"EOS": 1.00},
    ("the",): {"EOS": 0.90, "ok": 0.10},
}
MAX_LEN = 4


def children(prefix):
    """prefix 含句首的 <s>；树按「已生成的词元元组」索引。"""
    return TREE.get(tuple(prefix[1:]), {})


print("=== 1) 贪心解码 ===")
prefix, seq, logp = ("<s>",), [], 0.0
trace_greedy = []
for step in range(MAX_LEN):
    cand = children(prefix)
    if not cand:
        break
    w = max(cand, key=cand.get)
    trace_greedy.append({"step": step + 1, "prefix": " ".join(prefix[1:]) or "<s>",
                         "chosen": w, "p_chosen": cand[w],
                         "alternatives": {k: v for k, v in sorted(cand.items(), key=lambda kv: -kv[1])}})
    logp += np.log(cand[w])
    if w == "EOS":
        break
    seq.append(w)
    prefix = prefix + (w,)
greedy_score = float(np.exp(logp))
print(f"  贪心输出：{' '.join(seq)} EOS   概率={greedy_score:.4f}")
for t in trace_greedy:
    print(f"    t={t['step']} 前缀 {t['prefix']!r} 选 {t['chosen']} (p={t['p_chosen']:.2f}) "
          f"候选 " + ", ".join(f"{k}:{v:.2f}" for k, v in t["alternatives"].items()))


def beam_search(k, alpha=0.0, max_len=MAX_LEN):
    """alpha>0 时用 GNMT 式长度归一化 (5+|y|)^a / 6^a 给分数。"""
    beams = [((("<s>",), 0.0))]
    finished = []
    trace = []
    for step in range(max_len):
        cands = []
        for prefix, lp in beams:
            for w, p in children(prefix).items():
                nlp = lp + np.log(p)
                if w == "EOS":
                    ylen = len(prefix) - 1      # 不含 <s>
                    pen = ((5 + ylen) ** alpha) / (6 ** alpha)
                    finished.append((prefix, nlp - np.log(pen) if alpha else nlp, nlp))
                else:
                    cands.append((prefix + (w,), nlp))
        # 只保留 k 个未完成假设（按原始对数概率）
        cands.sort(key=lambda x: -x[1])
        beams = cands[:k]
        trace.append({"step": step + 1,
                      "alive": [(" ".join(p[1:]), round(lp, 4)) for p, lp in beams],
                      "finished": [(" ".join(p[1:]) + " EOS", round(lp, 4)) for p, lp, _ in finished]})
        if not beams:
            break
    pool = [((" ".join(p[1:]) + " EOS"), lp) for p, lp in beams] + \
           [((" ".join(p[1:]) + " EOS"), lp) for p, lp, _ in finished]
    pool.sort(key=lambda x: -x[1])
    return pool, trace, finished


print("\n=== 2) 束搜索 ===")
for k in (1, 2, 3):
    pool, trace, fin = beam_search(k)
    print(f"  k={k}: " + " | ".join(f"{s} {lp:.3f}" for s, lp in pool[:3]))

pool2, trace2, fin2 = beam_search(2)
with open(os.path.join(OUT, "beam_trace.csv"), "w", encoding="utf-8") as fh:
    fh.write("step,alive,logp\n")
    for t in trace2:
        for s, lp in t["alive"]:
            fh.write(f"{t['step']},{s},{lp}\n")

print("\n  束宽 k=2 的逐步轨迹：")
for t in trace2:
    print(f"    t={t['step']} alive=" + " ".join(f"[{s} {lp:.3f}]" for s, lp in t["alive"])
          + ("  finished=" + " ".join(f"[{s} {lp:.3f}]" for s, lp in t["finished"]) if t["finished"] else ""))

print("\n=== 3) 长度归一化：翻转率实验 ===")
rng = np.random.default_rng(0)
N, TRIALS, ALPHA = 6, 2000, 1.0
flips = {"gnmt": 0, "avg": 0}
for _ in range(TRIALS):
    lens = rng.integers(2, 12, size=N)
    # 每个假设的平均对数概率在 [-2.5,-0.3]，长度越长越容易「平均更好但总和更差」
    mean_lp = rng.uniform(-2.5, -0.3, size=N) + 0.08 * (lens - 2)
    total = mean_lp * lens
    raw_best = int(np.argmax(total))
    gnmt = total / (((5 + lens) ** ALPHA) / (6 ** ALPHA))
    avg = total / lens
    flips["gnmt"] += int(np.argmax(gnmt) != raw_best)
    flips["avg"] += int(np.argmax(avg) != raw_best)
print(f"  随机 {TRIALS} 组假设集（每组 {N} 条，长度 2–11），α=1：")
print(f"    GNMT 归一化 (5+|y|)^α/6^α 改变最优选择的比例 = {flips['gnmt'] / TRIALS:.3%}")
print(f"    平均对数概率归一化 (÷|y|)      改变最优选择的比例 = {flips['avg'] / TRIALS:.3%}")

# 书中那棵树在两种归一化下的排序
rows = []
for s, lp in pool2:
    ylen = len(s.split()) - 1
    gnmt = lp / (((5 + ylen) ** 1.0) / 6 ** 1.0) if ylen else lp
    rows.append({"hyp": s, "len": ylen, "logp": round(lp, 4),
                 "avg_lp": round(lp / max(ylen, 1), 4), "gnmt": round(gnmt, 4)})
print("\n  书中树上 k=2 的候选在三种打分下的排序：")
for r in sorted(rows, key=lambda r: -r["gnmt"]):
    print(f"    {r['hyp']:<16} len={r['len']} logP={r['logp']:.3f} "
          f"avg={r['avg_lp']:.3f} gnmt={r['gnmt']:.3f}")

with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as fh:
    json.dump({
        "greedy": {"seq": " ".join(seq) + " EOS", "prob": round(greedy_score, 4), "trace": trace_greedy},
        "beam": {"k": 2, "pool": [{"hyp": s, "logp": round(lp, 4)} for s, lp in pool2]},
        "length_norm": {"trials": TRIALS, "n_hyp": N, "alpha": ALPHA,
                        "flip_rate_gnmt": round(flips["gnmt"] / TRIALS, 4),
                        "flip_rate_avg": round(flips["avg"] / TRIALS, 4)},
        "top2_scores": rows,
    }, fh, ensure_ascii=False, indent=2)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(1, 2, figsize=(9.4, 3.4))
labels = [r["hyp"].replace(" EOS", "") for r in rows]
xx = np.arange(len(rows))
ax[0].bar(xx - 0.2, [r["logp"] for r in rows], 0.4, label="log P(y)")
ax[0].bar(xx + 0.2, [r["gnmt"] for r in rows], 0.4, label="length-normalized")
ax[0].set_xticks(xx); ax[0].set_xticklabels(labels, fontsize=8)
ax[0].set_title("beam candidates: raw vs normalized")
ax[0].legend(fontsize=8)

lens = np.arange(2, 12)
ax[1].plot(lens, -1.0 - 0.05 * lens, "o-", label="short & fluent")
ax[1].plot(lens, -2.2 - 0.02 * lens, "s--", label="longer, slightly worse avg")
ax[1].set_xlabel("|y|"); ax[1].set_ylabel("log P(y)"); ax[1].set_title("why length matters")
ax[1].legend(fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "beam.png"), dpi=150)

print(f"\n[done] 束搜索找到 {' '.join(pool2[0][0].split())} ({pool2[0][1]:.3f})，"
      f"贪心只找到 {' '.join(seq)} EOS ({greedy_score:.3f})")
