#!/usr/bin/env python3
"""lab-02: 语义轴方法 (Semantic Axis)
对应 actions.md 第 2 条，书中 §23.4.1
"""
import csv
import os
import numpy as np

rng = np.random.default_rng(42)

# 构造一个 100 维的合成向量空间：
# 前 20 维 = 情感维度（正向词高，负向词低）
# 中间 40 维 = 主题维度（food, movie, sports 等）
# 后 40 维 = 噪声
dim = 100
n_words = 200

words = []
vectors = {}

# 正向种子词
pos_seeds = ["good", "great", "amazing", "love", "excellent"]
# 负向种子词
neg_seeds = ["bad", "terrible", "awful", "hate", "horrible"]

# 候选词：包含明确正向、明确负向、多义词、中性词
candidates = [
    "wonderful", "fantastic", "delightful", "superb", "marvelous",
    "terrific", "horrible", "dreadful", "atrocious", "appalling",
    "mediocre", "adequate", "acceptable", "satisfactory", "fine",
    "critical", "volatile", "sharp", "bright", "light",
    "neutral", "ordinary", "standard", "common", "usual",
]

all_words = pos_seeds + neg_seeds + candidates

for w in all_words:
    v = rng.normal(0, 0.3, dim)
    # 情感维度（前 20 维）
    if w in pos_seeds or w in {"wonderful", "fantastic", "delightful", "superb", "marvelous", "terrific"}:
        v[:20] += 1.5
    elif w in neg_seeds or w in {"horrible", "dreadful", "atrocious", "appalling"}:
        v[:20] -= 1.5
    elif w in {"mediocre", "adequate", "acceptable", "satisfactory", "fine"}:
        v[:20] += 0.2  # 弱正面
    elif w in {"critical"}:
        v[:20] -= 0.8  # 偏负面（多义）
        v[20:35] += 1.0  # 但也有「关键」的语义
    elif w in {"volatile"}:
        v[:20] -= 0.5
        v[35:50] += 1.0
    elif w in {"sharp", "bright", "light"}:
        v[:20] += 0.5  # 弱正面（多义）
        v[50:65] += 0.8
    else:
        pass  # 中性词
    vectors[w] = v

# 语义轴计算（书中式 23.3 的重建）
V_pos = np.mean([vectors[w] for w in pos_seeds], axis=0)
V_neg = np.mean([vectors[w] for w in neg_seeds], axis=0)
V_axis = V_pos - V_neg
V_axis = V_axis / np.linalg.norm(V_axis)

print("Semantic axis computed.")
print(f"V_pos[:5] = {V_pos[:5]}")
print(f"V_neg[:5] = {V_neg[:5]}")
print(f"V_axis[:5] = {V_axis[:5]}")

# 给候选词打分
results = []
for w in candidates:
    v = vectors[w] / np.linalg.norm(vectors[w])
    score = float(np.dot(v, V_axis))
    # 方向判断：score>0 → 正向，score<0 → 负向
    direction = "pos" if score > 0 else "neg"
    results.append({"word": w, "score": f"{score:.4f}", "direction": direction})

# 按 score 排序
results.sort(key=lambda x: float(x["score"]), reverse=True)

print("\nTop 20 candidates by semantic axis score:")
for r in results[:20]:
    print(f"  {r['word']:15s}  score={float(r['score']):+.4f}  → {r['direction']}")

# 检查明显错误的词（多义词）
print("\nPotentially ambiguous words:")
for r in results:
    if r["word"] in {"critical", "volatile", "sharp", "bright", "light"}:
        print(f"  {r['word']:15s}  score={float(r['score']):+.4f}  → {r['direction']}")

# 统计
n_correct = sum(1 for r in results if r["direction"] == "pos")  # 大部分候选词构造为正向
n_total = len(results)
print(f"\nDirection check: {n_correct}/{n_total} scored as positive (expect mostly positive in this setup)")

os.makedirs("out", exist_ok=True)
with open("out/axis_scores.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["word", "score", "direction"])
    w.writeheader()
    w.writerows(results)

print("saved: out/axis_scores.csv")
