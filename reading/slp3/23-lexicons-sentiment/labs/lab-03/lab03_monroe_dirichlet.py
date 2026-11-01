#!/usr/bin/env python3
"""lab-03: 对数几率比信息狄利克雷先验 (Monroe 2008)
对应 actions.md 第 3 条，书中 §23.5.1 式 23.7–23.11
"""
import csv
import math
import os
import numpy as np

rng = np.random.default_rng(42)

# 构造两个合成语料：正面评论 vs 负面评论
# 每类 50 句，每句 10-15 词
positive_reviews = [
    "great amazing wonderful fantastic love excellent perfect best superb",
    "amazing experience wonderful food great service love this place",
    "fantastic movie excellent acting superb directing wonderful story",
    "love it amazing quality great value perfect condition excellent",
    "wonderful time amazing view great atmosphere love the service",
    "excellent work amazing result fantastic job great effort perfect",
    "superb performance amazing talent wonderful voice great music",
    "fantastic book amazing story excellent writing wonderful characters",
    "great product amazing features wonderful design love the quality",
    "perfect experience amazing food wonderful service great location",
] * 5

negative_reviews = [
    "terrible awful horrible bad hate worst dreadful atrocious",
    "awful experience terrible food bad service hate this place",
    "horrible movie terrible acting bad directing awful story",
    "hate it awful quality terrible value worst condition bad",
    "terrible time awful view bad atmosphere hate the service",
    "bad work awful result terrible job horrible effort worst",
    "dreadful performance terrible talent awful voice bad music",
    "horrible book awful story bad writing terrible characters",
    "terrible product awful features bad design hate the quality",
    "worst experience awful food terrible service bad location",
] * 5

def tokenize(reviews):
    tokens = []
    for r in reviews:
        tokens.extend(r.lower().split())
    return tokens

pos_tokens = tokenize(positive_reviews)
neg_tokens = tokenize(negative_reviews)

# 加入一些中性词和罕见词
neutral_words = ["the", "a", "is", "was", "and", "it", "this", "that"]
for _ in range(200):
    pos_tokens.append(rng.choice(neutral_words))
    neg_tokens.append(rng.choice(neutral_words))

# 加入一个只在正面出现的极罕见词
pos_tokens.append("flabbergasting")

# 加入一个高频中性词
for _ in range(100):
    pos_tokens.append("movie")
    neg_tokens.append("movie")

pos_counts = {}
neg_counts = {}
for t in pos_tokens:
    pos_counts[t] = pos_counts.get(t, 0) + 1
for t in neg_tokens:
    neg_counts[t] = neg_counts.get(t, 0) + 1

n_pos = len(pos_tokens)
n_neg = len(neg_tokens)
print(f"Corpus sizes: pos={n_pos}, neg={n_neg}")

# 背景语料（先验）：合并两个语料
bg_counts = {w: pos_counts.get(w, 0) + neg_counts.get(w, 0) for w in set(pos_counts) | set(neg_counts)}
n_bg = n_pos + n_neg

# 缩放先验（书中 α0 和 αw）
alpha_scale = 0.1  # α0 = n_bg * alpha_scale
alpha0 = n_bg * alpha_scale

def monroe_score(w):
    """计算 Monroe 2008 的对数几率比 z 分数"""
    f_pos = pos_counts.get(w, 0)
    f_neg = neg_counts.get(w, 0)
    f_bg = bg_counts.get(w, 0)

    # 先验计数（缩放）
    alpha_w = f_bg * alpha_scale

    # 式 23.9：经先验修正的对数几率比
    num_pos = f_pos + alpha_w
    den_pos = n_pos + alpha0 - (f_pos + alpha_w)
    num_neg = f_neg + alpha_w
    den_neg = n_neg + alpha0 - (f_neg + alpha_w)

    if den_pos <= 0 or den_neg <= 0 or num_pos <= 0 or num_neg <= 0:
        return 0.0, 0.0

    delta = math.log(num_pos / den_pos) - math.log(num_neg / den_neg)

    # 式 23.10：方差估计
    sigma2 = 1.0 / (f_pos + alpha_w) + 1.0 / (f_neg + alpha_w)

    # 式 23.11：z 分数
    z = delta / math.sqrt(sigma2)
    return delta, z

def simple_log_odds(w):
    """简单对数几率比（不加先验）"""
    f_pos = pos_counts.get(w, 0)
    f_neg = neg_counts.get(w, 0)
    if f_pos == 0 or f_neg == 0:
        return float('inf') if f_pos > 0 else float('-inf')
    p_pos = f_pos / n_pos
    p_neg = f_neg / n_neg
    return math.log(p_pos / (1 - p_pos)) - math.log(p_neg / (1 - p_neg))

# 计算所有词的 z 分数
words = list(set(pos_counts) | set(neg_counts))
scores = []
for w in words:
    delta, z = monroe_score(w)
    simple = simple_log_odds(w)
    scores.append({"word": w, "delta": f"{delta:.4f}", "z": f"{z:.4f}", "simple": f"{simple:.4f}" if np.isfinite(simple) else "inf"})

# 按 z 分数排序
scores.sort(key=lambda x: float(x["z"]), reverse=True)

print("\nTop 10 words by Monroe z-score (positive):")
for s in scores[:10]:
    zv = float(s['z'])
    sv = s['simple']
    sv_fmt = f"{float(sv):+.4f}" if sv not in ("inf", "-inf") else f"{sv:>10s}"
    print(f"  {s['word']:20s}  z={zv:+.4f}  simple={sv_fmt:>10s}")

print("\nBottom 10 words by Monroe z-score (negative):")
for s in scores[-10:]:
    zv = float(s['z'])
    sv = s['simple']
    sv_fmt = f"{float(sv):+.4f}" if sv not in ("inf", "-inf") else f"{sv:>10s}"
    print(f"  {s['word']:20s}  z={zv:+.4f}  simple={sv_fmt:>10s}")

# 检查极罕见词
print("\nRare word check:")
for s in scores:
    if s["word"] == "flabbergasting":
        print(f"  flabbergasting: z={s['z']}, simple={s['simple']}")

# 检查高频中性词
for s in scores:
    if s["word"] == "movie":
        print(f"  movie: z={s['z']}, simple={s['simple']}")

os.makedirs("out", exist_ok=True)
with open("out/monroe_zscores.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["word", "delta", "z", "simple"])
    w.writeheader()
    w.writerows(scores)

print("\nsaved: out/monroe_zscores.csv")
