#!/usr/bin/env python3
"""lab-04: 简化版 SentProp 标签传播
对应 actions.md 第 4 条，书中 §23.4.2
"""
import csv
import os
import numpy as np
from scipy import stats

rng = np.random.default_rng(42)

# 构造 50 词小图：25 正向 + 25 负向
# 每个词有 100 维向量，前 20 维是情感维度
dim = 100
words = []
vectors = {}

pos_words = [f"pos{i}" for i in range(25)]
neg_words = [f"neg{i}" for i in range(25)]

for w in pos_words:
    v = rng.normal(0, 0.3, dim)
    v[:20] += 1.5  # 正向词在情感维度上高
    vectors[w] = v
    words.append(w)

for w in neg_words:
    v = rng.normal(0, 0.3, dim)
    v[:20] -= 1.5  # 负向词在情感维度上低
    vectors[w] = v
    words.append(w)

# 构建 k-NN 图（k=5）
k = 5
n = len(words)
adj = np.zeros((n, n))
for i in range(n):
    sims = []
    for j in range(n):
        if i == j:
            continue
        vi = vectors[words[i]] / np.linalg.norm(vectors[words[i]])
        vj = vectors[words[j]] / np.linalg.norm(vectors[words[j]])
        cos = np.dot(vi, vj)
        sims.append((j, cos))
    sims.sort(key=lambda x: x[1], reverse=True)
    for j, cos in sims[:k]:
        adj[i, j] = max(cos, 0.01)  # 避免零权重

# 归一化邻接矩阵（随机游走转移概率）
row_sums = adj.sum(axis=1, keepdims=True)
P = adj / row_sums

# 种子词集合（3 组不同的种子）
seed_sets = [
    {"pos": ["pos0", "pos1", "pos2"], "neg": ["neg0", "neg1", "neg2"]},
    {"pos": ["pos5", "pos6", "pos7"], "neg": ["neg5", "neg6", "neg7"]},
    {"pos": ["pos10", "pos11", "pos12"], "neg": ["neg10", "neg11", "neg12"]},
]

def sentprop(seed_pos, seed_neg, n_iter=100, reset_prob=0.2):
    """简化版 SentProp：带重启的随机游走"""
    # 初始得分：种子词分别设为 1 和 0，其他 0.5
    score_pos = np.zeros(n)
    score_neg = np.zeros(n)
    for w in seed_pos:
        score_pos[words.index(w)] = 1.0
    for w in seed_neg:
        score_neg[words.index(w)] = 1.0

    # 随机游走
    for _ in range(n_iter):
        new_pos = (1 - reset_prob) * P.T @ score_pos
        new_neg = (1 - reset_prob) * P.T @ score_neg
        # 重置到种子
        for w in seed_pos:
            new_pos[words.index(w)] += reset_prob * 1.0
        for w in seed_neg:
            new_neg[words.index(w)] += reset_prob * 1.0
        score_pos, score_neg = new_pos, new_neg

    # 合并得分（书中式：score+ = rawscore+ / (rawscore+ + rawscore-)）
    total = score_pos + score_neg
    total[total == 0] = 1e-10
    final = score_pos / total
    return final

# 跑 3 组种子
all_ranks = []
for idx, seeds in enumerate(seed_sets):
    final = sentprop(seeds["pos"], seeds["neg"])
    # 排名（从高到低）
    ranks = np.argsort(-final)
    rank_dict = {words[r]: r + 1 for r in ranks}
    all_ranks.append(rank_dict)

    print(f"\nSeed set {idx+1}: pos={seeds['pos']}, neg={seeds['neg']}")
    print("  Top 5:", [words[r] for r in ranks[:5]])
    print("  Bottom 5:", [words[r] for r in ranks[-5:]])

# 计算 Spearman 相关系数
print("\nSpearman rank correlations between seed sets:")
for i in range(3):
    for j in range(i+1, 3):
        r1 = [all_ranks[i][w] for w in words]
        r2 = [all_ranks[j][w] for w in words]
        rho, p = stats.spearmanr(r1, r2)
        print(f"  set{i+1} vs set{j+1}: ρ={rho:.4f}, p={p:.6f}")

# 找出排名波动最大的词
rank_std = {}
for w in words:
    ranks_w = [all_ranks[i][w] for i in range(3)]
    rank_std[w] = np.std(ranks_w)

most_unstable = sorted(rank_std.items(), key=lambda x: x[1], reverse=True)[:5]
print("\nMost unstable words (std of ranks across seed sets):")
for w, std in most_unstable:
    print(f"  {w}: std={std:.2f}")

os.makedirs("out", exist_ok=True)
with open("out/sentprop_ranks.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["word"] + [f"rank_set{i+1}" for i in range(3)] + ["rank_std"])
    for w in words:
        writer.writerow([w] + [all_ranks[i][w] for i in range(3)] + [f"{rank_std[w]:.2f}"])

print("\nsaved: out/sentprop_ranks.csv")
